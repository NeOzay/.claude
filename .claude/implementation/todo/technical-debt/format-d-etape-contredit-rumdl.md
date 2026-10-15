+++
id = "format-d-etape-contredit-rumdl"
title = "Le format d'Étape sur une ligne contredit le réenroulement de `rumdl`"
date = 2026-10-15
severite = "avertissement"
chantier = "solder-sept-dettes"
reference = "R2"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`references/contrat.md` d'implementation-tracker, « Format d'étape », écrit une Étape sur une
ligne, et `audit new` (`rapport_audit/pose.py`, motif `COCHEE`) lit la commande `— vérif:` sur
cette seule ligne. `.rumdl.toml` réenroule la prose à 100 colonnes, et ne l'exempte que pour
`done/` : `uvx rumdl fmt --check .` est donc rouge sur toute branche qui porte un Suivi actif, et
`rumdl fmt .` casserait les Étapes. La Base est verte parce qu'elle n'en porte aucun.

## Pourquoi c'est gênant

Un critère « `rumdl` vert » échoue sur chaque Chantier, et cote un bloquant d'office à l'audit :
c'est le R2 de l'audit `e2b506a` de `solder-sept-dettes`, écarté pour le Suivi. Qui suit la règle
d'`OUTILLAGE.md`, « `uvx rumdl fmt .` avant de commiter du Markdown », rend les Étapes illisibles
pour `audit new`, sans erreur.

## Pour solder

Exempter les Suivis actifs de MD013 dans `.rumdl.toml`, ou faire lire à `pose.py` une Étape
enroulée ; puis vérifier, sur une branche de Chantier, que `uvx rumdl fmt --check .` passe et que
`audit new` exécute encore chaque `vérif:`.

## Assumé

<OPTIONNEL>
