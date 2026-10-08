"""Fixtures des tests de session-dump.

sys.path vise `scripts/`, ce qui rend `import session_dump` disponible. `ecrire_jsonl` pose un
JSONL de session synthétique : un test n'a besoin que des lignes qui l'intéressent.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

type Ligne = Mapping[str, object]


@pytest.fixture
def ecrire_jsonl() -> Callable[[Path, Iterable[Ligne]], Path]:
    def ecrire(chemin: Path, lignes: Iterable[Ligne]) -> Path:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text("".join(json.dumps(ligne) + "\n" for ligne in lignes), encoding="utf-8")
        return chemin

    return ecrire
