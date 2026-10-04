+++
id = "noms-du-suivi-valides-par-tags"
title = "Les noms du champ `skills` d'un Suivi sont validés par une fonction nommée `_tags`"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R3"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Dans `skills/shadow-skill/scripts/shadow_skill.py`, `noms_du_suivi` valide la liste de noms du champ
`skills` d'un Suivi par `_tags`. La docstring de `_tags` parle d'« une liste de chaînes », mais son
nom dit « tags ». Le comportement est juste.

## Pourquoi c'est gênant

Le lecteur de `noms_du_suivi` croit qu'on y lit des tags. Une évolution de la validation des tags
(format, registre) s'appliquerait alors aux noms de skills sans que personne l'ait voulu.

## Pour solder

Renommer `_tags` d'après ce qu'elle vérifie (une liste de chaînes), ou donner aux noms du Suivi leur
propre fonction de validation.

## Assumé

<OPTIONNEL>
