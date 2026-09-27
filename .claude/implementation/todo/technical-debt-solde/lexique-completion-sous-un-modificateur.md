+++
id = "lexique-completion-sous-un-modificateur"
title = "La complétion de `:Lexique` ne propose rien derrière un modificateur de commande"
date = 2026-09-27
source = "Identifié par `lexique-nvim`, R8 du rapport d'audit de clôture."
+++

## Constat

La complétion de `skills/lexique/nvim/lexique.lua` isole le texte tapé en supposant que
`Lexique` est le premier mot de la ligne de commande. Derrière un modificateur, elle ne rend
rien, alors que la commande elle-même s'exécute.

Établi par : `getcompletion("silent Lexique Sig", "cmdline")` → `{}`, audit de clôture de
`lexique-nvim` (`a30c7ce`).

## Pourquoi c'est gênant

Une complétion muette passe pour une absence de terme : l'utilisateur croit le lexique vide ou
le terme inexistant.

## Pour solder

Isoler l'argument à partir de la position du nom de commande dans la ligne, non de son début ;
vérifier par `getcompletion("silent Lexique Sig", "cmdline")` → `{ "Signal de dérive" }`. À faire
dans la version intégrée à `~/.config/nvim`, qui reprendra ce code.

## Assumé

Reporté à la clôture de `lexique-nvim` : aucun critère ne le demandait, et le code sera repris à
l'intégration.
