+++
id = "lexique-home-versionne-par-git"
title = "`lexique liste` et `init` sans `--projet` visent le HOME quand il est lui-même un dépôt git"
date = 2026-09-23
source = "Identifié par `lexique`, R14 du rapport d'audit de clôture."
+++

## Constat

Sans `--projet`, `liste` et `init` prennent pour projet la racine git du répertoire courant
(`racine_projet`, `skills/lexique/scripts/lexique.py`). Quand le HOME est versionné par git, un
projet non versionné rangé dessous a pour racine le HOME, dont `.claude/LEXIQUE.md` est le lexique
global : `liste` l'ignore comme local et ne lit pas le lexique du projet (sortie 0), `init` refuse
en désignant le global. La docstring de `racine_projet` justifie son choix par ce même défaut.
`session` n'est pas concernée. Le cas n'existe pas sur la machine où le chantier a été mené.

Établi par : l'audit de clôture de `lexique` (`6b06ca6`), sur un HOME git simulé.

## Pourquoi c'est gênant

Le contrôle des réservations passe en silence : un terme local qui redéfinit un terme global
n'est pas signalé, alors que c'est la faute que la commande existe pour attraper.

## Pour solder

Quand la racine git trouvée est celle qui porte le lexique global, retomber sur le répertoire
courant ; corriger la docstring ; ajouter un test sur un HOME git simulé.

## Assumé

Reporté à la clôture de `lexique` par décision de l'utilisateur : aucun HOME versionné sur la
machine, et `--projet` contourne le cas.
