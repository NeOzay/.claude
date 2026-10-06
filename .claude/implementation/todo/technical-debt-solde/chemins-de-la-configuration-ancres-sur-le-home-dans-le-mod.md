+++
id = "chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod"
title = "Le mod `lexique-sous-agent` ancre deux chemins sur le HOME"
date = 2026-10-05
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, R8"
+++

## Constat

Le mod lance `${HOME}/.claude/skills/lexique/scripts/lexique-cli.py` (`register.ts`) et se charge
par `CLAUDE_CODE_PLUGIN_DIRS = ~/.claude/skills/lexique/mod` dans `settings.json`. Le contrôle 7 de
`check_pipeline.py` refuse cet ancrage dans les `.md` mais ne lit pas le TypeScript ni
`settings.json`.

## Pourquoi c'est gênant

Une configuration déplacée de `~/.claude` casse le mod sans bruit : la commande ne se trouve plus,
le sous-agent démarre sans lexique, et rien ne le dit sinon la ligne d'état.

## Pour solder

Résoudre la racine de la configuration depuis le mod (par exemple relativement à son dossier) au
lieu de `$HOME`, ou étendre le contrôle 7 au TypeScript et à `settings.json`.

## Assumé

Même forme que l'entrée `SessionStart` voisine de `settings.json`, qui ancre le HOME de la même
façon.

## Soldé le

**2026-10-06, chantier `mods-a-la-racine-des-skills`** — le mod lexique appelle `lexique` par son
nom de `bin/`, résolu par le `PATH`, et se charge depuis la racine de son skill, sans réglage.

Établi par :

- `grep -rnE 'HOME|~/\.claude|/home/'` sur les `*.ts` et `plugin.json` des trois mods → 0 ligne.
- `grep -n argv skills/lexique/hooks/register.ts` → `argv: ['lexique', 'session']` et
  `argv: ['lexique', 'sous-agent', e.subagentType]`.
- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` → `0`.

Prix assumé : le mod dépend du `PATH` de la session, au registre sous
`lexique-depend-du-path-de-la-session`.
