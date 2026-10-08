+++
id = "conversation-reprise-sans-lexique-local-jusqua-compaction"
title = "Une conversation reprise garde son prompt système enregistré, donc son lexique local d'origine ou son absence"
date = 2026-10-06
severite = "critique"
chantier = "Hors chantier"
reference = "R5"
pin = true
source = "audit hors chantier de `lexique-local-tronque-par-le-hook-session`, troisième passage du 2026-10-06, `.claude/implementation/lexique-local-tronque.audit.md`, R5"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

À `--resume` et `--continue`, Claude Code réutilise le prompt système enregistré dans la
conversation jusqu'à sa prochaine compaction : le mod ne le recompose pas. Constaté le 2026-10-06
dans `claude-translator` : une conversation commencée sans la section (mod non chargé, ou
`lexique session` en échec à la première requête) n'en reçoit pas à la reprise — réponse « Absent.
» ; et une modification de `.claude/LEXIQUE.md` n'atteint pas une conversation reprise.

## Pourquoi c'est gênant

Le lexique que voit une session reprise est celui du jour où elle a commencé, pas celui du jour où
elle reprend : un terme ajouté ou retiré entre-temps n'y figure pas, et une conversation née sans le
mod ne le reçoit jamais avant sa compaction. Rien ne le signale.

## Pour solder

Établir si une voie recompose la section à la reprise (un événement de reprise du mod, ou
`prompt.context` à condition de garder les sous-agents isolés), ou écrire cette limite dans
`skills/lexique/SKILL.md` et dans `shadow-skills/claude-code-mods/SKILL.md`.

## Assumé

<OPTIONNEL>
