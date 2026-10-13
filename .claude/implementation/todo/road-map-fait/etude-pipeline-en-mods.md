+++
id = "etude-pipeline-en-mods"
title = "Étudier le portage du pipeline des Chantiers à l'intérieur de Claude Code, par des mods"
date = 2026-10-09
source = "demande de l'utilisateur, session d'analyse des dumps du 2026-10-09"
+++

## À faire

Étudier ce que les mods de Claude Code permettraient de porter du pipeline des Chantiers, qui vit
aujourd'hui en prose de skills que le modèle relit et applique. Le livrable est une étude : ce qui
gagnerait à passer en mod, ce qui doit rester au modèle, et ce qu'il faut d'abord vérifier. La
suite se décide après elle, en Chantiers à part.

Ce qui est établi, d'après le Shadow-skill `claude-code-mods` (versions 2.1.289 à 2.1.291) :

- `prompt.compose` verse une section au prompt système de la session principale, sans plafond de
  taille, et elle survit à `/clear` et `/compact`. L'état du Suivi ou sa section `## Passation`
  pourraient y entrer, au lieu d'être relus à chaque reprise ;
- `agent.spawn` réécrit le prompt d'un sous-agent : c'est déjà la voie du mod `outillage` vers
  `implementation-auditor` et `plan-reviewer` ;
- un mod lance une commande de `bin/` par `$.process.run` ;
- un mod placé à la racine d'un skill se charge seul.

Ce que la description de `plugin-authoring` annonce, sans essai dans ce dépôt : commandes `/`,
panneau ou bande au-dessus de l'invite, ligne d'état, notification, hook sur les appels d'outils.
Un panneau pourrait afficher les Étapes et leur état. Un hook sur `git commit` pourrait garder la
forme des commits d'Étape, comme l'entrée `formater-avant-chaque-commit` le prévoit pour le
formatage.

Points de friction des dumps qu'un mod pourrait traiter, à confronter à l'étude : les tours
procéduraux (`enchainement-du-chantier`), la relecture complète du Suivi à chaque reprise, la
mesure du contexte après chaque commit.

Questions à trancher au Brief :

- quel geste du pipeline relève du mécanique, donc d'un mod, et lequel du jugement, donc du
  modèle ? La convention « les scripts font la structure, le modèle fait le jugement » donne la
  ligne de partage ;
- les mods sont en TypeScript, que l'utilisateur n'écrit pas : `rules/claude-typescript-style.md`
  suffit-il à les maintenir ?
- l'API des mods bouge d'une version à l'autre, et le banc de test ne voit pas tout
  (`session.append`, les noms ajoutés à `$`). Quel risque de casse est acceptable pour un pipeline
  dont dépendent tous les Chantiers ?

## Fait le

2026-10-13, Chantier `pipeline-v2`, archivé en
`.claude/implementation/done/2026-10-13-pipeline-v2.md`. Conclusion mitigée :
`pipeline-v2/conclusion.md` ; reprise notée en road-map, `reprendre-pipeline-v2-au-navigateur`.

## Références

- Shadow-skill `claude-code-mods` : `shadow-skills/claude-code-mods/SKILL.md`, sections « Ce qui
  marche », « Limites constatées » et « Non essayé »
- mods existants : `skills/lexique/` (`prompt.compose`, `agent.spawn`), `skills/mod-commun/`
  (`$.commande`), `.claude/skills/outillage/`
- skill `plugin-authoring` de Claude Code, pour ce qui n'est pas encore essayé
- pipeline : `skills/implementation-tracker/SKILL.md` et ses `references/`,
  `skills/intent-brief/SKILL.md`, `skills/git-smart-commit/`
- convention : `shadow-skills/skill-convention/references/prose.md`, « Les scripts font la
  structure, le modèle fait le jugement »
- entrées liées : `enchainement-du-chantier`, `formater-avant-chaque-commit`
