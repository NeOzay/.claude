+++
gabarit = "suivi"
slug = "enchainement-du-chantier"
titre = "Réduire les allers-retours d'un Chantier : un accord par geste, des choix de fin d'Étape qui enchaînent"
branche = "enchainement-du-chantier"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-10-enchainement-du-chantier.plan.md"
brief = ".claude/implementation/done/2026-10-10-enchainement-du-chantier.brief.md"
audit = ".claude/implementation/done/2026-10-10-enchainement-du-chantier.audit.md"
road-map = "enchainement-du-chantier"
skills = ["skill-convention"]
"créé" = 2026-10-09
maj = 2026-10-10
+++

## Objectif et périmètre

**Symptôme** : près de la moitié des messages de l'utilisateur sont procéduraux — « oui », « 1 »,
« Valider », « Commit et continue », « Commit et fait la Passation » puis « 1 », « Commence ».
Chaque tour relit tout le contexte.

**But** : qu'un passage obligé d'un Chantier — validation du Plan, commit `<L>E0` et Passation,
fin d'Étape, reprise — tienne en un seul tour de l'utilisateur.

**Critères de réussite** :

- **C1** — `creation.md` suit cet ordre : `plan-reviewer` lancé une fois, son verdict consigné
  dans une section en tête du Plan, `AskUserQuestion`, Plan corrigé selon les réponses,
  `ExitPlanMode`. Plus de point Passation séparé : elle devient le choix 1 du commit `<L>E0`.
- **C2** — `etape.md` fait proposer le commit `<L>E0` avec deux choix : « Valider et faire la
  Passation », « Valider et passer à l'Étape suivante ».
- **C3** — `etape.md` fait proposer le commit d'Étape ou de Retouche avec trois choix : « Valider
  et passer à l'Étape suivante », « Valider et attendre », « Autre chose » ; au-delà de 300 000
  tokens, « Valider et commencer la Passation » s'y ajoute ; après la dernière Étape, le premier
  devient « Valider et lancer l'audit de Clôture ».
- **C4** — `execution.md` lance `contexte` avant de proposer le commit d'Étape ou de Retouche, plus
  après.
- **C5** — `confirmation.md` garde « un accord ne vaut que pour son commit », avec pour seule
  exception écrite le commit de Passation couvert par « Valider et faire la Passation ».
- **C6** — la Phase 3 de `SKILL.md` rend un court message : l'Étape en cours, la prochaine action,
  les blocages, puis la proposition de commencer l'Étape X ; les écarts restent signalés.
- **C7** — la semence `brief` prescrit la numérotation des critères (`**C1** — …`) et des signaux
  (`**S1** — …`).
- **C8** — la Phase 6 d'`intent-brief` fait proposer la validation du Brief dans un message dédié,
  avec deux choix — « Valider le Brief et passer au Plan », « Autre chose » — ; seule une réponse
  à cette proposition passe `statut` à `validé`.
- **C9** — `uvx rumdl fmt --check .` passe.

**Hors-périmètre** :

- La règle `ask` sur `git commit` dans `settings.json`, et le « commit » lancé sans proposition
  préalable.
- La forme des messages du pipeline (Chantier `messages-du-pipeline`, livré).
- Le fond de l'audit — verdict, relance, forme du rapport : entrée `refonte-de-l-audit`.

**Signaux de dérive** :

- **S1** — un commit part sans que l'utilisateur ait choisi un des choix proposés, hors le commit
  de Passation couvert par le choix 1 de `<L>E0`.
- **S2** — le diff touche au bloc `permissions` de `settings.json`, ou à la règle absolue du
  `CLAUDE.md` racine.
- **S3** — la reprise démarre une Étape sans la réponse de l'utilisateur.
- **S4** — `plan-reviewer` est relancé sur le Plan corrigé.
- **S5** — les seuils de 300 000 ou de 400 000 tokens changent.
- **S6** — le diff touche au fond de l'audit — verdict, relance, rapport,
  `agents/implementation-auditor.md` — ou à la forme des messages hors des choix.

## Étapes

- [x] 1. Choix de fin de commit, côté git-smart-commit —
      `skills/git-smart-commit/references/etape.md`, `confirmation.md` — vérif:
      `grep -n "Valider et faire la Passation" skills/git-smart-commit/references/confirmation.md && python3 scripts/check_pipeline.py`
- [x] 2. Fin d'Étape et Passation, côté tracker —
      `skills/implementation-tracker/references/execution.md`, `SKILL.md` — vérif:
      `awk '/Étape terminée/ { exit !(index($0,"contexte") < index($0,"propos")) }' skills/implementation-tracker/references/execution.md && python3 scripts/check_pipeline.py`
- [x] 3. Création : relecture du Plan, `<L>E0` et Passation —
      `skills/implementation-tracker/references/creation.md`, `contrat.md` — vérif:
      `grep -n "## Relecture" skills/implementation-tracker/references/creation.md && python3 scripts/check_pipeline.py`
- [x] 4. Reprise en un court message — `skills/implementation-tracker/SKILL.md` — vérif:
      `! grep -n "commandes de vérification à rejouer" skills/implementation-tracker/SKILL.md && python3 scripts/check_pipeline.py`
- [x] 5. Brief : numérotation et validation — `skills/gabarit/gabarit/brief/contract.toml`,
      `skills/intent-brief/SKILL.md` — vérif:
      `grep -n "Valider le Brief et passer au Plan" skills/intent-brief/SKILL.md && gabarit check .claude/implementation/enchainement-du-chantier.brief.md --filled`
- [x] 6. Formatage des six fichiers hors Chantier — `.claude/implementation/` — vérif:
  `uvx rumdl fmt --check .`

## État courant

**Prochaine action** : Clôture — audit par `implementation-auditor`.

**Vérification** :
`python3 scripts/check_pipeline.py && ~/.claude/.venv/bin/python -m pytest scripts/tests/ -q && uvx rumdl fmt --check .`

**Dernier audit** : e80dda8 — RÉSERVES — 2026-10-10

**Notes** : —

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien.

**À savoir** :

- `uvx rumdl check .` relève aussi des écarts dans `CLAUDE.md`, `skills/debt-review/SKILL.md` et
  `shadow-skills/`, mais seul `uvx rumdl fmt --check .` fait foi pour C9 : il n'échoue que sur les
  6 fichiers d'E6.
- `uvx rumdl fmt` replie les lignes d'Étape du Suivi : le relancer sur le Suivi après chaque
  écriture, sinon C9 échoue à la Clôture.
- `scripts/check_pipeline.py` exige que chaque empreinte d'une section de `contrat.md` reste
  unique : en E3, ne pas recopier « Au moindre doute, Opus » hors de « Modèle d'implémentation ».
- Les commits du Chantier suivent `etape.md` tel qu'il est au moment du commit : les choix de fin
  de commit ne s'appliquent qu'une fois E1 livrée.

## Journal de décisions

- **2026-10-09** — Après une Étape, « Valider et commencer la Passation » ne couvre que le commit
  d'Étape ; le commit de Passation demande son accord. *Pourquoi* : C5 borne l'exception à `<L>E0`.
  *Rejeté* : un accord pour les deux commits.
- **2026-10-09** — C9 servi en formatant les 6 fichiers hors Chantier (E6). *Pourquoi* : arbitrage
  de l'utilisateur à la relecture du Plan. *Rejeté* : borner C9 au diff.
- **2026-10-10** — Le choix 1 de `<L>E0` s'écrit « Valider et faire la Passation (commit inclus) ».
  *Pourquoi* : le libellé dit lui-même que l'accord couvre le commit de Passation. *Rejeté* : le
  libellé du Brief, sans la précision.
- **2026-10-10** — Motif de l'exception C5 réécrit en Retouche (AE6.1) : rien n'est implémenté, la
  section ne transmet que ce que la création a établi. *Pourquoi* : « rien à relire », motif du
  Brief, était faux (R3 du premier audit). *Rejeté* : garder le motif du Brief.
- **2026-10-10** — Clôture avec réserves : R1 à R3 du premier audit traitées, libellés recopiés
  versés à la dette, le reste clos tel quel ; `feedback/` gardé dans `.gitignore`, ajouté en AE0.
  *Pourquoi* : arbitrage de l'utilisateur. *Rejeté* : traiter le contrôle des libellés ici.
