"""Crée une liste : son contrat squelette, ou celui d'une définition.

AUCUNE LOGIQUE ICI. Comme toutes les commandes, ce module se réduit à un
register() et à un appel de la bibliothèque : c'est ce qui garantit qu'un script
tiers et la ligne de commande font exactement la même chose. La résolution d'un
nom de définition vit dans definitions.py, la copie dans store.init_list.

DEUX OPTIONS, ET ELLES S'EXCLUENT. `--def` désigne une définition PAR SON NOM et la
fait résoudre dans les quatre rangs ; `--from` désigne un RÉPERTOIRE, tel quel.
argparse refuse lui-même la combinaison — un `--def` et un `--from` ensemble
poseraient la question de qui gagne, et toute réponse serait arbitraire.

POURQUOI `--from` EXISTE malgré `--def` : une définition qui n'est encore rangée
dans aucun rang doit pouvoir s'essayer avant d'être installée. Sans cette porte,
la seule façon de tester une définition serait de la déployer.

IMPORTS ABSOLUS, jamais relatifs : un module de commande est chargé par chemin de
fichier, hors de tout paquet. `from ..types import` lèverait ImportError.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

from listdir.definitions import resolve, roots
from listdir.store import init_list
from listdir.types import Result, Utils

DESCRIPTION = "crée une liste, d'un contrat squelette ou d'une définition"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("repertoire", help="le répertoire à transformer en liste")
    parser.add_argument("--name", default="", help="nom de la liste (défaut : nom du répertoire)")
    parser.add_argument("--description", default="", help="description portée par le contrat")
    source = parser.add_mutually_exclusive_group()
    _ = source.add_argument(
        "--def", dest="definition", default="", help="une définition, par son nom"
    )
    _ = source.add_argument(
        "--from", dest="depuis", default="", help="une définition, par son chemin"
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    nom = cast("str", args.definition)
    chemin = cast("str", args.depuis)
    libelle = cast("str", args.name)
    desc = cast("str", args.description)

    # `--name` et `--description` n'écrivent que le SQUELETTE : une définition porte
    # déjà les siennes, et les écraser ferait mentir le diff qui prouve qu'une
    # semence est la copie de son original. Les accepter en les ignorant serait un
    # échec ouvert — la commande rendrait 0 sur un contrat qui ne porte pas ce qui
    # a été demandé, et rien ne le dirait. Code 2 : c'est une erreur d'appel, au
    # même titre que `--def` et `--from` ensemble.
    if (nom or chemin) and (libelle or desc):
        return utils.fail(
            "--name et --description ne s'appliquent qu'au squelette : "
            "une définition porte déjà les siennes",
            2,
        )

    definition: Path | None = None
    if nom:
        trouve = resolve(nom, roots())
        if not trouve:
            return utils.fail(trouve.message)
        definition = trouve.unwrap()
    elif chemin:
        definition = Path(chemin)

    r = init_list(Path(cast("str", args.repertoire)), libelle, desc, definition)
    if not r:
        return utils.fail(r.message)
    return utils.ok(str(r.unwrap()))
