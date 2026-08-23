+++
id = "champs-plan-brief-audit-a-faux"
title = "Les champs `plan:` / `brief:` / `audit:` pointent à faux après archivage"
date = 2026-08-14
source = "Identifié par `audit-integre`, corollaire de R1 ; aggravation constatée par `dette-technique`."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

la clôture déplace suivi, brief, rapport et plan vers `done/` avec un préfixe de date
(`cloture.md`, point 4), mais ne réécrit pas les chemins du frontmatter. Vérifié sur
`done/2026-08-14-audit-integre.md` : `brief:` pointe vers `.claude/implementation/audit-integre.brief.md`
et `audit:` vers `…/audit-integre.audit.md`, deux chemins qui n'existent plus.

**Aggravant, constaté le 2026-08-14** — le même fichier porte `plan:
.claude/plans/linked-toasting-graham.md`, nom que le harness a depuis réattribué au plan d'un
**autre** chantier. Ce champ ne pointe donc plus vers rien : il pointe vers le mauvais contenu, ce
qu'aucune vérification d'existence ne détecte.

## Soldé le

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — les six champs ont été réécrits vers
leurs cibles `done/`, et la boucle d'archivage de `cloture.md` les réécrit désormais à chaque
clôture. Le contrôle 5 du garde-fou vérifie qu'ils résolvent.
Établi par : `bash scripts/check-pipeline.sh` → contrôle 5 « ✓ tous les champs plan/brief/audit
résolvent », code 0.

## Pourquoi c'est gênant

ces champs existent pour qu'une reprise à froid retrouve l'intention et
le contenu des étapes. Un chemin mort les prive de leur seul usage ; un chemin qui résout vers le
plan d'un autre chantier est pire, parce qu'il a l'air de fonctionner.

## Pour solder

réécrire les trois champs pendant la boucle d'archivage de `cloture.md`, avec les
chemins `done/` définitifs.

## Assumé

dette préexistante, non aggravée par le chantier qui l'a relevée.
