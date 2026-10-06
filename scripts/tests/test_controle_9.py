"""Contrôle 9 — `pyright` n'est cité que pour être écarté, scripts des skills compris.

Le rappel d'outillage quitte `hooks/` pour `.claude/skills/outillage/scripts/` : le
contrôle doit l'y suivre, sans quoi une consigne `pyright` versée à chaque sous-agent
passerait au vert.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from check_pipeline import check_pyright
from depot_jouet import ecrire

EMPLACEMENTS = [
    ".claude/skills/x/scripts/rappel.sh",
    "skills/x/scripts/rappel.sh",
    "hooks/rappel.sh",
]


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_pyright(root) if not f.ok]


@pytest.mark.parametrize("rel", EMPLACEMENTS)
def test_script_qui_cite_pyright_sans_l_ecarter(tmp_path: Path, rel: str) -> None:
    _ = ecrire(tmp_path, rel, "#!/bin/sh\necho 'typage : pyright .'\n")
    assert any(rel in m for m in rouges(tmp_path))


@pytest.mark.parametrize("rel", EMPLACEMENTS)
def test_script_qui_ecarte_pyright(tmp_path: Path, rel: str) -> None:
    _ = ecrire(tmp_path, rel, "#!/bin/sh\necho 'typage : basedpyright, jamais pyright.'\n")
    assert rouges(tmp_path) == []


def test_script_hors_des_scripts_d_un_skill_ignore(tmp_path: Path) -> None:
    """Le contrôle ne lit pas tout `.sh` du dépôt : seulement les emplacements nommés."""
    _ = ecrire(tmp_path, ".claude/skills/x/autre/rappel.sh", "echo 'pyright .'\n")
    assert rouges(tmp_path) == []
