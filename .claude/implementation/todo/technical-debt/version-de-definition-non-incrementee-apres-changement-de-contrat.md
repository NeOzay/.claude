+++
id = "version-de-definition-non-incrementee-apres-changement-de-contrat"
title = "Le contrat des trois définitions a changé sans que [origin].version bouge"
date = 2026-09-06
source = "chantier description-obligatoire-partout, audit de clôture e441337, R4 — dette induite"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le chantier `description-obligatoire-partout` a modifié le `contract.toml` des trois définitions
de `skills/implementation-tracker/list-dir/` — ajout d'une `description` à `[fields.id]` — en
laissant `[origin] version = 2` inchangé. C'est une décision assumée du plan : copies de travail
et semences de ce dépôt ont reçu les mêmes octets, ce que les `md5sum` de l'audit confirment.

Hors de ce dépôt, l'effet n'est pas nul. Une liste semée ailleurs depuis ces définitions avant le
changement porte un `[fields.id]` sans `description` : son contrat local est désormais refusé, et
la version identique n'annoncera aucune péremption.

## Pourquoi c'est gênant

L'effet se cumule avec `reseed-refuse-un-contrat-local-invalide` : le contrat local est invalide,
`validate` le refuse, `reseed` refuse de le rattraper, et le mécanisme qui aurait dit « ta
définition a évolué » se tait puisque le numéro n'a pas bougé. Aucun des trois signaux ne joue.

Mode de défaillance : sur une telle machine, la seule issue est l'édition manuelle d'un fichier
dont rien n'a dit qu'il fallait le toucher. Le coût est purement externe et différé — aucune liste
de ce genre n'existe dans ce dépôt, l'audit `tomllib` de l'auditeur le confirme.

## Pour solder

Trancher la règle et l'écrire dans
`skills/list-dir/references/provenance.md` : un changement du texte d'une définition incrémente-t-il
`version` ? Si oui, incrémenter les trois définitions et propager aux copies et semences de ce
dépôt, en vérifiant par `md5sum` que les triplets restent identiques.

## Assumé

Le report est délibéré et daté du 2026-09-06 : aucune règle documentée n'impose aujourd'hui
l'incrément, et le plan a préféré ne pas en inventer une au détour d'un chantier qui portait sur
autre chose.
