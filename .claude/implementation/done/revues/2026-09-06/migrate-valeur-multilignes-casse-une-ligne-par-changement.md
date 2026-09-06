+++
id = "migrate-valeur-multilignes-casse-une-ligne-par-changement"
title = "Une valeur préremplie multi-lignes casse l'invariant « un changement, une ligne » de migrate"
date = 2026-08-31
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n 'Change(item.path, subject, f"ajoutée' skills/list-dir/scripts/listdir/store.py
391:                changes.append(Change(item.path, subject, f"ajoutée, {corps}"))

$ grep -n 'join' skills/list-dir/scripts/listdir/commands/migrate.py
63:    detail = "\n".join(str(c) for c in changes)
```

## Verdict

Le libellé du `Change` interpole toujours `corps` tel quel, sans troncature ni `repr()`. Une valeur
préremplie multi-lignes produit donc autant de lignes de sortie qu'elle a de lignes, et l'invariant
« un changement, une ligne » sur lequel se grep la sortie de `migrate` est faux dès qu'un contrat
déclare un `command` multi-lignes.

Le `Pour solder` — première ligne suivie de « … », ou `repr()` — n'a pas été appliqué. Aucun
nouveau site d'interpolation n'est apparu : `pertinent`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
