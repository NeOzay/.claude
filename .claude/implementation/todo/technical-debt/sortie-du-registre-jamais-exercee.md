+++
id = "sortie-du-registre-jamais-exercee"
title = "La moitié « sortie du registre » de `debt-review` n'a jamais été exercée"
date = 2026-08-17
source = "Identifié par `revue-dette`, R12 du rapport d'audit de clôture."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

la première passe réelle du skill n'a produit aucune des quatre catégories qui font
sortir une entrée : ni `a-solder`, ni `non-pertinent`, ni `doublon`, ni `pas-une-dette`. Le fichier
`technical-debt-ecarte.md` n'existe donc pas, son préambule n'a jamais été rédigé, le champ
`**Écartée le <date> — <motif>**` jamais écrit, et le déplacement vers `technical-debt-solde.md`
jamais effectué par ce skill.
Établi par : `ls .claude/implementation/todo/` → `README.md`, `technical-debt.md`,
`technical-debt-solde.md` — trois fichiers, pas quatre.

## Pourquoi c'est gênant

quatre catégories sur sept sont validées par le seul tri de l'exemple
fictif. Le premier écartement réel sera aussi le premier test de ce chemin, et il s'exécutera sur
une entrée qu'on **retire** d'un fichier : le mode de défaillance y est la perte, pas l'erreur
visible.

## Pour solder

constater au premier écartement réel que l'entrée atterrit bien dans
`technical-debt-ecarte.md` avec son motif et sa preuve, et que le contrôle de conservation reste
juste. C'est le même mode de solde que pour les deux entrées d'audit jamais mené : un usage réel,
pas une relecture.

## Assumé

la revue du 2026-08-17 n'avait rien à écarter — les 14 entrées tiennent toutes. On ne
fabrique pas une sortie de registre pour éprouver un chemin de code.
