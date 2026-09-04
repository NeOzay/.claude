+++
id = "reseed-sans-test-cli"
title = "reseed n'a aucun test de bout en bout par la ligne de commande"
date = 2026-09-04
source = "chantier peremption-contrat, audit de clôture ddebb2b, R4"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`reseed` est couvert par des tests de bibliothèque seulement : `test_reseed.py` appelle
`provenance.reseed()` directement. Aucun test ne passe par `list-dir reseed`. La seule
vérification CLI ajoutée par le chantier porte sur `init --def` discordant et sur
l'avertissement de provenance de `validate`.

C'est précisément cet angle mort qui a laissé passer le premier bloquant de l'audit : la
bibliothèque rendait le code 2, `commands/reseed.py` le ramenait à 1, et aucun test de
bibliothèque ne pouvait le voir. Le correctif a ajouté un test CLI pour `init`, pas pour
`reseed`.

## Pourquoi c'est gênant

Ce qu'un test de bibliothèque ne voit jamais, c'est la couche de traduction : code de retour,
canal de sortie, mise en page du rapport. Trois comportements de `reseed` n'existent que là —
le refus d'un conflit, le passage de `--force`, l'absence d'écriture sous `--dry-run` — et
chacun peut se dégrader sans faire tomber un seul des tests actuels.

Mode de défaillance : un `reseed` qui rendrait 0 sur un conflit. Un script appelant enchaînerait
sur un contrat non rattrapé en croyant l'avoir rattrapé, et rien ne le dirait.

## Pour solder

Ajouter à `scripts/tests/test_entree_cli.py` les cas de bout en bout de `reseed` : conflit
(code non nul, contrat inchangé), `--force` sur une liste gelée (code 0), `--dry-run`
(rien écrit), et nom discordant (code 2). Le harnais `lancer()` existe déjà et les monte en
sous-processus.

## Assumé

Le chantier a livré la couverture de bibliothèque et un seul test CLI, sur le défaut qui avait
été constaté. L'utilisateur a arbitré de clore avec cette réserve plutôt que de compléter la
couverture avant.
