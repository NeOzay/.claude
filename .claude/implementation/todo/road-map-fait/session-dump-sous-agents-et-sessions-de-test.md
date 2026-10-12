+++
id = "session-dump-sous-agents-et-sessions-de-test"
title = "`session-dump` : détailler les sous-agents au frontmatter, marquer les sessions lancées par `claude -p`"
date = 2026-10-09
source = "analyse des dumps de session du 2026-10-09, après le chantier `dump-sessions`"
+++

## À faire

Deux ajouts au dump, nés de la première analyse des dumps.

- **Les sous-agents au frontmatter** : une table par type de sous-agent (`agentType` du
  `*.meta.json`), avec son nombre de lancements et ses tokens. Les totaux de `[tokens]` incluent
  déjà les sous-agents, mais sans les distinguer. Mesurer le poids des audits a demandé de relire
  les transcriptions brutes de `<session>/subagents/` : `implementation-auditor` y pèse 153 M de
  tokens sur 917 M, en 44 lancements.
- **Les sessions lancées par `claude -p`** : leurs lignes portent `"entrypoint": "sdk-cli"`, au lieu
  de `"cli"` pour une session interactive. Ce dépôt en compte 15, toutes à un tour (« Réponds
  OK. », lancement d'un agent témoin), surtout le 2026-10-06 pour tester les mods. Elles se mêlent
  aux discussions dans le répertoire de dumps. Les marquer dans le frontmatter, ou les écarter
  comme les sessions sans tour.

Le brief de `dump-sessions` prévoyait que d'autres métriques s'ajouteraient au besoin : celles-ci
sont les premières dont l'analyse a eu besoin.

## Références

- skill : `skills/session-dump/SKILL.md`, « Ce qu'elle écrit » ; code :
  `skills/session-dump/scripts/session_dump.py`
- chantier d'origine : `.claude/implementation/done/2026-10-08-dump-sessions.md` et son brief,
  Hors-périmètre (« toute autre métrique »)
- format : `projects/-home-debian--claude/<session>/subagents/agent-<id>.meta.json` (`agentType`)
  et `agent-<id>.jsonl` (`usage` de chaque message) ; champ `entrypoint` des lignes de session
- entrée liée : `refonte-de-l-audit`, qui cite la mesure des audits

## Fait le

2026-10-12, par le chantier `affiner-session-dump`. Le dump porte les tokens de chaque sous-agent,
par lancement et par famille, et le répertoire de dumps n'est plus peuplé que de discussions : les
sessions sans tour, lancées par `claude -p` ou à moins de 2 tours et 10 000 tokens sont écartées,
et la sortie les compte par motif. Archive du chantier :
`.claude/implementation/done/2026-10-12-affiner-session-dump.md`.
