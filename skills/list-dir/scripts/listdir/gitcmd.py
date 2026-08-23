"""Le seul appel à git du paquet.

UNE SEULE DÉFINITION. store.py en a besoin pour `git mv`, utils.py pour l'exposer
aux commandes : deux implémentations de « lancer git et traduire son code retour »
finiraient par différer sur le traitement de stderr, c'est-à-dire sur ce qu'un
échec dit.

git ABSENT N'EST PAS UN SUCCÈS : l'OSError est traduit en Result d'échec nommant
la cause, jamais avalé.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .types import Result, fail, ok


def git(*argv: str, cwd: Path | None = None) -> Result[str]:
    """git <argv> dans cwd. Rend sa sortie standard, ou son erreur."""
    try:
        proc = subprocess.run(
            ["git", *argv],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
    except OSError as exc:
        return fail(f"git introuvable — {exc}")
    if proc.returncode != 0:
        return Result(proc.returncode, None, (proc.stderr or proc.stdout).strip())
    return ok(proc.stdout)
