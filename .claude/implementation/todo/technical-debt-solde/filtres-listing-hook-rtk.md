+++
id = "filtres-listing-hook-rtk"
title = "Les filtres de listing sont cassés par le hook `rtk`"
date = 2026-08-14
source = "Identifié par `audit-integre`, journal du suivi."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`ls .claude/implementation/*.md | grep -vE '\.(brief|audit)\.md$'` n'exclut plus rien.
Le hook `rtk` réécrit `ls` en ajoutant une colonne de taille en fin de ligne
(`…brief.md  6.2K`), donc l'ancre `$` ne matche jamais. Vérifié le 2026-08-14 : la commande de
l'Étape 0 du tracker remonte `dette-technique.brief.md` à côté de `dette-technique.md`.

## Soldé le

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — le filtre vit désormais dans
`skills/implementation-tracker/scripts/impl-list.sh`, un script que le hook `rtk` ne réécrit pas, et
que l'Étape 0 comme le Cas C appellent au lieu de recopier une commande.
Établi par : `bash "$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh" .claude/implementation/done | grep -cE '\.(brief|audit|plan)\.md$'` → `0`,
sur un répertoire contenant pourtant 2 `.brief.md`, 2 `.audit.md` et 2 `.plan.md`.

## Pourquoi c'est gênant

les `*.brief.md` et `*.audit.md` apparaissent dans la liste des
implémentations en cours, que l'Étape 0 de `implementation-tracker` existe précisément pour tenir
propre. Le filtre est écrit à trois endroits (`SKILL.md` Étape 0 et Cas C, et la commande du Cas C).

## Pour solder

filtrer sur le nom de fichier plutôt que sur la fin de ligne : `find
.claude/implementation -maxdepth 1 -name '*.md' ! -name '*.brief.md' ! -name '*.audit.md'`, ou un
`grep -vE '\.(brief|audit)\.md( |$)'`.

## Assumé

<OPTIONNEL>
