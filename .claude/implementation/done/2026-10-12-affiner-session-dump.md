+++
gabarit = "suivi"
slug = "affiner-session-dump"
titre = "`session-dump` : détailler les sous-agents au frontmatter, écarter les sessions lancées par `claude -p` et les sessions vides"
branche = "affiner-session-dump"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "sonnet"
plan = ".claude/implementation/done/2026-10-12-affiner-session-dump.plan.md"
brief = ".claude/implementation/done/2026-10-12-affiner-session-dump.brief.md"
road-map = "session-dump-sous-agents-et-sessions-de-test"
skills = ["skill-convention"]
audit = ".claude/implementation/done/2026-10-12-affiner-session-dump.audit"
"créé" = 2026-10-11
maj = 2026-10-12
+++

## Objectif et périmètre

**Symptôme** : « Mesurer le poids des audits a demandé de relire les transcriptions brutes de
`<session>/subagents/` » ; les sessions lancées par `claude -p` « se mêlent aux discussions dans le
répertoire de dumps » (road-map: `session-dump-sous-agents-et-sessions-de-test`).

**But** : que chaque dump dise ce que chacun de ses sous-agents a consommé, et que le répertoire de
dumps ne garde que les discussions.

**Critères de réussite** :

- **C1** — `session-dump`, lancé sur ce dépôt, n'écrit aucun dump de session `sdk-cli` ni de
  session à moins de 2 tours et moins de 10 000 tokens ; sa sortie compte les écartées par motif
  (sans tour, `claude -p`, trop courte).
- **C2** — Lu par `tomllib`, le dump d'une session à sous-agents porte une entrée par lancement et
  une par famille, chacune avec les champs de `[tokens]` ; le total d'une famille égale la somme de
  ses lancements.
- **C3** — Sur l'ensemble des dumps, le nombre de lancements par famille égale celui des
  `*.meta.json` qui portent cet `agentType`.
- **C4** — `skills/session-dump/SKILL.md`, « Ce qu'elle écrit », décrit les tables des
  sous-agents et les règles d'écart.
- **C5** — `pytest skills/session-dump/scripts/tests/`, `ruff` et `basedpyright` passent, selon
  `OUTILLAGE.md`.

**Hors-périmètre** :

- L'analyse des dumps.
- Le dump des transcriptions des sous-agents.
- Le coût par sous-agent.

**Signaux de dérive** :

- **S1** — Un critère d'écart autre que `sdk-cli` ou « moins de 2 tours et moins de 10 k
  tokens » : fondé sur le titre, le contenu, ou un autre seuil.
- **S2** — Un coût par sous-agent, ou une table de prix, dans le diff.
- **S3** — Le `[tokens]` d'une session à `cost-state` change, recalculé depuis les transcriptions.
- **S4** — Le corps du dump change : transcriptions des sous-agents, résultats d'outils.
- **S5** — Le diff interprète ou classe le contenu des sessions au lieu de l'extraire.

## Étapes

- [x] 1. Lire les sous-agents — `skills/session-dump/scripts/session_dump.py`, `tests/test_lecture.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`
- [x] 2. Rendre les sous-agents au frontmatter — `session_dump.py`, `tests/test_rendu.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`
- [x] 3. Écarter par motif — `session_dump.py`, `session-dump-cli.py`, `tests/test_cli.py`, `tests/test_lecture.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`
- [x] 4. Documenter et vérifier sur le dépôt — `skills/session-dump/SKILL.md`, `session_dump.py` — vérif: section « Vérification » du plan (C1 à C5, S3)

## État courant

**Prochaine action** : toutes les Étapes sont livrées — lancer l'audit de Clôture. Contrôles de
l'Étape 4 passés : C5 (pytest 68, ruff, basedpyright, rumdl), C1–C3 (78 lancements sur 68 dumps,
les 4 autres `*.meta.json` étant dans des sessions `sdk-cli` écartées), S3 (0 écart).

**Vérification** : section « Vérification » du plan — pytest, ruff, basedpyright, rumdl, puis
`session-dump` sur ce dépôt et les scripts de contrôle C1–C3 et S3.

**Dernier audit** : be6978c — FAVORABLE — 2026-10-12

**Notes** : forme du frontmatter fixée au plan, section « Forme du frontmatter ».

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien.

**À savoir** :

- Le classifieur du mode auto a refusé `git commit` et `git tag` (motif « Git Destructive »), puis
  un `git status` : `AE0` a été posé par l'utilisateur, en `! git …`. Un commit d'Étape refusé se
  rend à l'utilisateur sous cette forme, sans contournement.
- Le dépôt compte désormais 82 `*.meta.json` (81 au plan) : les nombres du plan sont indicatifs,
  le script de contrôle compare aux fichiers présents.
- Le contrôle S3 tolère un écart, la session en cours : son `cost-state` grandit entre le dump
  d'avant et celui d'après.

## Dettes écartées

<OPTIONNEL>

## Journal de décisions

- **2026-10-11** — C3 se lit sur les `*.meta.json` des sessions dumpées seulement. *Pourquoi* : 4
  sessions `sdk-cli`, écartées par C1, portent un sous-agent `lexique-test-isole` ; C3 à la lettre
  ne tiendrait pas avec C1 (relecture du plan, Q1). *Rejeté* : compter ailleurs les sous-agents
  des sessions écartées, qui élargissait le brief.
- **2026-10-11** — Un `.meta.json` absent donne `famille = "?"` sans signalement ; seul un
  `.meta.json` illisible compte un illisible (relecture du plan, Q8).
