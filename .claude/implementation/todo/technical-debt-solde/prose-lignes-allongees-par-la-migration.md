+++
id = "prose-lignes-allongees-par-la-migration"
title = "Des lignes de `prose.md` dépassent 100 colonnes depuis la réécriture de ses liens"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R4"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

La migration de `skill-convention` a réécrit les liens de
`shadow-skills/skill-convention/references/prose.md` (`../../` devient `../../../skills/`) sans
rejustifier les paragraphes. Au 2026-10-04, une dizaine de lignes y dépassent 100 colonnes, alors
que leurs voisines s'arrêtent avant.

## Soldé le

**2026-10-04, hors chantier** — `rumdl fmt`, adopté comme formateur Markdown du dépôt, réenroule
à 100 colonnes tout paragraphe dont une ligne dépasse (`.rumdl.toml`, section `[MD013]`). Le
reformatage du dépôt (`style: appliquer rumdl fmt au Markdown du dépôt`) a rejustifié les
paragraphes de `prose.md`, et `rumdl fmt --check` empêche désormais l'écart de revenir.

Établi par :

```
$ python3 (len(ligne) > 100, en caractères) sur shadow-skills/skill-convention/references/prose.md
prose.md : 0 lignes > 100 caractères, dont 0 hors tableaux et blocs de code

$ uvx rumdl check --enable MD013 shadow-skills/skill-convention/references/prose.md
Success: No issues found in 1 file
```

## Pourquoi c'est gênant

Le fichier qui énonce les conventions de prose du dépôt ne les tient plus dans sa forme. Le rendu
n'est pas touché, mais un diff futur sur ces paragraphes mélangera rejustification et changement de
fond.

## Pour solder

Rejustifier les paragraphes concernés à 100 colonnes.

## Assumé

<OPTIONNEL>
