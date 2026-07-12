# Plan — Notion de chapitre (regroupement de pages)

## Contexte

La base de données représente une œuvre entière et doit gérer un grand
nombre de pages. Actuellement `pages` est une table plate, sans aucun
regroupement : la seule navigation possible est une bande horizontale de
vignettes (`PageBar`) qui liste **toutes** les pages du volume, ce qui ne
tient pas à l'échelle d'une œuvre complète.

Objectif : introduire des **chapitres** pour regrouper les pages, avec
CRUD chapitre, un filtre/recherche dans la navigation, et un import en
masse de pages assignées à un chapitre. Décisions déjà validées avec
l'utilisateur (non renégociables) :

1. `bubbles.reading_order` reste **global à l'œuvre**, comportement
   inchangé.
2. Suppression d'un chapitre = **cascade** (pages + bulles), avec
   confirmation forte côté GUI.
3. Import en masse : tri par **nom de fichier, ordre croissant**.
4. `PageBar` existante reste la navigation principale ; on **ajoute** un
   menu déroulant chapitre (filtre + aperçu premières pages) et une
   barre de recherche (page **et** titre de chapitre) — pas de refonte.
5. Ordre des chapitres = numérotation fixe (pas de drag&drop).

Aucune notion de chapitre n'existe dans le code actuel (vérifié par
exploration) — tout est à créer.

**Décision de conception : `pages.page_order` reste unique globalement au
volume** (pas d'unicité par chapitre), par symétrie avec `reading_order`
(décision #1), et parce qu'une contrainte composite `(chapter_id,
page_order)` nécessiterait de recréer la table (SQLite ne permet pas de
modifier une contrainte UNIQUE existante par simple `ALTER TABLE`). Le
chapitre reste une étiquette de regroupement/filtrage, pas une nouvelle
unité d'ordonnancement. L'affichage "page N du chapitre" est un rang
calculé à l'affichage, pas une colonne stockée.

Le plan est séquencé en étapes livrables indépendamment : **A** backend
pur (schéma/modèles/repository) → **B** controllers GUI → **C** UI
synchrone (filtre, CRUD, import) → **D** vignettes asynchrones
(optionnel, additif) → **E** tests.

## Étape A — Schéma, modèles, repository

- `src/manga_trad/db/schema.sql` : ajouter
  `CREATE TABLE IF NOT EXISTS chapters (id INTEGER PRIMARY KEY
  AUTOINCREMENT, chapter_number INTEGER NOT NULL UNIQUE, title TEXT NOT
  NULL DEFAULT '')`. Ne pas ajouter `pages.chapter_id` ici — suivre le
  pattern déjà documenté en commentaire (schema.sql:47-50) : toute
  colonne ajoutée à une table existante doit passer par `_migrate()`,
  jamais par `schema.sql` directement (casserait l'ouverture d'une base
  préexistante).
- `src/manga_trad/db/repository/base.py::RepositoryBase._migrate()` :
  ajouter deux DDL au pattern `try/except sqlite3.OperationalError`
  existant (base.py:50-71) :
  `ALTER TABLE pages ADD COLUMN chapter_id INTEGER REFERENCES
  chapters(id) ON DELETE CASCADE` (nullable — pages existantes restent
  valides) et `CREATE INDEX IF NOT EXISTS idx_pages_chapter_id ON
  pages(chapter_id)`. `PRAGMA foreign_keys = ON` est déjà actif
  (base.py:26), donc `ON DELETE CASCADE` déclenche automatiquement la
  suppression cascade pages→bulles (déjà en place via
  `bubbles.page_id ... ON DELETE CASCADE`) : **aucune logique cascade
  manuelle à écrire côté Python**, `delete_chapter` reste un simple
  `DELETE FROM chapters WHERE id = ?`.
- `src/manga_trad/db/models.py` : ajouter
  `@dataclass(slots=True) class Chapter: chapter_number: int; title: str
  = ""; id: int | None = None`. Étendre `Page` avec `chapter_id: int |
  None = None` en dernière position (compat rétro, tous les appels
  existants sont en kwargs).
- `src/manga_trad/db/repository/chapters.py` (nouveau) : `ChaptersMixin`
  suivant exactement le pattern de `pages.py` (add/rename/delete/get/
  list/`next_chapter_number` sur le modèle de `max_reading_order`).
- `src/manga_trad/db/repository/pages.py` : `add_page` inclut
  `chapter_id` dans l'INSERT ; `_page_from_row` inclut
  `chapter_id=row["chapter_id"]` ; `list_pages(chapter_id: int | None =
  None, search: str | None = None)` — sans arguments comportement
  strictement inchangé (non-régression), avec `chapter_id` ajoute
  `WHERE chapter_id = ?`, avec `search` ajoute un `LEFT JOIN chapters`
  et filtre sur nom de fichier **ou** titre de chapitre. Filtres
  cumulables.
- `src/manga_trad/db/repository/__init__.py` : importer `ChaptersMixin`,
  l'ajouter à `_MIXINS` (ligne 26-33) et à la liste de bases de
  `Repository` (ligne 45-53). `_apply_locking()` s'applique
  automatiquement.

## Étape B — Controllers GUI

- `src/manga_trad/gui/controllers/chapter_controller.py` (nouveau) :
  `ChapterController(repository, copy_image: Callable[[str], str])` —
  contrôleur dédié (même logique que `OcrController` séparé de
  `PageController`), avec `copy_image` **injecté** depuis
  `PageController.copy_image` existant (pas de dépendance directe entre
  contrôleurs, testable avec un callable factice).
  - `list_chapters`, `create_chapter(title)` (calcule
    `next_chapter_number` puis délègue), `rename_chapter`,
    `delete_chapter` (délégation simple, pas de confirmation ici).
  - `import_pages_bulk(image_paths, chapter_id) -> list[Page]` : trie
    par nom de fichier croissant via
    `sorted(image_paths, key=lambda p: Path(p).name)` — corrige le tri
    actuel de `main_window.py:297` qui trie les chemins complets. Calcule
    `next_order` global comme aujourd'hui, copie via `copy_image` injecté,
    crée chaque `Page(chapter_id=...)`, retourne la liste créée.
- `src/manga_trad/gui/controllers/page_controller.py` : aucune
  modification, `copy_image`/`images_dir` réutilisés tels quels.

## Étape C — UI

- `src/manga_trad/gui/chapter_filter_bar.py` (nouveau) :
  `ChapterFilterBar(QWidget)`, signal `filter_changed(object, str)`
  (chapter_id, search_text). `QComboBox` chapitre (item "Tous les
  chapitres" en tête, `data=None`), icône = vignette de la première page
  du chapitre via `make_thumb_icon`/`gui/utils.py` (réutiliser
  `_ICON_SIZE`). `QLineEdit` recherche avec debounce `QTimer` (~250ms,
  même idée que `_auto_ocr_timer` dans `main_window.py:70-72`).
  `reload_chapters()` public.
- `src/manga_trad/gui/page_bar.py` : évolution minimale — `reload(self,
  chapter_id: int | None = None, search: str | None = None)` transmet
  ces paramètres à `self._repo.list_pages(...)`. Défauts `None`
  préservent tous les appels existants sans argument (`page_bar.py:57`
  et tous les `self._page_bar.reload()` dans `main_window.py`). Stocker
  `_current_chapter_id`/`_current_search` pour que les rechargements
  déclenchés par d'autres actions (suppression bulle/page) conservent le
  filtre actif.
- `src/manga_trad/gui/main_window.py` :
  - Instancier `self._chapter_controller = ChapterController(repository,
    copy_image=self._controller.copy_image)`.
  - Remplacer `top_dock.setWidget(self._page_bar)` (main_window.py:90)
    par un conteneur `QWidget`/`QVBoxLayout` contenant
    `self._chapter_filter_bar` puis `self._page_bar`.
  - Connecter `filter_changed` → nouveau slot `_on_page_filter_changed`
    qui appelle `self._page_bar.reload(chapter_id, search)`.
  - `_on_import_page` (main_window.py:285-307) : si des chapitres
    existent, demander le chapitre cible via `QInputDialog.getItem`
    avant la boucle ; remplacer la boucle manuelle par
    `self._chapter_controller.import_pages_bulk(paths, chapter_id)`.
  - Nouveaux slots `_on_new_chapter`/`_on_rename_chapter`/
    `_on_delete_chapter` : `QInputDialog.getText` pour créer/renommer ;
    pour la suppression, reprendre le pattern `QMessageBox.question` de
    `_on_delete_page` (main_window.py:309-322) en renforçant le message
    avec le nombre de pages impactées (`len(repo.list_pages(chapter_id=
    cid))`) et `defaultButton=No`.
- `src/manga_trad/gui/main_toolbar.py` : ajouter une section "Chapitres :"
  après le séparateur existant (main_toolbar.py:48) avec trois
  `QAction` (`new_chapter_action`, `rename_chapter_action`,
  `delete_chapter_action`), exposées en attributs publics suivant le
  pattern documenté en tête de classe ; `MainWindow._connect_signals`
  les connecte aux slots ci-dessus.

## Étape D — Vignettes asynchrones (optionnel, additif)

Objectif : éviter de bloquer l'UI quand `PageBar.reload()` régénère de
nombreuses vignettes après un import en masse. Réutilise exactement le
pattern `OcrJob`/`OcrTaskManager` (`gui/workers/ocr_worker.py`,
`gui/controllers/ocr_task_manager.py`) :

- `src/manga_trad/gui/workers/thumbnail_worker.py` (nouveau) :
  `ThumbnailJobSignals`/`ThumbnailJob(QRunnable)` — charge/redimensionne
  l'image **hors thread GUI** via numpy/PIL (pas de `QPixmap`/`QIcon`
  dans `run()`, contrainte Qt), émet un tableau numpy.
- `src/manga_trad/gui/controllers/thumbnail_task_manager.py` (nouveau) :
  même squelette que `OcrTaskManager` (génération/annulation de jobs
  obsolètes), mais `QThreadPool` peut avoir plusieurs threads (pas de
  cache partagé non thread-safe comme pour l'OCR) — ex.
  `min(4, os.cpu_count() or 1)`. `wait_for_pending()` appelé dans
  `MainWindow.closeEvent` aux côtés de `self._ocr_task_manager.
  wait_for_pending()` (main_window.py:384-386).
- `page_bar.py` : constructeur accepte `thumbnail_manager:
  ThumbnailTaskManager | None = None` (défaut `None` = chemin synchrone
  actuel inchangé, livrable indépendamment de D). Si fourni, `reload()`
  crée les items avec icône vide puis demande chaque vignette au
  manager ; slot `_on_thumbnail_ready(page_id, arr)` retrouve l'item et
  appelle `make_thumb_icon(np_to_pixmap(arr))` **sur le thread GUI**
  (contrainte documentée dans `gui/utils.py`).

## Étape E — Tests

- `tests/db/test_repository.py` : CRUD chapitres, et surtout
  `test_delete_chapter_cascades_to_pages_and_bubbles` (prouve que le
  `ON DELETE CASCADE` SQL suffit, sans code Python), pattern d'isolation
  repris de `test_delete_page_does_not_affect_other_pages`
  (test_repository.py:286), tests de `list_pages` avec/sans filtres
  (non-régression explicite du comportement par défaut).
- `tests/gui/test_page_controller.py` : ajouter
  `test_create_bubble_reading_order_is_global_across_chapters`, calqué
  sur `test_create_bubble_on_second_page_uses_global_max_order`
  (test_page_controller.py:99), pour prouver que la décision #1 survit
  à l'introduction des chapitres.
- `tests/gui/test_chapter_controller.py` (nouveau) : reprendre les
  fixtures `repo`/`pid`/`not_none` de `test_page_controller.py`. Cas
  clé : `test_import_pages_bulk_sorts_by_filename_not_full_path` (chemins
  dont l'ordre des chemins complets diffère de l'ordre des noms de
  fichiers seuls), `test_import_pages_bulk_uses_injected_copy_image`
  (callable factice, pas de disque).
- `tests/gui/test_thumbnail_task_manager.py` (nouveau, étape D) :
  dupliquer le pattern de `test_ocr_task_manager.py` (fixture `qapp`,
  source factice avec gates/résultats/exceptions).

## Vérification

- `uv run ruff check .` et `uv run ruff format .`.
- `uv run basedpyright`.
- `uv run pytest` (en particulier les nouveaux tests de cascade et de
  tri d'import).
- Test manuel GUI : lancer l'appli, créer 2 chapitres, importer un lot
  de pages avec noms non triés par défaut du système de fichiers
  (vérifier l'ordre résultant), filtrer via le combo chapitre et la
  recherche, supprimer un chapitre non vide et vérifier la confirmation
  + la disparition des pages/bulles associées.
