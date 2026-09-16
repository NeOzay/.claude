+++
id = "list-dir-depend-de-gabarit-sans-le-dire"
title = "list-dir dépend désormais de gabarit, et sa documentation ne le dit pas"
date = 2026-09-15
source = "chantier fichier-seme, audit de clôture R5 (`fadddf1`), reconduit par R6 (`5123a3d`) — hors-périmètre assumé au brief"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Depuis le chantier `fichier-seme`, `listdir/__init__.py` localise le paquet `gabarit` (premier
`bin/gabarit` en remontant, puis `PATH`) et échoue à l'import sans lui. `skills/list-dir/SKILL.md` et
ses références n'en disent rien : la dépendance n'est écrite que dans `OUTILLAGE.md`, « Ce dont le
dépôt dépend ». Le `ruff.toml` de list-dir le présente pourtant comme « destiné à être déployé
ailleurs ».

## Pourquoi c'est gênant

Un déploiement de list-dir seul échoue désormais à l'import. L'échec est fermé et nommé
(`ImportError: listdir exige le paquet gabarit…`), mais rien dans le skill ne l'annonce avant qu'on
le rencontre : le prérequis se découvre à l'exécution.

## Pour solder

Écrire la dépendance dans `skills/list-dir/SKILL.md` (« Prérequis ») et renvoyer à
`skills/gabarit/SKILL.md` pour ce qu'une liste en tient (format, contrat, préremplissage). Attention
à l'homonymie relevée par `gabarit-nomme-deux-choses-dans-list-dir`. Vérifier :
`grep -n 'gabarit' skills/list-dir/SKILL.md` → au moins une ligne dans « Prérequis », et
`.venv/bin/python scripts/check_pipeline.py` → conforme.

## Assumé

Délibéré, le 2026-09-15 : le brief de `fichier-seme` exigeait une documentation de list-dir
identique. La mise à jour est attendue au chantier qui branchera implementation-tracker sur gabarit.
