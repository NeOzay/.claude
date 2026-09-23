"""Démarrage de session : le lexique local versé au contexte, en échec ouvert."""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from lexique import annonce_session

Ecrire = Callable[[str, str], Path]
CLI = Path(__file__).resolve().parents[1] / "lexique-cli.py"


def _session(projet: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(projet)}
    return subprocess.run(
        [sys.executable, str(CLI), "session"], capture_output=True, text=True, env=env, check=False
    )


def test_silencieux_sans_lexique_local(tmp_path: Path) -> None:
    assert annonce_session(tmp_path / "g.md", tmp_path / "absent.md", tmp_path) == ""


def test_verse_le_lexique_local(ecrire: Ecrire, tmp_path: Path) -> None:
    lo = ecrire("p/.claude/LEXIQUE.md", "| Essai | Un terme local. | [x](x) |\n")
    texte = annonce_session(tmp_path / "absent.md", lo, tmp_path / "p")
    assert texte.startswith(f"Lexique local de {tmp_path / 'p'}")
    assert "| Essai | Un terme local. | [x](x) |" in texte
    assert "ALERTE" not in texte


def test_alerte_sur_un_terme_reserve(ecrire: Ecrire, tmp_path: Path) -> None:
    g = ecrire("g/LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    lo = ecrire("p/.claude/LEXIQUE.md", "| Gabarit | Autre chose. | [x](x) |\n")
    texte = annonce_session(g, lo, tmp_path / "p")
    assert "ALERTE" in texte
    assert "déjà réservé au global" in texte


def test_alerte_sur_un_lexique_malforme(ecrire: Ecrire, tmp_path: Path) -> None:
    lo = ecrire("p/.claude/LEXIQUE.md", "| Essai | sans lien |\n")
    texte = annonce_session(tmp_path / "absent.md", lo, tmp_path / "p")
    assert "ALERTE" in texte
    assert "cellules" in texte


def test_cli_silencieuse_sans_lexique_local(tmp_path: Path) -> None:
    r = _session(tmp_path)
    assert (r.returncode, r.stdout) == (0, "")


def test_cli_sort_en_zero_malgre_un_lexique_malforme(ecrire: Ecrire, tmp_path: Path) -> None:
    ecrire("p/.claude/LEXIQUE.md", "!du texte, aucun tableau\n")
    r = _session(tmp_path / "p")
    assert r.returncode == 0
    assert "ALERTE" in r.stdout


def test_cli_sous_projet_de_monodepot(ecrire: Ecrire, tmp_path: Path) -> None:
    """`$CLAUDE_PROJECT_DIR` tel quel : le lexique du sous-projet, pas celui de la racine git."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    ecrire("sous/.claude/LEXIQUE.md", "| Zorglubage | Un terme du sous-projet. | [x](x) |\n")
    r = _session(tmp_path / "sous")
    assert r.returncode == 0
    assert "Zorglubage" in r.stdout


def test_alerte_sur_un_lexique_non_utf8(tmp_path: Path) -> None:
    lo = tmp_path / "p" / ".claude" / "LEXIQUE.md"
    lo.parent.mkdir(parents=True)
    lo.write_bytes("| Terme | Définition | Lien |\n".encode("latin-1"))
    texte = annonce_session(tmp_path / "absent.md", lo, tmp_path / "p")
    assert "illisible" in texte
    assert "ALERTE" in texte
    assert "pas en UTF-8" in texte


def test_silencieux_quand_le_local_est_le_global(ecrire: Ecrire, tmp_path: Path) -> None:
    g = ecrire(".claude/LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    assert annonce_session(g, g, tmp_path) == ""
