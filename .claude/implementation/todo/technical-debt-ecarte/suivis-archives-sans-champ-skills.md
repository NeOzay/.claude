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

## Pourquoi c'est gênant

Un contrôle global de `done/` les signalerait comme fautifs, et masquerait parmi eux un vrai défaut
d'archive.

## Pour solder

Ajouter `skills = []` aux archives, ou exclure `done/` de tout contrôle par la Semence courante.

## Assumé

Arbitrage de l'utilisateur pendant le Chantier : les archives restent intactes.
