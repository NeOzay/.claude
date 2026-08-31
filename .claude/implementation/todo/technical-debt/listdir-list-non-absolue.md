+++
id = "listdir-list-non-absolue"
title = "LISTDIR_LIST n'est pas absolue, contrairement à LISTDIR_ROOT et au plan"
date = 2026-08-31
source = "chantier 2026-08-31-champs-preremplis, audit de clôture R6"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`listdir/prefill.py`, `_environment` : `LISTDIR_LIST` reçoit `str(ctx.list_dir)` tel quel.
`list-dir new l a` pose donc `LISTDIR_LIST=l`, quand `LISTDIR_ROOT` et le `pwd` de la commande sont
absolus. Le plan annonçait « chemin absolu du répertoire-liste ».

La documentation a été adoucie en « le chemin du répertoire-liste » sans entrée au journal de
décisions : l'écart a été effacé plutôt que tranché.

## Pourquoi c'est gênant

Deux variables du même tableau n'offrent pas la même garantie, et rien ne le dit. Une commande qui
fait `cd "$LISTDIR_LIST"` marche depuis un cwd et pas depuis un autre — en `derive`, où le cwd est
l'ancêtre de la liste, un chemin relatif ne résout pas.

## Pour solder

Résoudre `list_dir` en absolu à la construction du `PrefillContext` — `Path.resolve()`, qui ne
touche pas au disque pour un répertoire inexistant — et rétablir la formulation « chemin absolu »
dans la documentation. Ou bien assumer le relatif et l'écrire, avec sa raison.

## Assumé

<OPTIONNEL>
