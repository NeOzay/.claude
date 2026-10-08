+++
gabarit = "suivi"
slug = "dump-sessions"
titre = "Dumper les sessions d'un espace de travail, statistiques en frontmatter TOML"
branche = "dump-sessions"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "sonnet"
plan = ".claude/implementation/done/2026-10-08-dump-sessions.plan.md"
brief = ".claude/implementation/done/2026-10-08-dump-sessions.brief.md"
audit = ".claude/implementation/done/2026-10-08-dump-sessions.audit.md"
skills = ["skill-convention"]
"créé" = 2026-10-08
maj = 2026-10-08
+++

## Objectif et périmètre

**Symptôme** : pas de matière pour « rechercher des voies d'amélioration pour le pipeline des
Chantiers, réduire la consommation de tokens dans les discussions et fluidifier le workflow ».

**But** : « optimiser les échanges et faire remonter les lourdeurs » ; une commande qui dumpe
toutes les discussions d'un espace de travail, chacune avec ses statistiques en frontmatter TOML,
pilotée par un script Python.

**Critères de réussite** :

- La commande, lancée sans argument puis avec le chemin d'un autre projet, écrit un dump par
  session principale de l'espace de travail dans `<projet>/.claude/session-dump/<id>/`, nommé
  `<date de création>-<nom>.md`.
- Chaque frontmatter se lit par `tomllib` et porte tokens (total et par type), coût, durée,
  nombre de tours.
- Aucun corps ne contient de résultat d'outil ni de thinking ; chaque appel d'outil y tient en
  une ligne.
- Le skill porte `disable-model-invocation: true`.
- Les tests du script passent, selon `OUTILLAGE.md`.

**Hors-périmètre** :

- L'analyse des dumps : le Chantier ne fait que le dump ; ils sont analysés dans une discussion
  à part.
- D'autres métriques que tokens, coût, durée, nombre de tours.
- Les résultats d'outils et le thinking dans le corps.

**Signaux de dérive** :

- Autre chose que de l'extraction : le diff interprète, classe ou analyse le contenu des
  sessions.

## Étapes

- [x] 1. Lecture et statistiques — skills/session-dump/{ruff.toml,pyrightconfig.json},
      skills/session-dump/scripts/session_dump.py,
      skills/session-dump/scripts/tests/{conftest.py,test_lecture.py} — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`
- [x] 2. Rendu du frontmatter, du corps et du nom — skills/session-dump/scripts/session_dump.py,
  skills/session-dump/scripts/tests/test_rendu.py
  — vérif: `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`
- [x] 3. Commande et écriture — skills/session-dump/scripts/session-dump-cli.py, bin/session-dump,
      skills/session-dump/scripts/tests/test_cli.py — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/ && command -v session-dump`
- [x] 4. Skill et branchement, essai réel — skills/session-dump/SKILL.md, .gitignore
  — vérif: contrôle des vrais dumps de la section « Vérification de bout en bout » du plan

## État courant

**Prochaine action** : aplatissement sur `master` (`commit-chantier cloture dump-sessions`). L'audit
de clôture est RÉSERVES : R2 constatée par l'utilisateur, R5 à R7 versées au registre de dette.

**Vérification** : `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/ &&
uvx ruff check skills/session-dump && uvx ruff format --check skills/session-dump &&
uvx --with pytest basedpyright -p skills/session-dump`

**Dernier audit** : 5ed63de — RÉSERVES — 2026-10-08

**Notes** : chaque Étape passe aussi ruff et basedpyright (`OUTILLAGE.md`).

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien — l'Étape 1 n'a pas commencé.

**À savoir** :

- Les lignes `agent-name` (`agentName`, ex. « clear-conversation-history ») ne sont pas un titre
  donné par l'utilisateur : seul `custom-title` (`customTitle`) l'est.
- Une commande `/` arrive comme message utilisateur dont le texte porte les balises
  `<command-name>` et `<command-args>` ; le corps du skill qu'elle charge suit en message
  `isMeta`, à exclure.
- Le texte d'un message utilisateur peut embarquer des blocs `<system-reminder>`.
- Des lignes `continued-in` renvoient vers une autre session : chacune reste une session à part.
- Le JSONL de la session en cours grossit pendant le dump : elle y figure, partielle.

## Journal de décisions

- **2026-10-08** — Les sessions sans aucun tour ne sont pas dumpées ; leur compte s'affiche.
  *Pourquoi* : sans tour, pas de discussion ; relevé Q1 de plan-reviewer, plan validé par
  l'utilisateur en connaissance. *Rejeté* : un dump vide par session.
- **2026-10-08** — Tokens, coût et durée viennent de la dernière ligne `cost-state` ; à défaut,
  tokens recalculés depuis les transcriptions (principale et sous-agents), coût et durée omis.
  *Pourquoi* : `modelUsage` est seul cohérent avec `totalCostUSD`. *Rejeté* : sommer les
  transcriptions dans tous les cas.
- **2026-10-08** — Les nombres du frontmatter s'écrivent par groupes de trois chiffres séparés par
  `_` (`45_372_384`). *Pourquoi* : demande de l'utilisateur, lisibilité ; TOML admet `_` et
  `tomllib` le relit (Retouche E4.1). *Rejeté* : nombres bruts du Plan.
- **2026-10-08** — Le résumé de compaction (`isCompactSummary`) n'est pas un tour ; un caractère non
  encodable en UTF-8 est écrit U+FFFD. *Pourquoi* : audit R1 et R4 — le résumé gonflait `tours` et
  le corps, une demi-paire de substitution faisait échouer tout le dump. *Rejeté* : compter le
  résumé comme tour ; écarter la session fautive.
