"""Fixtures des tests du lexique.

sys.path vise `scripts/`, ce qui rend `import lexique` disponible.
"""

import sys
from collections.abc import Callable
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ENTETE = "| Terme | Définition | Lien |\n|---|---|---|\n"


@pytest.fixture
def ecrire(tmp_path: Path) -> Callable[[str, str], Path]:
    """Écrit un lexique sous `tmp_path` : `ecrire("g.md", "| a | b | [c](d) |\\n")`.

    Le corps est précédé de l'en-tête et de la séparation, sauf s'il commence par `!`.
    """

    def _ecrire(nom: str, corps: str) -> Path:
        chemin = tmp_path / nom
        chemin.parent.mkdir(parents=True, exist_ok=True)
        texte = corps[1:] if corps.startswith("!") else ENTETE + corps
        chemin.write_text(texte, encoding="utf-8")
        return chemin

    return _ecrire
