+++
id = "list-dir-list-trace-brokenpipe-sous-head"
title = "`list-dir list` coupé par `head` imprime une trace `BrokenPipeError` sur stderr"
date = 2026-10-07
severite = "avertissement"
chantier = "registre-de-dette-severite-chantier-pin"
reference = "journal du Suivi"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le 2026-10-07, `list-dir list <liste> | head -1` rend la première ligne attendue, puis écrit sur
stderr `Exception ignored in: <_io.TextIOWrapper name='<stdout>' …>` et
`BrokenPipeError: [Errno 32] Broken pipe`. Reproduit le 2026-10-08 sur le registre de dette.

## Pourquoi c'est gênant

Une trace Python sur stderr se lit comme un échec de la commande, alors que la sortie est juste. Un
agent qui lit la sortie entière peut conclure à une panne et s'écarter de la procédure ; la
procédure de migration du registre a dû prendre ses lots par `sed -n 1,30p`, qui lit tout, pour
l'éviter.

## Pour solder

`list-dir` traite la fermeture de stdout par le lecteur comme une fin normale :
`list-dir list … | head -1` ne rend rien sur stderr, et un test le vérifie.

## Assumé

<OPTIONNEL>
