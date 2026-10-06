+++
id = "aucun-signal-quand-le-mod-lexique-ne-se-charge-pas"
title = "Rien ne signale que le mod lexique-sous-agent n'est pas chargé"
date = 2026-10-06
source = "audit hors chantier de `lexique-local-tronque-par-le-hook-session`, troisième passage du 2026-10-06, `.claude/implementation/lexique-local-tronque.audit.md`, R17 (R6 du premier passage)"
+++

## Constat

Le lexique local de la session ne vient plus que du mod `lexique-sous-agent`, nommé par
`CLAUDE_CODE_PLUGIN_DIRS` dans `settings.json` ; le hook `SessionStart` qui le doublait est retiré.
Si le mod ne se charge pas (dossier déplacé, variable retirée, API de mod changée, `--bare`), la
session n'a aucun lexique local. Constaté le 2026-10-06 : `scripts/sante_skills.py`, seul hook
`SessionStart` restant, ne cite ni le mod ni `CLAUDE_CODE_PLUGIN_DIRS`.

## Pourquoi c'est gênant

C'est le tort que la dette `lexique-local-tronque-par-le-hook-session` décrivait (« rien ne le dit
»), déplacé : la session perd tout le lexique local sans le moindre message, et seule une phrase du
modèle employant mal un terme le laisse deviner.

## Pour solder

Faire vérifier par `sante_skills.py` que `CLAUDE_CODE_PLUGIN_DIRS` nomme un dossier de mod existant
qui porte un `hooks/hooks.json`, et qu'il dise l'anomalie dans son stdout, comme pour les autres
dépendances.
