+++
id = "merge-aplatit-les-labels-title"
title = "merge rend les labels title au rang de leur section"
date = 2026-10-17
severite = "avertissement"
chantier = "gabarit-sections-structurees"
reference = "R3"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`list-dir merge` rend chaque section d'un Élément sous `### <titre>` (`listdir/store.py`,
`merge_text`). Les labels `forme = "title"` d'une section, écrits en `###` dans l'Élément, y
gardent ce rang : ils deviennent des titres de même niveau que leur section. Rien ne le signale, et
la prose de list-dir n'en dit rien.

## Pourquoi c'est gênant

La hiérarchie de l'aggloméré se perd sans erreur : un label se lit comme une section sœur. Le
coût vient avec la première List-dir dont un Contrat déclare une section `forme = "title"`.

## Pour solder

Décaler dans `merge` les titres d'une section `title` d'un rang, hors blocs de code comme le
recomptage, avec un test ; à défaut, nommer la limite dans `skills/list-dir/references/format.md`.

## Assumé

Limite admise par le Plan de `gabarit-sections-structurees`, à porter en dette à la Clôture :
aucune List-dir ne déclare encore de labels `title`.
