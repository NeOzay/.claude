+++
id = "session-dump-ecart-ambigu-dans-skill-md"
title = "`session-dump/SKILL.md` : la règle d'écart se lit dans deux sens et la session en cours semble y échapper"
date = 2026-10-12
severite = "note"
chantier = "affiner-session-dump"
reference = "R1"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Dans `skills/session-dump/SKILL.md`, section « Ce qu'elle écrit », la phrase « par session
principale que les règles d'écart ci-dessous ne retiennent pas » se lit dans deux sens : « retenir »
au sens de « saisir » (sens voulu) ou de « garder » (sens contraire). Plus bas, « La session en
cours y figure, partielle » suit une phrase sur les sessions écartées : le « y » n'a plus
d'antécédent clair et semble dire que la session en cours échappe aux motifs, alors que
`motif_d_ecart` la juge comme les autres. Relevé à l'audit `01-be6978c`.

## Pourquoi c'est gênant

Un lecteur peut croire qu'une session en cours n'est jamais écartée, ou comprendre la règle à
l'envers. Le tableau des motifs lève l'ambiguïté plus bas, mais le lecteur qui s'arrête à la
première phrase repart avec le mauvais sens.

## Pour solder

Écrire « par session principale qu'aucune règle d'écart ci-dessous n'écarte », et rattacher la
session en cours aux dumps : « Le dump de la session en cours, quand elle n'est pas écartée, est
partiel. » Relancer `uvx rumdl fmt --check skills/session-dump/SKILL.md`.

## Assumé

<OPTIONNEL>
