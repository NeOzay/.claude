"""Agglomère les éléments d'une liste en un seul document.

CONSERVATION VÉRIFIÉE : autant de blocs rendus que de fichiers dans le répertoire,
l'écart faisant échouer. Agglomérer zéro élément sans broncher se lirait « rien à
traiter » — le mode de défaillance que tout ce dispositif combat.

EXIGE QUE TOUT SOIT REMPLI : un document contenant encore un marqueur se lirait
comme instruit alors qu'il ne l'est pas. Les sections restées facultatives, elles,
sont omises : elles ont joué leur rôle de guide et n'ont rien à dire ici.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "agglomère les éléments en un document, conservation vérifiée"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument(
        "--out",
        default="",
        metavar="FICHIER",
        help="fichier de sortie ; sans lui, le document part sur la sortie standard",
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    store = utils.open(cast("str", args.liste))
    if not store:
        return utils.fail(store.message)
    lst = store.unwrap()

    out = cast("str", args.out)
    if not out:
        text = lst.merge_text()
        if not text:
            return utils.fail(text.message)
        return utils.ok(text.unwrap().rstrip("\n"))

    written = lst.merge(out)
    if not written:
        return utils.fail(written.message)
    return utils.ok(str(written.unwrap()))
