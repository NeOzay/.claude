"""Le dépôt-jouet : contrat minimal, chemins de référence, et l'écriture d'un fichier.

POURQUOI CE MODULE N'EST PAS `conftest.py` : deux suites coexistent dans ce dépôt, et
`skills/list-dir/scripts/tests/conftest.py` porte déjà ce nom. En mode d'import
« prepend », pytest dérive le nom de module du basename : un `from conftest import …`
résout alors vers l'un ou l'autre selon l'ordre de collecte, et le diagnostic accuse le
mauvais fichier. Un nom unique supprime l'ambiguïté ; `conftest.py` ne garde que les
fixtures, qui ne s'importent jamais. Le pendant côté `list-dir` est `jouet.py` — les deux
basenames diffèrent, c'est délibéré.
"""

from __future__ import annotations

from pathlib import Path

CONTRAT_REL = "skills/implementation-tracker/references/contrat.md"

CONTRAT_MINIMAL = """# Contrat

## Arborescence et nommage

Une règle.

## Dates et listing

Une autre règle.
"""


def ecrire(root: Path, rel: str, contenu: str) -> Path:
    """Écrit `contenu` dans `root/rel`, en créant les répertoires manquants."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(contenu, encoding="utf-8")
    return path
