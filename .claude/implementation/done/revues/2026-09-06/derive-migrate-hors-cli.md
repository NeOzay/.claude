+++
id = "derive-migrate-hors-cli"
title = "`derive` et `migrate` ne sont exercés que par la bibliothèque, jamais par la ligne de commande"
date = 2026-08-24
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n "lancer(\"derive\"\|lancer(\"migrate\"" skills/list-dir/scripts/tests/test_entree_cli.py
(aucun résultat)

$ grep -n "\-\-template\|--dry-run\|--drop" skills/list-dir/scripts/tests/test_entree_cli.py
502:    r = lancer("contract", str(liste), "--template", "revue")
513:    r = lancer("contract", "--def", "jouet", "--template", "revue", cwd=tmp_path)
521:    r = lancer("contract", str(liste), "--template", "absent")
534:    r = lancer("contract", str(liste), "--template", "seule")
598:        "--template",
614:    r = lancer("contract", str(liste), "--template", "../contract")
```

## Verdict

Aucun cas de `test_entree_cli.py` ne lance `derive` ni `migrate` en sous-processus : les six
occurrences de `--template` appartiennent toutes à `contract`, une commande arrivée depuis. La
façade des deux commandes les plus destructrices du paquet — `--template` requis, `--drop`,
`--dry-run` — reste donc non exercée, exactement comme au constat.

Le `Pour solder` nomme sa preuve (`uvx pytest … test_entree_cli.py -q` vert avec ces cas) ; elle
ne peut pas être produite puisque les cas n'existent pas. Rien n'a été payé.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
