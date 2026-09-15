+++
id = "suivi-commite-en-retard-sur-son-commit-d-etape"
title = "Le suivi commité dans un commit d'étape annonce ce même commit comme restant à faire"
date = 2026-09-15
source = "chantier `git-smart-commit-trois-commits`, R18 et R20 du rapport d'audit"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`implementation-tracker` (Étape 4, « Étape terminée ») coche l'étape puis propose le commit d'étape,
qui embarque le suivi. Le suivi ne peut pas citer le SHA ni le tag du commit qui le contient : sa
« Prochaine action » le donne comme à faire, et « Dernier audit » ou le journal restent un commit en
arrière. Constaté deux fois de suite sur `git-smart-commit-trois-commits` : `138b35f` (`AE7`, R18) et
`9513ccd` (`AE8`, R20).

## Pourquoi c'est gênant

Chaque audit relève l'écart comme un défaut, et chaque clôture risque d'archiver un suivi dont la
prochaine action et le dernier audit sont faux, si personne ne le met à jour avant le commit de
finalisation.

## Pour solder

Écrire la règle dans le tracker ou dans `etape.md` : la « Prochaine action » d'un suivi commité en
commit d'étape se rédige comme si ce commit était fait (« après `<L>E<n>` : … »), sans SHA ; le SHA et
le verdict d'audit s'inscrivent au commit suivant. Et dire à l'auditeur de ne pas le relever.
