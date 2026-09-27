+++
gabarit = "brief"
slug = "lexique-nvim"
titre = "Commande Neovim :Lexique, alimentée par la commande lexique"
statut = "validé"
execution = "délégué"
"créé" = 2026-09-27
+++

## Intention

**Symptôme** : en relisant des diffs et en parcourant les fichiers du projet dans Neovim, obtenir le sens d'un terme demande de quitter l'éditeur ou d'aller fouiller les lexiques.
**But** : obtenir rapidement, depuis Neovim, la définition d'un terme dans le projet du cwd, et ouvrir d'une commande le lexique local ou global.

## Critères de réussite

- Après `:source <fichier Lua>` dans Neovim, lancé depuis un projet doté d'un lexique local : `:Lexique` ouvre ce lexique local, `:Lexique!` ouvre le global.
- Depuis un projet sans lexique local, `:Lexique` affiche que le fichier n'existe pas, sans rien ouvrir.
- `:Lexique <Tab>` propose les termes des lexiques global et local.
- `:Lexique <terme>` affiche la définition du terme avec `vim.print()`.
- `:Lexique Signal de dérive` affiche la définition du terme composé, et `:Lexique Signal de <Tab>` le complète.
- Les nouvelles commandes de `lexique` ont leurs tests, et la suite passe : `/home/debian/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests`.
- `init`, `liste` et `session` rendent la même sortie et le même code qu'avant, sur les mêmes lexiques.

## Hors-périmètre

- L'intégration de `:Lexique` dans la configuration Neovim (`~/.config/nvim`) : elle fera l'objet de son propre chantier, dans ce dépôt-là.
- Les mappages, dont celui qui donnerait la définition du mot sous le curseur : ils viendront après, sur la commande livrée ici.

## Signaux de dérive

- Le diff change le comportement ou la sortie d'une commande existante de `lexique` (`init`, `liste`, `session`) : les besoins de Neovim passent par de nouvelles commandes (dit)
- Le Lua lit, parse ou cherche lui-même dans un `LEXIQUE.md` ou en construit le chemin : tout ce qu'il sait d'un lexique vient de la commande `lexique` (dit)

## Contraintes connues de l'utilisateur

- **Décision** : les commandes Neovim vivent dans un fichier de ce dépôt, sourcé à la main pour les tester ; il sera supprimé une fois l'intégration faite dans Neovim (dit)
- **Décision** : Neovim obtient de la commande `lexique` les chemins des lexiques global et local, les termes disponibles (complétion de `<terme>`) et la définition d'un terme ; il ne lit pas les fichiers lui-même (dit)
- **Décision** : sans lexique local, `:Lexique` affiche que le fichier n'existe pas (dit)
- **Décision** : la définition s'affiche avec `vim.print()` (dit)
- **Décision** : le projet passé à `lexique` est le cwd de Neovim (dit)
- **Existant** : `lexique` n'a que `init`, `liste` et `session` ; `liste` ne sort ni la définition ni les chemins, et rend 1 dès qu'il y a un constat (dépôt: skills/lexique/scripts/lexique-cli.py)
- **Décision** : le fichier à sourcer est `skills/lexique/nvim/lexique.lua` (dit)
- **Décision** : quand le lexique local est le global lui-même (cwd = `~/.claude`), `:Lexique` dit qu'il n'y a pas de lexique local, comme `liste` qui l'ignore alors (dit)
- **Décision** : `:Lexique <terme>` trouve le terme à la casse et aux espaces près, comme la comparaison de `lexique` : « suivi » trouve « Suivi » (dit)
- **Décision** : un lexique non conforme sert quand même ses termes lisibles à la complétion et à la définition, et l'anomalie est signalée à part ; un lexique illisible donne une erreur (dit)
- **Réutiliser** : `chemin_global()`, `chemin_local()` et `Terme.definition` existent déjà (dépôt: skills/lexique/scripts/lexique.py)

## Incertitudes à lever en plan

— aucune
