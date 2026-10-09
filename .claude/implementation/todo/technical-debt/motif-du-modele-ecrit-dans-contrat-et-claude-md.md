+++
id = "motif-du-modele-ecrit-dans-contrat-et-claude-md"
title = "Le motif du `/model` pour la session seulement est écrit dans `contrat.md` et dans `.claude/CLAUDE.md`, sans contrôle"
date = 2026-10-09
severite = "note"
chantier = "modele-hors-de-settings-json"
reference = "R3"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

« `settings.json` est versionné, un `/model` en défaut salit l'arbre, et un Chantier ne se crée ni
ne se reprend sur un arbre sale » figure dans `skills/implementation-tracker/references/contrat.md`
(« Modèle d'implémentation ») et dans `.claude/CLAUDE.md` (« Le modèle d'une session »). Le plan
voulait cette double écriture ; `scripts/check_pipeline.py` ne lit pas `.claude/CLAUDE.md`.

## Pourquoi c'est gênant

Si le pipeline cesse de bloquer sur arbre sale, ou si l'option C du brief entre, il faut corriger
deux endroits, et rien ne signale celui qu'on oublie.

## Pour solder

`.claude/CLAUDE.md` renvoie à `contrat.md#modèle-dimplémentation` au lieu de redire le motif, ou
`check_pipeline.py` rapproche les deux passages.

## Assumé

<OPTIONNEL>
