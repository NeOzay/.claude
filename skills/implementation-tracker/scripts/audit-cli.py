#!/usr/bin/env python3
"""Point d'entrée en ligne de commande des rapports d'audit.

AUCUNE LOGIQUE MÉTIER ICI. Ce fichier parse des arguments, appelle le paquet `rapport_audit` et
traduit le résultat en code de sortie. La commande s'appelle `audit` par son lien de `bin/`.

ÉCHEC FERMÉ : sortie 2 sur une erreur d'appel, 1 sur un échec nommé sur stderr, une faute par
ligne.

LES DEUX GARDES SONT CELLES DE `gabarit-cli.py`, et pour les mêmes raisons : la version de
Python avant tout import (syntaxe PEP 695), puis la ré-exécution dans le venv du dépôt, seul à
porter Pydantic et tomlkit.
"""

import sys

# `noqa: UP036` : ruff juge ce bloc mort parce que target-version vaut py312. Il n'existe que
# pour le Python plus ancien qui exécuterait ce fichier.
if sys.version_info < (3, 12):  # noqa: UP036
    v = ".".join(str(n) for n in sys.version_info[:3])  # pyright: ignore[reportUnreachable]
    sys.stderr.write(f"audit exige Python >= 3.12, trouvé {v} ({sys.executable}).\n")
    raise SystemExit(2)

import os
from pathlib import Path

# Voir `list-dir.py` pour le raisonnement complet : `sys.prefix` et non `sys.executable`, un
# seul `if` pour ne pas déclencher E402, et un venv absent qui ne bloque rien — c'est
# sante_skills qui le signale.
if (
    _venv := next(
        (
            a / ".venv"
            for a in Path(__file__).resolve().parents
            if (a / ".venv/bin/python").exists()
        ),
        None,
    )
) is not None and Path(sys.prefix).resolve() != _venv.resolve():
    _python = str(_venv / "bin" / "python")
    os.execv(_python, [_python, str(Path(__file__).resolve()), *sys.argv[1:]])

sys.path.insert(0, str(Path(__file__).resolve().parent))

import argparse
import datetime as dt
from typing import cast

from rapport_audit.dettes import Tableau, ajouter, ranger
from rapport_audit.export import exporter_vers
from rapport_audit.modele import NATURES, SEVERITES, Nature, Severite, controler, verdicts_admis
from rapport_audit.pose import Type, poser


def _check(fichier: Path, rempli: bool) -> int:
    r = controler(fichier, rempli)
    if not r:
        sys.stderr.write(r.message + "\n")
        return 1
    admis = verdicts_admis(r.unwrap().dette.actuelle)
    if admis is None:
        print("verdicts admis : à connaître, une sévérité de la Dette actuelle reste à remplir")
    else:
        print("verdicts admis : " + " ou ".join(sorted(admis)))
    return 0


def _new(slug: str, type_: Type) -> int:
    r = poser(Path.cwd(), slug, type_, dt.date.today())
    if not r:
        sys.stderr.write(r.message + "\n")
        return 1
    print(r.unwrap())
    return 0


def _range(fichier: Path, id_: str, vers: Tableau, preuve: str | None) -> int:
    r = ranger(fichier, id_, vers, preuve)
    if not r:
        sys.stderr.write(r.message + "\n")
        return 1
    print(r.unwrap())
    return 0


def _dette(fichier: Path, nature: Nature, severite: Severite) -> int:
    r = ajouter(fichier, nature, severite)
    if not r:
        sys.stderr.write(r.message + "\n")
        return 1
    print(r.unwrap())
    return 0


def _export(fichier: Path, scratchpad: Path) -> int:
    r = exporter_vers(fichier, scratchpad)
    if not r:
        sys.stderr.write(r.message + "\n")
        return 1
    print(r.unwrap())
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="audit", description="Rapports d'audit de Chantier")
    sub = parser.add_subparsers(dest="commande", required=True)
    p = sub.add_parser("new", help="pose le rapport suivant du Chantier, et affiche son chemin")
    p.add_argument("slug", metavar="SLUG")
    quand = p.add_mutually_exclusive_group(required=True)
    quand.add_argument(
        "--cloture", dest="type", action="store_const", const="clôture", help="audit de Clôture"
    )
    quand.add_argument(
        "--intermediaire",
        dest="type",
        action="store_const",
        const="intermédiaire",
        help="audit intermédiaire",
    )
    p = sub.add_parser(
        "check",
        help="contrôle un rapport, puis sa suite au précédent ; affiche les verdicts admis",
    )
    p.add_argument("fichier", metavar="FICHIER", help="le rapport, <NN>-<sha>.toml")
    p.add_argument("--filled", action="store_true", help="plus aucun Marqueur n'est admis")
    p = sub.add_parser("range", help="range une dette précédente, sans la recopier")
    p.add_argument("fichier", metavar="FICHIER", help="le rapport, <NN>-<sha>.toml")
    p.add_argument("id", metavar="R<n>")
    p.add_argument("vers", choices=["actuelle", "corrigee", "ecartee"])
    p.add_argument("--preuve", help="vers corrigee : la commande et sa sortie, ou le chemin:lignes")
    p = sub.add_parser("dette", help="ajoute une dette neuve au Marqueur, et affiche son R<n>")
    p.add_argument("fichier", metavar="FICHIER", help="le rapport, <NN>-<sha>.toml")
    p.add_argument("--nature", required=True, choices=NATURES)
    p.add_argument("--severite", required=True, choices=SEVERITES)
    p = sub.add_parser("export", help="écrit le rapport en Markdown, et affiche son chemin complet")
    p.add_argument("rapport", metavar="RAPPORT", help="le rapport, <NN>-<sha>.toml")
    p.add_argument(
        "scratchpad", metavar="SCRATCHPAD", help="le répertoire où écrire <slug>-<NN>-<sha>.md"
    )
    return parser


def main(argv: list[str]) -> int:
    args = _parser().parse_args(argv)
    match cast("str", args.commande):
        case "new":
            return _new(cast("str", args.slug), cast("Type", args.type))
        case "range":
            return _range(
                Path(cast("str", args.fichier)),
                cast("str", args.id),
                cast("Tableau", args.vers),
                cast("str | None", args.preuve),
            )
        case "export":
            return _export(Path(cast("str", args.rapport)), Path(cast("str", args.scratchpad)))
        case "dette":
            return _dette(
                Path(cast("str", args.fichier)),
                cast("Nature", args.nature),
                cast("Severite", args.severite),
            )
        case _:
            return _check(Path(cast("str", args.fichier)), cast("bool", args.filled))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
