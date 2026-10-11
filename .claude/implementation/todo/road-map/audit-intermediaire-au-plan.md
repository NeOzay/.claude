+++
id = "audit-intermediaire-au-plan"
title = "Décider au Plan quand un audit intermédiaire est pertinent, à la place du seuil de 400 lignes"
date = 2026-10-11
source = "Brief du Chantier `refonte-de-l-audit`, qui l'exclut de son périmètre"
+++

## À faire

L'audit intermédiaire est aujourd'hui proposé dès que le diff de la branche dépasse 400 lignes.
L'utilisateur juge ce seuil peu utile : la pertinence d'un audit intermédiaire se décide au Plan,
Étape par Étape, et non sur un volume de diff. Reste à dire ce que le Plan porte — quelles Étapes
appellent un audit, et pourquoi —, comment plan-reviewer le relit, et ce que devient le seuil.

## Références

- `skills/implementation-tracker/references/audit.md` : « Quand auditer », le seuil de 400 lignes
  et `git diff --shortstat <base>...<slug>`
- `skills/implementation-tracker/references/creation.md`, point 2 : la construction du Plan
- `agents/plan-reviewer.md` : ce que la relecture du Plan juge
- Brief `.claude/implementation/refonte-de-l-audit.brief.md`, `## Hors-périmètre`
