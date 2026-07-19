# Alléger `main_window.py` — extraire la logique métier

## Context

`src/manga_trad/gui/main_window.py` (~585 lignes) mélange trois responsabilités :
construction de l'UI, câblage des signaux, et **orchestration métier** des actions
(dialogues chapitre/page, flux OCR différé). Le projet a déjà amorcé le découplage
via des *controllers* (`core/services/`) et des *coordinateurs* GUI
(`gui/controllers/`, ex. `OcrUiCoordinator`). Objectif : poursuivre ce mouvement en
sortant de `MainWindow` ce qui n'y a pas sa place, pour la ramener à son rôle
d'assemblage + câblage inter-widgets. Aucun changement de comportement visible.

Périmètre validé : **les 3 extractions**. Hors-périmètre : refonte de `_connect_signals`,
de `_open_page`/`_refresh_page_views`, du `SidePanel`, ou du backend `core/`.

## Extraction #1 — `LibraryActionsCoordinator` (gain principal, ~220 lignes)

Nouveau fichier `src/manga_trad/gui/controllers/library_actions.py`.
Sur le modèle de `OcrUiCoordinator` : `QObject` qui **pilote directement** les widgets
vues qu'il possède légitimement (`ChapterFilterBar`, `PageBar`) et **émet des signaux**
pour ce qui reste à `MainWindow` (ouvrir une page, réinitialiser l'état vide).

Méthodes déplacées depuis `MainWindow` :
`_on_import_page`, `_prompt_chapter_choice`, `_on_new_chapter`, `_on_rename_chapter`,
`_on_delete_chapter`, `_on_reorder_chapters`, `_on_reorder_pages`, `_on_delete_page`
(lignes ~377-521 et ~526-550).

Constructeur :
```python
LibraryActionsCoordinator(
    chapter_controller, page_controller,
    filter_bar: ChapterFilterBar, page_bar: PageBar,
    parent: QWidget,   # cible des QInputDialog / QMessageBox
)
```
Signaux émis (réagis par `MainWindow`) :
- `page_opened(int)` → `MainWindow._open_page`
- `library_emptied()` → `MainWindow._reset_to_empty_state()`

`MainWindow` gagne un helper `_reset_to_empty_state()` factorisant le bloc « plus
aucune page » aujourd'hui dupliqué 2× (fin de `_on_delete_chapter` et `_on_delete_page` :
`canvas.load_page_image("")` + `timeline.load_bubbles([])` + `side_panel.load_bubble(None)`
+ `delete_page_action.setEnabled(False)`). Ce bloc touche canvas/timeline → reste dans
`MainWindow`, d'où le signal plutôt qu'un accès direct depuis le coordinateur.

Câblage dans `MainWindow` : connecter les `QAction` du toolbar (import, new/rename/delete
chapter, reorder chapters/pages, delete page) vers les méthodes du coordinateur, dans
`_connect_signals`. Mutualiser le garde « aucun chapitre sélectionné → QMessageBox.information »
(présent dans `_on_rename_chapter` et `_on_delete_chapter`) en un helper privé du coordinateur.

## Extraction #2 — `make_dock` dans `utils.py` (~40 lignes du `__init__`)

Ajouter à `src/manga_trad/gui/utils.py` :
```python
def make_dock(title: str, widget: QWidget, parent: QMainWindow) -> QDockWidget:
    """QDockWidget Movable|Floatable prêt à addDockWidget."""
```
Remplace les 3 blocs répétés (top_dock 88-94, right_dock 102-107, bottom_dock 113-118)
qui refont chacun `setWidget` + `setFeatures(Movable|Floatable)`. Le `top_container`
(VBox `chapter_filter_bar` + `page_bar`) reste construit dans `__init__`, puis passé à
`make_dock`. `_right_dock` et `_bottom_dock` restent des attributs (utilisés par
`_update_side_docks_visibility`).

## Extraction #3 — flux OCR différé → `OcrUiCoordinator` (~35 lignes)

Le coordinateur possède déjà `canvas`, `side_panel`, `ocr_controller`, `task_manager`.
Lui passer aussi `deferred_batch_queue` et `toolbar` au constructeur, et y déplacer :
- les 5 connexions `_deferred_batch_queue.*` (lignes 147-161) ;
- les handlers `_on_deferred_batch_enqueued/_finished/_failed` (561-571).

`_finished`/`_failed` appellent `toolbar.set_deferred_batch_running(False)` puis
respectivement `apply_batch_results` (déjà dans le coordinateur) et `ocr_failed.emit(...)`.
Étendre :
- `cancel_ocr(bubble_id)` → appeler aussi `deferred_batch_queue.remove(bubble_id)`
  (remplace l'appel direct dans `MainWindow._on_bubble_delete_requested`) ;
- `wait_for_pending()` → attendre aussi `deferred_batch_queue.wait_for_pending()`
  (remplace l'appel direct dans `closeEvent`).

`MainWindow` conserve la construction de `_deferred_batch_queue` (nécessaire à
`OcrTaskManager`) et le seul câblage `deferred_batch_action.triggered → queue.run_now`
dans `_connect_signals`. Ordre de construction inchangé : toolbar (123) → queue (132) →
task_manager (135) → `OcrUiCoordinator(..., queue, toolbar)` (138).

## Fichiers touchés

- **Créé** : `src/manga_trad/gui/controllers/library_actions.py`
- **Modifiés** : `src/manga_trad/gui/main_window.py` (retrait ~290 lignes nettes),
  `src/manga_trad/gui/utils.py` (+`make_dock`),
  `src/manga_trad/gui/controllers/ocr_ui_coordinator.py` (+flux différé).

Cible : `main_window.py` passe d'environ 585 à ~300 lignes.

## Vérification

1. `uv run ruff check . && uv run ruff format .`
2. `uv run basedpyright`
3. `uv run pytest`
4. Test manuel (skill `/run` ou lancement app) : importer des pages, créer/renommer/
   supprimer un chapitre, réorganiser chapitres et pages, supprimer la dernière page
   (→ état vide correct), créer une bulle et vérifier l'OCR différé (compteur toolbar,
   application du lot), supprimer une bulle en attente, fermer l'app (pas de warning de
   thread en cours). Vérifier la bascule mode Lecture (docks droit/bas masqués).

## Ordre d'exécution

#1 (autonome, plus gros gain) → #2 → #3. Un commit par extraction après validation
(vérifs vertes), référence notée dans le fichier de suivi.
