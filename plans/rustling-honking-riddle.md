# Typage statique des signaux Qt (`TypedSignal`)

## Contexte

Les ~25 signaux Qt du projet (`gui/session_state.py`, `canvas.py`,
`timeline.py`, `controllers/*`, `workers/*`, `side_panel/*`...) sont
déclarés avec les types Qt basiques (`Signal(object)`, `Signal(list)`,
`Signal(int, object)`...) qui acceptent n'importe quoi statiquement — le
vrai type n'est documenté qu'en commentaire (`# Page | None`,
`# list[Bubble]`...). Le chantier précédent (`2026-07-cablage-signaux`,
clos hier) a stabilisé l'architecture du câblage (qui possède quel état,
qui s'abonne à qui) mais n'a pas touché au typage des signatures
`.emit()`/`.connect()`.

Objectif : rendre ces signatures vérifiables par `basedpyright`, sans
changer le comportement runtime — ces signaux servent notamment à des
connexions cross-thread (workers `QThreadPool` → thread GUI), donc
l'enregistrement Qt/shiboken du vrai `Signal` à la déclaration de classe
ne doit surtout pas être perturbé.

Décisions déjà validées avec l'utilisateur :
- Generics **par arité dédiée** (`Signal0`, `Signal1[T]`, ... `Signal5[T1..T5]`,
  arité max observée = 5 sur `Canvas.bubble_geometry_changed`), pas de
  `TypeVarTuple`/PEP 646 (jugé plus fragile avec basedpyright en mode
  `standard`).
- **Migration complète immédiate** des ~25 signaux recensés, pas de pilote
  partiel.

## Conception retenue

Pas de wrapper instancié à l'exécution. La ligne réelle
(`page_changed = Signal(object)`) **reste strictement inchangée** — on
ajoute uniquement, avant elle, un bloc `if TYPE_CHECKING:` qui déclare le
type précis de l'attribut (pattern standard "declare now, assign later") :

```python
class SessionState(QObject):
    if TYPE_CHECKING:
        about_to_change: Signal0
        page_changed: Signal1[Page | None]
        bubbles_changed: Signal1[list[Bubble]]
        selection_changed: Signal1[Bubble | None]
        ensure_visible_requested: Signal1[int]
        filter_changed: Signal2[int | None, str]

    about_to_change = Signal()
    page_changed = Signal(object)  # Page | None
    bubbles_changed = Signal(list)  # list[Bubble] de la page courante
    selection_changed = Signal(object)  # Bubble | None
    ensure_visible_requested = Signal(int)
    filter_changed = Signal(object, str)  # chapter_id, search
```

Avantages : diff par fichier = ajout pur (aucune ligne existante modifiée),
zéro risque sur l'enregistrement Qt (il voit toujours un vrai `Signal`),
aucune ambiguïté runtime.

### Nouveau module `src/manga_trad/gui/typed_signal.py`

Emplacement `gui/` (pas `core/`) : dépend de `PySide6.QtCore`, et le
`CLAUDE.md` interdit à `core/` d'importer Qt.

Contenu — classes `Signal0` .. `Signal5[T1..T5]` et `BoundSignal0` ..
`BoundSignal5[T1..T5]`, **actives uniquement sous `if TYPE_CHECKING:`**
(aucun symbole utilisé hors de ce bloc → mort à l'exécution) :

- `BoundSignalN` hérite (au sens typage) de `SignalInstance` réel de
  PySide6 — permet à un `BoundSignalN` d'être passé partout où un
  `SignalInstance` est attendu (forwarding `btn.clicked.connect(self.signal)`)
  sans avoir à modéliser le forwarding signal-vers-signal dans nos propres
  overloads.
- `SignalN.__get__` overloadé (`instance: None` → `SignalN[...]` pour
  l'accès classe ; `instance: QObject` → `BoundSignalN[...]` pour l'accès
  instance), avec `.emit(...)`, `.connect(slot: Callable[[...], object])`,
  `.disconnect(...)` typés sur `BoundSignalN`.
- Pas de `__init__` (classes jamais instanciées, ni à l'exécution ni en
  type-checking — utilisées seulement comme expression de type).

Squelette pour l'arité 2 (à dupliquer/adapter pour 0, 1, 3, 4, 5) :

```python
if TYPE_CHECKING:
    from PySide6.QtCore import QMetaObject, QObject, SignalInstance
    T1 = TypeVar("T1")
    T2 = TypeVar("T2")

    class BoundSignal2(SignalInstance, Generic[T1, T2]):
        def emit(self, arg1: T1, arg2: T2, /) -> None: ...
        def connect(self, slot: Callable[[T1, T2], object], /) -> QMetaObject.Connection: ...
        def disconnect(self, slot: Callable[[T1, T2], object] | None = None, /) -> bool: ...

    class Signal2(Generic[T1, T2]):
        @overload
        def __get__(self, instance: None, owner: object = ...) -> Signal2[T1, T2]: ...
        @overload
        def __get__(self, instance: QObject, owner: object = ...) -> BoundSignal2[T1, T2]: ...
```

## POC de dérisquage (étape 1, avant toute migration)

Fichier scratchpad jetable (jamais committé), exerçant : arité 0, arité 1
avec union `T | None`, arité 2, un `.connect()` avec slot correct et un
avec slot incorrect (arité et type), plus une vérification runtime
(`python -c ...`) que l'attribut reste une vraie `PySide6.QtCore.SignalInstance`
à l'exécution. Critère de sortie : `uv run basedpyright <fichier>` ne
remonte des erreurs *que* sur les lignes volontairement fautives.

Si basedpyright standard ne remonte pas certaines erreurs attendues
(risque connu : variance des `Callable` avec paramètres positionnels),
ajuster la conception avant de lancer la migration à 25 fichiers.

## Cas particuliers identifiés

- **Payloads issus de `Protocol`** (`OcrJobSignals.finished`,
  `DeferredBatchJobSignals.finished` dans `workers/`) : construits contre
  des `Protocol` (`OcrControllerLike`, `DeferredBatchQueueControllerLike`)
  pour rester substituables par des doublures de test sans importer
  `core.db.models`. Garder `object` comme type de leur payload
  (`Signal3[int, int, object]`, `Signal2[list[int], object]`) — retyper le
  Protocol lui-même serait hors périmètre.
- **`ThumbnailJobSignals.finished`** : commenté `# ..., np.ndarray | None`
  mais `ThumbnailJob.run()` n'émet `finished` que côté succès (l'échec
  passe par `failed`) → typer `Signal3[int, int, np.ndarray]` (sans
  `| None`), en se fiant au code plutôt qu'au commentaire.
- **`preprocessing_step_row.py`** : lambdas 0-arg qui appellent
  `.emit(self, -1)` avec `self: StepRowWidget` — sous-type de `QWidget`,
  assignable à `T1=QWidget` sans souci (variance normale en position
  d'argument).
- Repasser sur les slots connectés dont le paramètre était `object`/`list`
  non typé pour leur donner le type précis désormais garanti par le
  signal (permet de retirer des `cast(...)` existants là où c'est le cas).

## Étapes (fichier de suivi `.claude/implementation/typage-signaux-qt.md`, branche `typage-signaux-qt`, base `master`)

1. **Wrapper + POC** — créer `gui/typed_signal.py`, valider le POC
   scratchpad avec `uv run basedpyright`. Vérifier que
   `uv run basedpyright src tests` reste vert par ailleurs (module non
   encore référencé).
2. **`session_state.py`** — signal le plus central, deuxième validation en
   conditions réelles.
3. **`canvas.py` + `timeline.py` + `preprocessing_step_row.py`** — arités
   hautes (4, 5) et cas `QWidget` en paramètre, traités tôt pour dérisquer.
4. **`gui/controllers/*.py`** (`deferred_batch_queue.py`,
   `ocr_task_manager.py`, `ocr_ui_coordinator.py`,
   `thumbnail_task_manager.py`) — attention au cas Protocol.
5. **`gui/workers/*.py`** (`thumbnail_worker.py`,
   `deferred_batch_worker.py`, `ocr_worker.py`) — étape sensible
   cross-thread : rejouer les tests `pytest-qt` (`qtbot.waitSignal`) qui
   couvrent ces workers.
6. **`gui/side_panel/*.py` + widgets restants** (`comparison_tab.py`,
   `ocr_translation_tab.py`, `panel.py`, `preprocessing_presets_tab.py`,
   `chapter_filter_bar.py`, `main_toolbar.py`, `page_bar.py`).
7. **Vérification globale** — `ruff check .`, `ruff format --check .`,
   `basedpyright`, `pytest` (suite complète). `git diff` final ne doit
   montrer que des ajouts de blocs `if TYPE_CHECKING` + imports +
   d'éventuelles annotations de paramètres de slots — jamais de
   modification des lignes `Signal(...)` elles-mêmes. Comparer le nombre
   d'erreurs basedpyright avant/après pour objectiver le gain.

## Vérification par étape

- `uv run basedpyright <fichier(s) touché(s)>` puis
  `uv run basedpyright src/manga_trad/gui` (capte les régressions chez
  les consommateurs non modifiés, ex. `main_window.py`).
- `uv run ruff check <fichier(s)>` + `uv run ruff format --check <fichier(s)>`.
- Tests `pytest` ciblant le fichier/la classe migrée s'il en existe.

**Note héritée** du chantier précédent : `ruff check .` remonte déjà 26
`E501` préexistants sur `core/`, et `pytest` échoue déjà sur
`tests/core/ocr/test_ollama_adapter_batch.py::test_recognize_single_does_not_set_explicit_keep_alive`
— non liés à ce chantier, à ne pas confondre avec une régression.

## Fichiers critiques

- `src/manga_trad/gui/typed_signal.py` (nouveau)
- `src/manga_trad/gui/session_state.py`
- `src/manga_trad/gui/canvas.py`
- `src/manga_trad/gui/workers/ocr_worker.py`
- `src/manga_trad/gui/controllers/ocr_task_manager.py`
