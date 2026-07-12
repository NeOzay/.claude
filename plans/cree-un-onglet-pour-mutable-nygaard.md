# Onglet "Presets de prétraitement OCR" sélectionnables par bulle

## Contexte

Le nouvel onglet « Test OCR » (déjà en place) permet d'expérimenter des
combinaisons de prétraitement (upscale, binarisation, morphologie...) sur
une image, mais ces combinaisons sont éphémères : rien n'est mémorisé
d'une session à l'autre, et rien ne permet de dire « pour CETTE bulle,
utilise toujours cette suite de traitements ».

L'utilisateur veut un troisième onglet qui permette de **composer une
série ordonnée d'étapes de prétraitement** (avec doublons autorisés — ex.
deux étapes Upscale successives), de la **nommer et l'enregistrer**, de la
**reconfigurer** plus tard, puis de la **choisir bulle par bulle** dans le
panneau latéral (exactement comme le preset de traduction existant), afin
qu'elle pilote le prétraitement appliqué lors du lancement OCR de cette
bulle précise.

Aujourd'hui, `core/ocr/preprocessing.py` n'expose que 4 presets figés en
dur dans le code (`PRESETS` dict), non persistés, non éditables par
l'utilisateur, et appliqués globalement à toute la fenêtre (pas par
bulle). Il n'existe aucune notion de preset de prétraitement en base de
données — à ne pas confondre avec la table `presets` existante, qui
concerne exclusivement la traduction (pronom, genre, glossaire).

## Approche

### 1. Persistance (DB)

**`src/manga_trad/db/schema.sql`** — nouvelle table, ajoutée après le bloc `presets` :
```sql
CREATE TABLE IF NOT EXISTS ocr_preprocessing_presets (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL UNIQUE,
    steps   TEXT NOT NULL DEFAULT '[]'   -- JSON [{"type": "...", "params": {...}}, ...] ordonné
);
```
Dans le bloc `bubbles`, ajouter une colonne juste après `preset_id` :
```sql
ocr_preprocess_preset_id INTEGER REFERENCES ocr_preprocessing_presets(id) ON DELETE SET NULL,
```
Plus un index :
```sql
CREATE INDEX IF NOT EXISTS idx_bubbles_ocr_preprocess_preset_id ON bubbles(ocr_preprocess_preset_id);
```

**`src/manga_trad/db/repository.py` — `_migrate()`** : ajouter à la liste de DDL idempotentes existante (`ALTER TABLE` protégés par `try/except sqlite3.OperationalError`) :
```python
"ALTER TABLE bubbles ADD COLUMN ocr_preprocess_preset_id INTEGER REFERENCES ocr_preprocessing_presets(id) ON DELETE SET NULL",
"CREATE INDEX IF NOT EXISTS idx_bubbles_ocr_preprocess_preset_id ON bubbles(ocr_preprocess_preset_id)",
```
(la table elle-même est créée par `schema.sql` via `executescript`, exécuté avant `_migrate()` — pas besoin de la recréer en migration).

**`src/manga_trad/db/models.py`** — nouveau dataclass, même style que `Preset` :
```python
@dataclass(slots=True)
class OcrPreprocessingPreset:
    name: str
    steps: list[dict] = field(default_factory=list)  # [{"type": str, "params": dict}, ...] ordonné
    id: int | None = None
```
Sur `Bubble`, ajouter juste après `preset_id` :
```python
ocr_preprocess_preset_id: int | None = None
```

**`src/manga_trad/db/repository.py`** — nouvelle section CRUD, symétrique à `# -- presets --` mais **avec update/delete** (contrairement à `Preset` traduction qui n'en a pas — ici nécessaire car « reconfigurer » est explicitement demandé) :
```python
def add_ocr_preprocessing_preset(self, preset: OcrPreprocessingPreset) -> OcrPreprocessingPreset: ...
def update_ocr_preprocessing_preset(self, preset: OcrPreprocessingPreset) -> None: ...   # lève ValueError si id is None
def delete_ocr_preprocessing_preset(self, preset_id: int) -> None: ...
def get_ocr_preprocessing_preset(self, preset_id: int) -> OcrPreprocessingPreset | None: ...
def list_ocr_preprocessing_presets(self) -> list[OcrPreprocessingPreset]: ...  # ORDER BY name
def count_bubbles_using_ocr_preprocess_preset(self, preset_id: int) -> int: ...  # SELECT COUNT(*) WHERE ocr_preprocess_preset_id = ?
```
`steps` sérialisé/désérialisé avec `json.dumps(preset.steps, ensure_ascii=False)` / `json.loads(row["steps"] or "[]")`, suivant exactement le pattern déjà utilisé pour `Preset.glossary` et `Bubble.ocr_results`/`tags`.

Mettre à jour `_bubble_to_params` (ajouter `bubble.ocr_preprocess_preset_id` au tuple) et `_bubble_from_row` (lire `row["ocr_preprocess_preset_id"]`), ainsi que les listes de colonnes explicites dans `add_bubble`/`update_bubble` (INSERT et UPDATE) — **attention** : ces 3 endroits (liste colonnes INSERT, liste colonnes UPDATE, tuple `_bubble_to_params`) doivent rester synchronisés en nombre et en ordre, piège de désynchronisation déjà présent dans le code actuel à ne pas aggraver.

`count_bubbles_using_ocr_preprocess_preset` sert à avertir l'utilisateur avant suppression d'un preset encore utilisé (voir section GUI) — `ON DELETE SET NULL` évite un crash mais serait sinon une régression silencieuse (une bulle perd son prétraitement dédié sans que l'utilisateur s'en aperçoive).

**Tests (`tests/db/test_repository.py`)**, suivant le style Given/When/Then existant (ex. `test_add_and_get_preset_roundtrips_glossary`) :
- `test_add_and_get_ocr_preprocessing_preset_roundtrips_steps`
- `test_update_ocr_preprocessing_preset_changes_name_and_steps`
- `test_delete_ocr_preprocessing_preset_sets_bubble_reference_to_null`
- `test_count_bubbles_using_ocr_preprocess_preset`
- `test_add_bubble_roundtrips_ocr_preprocess_preset_id`

### 2. Registre des types d'étapes (nouveau fichier)

**`src/manga_trad/core/ocr/preprocessing_registry.py`** — traduit les ~12 classes de `preprocessing.py` en entrées catalogables/sérialisables, sur le modèle de `OCR_ENGINES` dans `core/ocr/registry.py` :

```python
@dataclass(frozen=True, slots=True)
class ParamSpec:
    key: str; label: str; kind: str  # "int" | "float" | "choice"
    default: object; lo: float | None = None; hi: float | None = None
    choices: tuple[str, ...] | None = None

@dataclass(frozen=True, slots=True)
class StepType:
    key: str; label: str; params: tuple[ParamSpec, ...]
    build: Callable[[dict], Preprocessor]

STEP_TYPES: dict[str, StepType] = {...}  # "upscale", "denoise", "invert_polarity",
    # "remove_bubble_border", "binarization", "isolate_dark", "clahe", "deskew",
    # "deslant", "morphology", "unsharp_mask", "padding"

def build_pipeline(steps: list[dict]) -> PreprocessingPipeline:
    """Reconstruit une pipeline exécutable depuis le JSON stocké en base.
    Ignore silencieusement les types inconnus et les étapes dont la
    construction lève une exception (params corrompus) — ne doit jamais
    faire planter un lancement OCR."""
```

Fusion par rapport à `ocr_test_tab.py` : `binarization` devient un seul type avec paramètre `method` choice (`otsu`/`adaptive`/`sauvola`, **pas** de `"aucune"` — dans ce nouvel onglet, l'absence de l'étape = ne pas l'ajouter au menu) ; `upscale` fusionne l'interpolation (`bicubic`/`lanczos`/`realesrgan`) comme paramètre choice. Les clés stockées en JSON (`"upscale"`, `"realesrgan"`...) sont des identifiants stables distincts des libellés affichés — ne jamais y mettre le texte français affiché.

`_build_upscale(params)` gère le fallback défensif : si `interpolation == "realesrgan"` mais `realesrgan_available()` est faux, retombe sur `bicubic` sans lever d'exception (utile si un preset créé sur une machine avec Real-ESRGAN est rouvert sur une machine sans ce package).

**Tests (`tests/core/test_preprocessing_registry.py`, nouveau fichier)** :
- `test_build_pipeline_reconstructs_known_steps_in_order`
- `test_build_pipeline_ignores_unknown_step_type`
- `test_build_pipeline_falls_back_to_bicubic_when_realesrgan_unavailable`
- `test_build_pipeline_ignores_step_with_invalid_morphology_op`

### 3. Nouvel onglet GUI

**`src/manga_trad/gui/preprocessing_presets_tab.py`** (nouveau fichier) — `QWidget` en splitter 3 colonnes, sur le modèle visuel de `ocr_test_tab.py` :

- **Colonne gauche** : liste des presets sauvegardés (`QListWidget` simple, une ligne = un nom), boutons "Nouveau" (réinitialise l'éditeur), sélection d'un preset charge son nom + ses étapes dans l'éditeur.
- **Colonne centrale (éditeur)** : `QLineEdit` nom du preset, puis un combo "Ajouter un traitement" (peuplé depuis `STEP_TYPES`) + bouton "Ajouter" qui **empile une nouvelle ligne configurable** (doublons autorisés — c'est le point clé demandé). Chaque ligne a ▲/▼ pour réordonner et un bouton "✕ Supprimer" pour la retirer. Boutons "Enregistrer" (update si un preset est chargé, sinon équivalent "Enregistrer sous"), "Enregistrer sous" (nouveau nom via `QInputDialog`), "Supprimer le preset".
- **Colonne droite (aperçu, optionnel mais utile)** : réutilise le principe de `ocr_test_tab.py` — "Charger la bulle sélectionnée" / "Ouvrir une image…", bouton "Aperçu" qui applique `build_pipeline(steps_courants)` et affiche avant/après.

**Point d'architecture important — ne pas copier tel quel le pattern `ocr_test_tab.py`** : dans `ocr_test_tab.py`, `self._steps` est une liste **figée** construite une seule fois (13 lignes fixes, jamais ajoutées/retirées), et chaque ligne porte un `step_index` entier (property Qt) pointant dans cette liste fixe. Ici, les lignes sont ajoutées/retirées dynamiquement à l'exécution (c'est le besoin même de l'onglet), donc un index entier figé se désynchroniserait dès qu'une ligne est supprimée au milieu. À la place :
- Créer une petite classe `_StepRowWidget(QWidget)` qui porte directement une méthode `read_step() -> dict` (lit `type` + `params` depuis ses propres widgets internes) et se retire proprement du layout via son bouton "✕" (`layout.removeWidget(self); self.deleteLater()`).
- Maintenir une liste Python `self._rows: list[_StepRowWidget]` en parallèle (append à l'ajout, `.remove()` à la suppression) uniquement pour le comptage/validation ; pour **lire l'ordre final** (sauvegarde ou aperçu), itérer `self._steps_layout` dans son ordre visuel courant et appeler `.read_step()` sur chaque widget de ligne rencontré (widget non-None ; ignorer le stretch final) — ce sous-pattern (itérer le layout dans l'ordre visuel plutôt qu'une liste figée) est déjà utilisé par `ocr_test_tab.py._on_apply_preprocessing` et reste valable ici.
- Réordonnancement ▲/▼ : `layout.removeWidget(row); layout.insertWidget(new_idx, row)` — **jamais** `QListWidget.setItemWidget`/`takeItem` (Qt détruit le widget détaché via `deleteLater`, bug déjà rencontré et corrigé dans ce projet lors de l'implémentation de `ocr_test_tab.py`).

**Angle mort à traiter — suppression d'un preset utilisé** : avant `delete_ocr_preprocessing_preset`, appeler `repo.count_bubbles_using_ocr_preprocess_preset(preset_id)` et, si > 0, afficher une `QMessageBox.question` de confirmation explicite ("N bulles utilisent ce preset, elles repasseront sur le prétraitement global. Continuer ?") — sur le modèle de la confirmation déjà présente dans `main_window._on_delete_page`.

**Angle mort à traiter — renommage en collision** : `name` a une contrainte `UNIQUE` ; intercepter `sqlite3.IntegrityError` lors du save/update et afficher un message clair plutôt que laisser remonter l'exception brute.

**Signal exposé** : `presets_changed = Signal()`, émis après tout save/delete réussi, pour que `SidePanel` puisse rafraîchir son combo sans redémarrer l'appli.

**API publique** (même contrat que `OcrTestTab`) : `set_selected_bubble_source(image_path: str | None, region) -> None`.

Aide visuelle (angle mort C) : si une ligne "Upscale" a `interpolation == "realesrgan"` mais `realesrgan_available()` est faux au moment de l'affichage, afficher un petit indicateur "(indisponible ici, fallback bicubique à l'exécution)" à côté de cette ligne — évite qu'un preset paraisse fonctionner en Real-ESRGAN alors qu'il tourne silencieusement en bicubique.

Le helper `_np_to_pixmap` (actuellement privé dans `ocr_test_tab.py`) est dupliqué (10 lignes) dans ce nouveau fichier plutôt que déplacé/partagé, pour ne toucher à aucune ligne de `ocr_test_tab.py` (zéro risque de régression sur ce fichier déjà vérifié manuellement) — compromis pragmatique cohérent avec le fait que la définition des types de prétraitement est elle aussi dupliquée entre les deux onglets pour la même raison.

### 4. Sélection par bulle (`src/manga_trad/gui/side_panel.py`)

Ajouter un second combo dans le header, à côté du combo `_preset` (traduction), suivant très précisément le même pattern :
```python
self._preset_ocr_prep = QComboBox()
header.addRow("Prétraitement OCR", self._preset_ocr_prep)
```
- `_load_ocr_preprocess_presets()` : `clear()` + item `"(aucun — preset global)"` (data `None`) + `repo.list_ocr_preprocessing_presets()`.
- **Piège Qt à éviter (angle mort D)** : envelopper `clear()`/repeuplement dans `blockSignals(True)`/`blockSignals(False)`, et **après** repeuplement, si `self._bubble is not None`, refaire `findData(self._bubble.ocr_preprocess_preset_id)` + `setCurrentIndex` pour préserver la sélection de la bulle actuellement affichée — sinon un rafraîchissement pendant qu'une bulle est ouverte réinitialiserait silencieusement sa sélection à "(aucun)" sans que `save_current()` n'écrive quoi que ce soit nulle part (perte de données à la prochaine sauvegarde).
- Méthode publique `reload_ocr_preprocessing_presets()` (appelle `_load_ocr_preprocess_presets()`), connectée depuis `MainWindow` au signal `presets_changed` du nouvel onglet.
- `load_bubble()` : ajouter le bloc `blockSignals`/`findData`/`setCurrentIndex` pour `_preset_ocr_prep`, symétrique à celui de `_preset`.
- `save_current()` : ajouter `self._bubble.ocr_preprocess_preset_id = self._preset_ocr_prep.currentData()`.
- `_clear()` : ajouter `self._preset_ocr_prep.setCurrentIndex(0)`.
- `_set_editable()` : ajouter `self._preset_ocr_prep` au tuple de widgets (dés)activés.
- `__init__` : appeler `_load_ocr_preprocess_presets()` à côté de `_load_presets()`.

### 5. Intégration (`src/manga_trad/gui/main_window.py`)

- `__init__` : instancier `self._preprocessing_presets_tab = PreprocessingPresetsTab(repository)`, `self._central_tabs.addTab(self._preprocessing_presets_tab, "Presets de prétraitement")`, connecter `self._preprocessing_presets_tab.presets_changed.connect(self._side_panel.reload_ocr_preprocessing_presets)`.
- `_sync_ocr_test_source` : ajouter l'appel `self._preprocessing_presets_tab.set_selected_bubble_source(page.image_path, bubble.region)` en plus de celui déjà fait pour `_ocr_test_tab`.
- `_on_ocr_all_requested` : si `bubble.ocr_preprocess_preset_id is not None`, charger le preset via `self._repo.get_ocr_preprocessing_preset(...)` et construire la pipeline via `build_pipeline(preset.steps)` (import depuis `core.ocr.preprocessing_registry`) au lieu de `self._preprocessor` (pipeline globale de la toolbar) ; fallback sur `self._preprocessor` si aucun preset choisi pour cette bulle ou si le preset référencé n'existe plus (`get_ocr_preprocessing_preset` renvoie `None`).
- `_update_side_docks_visibility` : **aucune modification nécessaire**, déjà générique (`currentWidget() is self._canvas`), se généralise correctement au 3ᵉ onglet.

## Fichiers concernés

- `src/manga_trad/db/schema.sql` — nouvelle table + colonne + index
- `src/manga_trad/db/models.py` — `OcrPreprocessingPreset`, champ sur `Bubble`
- `src/manga_trad/db/repository.py` — migration, CRUD, `_bubble_to_params`/`_bubble_from_row`
- `tests/db/test_repository.py` — tests roundtrip/CRUD
- `src/manga_trad/core/ocr/preprocessing_registry.py` (nouveau) — registre + `build_pipeline`
- `tests/core/test_preprocessing_registry.py` (nouveau) — tests registre
- `src/manga_trad/gui/preprocessing_presets_tab.py` (nouveau) — onglet
- `src/manga_trad/gui/side_panel.py` — combo preset prétraitement par bulle
- `src/manga_trad/gui/main_window.py` — intégration 3ᵉ onglet + application à l'OCR

`src/manga_trad/gui/ocr_test_tab.py` et `src/manga_trad/core/ocr/preprocessing.py` (classes `Preprocessor` existantes) **ne sont pas modifiés** — seulement consommés/importés par le nouveau registre.

## Vérification

1. **Tests automatisés** : `uv run pytest -q` — les nouveaux tests DB (`test_repository.py`) et registre (`test_preprocessing_registry.py`) doivent passer, ainsi que la suite existante (58 tests actuellement) sans régression.
2. **Test manuel GUI** (pas de précédent de test Qt automatisé dans ce repo — confirmé par exploration ; à documenter comme vérification manuelle) :
   - Lancer `uv run manga-trad manga_trad.db`, ouvrir l'onglet "Presets de prétraitement".
   - Composer un preset avec au moins deux fois le même type d'étape (ex. deux "Upscale" avec des échelles différentes), vérifier le réordonnancement ▲/▼, l'enregistrer sous un nom.
   - Recharger le preset (sélection dans la liste de gauche), vérifier que les étapes et leurs paramètres sont fidèlement restaurés dans le même ordre.
   - Basculer sur l'onglet Édition, sélectionner une bulle, choisir ce preset dans le nouveau combo "Prétraitement OCR" du panneau latéral, sauvegarder la bulle, cliquer "Lancer tous les OCR" — vérifier que le résultat diffère de celui obtenu avec le preset global de la toolbar (preuve que le pipeline par bulle est bien utilisé).
   - Supprimer un preset utilisé par au moins une bulle — vérifier l'avertissement de confirmation, puis que la bulle repasse bien sur "(aucun — preset global)" après suppression confirmée.
   - Renommer un preset existant vers un nom déjà pris — vérifier qu'un message d'erreur clair s'affiche (pas de crash/traceback brut).
3. **Smoke test headless** (comme pratiqué dans les sessions précédentes de ce projet) : `QT_QPA_PLATFORM=offscreen uv run python -c "..."` instanciant `MainWindow` avec un `Repository.connect(':memory:')` pour vérifier l'absence d'exception à la construction des 3 onglets.
