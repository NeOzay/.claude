+++
id = "prose-lignes-allongees-par-la-migration"
title = "Des lignes de `prose.md` dépassent 100 colonnes depuis la réécriture de ses liens"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R4"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

La migration de `skill-convention` a réécrit les liens de `shadow-skills/skill-convention/references/prose.md` (`../../` devient `../../../skills/`) sans rejustifier les paragraphes. Au 2026-10-04, une dizaine de lignes y dépassent 100 colonnes, alors que leurs voisines s'arrêtent avant.

## Pourquoi c'est gênant

Le fichier qui énonce les conventions de prose du dépôt ne les tient plus dans sa forme. Le rendu n'est pas touché, mais un diff futur sur ces paragraphes mélangera rejustification et changement de fond.

## Pour solder

Rejustifier les paragraphes concernés à 100 colonnes.

## Assumé

<OPTIONNEL>
