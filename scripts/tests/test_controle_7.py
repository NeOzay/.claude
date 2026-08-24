"""Contrôle 7 — existence des chemins de skill cités.

Nouveau contrôle. Il solde le SYMPTÔME de `chemin-skill-code-en-dur` : un point
d'édition oublié devient rouge. La cause — le chemin écrit en dur, forme que le
contrôle 6 impose — reste ouverte au registre.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from check_pipeline import check_chemins_skill
from conftest import ecrire


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_chemins_skill(root) if not f.ok]


@pytest.mark.parametrize("ecriture", ["$HOME", "${HOME}", "~"])
def test_chemin_existant(tmp_path: Path, ecriture: str) -> None:
    _ = ecrire(tmp_path, "skills/x/scripts/outil.py", "x = 1\n")
    _ = ecrire(tmp_path, "skills/x/SKILL.md", f'```bash\npython3 "{ecriture}/.claude/skills/x/scripts/outil.py"\n```\n')
    assert rouges(tmp_path) == []


def test_chemin_inexistant(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/x/SKILL.md", '```bash\npython3 "$HOME/.claude/skills/x/scripts/disparu.py"\n```\n')
    assert any("chemin de skill inexistant" in m for m in rouges(tmp_path))


def test_repertoire_accepte(tmp_path: Path) -> None:
    """Toutes les citations ne visent pas un fichier : `grep -ril … skills/list-dir/`."""
    _ = ecrire(tmp_path, "skills/x/scripts/outil.py", "x = 1\n")
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "```bash\ngrep -ril x $HOME/.claude/skills/x/\n```\n")
    assert rouges(tmp_path) == []


def test_gabarit_ignore(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "Voir `$HOME/.claude/skills/<nom>/SKILL.md`.\n")
    assert any("aucun chemin de skill cité" in m for m in rouges(tmp_path))


def test_aucun_chemin_cite(tmp_path: Path) -> None:
    """Un contrôle qui n'examine rien échoue."""
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "Aucun chemin ici.\n")
    assert any("contrôle sans objet" in m for m in rouges(tmp_path))
