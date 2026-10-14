"""Inverse un booléen écrit sur les éléments désignés.

LE CAS QU'ELLE COUVRE : un `pin` ou un `archive` qui se bascule d'un geste, sans que
l'appelant lise la valeur pour dire la contraire — c'est `fill --override` sans la valeur.

ELLE NE BASCULE QUE CE QUI A UN ÉTAT : un `bool` écrit. Un autre type, un `bool` resté
au marqueur ou absent fait échouer l'appel en le nommant. ELLE NE CONNAÎT PAS `--all` :
inverser tous les éléments d'une liste n'a pas de sens, chacun partant d'un état différent.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "inverse un booléen écrit sur les éléments désignés"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument("champ", help="le champ bool à inverser, déclaré au contrat")
    # Requis, et sans pendant `--all` : l'oubli de --id ne doit rien basculer.
    _ = parser.add_argument(
        "--id",
        action="append",
        default=[],
        dest="ids",
        metavar="ID",
        required=True,
        help="l'élément à basculer (répétable)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="montre ce qui serait fait sans écrire dans aucun fichier",
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    store = utils.open(cast("str", args.liste))
    if not store:
        return utils.fail(store.message)
    lst = store.unwrap()

    dry_run = cast("bool", args.dry_run)
    r = lst.toggle(cast("str", args.champ), cast("list[str]", args.ids), dry_run=dry_run)
    if not r:
        return utils.fail(r.message, r.status)

    changes = r.unwrap()
    detail = "\n".join(str(c) for c in changes)
    n = len(changes)
    s = "s" if n > 1 else ""
    verbe = ("seraient" if n > 1 else "serait") + f" basculé{s}" if dry_run else f"basculé{s}"
    return utils.ok(f"{detail}\n\n{lst.path} : {n} élément{s} {verbe}")
