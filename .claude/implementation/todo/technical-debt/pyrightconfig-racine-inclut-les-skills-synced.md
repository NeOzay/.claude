+++
id = "pyrightconfig-racine-inclut-les-skills-synced"
title = "Le `pyrightconfig.json` de la racine inclut les skills synchronisées et rend 8097 erreurs"
date = 2026-09-18
source = "chantier `skill-convention`, étape 7 — confrontation du Python à `rules/claude-python-style.md`"
+++

## Constat

`uvx --with pytest basedpyright` lancé à la racine — la commande que documente `OUTILLAGE.md` —
rend **8097 erreurs**. Elles viennent presque toutes de `skills/synced/`, la copie déposée par la
synchronisation Claude Code, ignorée par `.gitignore` depuis le 2026-09-17.

L'`include` du `pyrightconfig.json` de la racine vaut `skills` et `scripts` ; son `exclude` ne
mentionne que `plugins`, `**/node_modules` et `**/__pycache__`. Le Python versionné du dépôt, lui,
ne rend que 12 erreurs (`scripts/tests/test_sante_skills.py`).

## Pourquoi c'est gênant

La commande d'outillage est inexploitable à la racine : personne ne lit 8097 erreurs, et le verdict
du dépôt devient invérifiable d'un seul geste. Le nombre dépend en outre de ce que la
synchronisation a déposé ce jour-là — il change sans qu'aucun fichier versionné n'ait bougé.

## Pour solder

Ajouter `skills/synced` et `plugins/synced` à l'`exclude` du `pyrightconfig.json` de la racine, puis
vérifier que la commande ne rend plus que les erreurs du code versionné.
