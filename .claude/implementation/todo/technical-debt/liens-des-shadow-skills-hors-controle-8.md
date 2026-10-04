+++
id = "liens-des-shadow-skills-hors-controle-8"
title = "Les liens de `shadow-skills/` échappent au contrôle 8 de `check_pipeline.py`"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R6"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`scripts/check_pipeline.py` contrôle les liens et les ancres des fichiers de `skills/`, pas ceux de `shadow-skills/`. `shadow-skills/skill-convention/references/prose.md` affirme pourtant que « `check_pipeline.py` les contrôle », et porte des renvois à ancre (`#frontmatter`, `#dates-et-listing`).

## Pourquoi c'est gênant

Un intitulé renommé dans `skills/` casse en silence les ancres qui le visent depuis un Shadow-skill. Le premier à s'en apercevoir est l'agent qui suit le lien en cours de tâche.

## Pour solder

Étendre le contrôle 8 à `shadow-skills/`, ou corriger l'affirmation de `prose.md`.

## Assumé

<OPTIONNEL>
