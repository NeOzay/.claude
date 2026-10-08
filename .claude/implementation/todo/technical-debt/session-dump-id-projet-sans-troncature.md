+++
id = "session-dump-id-projet-sans-troncature"
title = "L'identifiant de projet de session-dump ne reproduit pas la troncature de Claude Code"
date = 2026-10-08
severite = "avertissement"
chantier = "dump-sessions"
reference = "R5"
pin = false
+++

## Constat

`id_projet` de `skills/session-dump/scripts/session_dump.py` remplace chaque caractère non
alphanumérique du chemin par `-`. Claude Code 2.1.294 tronque en outre l'identifiant à 200
caractères et y ajoute un hachage du chemin (relu dans le binaire par l'audit du 2026-10-08). Le
Plan n'avait vérifié la règle que sur 12 répertoires de `projects/`, tous plus courts.

## Pourquoi c'est gênant

Pour un projet dont l'identifiant dépasse 200 caractères, `session-dump` répond « aucune session »
(sortie 1) alors qu'il y en a : l'échec nomme un chemin attendu qui n'existe pas sous ce nom. Aucun
projet actuel n'est concerné.

## Pour solder

Reproduire la troncature et le hachage dans `id_projet`, d'après le binaire de Claude Code, avec un
test sur un chemin de plus de 200 caractères ; ou chercher sous `projects/` le répertoire dont le
`cwd` des sessions est le projet.
