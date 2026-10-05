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

## Écartée le

> **2026-10-05 — non pertinent** — `step-implementer` et la délégation d'Étape ont été retirés du
> pipeline par le Chantier `retouches-et-modele-du-chantier` : plus aucun agent n'exécute une Étape
> hors de la session, qui charge elle-même les Shadow-skills du Suivi à la reprise.
> Établi par : `test -e agents/step-implementer.md; echo $?` → `1`, l'agent n'existe plus.

## Pourquoi c'est gênant

Une Étape déléguée s'exécute sans les conventions que le Chantier a jugées nécessaires : l'exécutant
écrit, par exemple, un skill sans `skill-convention`. L'écart ne se voit qu'à la relecture du diff.

## Pour solder

Faire lancer `shadow-skill depuis-suivi <slug>` puis `shadow-skill charge` par `step-implementer` au
début de son Étape, ou faire transmettre les noms par l'appelant.

## Assumé

<OPTIONNEL>
