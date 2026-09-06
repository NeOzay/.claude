+++
id = "prefill-date-preremplie-ecrite-guillemetee"
title = "Un champ date prérempli est écrit entre guillemets, contre la forme nue des dates saisies"
date = 2026-08-31
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

Reproduit le 2026-09-06 — contrat portant `[fields.jour] type = "date"`, `command = "date +%F"` :

```
$ list-dir new l a && cat l/a.md
+++
id = "a"
jour = "2026-09-06"
[…]
+++
```
La valeur est **entre guillemets**, là où une date saisie à la main est écrite nue — les entrées du
registre de dette portent `date = 2026-08-31`, sans guillemets.

```
$ grep -n -A4 "def initial_field" skills/list-dir/scripts/listdir/prefill.py
137:def initial_field(f: Field, item_id: str, ctx: PrefillContext) -> Result[FieldValue]:
```
Aucune conversion en `datetime.date` après `check_value` : la sortie de `command` reste une `str`.

## Verdict

Le constat tient et se reproduit à l'identique. Les deux graphies du même champ coexistent selon
l'origine de la valeur, et rien n'échoue puisque `check_value` accepte `str` comme
`datetime.date` — c'est bien le défaut décrit. La conversion demandée au `Pour solder` n'a pas été
écrite.

Ce n'est pas `pas-une-dette` : un `grep '^date = 2026'` sur une liste mixte en attrape la moitié,
ce qui est un coût réel, pas une préférence de style.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
