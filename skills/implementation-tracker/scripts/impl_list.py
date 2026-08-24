#!/usr/bin/env python3
"""Liste les fichiers de SUIVI d'un répertoire d'implémentation, un nom par ligne.

PORTÉE : ne remonte que les suivis — ni `.brief.md`, ni `.audit.md`, ni `.plan.md`.
Utilisé par implementation-tracker (Étape 0 et Cas C), et par le garde-fou
`scripts/check_pipeline.py`, qui importe `suivis()` plutôt que de relancer un
processus : c'est ce qui garantit que le contrôle juge le filtre réellement en
service. Voir ../references/contrat.md, section « Dates et listing ».

POURQUOI UN SCRIPT ET PAS UNE COMMANDE EN LIGNE : le hook `rtk` réécrit les appels
Bash du modèle et ajoute une colonne de taille en fin de ligne, ce qui empêche toute
ancre `$` de matcher — les trois copies du filtre `grep -vE '\\.(brief|audit)\\.md$'`
ont cassé ensemble sans qu'aucune commande n'échoue. Un script échappe à cette
réécriture, qui ne s'applique qu'aux appels du modèle. Et un appel de script est un
appel : la définition du filtre reste ici, à un seul endroit.

RÉPERTOIRE ABSENT : message sur stderr, sortie vide, code 0. La distinction entre
« aucun chantier » et « arborescence absente » est faite par l'appelant, qui doit de
toute façon demander confirmation avant de créer l'arborescence.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Les suffixes qui ne sont PAS des suivis. Écrits en dur plutôt que dérivés : la
# liste est le filtre, et un fichier de chantier qui ne porte aucun de ces suffixes
# est un suivi par définition.
ANNEXES = (".brief.md", ".audit.md", ".plan.md")


def suivis(dir: Path) -> list[str]:
    """Les noms des fichiers de suivi de `dir`, triés. Répertoire absent → liste vide.

    Non récursif : les chantiers archivés vivent dans `done/`, qui se liste
    séparément, et `done/revues/` ne contient pas de suivis.
    """
    if not dir.is_dir():
        return []
    return sorted(
        p.name
        for p in dir.iterdir()
        if p.is_file() and p.name.endswith(".md") and not p.name.endswith(ANNEXES)
    )


def main(argv: list[str]) -> int:
    dir = Path(argv[0]) if argv else Path(".claude/implementation")
    if not dir.is_dir():
        sys.stderr.write(f"impl-list: répertoire absent : {dir}\n")
        return 0
    for name in suivis(dir):
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
