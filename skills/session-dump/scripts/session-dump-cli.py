#!/usr/bin/env python3
"""Point d'entrée en ligne de commande de `session-dump`.

AUCUNE LOGIQUE MÉTIER ICI. Ce fichier parse des arguments, appelle `session_dump.py` et traduit
le résultat en code de sortie.

LE NOM PORTE UN TIRET, comme `gabarit-cli.py` : il n'est pas importable, et ne dispute pas son
nom au module `session_dump` rangé à côté. La commande s'appelle `session-dump` par son lien de
`bin/`.

ÉCHEC FERMÉ : sortie 2 sur une erreur d'appel (chemin qui n'est pas un répertoire), 1 sur un
échec nommé sur stderr (aucune session pour ce projet, écriture impossible). Seule la
bibliothèque standard est utilisée : pas de venv à rejoindre.
"""

import sys

# `noqa: UP036` : ruff juge ce bloc mort parce que target-version vaut py312. Il n'existe que
# pour le Python plus ancien qui exécuterait ce fichier.
if sys.version_info < (3, 12):  # noqa: UP036
    v = ".".join(str(n) for n in sys.version_info[:3])  # pyright: ignore[reportUnreachable]
    sys.stderr.write(f"session-dump exige Python >= 3.12, trouvé {v} ({sys.executable}).\n")
    raise SystemExit(2)

import argparse
import os
from pathlib import Path
from typing import cast

from session_dump import TOKENS_MIN, TOURS_MIN, Bilan, Motif, dumper

# Le libellé de chaque motif d'écart, dans l'ordre où la commande les rapporte.
LIBELLES: dict[Motif, str] = {
    "sans-tour": "sans tour",
    "claude-p": "lancée(s) par claude -p",
    "trop-courte": f"moins de {TOURS_MIN} tours et de {TOKENS_MIN:_} tokens".replace("_", " "),
}


def main(argv: list[str]) -> int:
    analyseur = argparse.ArgumentParser(
        prog="session-dump",
        description=(
            "Écrit un dump par discussion du projet dans "
            "<projet>/.claude/session-dump/<id>/, statistiques en frontmatter TOML."
        ),
    )
    analyseur.add_argument(
        "chemin", nargs="?", default=".", help="répertoire du projet (défaut : le courant)"
    )
    arguments = analyseur.parse_args(argv)
    resultat = dumper(Path(cast("str", arguments.chemin)), os.environ)
    if not isinstance(resultat, Bilan):
        sys.stderr.write(resultat.message + "\n")
        return resultat.code
    print(f"session-dump : {resultat.ecrits} dumps écrits dans {resultat.destination}")
    for motif, libelle in LIBELLES.items():
        if resultat.ecartes.get(motif):
            print(f"session-dump : {resultat.ecartes[motif]} session(s) écartée(s) — {libelle}")
    if resultat.illisibles:
        sys.stderr.write(f"session-dump : {resultat.illisibles} ligne(s) illisible(s) ignorée(s)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
