+++
id = "formater-avant-chaque-commit"
title = "Formater chaque fichier avant de proposer un commit, avec la configuration qui le gouverne"
date = 2026-10-04
source = "discussion du 2026-10-04, après l'adoption de ruff format et de rumdl"
+++

## À faire

Faire formater automatiquement, avant chaque proposition de commit et dans tout projet, les fichiers
à commiter, chacun par le formateur et la configuration dont il relève :

- **un fichier de `~/.claude/` ou du `.claude/` d'un projet** → `fmt-claude [--check] <fichiers>`,
  une commande globale, qui passe toujours la configuration de `~/.claude` de façon explicite
  (`rumdl --config ~/.claude/.rumdl.toml`, `ruff --config ~/.claude/ruff.toml`). Sans elle, un
  `.md` sans `.rumdl.toml` à proximité prend les règles par défaut de rumdl, qui transforment les
  `##` en `###`. Un `.py` du `.claude/` d'un projet prendrait, lui, la configuration ruff du
  projet ;
- **tout autre fichier du projet** → les formateurs du projet, avec sa propre configuration. Ils
  se **déclarent** au lieu d'être devinés, par une commande locale
  `.claude/bin/fmt-projet [--check] <fichiers>`, posée selon la procédure des commandes locales ;
- **un aiguilleur global** `fmt [--check] <fichiers>` répartit les fichiers entre les deux. Si un
  projet n'a pas de `fmt-projet`, il le signale et laisse passer, au lieu de se taire.

Déclenchement, sur deux niveaux complémentaires :

1. **une étape de `git-smart-commit`** : lancer `fmt` sur les fichiers à commiter avant de
   présenter le diff, pour que l'utilisateur approuve un contenu déjà formaté ;
2. **un hook `PreToolUse` global** sur `git commit` et `commit-chantier` : il lance `fmt --check`
   et refuse le commit (code 2) en nommant les fichiers non formatés. Il ne formate jamais
   lui-même, sinon il ferait commiter un contenu que l'utilisateur n'a pas vu.

Pourquoi au commit et non à chaque modification : formater en continu fait échouer les
modifications suivantes de l'agent, dès qu'un paragraphe réenroulé ne correspond plus au texte
qu'il recopie. Cela ajoute aussi un avis de « fichier modifié » à son contexte à chaque fois.

Questions à trancher au Brief ou au Plan :

- le hook ne voit que l'arbre de travail, et un `fmt-projet` quelconque ne sait pas lire le
  contenu indexé sur l'entrée standard. Faut-il refuser aussi un fichier dont la version indexée
  diffère de l'arbre de travail ?
- les archives figées (`done/`, `archive/`) sont exclues par `.rumdl.toml`. Mais un fichier passé
  explicitement à rumdl échappe à l'exclusion tant que `force_exclude = true` n'y est pas posé ;
- si `uvx` manque : laisser passer en le signalant sur stderr. Ni bloquer tout commit, ni se taire
  comme `intent-brief-gate.sh` le faisait ;
- les commits de l'utilisateur hors de l'agent (Neovim) ne passent pas par le hook. Un hook git
  `pre-commit`, à installer dans chaque dépôt, est-il voulu ?

## Références

- conventions et lanceurs : `OUTILLAGE.md`, sections « Vérifier le code Python » et « Formater le
  Markdown » ; configurations `ruff.toml` (racine et une par skill) et `.rumdl.toml`
- commandes globales et locales : `shadow-skills/skill-convention/references/commandes-locales.md`
- procédure de commit : `skills/git-smart-commit/references/staging.md` et `confirmation.md`
- vérifié le 2026-10-04 sur un faux projet : depuis sa racine,
  `uvx rumdl fmt --config ~/.claude/.rumdl.toml .claude/` réenroule `.claude/implementation/todo/`
  et laisse `done/` intact. Sans `--config`, rumdl répond « No configuration file found (using
  defaults) »
- dettes liées : `ruff-format-absent-des-agents` (les sous-agents ignorent le formatage) et
  `dates-entre-guillemets-acceptees` (un défaut de forme que le formateur ne voit pas : le front
  matter)
- précédent d'une dépendance absente qui laissait tout passer en silence :
  `hooks/intent-brief-gate.sh`, rapporté dans `OUTILLAGE.md`
