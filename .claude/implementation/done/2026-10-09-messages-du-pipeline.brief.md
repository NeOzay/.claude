+++
gabarit = "brief"
slug = "messages-du-pipeline"
titre = "Raccourcir les messages que le pipeline rend à l'utilisateur : Brief, commit, contexte, audit"
statut = "validé"
"créé" = 2026-10-09
+++

## Intention

**Symptôme** : les messages du pipeline redisent ce que l'utilisateur voit déjà ailleurs — les
fichiers et les diffs dans Neovim, les tokens dans la ligne d'état — : « Ma lecture », « Chemins
stagés », « Voir le diff complet », « Contexte : … sous le seuil », « Le verdict est inscrit au
suivi », « Je ne la lance pas sans votre feu vert ».

**But** : réduire chaque message du pipeline à ce que l'utilisateur ne voit pas déjà ailleurs, et
le cadrage du Brief à des échanges, puis à un fichier que l'utilisateur corrige.

## Critères de réussite

- `grep -rn "Voir le diff\|Ma lecture\|Qu'est-ce qui est faux\|Chemins stagés" skills agents` ne
  rend rien.
- `staging.md` stage toutes les modifications en attente, sauf les exclusions ; `confirmation.md`
  ne présente que le message, le tag et les exclusions, avec deux choix : « Valider », libellé
  ajusté au contexte, et « Autre chose ».
- À la fin d'une Étape, `etape.md` fait demander le commit sous cette forme :

  ```md
  Commit d'Étape proposé :
  - Message : `dump-sessions: E4 — Skill et branchement`, avec le pied d'attribution.
  - Tag : AE4.
  ```

  Pour `<L>E0`, session et Passation, il fait demander l'accord sans afficher le titre.
- intent-brief suit l'ordre : reconnaissance ; échanges, questions regroupées par thème, deux au
  plus par tour ; écriture du Brief, slug choisi là et renommable jusqu'à la validation ;
  corrections de l'utilisateur et arbitrages fermés ; critères et signaux proposés à la fin ;
  validation. Chaque message qui écrit le Brief redonne son chemin et les incertitudes.
- `execution.md` ne fait plus dire la mesure du contexte quand elle reste sous le seuil.
- `audit.md`, « Au retour », impose la restitution en une ligne, puis le tableau
  `# | Réserve | Gravité réelle`.
- Une règle du pipeline interdit les rappels qui reviennent à chaque message sans rien apprendre.
- La mémoire `index-avant-commit` est supprimée, avec sa ligne de `MEMORY.md`, si elle contredit la
  procédure.
- `uvx rumdl fmt --check .` passe.

## Hors-périmètre

- Les choix qui terminent un commit d'Étape ou de Retouche, et le déroulement qu'ils entraînent ;
  le nombre de tours d'un Chantier : entrée `enchainement-du-chantier`, qui porte les décisions
  prises à ce Brief (dit).
- Le fond de l'audit — verdict, relance, forme du rapport : entrée `refonte-de-l-audit`.

## Signaux de dérive

- Le diff touche aux choix de fin d'Étape ou au déroulement qu'ils entraînent (dit).
- Le diff touche à l'échelle du verdict, à la relance de l'audit, à la forme du rapport ou à
  `agents/implementation-auditor.md` (dit).
- Un commit, de quelque type, peut partir sans demande d'accord, ou la règle globale de
  `CLAUDE.md` change (dit).
- intent-brief perd les arbitrages fermés, ou ses questions précèdent la reconnaissance du dépôt
  (dit).
- Un message du pipeline gagne une formule fixe au lieu d'en perdre (dit).

## Contraintes connues de l'utilisateur

Brief :

- **Décision** : le Brief se cadre en plusieurs tours d'échanges avant d'être écrit ; puis il
  s'écrit, et l'utilisateur le corrige : ajustements, résolution des incertitudes, exigences. Les
  signaux de dérive et les critères de réussite se décident à la fin, sur propositions. La
  validation ne vient qu'ensuite (dit).
- **Décision** : aux échanges, les questions se regroupent par thème, deux au plus par tour (dit).
- **Décision** : le slug se choisit à l'écriture du Brief ; jusqu'à la validation, il peut changer,
  en renommant le fichier et le `slug` du front matter (dit).
- **Décision** : chaque fois que le Brief est écrit ou modifié, le message redonne son chemin, et ne
  rappelle que les incertitudes (dépôt:
  .claude/implementation/todo/road-map/messages-du-pipeline.md).
- **Décision** : le principe de la Phase 4 d'intent-brief — les ambiguïtés relevées se tranchent
  par arbitrages fermés, `AskUserQuestion` — se conserve. Ces arbitrages se posent une fois le Brief
  écrit, sur les incertitudes restantes à réponses fermées, en un seul appel, avant de proposer
  critères et signaux ; les échanges restent des questions ouvertes (dit).
- **Existant** : « Ma lecture » et « Qu'est-ce qui est faux là-dedans ? » sont prescrits par la
  Phase 2 d'intent-brief, qui pose aussi le Brief et arrête le slug (dépôt:
  skills/intent-brief/SKILL.md).

Commits :

- **Décision** : un commit, de quelque type qu'il soit, prend toutes les modifications en
  attente ; la proposition n'indique que les fichiers exclus, ceux qui n'ont aucun rapport avec la
  tâche en cours (dit).
- **Décision** : la proposition d'un commit se réduit à son message et à son tag (dépôt:
  .claude/implementation/todo/road-map/messages-du-pipeline.md).
- **Décision** : un commit qui n'est ni d'Étape ni de Retouche se propose avec deux choix — 1.
  Valider, libellé ajusté au contexte (par exemple « Réaliser la Clôture ») ; 2. Autre chose (dit).
- **Décision** : les commits mécaniques — `<L>E0`, session, Passation — demandent toujours
  l'accord, mais sans afficher leur titre. Le Suivi écrit après la validation du Plan, l'accord se
  demande pour le commit `<L>E0` (dit).
- **Existant** : `staging.md` interdit `git add -A`, `-u` et `.`, et ne stage que les chemins
  présentés ; `confirmation.md` impose les réponses « Valider », « Modifier », « Voir le diff
  complet » (dépôt: skills/git-smart-commit/references/staging.md, confirmation.md).
- **Historique** : un commit approuvé pour 4 fichiers en a pris 31 le 2026-10-04, parce que
  l'utilisateur avait indexé les autres pendant sa relecture (dépôt:
  projects/-home-debian--claude/memory/index-avant-commit.md).
- **Décision** : la mémoire `index-avant-commit` se supprime si elle contredit la nouvelle
  procédure de commit (dit).

Contexte, audit, formules de fin :

- **Décision** : la mesure du contexte ne se dit que si elle déclenche la question de la
  Passation (dépôt: .claude/implementation/todo/road-map/messages-du-pipeline.md).
- **Décision** : l'audit se restitue en une ligne — verdict et chemin du rapport —, puis les
  réserves en tableau `# | Réserve | Gravité réelle`, sans « Le verdict est inscrit au suivi »
  (dépôt: .claude/implementation/todo/road-map/messages-du-pipeline.md).
- **Décision** : plus de rappel qui revient à chaque message sans rien apprendre, comme « Je ne la
  lance pas sans votre feu vert » ou « Le suivi et le rapport d'audit restent non commités »
  (dépôt: .claude/implementation/todo/road-map/messages-du-pipeline.md).
- **Existant** : ces formules-là ne figurent dans aucun texte de skill ni d'agent ; elles naissent
  de procédures qui disent de mesurer ou d'inscrire, sans dire de se taire (dépôt:
  skills/implementation-tracker/references/execution.md, audit.md).

## Incertitudes à lever en plan

— aucune
