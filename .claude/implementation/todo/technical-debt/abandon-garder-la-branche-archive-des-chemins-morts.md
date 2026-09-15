+++
id = "abandon-garder-la-branche-archive-des-chemins-morts"
title = "L'abandon « garder la branche » archive un suivi dont plan: et brief: visent des fichiers absents"
date = 2026-09-14
source = "chantier `git-smart-commit-trois-commits`, journal du suivi (hors périmètre) et R8 du rapport d'audit"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`aplatissement.md` § Abandon, cas *garder la branche* : seul le suivi est ramené sur `base:` et
archivé en `done/`. Ses champs `plan:` et `brief:` ne sont pas réécrits, et visent des fichiers qui
n'existent que sur la branche conservée. Le contrôle 5 de `check_pipeline.py` (« Chemins du
frontmatter des chantiers archivés ») exige que ces champs résolvent dans l'arbre.

## Pourquoi c'est gênant

Au premier abandon de ce type, le garde-fou vire au rouge sur `base:`, sans que rien dans l'archive
ne dise pourquoi : la procédure suivie à la lettre produit une archive que le dépôt refuse. Le
réflexe sera de « réparer » le suivi archivé à la main, ou de désactiver le contrôle.

## Pour solder

Choisir entre archiver aussi le plan et le brief (comme *tout jeter*, en réécrivant les champs), ou
retirer ces champs du suivi archivé en le disant dans l'archive, ou faire tolérer au contrôle 5 un
chantier `statut: abandonné` dont la branche existe. Puis l'écrire dans `aplatissement.md` § Abandon
et le couvrir par un test du contrôle 5.

## Assumé

Hors périmètre de `git-smart-commit-trois-commits`, qui déplaçait les commits de l'abandon sans en
changer les gestes.
