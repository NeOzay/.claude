"""Rattrape une liste sur la définition qui l'a semée.

AUCUNE LOGIQUE ICI, comme toute commande : la résolution du nom vit dans
definitions.py, la fusion et l'écriture dans provenance.py. Ce module choisit la
semence visée, appelle, et met la sortie en page.

LA SEMENCE SE DÉSIGNE DE TROIS FAÇONS, et la troisième est la seule qu'on tape :
`--def <nom>` la résout dans les quatre rangs, `--from <chemin>` la prend telle
quelle, et sans option c'est l'`origin.def` de la liste qui parle. C'est tout
l'intérêt de l'estampille — une liste sait d'où elle vient, on n'a pas à le lui
rappeler.

UNE LISTE SANS PROVENANCE ET SANS OPTION EST UN ÉCHEC NOMMÉ, jamais un repli sur
une devinette : deviner la définition d'après le `name` du contrat marcherait
souvent, et écraserait un jour une liste avec le contrat d'une homonyme.

IMPORTS ABSOLUS, jamais relatifs : un module de commande est chargé par chemin de
fichier, hors de tout paquet.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

from listdir.contract import load_contract
from listdir.definitions import resolve, roots
from listdir.provenance import reseed
from listdir.types import Result, Utils

DESCRIPTION = "rattrape le contrat d'une liste sur la définition qui l'a semée"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")
    source = parser.add_mutually_exclusive_group()
    _ = source.add_argument("--def", dest="definition", default="", help="la semence, par son nom")
    _ = source.add_argument("--from", dest="depuis", default="", help="la semence, par son chemin")
    parser.add_argument(
        "--force",
        action="store_true",
        help="passe outre un « frozen = true » ; ne tranche aucun conflit",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="montre ce qui serait fait sans rien écrire"
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    liste = Path(cast("str", args.liste))
    nom = cast("str", args.definition)
    chemin = cast("str", args.depuis)

    lu = load_contract(liste)
    if not lu:
        return utils.fail(lu.message)
    origin = lu.unwrap().origin

    if chemin:
        definition = Path(chemin)
    else:
        vise = nom or (origin.name if origin is not None and origin.name is not None else "")
        if not vise:
            return utils.fail(
                f"{liste} : aucune semence à rattraper — cette liste ne déclare pas "
                "d'« origin.def », et ni « --def » ni « --from » n'ont été donnés"
            )
        trouve = resolve(vise, roots())
        if not trouve:
            return utils.fail(trouve.message)
        definition = trouve.unwrap()

    # LE NOM ÉCRIT ENGAGE LA SEMENCE, comme à l'`init` : rattraper une liste sur une
    # définition qui se nomme autrement lui poserait une estampille pointant ailleurs
    # que là où elle vient d'être rattrapée. Le contrôle vit dans la bibliothèque.
    r = reseed(
        liste,
        definition,
        force=cast("bool", args.force),
        dry_run=cast("bool", args.dry_run),
        expected_name=nom,
    )
    if not r:
        # LE CODE DE LA BIBLIOTHÈQUE EST REPORTÉ TEL QUEL. `utils.fail` retombe sur 1
        # quand on ne lui en donne pas, et une erreur d'appel rendue en 2 par la
        # bibliothèque redescendait alors en simple échec : la commande annonçait
        # autre chose que ce qu'elle avait décidé, sans qu'aucun test de bibliothèque
        # puisse le voir.
        return utils.fail(r.message, r.status)

    fait = r.unwrap()
    if not fait.changements:
        etat = "déjà à jour" if fait.ecrit else "déjà à jour, rien à faire"
        return utils.ok(f"{liste} : {etat} sur {definition}")

    detail = "\n".join(f"  {c}" for c in fait.changements)
    verbe = "appliqués" if fait.ecrit else "seraient appliqués"
    bilan = f"{liste} : {len(fait.changements)} changement(s) {verbe} depuis {definition}"
    if fait.ecrit and not fait.verbatim:
        bilan += (
            "\nLe contrat a été réémis : les commentaires de la version précédente "
            "sont dans .list/backup/."
        )
    return utils.ok(f"{detail}\n\n{bilan}")
