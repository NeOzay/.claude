"""Fixtures des tests du garde-fou.

LE DÉPÔT-JOUET EST LA BRIQUE DE BASE : chaque contrôle reçoit une racine et ne lit
rien d'autre, donc un test se réduit à monter l'arborescence minimale qui déclenche
— ou non — le constat visé. Aucun test ne lit le vrai dépôt : un contrôle qui
passerait au vert seulement ici serait invérifiable.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un dépôt-jouet sain : un contrat à deux sections, chacune citée une fois."""
    _ = ecrire(tmp_path, CONTRAT_REL, CONTRAT_MINIMAL)
    _ = ecrire(
        tmp_path,
        "skills/implementation-tracker/SKILL.md",
        "Voir [Arborescence](references/contrat.md#arborescence-et-nommage)\n"
        "et [Dates](references/contrat.md#dates-et-listing).\n",
    )
    return tmp_path
