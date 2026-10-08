+++
id = "aucun-signal-quand-le-mod-lexique-ne-se-charge-pas"
title = "Rien ne signale que le mod lexique-sous-agent n'est pas chargé"
date = 2026-10-06
severite = "<OPTIONNEL>"
chantier = "<OPTIONNEL>"
reference = "<OPTIONNEL>"
pin = "<OPTIONNEL bool>"
source = "audit hors chantier de `lexique-local-tronque-par-le-hook-session`, troisième passage du 2026-10-06, `.claude/implementation/lexique-local-tronque.audit.md`, R17 (R6 du premier passage)"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le lexique local de la session ne vient plus que du mod `lexique-sous-agent`, nommé par
`CLAUDE_CODE_PLUGIN_DIRS` dans `settings.json` ; le hook `SessionStart` qui le doublait est retiré.
Si le mod ne se charge pas (dossier déplacé, variable retirée, API de mod changée, `--bare`), la
session n'a aucun lexique local. Constaté le 2026-10-06 : `scripts/sante_skills.py`, seul hook
`SessionStart` restant, ne cite ni le mod ni `CLAUDE_CODE_PLUGIN_DIRS`.

## Soldé le

**2026-10-06, chantier `mods-a-la-racine-des-skills`** — `CLAUDE_CODE_PLUGIN_DIRS` n'existe plus :
chaque mod se charge depuis la racine de son skill. Le « Pour solder » est donc transposé :
`scripts/sante_skills.py` contrôle, à chaque démarrage, les mods à la racine d'un skill
(`plugin.json` lisible avec un `name`, modules de `hooks.json` présents, `dependencies` présentes),
et signale la variable si elle revient dans `settings.json`.

Établi par :

- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` → `0` ; `python3 scripts/sante_skills.py` →
  code 0, aucune sortie.
- copie de `HEAD` par `git archive`, `skills/mod-commun/hooks/register.ts` supprimé, puis
  `python3 scripts/sante_skills.py` → code 1, « ✗ mod skills/mod-commun : le module
  './register.ts' de hooks/hooks.json est absent. ».
- `pytest scripts/tests/test_sante_skills.py` → 34 passés.

Limite : un module présent qui échoue au chargement échappe au contrôle ; seul le journal de
`claude --debug` le montre (docstring de `mods_en_defaut`, `claude-code-mods`). Reste au registre :
`sante-skills-plante-sur-une-dependance-objet`.

## Pourquoi c'est gênant

C'est le tort que la dette `lexique-local-tronque-par-le-hook-session` décrivait (« rien ne le dit
»), déplacé : la session perd tout le lexique local sans le moindre message, et seule une phrase du
modèle employant mal un terme le laisse deviner.

## Pour solder

Faire vérifier par `sante_skills.py` que `CLAUDE_CODE_PLUGIN_DIRS` nomme un dossier de mod existant
qui porte un `hooks/hooks.json`, et qu'il dise l'anomalie dans son stdout, comme pour les autres
dépendances.

## Assumé

<OPTIONNEL>
