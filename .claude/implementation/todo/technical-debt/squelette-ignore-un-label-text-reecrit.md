+++
id = "squelette-ignore-un-label-text-reecrit"
title = "Un label prérempli réécrit laisse une table facultative tenue pour intacte"
date = 2026-10-17
severite = "avertissement"
chantier = "gabarit-sections-structurees"
reference = "R6"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`_squelette_au_marqueur`, dans `skills/gabarit/scripts/gabarit/structure.py`, saute un label
prérempli par `text` ou `command` sans lire son corps. Une table de labels facultative dont seul un
label prérempli a été réécrit est donc tenue pour laissée au Marqueur. Rejoué à l'audit 02 : table
`Annexe` facultative, `Source` requis, `Outil` à `text = "pytest"` réécrit « nox » ;
`list-dir validate --filled` rend conforme, et `list-dir merge` omet la section entière.

## Pourquoi c'est gênant

Défaillance silencieuse : la valeur écrite disparaît de l'aggloméré, et les labels requis de la
table ne sont pas réclamés. Le cas est rare, mais il viendra avec le Chantier d'intégration si une
Semence déclare des labels `text`.

## Pour solder

Compter comme entamé un label `text` dont le corps rogné diffère de son `text`, qui est littéral ;
ne garder le saut que pour une `command`, et nommer cette limite dans
`skills/gabarit/references/format.md`, « Une table facultative laissée au squelette ». Ajouter le
cas d'un `text` réécrit à `test_squelette.py` et à `test_structure.py` de list-dir.

## Assumé

Clôture de `gabarit-sections-structurees` décidée par l'utilisateur avec cette dette : à traiter
avec le Chantier d'intégration.
