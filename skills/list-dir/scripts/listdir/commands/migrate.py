"""Remet les éléments d'une liste en conformité avec son contrat courant.

LE CAS QU'ELLE COUVRE : le contrat change — un champ apparaît, une section est
ajoutée, l'ordre est remanié — et tous les éléments écrits avant deviennent
invalides d'un coup. Sans elle, la seule issue serait l'édition à la main de
chaque fichier, c'est-à-dire précisément ce que ce format existe pour supprimer.

NON SURCHARGEABLE (cf. loader.PROTECTED) : elle réécrit des fichiers en se
réclamant du contrat. Une liste qui redéfinirait « mettre en conformité »
pourrait réécrire ce qu'elle veut sous couvert d'une commande générique.

ELLE NE JUGE PAS. Elle pose ce qui manque au marqueur et remet dans l'ordre ;
elle ne renomme rien, ne reporte aucune valeur, ne supprime rien de son propre
chef. Un champ que le contrat ne déclare plus est conservé et signalé — `--drop`,
demandé explicitement, le retire. Le renommage d'un champ reste au modèle, qui
seul a le contexte pour dire que `severite` est devenu `gravite`.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "remet les éléments en conformité avec le contrat courant"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="retire les champs et sections que le contrat ne déclare plus (destructif)",
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

    drop = cast("bool", args.drop)
    dry_run = cast("bool", args.dry_run)
    r = lst.migrate(drop=drop, dry_run=dry_run)
    if not r:
        return utils.fail(r.message)

    changes = r.unwrap()
    if not changes:
        return utils.ok(f"{lst.path} : déjà conforme au contrat, aucun fichier touché")

    # Un changement par ligne, chacun nommant fichier, sujet et acte : la même
    # sortie que validate, pour qu'on relise une migration comme on relit un
    # manquement.
    detail = "\n".join(str(c) for c in changes)
    faits = sum(1 for c in changes if c.applied)
    remarques = len(changes) - faits

    if faits > 1:
        bilan = f"{faits} changements {'seraient appliqués' if dry_run else 'appliqués'}"
    elif faits == 1:
        bilan = f"1 changement {'serait appliqué' if dry_run else 'appliqué'}"
    else:
        bilan = "aucun changement"
    if remarques:
        bilan += f", {remarques} remarque{'s' if remarques > 1 else ''} sans écriture"
    return utils.ok(f"{detail}\n\n{lst.path} : {bilan}")
