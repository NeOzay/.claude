+++
gabarit = "brief"
slug = "pipeline-gabarit"
titre = "Brancher le pipeline sur gabarit pour les fichiers qu'il crée depuis un gabarit"
statut = "validé"
execution = "direct"
"créé" = 2026-09-16
+++

## Intention

**Symptôme** : la structure du suivi est écrite à deux endroits (modèle Markdown et semence `suivi`)
sans que rien ne les confronte, et le front matter des fiches est lu par regex, sans grammaire, par
deux lecteurs alignés à la main (dépôt: .claude/implementation/todo/technical-debt/suivi-pose-depuis-un-gabarit-markdown.md,
.claude/implementation/todo/technical-debt/frontmatter-suivi-lu-par-regex.md) — à confirmer
**But** : migrer le pipeline pour qu'il utilise `gabarit`, livré par le dernier chantier (dit), pour
tous les fichiers qu'il crée à partir de gabarits (dit).

## Critères de réussite

- `gabarit check --filled` est exécuté avant la validation du brief (dit)
- `gabarit check --filled` est exécuté après le premier remplissage du suivi, et conditionne le
  début de l'implémentation (dit)
- les dettes `suivi-pose-depuis-un-gabarit-markdown` et `frontmatter-suivi-lu-par-regex` sont
  soldées (dit)
- les fiches de ce chantier sont converties au nouveau format (dit)
- en fin de chantier, une entrée `road-map/` porte le rapport d'audit en liste `list-dir` (dit)

## Hors-périmètre

- les éléments de `done/` ne sont pas touchés (dit)
- le rapport d'audit : il serait mieux porté par une liste `list-dir`, chaque nouvel audit ayant
  son front matter prérempli des audits précédents ; l'ensemble est à discuter et approfondir
  dans un chantier à part, amorcé par une entrée `road-map/` (dit). Son « Gabarit du rapport »
  reste donc dans `audit.md`

## Signaux de dérive

- une skill garde un élément de fiche Markdown — modèle recopiable, liste de sections ou de champs —
  au lieu de renvoyer à la semence, qui est autodescriptive (dit) — le rapport d'audit excepté,
  hors-périmètre

## Contraintes connues de l'utilisateur

- **Existant** : la semence `suivi` existe, le tracker n'y est pas branché (dépôt: skills/gabarit/gabarit/suivi/contract.toml)
- **Existant** : le front matter du suivi est lu en YAML `---` ligne à ligne par `commit_chantier.py` (dépôt: skills/git-smart-commit/scripts/commit_chantier.py:96)
- **Existant** : le contrôle 5 de `check_pipeline.py` lit les chemins du front matter des chantiers archivés (dépôt: scripts/check_pipeline.py:393)
- **Existant** : gabarits en prose aujourd'hui — brief, suivi, rapport d'audit (dépôt: skills/intent-brief/references/gabarit-brief.md, skills/implementation-tracker/references/gabarit-suivi.md, skills/implementation-tracker/references/audit.md « Gabarit du rapport »)
- **Décision** : un lecteur unique de front matter, partagé par `commit_chantier.py` et
  `check_pipeline.py`, lit le TOML `+++` et, en repli, le YAML `---` des archives de `done/` (dit)
- **Décision** : le brief et le suivi de ce chantier sont convertis dès que leurs semences
  existent ; le brief reste en YAML `---` d'ici là (dit)
- **Format** : gabarit n'accepte que le front matter TOML `+++` (dépôt: .claude/implementation/done/2026-09-16-fichier-seme.brief.md)

## Incertitudes à lever en plan

— aucune
