#!/usr/bin/env python3
"""Point d'entrée en ligne de commande des gabarits.

AUCUNE LOGIQUE MÉTIER ICI. Ce fichier parse des arguments, appelle la bibliothèque
et traduit un Result en code de sortie. Toute la logique vit dans gabarit/.

LE NOM PORTE UN TIRET, comme `list-dir.py` : il n'est pas importable. C'est ce qui
évite que ce fichier et le paquet `gabarit/`, rangés côte à côte dans `scripts/`, se
disputent le même nom de module. La commande s'appelle `gabarit` par son lien de
`bin/`.

ÉCHEC FERMÉ : sortie 2 sur une erreur d'appel, sortie non nulle et message sur
stderr sur toute autre erreur. Jamais de succès silencieux.

LES DEUX GARDES SONT CELLES DE `list-dir.py`, et pour les mêmes raisons : la version
de Python avant tout import du paquet (syntaxe PEP 695), puis la ré-exécution dans le
venv du dépôt, seul à porter tomlkit.
"""

import sys

# `noqa: UP036` : ruff juge ce bloc mort parce que target-version vaut py312. Il
# n'existe que pour le Python plus ancien qui exécuterait ce fichier.
if sys.version_info < (3, 12):  # noqa: UP036
    v = ".".join(str(n) for n in sys.version_info[:3])  # pyright: ignore[reportUnreachable]
    sys.stderr.write(f"gabarit exige Python >= 3.12, trouvé {v} ({sys.executable}).\n")
    raise SystemExit(2)

import os
from pathlib import Path

# Voir `list-dir.py` pour le raisonnement complet : `sys.prefix` et non
# `sys.executable`, un seul `if` pour ne pas déclencher E402, et un venv absent qui
# ne bloque rien — c'est sante_skills qui le signale.
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

from gabarit.commandes import check, contract, defs, new, trouver_semence
from gabarit.types import Result

# Le nom sous lequel on a été appelé. Après la ré-exécution dans le venv, c'est le
# chemin résolu du fichier, donc « gabarit-cli.py » — la même limite que `list-dir.py`.
USAGE = f"{Path(sys.argv[0]).name} <commande> [arguments]"


def _options_new(p_new: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Les arguments de `new` : `[<nom>] <fichier>` en un seul positionnel, et `--from`.

    UN SEUL POSITIONNEL, LU EN MODE ENTREMÊLÉ (`parse_intermixed_args`, dans `main`).
    argparse apparie sinon les positionnels par paquets entre les options :
    `new suivi --from P x.md` devenait « unrecognized arguments », et le vrai refus — un
    nom et --from ensemble — n'était jamais atteint. Le mode entremêlé ne supporte pas
    les sous-commandes, d'où ce parseur à part pour `new`.
    """
    p_new.add_argument(
        "cibles", nargs="+", metavar="[nom] fichier", help="la semence par son nom, et le fichier"
    )
    p_new.add_argument(
        "--from", dest="depuis", metavar="CHEMIN", help="le répertoire d'une semence, tel quel"
    )
    return p_new


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gabarit", description="fichiers préstructurés")
    sub = parser.add_subparsers(dest="commande", required=True, metavar="<commande>")

    _options_new(sub.add_parser("new", help="crée un fichier prérempli d'une semence, estampillé"))

    p_check = sub.add_parser("check", help="vérifie un fichier contre sa semence")
    p_check.add_argument("fichier", help="le fichier à vérifier")
    p_check.add_argument(
        "--filled",
        action="store_true",
        help="exige en plus qu'aucun marqueur ne subsiste sur un champ ou une section requis",
    )
    imposee = p_check.add_mutually_exclusive_group()
    imposee.add_argument("--def", dest="nom", metavar="NOM", help="la semence, par son nom")
    imposee.add_argument(
        "--from", dest="depuis", metavar="CHEMIN", help="le répertoire d'une semence, tel quel"
    )

    p_contract = sub.add_parser("contract", help="affiche le contrat d'une semence, tel quel")
    p_contract.add_argument("nom", nargs="?", help="la semence, résolue par son nom")
    p_contract.add_argument(
        "--from", dest="depuis", metavar="CHEMIN", help="le répertoire d'une semence, tel quel"
    )
    p_contract.add_argument(
        "--values", default="", metavar="CHAMP", help="les valeurs déclarées de ce champ"
    )

    sub.add_parser("defs", help="les semences disponibles, avec leur rang et leur origine")
    return parser


def _sortie(r: Result[object]) -> int:
    """Échec : message sur stderr, code non nul. Succès : la valeur seule sur stdout, et
    l'éventuel avertissement sur stderr — jamais sur stdout, qu'un appelant lit."""
    if not r:
        sys.stderr.write(f"{r.message}\n")
        return r.status or 1
    if r.value is not None:
        print(r.value)
    if r.message:
        sys.stderr.write(f"{r.message}\n")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write(f"usage: {USAGE}\n\nAucune commande.\n")
        return 2
    if argv[0] == "new":
        parser_new = argparse.ArgumentParser(
            prog="gabarit new", usage="gabarit new <nom> <fichier> | --from <chemin> <fichier>"
        )
        args = _options_new(parser_new).parse_intermixed_args(argv[1:])
        args.commande = "new"
    else:
        args = _parser().parse_args(argv)

    match cast("str", args.commande):
        case "new":
            cibles = cast("list[str]", args.cibles)
            if len(cibles) > 2:
                sys.stderr.write(f"gabarit new [<nom>] <fichier> — trop d'arguments : {cibles}\n")
                return 2
            nom, fichier = (None, cibles[0]) if len(cibles) == 1 else (cibles[0], cibles[1])
            depuis = cast("str | None", args.depuis)
            semence = trouver_semence(nom, Path(depuis) if depuis is not None else None)
            if not semence:
                return _sortie(semence)
            return _sortie(new(Path(fichier), semence.unwrap()))
        case "check":
            nom = cast("str | None", args.nom)
            depuis = cast("str | None", args.depuis)
            imposee = None
            if nom is not None or depuis is not None:
                trouvee = trouver_semence(nom, Path(depuis) if depuis is not None else None)
                if not trouvee:
                    return _sortie(trouvee)
                imposee = trouvee.unwrap()
            fichier = Path(cast("str", args.fichier))
            return _sortie(check(fichier, cast("bool", args.filled), imposee))
        case "contract":
            depuis = cast("str | None", args.depuis)
            semence = trouver_semence(
                cast("str | None", args.nom), Path(depuis) if depuis is not None else None
            )
            if not semence:
                return _sortie(semence)
            return _sortie(contract(semence.unwrap(), cast("str", args.values)))
        case "defs":
            return _sortie(defs())
        case autre:
            sys.stderr.write(f"usage: {USAGE}\n\ncommande « {autre} » inconnue\n")
            return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
