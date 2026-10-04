#!/usr/bin/env python3
"""Point d'entrée en ligne de commande des shadow-skills.

AUCUNE LOGIQUE MÉTIER ICI. Ce fichier parse des arguments, appelle `shadow_skill.py` et
traduit le résultat en code de sortie.

LE NOM PORTE UN TIRET, comme `gabarit-cli.py` : il n'est pas importable, et ne dispute pas son
nom au module `shadow_skill` rangé à côté. La commande s'appelle `shadow-skill` par son lien de
`bin/`.

ÉCHEC FERMÉ : sortie 2 sur une erreur d'appel, 1 sur un échec nommé sur stderr. `verifie`
sort 1 sur le moindre constat, et sur un ensemble vide : un contrôle qui n'examine rien
échoue. `liste`, `cherche` et `chemin` alimentent la future intégration Neovim : leur sortie,
une ligne tabulée par skill, est une interface.

LES DEUX GARDES SONT CELLES DE `gabarit-cli.py`, et pour les mêmes raisons : la version de
Python avant tout import (syntaxe PEP 695 du paquet gabarit), puis la ré-exécution dans le venv
du dépôt, seul à porter tomlkit, que le paquet gabarit importe.
"""

import sys

# `noqa: UP036` : ruff juge ce bloc mort parce que target-version vaut py312. Il n'existe que
# pour le Python plus ancien qui exécuterait ce fichier.
if sys.version_info < (3, 12):  # noqa: UP036
    v = ".".join(str(n) for n in sys.version_info[:3])  # pyright: ignore[reportUnreachable]
    sys.stderr.write(f"shadow-skill exige Python >= 3.12, trouvé {v} ({sys.executable}).\n")
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
from typing import cast

from shadow_skill import (
    Lecture,
    Skill,
    charger,
    chemin_suivi,
    chercher,
    lister,
    niveaux,
    noms_du_suivi,
    racine_projet,
    registre,
    trouver,
    verifier,
)


def _ligne(s: Skill) -> str:
    """Une ligne de `liste` et de `cherche`.

    `when-to-load` Y FIGURE : c'est sur lui que l'agent décide de charger un skill, et il ne
    doit pas avoir à le charger pour le savoir.
    """
    return f"{s.niveau}\t{s.nom}\t{s.description}\t{s.when_to_load}"


def _lire(projet: Path) -> Lecture:
    """Les skills du projet ; leurs fautes vont sur stderr, sans toucher au code."""
    lu = lister(niveaux(projet))
    for f in lu.fautes:
        sys.stderr.write(f + "\n")
    return lu


def _liste(projet: Path) -> int:
    lu = _lire(projet)
    for s in lu.skills:
        print(_ligne(s))
    return 1 if lu.illisible else 0


def _cherche(projet: Path, mots: list[str]) -> int:
    trouves = chercher(_lire(projet).skills, mots)
    for s in trouves:
        print(_ligne(s))
    return 0 if trouves else 1


def _resoudre(projet: Path, nom: str) -> Skill | None:
    r = trouver(_lire(projet).skills, nom)
    if not r:
        sys.stderr.write(r.message + "\n")
        return None
    return r.unwrap()


def _charge(projet: Path, nom: str) -> int:
    s = _resoudre(projet, nom)
    if s is None:
        return 1
    r = charger(s)
    if not r:
        sys.stderr.write(r.message + "\n")
        return 1
    sys.stdout.write(r.unwrap())
    return 0


def _chemin(projet: Path, nom: str) -> int:
    s = _resoudre(projet, nom)
    if s is None:
        return 1
    print(s.chemin)
    return 0


def _depuis_suivi(projet: Path, slug: str) -> int:
    suivi = chemin_suivi(projet, slug)
    if not suivi:
        sys.stderr.write(suivi.message + "\n")
        return 1
    noms = noms_du_suivi(suivi.unwrap())
    if not noms:
        sys.stderr.write(noms.message + "\n")
        return 1
    skills = _lire(projet).skills
    code = 0
    for nom in noms.unwrap():
        r = trouver(skills, nom)
        if not r:
            sys.stderr.write(r.message + "\n")
            code = 1
            continue
        s = r.unwrap()
        print(f"{s.nom}\t{s.description}\t{s.when_to_load}")
    return code


def _tags(projet: Path) -> int:
    reg = registre(niveaux(projet))
    for t in reg.tags:
        print(f"{t.niveau}\t{t.nom}\t{t.description}")
    for f in reg.fautes:
        sys.stderr.write(f + "\n")
    return 1 if reg.fautes else 0


def _verifie(projet: Path) -> int:
    ou = niveaux(projet)
    constats = verifier(lister(ou), registre(ou))
    for c in constats:
        sys.stderr.write(c + "\n")
    return 1 if constats else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shadow-skill", description="Shadow-skills")
    sub = parser.add_subparsers(dest="commande", required=True)
    projet = argparse.ArgumentParser(add_help=False)
    projet.add_argument(
        "--projet", metavar="DIR", help="le projet du niveau local ; défaut : la racine git"
    )
    sub.add_parser(
        "liste", parents=[projet], help="niveau, nom, description, when-to-load de chaque skill"
    )
    p = sub.add_parser(
        "cherche", parents=[projet], help="les skills où figure chaque mot, sans casse ni accents"
    )
    p.add_argument("mots", nargs="+", metavar="MOT")
    p = sub.add_parser("charge", parents=[projet], help="le fichier principal d'un skill")
    p.add_argument("nom", metavar="NOM")
    p = sub.add_parser("chemin", parents=[projet], help="le chemin du fichier principal")
    p.add_argument("nom", metavar="NOM")
    p = sub.add_parser(
        "depuis-suivi",
        parents=[projet],
        help="nom, description, when-to-load des Shadow-skills du Suivi d'un Chantier",
    )
    p.add_argument("slug", metavar="SLUG")
    sub.add_parser("tags", parents=[projet], help="niveau, tag, description de chaque tag")
    sub.add_parser("verifie", parents=[projet], help="les constats sur les skills et leurs tags")
    return parser


def main(argv: list[str]) -> int:
    args = _parser().parse_args(argv)
    commande = cast("str", args.commande)
    brut = cast("str | None", args.projet)
    projet = Path(brut) if brut is not None else racine_projet(Path.cwd())
    match commande:
        case "liste":
            return _liste(projet)
        case "cherche":
            return _cherche(projet, cast("list[str]", args.mots))
        case "charge":
            return _charge(projet, cast("str", args.nom))
        case "chemin":
            return _chemin(projet, cast("str", args.nom))
        case "depuis-suivi":
            return _depuis_suivi(projet, cast("str", args.slug))
        case "tags":
            return _tags(projet)
        case _:
            return _verifie(projet)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
