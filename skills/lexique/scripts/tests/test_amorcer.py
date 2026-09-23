"""Amorçage d'un lexique local : l'en-tête posé par la commande, jamais un fichier écrasé."""

import subprocess
import sys
from pathlib import Path

from lexique import LOCAL, amorcer, chemin_local, lire

CLI = Path(__file__).resolve().parents[1] / "lexique-cli.py"


def test_pose_un_lexique_lisible_et_vide(tmp_path: Path) -> None:
    chemin = chemin_local(tmp_path)
    r = amorcer(chemin)
    assert r.value == chemin
    lu = lire(chemin, LOCAL)
    assert lu and lu.value == []


def test_n_ecrase_rien(tmp_path: Path) -> None:
    chemin = chemin_local(tmp_path)
    chemin.parent.mkdir(parents=True)
    chemin.write_text("à garder\n", encoding="utf-8")
    r = amorcer(chemin)
    assert not r
    assert "existe déjà" in r.message
    assert chemin.read_text(encoding="utf-8") == "à garder\n"


def test_cli_init(tmp_path: Path) -> None:
    argv = [sys.executable, str(CLI), "init", "--projet", str(tmp_path)]
    premier = subprocess.run(argv, capture_output=True, text=True, check=False)
    assert (premier.returncode, premier.stdout) == (0, f"{chemin_local(tmp_path)}\n")
    second = subprocess.run(argv, capture_output=True, text=True, check=False)
    assert second.returncode == 1
    assert "existe déjà" in second.stderr
