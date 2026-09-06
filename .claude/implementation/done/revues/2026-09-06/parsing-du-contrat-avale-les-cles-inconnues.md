+++
id = "parsing-du-contrat-avale-les-cles-inconnues"
title = "Le parsing du contrat accepte en silence ce qu'il ne comprend pas"
date = 2026-08-31
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n 'bool(body.get("required", False))' skills/list-dir/scripts/listdir/contract.py
450:            required=bool(body.get("required", False)),
497:            required=bool(body.get("required", False)),
```
Les deux sites — champs et sections — emploient toujours la même coercition. Aucune clé inconnue
n'est confrontée à une liste de clés reconnues : rien dans `contract.py` ne compare les clés
présentes à celles attendues.

## Verdict

Les deux laxismes sont intacts et toujours symétriques entre `Field` et `Section`. Une clé
`require = true` reste avalée en silence (la section devient facultative), et `required = "false"`
reste coercée en `True` par `bool()` — l'exact contraire de ce qui est écrit.

La question de fond que le `Pour solder` demandait de trancher — contrat fermé ou extensible avec
signalement — n'est tranchée nulle part. L'`Assumé` reste vrai : aucune clé optionnelle n'existe
encore, l'échéance est la première extension. Le report est légitime, la dette est entière.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
