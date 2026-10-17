"""Types fondamentaux d'un gabarit : un fichier, son front matter, ses sections.

PORTÉE : ce module ne lit ni n'écrit aucun fichier. Il définit ce qu'est un résultat,
un fichier préstructuré, un manquement — et les deux marqueurs de ce qui reste à
remplir. Tout le reste du paquet en dépend ; lui ne dépend de rien.

`listdir` en réexporte l'essentiel : une list-dir est une liste de gabarits.

PYTHON >= 3.12 : la syntaxe de généricité (PEP 695) est utilisée ici. La garde de
version vit dans les points d'entrée, avant tout import de ce paquet — un SyntaxError
à l'import ne laisserait aucune place à un message lisible.
"""

from __future__ import annotations

import datetime
import re
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Never, cast, get_args, override

# --------------------------------------------------------------- les marqueurs
# Définis ici et NULLE PART AILLEURS. Un marqueur recopié est un marqueur qui
# diverge : le jour où l'un des deux change, l'autre copie continue de traîner
# dans des fichiers que plus rien ne signale.
PLACEHOLDER = "<À REMPLIR>"  # requis — tant qu'il est là, l'élément n'est pas instruit
OPTIONAL = "<OPTIONNEL>"  # facultatif — sa présence n'empêche rien


class GabaritError(Exception):
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
        """La valeur, ou GabaritError(message).

        Pour les scripts qui préfèrent l'exception au code retour. La CLI ne s'en
        sert jamais : elle traduit status en code de sortie et message sur stderr.
        """
        if self.status != 0:
            raise GabaritError(self.message)
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
type FieldType = Literal["slug", "text", "date", "enum", "list", "int", "bool"]
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

TYPED_MARKER_TYPES: frozenset[FieldType] = frozenset({"int", "date", "bool", "list"})
"""Les types dont la valeur TOML ne s'écrit pas entre guillemets : leur marqueur dit le
type (`<OPTIONNEL date>`), pour que le modèle n'écrive pas `reviewed = "<OPTIONNEL>"` et
n'y laisse pas les guillemets d'une chaîne. `text`, `enum` et `slug` n'y sont pas : leur
valeur finale est aussi une chaîne, le marqueur générique y est exact."""


def marker(required: bool, type: FieldType | None = None) -> str:
    """Le marqueur d'un champ ou d'une section : requis ou facultatif, typé ou non.

    LA SEULE CONSTRUCTION D'UN MARQUEUR TYPÉ. Elle part des deux constantes ci-dessus et
    n'en recopie aucune : `<À REMPLIR>` devient `<À REMPLIR int>`, rien d'autre ne change.
    Une section, ou un type hors de `TYPED_MARKER_TYPES`, reçoit le marqueur générique.

    Args:
        required: vrai pour `<À REMPLIR…>`, faux pour `<OPTIONNEL…>`.
        type: le type du champ ; None pour une section.
    """
    base = PLACEHOLDER if required else OPTIONAL
    if type is None or type not in TYPED_MARKER_TYPES:
        return base
    return f"{base[:-1]} {type}>"


ALL_MARKERS: frozenset[str] = frozenset(
    marker(required, type_)
    for required in (True, False)
    for type_ in (None, *sorted(TYPED_MARKER_TYPES))
)
"""Toutes les formes qu'un marqueur peut prendre. Dérivées de `marker`, jamais recopiées."""


def accepted_markers(type: FieldType) -> frozenset[str]:
    """Les marqueurs qu'un champ de ce type accepte : les deux génériques — l'ancienne
    forme, tolérée — et les deux de son propre type, jamais ceux d'un autre."""
    return frozenset(marker(required, t) for required in (True, False) for t in (None, type))


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
    text: str | None = None  # texte littéral posé à la place du marqueur
    command: str | None = None  # commande dont la sortie est posée à la place du marqueur
    deprecated: str | None = None  # la consigne : ce champ n'est plus posé, et que faire de lui

    @property
    def marker(self) -> str:
        """Le marqueur que ce champ reçoit à la création.

        Un champ facultatif se marque comme une section facultative : sinon
        --filled réclamerait de remplir ce que le contrat dit optionnel. Un champ
        d'un type dont la valeur ne s'écrit pas en chaîne porte le marqueur de son
        type : voir `marker`.
        """
        return marker(self.required, self.type)


@dataclass(frozen=True)
class Capture(Field):
    """Une capture du motif d'une section, déclarée par `[sections.X.captures.<nom>]`.

    UN CHAMP, ET RIEN D'AUTRE À JUGER : sa valeur passe par `check_value` comme celle d'un
    champ. `min`, `max` et `sequence` sont des contraintes EN PLUS du type, jamais une
    seconde définition de l'entier. Requise par défaut, à l'inverse d'un champ : une
    capture facultative est l'exception que le contrat doit dire.
    """

    required: bool = True
    min: int | None = None  # int seulement
    max: int | None = None  # int seulement
    sequence: bool = False  # int seulement : la puce i vaut `min + i`, ou `1 + i` sans `min`


type SectionType = Literal["motif", "label"]
"""Les structures qu'une section peut déclarer par `type`. Sans `type`, la section est en
prose libre et suit exactement le chemin d'avant."""

# `__value__` d'un alias PEP 695 : voir FIELD_TYPES.
SECTION_TYPES: tuple[SectionType, ...] = cast(
    "tuple[SectionType, ...]",
    get_args(SectionType.__value__),  # pyright: ignore[reportAny]
)

type Forme = Literal["bold", "title"]
"""L'écriture des labels d'une section `label` : `**Nom** :`, ou un titre d'un rang de plus
que la table qui les porte. Une seule par table : deux formes à un même niveau ne se
déclarent pas."""

# `__value__` d'un alias PEP 695 : voir FIELD_TYPES.
FORMES: tuple[Forme, ...] = cast(
    "tuple[Forme, ...]",
    get_args(Forme.__value__),  # pyright: ignore[reportAny]
)

RANG_SECTION = 2
"""Le rang du titre d'une section : ses labels `title` sont du rang suivant."""

RANG_MAX = 6
"""Le rang du plus petit titre Markdown : un label `title` ne descend pas plus bas."""

ENTIER = re.compile(r"[+-]?[0-9]+")
"""Un entier en base 10, tel qu'une commande, un `text` ou une capture l'écrit. `[0-9]` et
non `\\d`, qui admettrait des chiffres d'autres écritures que `int()` convertirait sans
broncher."""

MOTIF_MARKER = "motif:"
"""Ce qui suit le statut dans le marqueur d'une section à motif, avant le motif lui-même."""

# Définis ici, et non dans motif.py qui les lit : `Section` en fait ses défauts.
DEBUT = "-"  # ce qui ouvre une puce, suivi d'un blanc
FIN = ";;"  # ce qui la ferme — « ; » seul paraît à l'intérieur de puces existantes
FIN_LIGNE = "\n"  # la puce finit à la ligne ; sa suite s'écrit en retrait, comme en Markdown


@dataclass(frozen=True)
class Section:
    """Une section déclarée au contrat."""

    name: str
    required: bool = False
    description: str = ""
    text: str | None = None  # texte littéral posé à la place du marqueur
    command: str | None = None  # commande dont la sortie est posée à la place du marqueur
    deprecated: str | None = None  # la consigne : cette section n'est plus posée
    type: SectionType | None = None  # None : prose libre
    motif: str | None = None  # type « motif » seulement : le gabarit de ligne de chaque puce
    debut: str = DEBUT
    fin: str = FIN
    captures: Mapping[str, Capture] = field(default_factory=dict[str, Capture])
    forme: Forme | None = None  # type « label » seulement
    labels: Mapping[str, Section] = field(
        default_factory=dict[str, "Section"]
    )  # type « label » seulement
    prefix: str | None = None  # type « label » : ce que dit la prose admise avant le 1er label
    order: int | None = None  # un label seulement : son rang parmi ceux qui en portent un

    @property
    def marker(self) -> str:
        """Le marqueur que cette section reçoit à la création. Voir Field.marker.

        Une section à motif porte son motif dans son marqueur, bornes comprises —
        `<À REMPLIR motif: - [{etat: enum}] {n: int}. {intitule} ;;>` : qui la remplit lit
        la forme d'une puce là où il l'écrit. Construit depuis `marker`, rien n'est recopié.

        `fin` SE COLLE AU MOTIF : `(gravité {g: int}).` ne prend pas d'espace avant son point,
        et un motif qui en veut une la porte à sa fin. Une `fin` de ligne ne s'y écrit pas :
        le marqueur tient sur une ligne.
        """
        base = marker(self.required)
        if self.type != "motif" or self.motif is None:
            return base
        fin = "" if self.fin == FIN_LIGNE else self.fin
        return f"{base[:-1]} {MOTIF_MARKER} {self.debut} {self.motif}{fin}>"


@dataclass(frozen=True)
class Contract:
    """Ce qu'un fichier doit contenir : ses champs et ses sections, dans l'ordre."""

    name: str
    description: str = ""
    fields: Mapping[str, Field] = field(default_factory=dict[str, Field])
    sections: Mapping[str, Section] = field(default_factory=dict[str, Section])

    @property
    def required_sections(self) -> list[str]:
        """Les titres requis, dans l'ordre du TOML — ce que lit store.py."""
        return [s.name for s in self.sections.values() if s.required]


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
    """Un fichier préstructuré : son chemin, son front matter, ses sections.

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
