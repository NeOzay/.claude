"""Les commandes disponibles, avec leur description.

C'EST LE SEUL POINT D'OÙ L'INTERFACE COMPLÈTE SE DÉCOUVRE : les génériques, et
celles que la liste visée ajoute ou substitue. Sans une liste en argument, seules
les génériques sont visibles — ce qui est exact, et non un oubli.

RIEN N'EST EXÉCUTÉ POUR AFFICHER CETTE PAGE. Les descriptions sont lues par
analyse syntaxique (`ast.parse`), jamais par import : afficher l'aide ne doit pas
pouvoir lancer le code d'un module déposé dans une liste, ni échouer parce que ce
module est cassé. Un module illisible est SIGNALÉ comme tel, à sa place, et les
autres restent listés.

NON SURCHARGEABLE (cf. loader.PROTECTED) : une liste qui redéfinirait `help`
pourrait cacher ses propres commandes. Une surcharge invisible est un piège, et
c'est précisément ce que la mention « (surchargée) » existe pour empêcher.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from listdir.loader import CommandSpec, discover
from listdir.types import Result, Utils

DESCRIPTION = "les commandes disponibles, génériques et propres à la liste"
REQUIRES: list[str] = []

# Le nom sous lequel on a été appelé, comme dans `list-dir.py` : un usage affiché doit
# être recopiable tel quel, et le point d'entrée peut porter n'importe quel nom.
USAGE = f"{Path(sys.argv[0]).name} <commande> [<liste>] [options]"


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "liste",
        nargs="?",
        help="un répertoire-liste, pour voir aussi les commandes qu'il ajoute",
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    brut = cast("str | None", args.liste)
    list_dir = Path(brut) if brut else None
    if list_dir is not None and not (list_dir / ".list").is_dir():
        return utils.fail(f"{list_dir}: n'est pas un répertoire-liste — .list/ attendu")

    commands, refus = discover(list_dir)
    if refus:
        # Une surcharge interdite n'est jamais tue : la cacher ferait croire à
        # l'auteur que sa commande est prise en compte.
        return utils.fail("\n".join(refus))

    def tri(origine: str) -> list[CommandSpec]:
        return sorted((s for s in commands.values() if s.origin == origine), key=lambda s: s.name)

    generiques, propres = tri("générique"), tri("liste")

    lignes = [f"usage: {USAGE}", "", f"Commandes génériques ({len(generiques)}) :"]
    lignes += [_ligne(s) for s in generiques]
    if list_dir is None:
        lignes += ["", "Passer un répertoire-liste en argument montre aussi ses commandes propres."]
    elif propres:
        lignes += ["", f"Commandes de {list_dir} ({len(propres)}) :"]
        lignes += [_ligne(s) for s in propres]
    else:
        lignes += ["", f"{list_dir} n'ajoute aucune commande."]
    return utils.ok("\n".join(lignes))


def _ligne(spec: CommandSpec) -> str:
    if spec.broken:
        return f"  {spec.name:<9} INUTILISABLE — {spec.broken}"
    marques = ""
    if spec.overrides:
        marques += "  (surchargée)"
    if spec.requires:
        marques += f"  [exige {', '.join(spec.requires)}]"
    return f"  {spec.name:<9} {spec.description}{marques}"
