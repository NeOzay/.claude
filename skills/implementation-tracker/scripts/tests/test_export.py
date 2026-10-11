"""`audit export` : le rapport rendu en Markdown, sur les audits factices."""

import subprocess
import sys
from pathlib import Path

from rapport_audit.export import exporter
from rapport_audit.modele import lire

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "contexte-tracker.audit"
SECOND = FIXTURES / "02-b323e5a.toml"
CLI = Path(__file__).resolve().parents[1] / "audit-cli.py"


def _export() -> str:
    return exporter(lire(SECOND, rempli=True).unwrap())


def test_l_ordre_est_celui_du_rapport() -> None:
    texte = _export()
    titres = [ligne for ligne in texte.splitlines() if ligne.startswith(("# ", "## ", "### "))]
    assert titres == [
        "# Audit 02-b323e5a — contexte-tracker",
        "## Vérifications exécutées",
        "## Conformité au Brief",
        "### Critères de réussite",
        "### Hors-périmètre",
        "### Signaux de dérive",
        "### Symptôme",
        "## Dettes",
        "### Dette précédente",
        "### Dette actuelle",
        "### Dette corrigée",
        "### Dette écartée",
        "## Verdict",
    ]
    assert texte.rstrip().endswith(
        "**RÉSERVES** — Deux dettes `majeur`, dont un critère invérifiable (R12) qui attend la "
        "validation de\nl'utilisateur ; aucune dette `bloquant` ni `critique` ; R2, bloquante au "
        "premier audit, est corrigée."
    )


def test_l_en_tete_nomme_le_precedent() -> None:
    assert "- **Rang** : 2, après 01-38d27af" in _export()


def test_les_tableaux_gagnent_leurs_colonnes() -> None:
    lignes = _export().splitlines()
    assert "| # | Nature | Emplacement | Constat | Solution | Depuis | Sévérité |" in lignes
    assert (
        "| # | Nature | Emplacement | Constat | Solution | Depuis | Corrigée par | Preuve "
        "| Sévérité |"
    ) in lignes
    assert (
        "| # | Nature | Emplacement | Constat | Solution | Depuis | Écartée le | Justificatif "
        "| Sévérité |"
    ) in lignes


def test_une_cellule_tient_sur_une_ligne() -> None:
    (ligne,) = [x for x in _export().splitlines() if x.startswith("| R1 |")][:1]
    assert (
        "Passation » ne dit pas ce que devient la mesure du contexte quand l'utilisateur" in ligne
    )
    assert ligne.endswith("| majeur |")


def test_un_point_renvoie_a_sa_dette() -> None:
    assert "- **C3** — invérifiable → R12 — " in _export()


def test_la_sortie_d_une_verification_se_lit_en_bloc() -> None:
    texte = _export()
    assert (
        "- **Étape 3** — passée — `python3 -m pytest skills/implementation-tracker/tests`" in texte
    )
    assert "  ```text\n  38 passed in 1.42s\n  ```" in texte


def test_export_nomme_le_fichier_et_affiche_son_chemin_complet(tmp_path: Path) -> None:
    scratchpad = tmp_path / "sous"
    cible = scratchpad / "contexte-tracker-02-b323e5a.md"
    p = subprocess.run(
        [sys.executable, str(CLI), "export", str(SECOND), str(scratchpad)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    assert p.stdout == f"{cible.resolve()}\n"
    assert cible.read_text(encoding="utf-8") == _export()
