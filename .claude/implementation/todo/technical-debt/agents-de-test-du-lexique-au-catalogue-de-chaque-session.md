+++
id = "agents-de-test-du-lexique-au-catalogue-de-chaque-session"
title = "Trois agents de test du lexique figurent au catalogue de chaque session"
date = 2026-10-05
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, R9"
+++

## Constat

`agents/lexique-test-claude-md.md`, `lexique-test-isole.md` et `lexique-test-injecte.md` sont des
agents utilisateur : leurs trois descriptions entrent au contexte de chaque session, dans tous les
projets, alors qu'ils ne servent qu'à vérifier le mod.

## Pourquoi c'est gênant

Trois descriptions au contexte de chaque session, et un risque de lancement par erreur malgré leur
mention « jamais pour une tâche ».

## Pour solder

Les retirer de `agents/` une fois le mod éprouvé, ou les ranger sous un dossier de test hors du
catalogue, chargé à la demande.

## Assumé

Versionnés dans `agents/` par choix de l'utilisateur, pour rejouer la vérification réelle à chaque
changement du mod.
