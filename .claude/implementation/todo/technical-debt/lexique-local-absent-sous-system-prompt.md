+++
id = "lexique-local-absent-sous-system-prompt"
title = "Sous `--system-prompt`, la session ne reçoit plus aucun lexique local"
date = 2026-10-06
source = "audit hors chantier de `lexique-local-tronque-par-le-hook-session`, troisième passage du 2026-10-06, `.claude/implementation/lexique-local-tronque.audit.md`, R4"
+++

## Constat

Le mod `lexique` verse le lexique local en section de `prompt.compose`. Lancé avec
`--system-prompt`, qui remplace le prompt système, `claude -p` dans `claude-translator` ne porte
plus la section : le prompt enregistré compte 2 blocs et le modèle répond que le lexique est absent.
Avec `--append-system-prompt`, la section est présente, une fois. Constaté le 2026-10-06 ; l'ancien
hook `SessionStart` versait au moins l'aperçu de 2 Ko dans ce mode.

## Pourquoi c'est gênant

Une session lancée avec `--system-prompt` emploie des termes réservés qu'elle ignore, et rien ne le
dit. Aucun projet de `/home/debian/projects` n'emploie ce mode aujourd'hui, mais un script ou un
outil qui le passerait perdrait le lexique en silence.

## Pour solder

Verser le lexique local par une voie que `--system-prompt` ne remplace pas, ou faire dire au mod,
sur la ligne d'état, qu'il n'a trouvé aucune composition où se loger. Sinon, écrire la limite dans
`skills/lexique/SKILL.md` (« Ce que reçoit la session »).
