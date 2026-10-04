+++
id = "contexte-point-d-entree-et-logique-meles"
title = "`contexte.py` mêle point d'entrée et logique, contre la convention Python du dépôt"
date = "2026-10-04"
source = "chantier `contexte-tracker`, audits de clôture, constat R13"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/implementation-tracker/scripts/contexte.py` porte dans un même fichier importable le
parseur d'arguments, les écritures sur stderr et la logique de stockage, et `main` traduit une
`OSError` par un `except`. `rules/claude-python-style.md`, section « Structure », demande un point
d'entrée à tiret sans logique et un `Result[T]` entre couches. Son voisin `impl_list.py` a la même
forme.

## Pourquoi c'est gênant

Tant que le script a deux usages, le coût est faible. Un troisième usage greffé là ferait
grossir `main` et ses chemins d'erreur hors de toute couche testable seule.

## Pour solder

Séparer un point d'entrée `contexte-cli.py` et une bibliothèque qui rend un `Result[T]`, en même
temps que `impl_list.py` pour garder les deux scripts du skill alignés.

## Assumé

Reporté à la Clôture de `contexte-tracker` : le script suit la forme établie du skill, et le
réaligner seul l'en écarterait.
