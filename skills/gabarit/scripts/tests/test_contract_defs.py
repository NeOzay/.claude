"""`gabarit contract` et `gabarit defs` — lire une semence avant de remplir, et savoir
lesquelles existent.

CE QUE CE FICHIER PROUVE : `contract` rend le texte tel qu'il est écrit, commentaires
compris, et refuse une semence cassée ; `--values` rend les valeurs dans l'ordre du
fichier et échoue en nommant un champ inconnu ou sans valeurs ; `defs` imprime ses
ancrages, le rang et l'origine de chaque semence, les masquées et les ambiguës, et dit
qu'il n'y a rien plutôt que de se taire.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from gabarit.commandes import contract, defs, lire_semence
from gabarit.definitions import DEFS

CLI = Path(__file__).resolve().parent.parent / "gabarit-cli.py"

CONTRAT = """# la semence d'essai
name = "essai"
description = ""

[fields.statut]
type = "enum"
description = "où en est le fichier"
values = ["en-cours", "bloqué", "terminé"]

[fields.titre]
type = "text"
description = ""
"""


def semer(racine: Path, nom: str = "essai", contrat: str = CONTRAT) -> Path:
    d = racine / nom
    d.mkdir(parents=True)
    _ = (d / "contract.toml").write_text(contrat, encoding="utf-8")
    return d


# ---------------------------------------------------------------------- contract
def test_contract_rend_le_texte_tel_quel(tmp_path: Path) -> None:
    semence = lire_semence(semer(tmp_path)).unwrap()
    assert contract(semence).unwrap() == CONTRAT.rstrip("\n")


def test_une_semence_cassee_ne_sort_pas(tmp_path: Path) -> None:
    r = lire_semence(semer(tmp_path, contrat=CONTRAT.replace('"enum"', '"inconnu"')))
    assert not r
    assert "inconnu" in r.message


def test_values_dans_l_ordre_du_fichier(tmp_path: Path) -> None:
    semence = lire_semence(semer(tmp_path)).unwrap()
    assert contract(semence, "statut").unwrap() == "en-cours\nbloqué\nterminé"


def test_values_sur_champ_inconnu_ou_sans_values(tmp_path: Path) -> None:
    semence = lire_semence(semer(tmp_path)).unwrap()

    inconnu = contract(semence, "absent")
    assert not inconnu
    assert "non déclaré" in inconnu.message

    sans = contract(semence, "titre")
    assert not sans
    assert "aucune `values`" in sans.message


# -------------------------------------------------------------------------- defs
def test_defs_montre_rang_origine_et_masquee(tmp_path: Path) -> None:
    config = tmp_path / ".claude"
    _ = semer(config / "skills" / "outil" / DEFS)
    projet = tmp_path / "projet"
    _ = semer(projet / ".claude" / DEFS)

    sortie = defs(cwd=projet, package=config / "skills" / "gabarit" / "scripts").unwrap()

    assert f"projet : {projet / '.claude'}" in sortie
    assert f"config : {config}" in sortie
    ligne = next(ligne for ligne in sortie.splitlines() if "essai" in ligne)
    assert "rang 1" in ligne
    assert "masque config:outil" in ligne


def test_defs_dit_l_ambiguite(tmp_path: Path) -> None:
    # La configuration est rangée À CÔTÉ du répertoire courant, pas au-dessus : sinon
    # la remontée du projet la trouverait aussi, et les deux racines se confondraient.
    config = tmp_path / "cfg" / ".claude"
    _ = semer(config / "skills" / "a" / DEFS)
    _ = semer(config / "skills" / "b" / DEFS)
    vide = tmp_path / "vide"
    vide.mkdir()

    sortie = defs(cwd=vide, package=config / "skills").unwrap()

    assert "AMBIGUË — config:a, config:b" in sortie


def test_defs_sans_racine_le_dit(tmp_path: Path) -> None:
    sortie = defs(cwd=tmp_path, package=tmp_path).unwrap()
    assert "aucun — rangs 1 et 2 absents" in sortie
    assert "aucune semence" in sortie


# ------------------------------------------------------------------- point d'entrée
def lancer(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *argv], cwd=cwd, capture_output=True, text=True, check=False
    )


def test_cli_contract_et_values(tmp_path: Path) -> None:
    _ = semer(tmp_path / ".claude" / DEFS)

    r = lancer("contract", "essai", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert r.stdout == CONTRAT

    r = lancer("contract", "essai", "--values", "statut", cwd=tmp_path)
    assert r.stdout.splitlines() == ["en-cours", "bloqué", "terminé"]

    r = lancer("contract", "essai", "--values", "absent", cwd=tmp_path)
    assert r.returncode == 1
    assert r.stdout == ""


def test_cli_contract_sans_semence_code_2(tmp_path: Path) -> None:
    assert lancer("contract", cwd=tmp_path).returncode == 2


def test_cli_defs(tmp_path: Path) -> None:
    _ = semer(tmp_path / ".claude" / DEFS)
    r = lancer("defs", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "essai" in r.stdout
    assert "rang 1" in r.stdout
