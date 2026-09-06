+++
id = "sections-de-categories-jamais-confrontees-au-contrat"
title = "les sections de categories.md recopient l'ensemble des valeurs du contrat"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ diff <(list-dir contract --def technical-debt --template review --values category) \
       <(grep -oP '^## .*— `\K[a-z-]+' skills/debt-review/references/categories.md) \
  && echo IDENTIQUES
IDENTIQUES

$ grep -rn "categories.md" scripts/check_pipeline.py
(aucun résultat)

$ ls .claude/implementation/todo/technical-debt/.list/
backup/  semence/  templates/  contract.toml
```
(pas de `commands/` : aucune commande propre à la liste n'a été créée.)

## Verdict

Les deux ensembles **coïncident aujourd'hui** — mais ce n'est pas ce que l'entrée décrit. La dette
est que **rien ne le vérifie** : la commande du `Pour solder` existe et fonctionne, elle n'est
lancée par personne. Aucune des trois destinations envisagées ne l'a accueillie — ni
`.list/commands/` (le répertoire n'existe pas), ni `scripts/check_pipeline.py` (qui ignore
`categories.md`), ni la procédure de `debt-review`.

Ce n'est donc pas `a-solder` : la coïncidence constatée est un état, pas un contrôle, et c'est
précisément l'écart que `categories.md` interdit de confondre. Une valeur ajoutée demain au contrat
laisserait toujours la prose en décrire une de moins, en silence.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
