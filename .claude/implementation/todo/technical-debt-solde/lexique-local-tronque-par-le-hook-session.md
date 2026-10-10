+++
id = "lexique-local-tronque-par-le-hook-session"
title = "Un lexique local de plus de 10 000 caractères est tronqué par le hook `SessionStart`"
date = 2026-10-05
severite = "<OPTIONNEL>"
chantier = "<OPTIONNEL>"
reference = "<OPTIONNEL>"
pin = "<OPTIONNEL bool>"
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, constat du Journal du 2026-10-05, vérifié par l'utilisateur sur claude-translator"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Claude Code remplace tout `additionalContext` de plus de 10 000 caractères (`HXo = 1e4` dans le
binaire 2.1.289, non configurable) par un aperçu de 2 Ko et range le reste dans un fichier. Constaté
le 2026-10-05 : le lexique local de `claude-translator`, 12 973 caractères, arrive tronqué à la
session principale.

## Soldé le

**2026-10-06, hors chantier** (correction de la dette, trois audits dans
`.claude/implementation/lexique-local-tronque.audit.md`) — le mod `lexique-sous-agent` verse le
lexique local à la session par une section de `prompt.compose`, sans le plafond d'un hook ; le
hook `SessionStart` du lexique est retiré de `settings.json`.

Établi par :

- `wc -c < .claude/LEXIQUE.md` (dans `claude-translator`) → `13338` ; `lexique session` rend
  `13459` caractères : plus que les 10 000 du plafond.
- une session `claude -p --model haiku "Réponds OK." < /dev/null` dans `claude-translator`, puis
  le décompte de la ligne « Passe typographique » dans sa transcription → 1 occurrence dans
  chacun des 2 `prompt_snapshot`, 2 au total, aucune ailleurs : le lexique local figure entier
  dans le prompt système, jusqu'à sa dernière ligne.
- troisième audit : **RÉSERVES**, aucun bloquant ; le lexique figure une fois dans le prompt
  système en session neuve, après `/clear` et `/compact`, à `--resume` et `--continue` ;
  `lexique-test-isole` ne reçoit rien, `lexique-test-claude-md` et `lexique-test-injecte` le
  reçoivent une fois.

Limites restées au registre : `lexique-local-absent-sous-system-prompt`,
`conversation-reprise-sans-lexique-local-jusqua-compaction`,
`aucun-signal-quand-le-mod-lexique-ne-se-charge-pas`,
`nom-du-mod-lexique-sous-agent-trop-etroit`.

## Pourquoi c'est gênant

Une session principale ne voit que le début d'un gros lexique local, donc emploie des termes qu'elle
ignore, et rien ne le dit. Le mod du Chantier contourne le plafond pour les sous-agents, pas pour la
session.

## Pour solder

Verser le lexique local à la session par une voie sans plafond (un mod, comme pour les sous-agents),
ou le garder sous 10 000 caractères, et faire dire à `lexique liste` qu'il dépasse.

## Assumé

<OPTIONNEL>
