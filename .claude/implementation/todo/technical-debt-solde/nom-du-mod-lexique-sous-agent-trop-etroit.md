+++
id = "nom-du-mod-lexique-sous-agent-trop-etroit"
title = "Le mod `lexique-sous-agent` porte un nom qui ne dit plus que le lexique de la session passe aussi par lui"
date = 2026-10-06
source = "audit hors chantier de `lexique-local-tronque-par-le-hook-session`, troisième passage du 2026-10-06, `.claude/implementation/lexique-local-tronque.audit.md`, R12"
+++

## Constat

Le mod `skills/lexique/mod` verse le lexique local à la session (section de `prompt.compose`) et à
chaque sous-agent (`agent.spawn`), mais son nom, dans `.claude-plugin/plugin.json`, est
`lexique-sous-agent`. Constaté le 2026-10-06 : `grep -rl lexique-sous-agent` hors `done/` et hors
rapports d'audit trouve dix fichiers qui le citent (`SKILL.md`, `lexique-cli.py`, `lexique.py`,
`register.ts`, `register.test.ts`, `plugin.json`, `claude-code-mods/SKILL.md`, deux agents de test,
une entrée de dette).

## Pourquoi c'est gênant

Qui cherche pourquoi la session reçoit son lexique ne pense pas à un mod « sous-agent ». Le nom
étant cité par dix fichiers et par le préfixe `lexique-sous-agent:local` des sections, le renommer
plus tard coûte davantage à chaque ajout.

## Pour solder

Renommer le mod (par exemple `lexique`) dans `plugin.json`, les messages d'état, l'`id` de la
section et les dix fichiers qui le citent ; relancer `claude plugin test` et les trois agents
témoins.

## Soldé le

**2026-10-06, chantier `mods-a-la-racine-des-skills`** — le mod s'appelle `lexique`, sa section
`lexique:local`, et les fichiers qui le citaient sont renommés.

Établi par :

- `grep -n '"name"' skills/lexique/.claude-plugin/plugin.json` → `"name": "lexique",`.
- `grep -rln lexique-sous-agent`, hors `done/`, rapports d'audit et dettes soldées → le suivi, le
  brief et le plan du Chantier seuls, que la Clôture archive en `done/`.
- `claude plugin test skills/lexique` → 8 pass, 0 fail, code 0.
- les trois agents témoins, dans `claude-translator`, rendent le relevé d'avant le renommage
  (Journal du Chantier, Étape 6 ; audit de clôture).
