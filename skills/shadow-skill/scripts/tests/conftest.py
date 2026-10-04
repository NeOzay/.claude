"""Fixtures des tests des shadow-skills.

sys.path vise `scripts/`, ce qui rend `import shadow_skill` disponible.
"""

import sys
from collections.abc import Callable
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

type Poser = Callable[..., Path]


@pytest.fixture
def poser(tmp_path: Path) -> Poser:
    """Pose `<racine>/<nom>/SKILL.md` sous `tmp_path` et rend son chemin.

    `poser("g", "alpha", tags=["lua"])` ; `front=` remplace le front matter entier, pour
    écrire un fichier mal formé.
    """

    def _poser(
        racine: str,
        nom: str,
        *,
        description: str = "Une description.",
        quand: str = "Quand il le faut.",
        tags: list[str] | None = None,
        front: str | None = None,
    ) -> Path:
        chemin = tmp_path / racine / nom / "SKILL.md"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        liste = ", ".join(f'"{t}"' for t in (tags or []))
        entete = (
            front
            if front is not None
            else (
                f'gabarit = "shadow-skill"\nname = "{nom}"\ndescription = """{description}"""\n'
                f'when-to-load = "{quand}"\ntags = [{liste}]\n'
            )
        )
        chemin.write_text(f"+++\n{entete}+++\n\n## Instructions\n\nCorps.\n", encoding="utf-8")
        return chemin

    return _poser
