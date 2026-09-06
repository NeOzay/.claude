+++
id = "fence-non-fermee-diagnostic-trompeur"
title = "Une fence non refermée avale les sections suivantes, et les deux messages qui en découlent sont faux"
date = 2026-08-23
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

Le cas résiduel décrit par l'entrée — fence ouverte **avant le premier `## `** — rejoué le
2026-09-06 sur une liste neuve amorcée depuis la définition `technical-debt` :

```
$ list-dir init t_fence --def technical-debt
$ printf '+++\nid = "a"\ntitle = "t"\ndate = 2026-09-06\n+++\n\n```\ndu code jamais referme\n\n## Constat\n\nx\n\n## Pourquoi …\n\ny\n\n## Pour solder\n\nz\n' > t_fence/a.md
$ list-dir validate t_fence; echo "code $?"
t_fence/a.md: section « Constat » — manquante
t_fence/a.md: section « Pourquoi c'est gênant » — manquante
t_fence/a.md: section « Pour solder » — manquante

t_fence : 3 manquements
code 1
```

## Verdict

Le solde que l'entrée s'était fixé est explicite : « le corps du Constat ci-dessus (fence en
préambule) → `validate` code ≠ 0 avec un message **nommant la fence**, et non "section
manquante" ». Le code est bien ≠ 0, mais le message dit trois fois « section manquante » sur trois
sections **écrites dans le fichier**, et ne mentionne la fence nulle part. Le critère n'est donc
pas atteint et le versant préambule reste entier — ni `types.py`/`items.py`/`store.py` ni
`parse_sections` n'ont pris l'une des deux voies proposées.

Le versant « fence dans une section », lui, est bien traité, et l'entrée le consigne déjà : elle
est à jour, pas à corriger.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
