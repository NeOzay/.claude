+++
id = "entrees-vivantes-citent-des-chemins-deplaces"
title = "Des entrées vivantes des registres citent des chemins que le Chantier `shadow-skill` a déplacés"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R8"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le Chantier `shadow-skill` a déplacé `skills/nvim-mini-test/`, `skills/emmylua-ls/` et le contenu de `skills/skill-convention/` vers `shadow-skills/`. Au Registre de dette, `nvim-mini-test-redigee-en-anglais`, `emmylua-ls-description-sans-limite`, `criteres-de-brief-bornes-a-une-extension`, `deux-conventions-de-mode-de-defaillance`, `intent-brief-description-sans-limite` et `list-dir-codes-de-sortie-non-dits` citent les anciens chemins ; à la road-map, `lexique-des-sous-agents` aussi.

## Pourquoi c'est gênant

Qui reprend une de ces entrées cherche un fichier absent, et peut conclure à tort que la dette est soldée ou sans objet.

## Pour solder

Remplacer dans ces entrées les chemins sous `skills/nvim-mini-test/`, `skills/emmylua-ls/` et `skills/skill-convention/references/` par leurs équivalents sous `shadow-skills/`.

## Assumé

Le pipeline ne réécrit pas un Registre de lui-même (Journal du Chantier `shadow-skill`).
