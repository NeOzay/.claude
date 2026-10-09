+++
id = "rapport-audit-en-liste"
title = "Porter le rapport d'audit par une liste `list-dir` plutôt que par un modèle en prose"
date = 2026-09-19
source = "chantier `pipeline-gabarit`, cadrage du brief — idée de l'utilisateur, laissée hors-périmètre"
+++

## À faire

Le rapport d'audit `<slug>.audit.md` est le dernier fichier du pipeline recopié depuis un modèle
en prose (« Gabarit du rapport » de `audit.md`), avec des sections répétées à chaque audit.
L'idée : en faire une liste `list-dir`, un audit par élément, dont le front matter est prérempli à
partir des audits précédents du chantier. L'ensemble est à discuter et à approfondir avant tout
chantier : forme de la liste, emplacement, préremplissage, archivage à la clôture.

## Références

- `skills/implementation-tracker/references/audit.md`, section « Gabarit du rapport »
- `agents/implementation-auditor.md`, qui crée et appende le rapport
- le rapport d'audit de `pipeline-gabarit` (archivé en `done/` à sa clôture) : plusieurs audits
  appendus dans un même fichier
- chantier `pipeline-gabarit` (brief, hors-périmètre) : brief et suivi posés par leurs semences
  `gabarit`, le rapport d'audit volontairement laissé de côté
- `skills/list-dir/SKILL.md` et `skills/gabarit/SKILL.md` : préremplissage `command` d'un élément
