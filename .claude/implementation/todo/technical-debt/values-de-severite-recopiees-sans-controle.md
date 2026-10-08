+++
id = "values-de-severite-recopiees-sans-controle"
title = "Les `values` de `severite` sont recopiées dans quatre définitions, sans contrôle qui les rapproche"
date = 2026-10-08
severite = "avertissement"
chantier = "registre-de-dette-severite-chantier-pin"
reference = "R15"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

L'échelle `inconnue, note, avertissement, majeur, critique` est écrite dans les contrats de
`technical-debt`, `technical-debt-solde`, `technical-debt-ecarte` et du patron `review`. Aucun
contrôle ne vérifie qu'elles restent identiques ; `dette.md` assume cette limite.

## Pourquoi c'est gênant

Une échelle changée dans une seule définition laisse une revue écrire une valeur que le registre
refuse, ou une entrée sortir vers une liste qui ne connaît plus sa sévérité. `validate` le verrait,
mais après coup, sur les entrées déjà écrites.

## Pour solder

Les quatre définitions tirent l'échelle d'une source unique, ou `check_pipeline.py` refuse deux
échelles différentes.

## Assumé

<OPTIONNEL>
