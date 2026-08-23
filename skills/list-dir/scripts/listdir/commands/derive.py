"""Projette la structure d'une liste sur une liste neuve.

CE N'EST PAS UNE COPIE. Chaque élément source engendre une fiche de même `id`,
mais dont le corps vient du gabarit, jamais de la source. Une fiche qui porterait
la prose de l'élément qu'elle instruit en serait un doublon éditable, et la source
unique serait perdue.

Le gabarit est une paire, dans la liste SOURCE :

    <src>/.list/templates/<nom>.toml   le contrat de la liste engendrée
    <src>/.list/templates/<nom>.md     le moule d'une fiche, sections au marqueur

C'est ce qui laisse ce skill ignorant de ses consommateurs : les sections
préétablies viennent du contrat de leur liste, jamais d'une chaîne écrite ici.
"""

from __future__ import annotations

import argparse
from typing import cast

from listdir.types import Result, Utils

DESCRIPTION = "projette une liste sur une liste neuve, depuis une paire de gabarits"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("source", help="la liste à projeter")
    parser.add_argument("destination", help="la liste à créer — elle ne doit pas exister")
    parser.add_argument(
        "--template",
        required=True,
        metavar="NOM",
        help="nom de la paire <NOM>.toml / <NOM>.md dans .list/templates/ de la source",
    )


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    source = utils.open(cast("str", args.source))
    if not source:
        return utils.fail(source.message)

    derived = source.unwrap().derive(cast("str", args.destination), cast("str", args.template))
    if not derived:
        return utils.fail(derived.message)

    lst = derived.unwrap()
    return utils.ok(f"{lst.path} — {len(lst.paths())} fiche(s) à instruire")
