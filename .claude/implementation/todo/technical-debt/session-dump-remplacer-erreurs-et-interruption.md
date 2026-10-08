+++
id = "session-dump-remplacer-erreurs-et-interruption"
title = "remplacer annonce OSError seule et laisse un répertoire sur Ctrl-C"
date = 2026-10-08
severite = "note"
chantier = "dump-sessions"
reference = "R7"
pin = false
+++

## Constat

`remplacer` de `skills/session-dump/scripts/session_dump.py` relance toute `Exception` après avoir
retiré le répertoire en construction, mais sa docstring (`Raises`) n'annonce que `OSError`, et
`dumper` ne rattrape que `OSError`. Une interruption au clavier pendant l'écriture laisse
`.<id>.neuf-<pid>/`, que le nettoyage de tête, limité au pid courant, ne retire jamais.

## Pourquoi c'est gênant

Une erreur d'écriture autre qu'`OSError` sortirait en traceback, contre la promesse d'échec nommé
du CLI ; aucun chemin connu ne la déclenche. Les répertoires cachés d'interruptions s'accumulent
sous `.claude/session-dump/`, sans perte de données, ignorés par git.

## Pour solder

Aligner `Raises` sur ce que le bloc relance, rattraper l'erreur dans `dumper`, et retirer en tête
les répertoires `.<id>.neuf-*` et `.<id>.ancien-*` laissés par d'autres pid ; ou capter
`KeyboardInterrupt` pour nettoyer.
