+++
id = "session-dump-meta-illisible-compte-comme-ligne"
title = "`session-dump` rapporte un `.meta.json` illisible comme une « ligne illisible ignorée »"
date = 2026-10-12
severite = "note"
chantier = "affiner-session-dump"
reference = "R2"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`lire_sous_agents`, dans `skills/session-dump/scripts/session_dump.py`, ajoute un `.meta.json`
illisible au total `Bilan.illisibles`, avec les lignes JSONL illisibles, comme le journal du
Chantier le décide. `session-dump-cli.py` rapporte ce total en « N ligne(s) illisible(s)
ignorée(s) » : un `.meta.json` n'est pas une ligne, et il n'est pas ignoré, puisqu'il donne
`famille = "?"`. Relevé à l'audit `01-be6978c` ; le dépôt ne porte aucun cas.

## Pourquoi c'est gênant

Le message est inexact : l'utilisateur qui le lit cherche une ligne JSONL abîmée là où c'est un
fichier de métadonnées. Sans autre effet que le temps perdu à chercher.

## Pour solder

Libeller le total en « N élément(s) illisible(s) ignoré(s) », comme la docstring de
`lire_sous_agents` le dit déjà, ou compter les `.meta.json` à part. Adapter le test de la sortie
de la commande dans `tests/test_cli.py`.

## Assumé

<OPTIONNEL>
