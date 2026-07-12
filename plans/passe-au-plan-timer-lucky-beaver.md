# Traitement par lot OCR pour Ollama

## Contexte

L'adaptateur Ollama (`core/ocr/adapters/ollama_adapter.py`) sert deux modèles
de vision recommandés (`qwen2.5vl:3b` et `qwen2.5vl:7b`,
`RECOMMENDED_MODELS`). Aujourd'hui, `OcrController.run_all_engines` lance
**tous** les moteurs activés en parallèle via un `ThreadPoolExecutor`
(`ocr_controller.py:80-118`), y compris les deux entrées Ollama si toutes
deux sont cochées dans la toolbar — ce qui fait charger les deux modèles de
vision en VRAM **simultanément**, à chaque bulle. C'est la cause probable de
la saturation/instabilité VRAM observée.

Objectif : regrouper le travail Ollama par **lot multi-bulles, traité modèle
par modèle**, pour ne jamais avoir plus d'un modèle Ollama chargé à la fois,
et amortir le coût de chargement d'un modèle sur tout le lot plutôt que de
recharger à chaque bulle. Les moteurs OCR classiques (EasyOCR, Tesseract,
docTR, PaddleOCR) restent inchangés — déclenchement immédiat à la création
d'une bulle, comme aujourd'hui.

Décisions déjà actées avec l'utilisateur :
- CPU immédiat / Ollama en lot (pas de changement pour les moteurs CPU).
- File d'attente **en mémoire uniquement** (pas de nouveau champ DB) : une
  fermeture d'app avant lancement du lot perd la file, c'est acceptable.
- Timer d'auto-déclenchement du lot : **60s, redémarré à chaque nouvelle
  bulle mise en file** (pas un délai fixe depuis la première).
- En cas d'échec du lot (ex. serveur Ollama down) : les bulles sont remises
  en file (pas perdues) mais **pas de réessai automatique** — l'utilisateur
  doit recliquer sur le bouton, ou attendre qu'une nouvelle bulle relance le
  timer.

Contrainte projet : `core/` ne dépend jamais de Qt. Toute la logique de
regroupement/séquencement/revote/persistance vit dans `core/services/`, la
GUI ne fait qu'accumuler des `bubble_id`, gérer le timer/bouton, et
déclencher l'exécution sur un thread worker Qt (même pattern que
`OcrTaskManager`/`OcrJob`).

## Ordre d'implémentation

### 1. `core/ocr/base.py`
Ajouter, sans toucher au Protocol `OcrEngine` existant (pour ne pas casser
la conformité structurelle des 4 adaptateurs CPU qui n'ont que `recognize`) :
- `class BatchOcrEngine(Protocol): def recognize_batch(self, images: list[Any]) -> list[OcrResult]: ...`
- `def recognize_batch_naive(engine: OcrEngine, images: list[Any]) -> list[OcrResult]:` — boucle `[engine.recognize(img) for img in images]`, fallback pour tout moteur sans batch dédié.

### 2. `core/ocr/adapters/ollama_adapter.py`
- Refactoriser `recognize()` pour déléguer à un helper interne
  `_recognize_one(image, keep_alive)` (comportement inchangé, `keep_alive=None`
  par défaut → TTL serveur habituel).
- Ajouter `recognize_batch(images: list) -> list[OcrResult]` : boucle sur
  `_recognize_one(image, keep_alive="10m")` (garde le modèle chargé pendant
  tout le lot), puis dans un `finally`, décharge explicitement via un appel
  `chat()` avec `keep_alive=0` (pas de méthode `unload()` dédiée dans le
  client `ollama` — confirmé par lecture du package installé,
  `_client.py:352` et `_client.py:667` pour `ps()`). Le déchargement est
  best-effort (`try/except` large : ne doit jamais faire échouer le lot déjà
  produit).
- Exposer aussi `unload()` public (même logique), au cas où le contrôleur
  de lot veuille forcer un déchargement entre deux phases.

### 3. `core/ocr/voting.py`
Ajouter un petit helper de haut niveau, utilisé uniquement par le nouveau
contrôleur de lot (ne pas toucher au comportement existant de
`run_all_engines`, pour zéro risque de régression sur le chemin CPU actuel) :
```python
def vote_results(results: list[tuple[str, OcrResult]]) -> OcrResult | None
```
Renvoie le résultat unique tel quel si `len(results) <= 1`, sinon délègue à
`vote_tokens`.

### 4. `core/services/ocr_controller.py`
Extraire une méthode publique pour exposer l'instance de moteur cachée
(nécessaire pour que `OllamaBatchController` réutilise le même `client`
Ollama entre les appels d'un même lot) :
```python
def get_engine_instance(self, name: str) -> OcrEngine:
    factory, _ = OCR_ENGINES[name]
    if name not in self._engine_cache:
        self._engine_cache[name] = factory()
    return self._engine_cache[name]
```
`run_engine` devient un simple appel à `get_engine_instance(name).recognize(arr)`.
Aucun autre changement à `run_all_engines`/`run_ocr_for_bubble`.

### 5. `core/services/ollama_batch_controller.py` (nouveau)
`OllamaBatchController(repository, ocr_controller)` — composition avec
`OcrController` existant plutôt que duplication (réutilise crop, pipeline de
prétraitement, patterns, normalisation, cache moteurs).

- `ollama_engine_names() -> list[str]` : moteurs `"Ollama (...)"` de
  `OCR_ENGINES` actuellement dans `ocr_controller.enabled_engines`.
- `run_batch(bubble_ids: list[int]) -> list[tuple[Bubble, list[tuple[str, OcrResult]], OcrResult | None]]` :
  1. Retourne `[]` immédiatement si `ollama_engine_names()` est vide.
  2. Prépare chaque bulle (crop + pipeline de prétraitement, relu à
     l'exécution donc toujours à jour même si le preset a changé pendant
     l'attente) ; ignore silencieusement les bulles/pages introuvables
     (bulle supprimée entre-temps — même comportement que
     `run_ocr_for_bubble` aujourd'hui).
  3. Pour chaque modèle Ollama activé, dans l'ordre : appelle
     `get_engine_instance(name).recognize_batch(images)` (ou
     `recognize_batch_naive` en fallback), post-traite chaque résultat
     (`penalize_false_positives`, `apply_patterns`, `normalize_ocr` — même
     pipeline que `_run_engine_postprocessed`). Le séquencement modèle par
     modèle garantit qu'un seul modèle Ollama est chargé à la fois — aucun
     verrou supplémentaire nécessaire, c'est structurel (boucle séquentielle
     sur un seul thread worker).
  4. Recombine avec les résultats **CPU** déjà stockés dans
     `bubble.ocr_results` (filtre les entrées dont le nom ne commence pas par
     `"Ollama ("`, pour ignorer d'anciens résultats Ollama périmés), revote
     via `vote_results`, persiste `bubble.ocr_results`/`ocr`/`ocr_confidence`
     via `self._repo.bubbles.update(bubble)`.

### 6. `core/services/app_context.py`
Ajouter le champ `ollama_batch: OllamaBatchController` à `AppContext`,
construit après `ocr` :
```python
ollama_batch=OllamaBatchController(repository, ocr),
```

### 7. GUI — file d'attente + timer (nouveaux fichiers)

**`gui/workers/ollama_batch_worker.py`** (même split que `ocr_worker.py`) :
`OllamaBatchJobSignals` (`finished(list, object)`, `failed(list, str)`),
`OllamaBatchJob(QRunnable)` exécutant `OllamaBatchController.run_batch` sur
un thread du pool.

**`gui/controllers/ollama_batch_queue.py`** :
`OllamaBatchQueue(QObject)`, pool Qt à 1 thread (même raison que
`OcrTaskManager` : pas de gain à paralléliser, cache moteur pas thread-safe).
Constructeur avec délai injectable pour les tests :
`__init__(self, batch_controller, delay_ms: int = 60_000, parent=None)`.

- `enqueue(bubble_id)` : no-op si `ollama_engine_names()` vide ou bulle déjà
  en file ; sinon ajoute, émet `bubble_enqueued(bubble_id)` et
  `queue_changed(len)`, puis (re)démarre le `QTimer` singleShot à `delay_ms`.
- `remove(bubble_id)` : retire de la file (ex. bulle supprimée), émet
  `queue_changed`.
- `run_now()` : no-op si file vide ou lot déjà en cours ; sinon vide la file,
  émet `batch_started(ids)`, lance l'`OllamaBatchJob`.
- `wait_for_pending(timeout_ms=2000)`.
- Sur succès (`_on_finished`) : émet `batch_finished(result)`.
- Sur échec (`_on_failed`) : remet les `bubble_ids` en file, réémet
  `queue_changed`, émet `batch_failed(message)` — **pas de redémarrage du
  timer** (décision actée : pas de réessai automatique).

Signaux : `bubble_enqueued(int)`, `queue_changed(int)`, `batch_started(list)`,
`batch_finished(list)`, `batch_failed(str)`.

### 8. `gui/controllers/ocr_ui_coordinator.py`
Ajouter `apply_batch_results(batch_result: list[tuple[Bubble, list, OcrResult | None]])`,
généralisation multi-bulle de `_on_ocr_finished` : pour chaque bulle du lot,
`canvas.set_bubble_ocr_pending(id, False)`, `side_panel.set_ocr_pending(id, False)`,
et si c'est la bulle actuellement affichée, `load_bubble` +
`set_ocr_results(..., switch_tab=False)` (ne pas voler le focus de l'onglet
pour un rafraîchissement en arrière-plan).

### 9. `gui/main_toolbar.py`
Suivre le pattern `_build_ocr_menu`/`_update_ocr_button_text` :
- `ollama_batch_action = QAction("Lot Ollama (0)", self)`, désactivée par défaut.
- `set_ollama_batch_pending_count(count: int)` : met à jour le texte + active/désactive selon `count > 0`.
- `set_ollama_batch_running(running: bool)` : désactive le bouton pendant l'exécution.

### 10. `gui/main_window.py`
- Construire `self._ollama_batch_queue = OllamaBatchQueue(self._ctx.ollama_batch, self)`.
- Câbler : `bubble_enqueued` → set pending visuel (canvas + side_panel) ;
  `queue_changed` → `toolbar.set_ollama_batch_pending_count` ;
  `batch_started` → `toolbar.set_ollama_batch_running(True)` ;
  `batch_finished` → `toolbar.set_ollama_batch_running(False)` +
  `ocr_coordinator.apply_batch_results` ;
  `batch_failed` → `toolbar.set_ollama_batch_running(False)` + affichage
  d'erreur (réutiliser le chemin existant de `ocr_failed`).
  `toolbar.ollama_batch_action.triggered` → `ollama_batch_queue.run_now`.
- Points d'appel `enqueue`/`remove` :
  - `_on_bubble_created` (l.275-282) : après `schedule_auto_ocr(..., immediate=True)`, ajouter `self._ollama_batch_queue.enqueue(bubble.id)`.
  - `_on_bubble_geometry_changed` (l.328-336) : après `schedule_auto_ocr(bubble_id)`, ajouter `self._ollama_batch_queue.enqueue(bubble_id)` (crop modifié → repasse en file).
  - `_on_bubble_delete_requested` (l.338-342) : ajouter `self._ollama_batch_queue.remove(bubble_id)` à côté de `self._ocr_coordinator.cancel_ocr(bubble_id)`.
  - `closeEvent` (l.526-529) : ajouter `self._ollama_batch_queue.wait_for_pending()` à côté de `self._ocr_coordinator.wait_for_pending()`.

## Cas limites couverts

- Bulle supprimée pendant l'attente → retirée de la file ; si course avec un
  lot déjà en vol, ignorée silencieusement dans `_prepare` (comme
  `run_ocr_for_bubble` aujourd'hui).
- Preset de prétraitement changé pendant l'attente → relu à l'exécution, pas
  de valeur figée à l'enqueue.
- Aucun moteur Ollama activé → `enqueue` no-op, bouton toujours désactivé.
- Un seul moteur Ollama activé → boucle d'un seul tour, aucune branche
  spéciale nécessaire.
- Moteur Ollama désactivé entre l'enqueue et le run → simplement absent du
  lot à l'exécution (réévalué dans `run_batch`), pas de sur-ingénierie pour
  resynchroniser la file au toggle.
- Lot déjà en cours + nouveau déclenchement (bouton ou timer) → no-op côté
  `OllamaBatchQueue`, bouton toolbar désactivé pendant l'exécution.

## Tests

- `tests/core/ocr/test_ollama_adapter_batch.py` (nouveau) : mock du module
  `ollama` (client factice) — vérifie `keep_alive="10m"` par appel du lot,
  puis un appel final `keep_alive=0` même si une image lève une exception au
  milieu (`finally`) ; vérifie que `recognize()` seul n'envoie pas de
  `keep_alive` explicite.
- `tests/core/services/test_ollama_batch_controller.py` (nouveau) — style de
  `tests/core/services/test_ocr_controller.py` (fixture `repo` `:memory:`,
  `fake_engines` autouse) : moteurs Ollama factices avec `recognize_batch`,
  test d'absence de chevauchement (tracker d'ordre d'entrée/sortie, à
  l'image de `_BarrierEngine`/`_SlowEngine` existants mais pour prouver la
  séquentialité) ; test de recombinaison CPU+Ollama et revote ; test bulle
  supprimée ; test 0 et 1 moteur Ollama activé.
- `tests/gui/test_ollama_batch_queue.py` (nouveau) — style de
  `tests/gui/test_ocr_task_manager.py` (fixture `qapp`, `FakeBatchController`
  avec `calls`/`results`/`gates`, helper `_pump`) : redémarrage du timer à
  chaque `enqueue` (utiliser le `delay_ms` injectable pour un test rapide,
  ex. 50ms) ; `remove` avant déclenchement ; `run_now` manuel immédiat ;
  double déclenchement pendant un lot en cours → no-op ; échec → bulles
  remises en file sans redémarrage auto du timer.

## Vérification

- `uv run pytest` (suite complète, y compris les nouveaux fichiers de test).
- `uv run ruff check .` / `uv run ruff format .`.
- `uv run basedpyright`.
- Test manuel : lancer l'app, activer les deux moteurs Ollama dans la
  toolbar, créer 2-3 bulles rapidement (< 60s d'écart) → vérifier que le
  compteur "Lot Ollama (n)" monte, que le lot ne se déclenche pas avant 60s
  après la dernière bulle créée, que le bouton reste actionnable pour un
  déclenchement manuel avant l'échéance, et qu'un seul modèle Ollama à la
  fois apparaît chargé (`ollama ps` en parallèle pendant le lot).
