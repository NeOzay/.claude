"""Une ligne par élément : son id, puis les champs demandés à `--sort`.

FORMAT DÉLIBÉRÉMENT PAUVRE — un id par ligne, des champs séparés par une espace.
C'est ce qui se lit dans un `while read`, se compte au `wc -l` et se coupe au
`cut`. Un tableau aligné serait plus joli et inutilisable par un script.

FILTRER N'EST PAS CHERCHER : `--where` porte sur les champs déclarés au contrat,
et rien d'autre. Un plein texte referait `grep` en moins bien.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Item, Result, Utils

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
        help="champs de tri, séparés par des virgules ; ils sont aussi affichés",
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

    columns = [c for c in cast("str", args.sort).split(",") if c]
    connus = ", ".join(lst.contract.fields) or "aucun"
    for name in columns:
        if name not in lst.contract.fields:
            return utils.fail(
                f"--sort : champ « {name} » non déclaré au contrat ; connus : {connus}"
            )

    # where() porte déjà le refus d'un champ inconnu : le refaire ici ferait deux
    # définitions de la même règle, qui finiraient par diverger.
    found = lst.where(**criteria)
    if not found:
        return utils.fail(found.message)

    items = sorted(found.unwrap(), key=lambda it: _key(it, columns))
    lines = [" ".join([it.id, *(_cell(it, c) for c in columns)]) for it in items]

    # Aucun élément : aucune ligne, et code 0. Un filtre qui ne rend rien est une
    # réponse, pas une erreur — contrairement à merge, qui perdrait un élément.
    return utils.ok("\n".join(lines) if lines else None)


def _cell(item: Item, name: str) -> str:
    value = item.fields.get(name)
    return "" if value is None else str(value)


def _key(item: Item, columns: list[str]) -> tuple[str, ...]:
    """Tri par les colonnes demandées, l'id en dernier ressort.

    Les valeurs sont comparées sous leur forme textuelle : une date ISO s'ordonne
    alors comme une date, et deux types différents dans un même champ ne font pas
    lever le tri — c'est validate qui juge la conformité, pas list.
    """
    return (*(_cell(item, c) for c in columns), item.id)
