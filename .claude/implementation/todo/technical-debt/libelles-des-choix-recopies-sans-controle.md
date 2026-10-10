+++
id = "libelles-des-choix-recopies-sans-controle"
title = "Les libellés des choix de fin de commit sont recopiés dans cinq fichiers, sans contrôle"
date = 2026-10-10
severite = "avertissement"
chantier = "enchainement-du-chantier"
reference = "R7 (audit e06e952), R5 (audit e80dda8)"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le 2026-10-10, les libellés des choix — « Valider et faire la Passation (commit inclus) »,
« Valider et passer à l'Étape suivante », « Valider et attendre », « Valider et commencer la
Passation », « Valider et lancer l'audit de Clôture » — s'écrivent mot pour mot dans `etape.md`,
`confirmation.md`, `execution.md`, `creation.md` et le `SKILL.md` d'implementation-tracker.
`scripts/check_pipeline.py` ne vérifie pas qu'ils restent identiques.

## Pourquoi c'est gênant

Un libellé renommé dans `etape.md` et oublié ailleurs laisse un choix sans suite : le tracker ne
reconnaît plus le choix que git-smart-commit propose. Pour « Valider et faire la Passation (commit
inclus) », le libellé conditionne l'exception d'accord de `confirmation.md` : l'écart ferait
redemander un accord, ou en supposer un.

## Pour solder

Ajouter à `scripts/check_pipeline.py` un contrôle qui relève les libellés de `etape.md`, point 4,
et vérifie que chaque libellé cité ailleurs dans le pipeline y figure à l'identique.

## Assumé

Le 2026-10-10, versé à la Clôture d'`enchainement-du-chantier` plutôt que traité : le contrôle est
un changement de `check_pipeline.py`, hors du Plan.
