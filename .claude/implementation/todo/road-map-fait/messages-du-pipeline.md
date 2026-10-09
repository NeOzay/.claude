+++
id = "messages-du-pipeline"
title = "Raccourcir les messages que le pipeline rend à l'utilisateur : Brief, commit, contexte, audit"
date = 2026-10-09
source = "analyse des dumps de session du 2026-10-09, après le chantier `dump-sessions`"
+++

## À faire

Réduire chaque message du pipeline à ce que l'utilisateur ne voit pas déjà ailleurs : il relit
les fichiers et les diffs dans Neovim, et il voit les tokens consommés dans la ligne d'état.

- **Brief** : écrire directement le fichier, seule source de vérité, sans restitution « Ma
  lecture » ni « Qu'est-ce qui est faux là-dedans ? ». Le message ne rappelle que les incertitudes
  et invite à les trancher. Chaque fois que le Brief est écrit ou modifié, le message redonne son
  chemin. Cela remplace la Phase 2 d'`intent-brief`, qui est un choix de conception argumenté : le
  Brief doit dire ce qui en tient lieu, par exemple pour le slug, arrêté aujourd'hui en Phase 2.
- **Commit d'Étape** : la proposition se réduit au message et au tag.

  ```md
  Commit d'Étape proposé :
  - Message : `dump-sessions: E4 — Skill et branchement`, avec le pied d'attribution.
  - Tag : AE4.
  ```

  Ni « Chemins stagés », ni « Hors commit », ni « Voir le diff complet ». Les trois choix de fin
  d'Étape sont l'objet de l'entrée `enchainement-du-chantier`.
- **Contexte** : ne plus écrire « Contexte : 105 871 tokens, sous le seuil de Passation » après
  chaque commit. La mesure ne se dit que si elle déclenche la question de la Passation.
- **Audit** : le verdict tient en une ligne, puis les réserves en tableau, une colonne de
  commentaire court.

  ```md
  L'audit de clôture rend **RÉSERVES** : `.claude/implementation/dump-sessions.audit.md`.

  | # | Réserve | Gravité réelle |
  |---|---|---|
  | R1 | Le résumé de compaction est compté comme un tour. | Fausse `tours`. |
  ```

  Ne plus écrire « Le verdict est inscrit au suivi (`Dernier audit` et champ `audit`) ».
- **Formules de fin** : retirer les rappels qui reviennent à chaque message sans rien apprendre,
  comme « Je ne la lance pas sans votre feu vert » ou « Le suivi et le rapport d'audit restent non
  commités ».

Constats tirés des 76 dumps de ce dépôt (2026-09-09 au 2026-10-09) :

- 586 messages de l'assistant, 1 566 caractères de texte en moyenne, appels d'outils exclus ;
- l'option « Voir le diff complet » apparaît sous ses diverses formes plus de 70 fois, et
  l'utilisateur ne l'a jamais choisie ;
- « Chemins stagés » ou « Fichiers stagés » : plus de 30 listes ; « Qu'est-ce qui est faux
  là-dedans ? » : 17 fois ; « Ma lecture » : 15 fois.

Question à trancher au Brief ou au Plan :

- `confirmation.md` pose qu'un accord ne couvre que ce qui a été présenté, chemins stagés compris.
  Si la proposition ne les présente plus, qu'est-ce qui garantit que le commit d'Étape ne prend que
  les fichiers de l'Étape ? La mémoire `index-avant-commit` rappelle qu'un commit de 4 fichiers en
  a pris 31 le 2026-10-04, parce que l'utilisateur avait indexé les autres pendant sa relecture.

## Fait le

2026-10-09, par le chantier `messages-du-pipeline`. Archive :
`.claude/implementation/done/2026-10-09-messages-du-pipeline.md`.

## Références

- Brief : `skills/intent-brief/SKILL.md`, Phases 2 et 5 ;
  `skills/intent-brief/references/grille-questions.md`
- commit : `skills/git-smart-commit/references/confirmation.md` (« Ce qui est présenté », les trois
  réponses), `etape.md` (procédure, point 4), `staging.md`
- contexte : `skills/implementation-tracker/references/execution.md`, « Passation », tableau des
  mesures
- audit : `skills/implementation-tracker/references/audit.md`, « Au retour » ;
  `skills/implementation-tracker/references/cloture.md`, point 1
- dumps : `.claude/session-dump/-home-debian--claude/`. Cas types : `2026-10-08-commit-rapide.md`
  (Brief) et `2026-10-08-commit-et-suite-cc91322b.md` (Étapes, audit)
- mémoire : `projects/-home-debian--claude/memory/index-avant-commit.md`
- entrées liées : `enchainement-du-chantier`, qui porte le nombre de tours, et
  `refonte-de-l-audit`, qui porte le fond de l'audit
