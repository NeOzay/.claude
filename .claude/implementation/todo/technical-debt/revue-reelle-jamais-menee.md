+++
id = "revue-reelle-jamais-menee"
title = "Le flux de revue n'a jamais produit d'archive réelle sous `done/revues/`"
date = 2026-08-23
source = "chantier `format-registres`, R2 des audits de clôture — écart au brief ratifié le 2026-08-20"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le brief du chantier demandait qu'« une revue complète des 17 entrées actives tourne sur ce flux, et
que le fichier aggloméré soit archivé sous `done/revues/<date>-revue.md` ». La première moitié est
servie et vérifiée ; la seconde ne l'est pas. La revue à blanc dérive vers le scratchpad, remplit
d'un contenu de recette et agglomère — puis tout est effacé. Rien n'est commité sous `done/revues/`,
et c'est délibéré : l'écart a été ratifié le 2026-08-20.

## Pourquoi c'est gênant

Ce qui est démontré est la **mécanique** — le compte, la conservation, les deux verdicts de
`validate`. Ce qui ne l'est pas est le flux avec du **jugement** dedans : des verdicts réels, des
preuves exécutées de longueurs variées, un arbitrage écrit, des `move` vers les listes soldée et
écartée. C'est là que les surprises restent possibles, et R19 l'a montré — le défaut n'est apparu
que le jour où une vraie sortie de commande a été collée dans une fiche.

Tant que cette passe n'a pas eu lieu, `debt-review` réécrit de bout en bout n'a jamais servi une
seule fois pour de vrai.

## Pour solder

Mener une revue réelle avec `/debt-review` : elle produira l'archive attendue et exercera du même
coup `sortie-du-registre-jamais-exercee`. Le solde s'établit par l'existence d'un
`done/revues/<date>-revue.md` commité, dont le préambule porte le compte des entrées instruites, et
par au moins un `move` effectif vers une liste de sortie.

## Assumé

<OPTIONNEL>
