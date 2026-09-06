+++
id = "message-de-refus-de-la-racine-ne-nomme-pas-la-racine"
title = "Le refus d'un contrat sans description racine ne dit pas que c'est la racine"
date = 2026-09-06
source = "chantier description-obligatoire-partout, audit de clôture e441337, R1 — clos avec la réserve"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Depuis le chantier `description-obligatoire-partout`, `list-dir validate` refuse un contrat dont
la clé `description` manque à trois endroits. Deux des trois messages nomment l'endroit :
`champ « id » — « description » manquante`, `section « A » — « description » manquante`. Celui de
la racine ne porte que le chemin du fichier : `« description » manquante — la clé se déclare,
fût-elle vide`.

`skills/list-dir/references/format.md` promet pourtant, dans le paragraphe qui énonce la règle :
« Elle manque : le contrat est refusé, en nommant l'endroit. »

## Pourquoi c'est gênant

Sur un contrat qui déclare par ailleurs des champs et des sections, le lecteur du message doit
deviner lequel des trois endroits est visé — et son premier réflexe sera de relire les champs,
puisque ce sont eux que les deux autres messages nomment. La prose livrée et le code livré
divergent sur le point précis que la règle vend.

Mode de défaillance : quelqu'un ajoute `description = ""` à tous ses champs, relance `validate`,
obtient le même message, et conclut que l'outil se répète au lieu de regarder la racine.

## Pour solder

Faire dire au message qu'il s'agit de la racine du contrat, sur le modèle des deux autres — par
exemple `contrat — « description » manquante`. Vérifier par un contrat neuf portant des champs
tous documentés et pas de `description` racine, et par le test
`test_contrat_sans_description_est_refuse` de `skills/list-dir/scripts/tests/test_contract.py`,
dont l'assertion doit alors porter sur le nouveau libellé.

## Assumé

Le report est délibéré et daté du 2026-09-06 : l'écart a été relevé à l'audit de clôture, jugé de
coût faible, et l'utilisateur a choisi de clore avec plutôt que de rouvrir le code après l'audit.
