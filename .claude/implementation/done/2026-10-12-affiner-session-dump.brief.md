+++
gabarit = "brief"
slug = "affiner-session-dump"
titre = "`session-dump` : détailler les sous-agents au frontmatter, écarter les sessions lancées par `claude -p` et les sessions vides"
statut = "validé"
"créé" = 2026-10-11
+++

## Intention

**Symptôme** : « Mesurer le poids des audits a demandé de relire les transcriptions brutes de
`<session>/subagents/` » ; les sessions lancées par `claude -p` « se mêlent aux discussions dans le
répertoire de dumps » (road-map: `session-dump-sous-agents-et-sessions-de-test`).
**But** : que chaque dump dise ce que chacun de ses sous-agents a consommé, et que le répertoire de
dumps ne garde que les discussions.

## Critères de réussite

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

## Hors-périmètre

- L'analyse des dumps : la skill n'en analyse aucun (dépôt: skills/session-dump/SKILL.md).
- Le dump des transcriptions des sous-agents : seules leurs statistiques entrent au frontmatter de
  la session parente (dépôt: .claude/implementation/done/2026-10-08-dump-sessions.brief.md).
- Le coût par sous-agent : `cost-state` ne le ventile pas, et il ne s'estime pas ; le coût reste
  celui de la session (tranché).

## Signaux de dérive

- **S1** — Un critère d'écart autre que `sdk-cli` ou « moins de 2 tours et moins de 10 k
  tokens » : fondé sur le titre, le contenu, ou un autre seuil (dit).
- **S2** — Un coût par sous-agent, ou une table de prix, dans le diff (dit).
- **S3** — Le `[tokens]` d'une session à `cost-state` change, recalculé depuis les transcriptions
  (dit).
- **S4** — Le corps du dump change : transcriptions des sous-agents, résultats d'outils (dit).
- **S5** — Le diff interprète ou classe le contenu des sessions au lieu de l'extraire (dit).

## Contraintes connues de l'utilisateur

- **Décision** : les tokens des sous-agents se découpent comme ceux de la session, selon les champs
  de `[tokens]` (dit).
- **Décision** : ce découpage se donne à deux niveaux, par lancement de sous-agent et par famille
  (`agentType`) (dit).
- **Décision** : une session lancée par `claude -p` (`entrypoint = "sdk-cli"`) n'est pas dumpée
  (tranché).
- **Décision** : une session de moins de 2 tours **et** de moins de 10 000 tokens n'est pas dumpée
  (dit, tranché).
- **Décision** : le seuil de 10 000 tokens porte sur `[tokens].total`, sous-agents compris
  (tranché).
- **Décision** : la sortie compte les sessions écartées par motif (tranché).
- **Rejeté d'emblée** : écarter toute session de moins de 5 tours — une session de Chantier en
  compte peu pour des millions de tokens, et le pipeline découpe un Chantier en plusieurs sessions
  (dit).
- **Existant** : `cost-state` ventile tokens et coût par modèle (`modelUsage`), jamais par agent ;
  les tokens d'un sous-agent ne se lisent que dans l'`usage` de son `agent-<id>.jsonl`
  (dépôt: projects/-home-debian--claude/*.jsonl).
- **Existant** : chaque `agent-<id>.jsonl` a son `agent-<id>.meta.json`, qui porte `agentType` et
  `description` ; 81 lancements dans ce dépôt, dont 47 `implementation-auditor` et 20
  `plan-reviewer` (dépôt: projects/-home-debian--claude/*/subagents/).
- **Existant** : les 15 sessions `sdk-cli` de ce dépôt ont 1 tour, aucun titre, 26 k à 85 k tokens
  (dépôt: projects/-home-debian--claude/*.jsonl).
- **Existant** : la règle « 2 tours et 10 k tokens » écarte 9 sessions interactives, à 0 ou
  314 tokens (dépôt: projects/-home-debian--claude/*.jsonl).
- **Existant** : une session sans tour est déjà écartée, et la sortie compte les sessions écartées
  (dépôt: skills/session-dump/scripts/session_dump.py, `dumper`).

## Incertitudes à lever en plan

- La forme TOML des deux niveaux : noms des tables, clé d'un lancement (identifiant de l'agent,
  description).
