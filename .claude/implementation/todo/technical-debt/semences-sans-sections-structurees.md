+++
id = "semences-sans-sections-structurees"
title = "Les Semences brief et suivi ne déclarent aucune section structurée"
date = 2026-10-17
severite = "note"
chantier = "gabarit-sections-structurees"
reference = "R1"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le Chantier `gabarit-sections-structurees` livre `type = "motif"` et `type = "label"`, mais
aucune Semence livrée ne les déclare. Les sections `Étapes`, `Dettes écartées`, les critères du
Brief, `État courant`, `Objectif et périmètre` et `Passation` gardent leur format en prose, dans la
`description` de `skills/gabarit/gabarit/brief/contract.toml` et
`skills/gabarit/gabarit/suivi/contract.toml`. Une ligne d'Étape mal formée dans un Suivi passe
encore `gabarit check` (rejoué à l'audit 01, code 0).

## Pourquoi c'est gênant

Le symptôme d'origine reste entier sur les fichiers réels : une ligne mal formée n'échoue qu'à
`audit pose`, ou jamais si elle est ignorée, et le format existe toujours deux fois, en prose et
dans les regex de `rapport_audit`.

## Pour solder

Le Chantier d'intégration : déclarer le motif ou les labels de ces sections dans les Semences
`brief` et `suivi`, faire passer `rapport_audit` par `section_values`, puis vérifier qu'une ligne
d'Étape mal formée fait échouer `gabarit check`.

## Assumé

Hors-périmètre du Brief de `gabarit-sections-structurees` : l'adoption est un Chantier à part,
qui touche d'autres fichiers.
