+++
id = "clause-arbre-propre-sans-le-plan"
title = "La clause « arbre propre » du tracker ne couvre pas le plan"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, journal du suivi."
reviewed = 2026-08-17
category = "pertinent"
+++

## Constat

l'Étape 2 d'`implementation-tracker` refuse de créer un chantier si l'arbre n'est pas
propre, avec une exception explicite pour les `*.brief.md` produits par `intent-brief`. Or le flux
normal produit **aussi** un plan non suivi dans `.claude/plans/`, que la clause ne mentionne pas.

**Constaté** à l'ouverture de ce chantier même : `git status` remontait le brief *et* `.claude/plans/`,
et il a fallu décider hors procédure que le second relevait de la même logique que le premier.

## Pourquoi c'est gênant

la règle écrite dit d'arrêter là où le flux normal du pipeline exige de
continuer. Chaque ouverture de chantier rejouera l'arbitrage, et un modèle qui suit la lettre
refusera de démarrer.

## Pour solder

étendre l'exception au plan dans l'Étape 2 du tracker.

## Assumé

<OPTIONNEL>
