+++
id = "statusline-hors-des-linters"
title = "`statusline-command.py` échoue à la commande de lint documentée"
date = 2026-08-24
reviewed = 2026-09-06
category = "aggravee"
+++

## Vérifié par

```
$ uvx ruff check . --output-format concise | sed 's/:.*//' | sort | uniq -c
      1 Found 6 errors.
      1 skills/list-dir/scripts/tests/test_contract.py
      2 skills/list-dir/scripts/tests/test_fusion.py
      3 statusline-command.py

$ uvx ruff check scripts skills | tail -1
Found 3 errors.

$ grep -n -A3 '"include"' pyrightconfig.json
4:  "include": [
5-    "skills",
6-    "scripts"
7-  ],
```

## Verdict

**Le problème s'est étendu, et sur les deux axes à la fois.**

*Le compte* : `uvx ruff check .` rendait **3 erreurs** au constat, toutes dans
`statusline-command.py` ; il en rend **6** aujourd'hui. Les 3 d'origine sont toujours là, non
corrigées.

*Le périmètre* : les 3 nouvelles ne sont pas dans le fichier de la racine — elles sont dans
`skills/list-dir/scripts/tests/`, c'est-à-dire **dans** le répertoire que l'entrée citait comme
sain. La commande restreinte `uvx ruff check scripts skills`, qui rendait « All checks passed! »
au constat et servait de repli, sort désormais non nulle elle aussi. La seconde voie du
`Pour solder` — restreindre la commande documentée aux répertoires réellement couverts — ne
suffirait donc plus à rendre la ligne vraie.

`pyrightconfig.json` n'a pas bougé : la racine reste hors de `basedpyright`.

## Action

Reste au registre. Réécrire le **Constat** daté du 2026-09-06 : 6 erreurs, dont 3 hors de
`statusline-command.py`, et le repli `scripts skills` devenu rouge lui aussi.
`category = "aggravee"`, `reviewed = 2026-09-06`.

## Arbitrage

**Suivie.** Constat réécrit le 2026-09-06 : 6 erreurs, dont 3 hors de `statusline-command.py`, et
le repli `uvx ruff check scripts skills` devenu rouge — ce qui invalide la seconde voie du
**Pour solder** et le dit dans l'entrée.
