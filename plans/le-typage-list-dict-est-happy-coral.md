# Remplacer `list[dict]` par une dataclass typée pour les steps de prétraitement OCR

## Contexte

`OcrPreprocessingPreset.steps` (db/models.py) et `build_pipeline()`
(core/ocr/preprocessing/registry.py) manipulent des `list[dict]` bruts pour
représenter les étapes de prétraitement OCR (`{"type": str, "enabled": bool,
"params": dict}`). Ce typage est fragile : accès par clé sans vérification
statique, logique de valeurs par défaut (`.get(..., default)`) dupliquée à la
frontière JSON (repository) et dans le code GUI, et une dérive silencieuse
déjà constatée — le commentaire du modèle décrit `{"type", "params"}` mais le
code gère aussi `"enabled"` depuis un moment sans que rien ne l'ait signalé.
Basedpyright ne peut rien vérifier sur ces accès par clé.

Objectif : introduire une dataclass `PreprocessingStepConfig` (même style que
le reste de `db/models.py`) pour porter ce contrat, avec sérialisation JSON
isolée à la frontière repository. Le format JSON persisté en base ne change
pas (juste la représentation Python en mémoire) — aucune migration nécessaire,
compat totale avec les presets déjà stockés.

`params: dict[str, object]` reste volontairement un sac hétérogène (clés
différentes selon le type d'étape, déjà documentées via `ParamSpec`/`StepType`
pour la GUI) — ne pas le typer plus finement.

## Implémentation

### 1. `src/manga_trad/db/models.py`

Ajouter avant `OcrPreprocessingPreset` :

```python
@dataclass(slots=True)
class PreprocessingStepConfig:
    type: str
    params: dict[str, object] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> dict:
        return {"type": self.type, "enabled": self.enabled, "params": self.params}

    @classmethod
    def from_dict(cls, data: dict) -> PreprocessingStepConfig:
        return cls(
            type=data.get("type", ""),
            params=data.get("params", {}),
            enabled=data.get("enabled", True),
        )
```

Et changer `OcrPreprocessingPreset.steps: list[dict]` en
`list[PreprocessingStepConfig]`.

### 2. `src/manga_trad/db/repository/ocr_preprocessing_presets.py`

- Import `PreprocessingStepConfig`.
- `add_`/`update_ocr_preprocessing_preset` : sérialiser via
  `json.dumps([s.to_dict() for s in preset.steps], ensure_ascii=False)`.
- `_ocr_preprocessing_preset_from_row` : désérialiser via
  `steps=[PreprocessingStepConfig.from_dict(s) for s in json.loads(row["steps"] or "[]")]`.

### 3. `src/manga_trad/core/ocr/preprocessing/registry.py`

Import `PreprocessingStepConfig` depuis `manga_trad.db.models` (couplage déjà
existant ailleurs dans `core/` via `mining.py`/`patterns.py` → pas une
nouvelle direction de dépendance).

```python
def build_pipeline(steps: list[PreprocessingStepConfig]) -> PreprocessingPipeline:
    built: list[Preprocessor] = []
    for step in steps:
        if not step.enabled:
            continue
        step_type = STEP_TYPES.get(step.type)
        if step_type is None:
            continue
        try:
            built.append(step_type.build(step.params))
        except Exception:
            continue
    return PreprocessingPipeline(built)
```

Le try/except autour de `step_type.build()` reste nécessaire (défense contre
des `params` corrompus/incompatibles), seul l'accès aux clés `type`/`enabled`
devient typé.

### 4. `src/manga_trad/gui/preprocessing_step_row.py`

`read_step()` retourne `PreprocessingStepConfig(type=..., enabled=..., params=...)`
au lieu d'un dict. Import à ajouter.

### 5. `src/manga_trad/gui/preprocessing_presets_tab.py`

- `_collect_steps(self) -> list[PreprocessingStepConfig]` (corps inchangé).
- `_load_preset_into_editor` : `for step in preset.steps:
  self._add_step_row(step.type, step.params, step.enabled)`.
- Import `PreprocessingStepConfig`.

### 6. `src/manga_trad/gui/preprocessing_preview_panel.py`

`steps_provider: Callable[[], list[PreprocessingStepConfig]]` (import ajouté).
Le corps qui passe `self._steps_provider()` à `build_pipeline` ne change pas.

### 7. `src/manga_trad/gui/controllers/ocr_controller.py`

Aucun changement : `build_pipeline(preset.steps)` fonctionne tel quel une fois
`preset.steps` typé.

### 8. Tests à adapter

- `tests/db/test_repository.py` (lignes ~317-354) : remplacer les dicts bruts
  par `PreprocessingStepConfig(type=..., params={...})` ; comparer les objets
  directement (`fetched.steps == [PreprocessingStepConfig(...), ...]`, `__eq__`
  généré par la dataclass) plutôt que repasser par `.to_dict()`.
- `tests/core/ocr/test_preprocessing_registry.py` (5 tests) : remplacer chaque
  `steps = [{"type": ..., "params": {...}}]` par
  `steps = [PreprocessingStepConfig(type=..., params={...})]`.

### 9. Nettoyage mineur

Mettre à jour le commentaire JSON dans `schema.sql` (`-- JSON [{"type": "...",
"params": {...}}, ...]`) pour mentionner `"enabled"`, en cohérence avec le
format réellement stocké.

## Ordre d'implémentation

1. `db/models.py` (fondation).
2. `db/repository/ocr_preprocessing_presets.py` + test associé.
3. `core/ocr/preprocessing/registry.py` + test associé.
4. GUI : `preprocessing_step_row.py` → `preprocessing_presets_tab.py` →
   `preprocessing_preview_panel.py` (ordre du flux de données).
5. Vérifier `ocr_controller.py` (aucun changement attendu).

## Vérification

- `uv run basedpyright` : doit passer sans nouvelle erreur, confirme qu'aucun
  call site n'a été oublié.
- `uv run pytest tests/db/test_repository.py tests/core/ocr/test_preprocessing_registry.py` :
  doit passer après adaptation.
- `uv run pytest` (suite complète) pour non-régression globale.
- `uv run ruff check . && uv run ruff format .`.
- Test manuel GUI : ouvrir l'onglet presets de prétraitement, créer/modifier
  un preset avec plusieurs étapes (dont une désactivée), sauvegarder, recharger
  l'app, vérifier que le preset se recharge à l'identique et que l'aperçu
  (preview panel) applique bien le pipeline.
