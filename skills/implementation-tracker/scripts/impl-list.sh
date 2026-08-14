#!/usr/bin/env bash
# Liste les fichiers de SUIVI d'un répertoire d'implémentation, un nom par ligne.
#
# PORTÉE : ne remonte que les suivis — ni `.brief.md`, ni `.audit.md`, ni `.plan.md`.
# Utilisé par implementation-tracker (Étape 0 et Cas C). Voir
# skills/implementation-tracker/references/contrat.md, section « Dates et listing ».
#
# POURQUOI UN SCRIPT ET PAS UNE COMMANDE EN LIGNE : le hook `rtk` réécrit les appels
# Bash du modèle et ajoute une colonne de taille en fin de ligne, ce qui empêche toute
# ancre `$` de matcher — les trois copies du filtre `grep -vE '\.(brief|audit)\.md$'`
# ont cassé ensemble sans qu'aucune commande n'échoue. Un script échappe à cette
# réécriture, qui ne s'applique qu'aux appels du modèle. Et un appel de script est un
# appel : la définition du filtre reste ici, à un seul endroit.
#
# RÉPERTOIRE ABSENT : message sur stderr, sortie vide, code 0. La distinction entre
# « aucun chantier » et « arborescence absente » est faite par l'appelant, qui doit de
# toute façon demander confirmation avant de créer l'arborescence.
set -uo pipefail

dir="${1:-.claude/implementation}"

if [ ! -d "$dir" ]; then
  printf 'impl-list: répertoire absent : %s\n' "$dir" >&2
  exit 0
fi

find "$dir" -maxdepth 1 -type f -name '*.md' \
  ! -name '*.brief.md' \
  ! -name '*.audit.md' \
  ! -name '*.plan.md' \
  -printf '%f\n' | sort
