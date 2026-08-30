+++
id = "absent-masque-outil-absent"
title = "Un projet neuf sans list-dir affiche ABSENT plutôt que OUTIL ABSENT"
date = 2026-08-30
source = "chantier semences-de-listes, audit R19"
+++

## Constat

`skills/debt-review/SKILL.md`, Étape 0 : le test `[ ! -d "$T/$l" ]` précède l'appel à `list-dir` et
fait `continue`. Dans un projet où les registres n'existent pas **et** où `list-dir` est absent du
`PATH`, la boucle imprime donc trois `ABSENT` et n'atteint jamais la branche `rc -eq 127` qui
dirait `OUTIL ABSENT`.

La consigne suivie sera « amorcer les trois registres », dont la commande échouera aussitôt en code
127.

## Pourquoi c'est gênant

Le diagnostic affiché est incomplet plutôt que faux : les registres sont bien absents. Mais il
désigne la conséquence et tait la cause, et envoie exécuter une commande qui ne peut pas marcher.

La portée est bornée, et c'est ce qui a fait classer le constat en réserve : l'échec suivant est
bruyant et immédiat — `init` sort 127 en nommant la commande introuvable — là où le défaut jumeau
déjà corrigé (un registre sain affiché `NON CONFORME`) envoyait, lui, corriger ce qui n'était pas
cassé.

## Pour solder

Sonder l'outil une fois avant la boucle plutôt que par registre, sans pour autant recopier ici une
garde de présence : `contrat.md` réserve la vérification de présence à `sante_skills.py`, une fois
par session, et interdit qu'elle soit répétée dans chaque bloc. La forme reste donc à trouver — ce
qui est en cause n'est pas la présence de l'outil, mais l'ordre dans lequel deux constats se
recouvrent.
