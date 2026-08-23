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


def ok[T](value: T = None) -> Result[T]:
    return Result(0, value)


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

    @property
    def marker(self) -> str:
        """Le marqueur que ce champ reçoit à la création.

        Un champ facultatif se marque comme une section facultative : sinon
        --filled réclamerait de remplir ce que le contrat dit optionnel.
        """
        return PLACEHOLDER if self.required else OPTIONAL


@dataclass(frozen=True)
class Contract:
    name: str
    description: str = ""
    fields: Mapping[str, Field] = field(default_factory=dict[str, Field])
    required_sections: list[str] = field(default_factory=list)
    optional_sections: list[str] = field(default_factory=list)

    def section_marker(self, title: str) -> str:
        return PLACEHOLDER if title in self.required_sections else OPTIONAL

    @property
    def sections(self) -> list[str]:
        """Toutes les sections, requises d'abord — l'ordre dans lequel `new` les pose."""
        return [*self.required_sections, *self.optional_sections]


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
    TOML tel qu'il a été lu, et render() le reconduit tel quel tant qu'il est là.
    Muter `fields` en place le ferait diverger de `raw_front` sans que rien ne le
    signale. with_fields() rend une copie dont `raw_front` est None — c'est ce
    None, et lui seul, qui déclenche une resérialisation.
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
        return replace(self, fields={**self.fields, **kw}, raw_front=None)

    def with_sections(self, **kw: str) -> Item:
        return replace(self, sections={**self.sections, **kw})

    def realigned(self, fields: Mapping[str, object], sections: Mapping[str, str]) -> Item:
        """Le même élément, champs et sections REMPLACÉS — non fusionnés.

        with_fields et with_sections fusionnent : ils savent ajouter et écraser,
        jamais retirer ni réordonner. Or c'est exactement ce qu'une migration doit
        pouvoir faire quand le contrat a changé d'ordre ou perdu un champ. D'où ce
        troisième constructeur, et la resérialisation qu'il impose (raw_front None).
        """
        return replace(self, fields=dict(fields), sections=dict(sections), raw_front=None)

    def render(self) -> str:
        from .items import render_item

        return render_item(self)


# ------------------------------------------------------------------ protocoles
class Utils(Protocol):
    """Ce qu'une commande reçoit. Le noyau ne lui donne rien d'autre."""

    def open(self, list_dir: Path | str) -> Result[ListStore]: ...
    def git(self, *argv: str) -> Result[str]: ...
    def run(self, name: str, argv: list[str]) -> Result[object]: ...
    def ok[T](self, value: T) -> Result[T]: ...
    def fail(self, message: str, code: int = 1) -> Result[Never]: ...


class Command[T](Protocol):
    """Ce qu'un module de commande doit exposer. Vérifié au chargement."""

    DESCRIPTION: str
    REQUIRES: list[str]

    def register(self, parser: object) -> None: ...
    def command(self, args: object, utils: Utils) -> Result[T]: ...
