+++
id = "step-implementer-sans-shadow-skills"
title = "`step-implementer` ne reçoit pas les Shadow-skills du Suivi"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R7"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le Suivi d'un Chantier porte dans son champ `skills` les Shadow-skills retenus au brief et au plan.
`agents/step-implementer.md` n'en dit rien, et implementation-tracker ne les lui transmet pas à la
délégation d'une Étape.

## Pourquoi c'est gênant

Une Étape déléguée s'exécute sans les conventions que le Chantier a jugées nécessaires : l'exécutant
écrit, par exemple, un skill sans `skill-convention`. L'écart ne se voit qu'à la relecture du diff.

## Pour solder

Faire lancer `shadow-skill depuis-suivi <slug>` puis `shadow-skill charge` par `step-implementer` au
début de son Étape, ou faire transmettre les noms par l'appelant.

## Assumé

<OPTIONNEL>
