+++
gabarit = "suivi"
slug = "contexte-tracker"
titre = "Optimiser le contexte dans implementation-tracker"
branche = "contexte-tracker"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
execution = "direct"
plan = ".claude/implementation/done/2026-10-04-contexte-tracker.plan.md"
brief = ".claude/implementation/done/2026-10-04-contexte-tracker.brief.md"
audit = ".claude/implementation/done/2026-10-04-contexte-tracker.audit.md"
road-map = "<OPTIONNEL>"
skills = ["skill-convention"]
"créé" = 2026-10-04
maj = 2026-10-04
+++

## Objectif et périmètre

**Symptôme** : certains Chantiers dépassent largement les 400k de contexte.

**But** : rendre le passage à une nouvelle session le plus fluide possible, pour qu'un Chantier
tienne sous 400k sans payer de prefill inutile — coupures placées là où elles rapportent, un
message de passation qui porte ce que le Suivi ne dit pas, skill chargé par phase, et un agent
qui connaît son contexte.

**Critères de réussite** :

- `SKILL.md` du tracker ne porte plus les procédures de création ni d'exécution : il y renvoie
  vers deux fichiers de `references/`, et garde vérifications, routage et reprise.
- Chaque règle déplacée se retrouve à l'identique dans sa référence : `git diff --word-diff`
  sur le déplacement ne montre que titres et renvois.
- `grep -rn "Étape [0-6]" skills/implementation-tracker/SKILL.md` ne rend rien, et aucun
  renvoi aux anciens titres ne subsiste dans les fichiers qui les citaient.
- La procédure propose `/clear` puis la reprise après le commit `<L>E0`, et à un commit
  d'Étape seulement quand le contexte dépasse 300k tokens.
- La semence `suivi` déclare une section `## Passation` ; la procédure la réécrit avant le
  commit qui précède une coupure, et la reprise la restitue.
- L'agent lit la taille de son contexte courant par une commande ; la valeur concorde avec le
  dernier `usage` du transcript de la session.
- `uvx ruff check`, `uvx ruff format --check`, `uvx --with pytest basedpyright` et
  `uvx rumdl fmt --check` passent sur les fichiers touchés.

**Hors-périmètre** :

- Alléger la reprise : le Suivi reste lu en entier.
- Un hook `SessionStart` qui réinjecte l'état du Suivi après une compaction.
- Modifier `intent-brief` au-delà de ses renvois aux titres renommés.
- Un hook d'alerte au-delà du seuil dans toute session, hors Chantier.
- Les trois sous-agents (`step-implementer`, `plan-reviewer`, `implementation-auditor`).

**Signaux de dérive** :

- Une règle de `SKILL.md` perdue ou réécrite en passant vers `references/` — le déplacement
  doit être un déplacement.
- `statusline-command.py` fait plus que mesurer le contexte et écrire la valeur — hors la
  correction de ses 3 erreurs `ruff` préexistantes, acceptée le 2026-10-04.
- Une coupure proposée ailleurs qu'après `<L>E0` et au-delà du seuil à un commit d'Étape.

**Élargissements acceptés le 2026-10-04**, à la relecture du plan :

- `statusline-command.py` est remis au vert : ses 3 erreurs `ruff` préexistantes sont
  corrigées (Q1).
- Le critère `uvx rumdl check` du Brief devient `uvx rumdl fmt --check`, le contrôle
  qu'`OUTILLAGE.md` documente (Q3).
- Les trois fiches ouvertes du registre de dette qui citent « l'Étape 2 » du tracker sont mises
  à jour (Q7).

**Élargissement accepté le 2026-10-04**, au second audit de clôture : la Passation se dissocie de
l'Étape et prend son commit dédié, nouveau cas du type 2 de `git-smart-commit`
(`skills/git-smart-commit/references/etape.md`).

## Étapes

- [x] 1. Commande `contexte` — `skills/implementation-tracker/scripts/contexte.py`, `bin/contexte`,
      `skills/implementation-tracker/scripts/tests/test_contexte.py`, `OUTILLAGE.md` — vérif:
      `.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests && uvx ruff check skills/implementation-tracker && uvx ruff format --check skills/implementation-tracker && uvx --with pytest basedpyright skills/implementation-tracker`
- [x] 2. Statusline écrit la mesure — `statusline-command.py` — vérif: `contexte` et l'`ORACLE` du
      plan diffèrent de moins de 5 000 tokens ;
      `uvx ruff check statusline-command.py && uvx ruff format --check statusline-command.py && uvx --with pytest basedpyright statusline-command.py`
- [x] 3. Section `Passation` optionnelle dans la semence —
  `skills/gabarit/gabarit/suivi/contract.toml` — vérif: `gabarit new suivi` pose
  `## Passation` à `<OPTIONNEL>` ;
  `gabarit check --filled .claude/implementation/done/2026-10-04-shadow-skill.md` inchangé
- [x] 4. `SKILL.md` en routeur, déplacement pur — `skills/implementation-tracker/SKILL.md`,
  `references/creation.md`, `references/execution.md` — vérif:
  `git diff --no-index --word-diff` des extraits de `HEAD:SKILL.md` contre chaque référence ;
  `.venv/bin/python scripts/check_pipeline.py`
- [x] 5. Titres « Étape N » → « Phase N » et leurs renvois — liste du plan — vérif:
  `grep -rn "Étape [0-6]" skills/implementation-tracker` vide ;
  `grep -rln "Étape 2" .claude/implementation/todo/technical-debt` vide ;
  `.venv/bin/python scripts/check_pipeline.py`
- [x] 6. Coupures et passation dans la procédure — `references/creation.md`,
  `references/execution.md`, `SKILL.md` — vérif:
  `grep -rn "/clear" skills/implementation-tracker` ne rend que les deux points de coupure ;
  `.venv/bin/python scripts/check_pipeline.py`
- [x] 7. Traiter les réserves R1 à R6 de l'audit du 2026-10-04 — `references/execution.md`,
  `SKILL.md`, `skills/gabarit/gabarit/suivi/contract.toml`, `scripts/contexte.py` et ses tests,
  `statusline-command.py`, `OUTILLAGE.md`, fiches `point-3-premisse-harness-sans-repli` et
  `lettre-attribuee-sans-reservation` — vérif: la « Vérification d'ensemble » du plan
- [x] 8. Passation dissociée de l'Étape (R9, R10, R11) — `references/execution.md`,
      `references/creation.md`, `SKILL.md`, `skills/gabarit/gabarit/suivi/contract.toml`,
      `skills/git-smart-commit/references/etape.md`, `LEXIQUE.md` — vérif: `lexique liste` ;
      `.venv/bin/python scripts/check_pipeline.py` ; `uvx rumdl fmt --check` sur les fichiers
      touchés ; `gabarit new suivi` pose `## Passation` à `<OPTIONNEL>`
- [x] 9. `ORACLE` du Plan rejouable (R12) — `.claude/plans/sleepy-coalescing-marshmallow.md` —
  vérif: l'`ORACLE` et `contexte` rendent la même valeur
- [x] 10. Réserves R14 et R16 du troisième audit — `skills/git-smart-commit/SKILL.md`,
  `skills/implementation-tracker/SKILL.md`, `skills/gabarit/gabarit/suivi/contract.toml` — vérif:
  `.venv/bin/python scripts/check_pipeline.py` ; `uvx rumdl fmt --check` sur les fichiers touchés
- [x] 11. Réserves R17 et R18 du quatrième audit — `skills/implementation-tracker/SKILL.md`,
  `references/execution.md`, `skills/gabarit/gabarit/suivi/contract.toml` — vérif:
  `.venv/bin/python scripts/check_pipeline.py` ; `uvx rumdl fmt --check` sur les fichiers touchés

## État courant

- **Prochaine action** : Clôture — un dernier audit de clôture complet, puis le registre de dette.
- **Vérification** : la « Vérification d'ensemble » du plan.
- **Dernier audit** : `50071c4` — RÉSERVES — 2026-10-04
- **Notes** : `CLAUDE_CODE_SESSION_ID` est exporté aux commandes Bash (Claude Code 2.1.289).

## Journal de décisions

- **2026-10-04** — Section `## Passation` optionnelle dans la semence `suivi`. *Pourquoi* :
  `gabarit check` ignore une section facultative absente ; Suivis en cours et archives restent
  conformes. *Rejeté* : section obligatoire.
- **2026-10-04** — Phases du tracker titrées « Phase N ». *Pourquoi* : « Étape » est réservé par
  le Lexique à l'unité de travail d'un Chantier. *Rejeté* : « Option N », sans numéro.
- **2026-10-04** — La mesure du contexte est la somme des trois champs d'entrée de
  `context_window.current_usage`. *Pourquoi* : elle égale l'`ORACLE` à l'unité près. *Rejeté* :
  `total_input_tokens`, égal aujourd'hui, mais dont le nom dit un cumul.
- **2026-10-04** — La Passation est l'acte de passer d'une session à la suivante : proposée après
  `<L>E0`, et après un commit d'Étape au-delà de 300 000 tokens, avec son commit dédié. *Pourquoi* :
  jointe au commit d'Étape, la section s'écrivait avant l'accord et restait sur un refus (R9).
  *Rejeté* : la remise au marqueur à la reprise, qui effaçait « À savoir » (R10).
- **2026-10-04** — La section `## Passation` est à jour tant que son commit est le dernier de la
  branche et que seul `<slug>.audit.md` est hors commit. *Pourquoi* : une session qui continue après
  sa Passation garde son numéro. *Rejeté* : comparer les sessions (R16), exiger un arbre propre
  (R17).
- **2026-10-04** — La procédure de Passation n'existe qu'à un endroit, `execution.md`, que la
  création appelle : `/clear` n'y apparaît qu'une fois, là où l'Étape 6 en attendait deux.
- **2026-10-04** — « Passation » entre au Lexique global, sur accord explicite de l'utilisateur.
  *Pourquoi* : concept d'une skill globale. *Rejeté* : la minuscule.
- **2026-10-04** — Quatre audits de clôture, tous RÉSERVES ; R1–R6, R9–R12 et R14–R18 traités en
  Étapes 7 à 11. Clos sans audit de l'Étape 11, sur décision de l'utilisateur ; R7, R8, R13 et ce
  report vont au registre de dette.
