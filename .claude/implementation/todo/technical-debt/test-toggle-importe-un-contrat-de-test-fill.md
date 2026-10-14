+++
id = "test-toggle-importe-un-contrat-de-test-fill"
title = "`test_toggle.py` importe `CONTRAT_FILL` depuis `test_fill`"
date = 2026-10-14
severite = "note"
chantier = "list-dir-fill-override"
reference = "R4"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le 2026-10-14, `skills/list-dir/scripts/tests/test_toggle.py` fait `from test_fill import
CONTRAT_FILL`, un contrat défini dans un autre fichier de test, alors que les contrats partagés
des tests vivent dans `jouet.py`. Relevé à l'audit `01-3ec5803`.

## Pourquoi c'est gênant

Un fichier de test dépend d'un autre : lancer ou déplacer `test_fill.py` seul change ce que
`test_toggle.py` importe. Aucun test ne casse aujourd'hui.

## Pour solder

Déplacer `CONTRAT_FILL` dans `jouet.py`, et importer de là dans `test_fill.py` comme dans
`test_toggle.py`.

## Assumé

<OPTIONNEL>
