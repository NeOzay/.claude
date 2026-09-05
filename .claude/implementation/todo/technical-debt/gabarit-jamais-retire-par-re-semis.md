+++
id = "gabarit-jamais-retire-par-re-semis"
title = "un gabarit ne peut pas être retiré par un re-semis, et rien ne le dit"
date = 2026-09-04
source = "chantier peremption-contrat, audit de clôture ddebb2b, R8"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`provenance._poser` écrit les gabarits fusionnés mais n'efface jamais : un fichier présent dans
`.list/templates/` et absent de la semence y reste, et aucun re-semis ne peut le retirer.

Le comportement est cohérent avec la règle générale — ce que la semence ne porte plus est gardé
sur place — mais la documentation ne l'énonce que pour les clés du contrat. La table de fusion
de `provenance.md` parle de clés ; la ligne des gabarits, juste au-dessus, ne dit rien de la
suppression.

## Pourquoi c'est gênant

Un gabarit retiré d'une définition parce qu'il était faux continue d'exister dans toutes les
listes qu'elle a semées, et `derive` continue de l'accepter. Le rattrapage a l'air complet et
ne l'est pas.

Mode de défaillance : une liste dérivée d'un gabarit que sa définition a désavoué, sans qu'une
seule commande échoue.

## Pour solder

Documenter la règle côté gabarits dans `provenance.md`, section « `reseed` : rattraper sur ordre »,
et vérifier par un test qu'un gabarit absent de la semence survit à `reseed`. Si le retrait doit
devenir possible, il lui faut un drapeau explicite, sur le modèle du `--drop` de `migrate`.

## Assumé

Le chantier a traité les clés du contrat et laissé les gabarits sur la règle par défaut. Rien
n'a été constaté de faux, seulement de non écrit.
