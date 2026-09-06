+++
id = "listdir-list-non-absolue"
title = "LISTDIR_LIST n'est pas absolue, contrairement à LISTDIR_ROOT et au plan"
date = 2026-08-31
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n 'env\["LISTDIR_LIST"\]' skills/list-dir/scripts/listdir/prefill.py
84:    env["LISTDIR_LIST"] = str(ctx.list_dir)
```
Reproduit : contrat portant `[fields.ou] command = "echo \"$LISTDIR_LIST\""`, puis

```
$ list-dir new l a && cat l/a.md
+++
id = "a"
ou = "l"
+++
```
La valeur rendue est `l`, le chemin **relatif** passé sur la ligne de commande.

## Verdict

Le constat tient exactement : `LISTDIR_LIST` reçoit toujours `str(ctx.list_dir)` sans
`resolve()`, et rend donc un chemin relatif quand l'appelant en a passé un — alors que
`LISTDIR_ROOT` est absolu par construction (`git rev-parse --show-toplevel`). Ni la résolution en
absolu, ni le choix inverse assumé et écrit, n'ont été faits.

Le défaut est bien celui décrit et n'a pas de nouvelle occurrence : `pertinent`, pas `aggravee`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
