"""Fixtures des tests du paquet `listdir`.

LA LISTE-JOUET EST LA BRIQUE DE BASE, sur le modèle du dépôt-jouet de
`scripts/tests/conftest.py` : chaque test monte sur `tmp_path` la liste minimale qui
déclenche — ou non — le comportement visé. AUCUN TEST NE LIT LE VRAI DÉPÔT : un
comportement qui ne serait vert qu'ici serait invérifiable ailleurs, et c'est
précisément ce que ce paquet est censé garantir à qui le déploie.

Ce fichier ne porte QUE des fixtures. Le contrat-jouet et les fonctions qui montent
une liste vivent dans `jouet.py` — un `conftest` ne s'importe pas par son nom quand
deux suites en portent un (cf. la docstring de `jouet.py`).

sys.path vise `scripts/`, ce qui rend `import listdir` disponible. `list-dir.py`
porte un tiret : il n'est PAS importable, et les tests qui l'exercent passent par un
sous-processus (cf. test_entree_cli.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jouet import ELEMENT, ecrire, monter_liste


@pytest.fixture
def liste_vide(tmp_path: Path) -> Path:
    """Une liste conforme et sans élément. Une liste fraîchement créée est légitime."""
    return monter_liste(tmp_path / "jouet")


@pytest.fixture
def liste(liste_vide: Path) -> Path:
    """La même, avec un élément conforme et rempli."""
    _ = ecrire(liste_vide, "premier.md", ELEMENT)
    return liste_vide
