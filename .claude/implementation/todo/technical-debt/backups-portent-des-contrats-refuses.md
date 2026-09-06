+++
id = "backups-portent-des-contrats-refuses"
title = "Quatre contrats de .list/backup/ sont désormais refusés par validate"
date = 2026-09-06
source = "chantier description-obligatoire-partout, audit de clôture e441337, R5 — dette induite"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

L'audit `tomllib` de tous les contrats du dépôt, joué à la clôture du chantier
`description-obligatoire-partout`, en trouve quatre que `validate` refuserait : ceux des
`.list/backup/` des trois registres de dette, et le `templates/review.toml` de `technical-debt`.
Tous pour la même raison — un `[fields.id]` sans `description`.

C'est exactement le périmètre que le plan a délibérément laissé intact : un backup est
l'instantané de ce que le dernier `reseed` a remplacé (`format.md`, « ce que le dernier `reseed` a
remplacé »), et le corriger le ferait mentir. Rien ne le relit aujourd'hui : `provenance.py` ne
fait qu'y écrire.

## Pourquoi c'est gênant

Le coût est nul tant que la propriété « rien ne relit un backup » tient. Elle n'est garantie par
aucun test : c'est une propriété du code d'aujourd'hui, pas un invariant déclaré.

Mode de défaillance : le jour où une commande viendrait relire un backup — une restauration, une
comparaison avant re-semis — elle buterait sur un contrat refusé, et le message parlerait d'une
`description` manquante sans dire qu'il s'agit d'un instantané légitimement périmé. Le lecteur
conclurait à un backup corrompu.

## Pour solder

Décider ce qu'un backup doit garantir. Deux issues : soit `.list/backup/` est déclaré hors du
champ de toute lecture, et le dire dans `skills/list-dir/references/provenance.md` avec un test
qui l'établit ; soit toute lecture d'un backup passe par un chemin qui sait qu'un contrat archivé
peut être périmé et le dit dans son message.

## Assumé

Le report est délibéré et daté du 2026-09-06 : ne pas corriger un backup est le choix argumenté du
chantier, et l'entrée existe pour que ce choix reste su, pas pour être contesté.
