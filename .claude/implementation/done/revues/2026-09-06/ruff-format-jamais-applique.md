+++
id = "ruff-format-jamais-applique"
title = "Le formatage ruff n'a jamais été appliqué au paquet list-dir"
date = 2026-08-30
reviewed = 2026-09-06
category = "aggravee"
+++

## Vérifié par

```
$ cd skills/list-dir && uvx ruff format --check . | tail -1
8 files would be reformatted, 39 files already formatted

$ uvx ruff format --check . | grep -- '-->' | sed 's/.*--> //;s/:.*//' | sort -u
references/extension.md
scripts/tests/test_contract.py
scripts/tests/test_derive_merge.py
scripts/tests/test_fusion.py
scripts/tests/test_items.py
scripts/tests/test_loader.py
scripts/tests/test_move.py
scripts/tests/test_provenance.py

$ grep -n "ruff format" skills/implementation-tracker/references/contrat.md
(aucun résultat)
```

## Verdict

**Le compte est passé de cinq à huit.** Les cinq d'origine sont toujours là
(`references/extension.md`, `test_contract.py`, `test_items.py`, `test_loader.py`,
`test_move.py`), et **trois s'y sont ajoutés** : `test_fusion.py`, `test_derive_merge.py` et
`test_provenance.py` — trois suites écrites après le constat, c'est-à-dire exactement le mode de
défaillance que l'entrée annonçait : « rien n'empêche un chantier d'en ajouter un ».

`contrat.md` ne déclare toujours pas `ruff format --check` : la question de fond (le formatage
fait-il partie du contrat du paquet ?) n'est pas tranchée, dans un sens ni dans l'autre.

L'écart chiffré — trois fichiers de plus en une semaine — fait sortir cette entrée de `pertinent`.

## Action

Reste au registre. Réécrire le **Constat** daté du 2026-09-06 : huit fichiers, dont trois postérieurs
au constat d'origine. `category = "aggravee"`, `reviewed = 2026-09-06`.

## Arbitrage

**Suivie.** Constat réécrit le 2026-09-06 : huit fichiers, dont trois suites postérieures au
constat d'origine, nommées. La question de fond (le formatage fait-il partie du contrat du
paquet ?) reste ouverte au **Pour solder** — c'est elle qui tient l'entrée au registre.
