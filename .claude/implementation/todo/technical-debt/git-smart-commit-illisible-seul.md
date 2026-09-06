+++
id = "git-smart-commit-illisible-seul"
title = "`git-smart-commit` n'est plus lisible sans `implementation-tracker`"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R10 du rapport d'audit."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`squash.md` renvoie désormais à
`../../implementation-tracker/references/contrat.md`. Un déplacement ou un renommage du tracker
casse cette référence.

## Pourquoi c'est gênant

`git-smart-commit` est la seule skill du pipeline qui serve largement
hors de lui ; elle porte maintenant une dépendance vers une skill de chantier.

## Pour solder

rien tant que le tracker ne bouge pas. Si le noyau devait migrer vers un
emplacement neutre, c'est ce renvoi qui le motiverait.

## Assumé

conséquence directe de la décision d'emplacement du noyau, prise au cadrage. Le
contrôle 1 du garde-fou rend la casse visible (chemin mort), ce qui est le bon niveau de garantie.
