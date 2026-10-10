+++
id = "enchainement-du-chantier"
title = "Réduire les allers-retours d'un Chantier : un accord par geste, des choix de fin d'Étape qui enchaînent"
date = 2026-10-09
source = "analyse des dumps de session du 2026-10-09, après le chantier `dump-sessions`"
+++

## À faire

Faire tenir chaque passage obligé d'un Chantier en un seul tour de l'utilisateur.

- **Plan** : ce que l'utilisateur doit trancher avant de valider le Plan, réserves de
  `plan-reviewer` comprises, se demande **avant** `ExitPlanMode`, par `AskUserQuestion`, et non
  avec la demande de validation.
- **De la validation du Plan à `/clear`**, deux tours seulement :
  1. Plan validé → Suivi écrit → rendre la main avec la proposition du commit `<L>E0` ;
  2. un seul accord → commit `<L>E0`, section `## Passation` écrite, commit de Passation → rendre la
     main avec `/clear`, puis `/model <modèle>` et `/implementation-tracker @<suivi>`.

  Aujourd'hui, la Passation demande un second accord pour son propre commit (« Commit et fait la
  Passation », puis « 1 »), dans 6 sessions de création.
- **Fin d'Étape** : la proposition de commit (forme : entrée `messages-du-pipeline`) se termine
  par trois choix.
  1. Valider et passer à l'Étape suivante ;
  2. Valider et attendre ;
  3. Autre chose.

  Décidé au Brief de `messages-du-pipeline` (2026-10-09) : ces trois choix valent aussi pour une
  Retouche, qui est un commit d'Étape ; « Valider » s'ajuste au contexte ; les choix et le
  déroulement qu'ils entraînent relèvent de cette entrée, pas de `messages-du-pipeline`.
- **« Commit » sans proposition préalable** : quand l'utilisateur demande un commit et qu'aucun
  message n'a été proposé avant, lancer directement `git commit` avec le message rédigé. La demande
  de permission de Claude Code (règle `ask`) tient lieu de proposition. Cela suppose une règle
  `ask` sur `git commit` dans `settings.json`, qui tourne aujourd'hui en `defaultMode = "auto"`.
- **Reprise** : après `/implementation-tracker @<suivi>`, la reprise demande « Je démarre l'Étape
  1 ? », et l'utilisateur répond « oui », « Commence » ou « Commit puis commence » dans 8 reprises.
  Quand la reprise ne signale aucun écart, l'Étape suivante peut démarrer d'elle-même.

Constats tirés des 76 dumps de ce dépôt (2026-09-09 au 2026-10-09) :

- 272 des 594 messages de l'utilisateur (46 %) sont procéduraux : 122 « oui », « 1 » ou
  « Valider », 58 « Commit et continue », 33 demandes d'audit, 20 « commit », 19 « Corrige
  R<n> », 11 « Passe au plan » ;
- chaque tour relit tout le contexte : sur 917 M de tokens, 97,6 % sont lus en cache, et une
  session de Chantier passe vite les 150 000 tokens de contexte par tour (`dump-sessions` : de
  105 000 à 181 000 tokens sur ses quatre Étapes) ;
- deux reprises de Chantier ont commencé par le dernier message de la session précédente, recopié
  à la main par `/copy` (`2026-10-05-clear-conversation-history-5559ebe9`,
  `2026-10-08-commit-et-suite-965f9c0b`). Une Passation faite à la demande, en un accord, aurait
  porté ce que ce message transmettait.

Questions à trancher au Brief ou au Plan :

- le choix 1 enchaîne sur l'Étape suivante sans nouvel accord : la mesure du contexte et la
  proposition de Passation doivent alors passer avant le démarrage de l'Étape ;
- la règle `ask` sur `git commit` vaut aussi pour les commits que le pipeline propose déjà. Faut-il
  la borner, ou admettre une double confirmation pour ceux-là ?

## Fait le

2026-10-10, par le chantier `enchainement-du-chantier`. Un commit de Chantier se propose avec des
choix qui disent la suite : à `<L>E0`, « Valider et faire la Passation (commit inclus) » ou
« Valider et passer à l'Étape suivante » ; après une Étape ou une Retouche, passer à la suivante,
attendre, ou lancer l'audit de Clôture, avec la Passation au-delà de 300 000 tokens. La relecture
du Plan se tranche par `AskUserQuestion` avant `ExitPlanMode`, la reprise tient en un court
message, et le Brief se valide par une proposition dédiée. Archive du chantier :
`.claude/implementation/done/2026-10-10-enchainement-du-chantier.md`.

## Références

- création : `skills/implementation-tracker/references/creation.md`, points 3 (relecture du
  Plan), 9 (commit `<L>E0`) et 10 (Passation)
- exécution : `skills/implementation-tracker/references/execution.md`, tableau des déclencheurs
  et « Passation »
- reprise : `skills/implementation-tracker/SKILL.md`, Phase 3
- commit : `skills/git-smart-commit/references/etape.md` (cas Passation),
  `skills/git-smart-commit/references/confirmation.md`
- permissions : `settings.json`, bloc `permissions`
- dumps : `.claude/session-dump/-home-debian--claude/`. Cas types :
  `2026-10-08-commit-rapide.md` (création, Passation en deux accords) et
  `2026-10-08-commit-et-suite-cc91322b.md` (reprise, quatre Étapes)
- entrées liées : `messages-du-pipeline`, qui porte la forme des messages
