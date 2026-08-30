"""Fixtures des tests du garde-fou.

LE DÉPÔT-JOUET EST LA BRIQUE DE BASE : chaque contrôle reçoit une racine et ne lit
rien d'autre, donc un test se réduit à monter l'arborescence minimale qui déclenche
— ou non — le constat visé. Aucun test ne lit le vrai dépôt : un contrôle qui
passerait au vert seulement ici serait invérifiable.

Ce fichier ne porte QUE des fixtures. Le contrat-jouet et les fonctions qui montent
une arborescence vivent dans `depot_jouet.py` — un `conftest` ne s'importe pas par
son nom quand deux suites en portent un (cf. la docstring de `depot_jouet.py`).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from depot_jouet import CONTRAT_MINIMAL, CONTRAT_REL, ecrire


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
