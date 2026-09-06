+++
id = "critere-reussite-faux-dans-sa-lettre"
title = "Un critère de réussite du brief `contrat-pipeline` était faux dans sa lettre"
date = 2026-08-14
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -rn "persistant\|pièce\|état transitoire" skills/intent-brief/references/gabarit-brief.md
(aucun résultat)

$ sed -n '37,42p' skills/intent-brief/references/gabarit-brief.md
## Critères de réussite

Observables et vérifiables. Préférer une commande à une phrase : une commande se rejoue.

- `cargo test auth` passe
- un token expiré renvoie 401 au lieu d'un 500
```

## Verdict

Le « Pour solder, complété » exige qu'un critère de réussite **nomme la pièce persistante** qui
l'établit, et non un état transitoire de l'arbre de travail. Le gabarit de `intent-brief`
demande bien une commande plutôt qu'une phrase, mais **ne dit rien** de la persistance de ce sur
quoi la commande porte : c'est précisément l'écart que les deux occurrences ont produit. La
généralisation reste donc non écrite. Le fait historique (un brief figé porte un critère faux)
est invérifiable, mais l'entrée ne s'y réduit pas — son `Pour solder` est actionnable sur
`gabarit-brief.md`, ce qui l'écarte de `inverifiable`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
