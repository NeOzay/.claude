+++
gabarit = "suivi"
slug = "pipeline-gabarit"
titre = "Brancher le pipeline sur gabarit pour les fichiers qu'il crée depuis un gabarit"
branche = "pipeline-gabarit"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
execution = "direct"
plan = ".claude/implementation/done/2026-09-20-pipeline-gabarit.plan.md"
brief = ".claude/implementation/done/2026-09-20-pipeline-gabarit.brief.md"
audit = ".claude/implementation/done/2026-09-20-pipeline-gabarit.audit.md"
"créé" = 2026-09-19
maj = 2026-09-20
+++

## Objectif et périmètre

**Symptôme** : la structure du suivi est écrite à deux endroits (modèle Markdown et semence `suivi`)
sans que rien ne les confronte, et le front matter des fiches est lu par regex, sans grammaire, par
deux lecteurs alignés à la main — à confirmer.
**But** : migrer le pipeline pour qu'il utilise `gabarit` pour tous les fichiers qu'il crée à
partir de gabarits.
**Critères de réussite** :
- `gabarit check --filled` est exécuté avant la validation du brief ;
- `gabarit check --filled` est exécuté après le premier remplissage du suivi, et conditionne le
  début de l'implémentation ;
- les dettes `suivi-pose-depuis-un-gabarit-markdown` et `frontmatter-suivi-lu-par-regex` sont
  soldées ;
- les fiches de ce chantier sont converties au nouveau format ;
- en fin de chantier, une entrée `road-map/` porte le rapport d'audit en liste `list-dir`.

**Hors-périmètre** :
- les éléments de `done/` ne sont pas touchés ;
- le rapport d'audit et son « Gabarit du rapport » dans `audit.md` (chantier à part, amorcé par
  l'entrée `road-map/`).

**Élargissement du 2026-09-20**, accepté par l'utilisateur : corriger R4 de l'audit de clôture
(deux graphies du même champ `date` selon l'origine de la valeur) et solder la dette
`prefill-date-preremplie-ecrite-guillemetee` qui le porte. Cela touche `skills/gabarit` et
`skills/list-dir`, jusque-là hors du diff.

**Signaux de dérive** :
- une skill garde un élément de fiche Markdown — modèle recopiable, liste de sections ou de
  champs — au lieu de renvoyer à la semence, qui est autodescriptive ; le rapport d'audit excepté.

## Étapes

- [x] 1. Lecteur unique `fiche` — `skills/implementation-tracker/scripts/fiche.py`, `tests/test_fiche.py` — vérif: `.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests`
- [x] 2. Contrôle 5 sur `fiche` — `scripts/check_pipeline.py`, `scripts/tests/test_controles_4_5.py` — vérif: `.venv/bin/python -m pytest scripts/tests && python3 scripts/check_pipeline.py`
- [x] 3. `commit_chantier` : lecture par `fiche`, écriture par `gabarit` — `skills/git-smart-commit/scripts/commit_chantier.py`, ses tests — vérif: `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests && commit-chantier lettre`
- [x] 4. Corriger R1, R2, R3 de l'audit intermédiaire — `skills/implementation-tracker/{ruff.toml,pyrightconfig.json}`, `commit_chantier.py`, ses tests — vérif: `uvx ruff check scripts skills/implementation-tracker/scripts skills/git-smart-commit/scripts && PATH=/usr/bin:/bin .venv/bin/python -m pytest skills/git-smart-commit/scripts/tests`
- [x] 5. Corriger R1, R2 de l'audit `d32eeda` — `commit_chantier.py`, ses tests — vérif: `PATH=/usr/bin:/bin .venv/bin/python -m pytest -rs skills/git-smart-commit/scripts/tests`
- [x] 6. Semence `brief`, semence `suivi` autodescriptive — `skills/gabarit/gabarit/{brief,suivi}/contract.toml`, `skills/gabarit/SKILL.md` — vérif: `gabarit contract brief && gabarit new brief "$T/b.md" && gabarit check "$T/b.md"`
- [x] 7. Brancher `intent-brief` — `skills/intent-brief/SKILL.md`, suppression de `references/gabarit-brief.md` — vérif: `! grep -rn "gabarit-brief" skills agents && python3 scripts/check_pipeline.py`
- [x] 8. Convertir le brief de ce chantier — `.claude/implementation/pipeline-gabarit.brief.md` — vérif: `gabarit check .claude/implementation/pipeline-gabarit.brief.md --filled`
- [x] 9. Brancher `implementation-tracker` — `skills/implementation-tracker/SKILL.md`, `references/contrat.md`, suppression de `references/gabarit-suivi.md` — vérif: `! grep -rn "gabarit-suivi" skills agents && python3 scripts/check_pipeline.py`
- [x] 10. Citer les champs au format TOML — références git-smart-commit, `cloture.md`, `road-map.md`, `audit.md:61,76`, les deux `SKILL.md`, agents, `prose.md` — vérif: `! grep -rnE '\`(statut|maj|session|lettre|base|execution|plan|brief|audit|road-map): [^\`]+\`' skills agents --exclude-dir=synced && python3 scripts/check_pipeline.py`
- [x] 11. Solder les trois dettes (dont `impl-list-sans-configuration-de-linters`) — `todo/technical-debt/` → `todo/technical-debt-solde/` — vérif: `list-dir validate .claude/implementation/todo/technical-debt-solde --filled`
- [x] 12. Entrée road-map du rapport d'audit — `todo/road-map/` — vérif: `list-dir validate .claude/implementation/todo/road-map --filled`
- [x] 13. Corriger R1, R2, R3 de l'audit de clôture `5e8df3a` — `references/dette.md`, les deux `SKILL.md` — vérif: `! grep -rn '^\`\`\`markdown' skills/intent-brief skills/implementation-tracker --exclude=audit.md && python3 scripts/check_pipeline.py`
- [x] 14. Corriger R4 et solder `prefill-date-preremplie-ecrite-guillemetee` — `gabarit/prefill.py`, `gabarit/scripts/tests/test_date.py`, tests `list-dir`, `todo/technical-debt-solde/` — vérif: `.venv/bin/python -m pytest scripts/tests skills/*/scripts/tests && list-dir validate .claude/implementation/todo/technical-debt-solde --filled`

## État courant

**Prochaine action** : relancer un audit de clôture sur les correctifs des étapes 13 et 14.
**Vérification** : la « Vérification d'ensemble » du plan.
**Dernier audit** : `14d6464` — RÉSERVES — 2026-09-20 (clôture)
**Notes** : brief et suivi sont au format de leur semence (suivi posé par `gabarit new suivi`,
brief converti à l'étape 8). Le plan garde sa numérotation
d'origine : son étape N est l'étape N+2 du suivi à partir de 4.

## Journal de décisions

- **2026-09-19** — Lecteur unique `fiche.py` en bibliothèque standard (tomllib, YAML en repli pour
  les archives), écriture par `gabarit.items`. *Pourquoi* : `check_pipeline.py` tourne sous le
  python3 du PATH, sans tomlkit. *Rejeté* : écrivain TOML par regex.
- **2026-09-19** — `audit.md:61,76` alignés au TOML malgré le hors-périmètre, les règles de
  `contrat.md#frontmatter` gardées (propositions Q1 et Q5 de `plan-reviewer`). *Pourquoi* : sans
  cela, des consignes YAML resteraient pour un suivi TOML.
- **2026-09-19** — `commit_chantier` nomme tout module manquant par `ModuleNotFoundError.name`, et
  importe ses bibliothèques avant `--dry-run`. *Pourquoi* : un refus, jamais une trace Python.
  *Rejeté* : liste de dépendances en dur.
- **2026-09-19** — Brief converti au format de sa semence : seul le front matter change, le corps
  validé est recopié à l'identique et `créé` garde sa date d'origine. *Pourquoi* : le brief est
  figé ; seul son format devait bouger.
- **2026-09-20** — La structure d'une fiche n'est déclarée qu'à un seul endroit : `dette.md` perd
  ses deux blocs recopiables au profit d'un renvoi au contrat de liste, et les deux skills
  cessent d'énumérer les blocs d'`Objectif et périmètre`. *Pourquoi* : arbitrage du signal de
  dérive. *Rejeté* : restreindre la commande qui contrôle ce signal.
- **2026-09-20** — `gabarit.prefill.initial_field` convertit une date préremplie en
  `datetime.date` après `check_value` : `gabarit` et `list-dir` posent la même graphie nue que les
  dates saisies. *Pourquoi* : la dette `prefill-date-preremplie-ecrite-guillemetee` nommait ce
  correctif ; elle est soldée par lui. *Rejeté* : aligner `commit_chantier` sur les guillemets.
- **2026-09-20** — Clôture sur l'audit `14d6464` (RÉSERVES) : les dates du suivi réécrites nues à
  la main, les trois `E501` de `skills/list-dir/` versées au registre. *Pourquoi* : arbitrage de
  l'utilisateur, le correctif des E501 touche des fichiers étrangers au chantier.
