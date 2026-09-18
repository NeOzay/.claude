+++
id = "intent-brief-description-sans-limite"
title = "La `description` d'`intent-brief` ne dit pas ce que la skill ne fait pas"
date = 2026-09-18
source = "chantier `skill-convention`, audit de clôture R1 (`cea0665`)"
+++

## Constat

La convention « La description dit quoi, quand, et ce que la skill ne fait pas »
(`skills/skill-convention/references/prose.md`) demande une limite en une phrase négative. La
`description` de `skills/intent-brief/SKILL.md` se termine sur « Alimente implementation-tracker. »
et ne porte aucune limite, alors qu'`intent-brief` s'arrête explicitement au brief validé : il ne
planifie pas et ne confronte pas.

Le même écart a donné lieu à l'entrée `emmylua-ls-description-sans-limite`.

## Pourquoi c'est gênant

La `description` est tout ce que le modèle voit avant de déclencher la skill. Sans limite,
`intent-brief` se déclenche sur des demandes de planification qu'elle ne sait pas traiter, et le
travail repart du mauvais endroit.

## Pour solder

Ajouter une phrase de limite à la `description` d'`intent-brief` — « Ne planifie pas. » —, dans un
chantier qui a le droit d'éditer les skills existantes.
