+++
id = "prefill-oserror-message-et-branche-non-couverte"
title = "La branche OSError de prefill._run n'est jamais couverte, et son message ment sur la cause"
date = 2026-08-31
source = "chantier 2026-08-31-champs-preremplis, audit de clôture R2"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`listdir/prefill.py`, branche `except OSError` de `_run` : toute `OSError` est rapportée
« bash introuvable ». Le cas le plus probable — un `cwd` inexistant — a disparu avec le correctif
de R1, mais une permission refusée sur le `cwd`, un `bash` non exécutable ou un `ENOMEM` enverront
toujours chercher un `bash` qui est là.

`tests/test_prefill.py::test_champ_command_binaire_absent` exerce le **code 127** de `bash`, non la
branche `OSError`, sous un nom qui laisse croire le contraire, et n'assère que `not r` — pas le
message. La branche reste entièrement non couverte.

## Pourquoi c'est gênant

Un message d'erreur qui nomme la mauvaise cause envoie corriger ce qui va bien. Le module proclame
en en-tête « ÉCHEC FERMÉ […] Rien n'est avalé » : la promesse porte sur le fait d'échouer, pas sur
l'exactitude de ce qui est dit, et c'est cette nuance qui trompe.

## Pour solder

Distinguer les causes dans le message (`errno`), ou renoncer à nommer une cause qu'on ne connaît
pas et rapporter l'`OSError` telle quelle. Renommer le test existant d'après ce qu'il exerce
vraiment, et couvrir la branche `OSError` — un `bash` non exécutable posé dans un `PATH` de test
suffit.

## Assumé

<OPTIONNEL>
