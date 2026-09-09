"""Types fondamentaux d'un répertoire-liste.

PORTÉE : ce module ne lit ni n'écrit aucun fichier. Il définit ce qu'est un résultat,
un élément, un contrat — et les deux marqueurs de champ à remplir. Tout le reste du
paquet en dépend ; lui ne dépend de rien.

PYTHON >= 3.12 : la syntaxe de généricité (PEP 695) est utilisée ici. La garde de
version vit dans list-dir.py, avant tout import de ce paquet — un SyntaxError à
l'import ne laisserait aucune place à un message lisible.
"""

from __future__ import annotations

import datetime
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal, Never, Protocol, cast, get_args, override

if TYPE_CHECKING:  # pragma: no cover
    # Import de typage seulement. store.py dépend de ce module ; l'annotation étant
    # différée par `from __future__ import annotations`, rien n'est importé à
    # l'exécution. Sans cela, `Utils.open` rendrait un Result[object] et le protocole
    # n'apprendrait rien à personne sur ce qu'une commande reçoit.
    from .store import ListStore

# --------------------------------------------------------------- les marqueurs
# Définis ici et NULLE PART AILLEURS. Un marqueur recopié est un marqueur qui
# diverge : le jour où l'un des deux change, l'autre copie continue de traîner
# dans des fichiers que plus rien ne signale.
PLACEHOLDER = "<À REMPLIR>"  # requis — tant qu'il est là, l'élément n'est pas instruit
OPTIONAL = "<OPTIONNEL>"  # facultatif — sa présence n'empêche rien

SEPARATEUR = "/"
"""Ce qui sépare une définition du gabarit qu'on y vise, dans un `origin.def`. Défini
ici parce qu'`Origin` le découpe et que `_origin` le valide : deux modules, une seule
constante, sinon l'un accepterait un jour ce que l'autre ne saurait pas relire."""


def nom_mal_forme(nom: str) -> str | None:
    """Pourquoi `nom` n'est pas un nom de semence bien formé, ou None s'il l'est.

    DEUX FORMES, ET PAS UNE DE PLUS : `technical-debt` nomme une définition,
    `technical-debt/review` nomme le gabarit `review` de cette définition. Un
    troisième segment ne désignerait rien — les gabarits vivent à plat dans
    `templates/`.

    C'EST UN NOM, PAS UN CHEMIN, exactement comme pour `--template` : `..`
    remonterait hors de `templates/`, `.` désignerait le répertoire lui-même.

    ICI PLUTÔT QUE DANS `contract.py` : la règle sert à DEUX lecteurs qui n'ont pas le
    même vocabulaire — `_origin` juge un fichier et parle en `Result` avec un chemin,
    `resolve` juge un argument de ligne de commande. Rendre le seul MOTIF, sans
    chemin ni Result, est ce qui les laisse composer chacun son message sur une règle
    unique. Deux copies finiraient par diverger, et c'est arrivé : `resolve` a d'abord
    conseillé « --template  » sur un `technical-debt/` que `_origin` refusait déjà.
    """
    segments = nom.split(SEPARATEUR)
    if len(segments) > 2:
        return f"au plus un « {SEPARATEUR} », qui sépare une définition du gabarit qu'on y vise"
    if any(not s or s in (".", "..") for s in segments):
        return (
            f"chaque part d'un « <définition>{SEPARATEUR}<gabarit> » doit être non vide, "
            "et différente de « . » et « .. »"
        )
    return None


class ListError(Exception):
    """Levée par Result.unwrap() sur un résultat en échec."""


# ------------------------------------------------------------------- résultats
@dataclass(frozen=True)
class Result[T]:
    """Une opération et son issue. status 0 = succès, tout le reste = échec fermé.

    Le paramètre de type porte : items() rend un Result[list[Item]], move() un
    Result[Path]. Confondre les deux devient une erreur de typage, pas un
    AttributeError trois appels plus loin.
    """

    status: int
    value: T | None = None
    message: str = ""

    def __bool__(self) -> bool:
        return self.status == 0

    def unwrap(self) -> T:
        """La valeur, ou ListError(message).

        Pour les scripts qui préfèrent l'exception au code retour. La CLI ne s'en
        sert jamais : elle traduit status en code de sortie et message sur stderr.
        """
        if self.status != 0:
            raise ListError(self.message)
        # cast, et non un `type: ignore` : sur un succès, `value` est un T — c'est
        # l'invariant que `status == 0` porte, et qu'aucune annotation ne sait dire.
        return cast("T", self.value)


def ok[T](value: T = None, message: str = "") -> Result[T]:
    """Un succès, et ce qu'il y aurait à dire malgré tout.

    LE MESSAGE D'UN SUCCÈS EST UN AVERTISSEMENT, jamais une cause d'échec : la CLI
    l'écrit sur stderr sans toucher au code de retour ni à stdout. C'est ce qui
    permet à `validate` de signaler une liste périmée sans déclarer fautive une
    liste dont tous les éléments sont conformes.
    """
    return Result(0, value, message)


def fail(message: str, code: int = 1) -> Result[Never]:
    return Result(code, None, message)


# --------------------------------------------------------------------- contrat
type FieldType = Literal["slug", "text", "date", "enum", "list"]
"""Les types qu'un contrat peut déclarer. La liste est fermée : un contrat n'est
pas un langage, et un type inconnu est une faute que load_contract nomme."""

# `__value__` d'un alias PEP 695 est déclaré Any dans les stubs ; le cast rétablit ce
# que la ligne au-dessus affirme, et l'ignore ne couvre que cette lecture-là.
FIELD_TYPES: tuple[FieldType, ...] = cast(
    "tuple[FieldType, ...]",
    get_args(FieldType.__value__),  # pyright: ignore[reportAny]
)
"""Les mêmes, énumérables. Dérivés de l'alias, jamais recopiés : deux listes qui
se ressemblent finissent toujours par diverger."""

type FieldValue = str | bool | int | datetime.date | list[str]
"""Ce qu'un champ peut valoir. Exactement ce que le sérialiseur de items.py sait
écrire : borner l'entrée de l'API à ce que la sortie sait rendre est ce qui empêche
d'accepter une valeur qu'on ne pourra pas réécrire dans le front matter.

Les valeurs LUES sur le disque, elles, restent des `object` : un fichier édité à la
main peut contenir n'importe quoi, et c'est le rôle de validate de le dire."""


@dataclass(frozen=True)
class Field:
    """Un champ déclaré au contrat."""

    name: str
    type: FieldType
    required: bool = False
    description: str = ""
    values: list[str] = field(default_factory=list)  # enum seulement
    source: str | None = None  # le `from` d'un contrat dérivé
    text: str | None = None  # texte littéral posé à la place du marqueur
    command: str | None = None  # commande dont la sortie est posée à la place du marqueur

    @property
    def marker(self) -> str:
        """Le marqueur que ce champ reçoit à la création.

        Un champ facultatif se marque comme une section facultative : sinon
        --filled réclamerait de remplir ce que le contrat dit optionnel.
        """
        return PLACEHOLDER if self.required else OPTIONAL


@dataclass(frozen=True)
class Section:
    """Une section déclarée au contrat."""

    name: str
    required: bool = False
    description: str = ""
    text: str | None = None  # texte littéral posé à la place du marqueur
    command: str | None = None  # commande dont la sortie est posée à la place du marqueur

    @property
    def marker(self) -> str:
        """Le marqueur que cette section reçoit à la création. Voir Field.marker."""
        return PLACEHOLDER if self.required else OPTIONAL


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

    `name` PREND DEUX FORMES, et la seconde nomme un gabarit. Un segment unique
    désigne une définition, résolue dans les quatre rangs. Deux segments séparés
    d'un `/` — `technical-debt/review` — désignent le GABARIT `review` de la
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

        C'est elle qu'on résout dans les rangs — un gabarit n'y est jamais cherché
        pour lui-même, il vit dans le `templates/` de celle-ci.
        """
        return None if self.name is None else self.name.split(SEPARATEUR, 1)[0]

    @property
    def template(self) -> str | None:
        """Le gabarit nommé, ou None quand l'estampille désigne une définition.

        DEUX ABSENCES DIFFÉRENTES, ET C'EST VOULU : None sur `name is None` dit qu'il
        n'y a pas de semence du tout ; None sur un nom simple dit que la semence est
        une définition. Les deux se lisent au même endroit — `definition` — et rien
        n'oblige un appelant à les distinguer s'il n'en a pas besoin.
        """
        if self.name is None or SEPARATEUR not in self.name:
            return None
        return self.name.split(SEPARATEUR, 1)[1]


@dataclass(frozen=True)
class Contract:
    name: str
    description: str = ""
    fields: Mapping[str, Field] = field(default_factory=dict[str, Field])
    sections: Mapping[str, Section] = field(default_factory=dict[str, Section])
    origin: Origin | None = None
    """None = aucune table `[origin]` dans le fichier. Une liste antérieure à ce
    dispositif est dans cet état, et c'est ce que l'avertissement d'adoption dit."""

    @property
    def required_sections(self) -> list[str]:
        """Les titres requis, dans l'ordre du TOML — ce que lit store.py."""
        return [s.name for s in self.sections.values() if s.required]


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


@dataclass(frozen=True)
class Violation:
    """Un manquement d'un élément à son contrat."""

    path: Path
    subject: str  # nom du champ ou titre de section
    reason: str

    @override
    def __str__(self) -> str:
        return f"{self.path}: {self.subject} — {self.reason}"


# --------------------------------------------------------------------- élément
@dataclass(frozen=True)
class Item:
    """Un élément de liste : un fichier, son front matter, ses sections.

    IMMUABLE, et ce n'est pas un principe abstrait : `raw_front` conserve le texte
    TOML tel qu'il a été lu, et l'écriture REPROJETTE `fields` dessus — elle n'y
    touche que les champs dont la valeur a changé. Muter `fields` en place le ferait
    diverger de `raw_front` sans que rien ne le signale, et la reprojection écrirait
    alors sur un document qui ne correspond plus à rien.

    `raw_front` N'EST PLUS UN COMMUTATEUR. Il l'a été : le mettre à None déclenchait
    une resérialisation intégrale, qui aplatissait les tableaux et effaçait les
    commentaires de quelqu'un qui n'avait rien demandé. Il n'est plus que le document
    d'origine, et None y signifie « il n'y en a pas » — un élément neuf, rien de plus.
    """

    path: Path
    fields: Mapping[str, object] = field(default_factory=dict[str, object])
    sections: Mapping[str, str] = field(default_factory=dict[str, str])
    raw_front: str | None = None

    def __post_init__(self) -> None:
        # Une vue en lecture seule, pas une copie défensive : « en lecture » doit
        # être refusé par l'interpréteur, pas seulement écrit dans la doc.
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))
        object.__setattr__(self, "sections", MappingProxyType(dict(self.sections)))

    @property
    def id(self) -> str:
        return self.path.stem

    def with_fields(self, **kw: object) -> Item:
        return replace(self, fields={**self.fields, **kw})

    def with_sections(self, **kw: str) -> Item:
        return replace(self, sections={**self.sections, **kw})

    def realigned(self, fields: Mapping[str, object], sections: Mapping[str, str]) -> Item:
        """Le même élément, champs et sections REMPLACÉS — non fusionnés.

        with_fields et with_sections fusionnent : ils savent ajouter et écraser,
        jamais retirer ni réordonner. Or c'est exactement ce qu'une migration doit
        pouvoir faire quand le contrat a changé d'ordre ou perdu un champ. D'où ce
        troisième constructeur — mais plus la resérialisation qui l'accompagnait :
        retirer et réordonner se font désormais SUR le document d'origine, dont le
        reste garde sa mise en forme.
        """
        return replace(self, fields=dict(fields), sections=dict(sections))

    def render(self) -> str:
        from .items import render_item

        return render_item(self)


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
