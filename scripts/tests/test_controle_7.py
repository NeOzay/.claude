"""Contrôle 7 — existence des chemins de skill cités.

Nouveau contrôle. Il solde le SYMPTÔME de `chemin-skill-code-en-dur` : un point
d'édition oublié devient rouge. La cause — le chemin écrit en dur, forme que le
contrôle 6 impose — reste ouverte au registre.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from check_pipeline import check_chemins_skill
from depot_jouet import ecrire


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_chemins_skill(root) if not f.ok]


@pytest.mark.parametrize("ecriture", ["$HOME", "${HOME}", "~"])
def test_ancrage_sur_le_home_refuse(tmp_path: Path, ecriture: str) -> None:
    """Le solde de `chemin-skill-code-en-dur` : la supposition ne se recopie plus.

    Le fichier visé EXISTE : ce n'est pas son absence qu'on reproche, c'est la forme.
    """
    _ = ecrire(tmp_path, "skills/x/scripts/outil.py", "x = 1\n")
    _ = ecrire(tmp_path, "skills/x/SKILL.md", f'```bash\n"{ecriture}/.claude/skills/x/scripts/outil.py" list\n```\n')
    assert any("ancré sur le HOME" in m for m in rouges(tmp_path))


def test_repertoire_accepte(tmp_path: Path) -> None:
    """Toutes les citations ne visent pas un fichier : `grep -ril … skills/list-dir/`."""
    _ = ecrire(tmp_path, "skills/x/scripts/outil.py", "x = 1\n")
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "```bash\ngrep -ril x skills/x/\n```\n")
    assert rouges(tmp_path) == []


def test_gabarit_ignore(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "Voir `skills/<nom>/SKILL.md`.\n")
    assert any("aucun chemin de skill cité" in m for m in rouges(tmp_path))


def test_aucun_chemin_cite(tmp_path: Path) -> None:
    """Un contrôle qui n'examine rien échoue."""
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "Aucun chemin ici.\n")
    assert any("contrôle sans objet" in m for m in rouges(tmp_path))


# --- Chemin relatif au dépôt, et forme d'appel -------------------------------


def test_chemin_relatif_existant(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/x/scripts/outil.py", "x = 1\n")
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "Le module `skills/x/scripts/outil.py` porte tout.\n")
    assert rouges(tmp_path) == []


def test_chemin_relatif_inexistant(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "Voir `skills/x/scripts/disparu.py`.\n")
    assert any("chemin de skill inexistant" in m for m in rouges(tmp_path))


def test_chemin_alors_qu_une_commande_existe(tmp_path: Path) -> None:
    """Le cœur de la dette : un chemin de plus est un point d'édition de plus."""
    _ = ecrire(tmp_path, "skills/x/scripts/outil.py", "x = 1\n")
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "outil").symlink_to("../skills/x/scripts/outil.py")
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "```bash\nskills/x/scripts/outil.py list\n```\n")
    maux = rouges(tmp_path)
    assert any("s'appelle par son nom" in m for m in maux)
    assert any("« outil »" in m for m in maux), "le constat doit nommer la commande à employer"


def test_sans_bin_le_chemin_reste_licite(tmp_path: Path) -> None:
    """Tout exécutable n'est pas exposé : sans lien, le chemin est la seule façon."""
    _ = ecrire(tmp_path, "skills/x/scripts/outil.py", "x = 1\n")
    _ = ecrire(tmp_path, "skills/x/SKILL.md", "```bash\nskills/x/scripts/outil.py list\n```\n")
    assert rouges(tmp_path) == []
