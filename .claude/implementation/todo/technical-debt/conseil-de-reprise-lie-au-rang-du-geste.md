+++
id = "conseil-de-reprise-lie-au-rang-du-geste"
title = "Le conseil de reprise de la clôture dépend de la position du checkout dans la liste des gestes"
date = 2026-09-14
source = "chantier `git-smart-commit-trois-commits`, R16 du rapport d'audit"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Dans `commit_chantier.py`, `executer` choisit entre « la commande peut être relancée telle quelle »
et « terminer à la main » par une comparaison du rang du geste en échec (`rang <= 1`). Ce seuil
suppose que `git checkout <base>` est le second élément de la liste construite par `gestes`. Rien
ne relie les deux fonctions.

## Pourquoi c'est gênant

Un geste inséré avant le changement de branche décale le seuil : le script annoncerait une relance
possible alors qu'on est déjà sur `base:`, ou l'inverse. Le conseil de reprise, que la correction
de R2 visait à rendre fiable, deviendrait faux en silence, et aucun test ne le détecterait tant que
les rangs testés ne bougent pas.

## Pour solder

Porter l'information sur le geste lui-même (par exemple un booléen « quitte `<slug>` » dans le
tuple de `gestes`), et en dériver le conseil dans `executer`.
