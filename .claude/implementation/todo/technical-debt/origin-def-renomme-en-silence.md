+++
id = "origin-def-renomme-en-silence"
title = "un reseed sans option accepte une semence qui se renomme"
date = 2026-09-04
source = "chantier peremption-contrat, audit de clôture ddebb2b, R5"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le contrôle de discordance de nom ne s'applique qu'au nom **écrit** par l'appelant : dans
`commands/reseed.py`, `expected_name` reçoit la valeur de `--def`, et reste vide quand la
semence est désignée par l'`origin.def` de la liste — c'est-à-dire dans le cas courant, celui
d'un `list-dir reseed <liste>` sans option.

Une définition rangée sous le répertoire `A` mais dont le contrat déclare `def = "B"` renomme
alors l'estampille de la liste en `B` : la clé `origin.def` locale égale la base, donc la
semence gagne. Reproduit à l'audit : après le re-semis, le `validate` suivant rend « définition
introuvable dans les quatre rangs — péremption invérifiable ». Par `--from`, la version peut en
outre reculer.

Le changement figure dans le rapport (`origin.def — reprise de la semence`), donc il n'est pas
muet ; mais rien ne le distingue d'un apport anodin.

## Pourquoi c'est gênant

L'estampille est ce qui rattache une liste à sa définition. La laisser changer de nom par la
voie la plus employée coupe la liste de sa semence, et le seul symptôme est un avertissement
qui accuse l'installation plutôt que le re-semis qui l'a causé.

Mode de défaillance : la liste cesse d'être rattrapable, et le prochain lecteur conclut que le
skill n'est pas installé sur sa machine.

## Pour solder

Faire porter le contrôle sur le nom **que la liste déclare** quand aucune option n'est donnée :
si `origin.def` de la liste et `origin.def` de la semence diffèrent, refuser en nommant les
deux, et exiger un `--def` explicite pour entériner le renommage. Vérifier par un test qui
renomme le contrat d'une définition et attend un refus.

## Assumé

Cas de bord — il suppose une définition dont le répertoire et le contrat se contredisent. Le
contrôle existe déjà, il ne couvre simplement pas cette voie.
