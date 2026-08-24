"""Contrôle 6 — portabilité des appels de script.

Le cinquième angle mort est ici : le garde était cherché n'importe où dans la ligne,
et le chemin injecté tel quel dans un motif où ses `.` étaient des métacaractères.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from check_pipeline import check_portabilite
from conftest import ecrire

FAUTIFS = [
    "bash scripts/x.sh",
    "bash ./scripts/x.sh",
    'bash "scripts/x.sh"',
    "python3 scripts/x.py",
]

ABSOLUS = [
    "bash /opt/x.sh",
    "bash ~/x.sh",
    "bash $HOME/.claude/x.sh",
    "bash ${HOME}/.claude/x.sh",
    'python3 "$HOME/.claude/x.py"',
]


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_portabilite(root) if not f.ok]


@pytest.mark.parametrize("ligne", FAUTIFS)
def test_formes_fautives(tmp_path: Path, ligne: str) -> None:
    _ = ecrire(tmp_path, "skills/x/SKILL.md", f"```bash\n{ligne}\n```\n")
    assert any("appel relatif non gardé" in m for m in rouges(tmp_path))


@pytest.mark.parametrize("ligne", ABSOLUS)
def test_ecritures_absolues(tmp_path: Path, ligne: str) -> None:
    _ = ecrire(tmp_path, "skills/x/SKILL.md", f"```bash\n{ligne}\n```\n")
    assert rouges(tmp_path) == []


def test_garde_qui_commande_lappel(tmp_path: Path) -> None:
    """La forme légitime : cloture.md saute proprement le garde-fou hors de son dépôt."""
    ligne = "if [ -f scripts/x.sh ]; then bash scripts/x.sh; fi"
    _ = ecrire(tmp_path, "skills/x/SKILL.md", f"```bash\n{ligne}\n```\n")
    assert rouges(tmp_path) == []


def test_garde_en_commentaire_apres_lappel(tmp_path: Path) -> None:
    """Le faux vert : le garde ne commandait rien, il suivait l'appel."""
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "```bash\nbash scripts/x.sh  # [ -f scripts/x.sh ]\n```\n")
    assert any("appel relatif non gardé" in m for m in rouges(tmp_path))


def test_garde_sur_un_autre_fichier(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "```bash\nif [ -f autre.sh ]; then bash scripts/x.sh; fi\n```\n")
    assert any("appel relatif non gardé" in m for m in rouges(tmp_path))


def test_point_nest_pas_un_metacaractere(tmp_path: Path) -> None:
    """`re.escape` : sans lui, un garde sur `x-sh` validait un appel de `x.sh`."""
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "```bash\nif [ -f scriptsXx.sh ]; then bash scripts/x.sh; fi\n```\n")
    assert any("appel relatif non gardé" in m for m in rouges(tmp_path))


def test_variable_non_concernee(tmp_path: Path) -> None:
    """`python3 "$L"` ne porte aucun chemin en clair : c'est sa définition qui compte."""
    _ = ecrire(tmp_path, "skills/x/SKILL.md", '```bash\npython3 "$L" validate .\npython3 -c "print(1)"\n```\n')
    assert rouges(tmp_path) == []


def test_skills_vide(tmp_path: Path) -> None:
    assert any("contrôle sans objet" in m for m in rouges(tmp_path))
