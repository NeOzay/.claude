+++
id = "plans-archives-nom-reattribuable"
title = "Les plans archivés portent un nom réattribuable, sans garde-fou à l'écrasement"
date = 2026-08-14
source = "Identifié par `dette-technique`, incident constaté pendant sa propre clôture."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

la boucle d'archivage de `cloture.md` renommait le plan `<AAAA-MM-DD>-<son nom
généré>`. Or le harness réattribue ces noms (`linked-toasting-graham.md`) d'un chantier à l'autre.
À la clôture de `dette-technique`, le plan d'`audit-integre` a été **écrasé** : `git mv` refuse
d'écraser, mais le repli `mv` de la boucle, lui, écrase sans un mot. Détecté à la relecture de
`ls done/`, restauré depuis `HEAD`.

**Traité** — le plan est désormais archivé `<AAAA-MM-DD>-<slug>.plan.md`, et chaque déplacement est
précédé d'un `[ -e "$t" ]` qui refuse au lieu d'écraser (`cloture.md`, point 4).

**Ce qui reste en dette** — les archives déjà écrites gardent l'ancienne convention :
`done/2026-08-14-linked-toasting-graham.md` est le plan d'`audit-integre`, mais rien dans son nom
ne le dit. Et le champ `plan:` de `done/2026-08-14-audit-integre.md` continue de pointer vers
`.claude/plans/linked-toasting-graham.md`, chemin qui a depuis désigné deux chantiers différents.

## Soldé le

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — l'archive mal nommée a été renommée
d'après son slug, et les deux champs `plan:` pointent chacun vers leur propre plan. La règle de
nommage est au contrat, section « Arborescence et nommage ».
Établi par : `ls .claude/implementation/done/ | grep plan` → `2026-08-14-audit-integre.plan.md` et
`2026-08-14-dette-technique.plan.md` ; `grep -h '^plan:' .claude/implementation/done/*.md` → deux
chemins distincts, chacun vers le plan de son chantier.

## Pourquoi c'est gênant

<OPTIONNEL>

## Pour solder

renommer l'archive existante en `2026-08-14-audit-integre.plan.md` et réécrire le
champ `plan:` correspondant, en même temps que l'entrée sur les champs obsolètes ci-dessus.

## Assumé

<OPTIONNEL>
