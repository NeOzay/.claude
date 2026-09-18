---
slug: skill-convention
titre: Une skill qui consigne mes conventions, extraites de mes skills
branche: skill-convention
base: master
statut: terminé
session: 2
lettre: A
execution: direct
plan: .claude/implementation/done/2026-09-18-skill-convention.plan.md
brief: .claude/implementation/done/2026-09-18-skill-convention.brief.md
audit: .claude/implementation/done/2026-09-18-skill-convention.audit.md
road-map: commandes-locales-au-projet
créé: 2026-09-17
maj: 2026-09-18
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : — non abordé
**But** : « créer ma propre skill-convention avec mes pratiques », en extrayant les conventions
« à partir de mes skills », et y ajouter la road-map `commandes-locales-au-projet`. Deux volets :
la prose des skills, et les conventions de code — Python typé strict, doc compacte au format
Google. La skill inclut `commandes-locales-au-projet` pour indiquer comment une skill peut mettre
localement des commandes à disposition d'un agent.
**Critères de réussite** :
- `scripts/check_pipeline.py` passe toujours
- chaque convention cite au moins une skill où elle est pratiquée
- une entrée de dette par skill en écart, conforme à `list-dir validate`
- l'entrée `commandes-locales-au-projet` sort de la road-map à la clôture
**Hors-périmètre** : les skills existantes ne sont pas corrigées — la skill décrit les
conventions, et les écarts des skills à corriger sont consignés dans une dette.
**Signaux de dérive** :
- la nouvelle skill recopie des règles au lieu d'y renvoyer
- une skill existante est éditée

**Élargissement du 2026-09-17** (accepté par l'utilisateur, relecture du plan) :
- le critère de citation devient « chaque convention cite au moins un site du dépôt (skill,
  script, hook, agent) où elle est pratiquée » ;
- seule exception : les docstrings au format Google, prescrites sans être encore pratiquées.

**Élargissement du 2026-09-18** (accepté par l'utilisateur, relecture de la branche) :
- **Rôle de la skill** : elle décrit les conventions de maintien de la configuration globale
  (`~/.claude`) et des configurations locales à un projet — cadrage, pas seulement extraction
  des skills existantes.
- **Principe directeur, énoncé en tête du `SKILL.md`** : réduire au maximum le non-déterminisme
  du LLM. En découlent trois conventions : `gabarit` pose les documents prêts à l'emploi,
  `list-dir` tient la mémoire structurée (registres), le frontmatter sépare les données mutables
  de la prose.
- **Style imposé** : déclaratif et direct. Pas de constat historique, pas de récit de ce qui a
  mené à la règle. Le mode de défaillance évité reste écrit, en une phrase.
- Les autres sujets de configuration (hooks, `settings.json`, sous-agents, `rules/`, `CLAUDE.md`)
  ne sont **pas** nommés par ce chantier.
- Les citations « Pratiqué dans » sont conservées telles quelles ; leur justification en prose
  disparaît.
- **Écart au brief assumé** : le `SKILL.md` ne renvoie plus à `rules/lua-style.md` (jugé non
  pertinent par l'utilisateur, 2026-09-18). La contrainte « la skill renvoie à OUTILLAGE.md et
  rules/lua-style.md » du brief ne tient plus que pour `OUTILLAGE.md` ; le fichier
  `rules/lua-style.md` reste inchangé.

## Étapes

- [x] 1. Vérifier `CLAUDE_ENV_FILE` : sous-agents et cohabitation RTK — suivi (journal) — vérif: résultat consigné au journal avec la commande rejouable
- [x] 2. Poser `SKILL.md` — `skills/skill-convention/SKILL.md` — vérif: `.venv/bin/python scripts/check_pipeline.py`
- [x] 3. Écrire les conventions de prose — `skills/skill-convention/references/prose.md` — vérif: `.venv/bin/python scripts/check_pipeline.py`
- [x] 4. Écrire les conventions de code — `rules/claude-python-style.md` — vérif: `head -5 rules/claude-python-style.md` montre `paths` et `.venv/bin/python scripts/check_pipeline.py`
- [x] 5. Écrire la procédure des commandes locales et son modèle — `skills/skill-convention/references/commandes-locales.md`, `skills/skill-convention/modeles/commandes-locales.sh` — vérif: `bash -n` puis essai du modèle (plan)
- [x] 6. Consigner les écarts à la prose en dette — `.claude/implementation/todo/technical-debt/*.md` — vérif: `list-dir validate .claude/implementation/todo/technical-debt`
- [x] 7. Consigner les écarts au code Python en dette — `.claude/implementation/todo/technical-debt/*.md` — vérif: `list-dir validate .claude/implementation/todo/technical-debt`
- [x] 8. Réécrire le `SKILL.md` : principe directeur, `description`, cadrage config globale/locale — `skills/skill-convention/SKILL.md` — vérif: `.venv/bin/python scripts/check_pipeline.py`
- [x] 9. Écrire les conventions `gabarit`, `list-dir` et frontmatter — `skills/skill-convention/references/prose.md` — vérif: `.venv/bin/python scripts/check_pipeline.py`
- [x] 10. Réécrire les références en style déclaratif — `skills/skill-convention/references/*.md`, `rules/claude-python-style.md` — vérif: `.venv/bin/python scripts/check_pipeline.py`
- [x] 11. Contrôle final des bornes — aucun — vérif: commandes de la section Vérification du plan
- [x] 12. Lever les réserves de l'audit (R1, R2, R3) — `rules/claude-python-style.md`, `skills/skill-convention/SKILL.md`, `.claude/implementation/todo/technical-debt/*.md` — vérif: `.venv/bin/python scripts/check_pipeline.py` et `list-dir validate .claude/implementation/todo/technical-debt`

## État courant

**Prochaine action** : clôture — `/implementation-tracker close` (audit, puis aplatissement sur `master` et sortie de l'entrée de road-map).
**Vérification** : `.venv/bin/python scripts/check_pipeline.py` ; aucune skill existante dans
`git diff --name-only master -- skills`.
**Dernier audit** : cea0665 — RÉSERVES — 2026-09-18 (`.claude/implementation/skill-convention.audit.md`)
**Notes** : `.claude/implementation/pipeline-gabarit.brief.md` appartient à un autre chantier,
non suivi : ne jamais le stager ici.

## Journal de décisions

Chronologique, compacté à la clôture. Ne subsistent que les décisions qui contraignent la suite.

- **2026-09-17** — Règles de code dans `rules/claude-python-style.md` (renommé le 2026-09-18), la
  skill y renvoie. *Pourquoi* : `rules/` se charge au contact des fichiers visés. *Rejeté* :
  règles de code dans la skill.
- **2026-09-17** — Mode de défaillance intégré à la prose ; les blocs cités
  `> *Mode de défaillance* —` deviennent un écart. *Pourquoi* : arbitrage de la dette
  `deux-conventions-de-mode-de-defaillance`. *Rejeté* : bloc cité.
- **2026-09-17** — Commandes globales réservées aux skills de `~/.claude/skills`, via `bin/` ;
  locales par `.claude/bin/` et hook de projet. *Rejeté* : alias, fonctions shell, clé `env`.
- **2026-09-17** — Sonde (Claude Code 2.1.274) : `.claude/bin` exporté par `CLAUDE_ENV_FILE` est vu
  en direct **et par un sous-agent** ; chaque hook reçoit son propre fichier
  (`sessionstart-hook-<n>.sh`), RTK et `sante_skills.py` n'interfèrent pas. *Rejouer* : projet
  jetable + `claude -p "lance en Bash: sonde" --model haiku --allowedTools Bash < /dev/null`.
- **2026-09-17** — `skills/synced/` et `plugins/synced/` ignorés par `.gitignore`. *Pourquoi* :
  `check_pipeline.py` lisait une copie de `skill-creator`. *Rejeté* : les supprimer (non créés par
  le chantier).
- **2026-09-18** — Le champ `paths: "**/.claude/**/*.py"` est conservé. *Pourquoi* : la règle vise
  le Python des configurations Claude, pas tout le Python de tous les projets. *Rejeté* :
  `"**/*.py"` du plan. Conséquence consignée en dette : la règle ne se charge pas sur ce dépôt-ci.
- **2026-09-18** — Réserve d'audit R1 levée par report : une entrée pour le cas confirmé
  (`intent-brief`), une pour le balayage jamais mené. *Rejeté* : les 128 confrontations avant la
  clôture, qui se seraient faites vite et mal.
- **2026-09-18** — Les étapes 8 à 12 ne sont décrites que dans le suivi, pas dans le plan.
  *Pourquoi* : `execution: direct`, aucune délégation n'ira lire le plan. *Rejeté* : rééditer
  `.claude/plans/zany-napping-teacup.md`.
