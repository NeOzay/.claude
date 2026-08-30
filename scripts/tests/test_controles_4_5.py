"""Contrôles 4 (indépendance des sous-agents) et 5 (chemins des archives)."""

from __future__ import annotations

from pathlib import Path

from check_pipeline import LISTER, check_agents, check_archives
from depot_jouet import ecrire
from test_controle_3 import LISTER_FIDELE


def rouges_agents(root: Path) -> list[str]:
    return [f.message for f in check_agents(root) if not f.ok]


def rouges_archives(root: Path) -> list[str]:
    return [f.message for f in check_archives(root) if not f.ok]


def test_agents_independants(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "agents/auditeur.md", "Tu lis le suivi et le brief.\n")
    findings = check_agents(tmp_path)
    assert [f.ok for f in findings] == [True]


def test_agent_couple_au_contrat(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "agents/auditeur.md", "Voir references/contrat.md pour la règle.\n")
    assert any("auto-suffisant" in m for m in rouges_agents(tmp_path))


def test_repertoire_agents_absent(tmp_path: Path) -> None:
    assert any("contrôle sans objet" in m for m in rouges_agents(tmp_path))


def test_aucun_agent(tmp_path: Path) -> None:
    (tmp_path / "agents").mkdir()
    assert any("aucun agent examiné" in m for m in rouges_agents(tmp_path))


def archive(root: Path, nom: str, frontmatter: str) -> None:
    _ = ecrire(root, LISTER, LISTER_FIDELE)
    _ = ecrire(root, f".claude/implementation/done/{nom}", f"---\n{frontmatter}---\n\ncorps\n")


def test_champs_resolvent(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, ".claude/plans/p.md", "plan\n")
    archive(tmp_path, "chantier.md", "plan: .claude/plans/p.md\n")
    findings = check_archives(tmp_path)
    assert [f.ok for f in findings] == [True]


def test_champ_pointe_dans_le_vide(tmp_path: Path) -> None:
    archive(tmp_path, "chantier.md", "plan: .claude/plans/disparu.md\n")
    assert any("pointe dans le vide" in m for m in rouges_archives(tmp_path))


def test_frontmatter_sans_champ(tmp_path: Path) -> None:
    """Un champ absent n'est pas une anomalie : tous les chantiers n'ont pas d'audit."""
    archive(tmp_path, "chantier.md", "slug: x\n")
    assert rouges_archives(tmp_path) == []


def test_aucune_archive(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, LISTER, LISTER_FIDELE)
    (tmp_path / ".claude/implementation/done").mkdir(parents=True)
    assert any("contrôle sans objet" in m for m in rouges_archives(tmp_path))
