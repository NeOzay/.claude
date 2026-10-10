+++
gabarit = "brief"
slug = "enchainement-du-chantier"
titre = "Réduire les allers-retours d'un Chantier : un accord par geste, des choix de fin d'Étape qui enchaînent"
statut = "validé"
"créé" = 2026-10-09
+++

## Intention

**Symptôme** : près de la moitié des messages de l'utilisateur sont procéduraux — « oui », « 1 »,
« Valider », « Commit et continue », « Commit et fait la Passation » puis « 1 », « Commence ».
Chaque tour relit tout le contexte.

**But** : qu'un passage obligé d'un Chantier — validation du Plan, commit `<L>E0` et Passation,
fin d'Étape, reprise — tienne en un seul tour de l'utilisateur.

## Critères de réussite

- **C1** — `creation.md` suit cet ordre : `plan-reviewer` lancé une fois, son verdict consigné
  dans une section en tête du Plan, `AskUserQuestion`, Plan corrigé selon les réponses,
  `ExitPlanMode`. Plus de point Passation séparé : elle devient le choix 1 du commit `<L>E0`.
- **C2** — `etape.md` fait proposer le commit `<L>E0` avec deux choix : « Valider et faire la
  Passation », « Valider et passer à l'Étape suivante ».
- **C3** — `etape.md` fait proposer le commit d'Étape ou de Retouche avec trois choix : « Valider
  et passer à l'Étape suivante », « Valider et attendre », « Autre chose » ; au-delà de 300 000
  tokens, « Valider et commencer la Passation » s'y ajoute ; après la dernière Étape, le premier
  devient « Valider et lancer l'audit de Clôture ».
- **C4** — `execution.md` lance `contexte` avant de proposer le commit d'Étape ou de Retouche, plus
  après.
- **C5** — `confirmation.md` garde « un accord ne vaut que pour son commit », avec pour seule
  exception écrite le commit de Passation couvert par « Valider et faire la Passation ».
- **C6** — la Phase 3 de `SKILL.md` rend un court message : l'Étape en cours, la prochaine action,
  les blocages, puis la proposition de commencer l'Étape X ; les écarts restent signalés.
- **C7** — la semence `brief` prescrit la numérotation des critères (`**C1** — …`) et des signaux
  (`**S1** — …`).
- **C8** — la Phase 6 d'`intent-brief` fait proposer la validation du Brief dans un message dédié,
  avec deux choix — « Valider le Brief et passer au Plan », « Autre chose » — ; seule une réponse
  à cette proposition passe `statut` à `validé`.
- **C9** — `uvx rumdl fmt --check .` passe.

## Hors-périmètre

- La règle `ask` sur `git commit` dans `settings.json`, et le « commit » lancé sans proposition
  préalable : abandonnés (dit).
- La forme des messages du pipeline : Chantier `messages-du-pipeline`, livré (dépôt:
  .claude/implementation/done/2026-10-09-messages-du-pipeline.brief.md).
- Le fond de l'audit — verdict, relance, forme du rapport : entrée `refonte-de-l-audit` (dépôt:
  .claude/implementation/todo/road-map/refonte-de-l-audit.md).

## Signaux de dérive

- **S1** — un commit part sans que l'utilisateur ait choisi un des choix proposés, hors le commit
  de Passation couvert par le choix 1 de `<L>E0` (dit).
- **S2** — le diff touche au bloc `permissions` de `settings.json`, ou à la règle absolue du
  `CLAUDE.md` racine (dit).
- **S3** — la reprise démarre une Étape sans la réponse de l'utilisateur (dit).
- **S4** — `plan-reviewer` est relancé sur le Plan corrigé (dit).
- **S5** — les seuils de 300 000 ou de 400 000 tokens changent (dit).
- **S6** — le diff touche au fond de l'audit — verdict, relance, rapport,
  `agents/implementation-auditor.md` — ou à la forme des messages hors des choix (dit).

## Contraintes connues de l'utilisateur

Commits et choix :

- **Décision** : un accord ne vaut que pour le commit proposé, sauf le choix « Valider et faire la
  Passation » (dit).
- **Décision** : le commit `<L>E0` se propose avec deux choix — 1. Valider et faire la Passation ;
  2. Valider et passer à l'Étape suivante (dit).
- **Décision** : le choix « Valider et faire la Passation » couvre aussi le commit de Passation,
  fait dans la foulée sans nouvel accord : rien n'a commencé, la section `## Passation` ne porte
  rien que l'utilisateur doive relire (dit).
- **Décision** : les autres commits d'Étape se proposent avec trois choix — 1. Valider et passer à
  l'Étape suivante ; 2. Valider et attendre ; 3. Autre chose (dit).
- **Décision** : ces trois choix valent aussi pour une Retouche ; « Valider » s'ajuste au contexte
  (dépôt: .claude/implementation/todo/road-map/enchainement-du-chantier.md).
- **Décision** : le décompte des tokens se fait en fin d'Étape, avant de proposer le commit ;
  au-delà de 300 000 tokens, le choix « Valider et commencer la Passation » s'ajoute aux autres
  (dit).
- **Décision** : « Valider et passer à l'Étape suivante » enchaîne quel que soit le décompte : le
  plafond est de 400 000 tokens, et le tenir revient à l'utilisateur (dit).
- **Décision** : après la dernière Étape, ce choix devient « Valider et lancer l'audit de
  Clôture » (dit).
- **Existant** : « Un accord donné pour un commit ne vaut pas pour le suivant, même dans la même
  session et au sein de la même procédure » (dépôt:
  skills/git-smart-commit/references/confirmation.md).
- **Existant** : le contexte se mesure après le commit d'Étape ou de Retouche ; au-delà de
  300 000 tokens, la Passation se propose (dépôt:
  skills/implementation-tracker/references/execution.md).
- **Intouchable** : aucun commit sans accord explicite de l'utilisateur (dépôt: CLAUDE.md).

Brief :

- **Décision** : critères de réussite et signaux de dérive se numérotent — `**C1** — …`,
  `**S1** — …` — et la semence `brief` le prescrit (dit).
- **Décision** : la validation du Brief se propose dans un message dédié, qui dit que rien n'y sera
  plus ajouté et que le Plan suit ; un accord sur des critères, des signaux ou une décision ne vaut
  pas validation (dit).
- **Historique** : le 2026-10-09, ce Brief est passé à `validé` sur l'accord donné aux critères et
  aux signaux, faute d'une proposition de validation (dit).

Plan et reprise :

- **Décision** : `plan-reviewer` se lance une fois ; son résultat se consigne dans une section en
  tête du Plan ; puis `AskUserQuestion` pose à l'utilisateur ce qu'il doit trancher, et le Plan
  se corrige selon ses réponses, avant `ExitPlanMode` (dit).
- **Décision** : la reprise vérifie que tout est en ordre, puis propose de commencer l'Étape X,
  dans un court message qui ne restitue que l'Étape en cours, la prochaine action et les blocages
  (dit).
- **Existant** : `ExitPlanMode` présente aujourd'hui le Plan et le verdict ensemble, et le Plan ne
  se corrige jamais d'office sur un verdict (dépôt:
  skills/implementation-tracker/references/creation.md).

## Incertitudes à lever en plan

— aucune
