+++
id = "correctif-passation-e11-non-audite"
title = "La règle de fraîcheur de la section `## Passation` est livrée sans audit"
date = "2026-10-04"
source = "chantier `contexte-tracker`, clôture du 2026-10-04, arbitrage de l'utilisateur"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le quatrième audit de clôture (`50071c4`) a rendu RÉSERVES (R17, R18) sur la règle qui juge, à
la reprise, si la section `## Passation` est à jour. Leur correctif, l'Étape 11 (`0efba8f`), a été
clos sans nouvel audit, sur décision de l'utilisateur. Chacun des trois correctifs précédents de
cette règle avait ouvert un nouveau constat.

## Pourquoi c'est gênant

La règle décide si la reprise restitue la section comme actuelle. Un défaut non vu ferait
restituer une Passation périmée, ou taire une Passation fraîche.

## Pour solder

Auditer la Phase 3 de `skills/implementation-tracker/SKILL.md` sur les chemins de Passation :
acceptée puis coupée, acceptée puis continuée, refusée, après un audit intermédiaire.

## Assumé

Clos sans audit le 2026-10-04 : les réserves des audits successifs s'amenuisaient, et le défaut
connu ne jouait que dans un sens sûr.
