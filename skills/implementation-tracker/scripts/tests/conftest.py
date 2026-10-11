"""Fixtures des tests des scripts d'implementation-tracker.

sys.path vise `scripts/`, ce qui rend `import fiche` et `import contexte` disponibles.
`chantier` est un dépôt jouet, sur la branche d'un Chantier qui porte Suivi et Brief ; son slug
vit dans `chantier_jouet`, que les tests importent à la place de ce fichier.
`rapport_audit` est importé ici, avant tout module de test : c'est lui qui rend `gabarit`
importable, et un test qui importe `gabarit` en premier le trouverait absent.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import rapport_audit  # noqa: F401  # pyright: ignore[reportUnusedImport]
from chantier_jouet import SLUG

SUIVI = f"""+++
gabarit = "suivi"
slug = "{SLUG}"
branche = "{SLUG}"
base = "master"
plan = ".claude/plans/jouet.md"
brief = ".claude/implementation/{SLUG}.brief.md"
+++

## Étapes

- [x] 1. Un fichier — `a.txt` — vérif: `test -f a.txt`
- [ ] 2. Un autre — `b.txt` — vérif: `test -f b.txt`

## Dettes écartées

- R8 — Le terme entre au Lexique global à l'Étape 9, sur accord de
  l'utilisateur. — 2026-10-04
"""

BRIEF = """+++
gabarit = "brief"
+++

## Intention

**Symptôme** : « la Passation est jugée périmée » après
chaque audit.

**But** : la reprendre.

## Critères de réussite

- **C1** — La reprise signale une Passation périmée.
- **C2** — `contexte --session courante` rend la taille
  du contexte (`pytest`).

## Hors-périmètre

- La ligne de statut (dit ; dépôt:
  `statusline-command.py`).

## Signaux de dérive

- **S1** — Un script lit le rapport en entier (dit).
"""


def _git(depot: Path, *argv: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv],
        cwd=depot,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def chantier(tmp_path: Path) -> Path:
    """Un dépôt jouet sur la branche du Chantier `contexte-tracker`, son Suivi et son Brief."""
    implementation = tmp_path / ".claude" / "implementation"
    implementation.mkdir(parents=True)
    (implementation / f"{SLUG}.md").write_text(SUIVI, encoding="utf-8")
    (implementation / f"{SLUG}.brief.md").write_text(BRIEF, encoding="utf-8")
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "base")
    _git(tmp_path, "checkout", "-q", "-b", SLUG)
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "jouet")
    return tmp_path
