+++
gabarit = "brief"
slug = "dump-sessions"
titre = "Dumper les sessions d'un espace de travail, statistiques en frontmatter TOML"
statut = "validé"
"créé" = 2026-10-08
+++

## Intention

**Symptôme** : pas de matière pour « rechercher des voies d'amélioration pour le pipeline des
Chantiers, réduire la consommation de tokens dans les discussions et fluidifier le workflow ».
**But** : « optimiser les échanges et faire remonter les lourdeurs » ; une commande qui dumpe toutes les discussions d'un espace de travail, chacune avec ses
statistiques en frontmatter TOML, pilotée par un script Python.

## Critères de réussite

- La commande, lancée sans argument puis avec le chemin d'un autre projet, écrit un dump par
  session principale de l'espace de travail dans `<projet>/.claude/session-dump/<id>/`, nommé
  `<date de création>-<nom>.md`.
- Chaque frontmatter se lit par `tomllib` et porte tokens (total et par type), coût, durée,
  nombre de tours.
- Aucun corps ne contient de résultat d'outil ni de thinking ; chaque appel d'outil y tient en
  une ligne.
- Le skill porte `disable-model-invocation: true`.
- Les tests du script passent, selon `OUTILLAGE.md`.

## Hors-périmètre

- L'analyse des dumps : le Chantier ne fait que le dump ; ils sont analysés dans une discussion
  à part (dit).
- D'autres métriques que tokens, coût, durée, nombre de tours : « d'autres pourront s'ajouter au
  besoin », pas dans ce Chantier (dit).
- Les résultats d'outils et le thinking dans le corps : « ils n'interviennent pas dans les
  discussions » (dit).

## Signaux de dérive

- Autre chose que de l'extraction : le diff interprète, classe ou analyse le contenu des
  sessions (dit).

## Contraintes connues de l'utilisateur

- **Décision** : une /commande appelable uniquement par l'utilisateur (dit).
- **Décision** : elle dumpe toutes les discussions d'un espace de travail dans
  `.claude/session-dump/<id>/`, où `<id>` est le nom du répertoire de l'espace de travail sous
  `projects/` (ex. `-home-debian--claude`) (dit).
- **Décision** : le nom d'un dump commence par la date de création, suivie du nom de la
  discussion (dit).
- **Décision** : la commande peut prendre un chemin en entrée (dit).
- **Décision** : piloté par un script Python (dit).
- **Décision** : les lourdeurs visées sont « des textes à rallonge qui ne m'apprennent pas
  grand-chose » (dit).
- **Décision** : métriques du frontmatter — tokens (total et découpés par type), coût, durée,
  nombre de tours (dit).
- **Décision** : d'autres métriques pourront s'ajouter au besoin (dit).
- **Décision** : « il est fort probable que des ajustements soient nécessaires en cours
  d'implémentation » — un ajustement du format en cours de route n'est pas une dérive (dit).
- **Décision** : le dump va sous `./.claude` relatif à l'espace de travail :
  `<projet>/.claude/session-dump/<id>/` (dit).
- **Décision** : « un dump écrase les dumps existants » (dit).
- **Décision** : le chemin en entrée désigne le répertoire du projet, traduit en son `<id>` ;
  sans argument, le répertoire courant (tranché).
- **Décision** : dans le corps, un appel d'outil tient en une ligne — nom et cible, sans le
  contenu des arguments (tranché).
- **Décision** : les sous-agents ne sont pas dumpés ; leurs tokens et leur coût comptent dans
  le frontmatter de la session parente (tranché).
- **Décision** : nom de la discussion — titre donné par l'utilisateur, sinon titre généré
  (`ai-title`), sinon UUID de la session (tranché).
- **Existant** : une commande réservée à l'utilisateur est, dans ce dépôt, un skill à
  `disable-model-invocation` (dépôt: skills/implementation-tracker/SKILL.md).
- **Existant** : 23 sessions de ce dépôt n'ont pas de titre généré `ai-title`
  (dépôt: projects/-home-debian--claude/*.jsonl).
- **Existant** : 206 sessions sur 210 portent une ligne `cost-state` (dépôt: projects/*/*.jsonl).
- **Existant** : les sessions sont en JSONL, `projects/<projet encodé>/<uuid>.jsonl`, chaque
  message `assistant` porte son `usage`, chaque ligne `gitBranch`, une ligne `cost-state` donne
  coût et durées, les sous-agents sont dans `<uuid>/subagents/`
  (dépôt: projects/-home-debian--claude/3fa40780-a566-45e6-a9bc-abcf88b57c95.jsonl).

## Incertitudes à lever en plan

- `session-dump/` : versionné ou ignoré par git ?
- « écrase les dumps existants » : fichier par fichier, ou tout le répertoire `<id>/` ? Un
  titre changé entre deux dumps laisserait sinon l'ancien fichier.
- Les 4 sessions sans `cost-state` : coût et durée absents, recalculés, ou session écartée ?
- « nombre de tours » : messages de l'utilisateur, ou appels à l'API ?
