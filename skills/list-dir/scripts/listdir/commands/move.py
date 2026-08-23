"""Déplace un élément d'une liste vers une autre. `git mv`, et rien d'autre.

L'ÉTAT EST PORTÉ PAR LE RÉPERTOIRE, jamais par un champ : changer l'état d'un
élément, c'est le déplacer, pas lui écrire son nouvel état. Cette commande n'écrit
donc dans aucun fichier — c'est ce qui laisse la détection de renommage de Git
opérer, et `git log --follow` remonter jusqu'au commit de création dans la liste
de départ.

Ce que le contrat d'arrivée exige en plus est RAPPELÉ SUR STDERR, jamais imposé :
le déplacement a réussi, et stdout ne porte que le chemin d'arrivée, pour qu'un
script puisse le lire sans le démêler d'un commentaire.
"""

from __future__ import annotations

import argparse
import sys
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "déplace un élément vers une autre liste — git mv seul"
REQUIRES: list[str] = ["git"]


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="la liste de départ")
    parser.add_argument("id", help="l'identifiant de l'élément")
    parser.add_argument("cible", help="la liste d'arrivée")


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    source = utils.open(cast("str", args.liste))
    if not source:
        return utils.fail(source.message)
    cible = utils.open(cast("str", args.cible))
    if not cible:
        return utils.fail(cible.message)

    item_id = cast("str", args.id)
    moved = source.unwrap().move(item_id, cible.unwrap())
    if not moved:
        return utils.fail(moved.message)
    destination = moved.unwrap()

    arrived = cible.unwrap().get(item_id)
    if not arrived:
        return utils.fail(arrived.message)

    manquements = cible.unwrap().check_item(arrived.unwrap())
    if manquements:
        sys.stderr.write(
            f"déplacé. Le contrat de {cible.unwrap().path} demande encore :\n"
            + "".join(f"  {v.subject} — {v.reason}\n" for v in manquements)
            + "Les compléter demande un SECOND commit : ce commit-ci doit rester "
            "un renommage pur, sinon git perd la trace de l'élément.\n"
        )
    return utils.ok(str(destination))
