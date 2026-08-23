"""Affiche un élément tel qu'il est sur le disque.

Le texte rendu est celui du fichier, à ceci près que le saut de ligne final est
retiré : la CLI en ajoute un en imprimant. Un script qui veut les octets exacts
passe par la bibliothèque — `lst.get(id).unwrap().render()`.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "affiche un élément"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument("id", help="l'identifiant de l'élément")


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    store = utils.open(cast("str", args.liste))
    if not store:
        return utils.fail(store.message)

    item = store.unwrap().get(cast("str", args.id))
    if not item:
        return utils.fail(item.message)
    return utils.ok(item.unwrap().render().rstrip("\n"))
