+++
id = "semence-de-test-reseed-porte-un-preremplissage"
title = "La semence partagée de test_reseed.py porte un préremplissage que ses tests ne demandaient pas"
date = 2026-09-06
source = "chantier description-obligatoire-partout, audit de clôture e441337, R2 — clos avec la réserve"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/list-dir/scripts/tests/test_reseed.py` définit une constante `SEMENCE` que tous ses tests
partagent. Trois d'entre eux simulaient « une clé supprimée localement » en retirant la
`description` de `[fields.title]` — devenue non supprimable depuis que la clé est exigée. Le
chantier `description-obligatoire-partout` a ajouté à ce champ une clé facultative dédiée,
`text = "titre par défaut"`, et fait porter la suppression sur elle.

C'est le seul endroit du chantier où une fixture est modifiée au-delà de l'ajout d'une
`description`. Un **préremplissage** est ainsi introduit dans une semence dont d'autres tests du
même fichier se servent pour créer des éléments : ils héritent d'un `title` prérempli qu'ils ne
demandaient pas.

## Pourquoi c'est gênant

Un préremplissage n'est pas neutre — il fait échapper le champ aux marqueurs, et
`validate --filled` cesse de le réclamer (`format.md`, « Un champ prérempli est une valeur
ordinaire »). Les tests de `reseed` qui créent des éléments depuis `SEMENCE` s'exécutent donc
sur un cas de figure plus permissif que celui qu'ils croient couvrir.

Mode de défaillance : un futur test de `reseed` écrit contre cette semence passe au vert parce que
`title` est prérempli, et masque une régression sur le marquage des champs obligatoires. Rien ne
signale que la clé n'est là que pour donner prise à une suppression.

## Pour solder

Sortir la clé supprimable de la semence partagée : donner aux trois tests de suppression locale
leur propre contrat, ou porter la suppression sur un champ que les autres tests n'utilisent pas.
Vérifier que `uv run --with pytest pytest skills/list-dir/scripts/tests -q` reste au vert et que
`SEMENCE` ne porte plus ni `text` ni `command`.

## Assumé

Le report est délibéré et daté du 2026-09-06. La substitution était nécessaire — sans elle, trois
tests échouaient sur un contrat devenu invalide avant d'atteindre le comportement visé — et le
brief interdisait explicitement de remanier les fixtures à cette occasion.
