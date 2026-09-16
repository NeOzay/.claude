---
slug: fichier-seme
titre: Créer un fichier préstructuré depuis une semence, hors de toute liste
branche: fichier-seme
base: master
statut: terminé
session: 1
lettre: A
execution: direct
plan: .claude/implementation/done/2026-09-16-fichier-seme.plan.md
brief: .claude/implementation/done/2026-09-16-fichier-seme.brief.md
audit: .claude/implementation/done/2026-09-16-fichier-seme.audit.md
créé: 2026-09-15
maj: 2026-09-16
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : — non abordé
**But** : créer des fichiers préstructurés à remplir à partir d'une semence, comme la création d'un
élément de list-dir mais sans rattachement à une liste. Première utilisation : les fichiers de suivi
d'implementation-tracker.
**Critères de réussite** :
- la suite de tests de list-dir passe ; seuls ses imports sont modifiables sans autorisation
- une vraie semence de suivi du tracker est livrée
**Hors-périmètre** :
- pas de modification des skills existants ; création d'un nouveau skill
- list-dir : comportement et documentation identiques, seul le code interne bouge
- implementation-tracker n'est pas branché sur « gabarit » : chantier ultérieur
**Signaux de dérive** :
- un test de list-dir qu'on voudrait modifier au-delà des imports
- `gabarit` qui importe quoi que ce soit de `listdir`
- `gabarit` qui se met à gérer une notion de répertoire ou de liste

**Élargissement (2026-09-15)** : le type `int` est autorisé dans `gabarit` **et** dans list-dir, dont
`references/format.md` (« Types admis ») change en conséquence. Seule entorse au hors-périmètre
« comportement et documentation identiques » ; accepté en plan mode, plan approuvé avec le verdict
NON CONFORME de `plan-reviewer` qui la relevait.

**Élargissement (2026-09-15)** : `ListError` est un alias de `GabaritError` — `except ListError` inchangé, mais une
trace affiche `gabarit.types.GabaritError`. Relevé par l'audit de clôture (R1), accepté.

## Étapes

- [x] 1. Squelette du skill et amorce de dépendance — `skills/gabarit/`, `bin/gabarit`, `listdir/__init__.py`, `skills/list-dir/pyrightconfig.json` — vérif: `command -v gabarit && .venv/bin/python scripts/sante_skills.py && .venv/bin/python -m pytest skills/list-dir/scripts/tests -q`
- [x] 2. Types et I/O d'un fichier vers `gabarit` — `gabarit/{types,items,gitcmd}.py`, `listdir/{types,items,gitcmd}.py` — vérif: `.venv/bin/python -m pytest skills/list-dir/scripts/tests -q && ! grep -rnE '^\s*(from|import)\s+listdir' skills/gabarit/scripts`
- [x] 3. Parsing de contrat et confrontation d'un fichier — `gabarit/{contract,check}.py`, `listdir/{contract,store}.py` — vérif: idem étape 2
- [x] 4. Préremplissage à environnement injecté — `gabarit/prefill.py`, `listdir/{prefill,store}.py` — vérif: idem étape 2
- [x] 5. Résolution des semences paramétrée — `gabarit/definitions.py`, `listdir/definitions.py` — vérif: idem étape 2
- [x] 6. Type `int` — `gabarit/{types,contract}.py`, `skills/gabarit/scripts/tests/test_int.py`, `skills/list-dir/references/format.md` — vérif: `.venv/bin/python -m pytest skills/gabarit/scripts/tests skills/list-dir/scripts/tests -q && ! grep -rnE '^\s*(from|import)\s+listdir' skills/gabarit/scripts`
- [x] 7. Commande `new` — `gabarit/commandes.py`, `gabarit-cli.py`, `tests/test_new.py` — vérif: `.venv/bin/python -m pytest skills/gabarit/scripts/tests -q && ! grep -rnE '^\s*(from|import)\s+listdir' skills/gabarit/scripts`
- [x] 8. Commande `check` — `gabarit/commandes.py`, `gabarit-cli.py`, `tests/test_check.py` — vérif: idem étape 7
- [x] 9. Commandes `contract` et `defs` — `gabarit/commandes.py`, `gabarit-cli.py`, `tests/test_contract_defs.py` — vérif: idem étape 7
- [x] 10. Semence `suivi` — `skills/gabarit/gabarit/suivi/contract.toml` — vérif: bloc de l'étape 10 du plan
- [x] 11. Documentation et outillage — `skills/gabarit/SKILL.md`, `skills/gabarit/references/`, `OUTILLAGE.md` — vérif: `.venv/bin/python scripts/check_pipeline.py && grep -n 'gabarit' OUTILLAGE.md && ! grep -n 'deux commandes' OUTILLAGE.md`
- [x] 12. Réserves de l'audit de clôture (R2, R3) — `gabarit/commandes.py`, `gabarit-cli.py`, `tests/test_{new,check}.py` — vérif: `.venv/bin/python -m pytest skills/gabarit/scripts/tests skills/list-dir/scripts/tests -q`

## État courant

**Prochaine action** : aplatissement sur `master` et archivage (`commit-chantier cloture`).
**Vérification** : bloc « Vérification d'ensemble » du plan
**Dernier audit** : `5123a3d` — RÉSERVES — 2026-09-15 (R2, R3 levés ; R1 accepté ; R4 à R8 ouverts, aucun bloquant)
**Notes** : base avant chantier — list-dir 447 passed, ruff 3 erreurs, basedpyright 13 erreurs.

## Journal de décisions

- **2026-09-15** — `listdir` dépend directement de `gabarit`, sans 3e bibliothèque. *Pourquoi* : une
  list-dir est une liste de gabarits. *Rejeté* : bibliothèque commune tierce.
- **2026-09-15** — `listdir/__init__.py` trouve `gabarit` par le premier `bin/gabarit` en remontant, le
  PATH en repli. *Pourquoi* : `which` seul cassait `test_git_absent_du_path…` (dérive tranchée en E1).
  *Rejeté* : PATH seul ; chemin relatif entre skills.
- **2026-09-15** — Point d'entrée `scripts/gabarit-cli.py` (écart au plan). *Pourquoi* : pas de module
  homonyme du paquet `gabarit/`.
- **2026-09-15** — Type `int` ajouté aux deux paquets (élargissement). *Pourquoi* : `session` est un
  entier, rien ne justifie de l'interdire à list-dir. *Rejeté* : `session` en `text`.
- **2026-09-15** — Estampille `gabarit = "<nom>"` (slug, sans version), TOML `+++` seul, semences sous
  `gabarit/<nom>/` ; avec `--from`, le nom du répertoire. *Pourquoi* : le fichier se vérifie seul.
  *Rejeté* : semence nommée à la vérification ; `name` du contrat comme estampille.
- **2026-09-15** — Audits de clôture RÉSERVES (`fadddf1`, `5123a3d`) : R2, R3 corrigés (E12), R1 accepté,
  R4, R5, R7, R8 clos avec, au registre de dette. *Pourquoi* : R1 ne se corrige pas par sous-classe,
  `Result` étant partagé. *Rejeté* : `Result` porteur de sa classe d'erreur (invasif).
