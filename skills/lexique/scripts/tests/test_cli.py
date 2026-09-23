"""`lexique liste` : échec fermé, constats sur stderr."""

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

Ecrire = Callable[[str, str], Path]
CLI = Path(__file__).resolve().parents[1] / "lexique-cli.py"


def _liste(projet: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "liste", "--projet", str(projet)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_liste_un_terme_local(ecrire: Ecrire, tmp_path: Path) -> None:
    # Un terme inventé : il ne peut pas être déjà réservé au global du dépôt.
    ecrire("p/.claude/LEXIQUE.md", "| Zorglubage | Un terme local. | [x](x) |\n")
    r = _liste(tmp_path / "p")
    assert r.returncode == 0, r.stderr
    assert "local\tZorglubage\t[x](x)" in r.stdout


def test_liste_sort_en_un_sur_un_doublon_local(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire(
        "p/.claude/LEXIQUE.md", "| Zorglubage | Un. | [x](x) |\n| ZORGLUBAGE | Deux. | [x](x) |\n"
    )
    r = _liste(tmp_path / "p")
    assert r.returncode == 1
    assert "défini deux fois" in r.stderr


def test_liste_sort_en_un_sur_un_lexique_malforme(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire("p/.claude/LEXIQUE.md", "| Zorglubage | sans lien |\n")
    r = _liste(tmp_path / "p")
    assert r.returncode == 1
    assert "cellules" in r.stderr


def test_erreur_d_appel() -> None:
    r = subprocess.run([sys.executable, str(CLI)], capture_output=True, text=True, check=False)
    assert r.returncode == 2


def test_liste_dit_un_lexique_local_absent_sans_echouer(tmp_path: Path) -> None:
    r = _liste(tmp_path)
    assert r.returncode == 0, r.stderr
    assert "local : aucun lexique" in r.stderr
