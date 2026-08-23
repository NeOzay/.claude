+++
id = "revue-amende-le-pipeline-sans-brief"
title = "Une revue peut amender les règles du pipeline sans brief, plan ni audit"
date = 2026-08-17
source = "Identifié par `revue-dette`, R19 du troisième rapport d'audit."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

l'Étape 3 de `debt-review` fait écrire, **pendant la passe**, la règle qu'un arbitrage
produit, directement dans `dette.md`, `categories.md` ou `SKILL.md`. C'est l'inverse de ce que le
skill impose pour un correctif de code, qui doit passer par `/implementation-tracker` : un
amendement de règle entre au dépôt sans cadrage, sans plan relu, sans audit, et sans borne écrite
sur son ampleur. Rien ne distingue la phrase d'une revue d'une réécriture de section.
Établi par : la première passe réelle a produit deux règles de cette façon — l'interdiction des
numéros de ligne et la section *Corriger une entrée* — soit `git diff --stat 643581d 69fd11c --
skills` → 3 fichiers, 45 insertions.

## Pourquoi c'est gênant

c'est la seule porte du dépôt par laquelle une règle du pipeline entre
sans le dispositif qui existe pour ça. Elle est étroite et surveillée par un humain qui arbitre,
mais elle n'a pas de plafond : la même phrase autorise « ajouter une ligne à un gabarit » et
« réécrire la tenue des registres ».

## Pour solder

écrire la borne dans `SKILL.md` : ce qu'un arbitrage de revue peut amender seul
(une règle qui tient en un paragraphe, dans une section existante) et ce qui bascule en chantier
`/implementation-tracker` (section neuve, changement de gabarit, tout ce qui touche un script).

## Assumé

choix arbitré et daté au journal du chantier. L'alternative — ouvrir un chantier pour
chaque règle — était pire : les corrections d'entrées auraient été écrites sans la règle qui les
autorise, ou reportées jusqu'à ce que personne ne les fasse.
