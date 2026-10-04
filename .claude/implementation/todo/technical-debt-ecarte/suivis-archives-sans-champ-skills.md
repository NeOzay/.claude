+++
id = "suivis-archives-sans-champ-skills"
title = "Les Suivis archivés ne passent plus `gabarit check --filled`"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R9"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le Chantier `shadow-skill` a rendu obligatoire le champ `skills` de la Semence `suivi`. Les quatre
Suivis archivés dans `done/` et estampillés `suivi` ne le portent pas, et échouent depuis à
`gabarit check --filled`.

## Écartée le

**2026-10-04 — pas une dette** — sur décision de l'utilisateur, une archive de `done/` n'a plus à
passer `gabarit check --filled` contre la Semence courante : elle relate le Chantier tel qu'il a été
clos, et ne se réécrit pas. Les quatre Suivis archivés sans `skills` sont conformes à cette règle.
Établi par :

```
$ grep -n "pas une dette" skills/implementation-tracker/references/contrat.md
59:Qu'une archive ne passe plus un contrat qui a évolué depuis n'est pas une dette. Le pipeline
```

## Pourquoi c'est gênant

Un contrôle global de `done/` les signalerait comme fautifs, et masquerait parmi eux un vrai défaut
d'archive.

## Pour solder

Ajouter `skills = []` aux archives, ou exclure `done/` de tout contrôle par la Semence courante.

## Assumé

Arbitrage de l'utilisateur pendant le Chantier : les archives restent intactes.
