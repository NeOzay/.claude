"""Contrôle 2 — règles définies à un seul endroit.

Deux dettes ici : le comptage par fichiers (`garde-fou-cinq-angles-morts`, 3ᵉ point)
et la table d'empreintes non rattachée aux sections (`table-empreintes-a-la-main`).
"""

from __future__ import annotations

from pathlib import Path

import check_pipeline
import pytest
from check_pipeline import check_empreintes, sections
from depot_jouet import CONTRAT_REL, ecrire

CONTRAT = """# Contrat

## Une regle

Le corps porte la formulation distinctive.

## Une autre

Le second corps, avec sa propre formule.
"""

TABLE = {
    "une-regle": ("formulation distinctive",),
    "une-autre": ("propre formule",),
}


@pytest.fixture(autouse=True)
def table(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_pipeline, "EMPREINTES", TABLE)


@pytest.fixture
def contrat(tmp_path: Path) -> Path:
    _ = ecrire(tmp_path, CONTRAT_REL, CONTRAT)
    return tmp_path


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_empreintes(root) if not f.ok]


def test_arbre_sain(contrat: Path) -> None:
    assert rouges(contrat) == []


def test_motif_disparu(contrat: Path) -> None:
    _ = ecrire(contrat, CONTRAT_REL, "# C\n\n## Une regle\n\nVidé.\n\n## Une autre\n\npropre formule\n")
    assert any("introuvable" in m for m in rouges(contrat))


def test_deux_occurrences_dans_un_seul_fichier(contrat: Path) -> None:
    """Le comptage par fichiers laissait passer exactement ce cas."""
    _ = ecrire(
        contrat,
        CONTRAT_REL,
        CONTRAT + "\nRappel : la formulation distinctive, encore.\n",
    )
    assert any("2 occurrences" in m for m in rouges(contrat))


def test_recopie_dans_un_autre_fichier(contrat: Path) -> None:
    _ = ecrire(contrat, "skills/x/SKILL.md", "la formulation distinctive recopiée\n")
    assert any("2 occurrences" in m for m in rouges(contrat))


def test_motif_hors_de_sa_section(contrat: Path) -> None:
    """Une empreinte qui migre dans une autre section ne protège plus la sienne."""
    _ = ecrire(
        contrat,
        CONTRAT_REL,
        "# C\n\n## Une regle\n\nVidé.\n\n## Une autre\n\npropre formule et formulation distinctive\n",
    )
    assert any("hors de la section" in m for m in rouges(contrat))


def test_section_sans_empreinte(contrat: Path) -> None:
    """Le cas que la table plate ne savait pas voir."""
    _ = ecrire(contrat, CONTRAT_REL, CONTRAT + "\n## Neuve\n\nUne règle que rien ne protège.\n")
    assert any("section sans empreinte : #neuve" in m for m in rouges(contrat))


def test_empreinte_orpheline(contrat: Path) -> None:
    _ = ecrire(contrat, CONTRAT_REL, "# C\n\n## Une regle\n\nformulation distinctive\n")
    assert any("empreinte orpheline : #une-autre" in m for m in rouges(contrat))


def test_contrat_absent(tmp_path: Path) -> None:
    assert any("contrat introuvable" in m for m in rouges(tmp_path))


def test_titre_dans_un_bloc_de_code_nest_pas_une_section() -> None:
    texte = "## Vraie\n\n```bash\n## Fausse\n```\n\ncorps\n"
    assert list(sections(texte)) == ["vraie"]
    assert "## Fausse" in sections(texte)["vraie"]
