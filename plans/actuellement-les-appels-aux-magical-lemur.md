# Rendre l'OCR non-bloquant (PySide6)

## Contexte

Tous les appels OCR (`OcrController.run_ocr_for_bubble`) s'exécutent
aujourd'hui de façon synchrone dans le thread GUI principal, déclenchés
depuis `main_window.py` — soit par clic sur le bouton « OCR » du panneau
latéral, soit automatiquement après chaque redimensionnement/création de
bulle (`_schedule_auto_ocr`, debounce 800 ms). Le chargement lazy des
moteurs (EasyOCR/PaddleOCR/DocTR, ~200-300 Mo, inférence CPU) gèle donc
l'UI à chaque déclenchement, ce qui est particulièrement pénible avec
l'auto-OCR déclenché à chaque édition de géométrie de bulle.

Aucune infrastructure de threading/async n'existe dans le projet — à
créer entièrement, côté GUI uniquement (le `core/` ne doit jamais
importer Qt, cf. CLAUDE.md). Le pattern retenu : `QThreadPool` +
`QRunnable`, adapté à des jobs courts et fréquents, avec un mécanisme de
génération pour superseder/invalider les résultats obsolètes (cas du
debounce qui peut soumettre plusieurs requêtes pour la même bulle).

Prérequis bloquant découvert pendant l'investigation : la connexion
SQLite (`RepositoryBase`) n'est pas thread-safe (`sqlite3.connect` sans
`check_same_thread=False`, pas de verrou). Sans correctif, tout accès
DB depuis le thread OCR lève `ProgrammingError`. À corriger en premier.

## Étape 0 — Thread-safety de `RepositoryBase`

Fichier : `src/manga_trad/db/repository/base.py`

- `sqlite3.connect(str(db_path), check_same_thread=False)`
- Ajouter `self._lock = threading.RLock()` sur `RepositoryBase`.
- Exposer un context manager `lock()` sur `RepositoryBase`, utilisé par
  les méthodes des mixins de domaine (`bubbles.py`, `pages.py`, etc.)
  qui touchent `self._conn`. Vu le volume de méthodes, factoriser via un
  décorateur simple plutôt que dupliquer `with self._lock:` partout.

Test : `tests/db/test_repository.py` — appeler une méthode repository
depuis un `threading.Thread` séparé, vérifier l'absence d'exception.

## Étape 1 — Worker OCR

Nouveau package `src/manga_trad/gui/workers/` avec
`ocr_worker.py` :

```python
class OcrJobSignals(QObject):
    finished = Signal(int, int, object)   # bubble_id, generation, result|None
    failed = Signal(int, int, str)        # bubble_id, generation, message

class OcrJob(QRunnable):
    def __init__(self, controller, bubble_id, generation): ...
    def run(self) -> None:
        try:
            result = self._controller.run_ocr_for_bubble(self._bubble_id)
        except Exception as exc:
            self.signals.failed.emit(self._bubble_id, self._generation, str(exc))
            return
        self.signals.finished.emit(self._bubble_id, self._generation, result)
```

`OcrController.run_ocr_for_bubble` n'est pas modifié (reste Qt-free,
synchrone, testable seul).

## Étape 2 — `OcrTaskManager`

Nouveau fichier `src/manga_trad/gui/controllers/ocr_task_manager.py`,
`QObject` orchestrant le cycle de vie des jobs :

- `request_ocr(bubble_id)` : incrémente la génération de la bulle,
  retire un job pas encore démarré pour cette bulle via
  `QThreadPool.tryTake()`, soumet le nouveau job, émet `ocr_started`.
- `invalidate(bubble_id)` : bump la génération sans soumettre de job —
  utilisé quand l'utilisateur choisit un résultat manuel pendant qu'un
  OCR auto est en vol, pour que ce dernier soit ignoré à son retour.
- Slots internes `_on_job_finished`/`_on_job_failed` : comparent la
  génération reçue à la génération courante ; si elle diffère (job
  superseded ou invalidé), le résultat est jeté silencieusement ; sinon
  ré-émission via `ocr_finished(bubble_id, result)` /
  `ocr_failed(bubble_id, message)`.
- `QThreadPool` local avec `setMaxThreadCount(1)` : sérialise les
  inférences (le cache de moteurs `OcrController._engine_cache` n'est
  pas thread-safe ; évite aussi de charger plusieurs modèles lourds en
  parallèle ; limite l'accès DB concurrent à un seul thread non-GUI).

Un job déjà démarré ne peut pas être interrompu (appel bloquant opaque
à `engine.recognize()`) : on le laisse terminer et on jette son
résultat via le contrôle de génération plutôt que de tenter de le tuer.

Test : `tests/gui/test_ocr_task_manager.py` (nouveau `tests/gui/conftest.py`
avec fixture `QApplication` de session, pas de `pytest-qt` à ajouter —
piloter via `app.processEvents()` / `pool.waitForDone()`) :
- une requête unique aboutit à `ocr_finished` avec le bon résultat ;
- deux requêtes rapprochées sur la même bulle → un seul résultat émis
  (celui de la dernière génération) ;
- `invalidate()` juste après `request_ocr()` empêche toute émission
  pour ce job (contrôleur factice à latence contrôlée via
  `threading.Event`) ;
- contrôleur factice qui lève une exception → `ocr_failed` avec le bon
  message.

## Étape 3 — Câblage dans `main_window.py`

- Instancier `self._ocr_task_manager = OcrTaskManager(self._ocr_controller, self)`
  après la création de `self._ocr_controller` (l.34).
- Connecter `ocr_started` / `ocr_finished` / `ocr_failed` dans
  `_connect_signals`.
- `_on_ocr_all_requested` (l.310-321) devient : `self._ocr_task_manager.request_ocr(bubble_id)`.
- La logique actuelle de traitement du résultat (déstructuration
  `bubble, engine_results, vote_result`, `self._side_panel.load_bubble`,
  `set_ocr_results`) migre dans un nouveau slot `_on_ocr_finished`, avec
  garde : ignorer si la bulle affichée dans le panneau a changé entre
  temps (`self._side_panel._bubble is None or self._side_panel._bubble.id != bubble_id`).
- Nouveau slot `_on_ocr_failed` : reprend le `QMessageBox.warning`
  existant + efface l'indicateur pending.
- Nouveau slot `_on_ocr_started` : active l'indicateur pending (étape 4).
- `_on_ocr_result_selected` (l.323-334) : après `set_manual_ocr_result`,
  appeler `self._ocr_task_manager.invalidate(bubble_id)`.
- Ajouter `closeEvent` (n'existe pas encore) appelant
  `self._ocr_task_manager.wait_for_pending(timeout)` pour éviter un
  crash sur un `QRunnable` encore actif à la fermeture.

## Étape 4 — Indicateur visuel « OCR en cours »

- **Canvas** (`canvas_items.py` + `canvas.py`) : `BubbleItem.set_ocr_pending(bool)`
  appliquant un `QPen` pointillé distinct (suivre le pattern existant de
  sélection de pen selon l'état, ex. `OCR_VALIDATED_PEN`) ; méthode
  `Canvas.set_bubble_ocr_pending(bubble_id, pending)` qui délègue à
  l'item correspondant.
- **Side panel** (`side_panel/panel.py`) : méthode `set_ocr_pending(bubble_id, pending)`
  qui n'agit que si `bubble_id == self._bubble.id` — affiche un état
  « OCR en cours… » et/ou désactive le bouton OCR le temps du job.
- Appelées depuis `_on_ocr_started` (activer) et `_on_ocr_finished` /
  `_on_ocr_failed` (toujours désactiver, même si le résultat est
  obsolète/`None`, pour ne jamais laisser l'indicateur bloqué).

## Fichiers impactés

Créer :
- `src/manga_trad/gui/workers/__init__.py`, `ocr_worker.py`
- `src/manga_trad/gui/controllers/ocr_task_manager.py`
- `tests/gui/conftest.py`, `tests/gui/test_ocr_task_manager.py`

Modifier :
- `src/manga_trad/db/repository/base.py`
- `src/manga_trad/gui/main_window.py`
- `src/manga_trad/gui/canvas_items.py`, `canvas.py`
- `src/manga_trad/gui/side_panel/panel.py`
- `tests/db/test_repository.py`

## Ordre d'implémentation

1. Thread-safety `RepositoryBase` + test.
2. `OcrJob`/`OcrJobSignals`.
3. `OcrTaskManager` + tests unitaires isolés.
4. Câblage `main_window.py`.
5. Indicateurs visuels.
6. Vérification finale (voir ci-dessous).

## Vérification

- `uv run pytest` (suite complète, y compris les nouveaux tests).
- `uv run ruff check . && uv run ruff format --check .`
- `uv run basedpyright`
- Test manuel via `/run` ou lancement direct de l'app : redimensionner
  une bulle plusieurs fois rapidement et vérifier que l'UI reste
  réactive pendant l'OCR (déplacement de fenêtre, clic sur une autre
  bulle possibles pendant l'inférence), que l'indicateur pending
  apparaît/disparaît correctement, et qu'un résultat manuel saisi
  pendant un OCR auto en vol n'est pas écrasé par ce dernier à son
  retour.
