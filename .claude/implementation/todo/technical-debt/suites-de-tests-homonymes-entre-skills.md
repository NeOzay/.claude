+++
id = "suites-de-tests-homonymes-entre-skills"
title = "Les suites de `lexique` et de `shadow-skill` ne se lancent pas dans un même `pytest`"
date = 2026-10-15
severite = "avertissement"
chantier = "solder-sept-dettes"
reference = "Journal du Suivi, 2026-10-15"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/lexique/scripts/tests/` et `skills/shadow-skill/scripts/tests/` portent chacun un
`test_lire.py` et un `test_cli.py`, sans `__init__.py`. Lancées dans un même `pytest`, la collecte
échoue : « import file mismatch: imported module 'test_lire' has this __file__ attribute … ». Le
cas se produit sur `master` comme sur la branche du chantier. Il a rendu fausse, telle qu'écrite,
la vérification du Suivi de `solder-sept-dettes`, qui réunissait les quatre suites.

## Pourquoi c'est gênant

Une commande de vérification qui réunit les suites, la forme naturelle, échoue sur des erreurs de
collecte sans qu'aucun test soit faux. Il faut savoir qu'il faut lancer chaque suite à part, et la
commande de tests d'`OUTILLAGE.md` ne couvre aucune de ces deux suites.

## Pour solder

Donner aux fichiers de test des noms propres à leur skill, ou passer pytest en
`--import-mode=importlib` dans une configuration commune, puis vérifier que
`~/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests/ skills/shadow-skill/scripts/tests/`
collecte et passe.

## Assumé

<OPTIONNEL>
