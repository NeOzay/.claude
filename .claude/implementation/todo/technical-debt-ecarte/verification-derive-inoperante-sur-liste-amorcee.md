+++
id = "verification-derive-inoperante-sur-liste-amorcee"
title = "La vérification de l'étape 7 du plan semences-de-listes imprime ÉCHEC derive"
date = 2026-08-30
source = "chantier semences-de-listes, audit R6"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

Le plan du chantier `semences-de-listes` déclare à son étape 7 une boucle qui amorce les trois
registres puis lance `list-dir derive` sur `technical-debt`. Rejouée telle qu'elle est écrite, elle
imprime `ÉCHEC derive` : `derive` refuse une liste sans élément — « aucun élément — il n'y a rien à
projeter » — et une liste fraîchement amorcée est vide par construction.

Le critère que cette vérification servait est pourtant atteint : les gabarits suivent bien
l'amorçage, ce qui a été établi autrement, en créant une entrée avant de projeter.

## Pourquoi c'est gênant

Une commande de vérification qui échoue là où le critère est atteint est pire qu'une absence de
vérification : elle apprend à ignorer sa propre sortie. Le plan est archivé avec le chantier et sert
de référence à qui reprend le sujet ; il porte donc une commande dont on sait qu'elle ment, sans
que rien ne le dise à côté.

Le comportement de `derive` n'est pas en cause — refuser de projeter zéro élément est délibéré et
documenté. C'est la vérification qui est mal posée.

## Pour solder

Corriger la boucle dans le plan archivé pour qu'elle crée une entrée avant de projeter, ou qu'elle
attende un code non nul de `derive` sur une liste vide et le dise.

Plus largement : une commande de vérification s'écrit **après** l'avoir exécutée une fois. Celle-ci
a été rédigée depuis la lecture du code, ce qui suffit à produire une commande plausible et fausse.

## Assumé

Le chantier a été clos avec cette réserve, l'arbitrage ayant jugé que la correction du plan
archivé ne valait pas de rouvrir le chantier.
