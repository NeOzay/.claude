+++
id = "entete-agent-lit-le-yaml-par-regex"
title = "`lexique.py` lit le frontmatter d'un agent par regex, pas par un lecteur YAML"
date = 2026-10-05
severite = "avertissement"
chantier = "lexique-des-sous-agents"
reference = "R5"
pin = true
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, R5 (clos avec, choix de l'utilisateur)"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`entete_agent` lit les lignes `cle: valeur` en colonne 0 du frontmatter d'un agent, avec une regex,
un commentaire de fin de ligne ôté et `True` lu comme `true`. Claude Code lit le même frontmatter
par `Bun.YAML.parse`, puis compare à `"true"`. Constaté le 2026-10-05 :
`omitClaudeMd: "true"  # isolé` isole l'agent pour Claude Code, mais `entete_agent` rend la valeur
guillemets compris, et `annonce_sous_agent` verse alors le lexique local.

## Pourquoi c'est gênant

Chaque forme YAML que la regex ignore rompt l'isolation d'un agent à `omitClaudeMd: true` sans
qu'aucun message ne le dise : l'agent reçoit un lexique qu'il devait ne pas recevoir. Le correctif
par cas (commentaire, majuscule) laisse les formes suivantes ouvertes.

## Pour solder

Lire le frontmatter par un vrai lecteur YAML, au prix d'une dépendance ou d'un autre lanceur que le
`python3` du PATH, sous lequel `lexique.py` tourne en stdlib seule. Cas à couvrir par test : valeur
entre guillemets suivie d'un commentaire, booléens YAML, scalaires multilignes.

## Assumé

`lexique.py` reste en stdlib seule : le mod le lance sous le `python3` du PATH, où le venv du dépôt
n'est pas actif. Choix de l'utilisateur de clore avec cette réserve plutôt que d'ajouter une
rustine.
