+++
id = "statusline-hors-des-linters"
title = "`statusline-command.py` échoue à la commande de lint documentée"
date = 2026-08-24
source = "Identifié par `check-pipeline-python`, R8 du rapport d'audit de clôture."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`uvx ruff check .`, la commande que `contrat.md` § Dépendances documente pour vérifier « le code
Python versionné », rend **3 erreurs** dans `statusline-command.py` — un fichier de la racine,
préexistant à ce chantier et sans rapport avec lui.

Il échappe par ailleurs à `basedpyright` : l'`include` de `pyrightconfig.json` vaut `skills` et
`scripts`, jamais la racine. C'est le seul `.py` versionné du dépôt qu'aucun des deux linters ne
couvre vraiment — l'un l'ignore, l'autre échoue dessus.

Établi par : `uvx ruff check .` → `Found 3 errors.`, toutes dans `statusline-command.py` (dont
`BLE001` ligne 110) ; `uvx ruff check scripts skills/implementation-tracker` → `All checks passed!`.

## Pourquoi c'est gênant

la commande documentée doit pouvoir être lancée telle quelle par quelqu'un d'autre. Celle-ci sort
non nulle sur un dépôt sain : qui la rejoue apprend à ignorer son verdict, et le jour où elle
signale une vraie régression du pipeline, ce verdict ne vaudra plus rien. C'est le mode de
défaillance que ce paragraphe du contrat décrit déjà pour les linters absents du `PATH`, sous une
autre forme.

`check-pipeline-python` a corrigé le lanceur de `basedpyright` dans la même table (`R1`) sans
toucher celui de `ruff` : la ligne est donc à moitié juste, ce qui est plus trompeur qu'une ligne
franchement fausse.

## Pour solder

deux voies, à trancher : corriger les 3 erreurs de `statusline-command.py` et l'ajouter à
l'`include` de `pyrightconfig.json` — c'est la seule qui rende la commande vraie ; ou restreindre la
commande documentée aux répertoires réellement couverts, ce qui laisse le fichier hors de toute
vérification.

## Assumé

le fichier est un utilitaire d'affichage, hors du pipeline : aucune de ses 3 erreurs n'a d'effet sur
le contrat partagé.
