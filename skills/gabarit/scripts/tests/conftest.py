"""Fixtures des tests du paquet `gabarit`.

sys.path vise `scripts/`, ce qui rend `import gabarit` disponible. `gabarit-cli.py` porte
un tiret : il n'est PAS importable, et les tests qui l'exercent passent par un
sous-processus.

AUCUN TEST NE LIT LE VRAI DÉPÔT, sauf ceux qui le disent : un comportement qui ne serait
vert qu'ici serait invérifiable ailleurs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
