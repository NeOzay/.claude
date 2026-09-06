+++
id = "git-smart-commit-illisible-seul"
title = "`git-smart-commit` n'est plus lisible sans `implementation-tracker`"
date = 2026-08-14
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n "implementation-tracker/references" skills/git-smart-commit/references/squash.md
8:[Branche et commits](../../implementation-tracker/references/contrat.md#branche-et-commits).

$ test -f skills/implementation-tracker/references/contrat.md && echo "cible présente"
cible présente
```

## Verdict

Le renvoi existe toujours et sa cible résout : la dépendance de `git-smart-commit` vers le
tracker est intacte, donc le constat tient. Le `Pour solder` est explicitement passif (« rien
tant que le tracker ne bouge pas »), mais le fait, lui, se vérifie par commande — ce n'est donc
pas `inverifiable`, qui vise les faits historiques qu'aucune lecture du dépôt ne peut établir.
Une seule occurrence, comme au constat d'origine.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
