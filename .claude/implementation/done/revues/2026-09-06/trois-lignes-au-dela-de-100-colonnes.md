+++
id = "trois-lignes-au-dela-de-100-colonnes"
title = "Trois lignes du corpus dépassent l'enroulement à 100 colonnes"
date = 2026-08-14
reviewed = 2026-09-06
category = "aggravee"
+++

## Vérifié par

```
$ git ls-files -- skills scripts hooks | grep -E '\.(md|sh)$' | python3 -c "
import sys
n=0
for p in sys.stdin.read().split():
    n += sum(1 for l in open(p, encoding='utf-8').read().split('\n') if len(l) > 100)
print(n)"
157
```
Comptage **en caractères** (`len(l)`), pas en octets — la mesure d'origine du 2026-08-17 utilisait
la même commande et rendait **133**.

## Verdict

Même corpus, même commande, même unité : **157 lignes au-delà de 100 caractères contre 133 au
constat corrigé**, soit **24 de plus**. Le problème s'est étendu depuis la dernière mesure, ce
qui est la définition de `aggravee` : l'écart est chiffré, pas déclaré. La seconde décision que
le `Pour solder` réclame — convention outillée ou état accepté — n'a toujours pas été prise, et
c'est faute de l'avoir prise que le compte monte.

## Action

Reste au registre. Réécrire le **Constat** daté du 2026-09-06 avec la mesure de 157, en
conservant `title`, `id` et `date` d'origine. `category = "aggravee"`, `reviewed = 2026-09-06`.

## Arbitrage

**Suivie.** Constat réécrit le 2026-09-06 : 157 lignes, l'écart de 24 depuis la mesure du
2026-08-17 nommé comme une aggravation réelle, et l'historique des deux corrections de mesure
conservé pour qu'on ne le reprenne pas pour une troisième.
