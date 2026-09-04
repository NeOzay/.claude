+++
id = "validate-avertit-hors-machine-semeuse"
title = "validate écrit sur stderr partout où la définition n'est pas installée"
date = 2026-09-04
source = "chantier peremption-contrat, audit de clôture ddebb2b, R6"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`provenance._peremption` résout la définition à chaque appel de `validate`. Sur une machine où
le skill qui porte cette définition n'est pas installé, **tout** `validate` d'une liste
estampillée écrit une ligne sur stderr : « définition introuvable dans les quatre rangs —
péremption invérifiable ».

Le motif de vérification employé par ce dépôt lui-même en devient faux-positif :
`ERR=$(list-dir validate "$L" 2>&1 >/dev/null); [ -z "$ERR" ]`, la boucle de l'étape 8 du plan
de ce chantier, échoue hors de la machine d'origine alors que rien n'est fautif.

## Pourquoi c'est gênant

Un avertissement qu'on rencontre partout cesse d'être lu, et emporte les vrais avec lui. Le
coût est double : le bruit sur les machines sans le skill, et les contrôles écrits contre un
stderr vide qui se mettent à échouer sans qu'aucune liste ne soit en cause.

Mode de défaillance : un script de CI qui garde sur `[ -z "$ERR" ]` casse à la première machine
qui n'a pas la définition — un échec dont la cause est ailleurs que là où il s'affiche.

## Pour solder

Trancher entre deux voies et l'écrire dans `contrat-liste.md` : soit une définition introuvable
cesse d'avertir (le silence est alors la règle, et la péremption invérifiable ne se dit plus),
soit les contrôles de ce dépôt cessent de garder sur un stderr vide et visent une chaîne
précise. Vérifier en jouant `validate` dans un répertoire sans aucun `.claude` accessible.

## Assumé

Le coût a été nommé à l'audit et accepté : l'avertissement dit une chose vraie, et son
alternative — se taire — cache une péremption réelle sur la machine où elle compte.
