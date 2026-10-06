+++
id = "lexique-local-tronque-par-le-hook-session"
title = "Un lexique local de plus de 10 000 caractères est tronqué par le hook `SessionStart`"
date = 2026-10-05
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, constat du Journal du 2026-10-05, vérifié par l'utilisateur sur claude-translator"
+++

## Constat

Claude Code remplace tout `additionalContext` de plus de 10 000 caractères (`HXo = 1e4` dans le binaire
2.1.289, non configurable) par un aperçu de 2 Ko et range le reste dans un fichier. Constaté le 2026-10-05 :
le lexique local de `claude-translator`, 12 973 caractères, arrive tronqué à la session principale.

## Pourquoi c'est gênant

Une session principale ne voit que le début d'un gros lexique local, donc emploie des termes qu'elle
ignore, et rien ne le dit. Le mod du Chantier contourne le plafond pour les sous-agents, pas pour la
session.

## Pour solder

Verser le lexique local à la session par une voie sans plafond (un mod, comme pour les sous-agents), ou
le garder sous 10 000 caractères, et faire dire à `lexique liste` qu'il dépasse.
