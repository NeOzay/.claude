"""Contrôle 3 — filtre de listing des suivis.

Le contrôle charge le LISTER du dépôt audité et appelle sa fonction `suivis()` : un
faux LISTER suffit donc à éprouver les trois issues, sans dépendre du vrai.
"""

from __future__ import annotations

from pathlib import Path

from check_pipeline import LISTER, check_listing
from depot_jouet import ecrire

LISTER_FIDELE = '''
from pathlib import Path

ANNEXES = (".brief.md", ".audit.md", ".plan.md")


def suivis(dir: Path) -> list[str]:
    if not dir.is_dir():
        return []
    return sorted(
        p.name for p in dir.iterdir()
        if p.is_file() and p.name.endswith(".md") and not p.name.endswith(ANNEXES)
    )
'''

LISTER_SANS_FILTRE = '''
from pathlib import Path


def suivis(dir: Path) -> list[str]:
    return sorted(p.name for p in dir.iterdir()) if dir.is_dir() else []
'''


def peupler(root: Path) -> None:
    for nom in ("chantier.md", "chantier.brief.md", "chantier.plan.md", "chantier.audit.md"):
        _ = ecrire(root, f".claude/implementation/done/{nom}", "x\n")


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_listing(root) if not f.ok]


def test_filtre_fidele(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, LISTER, LISTER_FIDELE)
    peupler(tmp_path)
    findings = check_listing(tmp_path)
    assert [f.ok for f in findings] == [True]
    assert "1 fichiers listés" in findings[0].message


def test_filtre_cassé(tmp_path: Path) -> None:
    """Le mode de défaillance réel : les trois copies du filtre avaient cassé ensemble."""
    _ = ecrire(tmp_path, LISTER, LISTER_SANS_FILTRE)
    peupler(tmp_path)
    assert any("parasites" in m for m in rouges(tmp_path))


def test_lister_absent(tmp_path: Path) -> None:
    peupler(tmp_path)
    assert any("script de listing absent" in m for m in rouges(tmp_path))


def test_listing_vide(tmp_path: Path) -> None:
    """Un contrôle qui n'examine rien échoue — il ne rend jamais un vert par défaut."""
    _ = ecrire(tmp_path, LISTER, LISTER_FIDELE)
    (tmp_path / ".claude/implementation/done").mkdir(parents=True)
    assert any("contrôle sans objet" in m for m in rouges(tmp_path))


def test_lister_sans_fonction_suivis(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, LISTER, "x = 1\n")
    peupler(tmp_path)
    assert any("sans suivis()" in m for m in rouges(tmp_path))
