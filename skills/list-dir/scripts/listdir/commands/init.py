"""Crée une liste et son contrat squelette.

AUCUNE LOGIQUE ICI. Comme toutes les commandes, ce module se réduit à un
register() et à un appel de la bibliothèque : c'est ce qui garantit qu'un script
tiers et la ligne de commande font exactement la même chose.

IMPORTS ABSOLUS, jamais relatifs : un module de commande est chargé par chemin de
fichier, hors de tout paquet. `from ..types import` lèverait ImportError.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

from listdir.store import init_list
from listdir.types import Result, Utils

DESCRIPTION = "crée une liste et son contrat squelette"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("repertoire", help="le répertoire à transformer en liste")
    parser.add_argument("--name", default="", help="nom de la liste (défaut : nom du répertoire)")
    parser.add_argument("--description", default="", help="description portée par le contrat")


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    r = init_list(
        Path(cast("str", args.repertoire)), cast("str", args.name), cast("str", args.description)
    )
    if not r:
        return utils.fail(r.message)
    return utils.ok(str(r.unwrap()))
