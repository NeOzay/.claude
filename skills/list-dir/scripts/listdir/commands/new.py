"""Crée un élément prérempli de TOUT le contrat.

Champs et sections, requis comme facultatifs, chacun portant le marqueur de son
statut. Poser aussi le facultatif n'est pas de la générosité : ce qu'on ne voit
pas n'est jamais rempli, et c'est le modèle qui remplira ce fichier.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "crée un élément prérempli du contrat"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument("id", help="l'identifiant de l'élément — il devient le nom du fichier")


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    store = utils.open(cast("str", args.liste))
    if not store:
        return utils.fail(store.message)
    lst = store.unwrap()

    item = lst.create(cast("str", args.id))
    if not item:
        return utils.fail(item.message)

    written = lst.write(item.unwrap())
    if not written:
        return utils.fail(written.message)
    return utils.ok(str(written.unwrap()))
