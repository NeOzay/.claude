# Découplage GUI/DB : déplacer db/ et les controllers sous core/

## Contexte

Objectif énoncé par l'utilisateur : *"l'interface ne définisse aucune logique
pour la manipulation des données"*, avec l'idée que `core/` pilote directement
la DB. L'exploration a montré que ce n'est pas encore le cas : 8 widgets Qt
(`main_window.py`, `main_toolbar.py`, `page_bar.py`, `chapter_filter_bar.py`,
`ocr_patterns_tab.py`, `preprocessing_presets_tab.py`, `side_panel/panel.py`,
`side_panel/preset_selector.py`) reçoivent le `Repository` brut en injection
et l'appellent directement — certains avec de la vraie logique métier mêlée
(agrégation multi-pages pour le mining OCR, traduction de
`sqlite3.IntegrityError` en dialogue utilisateur, read-modify-write dupliqué).
Par ailleurs `db/` vit à la racine de `manga_trad/`, séparé de `core/`, alors
qu'il ne dépend ni de Qt ni du reste de `core/` (dépendance strictement
unidirectionnelle confirmée par grep).

Décision de conception validée avec l'utilisateur : les controllers
(actuellement dans `gui/controllers/`) déménagent aussi sous `core/`
(`core/services/`), puisqu'ils portent de la logique métier sans dépendre de
Qt — `gui/` ne fera plus qu'appeler ces services et gérer l'affichage/les
confirmations utilisateur. Le mining de patterns OCR reste en flux
retour-puis-confirmation-puis-upsert (pas d'écriture DB automatique).

Résultat attendu : `core/` regroupe toute la logique de manipulation de
données (DB + services), `gui/` ne fait plus jamais `self._repo.xxx()`, plus
aucun `import sqlite3` côté GUI.

## Étape A — Déplacer `db/` → `core/db/`

- `git mv src/manga_trad/db src/manga_trad/core/db` (contenu interne
  inchangé : mixins `PagesMixin`, `ChaptersMixin`, `PresetsMixin`,
  `OcrPreprocessingPresetsMixin`, `BubblesMixin`, `TranslationMemoryMixin`,
  `OcrPatternsMixin` + `RepositoryBase`).
- Renommer les imports `manga_trad.db.` → `manga_trad.core.db.` dans tous les
  fichiers concernés : `src/manga_trad/__init__.py`,
  `cli/mine_patterns.py`, `core/imaging.py`, `core/ocr/mining.py`,
  `core/ocr/patterns.py`, `core/ocr/preprocessing/registry.py`, tous les
  `gui/*.py` et `gui/controllers/*.py` qui importent `Repository`/`db.models`,
  et tous les tests (`tests/**`).
- Vérifier que `_apply_locking()` (dans `core/db/repository/__init__.py`,
  monkey-patch de verrouillage `RLock` sur chaque méthode des mixins à
  l'import) s'exécute toujours exactement une fois — pas de shim de
  compatibilité `manga_trad.db` à créer (l'utilisateur veut un renommage
  complet, pas un alias).
- Vérification : `grep -rn "manga_trad\.db\." src/ tests/` ne doit plus rien
  retourner en dehors de `core/db/` lui-même. Puis `uv run pytest`,
  `uv run ruff check .`, `uv run basedpyright` — cette étape est un no-op
  comportemental.

## Étape B — Déplacer les controllers vers `core/services/` + combler les trous

`git mv src/manga_trad/gui/controllers src/manga_trad/core/services`
(renommer le dossier ; garder les noms de fichiers/classes existants :
`page_controller.py`, `chapter_controller.py`, `ocr_controller.py`). Mettre à
jour tous les imports GUI (`from manga_trad.core.services.page_controller
import PageController`, etc.).

### B.1 Extension de `PageController`
```python
def get_page(self, page_id: int) -> Page:      # lève ValueError si absente
def list_pages(self, *, chapter_id: int | None = None, search: str | None = None) -> list[Page]
def delete_page(self, page_id: int) -> None
```
`get_bubble`/`list_bubbles_for_page` existent déjà — vérifier qu'ils sont
bien sans effet de bord avant de les réutiliser tels quels dans `page_bar.py`
et `ocr_patterns_tab.py`.

### B.2 Extension de `ChapterController`
```python
def get_chapter(self, chapter_id: int) -> Chapter   # lève ValueError si absent
```

### B.3 Nouveau `core/services/ocr_patterns_controller.py`
```python
class OcrPatternsController:
    def __init__(self, repository: Repository) -> None: ...
    def list_ocr_patterns(self) -> list[OcrPattern]: ...
    def delete_ocr_pattern(self, pattern_id: int) -> None: ...
    def delete_ocr_patterns(self, pattern_ids: Iterable[int]) -> None: ...
    def upsert_ocr_patterns(self, patterns: Sequence[...]) -> None: ...
    def mine_patterns_from_chapter(self, chapter_id: int | None = None) -> list[...]:
        """Reproduit exactement la logique actuelle de
        ocr_patterns_tab.py::_on_analyze_clicked : liste les pages (filtrées
        par chapter_id si fourni), agrège list_bubbles_for_page, filtre
        ocr_validated=True + ocr_results non vide, appelle
        core.ocr.mining.mine_patterns(...) et RETOURNE le résultat sans
        écrire en base — le widget affiche, demande confirmation, puis
        appelle upsert_ocr_patterns() séparément."""
```

### B.4 Nouveau `core/services/ocr_preprocessing_presets_controller.py`
```python
class PresetNameAlreadyExistsError(Exception): ...

class OcrPreprocessingPresetsController:
    def __init__(self, repository: Repository) -> None: ...
    def list_presets(self) -> list[OcrPreprocessingPreset]: ...
    def get_preset(self, preset_id: int) -> OcrPreprocessingPreset: ...  # ValueError si absent
    def add_preset(self, name: str, ...) -> OcrPreprocessingPreset:
        """try/except sqlite3.IntegrityError -> raise PresetNameAlreadyExistsError"""
    def update_preset(self, preset_id: int, name: str, ...) -> None:
        """même traduction d'exception"""
    def count_bubbles_using_preset(self, preset_id: int) -> int: ...
    def delete_preset(self, preset_id: int) -> None: ...
```
Seul endroit qui importera encore `sqlite3` — c'est la couche de traduction
prévue à cet effet. Élimine la duplication actuelle du try/except (présente
2× dans `preprocessing_presets_tab.py`, dans `_on_save_clicked` et
`_on_save_as_clicked`). La logique "compter usages → confirmer avec
`QMessageBox` → supprimer" reste dans le widget (la confirmation est de la
présentation), mais `count_bubbles_using_preset()`/`delete_preset()`
viennent du controller.

### B.5 Nouveau `core/services/preset_controller.py`
```python
class PresetController:
    def __init__(self, repository: Repository) -> None: ...
    def list_presets(self) -> list[Preset]: ...
    def get_preset(self, preset_id: int) -> Preset: ...  # ValueError si absent
```
Domaine glossaire/tags, distinct des presets de prétraitement OCR (mixins DB
séparés). `side_panel/preset_selector.py` consommera ce controller **et**
`OcrPreprocessingPresetsController` — pas d'extension artificielle de l'un
dans l'autre. `merge_tags()` (merge de dict sur données déjà chargées) reste
dans le widget.

### Vérification étape B
Ajouts additifs, aucun widget ne les utilise encore.
```
uv run pytest tests/core/services/   # nouveaux tests pour les controllers créés/étendus
uv run ruff check src/manga_trad/core/services/
uv run basedpyright
```

## Étape C — Migrer les widgets un par un (1 commit testable par sous-étape)

Câblage cible dans `MainWindow.__init__` :
```python
self._repo = Repository(...)   # reste privé, ne sert plus qu'à construire les services
self._page_controller = PageController(self._repo)
self._chapter_controller = ChapterController(self._repo, copy_image=...)
self._ocr_controller = OcrController(self._repo)
self._ocr_patterns_controller = OcrPatternsController(self._repo)
self._ocr_prep_presets_controller = OcrPreprocessingPresetsController(self._repo)
self._preset_controller = PresetController(self._repo)
```
Aucun widget ne doit plus recevoir `repository` en argument après cette
étape.

Ordre (du plus isolé au plus risqué) :

1. **`main_toolbar.py`** — `repository` → `ocr_prep_presets_controller`.
   `list_ocr_preprocessing_presets()` → `.list_presets()`.
2. **`chapter_filter_bar.py`** — `repository` → `chapter_controller,
   page_controller`. Pass-through direct.
3. **`page_bar.py`** — `repository` → `page_controller`. L'agrégation
   compte validé/total reste dans le widget (affichage seul).
4. **`side_panel/preset_selector.py`** — `repository` →
   `preset_controller, ocr_prep_presets_controller`.
5. **`side_panel/panel.py`** — `repository` → `page_controller` (garde
   `OcrController`). Dans `save_current()` : lire précisément quels champs
   sont mutés avant d'écrire, puis remplacer le
   re-fetch+mutation+`update_bubble` actuel par la méthode `PageController`
   équivalente (`update_bubble_region`/`reorder_bubble`, ou une nouvelle
   méthode si aucune ne correspond exactement) — **vraie déduplication**, à
   ne pas traiter comme un simple pass-through. Conserver la garantie
   anti-staleness (re-fetch avant mutation) dans le controller.
6. **`ocr_patterns_tab.py`** — `repository` → `ocr_patterns_controller`.
   `_on_analyze_clicked` → `mine_patterns_from_chapter(...)` puis, après
   confirmation utilisateur, `upsert_ocr_patterns(...)`. Plus gros gain de
   simplicité du refactor (toute l'orchestration list_pages +
   list_bubbles_for_page + filtre + mining sort du widget).
7. **`preprocessing_presets_tab.py`** (en dernier, cas le plus dense) —
   supprimer `import sqlite3` ; `repository` → `ocr_prep_presets_controller`
   (garde `OcrController` pour la preview) ; `_on_save_clicked`/
   `_on_save_as_clicked` attrapent `PresetNameAlreadyExistsError` au lieu de
   `sqlite3.IntegrityError` ; `count_bubbles_using_ocr_preprocess_preset` →
   `count_bubbles_using_preset`, confirmation `QMessageBox` inchangée,
   `delete_ocr_preprocessing_preset` → `delete_preset`.
8. **`main_window.py`** (dernier, agrège tout) — remplacer les 16
   call-sites `self._repo.*` : `get_page`×4 →
   `page_controller.get_page`, `list_pages`×5 →
   `page_controller.list_pages`, `get_bubble`×3 →
   `page_controller.get_bubble`, `get_chapter`×2 →
   `chapter_controller.get_chapter`, `list_chapters` (doublon ~L445,
   `chapter_controller.list_chapters()` existe déjà ailleurs dans le même
   fichier — corriger l'oubli), `delete_page`×1 →
   `page_controller.delete_page`. Mettre à jour tous les constructeurs de
   widgets instanciés dans `MainWindow.__init__` pour passer les services au
   lieu de `self._repo`.

### Vérification finale
```
grep -rn "self\._repo\b" src/manga_trad/gui/ --include=*.py | grep -v main_window.py   # doit être vide
grep -rn "^import sqlite3" src/manga_trad/gui/                                          # doit être vide
uv run pytest
uv run ruff check .
uv run basedpyright
```
Puis lancer l'app (via la skill `run` si disponible) et vérifier
manuellement : navigation page/chapitre, édition de bulle (side panel),
analyse + confirmation de mining OCR patterns, gestion presets de
prétraitement (save / save-as avec collision de nom / delete avec bulles
utilisatrices).

## Points de vigilance transverses

- **Threading OCR** : la connexion SQLite est partagée GUI/pool OCR
  (`check_same_thread=False` + `RLock` au niveau méthode, pas de garantie
  transactionnelle cross-appel). Préexistant, ne pas essayer de le corriger
  ici ; ne pas ajouter de cache local dans les nouveaux services sans
  revérifier `gui/controllers/ocr_task_manager.py` (devient
  `core/services/...` mais reste appelé depuis la GUI de la même façon).
- **`mine_patterns_from_chapter`** est le changement le plus à risque de
  régression silencieuse (reproduire exactement le filtre
  `ocr_validated`+`ocr_results`) — ajouter un test qui verrouille ce
  comportement avant de toucher `ocr_patterns_tab.py`.
- Un commit par sous-étape (A, B, puis C.1 à C.8) pour rester
  `git bisect`-able.
