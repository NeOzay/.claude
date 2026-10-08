+++
id = "session-dump-sessions-gardees-en-memoire"
title = "session-dump garde toutes les sessions en mémoire jusqu'à l'écriture"
date = 2026-10-08
severite = "note"
chantier = "dump-sessions"
reference = "R6"
pin = false
+++

## Constat

`dumper` de `skills/session-dump/scripts/session_dump.py` lit toutes les sessions d'un projet et
garde leurs lignes jusqu'au rendu : 260 Mo au pic pour 115 Mo de JSONL sur ce dépôt, le 2026-10-08.
Les noms de fichiers ne dépendent que des statistiques de chaque session, pas de leurs lignes.

## Pourquoi c'est gênant

Le coût en mémoire croît avec l'historique du projet. Ce n'est pas un défaut aujourd'hui ; il le
devient sur un projet dont l'historique se compte en gigaoctets.

## Pour solder

Rendre chaque session au moment de la lire, sans garder ses lignes, et ne conserver que les
contenus rendus ; ou écrire chaque dump dans le répertoire en construction au fil de la lecture.
