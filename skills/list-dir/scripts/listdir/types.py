"""Types fondamentaux d'un répertoire-liste.

CE QUI CONCERNE UN FICHIER SEUL VIT DANS `gabarit.types`, et se réexporte ici sous
son nom d'origine : résultat, marqueurs, types de champ, `Violation`, `Item`. Ne reste
ici que ce qui suppose une liste — contrat et provenance, protocoles des commandes.

PORTÉE : ce module ne lit ni n'écrit aucun fichier. Tout le reste du paquet en
dépend ; lui ne dépend que de `gabarit.types`.

PYTHON >= 3.12 : la syntaxe de généricité (PEP 695) est utilisée ici. La garde de
version vit dans list-dir.py, avant tout import de ce paquet — un SyntaxError à
l'import ne laisserait aucune place à un message lisible.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Never, Protocol, override

from gabarit.types import FIELD_TYPES as FIELD_TYPES
from gabarit.types import OPTIONAL as OPTIONAL
from gabarit.types import PLACEHOLDER as PLACEHOLDER
from gabarit.types import Contract as BaseContract
from gabarit.types import Field as BaseField
from gabarit.types import FieldType as FieldType
from gabarit.types import FieldValue as FieldValue
from gabarit.types import GabaritError as GabaritError
from gabarit.types import Item as Item
from gabarit.types import Result as Result
from gabarit.types import Section as Section
from gabarit.types import Violation as Violation
from gabarit.types import fail as fail
from gabarit.types import ok as ok

if TYPE_CHECKING:  # pragma: no cover
    # Import de typage seulement. store.py dépend de ce module ; l'annotation étant
    # différée par `from __future__ import annotations`, rien n'est importé à
    # l'exécution. Sans cela, `Utils.open` rendrait un Result[object] et le protocole
    # n'apprendrait rien à personne sur ce qu'une commande reçoit.
    from .store import ListStore

ListError = GabaritError
"""Le nom public, dans ce paquet, de ce que `Result.unwrap()` lève sur un échec."""

SEPARATEUR = "/"
"""Ce qui sépare une définition du patron qu'on y vise, dans un `origin.def`. Défini
ici parce qu'`Origin` le découpe et que `_origin` le valide : deux modules, une seule
constante, sinon l'un accepterait un jour ce que l'autre ne saurait pas relire."""


def nom_mal_forme(nom: str) -> str | None:
    """Pourquoi `nom` n'est pas un nom de semence bien formé, ou None s'il l'est.

    DEUX FORMES, ET PAS UNE DE PLUS : `technical-debt` nomme une définition,
    `technical-debt/review` nomme le patron `review` de cette définition. Un
    troisième segment ne désignerait rien — les patrons vivent à plat dans
    `patrons/`.

    C'EST UN NOM, PAS UN CHEMIN, exactement comme pour `--patron` : `..`
    remonterait hors de `patrons/`, `.` désignerait le répertoire lui-même.

    ICI PLUTÔT QUE DANS `contract.py` : la règle sert à DEUX lecteurs qui n'ont pas le
    même vocabulaire — `_origin` juge un fichier et parle en `Result` avec un chemin,
    `resolve` juge un argument de ligne de commande. Rendre le seul MOTIF, sans
    chemin ni Result, est ce qui les laisse composer chacun son message sur une règle
    unique. Deux copies finiraient par diverger, et c'est arrivé : `resolve` a d'abord
    conseillé « --patron  » sur un `technical-debt/` que `_origin` refusait déjà.
    """
    segments = nom.split(SEPARATEUR)
    if len(segments) > 2:
        return f"au plus un « {SEPARATEUR} », qui sépare une définition du patron qu'on y vise"
    if any(not s or s in (".", "..") for s in segments):
        return (
            f"chaque part d'un « <définition>{SEPARATEUR}<patron> » doit être non vide, "
            "et différente de « . » et « .. »"
        )
    return None


@dataclass(frozen=True)
class Field(BaseField):
    """Un champ déclaré au contrat d'une liste : celui d'un gabarit, plus son `from`.

    `source` EST PROPRE À UNE LISTE : le `from` d'un contrat dérivé nomme un champ de la
    liste source, et un gabarit seul n'a pas de source.
    """

    source: str | None = None  # le `from` d'un contrat dérivé


@dataclass(frozen=True)
class Origin:
    """D'où vient un contrat, et ce qu'on s'autorise à lui rappeler.

    ELLE VOYAGE AVEC LA SEMENCE. La table `[origin]` est écrite dans le contrat de la
    DÉFINITION, et la copie qu'`init` en fait la reçoit avec le reste : `init` ne
    l'écrit jamais lui-même. C'est ce qui préserve l'égalité octet pour octet entre
    une liste et sa semence — l'invariant que défend la docstring d'`init_list` — et
    ce qui fait que `--from <chemin>` estampille exactement comme `--def <nom>`.

    `name` NOMME, IL NE LOCALISE PAS. Un chemin dépend de la machine ; deux machines
    rendraient deux contrats, ce qui est précisément ce que la résolution par rangs
    de definitions.py existe pour éviter. `reseed` rerésout ce nom le jour venu.

    `name is None` DIT « CETTE LISTE N'A PAS DE SEMENCE » — c'est le `def = false`
    du fichier, et l'état du squelette qu'`init` écrit sans `--def`. À distinguer
    d'un `Contract.origin` à None, qui dit qu'aucune provenance n'est déclarée :
    l'un est une réponse, l'autre une absence de réponse.

    `name` PREND DEUX FORMES, et la seconde nomme un patron. Un segment unique
    désigne une définition, résolue dans les quatre rangs. Deux segments séparés
    d'un `/` — `technical-debt/review` — désignent le PATRON `review` de la
    définition `technical-debt`, c'est-à-dire la semence d'une liste engendrée par
    `derive`. La forme est vérifiée par `_origin`, seul constructeur de cette classe :
    les deux propriétés ci-dessous s'appuient là-dessus et ne revalident rien.
    """

    name: str | None
    version: int = 0
    frozen: bool = False
    """La liste a délibérément pris la main : plus d'avertissement de péremption, et
    `reseed` refuse d'y écrire sans `--force`. C'est ce refus qui justifie le mot."""

    @property
    def definition(self) -> str | None:
        """La définition nommée : le nom entier, ou son premier segment.

        C'est elle qu'on résout dans les rangs — un patron n'y est jamais cherché
        pour lui-même, il vit dans le `patrons/` de celle-ci.
        """
        return None if self.name is None else self.name.split(SEPARATEUR, 1)[0]

    @property
    def patron(self) -> str | None:
        """Le patron nommé, ou None quand l'estampille désigne une définition.

        DEUX ABSENCES DIFFÉRENTES, ET C'EST VOULU : None sur `name is None` dit qu'il
        n'y a pas de semence du tout ; None sur un nom simple dit que la semence est
        une définition. Les deux se lisent au même endroit — `definition` — et rien
        n'oblige un appelant à les distinguer s'il n'en a pas besoin.
        """
        if self.name is None or SEPARATEUR not in self.name:
            return None
        return self.name.split(SEPARATEUR, 1)[1]


@dataclass(frozen=True)
class Contract(BaseContract):
    """Le contrat d'une liste : celui d'un gabarit, plus sa provenance."""

    fields: Mapping[str, Field] = field(default_factory=dict[str, Field])
    origin: Origin | None = None
    """None = aucune table `[origin]` dans le fichier. Une liste antérieure à ce
    dispositif est dans cet état, et c'est ce que l'avertissement d'adoption dit."""


@dataclass(frozen=True)
class Change:
    """Une remise en conformité effectuée par migrate.

    Le pendant de Violation : celle-ci dit ce qui cloche, celui-ci ce qui a été
    fait pour que ça ne cloche plus. Deux types distincts parce qu'on ne les lit
    pas dans le même état d'esprit — l'un se corrige, l'autre se relit.
    """

    path: Path
    subject: str  # nom du champ ou titre de section
    action: str
    applied: bool = True
    """False = simple remarque, RIEN n'a été écrit pour elle. La distinction n'est
    pas cosmétique : c'est elle qui empêche une remarque de faire réécrire un
    fichier que la migration n'a pas eu à toucher."""

    @override
    def __str__(self) -> str:
        return f"{self.path}: {self.subject} — {self.action}"


# ------------------------------------------------------------------ protocoles
class Utils(Protocol):
    """Ce qu'une commande reçoit. Le noyau ne lui donne rien d'autre."""

    def open(self, list_dir: Path | str) -> Result[ListStore]: ...
    def git(self, *argv: str) -> Result[str]: ...
    def run(self, name: str, argv: list[str]) -> Result[object]: ...
    def ok[T](self, value: T, message: str = "") -> Result[T]: ...
    def fail(self, message: str, code: int = 1) -> Result[Never]: ...


class Command[T](Protocol):
    """Ce qu'un module de commande doit exposer. Vérifié au chargement."""

    DESCRIPTION: str
    REQUIRES: list[str]

    def register(self, parser: object) -> None: ...
    def command(self, args: object, utils: Utils) -> Result[T]: ...
