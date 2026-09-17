+++
id = "commandes-locales-au-projet"
title = "Standardiser la mise à disposition de commandes locales à un projet"
date = 2026-09-17
source = "discussion du 2026-09-16 sur l'ajout de commandes au modèle hors du PATH global"
+++

## À faire

Définir une procédure standard, reproductible d'un projet à l'autre, pour donner à l'agent des
commandes qui n'existent que dans un projet donné.

Aujourd'hui, une commande devient disponible en passant par `~/.claude/bin/`, qui est dans le
`PATH` global : elle vaut donc pour tous les projets. Rien ne permet de limiter une commande à un
seul dépôt.

La piste retenue en discussion :

- un répertoire `.claude/bin/` versionné dans le projet, avec un script exécutable par commande ;
- un hook `SessionStart` branché dans le `.claude/settings.json` **du projet**, qui ajoute ce
  répertoire au `PATH` en écrivant un `export` dans `$CLAUDE_ENV_FILE`. Claude Code source ce
  fichier avant chaque commande Bash de l'agent, ce qui en limite l'effet à l'agent et au projet ;
- l'annonce des commandes à l'agent, qui ne découvre pas seul le contenu d'un `PATH` : par la
  sortie du hook, comme `outillage-rappel.sh`, ou par le `CLAUDE.md` du projet.

Écartés en discussion : les alias, parce que Bash ne les développe pas en non-interactif sans
`shopt -s expand_aliases` ; les fonctions shell, qui fonctionnent mais ne sont ni visibles sur
disque ni testables isolément ; la clé `env` des settings, qui ne développe pas `$PATH`.

Points à trancher par le chantier :

- la forme du livrable : un skill, un script d'amorçage, une semence `gabarit`, ou une simple
  procédure documentée ;
- la couverture des sous-agents : ils ne reçoivent pas `SessionStart` (constaté pour
  `outillage-rappel.sh`), et il faut vérifier s'ils bénéficient ou non du `CLAUDE_ENV_FILE` de la
  session parente. Non vérifié à ce jour ;
- la cohabitation avec les autres hooks `SessionStart` et avec le hook RTK, qui réécrit les
  commandes Bash : écrire dans `$CLAUDE_ENV_FILE` avec `>>`, jamais avec `>` ;
- le comportement hors du dépôt : garde sur le répertoire de travail, et échec ouvert, sur le
  modèle d'`outillage-rappel.sh`.

## Références

- hook existant à prendre pour modèle : `hooks/outillage-rappel.sh`, branché dans
  `.claude/settings.json` (settings de projet), qui documente la portée par projet, la garde sur
  le répertoire, l'échec ouvert et l'absence de `SessionStart` chez les sous-agents
- mécanisme actuel, global : `bin/` (liens vers `list-dir`, `gabarit`, `impl-list`,
  `commit-chantier`)
- hooks globaux, à ne pas confondre : `settings.json`, sections `SessionStart` et `PreToolUse`
- documentation Claude Code : hooks `SessionStart` et variable `CLAUDE_ENV_FILE`
