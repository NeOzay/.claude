+++
id = "lexique-relu-a-chaque-composition"
title = "Le mod `lexique` relit le lexique local à chaque composition du prompt système, sans cache"
date = 2026-10-15
source = "chantier `solder-sept-dettes`, Étape 7, discussion du 2026-10-15"
+++

## À faire

Le mod garde le texte de `lexique session` pour toute la vie du processus (`local ??= …`) : ni
`/clear` ni `/compact` ne relisent `.claude/LEXIQUE.md`, et seul un redémarrage de Claude Code
donne le lexique à jour. Retirer ce cache et relancer la commande à chaque `prompt.compose`.

À établir d'abord, par `claude --debug` (un `$.process.run (lexique)` par composition) :
`prompt.compose` est-il rappelé à `/clear` et à `/compact` ? Sinon, retirer le cache ne change rien.

Ce que le changement ne couvre pas, même établi : la mise à jour au fil d'une conversation
(`prompt.compose` n'est pas rappelé à chaque requête), et une conversation reprise, qui garde son
prompt système enregistré jusqu'à sa compaction. Une commande qui ne rend rien doit continuer de
laisser les sections du moteur intactes. Le coût, un processus par composition, reste faible.

## Références

- `skills/lexique/hooks/register.ts` : le hook `prompt.compose` et son `local ??=`
- `skills/lexique/hooks/register.test.ts` : « ne lance la commande qu'une fois, pour toutes les
  compositions », test à revoir
- `skills/lexique/SKILL.md`, « Ce que reçoit la session » : la lecture unique par processus et le
  remède, à réécrire
- `shadow-skills/claude-code-mods/SKILL.md`, « Ce qui marche » : `prompt.compose`, « Mémoriser
  entre deux appels » ; « Vérifier en session réelle » pour la recette
- Dette `conversation-reprise-sans-lexique-local-jusqua-compaction` : la limite de la reprise,
  soldée par documentation dans `solder-sept-dettes`
