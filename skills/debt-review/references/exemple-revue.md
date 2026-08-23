# Sept fiches instruites, une par catégorie

Ce que le modèle écrit dans une fiche, une fois `derive` passé : les deux champs et les trois
sections requises, sur les sept verdicts possibles. La huitième fiche montre une section
`Arbitrage` remplie — le seul ajout de l'Étape 4.

Ce qui est reproduit ici est le **corps** d'une fiche, tel qu'il apparaîtrait dans
`done/revues/<AAAA-MM-DD>/<id>.md`. Le front matter est écrit par `derive` : `id`, `title` et `date`
sont reportés de l'entrée, seuls `category` et `reviewed` sont à remplir.

> **Les entrées ci-dessous sont fictives**, ainsi que le dépôt qu'elles décrivent — un service de
> commandes en Python qui n'existe pas. C'est délibéré : un exemple bâti sur une vraie entrée du
> registre livre un verdict pré-mâché sur une dette que le relecteur va rencontrer, et le pousse à
> recopier ce verdict au lieu d'exécuter sa commande. Aucun intitulé d'ici ne doit figurer dans
> `technical-debt`.

---

## `a-solder` — Le cache de sessions n'expire jamais

```markdown
category = "a-solder"
reviewed = 2026-09-02

## Vérifié par

`grep -n 'ttl' orders/cache.py` → `ttl=1800` passé au constructeur, depuis le commit `4f1c9ab`.

## Verdict

La dette a été payée : les entrées de cache expirent, le problème décrit ne se reproduit plus.

## Action

`move` vers `technical-debt-solde`, puis section `## Soldé le` portant la commande ci-dessus.
```

## `non-pertinent` — Le module `legacy/xmlrpc.py` n'a aucun test

```markdown
## Vérifié par

`ls orders/legacy/xmlrpc.py` → `No such file or directory`, code de sortie 2.

## Verdict

L'élément cité n'existe plus : le module a été supprimé, pas testé. Rien n'a été réparé, d'où
`non-pertinent` et non `a-solder`.

## Action

`move` vers `technical-debt-ecarte`, motif `non pertinent`.
```

## `doublon` — Le timeout du client HTTP n'est pas configurable

```markdown
## Vérifié par

Sans objet : la preuve est l'`id` de l'entrée conservée.

## Verdict

Dit la même chose que `client-http-sans-timeout`, datée du 2025-06-19, qui est **la plus ancienne
des deux** et donc celle qui est conservée.

## Action

`move` vers `technical-debt-ecarte`, motif `doublon`, en nommant `client-http-sans-timeout`.
```

## `pas-une-dette` — Les noms de variables du module de facturation sont abrégés

```markdown
## Vérifié par

`grep -rnc '\bqty\b\|\bamt\b' orders/billing.py` → 23 occurrences, le constat tient toujours.

## Verdict

Exact, mais c'est une préférence de style qu'aucun critère ne porte — exclue du registre par
construction.

## Action

`move` vers `technical-debt-ecarte`, motif `pas une dette`.
```

## `aggravee` — Trois vues dupliquent la règle de remise

```markdown
## Vérifié par

`grep -rln 'discount_rate' orders/views/` → 5 fichiers, là où l'entrée en décrivait 3.

## Verdict

Toujours vrai, et deux vues de plus qu'à l'origine.

## Action

L'entrée ne bouge pas : réécrire son **Constat**, daté du jour, et écrire `category` et `reviewed`.
```

## `pertinent` — Le client HTTP ne fixe aucun timeout

```markdown
## Vérifié par

`grep -rn 'requests.get\|requests.post' orders/ | grep -vc timeout` → 7 appels sur 7 sans timeout.

## Verdict

Inchangé depuis le constat d'origine.

## Action

Rien à déplacer ; seuls `category` et `reviewed` sont écrits sur l'entrée.
```

## `inverifiable` — La migration 0042 n'a jamais été rejouée sur une copie de production

```markdown
## Vérifié par

Sans objet : le constat porte un fait historique, pas un état du code. Aucune lecture du dépôt ne
peut établir qu'une opération n'a pas eu lieu ailleurs.

## Verdict

Restera vrai indéfiniment ; seul un usage réel peut le solder.

## Action

Rien à déplacer ; `category = "inverifiable"` et `reviewed` à la date du jour.
```

---

## Une fiche arbitrée

La section `Arbitrage` est écrite à l'Étape 4, après que l'utilisateur a tranché — et par elle
seule. Ici, un verdict **renversé** : `category` et le **Verdict** ont été corrigés en même temps,
pour que la fiche ne dise pas le contraire de ce qu'elle porte.

```markdown
## Arbitrage

Renversé le 2026-09-02 : classée `pas-une-dette` à l'instruction, l'utilisateur la maintient au
registre — l'abréviation gêne la relecture d'un module facturé au client, ce qui est un critère.
`category` passe à `pertinent`, le **Verdict** est réécrit en conséquence.
```

Laissée au marqueur, la section n'apparaît pas dans le rapport aggloméré : une fiche que personne
n'a discutée n'a pas de ligne d'arbitrage vide à montrer.
