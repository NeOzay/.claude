"""Le projet d'un appel : la racine git du répertoire courant, jamais un ancêtre au hasard."""

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from lexique import racine_projet

Ecrire = Callable[[str, str], Path]
CLI = Path(__file__).resolve().parents[1] / "lexique-cli.py"
# Un global hors de tout dépôt de test : aucune racine ne le porte.
GLOBAL_ABSENT = Path("/nulle-part/LEXIQUE.md")


def _git_init(racine: Path) -> None:
    subprocess.run(["git", "init", "-q", str(racine)], check=True)


def test_racine_git_depuis_un_sous_repertoire(tmp_path: Path) -> None:
    _git_init(tmp_path)
    sous = tmp_path / "a" / "b"
    sous.mkdir(parents=True)
    assert racine_projet(sous, GLOBAL_ABSENT).resolve() == tmp_path.resolve()


def test_hors_depot_le_repertoire_lui_meme(tmp_path: Path) -> None:
    # tmp_path n'est dans aucun dépôt git sur une machine de test ordinaire.
    assert racine_projet(tmp_path, GLOBAL_ABSENT) == tmp_path


def test_home_versionne_le_projet_reste_ici(tmp_path: Path) -> None:
    """Sous un HOME git, la racine qui porte le global n'est pas le projet."""
    _git_init(tmp_path)
    fichier_global = tmp_path / ".claude" / "LEXIQUE.md"
    fichier_global.parent.mkdir()
    _ = fichier_global.write_text("| Terme | Définition | Lien |\n|---|---|---|\n")
    proj = tmp_path / "proj"
    proj.mkdir()
    assert racine_projet(proj, fichier_global) == proj


def test_liste_depuis_un_sous_repertoire_lit_le_lexique_du_projet(
    ecrire: Ecrire, tmp_path: Path
) -> None:
    _git_init(tmp_path)
    ecrire(".claude/LEXIQUE.md", "| Zorglubage | Un terme local. | [x](x) |\n")
    sous = tmp_path / "src"
    sous.mkdir()
    r = subprocess.run(
        [sys.executable, str(CLI), "liste"], cwd=sous, capture_output=True, text=True, check=False
    )
    assert r.returncode == 0, r.stderr
    assert "local\tZorglubage" in r.stdout
