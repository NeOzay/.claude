"""`lexique chemin`, `termes`, `definition`, `definitions` : ce que Neovim reçoit de la CLI."""

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

Ecrire = Callable[[str, str], Path]
CLI = Path(__file__).resolve().parents[1] / "lexique-cli.py"


def _cli(*args: str, projet: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args, "--projet", str(projet)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_chemin_local(ecrire: Ecrire, tmp_path: Path) -> None:
    lo = ecrire("p/.claude/LEXIQUE.md", "| Zorglubage | Un terme local. | [x](x) |\n")
    r = _cli("chemin", projet=tmp_path / "p")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(lo)


def test_chemin_local_absent(tmp_path: Path) -> None:
    r = _cli("chemin", projet=tmp_path)
    assert r.returncode == 1
    assert "n'existe pas" in r.stderr


def test_chemin_global(tmp_path: Path) -> None:
    r = _cli("chemin", "--global", projet=tmp_path)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().endswith("LEXIQUE.md")


def test_termes_global_puis_local(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire("p/.claude/LEXIQUE.md", "| Zorglubage | Un terme local. | [x](x) |\n")
    r = _cli("termes", projet=tmp_path / "p")
    assert r.returncode == 0, r.stderr
    assert "Zorglubage" in r.stdout.splitlines()


def test_termes_ligne_fautive_servie_a_part(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire(
        "p/.claude/LEXIQUE.md",
        "| Zorglubage | Un terme inventé. | [x](x) |\n| Autre | sans lien |\n",
    )
    r = _cli("termes", projet=tmp_path / "p")
    assert r.returncode == 0, r.stderr
    assert "Zorglubage" in r.stdout.splitlines()
    assert "cellules" in r.stderr


def test_definitions_global_puis_local(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire("p/.claude/LEXIQUE.md", "| Zorglubage | Un terme local. | [x](x) |\n")
    r = _cli("definitions", projet=tmp_path / "p")
    assert r.returncode == 0, r.stderr
    lignes = r.stdout.splitlines()
    assert lignes[-1] == "local\tZorglubage\tUn terme local."
    assert all(ligne.startswith("global\t") for ligne in lignes[:-1])


def test_definitions_ligne_fautive_servie_a_part(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire(
        "p/.claude/LEXIQUE.md",
        "| Zorglubage | Un terme inventé. | [x](x) |\n| Autre | sans lien |\n",
    )
    r = _cli("definitions", projet=tmp_path / "p")
    assert r.returncode == 0, r.stderr
    assert "local\tZorglubage\tUn terme inventé." in r.stdout.splitlines()
    assert "cellules" in r.stderr


def test_definition_terme_compose(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire(
        "p/.claude/LEXIQUE.md",
        "| Zorglubage composé | Un terme à plusieurs mots. | [x](x) |\n",
    )
    r = _cli("definition", "zorglubage  composé", projet=tmp_path / "p")
    assert r.returncode == 0, r.stderr
    assert "Zorglubage composé\tUn terme à plusieurs mots." in r.stdout


def test_definition_aucune_correspondance(tmp_path: Path) -> None:
    r = _cli("definition", "Zorglubage", projet=tmp_path)
    assert r.returncode == 1
    assert "aucun terme correspondant" in r.stderr


def test_definition_prend_un_terme_en_tiret_apres_double_tiret(tmp_path: Path) -> None:
    r = subprocess.run(
        [sys.executable, str(CLI), "definition", "--projet", str(tmp_path), "--", "-h"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1
    assert "« -h » : aucun terme correspondant." in r.stderr
