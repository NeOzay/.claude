#!/usr/bin/env python3
"""Lit et écrit la taille du contexte d'une session Claude Code, en tokens.

PORTÉE : deux usages, et aucun autre.
  contexte ecrire <session> <tokens>   enregistre la mesure — appelé par la statusline
  contexte                             imprime la mesure de la session courante

La statusline est la seule à recevoir la taille du contexte ; l'agent, lui, ne la voit
pas. Ce script fait le pont : elle écrit, il lit. La session courante se désigne par
`$CLAUDE_CODE_SESSION_ID`, que Claude Code exporte aux commandes Bash de l'agent.

LE STOCKAGE N'EST DÉFINI QU'ICI : `${XDG_RUNTIME_DIR:-~/.cache}/claude-contexte/<session>`.
La statusline ne connaît que la commande ; déplacer le stockage ne touche qu'à ce fichier.

ÉCHEC FERMÉ : mesure absente ou illisible, ou écriture impossible → message sur stderr,
sortie 1 ; erreur d'appel → sortie 2. Jamais un nombre inventé : un agent qui lit 0
croirait avoir de la marge.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path

# Le nom de session devient un nom de fichier : TOUT CE QUI POURRAIT SORTIR DU
# RÉPERTOIRE (`/`, `..`) EST REFUSÉ. Claude Code donne un UUID, que ce motif couvre.
SESSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")

USAGE = "usage : contexte | contexte ecrire <session> <tokens>"


def repertoire(environ: Mapping[str, str]) -> Path:
    """Le répertoire des mesures, d'après l'environnement donné."""
    base = environ.get("XDG_RUNTIME_DIR") or str(
        Path(environ.get("HOME") or Path.home()) / ".cache"
    )
    return Path(base) / "claude-contexte"


def verifier_session(session: str) -> str | None:
    """Un message d'erreur si `session` ne peut pas servir de nom de fichier, sinon None."""
    if SESSION.fullmatch(session) is None:
        return f"contexte : session invalide : {session!r}"
    return None


def verifier_tokens(tokens: str) -> int | None:
    """Le nombre de tokens, ou None s'il n'est pas un entier positif ou nul."""
    if not tokens.isascii() or not tokens.isdigit():
        return None
    return int(tokens)


def ecrire(rep: Path, session: str, tokens: int) -> None:
    """Enregistre la mesure de `session`, en remplaçant la précédente.

    L'écriture passe par un fichier temporaire renommé : la statusline écrit pendant que
    l'agent lit, et un lecteur ne doit jamais voir un fichier à moitié écrit.
    """
    rep.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=rep, prefix=f".{session}.")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(f"{tokens}\n")
        os.replace(tmp, rep / session)
    except BaseException:
        # UN ÉCHEC NE LAISSE RIEN DERRIÈRE LUI : le fichier temporaire s'accumulerait à
        # chaque rafraîchissement de la statusline.
        Path(tmp).unlink(missing_ok=True)
        raise


def lire(rep: Path, session: str) -> int | None:
    """La mesure de `session`, ou None si elle est absente ou illisible."""
    try:
        contenu = (rep / session).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    return verifier_tokens(contenu)


def main(argv: list[str], environ: Mapping[str, str]) -> int:
    rep = repertoire(environ)
    match argv:
        case ["ecrire", session, brut]:
            if (erreur := verifier_session(session)) is not None:
                sys.stderr.write(erreur + "\n")
                return 2
            if (tokens := verifier_tokens(brut)) is None:
                sys.stderr.write(f"contexte : nombre de tokens invalide : {brut!r}\n")
                return 2
            try:
                ecrire(rep, session, tokens)
            except OSError as e:
                sys.stderr.write(f"contexte : écriture impossible dans {rep} : {e.strerror}\n")
                return 1
            return 0
        case []:
            session = environ.get("CLAUDE_CODE_SESSION_ID", "")
            if not session:
                sys.stderr.write("contexte : CLAUDE_CODE_SESSION_ID absent de l'environnement\n")
                return 1
            if (erreur := verifier_session(session)) is not None:
                sys.stderr.write(erreur + "\n")
                return 1
            if (tokens := lire(rep, session)) is None:
                sys.stderr.write(
                    f"contexte : aucune mesure pour la session {session} dans {rep}"
                    " — la statusline l'écrit-elle ?\n"
                )
                return 1
            print(tokens)
            return 0
        case _:
            sys.stderr.write(USAGE + "\n")
            return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], os.environ))
