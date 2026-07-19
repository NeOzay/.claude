# Refonte du lot Ollama en système générique de lot différé

## Contexte

L'implémentation actuelle (`.claude/implementation/ollama-batch-ocr.md`,
étape 12/12) fonctionne mais crée de la dette : une classe
`OllamaBatchController` dédiée, un flag `include_ollama` propagé sur 6
fichiers, et un filtrage par préfixe de nom (`"Ollama ("`) au lieu de
s'appuyer sur le protocole. L'utilisateur a déjà uniformisé
`core/ocr/base.py` : `OcrEngine` porte maintenant un attribut
`immediate: bool` (True pour les moteurs CPU, False pour Ollama) et
`recognize_batch` fait partie du protocole (avec fallback séquentiel dans
`OcrEngineBase`). Le but de ce chantier : supprimer `OllamaBatchController`
et tout son solde GUI dédié, et faire porter le mécanisme de lot
directement par `OcrController`, générique à *tout* moteur
`immediate=False` (pas seulement Ollama). Logique commune extraite dans un
nouveau fichier `utils.py`. Renommage de l'UI et des classes en
terminologie générique ("lot différé") — décidé avec l'utilisateur, pas de
mention Ollama en dur ailleurs que dans le nom des moteurs eux-mêmes.

## Fichiers supprimés

- `src/manga_trad/core/services/ollama_batch_controller.py`
- `src/manga_trad/gui/controllers/ollama_batch_queue.py`
- `src/manga_trad/gui/workers/ollama_batch_worker.py`
- `tests/core/services/test_ollama_batch_controller.py`
- `tests/gui/test_ollama_batch_queue.py`

(`tests/core/ocr/test_ollama_adapter_batch.py` est conservé tel quel — il
teste l'adaptateur, pas le contrôleur de lot.)

## Fichiers créés

**`src/manga_trad/core/services/utils.py`** — logique générique extraite,
partagée entre `run_ocr_for_bubble` et le nouveau lot différé :

- `prepare_bubble_crop(repo, ocr_controller, bubble_id) -> tuple[Bubble, np.ndarray] | None`
  — factorise le couple (charger bulle+page, `crop_region`, appliquer
  `ocr_controller.pipeline_for_bubble`) actuellement dupliqué entre
  `OcrController.run_ocr_for_bubble` et `OllamaBatchController._prepare`.
- `postprocess_result(repo, raw: OcrResult) -> OcrResult` — factorise
  `penalize_false_positives` + `apply_patterns` + `normalize_ocr`,
  actuellement dupliqué entre `_run_engine_postprocessed` et la boucle de
  `OllamaBatchController.run_batch`.
- `persist_vote(repo, bubble, combined: list[tuple[str, OcrResult]]) -> OcrResult | None`
  — construit `bubble.ocr_results`, vote via `vote_results` (voting.py,
  déjà générique), assigne `bubble.ocr`/`ocr_confidence`, persiste via
  `repo.bubbles.update`, retourne le résultat voté.

**`src/manga_trad/gui/workers/deferred_batch_worker.py`** (remplace
`ollama_batch_worker.py`) — `DeferredBatchJob`/`DeferredBatchJobSignals`,
identique à `OllamaBatchJob` mais la Protocol `DeferredBatchControllerLike`
exige `run_deferred_batch(bubble_ids) -> object`, satisfaite directement
par `OcrController` (plus de classe intermédiaire).

**`src/manga_trad/gui/controllers/deferred_batch_queue.py`** (remplace
`ollama_batch_queue.py`) — `DeferredBatchQueue`, identique à
`OllamaBatchQueue` mais construit avec `OcrController` directement (au
lieu de `OllamaBatchController`) ; la Protocol `DeferredBatchQueueControllerLike`
exige `deferred_engine_names() -> list[str]` + `run_deferred_batch(...)`.

## Fichiers modifiés

**`src/manga_trad/core/services/ocr_controller.py`** :
- Retirer `_OLLAMA_PREFIX`.
- Ajouter `deferred_engine_names(self) -> list[str]` : noms activés +
  disponibles où `get_engine_instance(name).immediate is False`.
- Ajouter `is_deferred_engine(self, name: str) -> bool` : vrai si `name`
  est dans `OCR_ENGINES` et que l'instance a `immediate is False` (utilisé
  pour filtrer les résultats déjà stockés dans `bubble.ocr_results`,
  indépendamment de l'état activé/désactivé courant — reproduit le
  comportement actuel du filtre par préfixe, généralisé).
- `run_all_engines(self, arr, include_deferred: bool = True)` : renommer
  le paramètre (`include_ollama` → `include_deferred`), remplacer le test
  `name.startswith(_OLLAMA_PREFIX)` par `not
  self.get_engine_instance(name).immediate` (donc engine immédiat toujours
  inclus, engine différé inclus seulement si `include_deferred`).
- `run_ocr_for_bubble(self, bubble_id, include_deferred: bool = True)` :
  renommer le paramètre, réutiliser `prepare_bubble_crop` du nouveau
  `utils.py` pour le crop+pipeline.
- Ajouter `run_deferred_batch(self, bubble_ids: list[int]) -> list[tuple[Bubble, list[tuple[str, OcrResult]], OcrResult | None]]`
  — reprend `OllamaBatchController.run_batch`, généralisé :
  1. `names = self.deferred_engine_names()`; vide → `[]`.
  2. `prepared = {bid: prepare_bubble_crop(...) for bid in bubble_ids}` (ignore `None`).
  3. Pour chaque `name` (traitement **séquentiel**, propriété qui
     garantissait déjà l'absence de chevauchement VRAM entre deux modèles
     Ollama — reste valable génériquement, aucun moteur différé ne tourne
     en parallèle d'un autre) : `engine.recognize_batch(images)` (plus de
     `getattr`/fallback `recognize_batch_naive` nécessaire, le protocole
     garantit la méthode), puis `postprocess_result` par image.
  4. Combine par bulle : résultats stockés filtrés par `not
     self.is_deferred_engine(item["engine"])` + nouveaux résultats
     différés.
  5. `persist_vote` par bulle, retour trié comme avant.
- Mettre à jour les docstrings qui citent `OllamaBatchController`.

**`src/manga_trad/core/services/app_context.py`** : retirer le champ
`ollama_batch` et son import/construction (`OcrController` seul suffit
désormais comme dépendance de la queue GUI).

**`src/manga_trad/gui/workers/ocr_worker.py`** : renommer `include_ollama`
→ `include_deferred` (paramètre de `OcrJob`/`OcrControllerLike`, inchangé
dans son principe — reste aligné sur `OcrController.run_ocr_for_bubble`).

**`src/manga_trad/gui/controllers/ocr_task_manager.py`** :
`request_ocr(self, bubble_id: int, force_immediate: bool = False) -> None`
— renommage demandé par l'utilisateur, **limité à `request_ocr`** (pas de
propagation à `OcrJob`/`run_ocr_for_bubble`, qui gardent
`include_deferred`). Traduction à la frontière : `OcrJob(...,
include_deferred=force_immediate)`.

**`src/manga_trad/gui/controllers/ocr_ui_coordinator.py`** :
- `request_ocr(self, bubble_id: int, force_immediate: bool = False) -> None`
  — traduit vers `self._task_manager.request_ocr(bubble_id,
  force_immediate=force_immediate)`.
- `schedule_auto_ocr`/`_run_pending_auto_ocr` : appellent désormais
  `self.request_ocr(bubble_id)` (défaut `force_immediate=False`, plus
  besoin de passer explicitement `include_ollama=False` comme avant).

**`src/manga_trad/gui/main_window.py`** — point d'attention supplémentaire
repéré en explorant le câblage : `self._side_panel.ocr_all_requested`
(`Signal(int)`, bouton manuel « OCR (tous) ») est aujourd'hui connecté
**directement** à `self._ocr_coordinator.request_ocr`, et s'appuyait sur
l'ancien défaut `include_ollama=True` pour forcer l'exécution immédiate
des moteurs différés. Comme le nouveau défaut est `force_immediate=False`,
cette connexion directe doit devenir :
```python
self._side_panel.ocr_all_requested.connect(
    lambda bubble_id: self._ocr_coordinator.request_ocr(
        bubble_id, force_immediate=True
    )
)
```
Sinon le bouton « OCR (tous) » perdrait silencieusement le déclenchement
immédiat des moteurs différés (régression comportementale).

**`src/manga_trad/gui/main_toolbar.py`** : renommage générique —
`ollama_batch_action` → `deferred_batch_action`,
`_build_ollama_batch_button` → `_build_deferred_batch_button`,
`set_ollama_batch_pending_count` → `set_deferred_batch_pending_count`,
`set_ollama_batch_running` → `set_deferred_batch_running`, texte du
bouton `"Lot Ollama (n)"` → `"Lot différé (n)"`.

**`src/manga_trad/gui/main_window.py`** : import
`DeferredBatchQueue` (au lieu de `OllamaBatchQueue`), construction avec
`self._ctx.ocr` (au lieu de `self._ctx.ollama_batch`), renommage de tous
les `_ollama_batch_*` / `_on_ollama_batch_*` en `_deferred_batch_*` /
`_on_deferred_batch_*`.

**`tests/gui/test_ocr_task_manager.py`** : `FakeOcrController.run_ocr_for_bubble`
paramètre `include_ollama` → `include_deferred`.

**`tests/core/services/test_ocr_controller.py`** : les moteurs factices
(`_FakeEngine`, `_BarrierEngine`, `_SlowEngine`, `_FailingEngine`) n'ont
actuellement pas d'attribut `immediate` — en ajouter `immediate = True` à
chacun (requis maintenant que `run_all_engines`/`get_engine_instance`
lisent cet attribut). Ajouter une section de tests pour
`run_deferred_batch` reprenant les scénarios de l'actuel
`test_ollama_batch_controller.py` (moteurs factices avec `immediate =
False`) :
- vide quand aucun moteur différé activé,
- séquence deux moteurs différés sans chevauchement (tracker start/end),
- combine résultats immédiats stockés + différés et vote,
- ignore une bulle supprimée,
- un seul moteur différé sans résultat CPU préexistant.

**`tests/core/services/test_ollama_batch_controller.py`** →
supprimé, contenu porté dans `test_ocr_controller.py` (voir ci-dessus).

**`tests/gui/test_ollama_batch_queue.py`** → renommé
`tests/gui/test_deferred_batch_queue.py`, `FakeBatchController` adapté à
`deferred_engine_names`/`run_deferred_batch`, classes de queue renommées.

## Hors-périmètre

- Pas de changement à `core/ocr/base.py` (déjà fait par l'utilisateur),
  ni aux adaptateurs OCR autres qu'Ollama.
- Pas de changement au verrou `_LOAD_LOCK`/`unload()` dans
  `ollama_adapter.py` — reste la garantie bas niveau contre le
  chevauchement VRAM, indépendante du contrôleur.
- Le fichier de suivi `.claude/implementation/ollama-batch-ocr.md` sera
  mis à jour après validation du plan (nouvelles étapes remplaçant les
  anciennes 1-12), pas dans ce tour — géré par le skill
  `implementation-tracker`, pas par ce plan d'implémentation.

## Vérification

```
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
```
Puis test manuel (comme prévu à l'étape 12 originale) : bouton "Lot
différé (n)" fonctionnel, timer 60s, déclenchement manuel, `ollama ps`
montrant un seul modèle chargé à la fois.
