+++
id = "migrate-valeur-multilignes-casse-une-ligne-par-changement"
title = "Une valeur préremplie multi-lignes casse l'invariant « un changement, une ligne » de migrate"
date = 2026-08-31
source = "chantier 2026-08-31-champs-preremplis, audit de clôture R3"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`listdir/store.py`, `_realign` : le libellé d'un `Change` interpole la valeur posée. Une section
portant `command = "printf 'ligne1\nligne2\n'"` rend
`l/a.md: section « Notes » — ajoutée, ligne1` puis `ligne2` sur une ligne à part.

## Pourquoi c'est gênant

La sortie de `migrate` se lit et se grep sur l'invariant « un changement, une ligne » — c'est ce
que fait `commands/migrate.py` en joignant les changements par `\n`, et ce que fait tout appelant
qui compte les lignes. Une valeur multi-lignes rend le compte faux sans qu'aucune commande
n'échoue.

## Pour solder

Tronquer ou échapper la valeur dans le libellé du `Change` — première ligne suivie d'un « … », ou
`repr()`. Le rendu doit rester lisible pour une valeur d'une ligne, qui est le cas courant.

## Assumé

<OPTIONNEL>
