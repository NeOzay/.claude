"""Contrôle 1 — renvois vers le contrat.

Trois des cinq angles morts de `garde-fou-cinq-angles-morts` sont ici : la portée
limitée à `skills/`, la slugification trop étroite, et l'auto-citation du contrat
qui satisfaisait à elle seule « section jamais citée ».
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from check_pipeline import check_renvois, slugify
from conftest import CONTRAT_MINIMAL, CONTRAT_REL, ecrire


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_renvois(root) if not f.ok]


def test_arbre_sain(depot: Path) -> None:
    findings = check_renvois(depot)
    assert [f.ok for f in findings] == [True]
    assert "2 renvois" in findings[0].message


def test_ancre_morte(depot: Path) -> None:
    _ = ecrire(depot, "skills/x/SKILL.md", "[X](../implementation-tracker/references/contrat.md#nexiste-pas)\n")
    assert any("ancre morte : #nexiste-pas" in m for m in rouges(depot))


def test_chemin_mort(depot: Path) -> None:
    _ = ecrire(depot, "skills/x/SKILL.md", "[X](contrat.md#dates-et-listing)\n")
    assert any("chemin mort" in m for m in rouges(depot))


def test_contrat_absent(tmp_path: Path) -> None:
    assert any("contrat introuvable" in m for m in rouges(tmp_path))


def test_contrat_sans_section(depot: Path) -> None:
    _ = ecrire(depot, CONTRAT_REL, "# Contrat\n\nRien.\n")
    assert any("aucune section" in m for m in rouges(depot))


def test_aucun_renvoi(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, CONTRAT_REL, "# C\n\n## Une section\n")
    assert any("aucun renvoi trouvé" in m for m in rouges(tmp_path))


def test_section_jamais_citee(depot: Path) -> None:
    _ = ecrire(depot, CONTRAT_REL, "# C\n\n## Arborescence et nommage\n\n## Dates et listing\n\n## Orpheline\n")
    assert any("section jamais citée : #orpheline" in m for m in rouges(depot))


def test_auto_citation_ne_compte_pas(depot: Path) -> None:
    """Le contrat qui se cite lui-même ne prouve rien : la section reste non citée."""
    _ = ecrire(
        depot,
        CONTRAT_REL,
        "# C\n\n## Arborescence et nommage\n\n## Dates et listing\n\n## Orpheline\n\n"
        "Exemple : [Orpheline](contrat.md#orpheline)\n",
    )
    assert any("section jamais citée : #orpheline" in m for m in rouges(depot))


def test_portee_hors_skills(depot: Path) -> None:
    """La preuve de la portée étendue : ces deux emplacements échappaient au contrôle."""
    contrat = "skills/implementation-tracker/references/contrat.md"
    # Le chemin est relatif au fichier qui le porte : depuis hooks/, il remonte d'un cran.
    for rel, cible in (("CLAUDE.md", contrat), ("hooks/garde.md", f"../{contrat}")):
        _ = ecrire(depot, rel, f"[X]({cible}#nexiste-pas)\n")
    messages = rouges(depot)
    assert sum("ancre morte" in m for m in messages) == 2


def test_zones_exclues(depot: Path) -> None:
    """Archives, registre et agents ne sont jamais scannés."""
    cible = "skills/implementation-tracker/references/contrat.md"
    for rel in (".claude/implementation/done/vieux.md", "agents/auditeur.md"):
        _ = ecrire(depot, rel, f"[X](../../../{cible}#nexiste-pas)\n")
    assert rouges(depot) == []


def test_slugify_ponctuation() -> None:
    """L'ancienne version ne retirait que les apostrophes."""
    assert slugify("Format d'étape et délégabilité") == "format-détape-et-délégabilité"
    assert slugify("Branche, commits (et staging)") == "branche-commits-et-staging"
    assert slugify("Autorité et divergence") == "autorité-et-divergence"


def test_fichier_ignore_par_git_est_saute(tmp_path: Path) -> None:
    """R2 de l'audit de clôture : un artefact déposé dans un répertoire ignoré ne peut
    pas être corrigé par son auteur — le garde-fou n'a rien à en dire."""
    _ = subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _ = ecrire(tmp_path, ".gitignore", "cache/\n")
    _ = ecrire(tmp_path, CONTRAT_REL, CONTRAT_MINIMAL)
    _ = ecrire(
        tmp_path,
        "skills/implementation-tracker/SKILL.md",
        "[A](references/contrat.md#arborescence-et-nommage)\n"
        "[D](references/contrat.md#dates-et-listing)\n",
    )
    cible = "skills/implementation-tracker/references/contrat.md"
    _ = ecrire(tmp_path, "cache/changelog.md", f"[X]({cible}#nexiste-pas)\n")
    assert rouges(tmp_path) == []

    # Le même lien, hors répertoire ignoré, crie bien.
    _ = ecrire(tmp_path, "notes.md", f"[X]({cible}#nexiste-pas)\n")
    assert any("ancre morte" in m for m in rouges(tmp_path))


def test_plans_exclus(tmp_path: Path) -> None:
    """R3 : un plan archivé est un document daté, comme une archive de done/."""
    _ = ecrire(tmp_path, CONTRAT_REL, CONTRAT_MINIMAL)
    _ = ecrire(
        tmp_path,
        "skills/implementation-tracker/SKILL.md",
        "[A](references/contrat.md#arborescence-et-nommage)\n"
        "[D](references/contrat.md#dates-et-listing)\n",
    )
    cible = "skills/implementation-tracker/references/contrat.md"
    _ = ecrire(tmp_path, ".claude/plans/vieux-plan.md", f"[X](../../{cible}#nexiste-pas)\n")
    assert rouges(tmp_path) == []
