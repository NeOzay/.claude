# Plan — contexte-tracker

## Contexte

Certains Chantiers dépassent largement 400k de contexte. But (Brief
`.claude/implementation/contexte-tracker.brief.md`) : rendre le passage à une nouvelle session le
plus fluide possible. Quatre leviers : des coupures placées là où elles rapportent (après
`<L>E0`, puis à un commit d'Étape au-delà de 300k tokens), une section `## Passation` du Suivi,
un `SKILL.md` chargé par phase, et un agent qui lit la taille de son contexte.

Exécution `direct` (deux incertitudes reportées au brief). Shadow-skill du Chantier :
`skill-convention`.

### Incertitudes du Brief : où elles en sont

- **Retrouver sa session** — levée en exploration : Claude Code 2.1.289 exporte
  `CLAUDE_CODE_SESSION_ID` dans l'environnement des commandes Bash ; il vaut le nom du transcript
  de la session (vérifié : `f118fa6a-…`).
- **Champ qui mesure le contexte courant** — reste ouverte, levée au début de l'Étape 2.
  L'oracle est la somme `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` du
  dernier `usage` du transcript, rendue par la commande `ORACLE` ci-dessous. On retient le champ
  de `context_window` qui la reproduit (`total_input_tokens`, ou `current_usage` s'il existe).
- **Passation obligatoire ou optionnelle** — tranchée dans ce plan : **optionnelle**
  (`required = false`). `gabarit new` la pose à `<OPTIONNEL>`, et `gabarit check` ne vérifie la
  présence que des sections obligatoires (`skills/gabarit/scripts/gabarit/check.py:90`) : les
  Suivis en cours et les archives de `done/` restent conformes, et une première session n'a rien
  à passer.

```bash
# ORACLE — taille du contexte d'après le transcript de la session courante
python3 -c 'import glob,json,os; f=glob.glob(os.path.expanduser("~/.claude/projects/*/"+os.environ["CLAUDE_CODE_SESSION_ID"]+".jsonl"))[0]; u=[m["usage"] for m in (json.loads(l).get("message") for l in open(f)) if isinstance(m,dict) and "usage" in m][-1]; print(u["input_tokens"]+u["cache_read_input_tokens"]+u["cache_creation_input_tokens"])'
```

La statusline se rafraîchit après un message, l'oracle lit le dernier appel : les deux valeurs
peuvent différer d'un tour. Tolérance retenue : **écart < 5 000 tokens**.

### Arbitrages de la relecture (2026-10-04)

Écrits au Suivi comme élargissements datés, avec une entrée au journal :

- **Q1** — `statusline-command.py` est remis au vert : l'Étape 2 corrige ses 3 erreurs `ruff`
  préexistantes (PLW1510, 2 × BLE001). La fiche `statusline-hors-des-linters` reste ouverte pour
  les erreurs de `list-dir` ; sa part statusline est notée au journal pour la Clôture.
- **Q3** — le critère `uvx rumdl check` devient `uvx rumdl fmt --check`, le contrôle
  qu'`OUTILLAGE.md` documente.
- **Q7** — les trois fiches ouvertes du registre de dette qui citent « l'Étape 2 » du tracker
  sont mises à jour à l'Étape 5.

### Choix de conception

- **Commande `contexte`** — exécutable de skill
  (`skills/implementation-tracker/scripts/contexte.py`), exposé par `bin/contexte` : une commande
  globale ne se déclare que par une skill (`skill-convention`, commandes-locales.md). Deux
  sous-commandes :
  - `contexte ecrire <session> <tokens>` — appelée par la statusline ;
  - `contexte` — lit `$CLAUDE_CODE_SESSION_ID` et imprime le nombre de tokens ; mesure absente
    → message sur stderr, sortie non nulle.

  Le chemin de stockage (`${XDG_RUNTIME_DIR:-~/.cache}/claude-contexte/<session>`) n'est défini
  qu'ici : la statusline ne connaît que la commande.
- **`statusline-command.py`** extrait le champ retenu et appelle `contexte ecrire`, en silence en
  cas d'échec. Rien d'autre (Signal de dérive).
- **Passation ≠ État courant** : `État courant` garde `Prochaine action` et `Notes`. `Passation`
  porte ce qu'aucun autre fichier ne dit : `**En cours** :` (le travail entamé dans l'Étape, état
  exact) et `**À savoir** :` (ce que la session a appris, absent du Suivi, du Plan et du code).
  Réécrite, jamais appendue, avant le commit qui précède une coupure.
- **Routeur** : l'actuelle « Étape 2 — Création » (`HEAD:SKILL.md` l. 97–232) part dans
  `references/creation.md`, l'actuelle « Étape 4 — Maintenir le fichier » (l. 259–359) dans
  `references/execution.md`, en **déplacement pur**. Seuls bougent les liens relatifs :
  `references/contrat.md#…` → `contrat.md#…`, `references/road-map.md#…` → `road-map.md#…`,
  `references/audit.md` / `references/dette.md` → `audit.md` / `dette.md`,
  `../git-smart-commit/…` → `../../git-smart-commit/…`. `SKILL.md` garde l'invocation,
  l'emplacement, les phases 0, 1, 3, 5, 6 et une consigne de lecture par référence (« lire au
  moment de créer », « lire au début de l'exécution »).
- **Titres** : « Étape 0…6 » → « Phase 0…6 », dans le skill et dans les fichiers qui les citent.
  Les fiches de dette ouvertes qui citent « l'Étape 2 » du tracker passent à « Phase 2 » (Q7).
- **Formatage** : `uvx rumdl fmt` sur chaque Markdown touché et `uvx ruff format` sur chaque
  Python touché, avant chaque commit (OUTILLAGE.md).

## Étapes

- [ ] 1. Commande `contexte` — `skills/implementation-tracker/scripts/contexte.py`, `bin/contexte`,
      `skills/implementation-tracker/scripts/tests/test_contexte.py`, `OUTILLAGE.md` (ligne de la
      table, et la phrase « quatre commandes » qui l'introduit) — vérif:
      `.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests && uvx ruff check skills/implementation-tracker && uvx ruff format --check skills/implementation-tracker && uvx --with pytest basedpyright skills/implementation-tracker`
- [ ] 2. Statusline écrit la mesure — `statusline-command.py`. D'abord établir le champ : écrire une
      fois `context_window` brut dans le scratchpad, le comparer à l'`ORACLE`, retenir le champ qui
      le reproduit et le noter au journal ; retirer l'écriture brute. Puis extraire ce champ et
      appeler `contexte ecrire` ; corriger les 3 erreurs `ruff` préexistantes (Q1) — vérif:
      `contexte` et l'`ORACLE` diffèrent de moins de 5 000 tokens ;
      `uvx ruff check statusline-command.py && uvx ruff format --check statusline-command.py && uvx --with pytest basedpyright statusline-command.py`
- [ ] 3. Section `Passation` optionnelle dans la semence —
      `skills/gabarit/gabarit/suivi/contract.toml` — vérif:
      `gabarit new suivi <scratchpad>/s.md && grep -A2 '^## Passation' <scratchpad>/s.md` montre
      `<OPTIONNEL>`, et
      `gabarit check --filled .claude/implementation/done/2026-10-04-shadow-skill.md` rend le même
      verdict qu'avant
- [ ] 4. `SKILL.md` en routeur, déplacement pur — `skills/implementation-tracker/SKILL.md`,
  `skills/implementation-tracker/references/creation.md`,
  `skills/implementation-tracker/references/execution.md` — vérif: extraire de
  `git show HEAD:skills/implementation-tracker/SKILL.md` les lignes 97–232 et 259–359 dans le
  scratchpad, puis `git diff --no-index --word-diff <extrait> <référence>` pour chacune ne montre
  que titres, liens et consignes de lecture ; `.venv/bin/python scripts/check_pipeline.py`
  conforme
- [ ] 5. Titres « Étape N » → « Phase N » et leurs renvois —
      `skills/implementation-tracker/SKILL.md`, ses `references/creation.md` et
      `references/execution.md`, `skills/intent-brief/SKILL.md` (l. 228, 235),
      `skills/implementation-tracker/references/contrat.md` (l. 211),
      `skills/implementation-tracker/references/dette.md` (l. 314),
      `skills/implementation-tracker/scripts/impl_list.py` (l. 5),
      `skills/gabarit/gabarit/suivi/contract.toml` (l. 3),
      `shadow-skills/skill-convention/references/prose.md` (l. 78), `OUTILLAGE.md` (l. 21), et les
      fiches `.claude/implementation/todo/technical-debt/point-3-premisse-harness-sans-repli.md`,
      `lettre-attribuee-sans-reservation.md`, `clause-arbre-propre-sans-le-plan.md` — vérif:
      `grep -rn "Étape [0-6]" skills/implementation-tracker` vide ;
      `grep -rn "Étape [0-6]" skills shadow-skills OUTILLAGE.md | grep -i "tracker\|implementation-tracker\|suivi"`
      vide ; `grep -rln "Étape 2" .claude/implementation/todo/technical-debt` vide ;
      `list-dir validate .claude/implementation/todo/technical-debt` ;
      `.venv/bin/python scripts/check_pipeline.py` conforme
- [ ] 6. Coupures et passation dans la procédure — `references/creation.md` (écrire la Passation
  avant le commit `<L>E0`, puis proposer `/clear` et `/implementation-tracker @<suivi>`),
  `references/execution.md` (au commit d'Étape : `contexte` ; au-delà de 300 000, écrire la
  Passation, committer, proposer la coupure ; mesure indisponible → le dire, ne rien proposer),
  `SKILL.md` (la reprise restitue la Passation) — vérif:
  `grep -rn "/clear" skills/implementation-tracker` ne rend que les deux points de coupure ;
  `.venv/bin/python scripts/check_pipeline.py` conforme ; `uvx rumdl fmt --check` sur les
  fichiers touchés

## Vérification d'ensemble

Sur les fichiers touchés par le Chantier :

```bash
.venv/bin/python scripts/check_pipeline.py
.venv/bin/python -m pytest skills/implementation-tracker scripts/tests
uvx ruff check skills/implementation-tracker statusline-command.py
uvx ruff format --check skills/implementation-tracker statusline-command.py
uvx --with pytest basedpyright skills/implementation-tracker statusline-command.py
uvx rumdl fmt --check skills/implementation-tracker skills/gabarit/gabarit/suivi \
  skills/intent-brief/SKILL.md shadow-skills/skill-convention/references/prose.md OUTILLAGE.md
contexte   # écart < 5 000 tokens avec l'ORACLE
```

## Hors du Chantier, à noter au journal

`intent-brief` et `debt-review` titrent aussi leurs phases « Étape N » : même collision avec le
Lexique, hors-périmètre ici — candidat au registre de dette.
