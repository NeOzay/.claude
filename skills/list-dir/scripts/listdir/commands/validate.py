"""Confronte chaque élément de la liste à son contrat.

NON SURCHARGEABLE (cf. loader.PROTECTED) : une liste qui redéfinirait ce que
« valide » veut dire viderait le contrat de son sens. C'est la seule commande,
avec `help`, dont le comportement est le même partout.

DEUX VERDICTS. Sans `--filled`, la structure seule — les marqueurs sont légitimes.
Avec `--filled`, plus aucun marqueur là où le contrat exige quelque chose, sans
jamais réclamer ce qu'il dit facultatif.

LES AVERTISSEMENTS DE PROVENANCE SORTENT DANS LES DEUX CAS, et ne changent ni l'un
ni l'autre. Une liste dont la semence a évolué n'a aucun élément fautif : la taire
sur un succès laisserait la péremption invisible là où on la cherche justement, et
la compter comme un manquement déclarerait invalide une liste en règle.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.provenance import warnings
from listdir.types import Result, Utils

DESCRIPTION = "vérifie les éléments contre le contrat ; --filled exige qu'ils soient remplis"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    parser.add_argument(
        "--filled",
        action="store_true",
        help="exige en plus qu'aucun marqueur ne subsiste sur un champ ou une section requis",
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    store = utils.open(cast("str", args.liste))
    if not store:
        return utils.fail(store.message)
    lst = store.unwrap()

    # LES AVERTISSEMENTS SE CALCULENT AVANT LE PREMIER RETOUR, et pas après le
    # dernier : un élément illisible fait sortir `validate` sans jamais parcourir la
    # suite, et la péremption disparaissait alors du seul appel où l'on regarde la
    # liste de plus près.
    note = "\n".join(warnings(lst.path, lst.contract))

    filled = cast("bool", args.filled)
    r = lst.validate(filled=filled)
    if not r:
        return utils.fail(f"{r.message}\n\n{note}" if note else r.message)

    violations = r.unwrap()
    if violations:
        # Un manquement par ligne, chacun nommant fichier, sujet et cause : c'est
        # la sortie qu'on relit pour corriger, pas un décompte.
        detail = "\n".join(str(v) for v in violations)
        pluriel = "s" if len(violations) > 1 else ""
        bilan = f"{detail}\n\n{lst.path} : {len(violations)} manquement{pluriel}"
        return utils.fail(f"{bilan}\n\n{note}" if note else bilan)

    quoi = "remplis et conformes" if filled else "conformes"
    return utils.ok(f"{lst.path} : {len(lst.paths())} élément(s) {quoi} au contrat", note)
