# Refonte du câblage des signaux GUI

## Contexte

`MainWindow` est le hub de tout le câblage : 33 `.connect()` dont 22 concentrés dans
`_connect_signals()` (`src/manga_trad/gui/main_window.py:154-226`). Le refactor c9ac4db a
sorti deux coordinateurs (`OcrUiCoordinator`, `LibraryActionsCoordinator`) mais avait
explicitement mis hors périmètre la refonte de `_connect_signals` / `_open_page` /
`_refresh_page_views` — c'est-à-dire exactement ce qui reste problématique.

Le désordre n'est pas « trop de `.connect` », c'est **un état partagé sans propriétaire** :

1. **Synchro impérative des vues.** Aucune connexion `Canvas ↔ Timeline ↔ SidePanel`.
   La page courante et la bulle sélectionnée sont propagées à la main dans `_select_bubble`
   (`main_window.py:298-309`), `_open_page` (`:228-239`) et `_refresh_page_views` (`:281-287`).
   D'où **6 sites de `blockSignals`** pour casser les boucles (`timeline.py:121-156`,
   `side_panel/panel.py:189-195`, `side_panel/preset_selector.py:43-51`,
   `chapter_filter_bar.py:61-77`, `main_toolbar.py:220-228`), plus un flag `_emit_reorder`
   qui fait doublon avec `blockSignals` dans `timeline.py`.
2. **État de page sans notification.** `PageController.page_id`
   (`core/services/page_controller.py:15`) est un attribut public muté depuis trois
   endroits (`page_controller.py:57`, `library_actions.py:81,154`) : personne n'est prévenu.
3. **Logique métier résiduelle dans la fenêtre** : `_on_bubble_created`,
   `_on_bubble_geometry_changed`, `_on_reorder_requested`, `_on_bubble_delete_requested`,
   `_sync_ocr_test_source` écrivent en base puis rafraîchissent trois vues à la main.
4. **Double câblage fragile** : `prep_combo.currentIndexChanged` connecté dans deux
   fichiers (`main_toolbar.py:83` persistance QSettings, `main_window.py:166` application
   au contrôleur OCR), avec des slots aux noms quasi identiques. `MainToolbar` n'expose pas
   de signal dédié ici, contrairement à `ocr_engines_changed`.
5. **Deux chemins parallèles** pour le rafraîchissement filtre→pages : le signal
   `filter_changed` (`main_window.py:184`) et des appels manuels `page_bar.reload(...)`
   dans `library_actions.py:98,152,170`.
6. **Fuites d'encapsulation** : `OcrUiCoordinator` lit `self._side_panel._bubble` en 3
   endroits (`ocr_ui_coordinator.py:95,120-122,146-147`) ;
   `ThumbnailTaskManager.thumbnail_failed` est émis (`thumbnail_task_manager.py:66`) mais
   jamais connecté — échecs de vignette silencieux.

**Résultat visé** : un propriétaire unique de l'état de session qui notifie, des vues qui
s'y abonnent au lieu d'être poussées, et `MainWindow` réduit à de l'assemblage.

**Contrainte respectée** : `specs/07-implementation-architecture.md:5-7` — le backend
n'importe jamais Qt. `SessionState` est un `QObject`, il vit donc dans `gui/`, pas dans
`core/`. Aucun bus d'événements global (flux implicite, non traçable) : le modèle d'état
est nommé et typé.

## Périmètre

**Dans** : tout le câblage GUI — axe bulle, toolbar/presets, filtre/bibliothèque,
navigation, reprise des deux coordinateurs existants.

**Hors périmètre** :
- Backend `core/translation`, `core/pipeline.py` (toujours absents).
- Le bug préexistant `apply_batch_results` (lot partiel laissant des bulles en
  « OCR en cours », `ocr_ui_coordinator.py:111-127`) — à traiter séparément.
- Refonte visuelle, ergonomie, nouvelles fonctionnalités.
- Schéma SQLite et modèle de données.

## Étapes

### 1. Infrastructure de test

- Ajouter `pytest-qt` aux deps dev (`pyproject.toml:26-30`).
- `tests/gui/conftest.py` : conserver la fixture `qapp` existante (`:9-14`), la faire
  cohabiter avec `qtbot` ; factoriser le `_pump()` dupliqué
  (`test_ocr_task_manager.py:44`, `test_deferred_batch_queue.py:39`) en helper partagé.
- Écrire des **tests de caractérisation** du comportement actuel, avant de toucher au
  câblage : sélection d'une bulle depuis le canvas → timeline et panneau suivent ;
  sélection depuis la timeline → canvas centre ; création/suppression/déplacement de
  bulle → les trois vues sont cohérentes. Ils servent de filet pour les étapes 2-3.
- Réutiliser la fixture `repo` (`tests/conftest.py:8-12`, `Repository.connect(":memory:")`)
  et les helpers `pid()` / `not_none()` (`tests/helpers.py`) — vrais `core`/`db`, conforme
  à `specs/07:73-74`.

### 2. `SessionState` — propriétaire de l'état de session

Nouveau `src/manga_trad/gui/session_state.py` :

```python
class SessionState(QObject):
    page_changed = Signal(object)        # Page | None
    bubbles_changed = Signal(list)       # list[Bubble] de la page courante
    selection_changed = Signal(object)   # Bubble | None
    filter_changed = Signal(object, str) # chapter_id, search
```

Détient `page`, `bubbles`, `selected_bubble`, `chapter_id`, `search`. API :
`open_page(page_id)`, `reload_bubbles()`, `select(bubble_id | None)`, `set_filter(...)`,
`clear()`. Il possède le `PageController` et devient le **seul** à écrire
`PageController.page_id` (retirer les mutations directes de `library_actions.py:81,154`).

**Point clé anti-boucle** : `select()` et `open_page()` sont **idempotents** — retour
immédiat si la valeur ne change pas. C'est ce qui remplace les `blockSignals` plutôt que
de les déplacer.

Brancher les vues en abonnés :
- `Canvas` ← `page_changed` (image), `bubbles_changed`, `selection_changed`.
- `Timeline` ← `bubbles_changed`, `selection_changed`.
- `SidePanel` ← `selection_changed`, `page_changed` (chemin image).
- `PageBar` ← `page_changed` (page courante), `filter_changed` (rechargement).
- `PreprocessingPresetsTab` ← `selection_changed` — remplace `_sync_ocr_test_source`
  (`main_window.py:311-321`).

Sens montant inchangé : `Canvas.bubble_selected` / `Timeline.bubble_selected` →
`state.select(bid)`. Supprimer les deux lambdas `from_timeline` (`main_window.py:193-198`) ;
le centrage canvas devient une décision du `Canvas` selon qui a l'initiative, exposée via
un argument explicite de `select()` plutôt qu'un booléen porté par la fenêtre.

Retirer les `blockSignals` devenus inutiles : `timeline.py:121-156` (et le flag
`_emit_reorder` en doublon), `side_panel/panel.py:189-195` vs
`side_panel/preset_selector.py:43-51` (deux couches sur le même combo — n'en garder qu'une).

### 3. `BubbleCoordinator` — CRUD bulle

Nouveau `src/manga_trad/gui/controllers/bubble_coordinator.py`, sur le modèle de
`LibraryActionsCoordinator`. Reçoit `SessionState`, `PageController`, `OcrUiCoordinator`.

Absorbe de `main_window.py` : `_on_bubble_created` (`:289-296`), `_on_reorder_requested`
(`:323-326`), `_on_bubble_geometry_changed` (`:344-354`), `_on_bubble_delete_requested`
(`:356-360`). Chaque méthode : écrire en base via `PageController`, puis
`state.reload_bubbles()` / `state.select(...)` — plus aucun appel direct aux vues.

Le commentaire de `_on_bubble_geometry_changed` (`:349-350`, panneau gardant l'ancienne
région) devient sans objet : le panneau se recharge depuis `selection_changed`.

### 4. Toolbar et presets

- `MainToolbar` : exposer `prep_preset_changed(object)` (préréglage effectif), sur le
  modèle de `ocr_engines_changed` (`main_toolbar.py:51`). La persistance QSettings reste
  interne au widget (`:83`) ; `main_window.py:166` et `_on_prep_changed` (`:376-380`)
  disparaissent au profit d'un abonné unique. Fin du double câblage.
- `presets_changed` (deux `connect` consécutifs, `main_window.py:221-226`) : ordre
  d'exécution rendu explicite dans un slot unique nommé, ou déplacé vers le coordinateur
  concerné.
- `_on_ocr_engines_changed` (`:365-366`) : connexion directe, plus de slot relais.

### 5. Bibliothèque, filtre et navigation

- `ChapterFilterBar.filter_changed` → `state.set_filter(...)` ; `PageBar` se recharge
  depuis `state.filter_changed`. Supprimer les `page_bar.reload(...)` manuels de
  `library_actions.py:98,152,170` — chemin unique.
- `LibraryActionsCoordinator` : `page_opened` / `library_emptied` (`:31-32`) sont
  remplacés par des appels à `state.open_page(...)` / `state.clear()`. Le coordinateur
  garde son rôle de dialogues CRUD.
- `_navigate_page` (`main_window.py:259-275`) migre dans le `SessionState` (ou un helper
  attenant) : il lit déjà `chapter_id` + `search`, qui deviennent de l'état de session au
  lieu d'être arrachés au `ChapterFilterBar`.
- `_reset_to_empty_state` (`:368-374`) devient `state.clear()`, les vues réagissant à
  `page_changed(None)` / `bubbles_changed([])`.

### 6. Nettoyage des fuites

- `SidePanel` : exposer `current_bubble` en lecture publique ; `OcrUiCoordinator`
  interroge le `SessionState` au lieu de `self._side_panel._bubble`
  (`ocr_ui_coordinator.py:95,120-122,146-147`).
- Connecter `ThumbnailTaskManager.thumbnail_failed` (`thumbnail_task_manager.py:66`), ou
  le supprimer si l'échec silencieux est le comportement voulu — décider explicitement.
- Corriger les commentaires obsolètes renvoyant à `main_window.py` :
  `ocr_ui_coordinator.py:73-74`, `main_toolbar.py:178-179`.

### 7. `MainWindow` réduit à l'assemblage + documentation

- Ne restent que : construction des widgets/docks, instanciation `SessionState` +
  coordinateurs, `eventFilter` / `_is_navigation_blocked`, visibilité des docks
  (`_on_mode_toggled`, `_update_side_docks_visibility`), `closeEvent`, et les deux
  `QMessageBox` (`_on_ocr_failed`, `_on_translate_page`).
- Mettre à jour `CLAUDE.md:20-32` (arborescence GUI : `side_panel/` est un package, les
  coordinateurs manquent) et `CLAUDE.md:49-58` (liste des signaux, obsolète) ; documenter
  la distinction **controllers métier `core/services/`** (sans Qt) vs **coordinateurs Qt
  `gui/controllers/`**, qui n'est écrite nulle part.
- `TASKS.md:170` (« aucun test GUI ») devient faux : mettre à jour.

## Vérification

À chaque étape :

```bash
uv run ruff format . && uv run ruff check .
uv run basedpyright
uv run pytest
```

Les tests de caractérisation de l'étape 1 doivent rester verts d'un bout à l'autre — c'est
le critère de non-régression du refactor.

Vérification end-to-end via `/run` (ou lancement manuel de la GUI) sur les parcours que les
tests headless couvrent mal :

1. Ouvrir une page, sélectionner une bulle dans le canvas → timeline et panneau suivent.
2. Sélectionner dans la timeline → le canvas centre sur la bulle.
3. Créer / déplacer / supprimer une bulle → les trois vues restent cohérentes, l'auto-OCR
   se déclenche.
4. Réordonner dans la timeline → l'ordre relatif affiché dans le canvas suit.
5. Changer le préréglage de prétraitement dans la toolbar → aperçu du panneau rafraîchi
   **et** valeur persistée après redémarrage (les deux effets de bord de l'ancien double
   câblage).
6. Filtrer par chapitre / rechercher → la barre de pages suit ; naviguer avec les touches
   reste borné au filtre courant.
7. Supprimer la dernière page / un chapitre entier → état vide propre.
8. Basculer Édition ↔ Lecture → docks droit et bas masqués.

## Critères de réussite

- Aucun appel direct vue→vue hors des coordinateurs ; `MainWindow` n'a plus de slot qui
  écrit en base.
- Les `blockSignals` restants sont justifiés par un commentaire, ou supprimés.
- `prep_combo` et le rafraîchissement filtre→pages ont chacun **un seul** chemin.
- `uv run pytest` vert, dont les tests de câblage ajoutés à l'étape 1.
