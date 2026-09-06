+++
id = "statusline-hors-des-linters"
title = "`statusline-command.py` échoue à la commande de lint documentée"
date = 2026-08-24
source = "Identifié par `check-pipeline-python`, R8 du rapport d'audit de clôture."
reviewed = 2026-09-06
category = "aggravee"
+++

## Constat

**Mesuré le 2026-09-06 :** `uvx ruff check .`, la commande que `contrat.md` § Dépendances documente
pour vérifier « le code Python versionné », rend **6 erreurs** — le double du constat d'origine, qui
en comptait 3 le 2026-08-24.

Les 3 d'origine sont toujours dans `statusline-command.py`, un fichier de la racine (dont `BLE001`
sur le `except Exception:` de la lecture du drapeau). **Les 3 nouvelles sont ailleurs** :
`skills/list-dir/scripts/tests/test_fusion.py` (2) et `test_contract.py` (1) — c'est-à-dire **dans**
le répertoire que l'entrée citait comme sain.

Conséquence directe : `uvx ruff check scripts skills`, qui rendait `All checks passed!` au constat
et servait de repli documentable, rend aujourd'hui `Found 3 errors.` La seconde voie du
**Pour solder** — restreindre la commande documentée aux répertoires réellement couverts — ne
suffirait donc plus à rendre la ligne vraie.

`statusline-command.py` échappe par ailleurs toujours à `basedpyright` : l'`include` de
`pyrightconfig.json` vaut `skills` et `scripts`, jamais la racine. C'est le seul `.py` versionné
qu'aucun des deux linters ne couvre vraiment — l'un l'ignore, l'autre échoue dessus.

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
