+++
id = "marqueurs-recopies-dans-gabarits"
title = "Les deux marqueurs sont recopiés en dur dans les gabarits, hors de tout contrôle"
date = 2026-08-23
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n "À REMPLIR\|OPTIONNEL" .claude/implementation/todo/technical-debt/.list/templates/review.md
6:contrat — requise à `<À REMPLIR>`, facultative à `<OPTIONNEL>` — et rien d'autre.
26:<À REMPLIR>
30:<À REMPLIR>
34:<À REMPLIR>
38:<OPTIONNEL>

$ grep -n "REMPLIR\|OPTIONNEL\|PLACEHOLDER\|templates" scripts/check_pipeline.py
(aucun résultat)
```

## Verdict

Les marqueurs sont toujours écrits en dur dans le gabarit — quatre fois comme corps de section,
plus une citation dans le préambule, soit **cinq occurrences** —, et le garde-fou
(`scripts/check_pipeline.py`, seul contrôle outillé du corpus) ne connaît ni les marqueurs ni le
répertoire `.list/templates/`. Aucune des deux voies du `Pour solder` n'a été prise : ni extension
du contrôle de définition unique, ni pose des marqueurs par `derive`.

Le décompte diffère de celui du constat (« quatre fois au total ») parce que celui-ci ne comptait
que les corps de section, pas la citation du préambule. Ce n'est pas une extension du problème :
la ligne 6 énonce la règle et n'est pas une duplication opérante. Donc `pertinent`, pas `aggravee`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
