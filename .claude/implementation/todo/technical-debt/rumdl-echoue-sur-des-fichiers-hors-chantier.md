+++
id = "rumdl-echoue-sur-des-fichiers-hors-chantier"
title = "`uvx rumdl fmt --check .` échoue sur des fichiers que ni ce Chantier ni le formateur n'ont touchés"
date = 2026-10-09
severite = "note"
chantier = "messages-du-pipeline"
reference = "R2"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le 2026-10-09, `uvx rumdl fmt --check .` échoue sur `master` comme sur la branche du Chantier, sur
des fichiers hors de son diff : cinq entrées de `todo/` (`technical-debt/`, `technical-debt-solde/`,
`road-map-fait/`) et `.claude/implementation/lexique-local-tronque.audit.md`, rapport d'audit resté
suivi à la racine de `.claude/implementation/` au lieu de `done/`.

Le 2026-10-10, le chantier `enchainement-du-chantier` a reformaté ces six fichiers (son Étape 6) :
`uvx rumdl fmt --check .` passe. Reste le rapport d'audit orphelin, toujours hors de `done/`.

## Pourquoi c'est gênant

Le critère « `rumdl fmt --check .` passe » ne peut être tenu par aucun Chantier sans reformater ce
qui n'est pas à lui : chaque Brief qui l'écrit doit être borné au diff, et un écart neuf se perd
parmi les anciens.

## Pour solder

Archiver le rapport d'audit orphelin, `lexique-local-tronque.audit.md`, dans `done/` sous son nom
daté.

## Assumé

<OPTIONNEL>
