+++
id = "revue-reelle-jamais-menee"
title = "Le flux de revue n'a jamais produit d'archive réelle sous `done/revues/`"
date = 2026-08-23
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ git ls-files .claude/implementation/done/revues/
.claude/implementation/done/revues/2026-08-17-revue.md

$ git log -1 --format='%h %ad %s' --date=short 75dd2a5
75dd2a5 2026-08-17 feat(skills): revue manuelle du registre de dette technique
```
La seule archive commitée est celle du 2026-08-17 — antérieure à cette entrée (2026-08-23) et
produite par une revue **manuelle**, avant la réécriture du flux en listes dérivées. Aucune archive
issue de `/debt-review` n'est commitée à l'instant de cette vérification.

## Verdict

Le `Pour solder` fixe deux conditions cumulatives : un `done/revues/<date>-revue.md` **commité**
dont le préambule porte le compte des entrées instruites, **et** au moins un `move` effectif vers
une liste de sortie au cours de cette passe. Ni l'une ni l'autre n'est établie au moment de la
vérification — la présente revue est en cours, rien n'est encore commité.

Classer `a-solder` sur une passe qu'on est soi-même en train de mener serait exactement le mode de
défaillance que `categories.md` nomme : celui qui vient de faire le travail affirmant qu'il l'a
fait. Le doute laisse donc la dette au registre.

## Action

Maintien au registre pour cette passe. `category = "pertinent"`, `reviewed = 2026-09-06`.

**À soumettre à l'arbitrage** : cette revue produira l'archive attendue et comporte un `move` vers
`technical-debt-solde` (entrée `sortie-du-registre-jamais-exercee`). Une fois ces deux gestes
commités, les conditions du `Pour solder` seront réunies et l'entrée pourra être soldée — soit sur
décision de l'utilisateur en fin de passe, soit à la revue suivante, qui pourra le **constater**
plutôt que l'annoncer.

## Arbitrage

**Suivie.** L'entrée reste au registre avec `category = "pertinent"`. La question de son solde par
cette passe même n'a pas été tranchée : elle dépend des deux `move` différés et du commit de
l'archive. C'est la revue suivante qui pourra le **constater**, ce que le Verdict ci-dessus dit
déjà être la bonne façon de l'établir.
