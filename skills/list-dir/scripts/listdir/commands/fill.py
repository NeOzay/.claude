"""Pose une valeur sur un champ des éléments où il est resté au marqueur.

LE CAS QU'ELLE COUVRE : `migrate` pose un champ neuf au marqueur dans chaque élément,
et ne le remplit jamais — elle ne juge pas. Sans `fill`, l'écrire revient à éditer
chaque fichier à la main, et une valeur commune à tous (`severite = "inconnue"`) se
recopie autant de fois qu'il y a d'éléments.

ELLE NE JUGE PAS NON PLUS : la valeur vient de l'appelant. Elle ne touche jamais une
valeur écrite — avec `--all`, l'élément est sauté ; avec `--id`, l'appel échoue en le
nommant. La valeur est contrôlée contre le type déclaré avant toute écriture.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "pose une valeur sur un champ resté au marqueur"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument("champ", help="le champ à remplir, déclaré au contrat")
    parser.add_argument("valeur", help="la valeur à poser, contrôlée contre le type du champ")
    # Toucher tous les éléments d'un coup se demande : l'oubli de --id ne doit pas
    # remplir la liste entière avec une valeur pensée pour un seul élément.
    cible = parser.add_mutually_exclusive_group(required=True)
    _ = cible.add_argument(
        "--id",
        action="append",
        default=[],
        dest="ids",
        metavar="ID",
        help="ne remplir que cet élément (répétable) ; un champ déjà rempli fait échouer",
    )
    _ = cible.add_argument(
        "--all",
        action="store_true",
        dest="tous",
        help="remplir tous les éléments où le champ est au marqueur ; les autres sont sautés",
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

    champ = cast("str", args.champ)
    dry_run = cast("bool", args.dry_run)
    r = lst.fill(
        champ,
        cast("str", args.valeur),
        cast("list[str]", args.ids),
        dry_run=dry_run,
    )
    if not r:
        return utils.fail(r.message)

    changes = r.unwrap()
    if not changes:
        return utils.ok(f"{lst.path} : aucun champ « {champ} » au marqueur, aucun fichier touché")

    # Un changement par ligne, comme migrate : on relit un remplissage comme une
    # migration.
    detail = "\n".join(str(c) for c in changes)
    n = len(changes)
    s = "s" if n > 1 else ""
    verbe = ("seraient" if n > 1 else "serait") + f" rempli{s}" if dry_run else f"rempli{s}"
    return utils.ok(f"{detail}\n\n{lst.path} : {n} élément{s} {verbe}")
