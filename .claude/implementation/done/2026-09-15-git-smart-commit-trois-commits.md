---
slug: git-smart-commit-trois-commits
titre: Découper git-smart-commit en trois types de commits
branche: git-smart-commit-trois-commits
base: master
statut: terminé
session: 2
lettre: A
execution: direct
plan: .claude/implementation/done/2026-09-15-git-smart-commit-trois-commits.plan.md
brief: .claude/implementation/done/2026-09-15-git-smart-commit-trois-commits.brief.md
audit: .claude/implementation/done/2026-09-15-git-smart-commit-trois-commits.audit.md
créé: 2026-09-14
maj: 2026-09-15
---

## Objectif et périmètre

Repris du brief (`brief:`), sans reformulation.

**Symptôme** : `git-smart-commit` est un skill ancien, créé avant `implementation-tracker`. Son
`SKILL.md` mêle le workflow général et le cas d'aplatissement, renvoyé en fin de fichier vers
`references/squash.md`.
**But** : trois types de commits distincts — (1) hors `implementation-tracker`, (2) commit rapide
d'une étape du tracker, (3) commit d'aplatissement du tracker. Chacun est lisible indépendamment, et
lu seulement au besoin. Le texte commun va dans des fichiers séparés et référencés.
**Critères de réussite** :
- les trois parties sont indépendantes, chacune lue seulement au besoin ;
- le texte commun est dans des fichiers séparés et référencés, sans être recopié ;
- `scripts/check_pipeline.py` sort avec le code 0 ;
- des tests pytest couvrent le script de clôture sur un dépôt jouet : dry-run, aplatissement,
  suppression des tags, refus sur conflit ;
- `uvx ruff check` et `uvx --with pytest basedpyright` passent sur le nouveau script.

**Hors-périmètre** : les chantiers clos (`done/`) ne sont pas touchés.

**Amendé le 2026-09-14** (arbitrage Q1) :
- migrent aussi dans `git-smart-commit` : les commits de l'abandon, la règle « jamais sans accord »
  et la règle de branche `<slug>` ;
- `contrat.md` § Branche et commits disparaît au profit de renvois ;
- la règle « déplacer puis prouver dans un second commit » reste où elle est.

**Signaux de dérive** :
- une modification qui ne touche pas au système de commit ;
- du jugement introduit, dans le script en particulier ;
- du texte recopié d'un skill à l'autre au lieu d'être référencé.

## Étapes

- [x] 1. Script `commit-chantier` et ses tests — `skills/git-smart-commit/scripts/`, `skills/git-smart-commit/ruff.toml`, `bin/commit-chantier`, `scripts/tests/README.md` — vérif: `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests -q && uvx ruff check skills/git-smart-commit && uvx --with pytest basedpyright`
- [x] 2. Type 1 et fichiers communs — `skills/git-smart-commit/SKILL.md`, `references/{hors-chantier,conventional-commits,confirmation,staging}.md`, `contrat.md` (staging et accord sortis de § Branche et commits), `scripts/check_pipeline.py` (empreinte) — vérif: `python3 scripts/check_pipeline.py && ! grep -n "tracker" skills/git-smart-commit/SKILL.md skills/git-smart-commit/references/{hors-chantier,conventional-commits,confirmation,staging}.md`
- [x] 3. Type 2 et branchement du tracker — `references/{etape,tags-etape,branche-chantier}.md`, routeur `SKILL.md`, tracker `SKILL.md` (points 3, 7 et 8, Étapes 3 et 4), `contrat.md` (§ Branche et commits supprimé, § Frontmatter `session` et `lettre`, l. 3), `cloture.md:122`, clé `EMPREINTES`, `gabarit-suivi.md`, ce suivi — vérif: `python3 scripts/check_pipeline.py && ! grep -rn "branche-et-commits\|court-circuité\|ne passent pas par" skills scripts/check_pipeline.py && ! grep -n "tracker" skills/git-smart-commit/references/branche-chantier.md`
- [x] 4. Type 3 (et § Abandon) et renvoi de la clôture vers le script — `references/aplatissement.md`, `references/squash.md` supprimé, `cloture.md` (clôture points 3-4, abandon points 2 et 4), tracker `SKILL.md` Étape 5 — vérif: `python3 scripts/check_pipeline.py && ! grep -rn "merge --squash\|branch -D" skills --include='*.md' | grep -v git-smart-commit/references/aplatissement.md`
- [x] 5. Vérification d'ensemble — aucun fichier hors du système de commit — vérif: `python3 scripts/check_pipeline.py && .venv/bin/python -m pytest scripts/tests skills/list-dir/scripts/tests skills/git-smart-commit/scripts/tests -q && uvx ruff check scripts skills/list-dir skills/git-smart-commit && uvx --with pytest basedpyright`
- [x] 6. Correctifs de l'audit R2 à R6 — `skills/git-smart-commit/scripts/commit_chantier.py`, `scripts/tests/test_commit_chantier.py`, `references/aplatissement.md`, `cloture.md` point 2 — vérif: `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests -q && uvx ruff check skills/git-smart-commit && python3 scripts/check_pipeline.py && ! uvx --with pytest basedpyright 2>&1 | grep git-smart-commit`
- [x] 7. Correctifs du second audit R12 à R14 — `skills/git-smart-commit/scripts/commit_chantier.py`, `scripts/tests/test_commit_chantier.py`, `references/aplatissement.md` — vérif: `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests -q && uvx ruff check skills/git-smart-commit && python3 scripts/check_pipeline.py && ! uvx --with pytest basedpyright 2>&1 | grep git-smart-commit`
- [x] 8. Correctifs du troisième audit R17 et R19 — `scripts/check_pipeline.py` (contrôle 5), `scripts/tests/test_controles_4_5.py`, `skills/git-smart-commit/scripts/tests/test_commit_chantier.py`, `references/aplatissement.md`, `scripts/tests/README.md`, dette `frontmatter-suivi-lu-par-regex` — vérif: `.venv/bin/python -m pytest scripts/tests skills/git-smart-commit/scripts/tests -q && uvx ruff check skills/git-smart-commit scripts/check_pipeline.py scripts/tests && python3 scripts/check_pipeline.py && ! uvx --with pytest basedpyright 2>&1 | grep 'git-smart-commit\|check_pipeline\|test_controles_4_5'`

## État courant

**Prochaine action** : aucune — chantier clos par `commit-chantier cloture` le 2026-09-15.
Registre de dette alimenté, `git-smart-commit-illisible-seul` soldée en partie (R7).
**Vérification** : `python3 scripts/check_pipeline.py && .venv/bin/python -m pytest scripts/tests skills/list-dir/scripts/tests skills/git-smart-commit/scripts/tests -q` (587 tests attendus)
**Constats hors chantier connus** : ruff sort 3 E501 dans `skills/list-dir/scripts/tests`, et
basedpyright 25 erreurs, identiques à `master`, aucune dans `git-smart-commit`.
**Dernier audit** : `9513ccd` — RÉSERVES — 2026-09-15

## Journal de décisions

- **2026-09-14** — Plan approuvé malgré le verdict `NON CONFORME` de `plan-reviewer`. *Pourquoi* :
  validation donnée en connaissance du verdict. *Rejeté* : corriger le plan d'office.
- **2026-09-14** — `contrat.md` § Branche et commits est supprimé : staging et accord vont dans
  `staging.md` et `confirmation.md` (communs aux trois types, type 1 compris, sans `-A`), branche,
  messages et tags dans `etape.md`, la cadence de `session:` reste au § Frontmatter. *Pourquoi* : le
  contrôle 2 refuse une section sans empreinte, et un champ du suivi se définit au contrat.
  *Rejeté* : une section réduite à un renvoi.
- **2026-09-14** — Les commits de l'abandon vont dans `aplatissement.md` § Abandon, et *tout jeter*
  archive aussi le plan en réécrivant les champs. *Pourquoi* : même fin de branche, et le contrôle 5
  exige des chemins qui résolvent. *Rejeté* : un quatrième type.
- **2026-09-14** — `commit-chantier` ne dépend que de la stdlib, ses tests le lancent en
  sous-processus. *Pourquoi* : la ligne de commande fait contrat. *Rejeté* : importer le module.
- **2026-09-14** — Le script tolère et indexe toutes les annexes du chantier (suivi, brief, audit,
  plan, `todo/`) dans le commit de finalisation, sauté s'il n'y a rien à indexer. *Pourquoi* : une
  annexe non suivie bloquerait la clôture, une annexe modifiée ferait refuser le checkout.
  *Rejeté* : suivi et `todo/` seuls.
- **2026-09-14** — La clôture s'exécute geste par geste ; un `ÉCHEC` dit ce qui est fait, ce qui
  reste, et s'il faut relancer ou finir à la main (R2). *Rejeté* : défaire un aplatissement entamé.
- **2026-09-14** — Frontmatter lu et réécrit par regex, même motif en lecture et en réécriture
  (`clé:` avec ou sans espace, commentaire de fin de ligne conservé), et le contrôle 5 aligné sur ce
  lecteur (R3, R14, R17). *Pourquoi* : `tomllib` ne lit pas le format. *Rejeté* : changer le format
  ici — dette `frontmatter-suivi-lu-par-regex`.
- **2026-09-14** — Ce chantier reçoit `lettre: A` sans tags rétroactifs ; les étapes 7 et 8, prises
  sous le type 2, portent `AE7` et `AE8`.
- **2026-09-15** — Quatre audits de clôture, tous `RÉSERVES` sans bloquant (`69e5fcc`, `dca29d3`,
  `138b35f`, `9513ccd`). R2 à R6, R12 à R14, R17 et R19 corrigés en étapes 6 à 8. Clôture acceptée
  avec les réserves restantes : R1/R11, R8, R9, R10, R15, R16, R18/R20 au registre de dette, R7 dit
  dans le solde de `git-smart-commit-illisible-seul`.
