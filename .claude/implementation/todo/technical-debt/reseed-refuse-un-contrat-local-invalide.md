+++
id = "reseed-refuse-un-contrat-local-invalide"
title = "Une liste dont le contrat local est invalide n'est plus rattrapable par reseed"
date = 2026-09-06
source = "chantier description-obligatoire-partout, audit de clôture e441337, R3 — dette induite"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/list-dir/scripts/listdir/provenance.py` fait commencer `reseed` par un `load_contract` de
la liste visée, et abandonne si ce contrat est refusé. Or `reseed` est précisément la commande qui
remplace un contrat local par celui de sa définition.

Le chantier `description-obligatoire-partout` a rendu le cas atteignable : une liste dont le
`contract.toml` local a perdu une `description` — ou qui n'en a jamais eu, ayant été semée avant
la règle — est refusée par `validate`, et `reseed` refuse d'y toucher pour la même raison. La
seule voie de réparation automatique est fermée ; la correction devient manuelle.

## Pourquoi c'est gênant

La commande dont l'objet est de remettre un contrat en état exige que ce contrat soit déjà en
état. Le coût tombe exactement là où l'outil devrait servir : sur la liste la plus abîmée.

Mode de défaillance : un utilisateur constate un contrat périmé, lance `reseed` comme la
documentation l'y invite, reçoit un message d'erreur qui parle de la clé manquante et non de
l'impossibilité de re-semer, et n'a aucune indication qu'il doit éditer à la main le fichier que
la commande allait de toute façon écraser.

## Pour solder

Décider ce que `reseed` a réellement besoin de lire dans le contrat local avant de l'écraser — le
`[origin]` seul, vraisemblablement, pour savoir de quelle définition il relève — et ne valider que
cela. À défaut, faire dire au refus qu'il s'agit d'un contrat local irrécupérable et nommer la
correction manuelle. Vérifier sur une liste dont on a retiré une `description` du contrat local :
`list-dir reseed` doit la rattraper, ou dire pourquoi il ne le peut pas.

## Assumé

Le report est délibéré et daté du 2026-09-06. La conséquence a été relevée pendant le chantier et
inscrite au journal du suivi ; la traiter aurait touché `provenance.py`, hors du périmètre d'un
chantier borné à `contract.py` et à `format.md`.
