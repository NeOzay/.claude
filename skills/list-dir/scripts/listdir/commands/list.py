"""Une ligne par élément : son id, puis les champs demandés à `--sort`.

FORMAT DÉLIBÉRÉMENT PAUVRE — un id par ligne, des champs séparés par une espace.
C'est ce qui se lit dans un `while read`, se compte au `wc -l` et se coupe au
`cut`. Un tableau aligné serait plus joli et inutilisable par un script.

`--sort=a,-b` : un `-` en tête d'un champ le trie en décroissant (la forme collée, car
argparse prend `--sort -b` pour une option). La clé suit le type
déclaré au contrat — un `int` en nombre, un `enum` dans l'ordre de ses `values`, un
`bool` faux avant vrai —, et ce qui n'est pas une valeur reste en fin quel que soit le sens.

FILTRER N'EST PAS CHERCHER : `--where` porte sur les champs déclarés au contrat,
et rien d'autre. Un plein texte referait `grep` en moins bien.
"""

from __future__ import annotations

import argparse
import functools
from typing import NamedTuple, cast

from listdir.contract import check_value, is_marker
from listdir.store import forme_texte
from listdir.types import Contract, Field, Item, Result, Utils

DESCRIPTION = "liste les éléments ; --where filtre, --sort ordonne et affiche"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument(
        "--where",
        action="append",
        default=[],
        metavar="CHAMP=VALEUR",
        help="filtre sur un champ déclaré ; répétable, les critères se cumulent",
    )
    parser.add_argument(
        "--sort",
        default="",
        metavar="CHAMPS",
        help="champs de tri, séparés par des virgules ; ils sont aussi affichés. Un `-` en "
        "tête trie en décroissant, et s'écrit collé : --sort=-CHAMP (argparse prendrait "
        "`--sort -CHAMP` pour une option)",
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str | None]:
    store = utils.open(cast("str", args.liste))
    if not store:
        return utils.fail(store.message)
    lst = store.unwrap()

    criteria: dict[str, str] = {}
    for raw in cast("list[str]", args.where):
        name, sep, value = raw.partition("=")
        if not sep or not name:
            return utils.fail(f"--where « {raw} » — la forme attendue est CHAMP=VALEUR")
        criteria[name] = value

    columns: list[Colonne] = []
    connus = ", ".join(lst.contract.fields) or "aucun"
    for raw in (c for c in cast("str", args.sort).split(",") if c):
        name = raw.removeprefix("-")
        if not name:
            return utils.fail("--sort : « - » doit précéder le nom d'un champ")
        if name not in lst.contract.fields:
            return utils.fail(
                f"--sort : champ « {name} » non déclaré au contrat ; connus : {connus}"
            )
        columns.append(Colonne(name, desc=raw.startswith("-")))

    # where() porte déjà le refus d'un champ inconnu : le refaire ici ferait deux
    # définitions de la même règle, qui finiraient par diverger.
    found = lst.where(**criteria)
    if not found:
        return utils.fail(found.message)

    items = sorted(
        found.unwrap(),
        key=functools.cmp_to_key(lambda a, b: _compare(a, b, columns, lst.contract)),
    )
    lines = [" ".join([it.id, *(_cell(it, c.name) for c in columns)]) for it in items]

    # Aucun élément : aucune ligne, et code 0. Un filtre qui ne rend rien est une
    # réponse, pas une erreur — contrairement à merge, qui perdrait un élément.
    return utils.ok("\n".join(lines) if lines else None)


def _cell(item: Item, name: str) -> str:
    value = item.fields.get(name)
    return "" if value is None else forme_texte(value)


class Colonne(NamedTuple):
    """Une colonne de `--sort` : le champ, et le sens.

    UN `NamedTuple`, PAS UN `dataclass` : le chargeur exécute ce module sans l'inscrire dans
    `sys.modules`, et `@dataclass` y cherche le module de sa classe.
    """

    name: str
    desc: bool = False


# Les trois groupes d'une valeur, dans l'ordre où ils se rangent.
CONFORME, NON_CONFORME, SANS_VALEUR = 0, 1, 2


def _rang(f: Field, value: object) -> tuple[int, int | str]:
    """Où une valeur se range : son groupe, puis ce qui la compare à ses pairs.

    TROIS GROUPES, et seul le premier se compare selon le type : une valeur conforme au
    contrat (un `int` en nombre, un `enum` par rang dans ses `values`, un `bool` faux avant
    vrai), puis une valeur non conforme (comparée en texte), puis l'absence ou le marqueur.
    Deux groupes ne se comparent jamais au-delà de leur rang : un type mêlé ne fait pas
    lever le tri — c'est `validate` qui juge la conformité, pas `list`.
    """
    if value is None or is_marker(value):
        return (SANS_VALEUR, 0)
    if check_value(f, value):
        return (NON_CONFORME, forme_texte(value))
    match f.type:
        case "int" | "bool":
            return (CONFORME, int(cast("int", value)))
        case "enum":
            return (CONFORME, f.values.index(cast("str", value)))
        case _:
            return (CONFORME, forme_texte(value))


def _compare(a: Item, b: Item, columns: list[Colonne], contract: Contract) -> int:
    """Compare deux éléments colonne après colonne, l'id en dernier ressort.

    LE SENS NE S'APPLIQUE QU'À LA COMPARAISON DES VALEURS d'un même groupe : le groupe
    n'est jamais inversé, de sorte que l'absence et les marqueurs restent en fin dans les
    deux sens. L'id, lui, reste croissant.
    """
    for c in columns:
        f = contract.fields[c.name]
        ga, va = _rang(f, a.fields.get(c.name))
        gb, vb = _rang(f, b.fields.get(c.name))
        if ga != gb:
            return -1 if ga < gb else 1
        if va != vb:
            # Au sein d'un groupe, les deux valeurs ont le même type : int/int ou str/str.
            sens = -1 if va < vb else 1  # pyright: ignore[reportOperatorIssue]
            return -sens if c.desc else sens
    if a.id == b.id:
        return 0
    return -1 if a.id < b.id else 1
