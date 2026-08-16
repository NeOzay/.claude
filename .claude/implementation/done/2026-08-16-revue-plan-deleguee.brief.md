---
slug: revue-plan-deleguee
titre: Déléguer la revue de plan à un sous-agent
statut: validé
execution: direct
créé: 2026-08-16
---

## Intention

**Symptôme** : `intent-brief` et `implementation-tracker` savent tous deux faire le plan et la
confrontation plan ↔ brief. Le tracker duplique le flux avec une clause d'exception
(`SKILL.md:126-127`), arbitrée par une condition que le modèle doit détecter lui-même.

**But** : couper `## Étape 6 — Passage au plan` d'`intent-brief` pour passer directement dans
`implementation-tracker` et créer le plan à l'intérieur. Migrer la comparaison brief ↔ plan dans le
tracker, réalisée par un sous-agent qui vérifie aussi la qualité du plan. (dit)

## Critères de réussite

- une seule voie mène au plan : `intent-brief` → `implementation-tracker` → plan (dit)
- la comparaison brief ↔ plan est exécutée par un sous-agent, pas par le modèle de cadrage (dit)
- le sous-agent juge aussi la qualité du plan (dit)
- **pas de brief** → le sous-agent juge la qualité du plan seulement (dit)
- la revue a lieu **avant** que le plan soit présenté à l'utilisateur ; verdict et plan arrivent
  dans le même `ExitPlanMode` (dit)

## Hors-périmètre

Quatre fichiers, pas un de plus : `skills/intent-brief/SKILL.md`,
`skills/implementation-tracker/SKILL.md`, `agents/plan-reviewer.md` (nouveau) et
`skills/implementation-tracker/references/contrat.md`. (dit)

- `gabarit-brief.md`, `gabarit-suivi.md`, `audit.md`, `dette.md`, `cloture.md` ne sont pas
  touchés (dit)
- `agents/implementation-auditor.md` et `agents/step-implementer.md` ne sont pas touchés (dit)
- pas d'alignement général des renvois du pipeline : ce n'est pas ce chantier (dit)

## Signaux de dérive

- si `intent-brief` conserve la moindre mécanique de plan ou de confrontation après la coupe,
  c'est raté — la duplication supprimée serait seulement déplacée (dit)
- si le prompt de `plan-reviewer` l'amène à proposer des alternatives de conception plutôt qu'à
  contrôler un contrat, c'est raté (dit)
- si une règle est dupliquée dans un `SKILL.md` au lieu d'être définie dans `contrat.md` avec un
  renvoi ancré, s'arrêter — ça défait le commit `3ebf3fe` (dit)

## Contraintes connues de l'utilisateur

- **Structure existante** : `intent-brief` porte les Étapes 6 (plan), 7 (confrontation) et 8
  (renvoi au tracker) ; le tracker duplique 6 et 7 en Étape 2 points 2-3
  (dépôt: skills/implementation-tracker/SKILL.md:117-127)
- **Réutiliser** : le contrat des sous-agents est déjà écrit — chemins absolus, git en lecture
  seule, l'appelant ne recopie rien, bloc de sortie normalisé
  (dépôt: skills/implementation-tracker/references/contrat.md#contrat-des-sous-agents)
- **Agents existants** : `step-implementer` et `implementation-auditor` seulement ; aucun agent de
  revue de plan (dépôt: agents/)
- **`implementation-tracker` est `disable-model-invocation: true`** : il ne s'invoque qu'à la main
  (dépôt: skills/implementation-tracker/SKILL.md:8)

## Décisions arrêtées

- **Position de la revue** : avant `ExitPlanMode`. Le plan est transmis **en clair et intégral**
  dans le prompt de l'agent — le fichier de plan n'existe qu'après `ExitPlanMode` et `Write` est
  bloqué en plan mode. Le brief, lui, n'est jamais recopié : l'agent le lit. Le contrat des
  sous-agents reçoit une **exception nommée** pour ce cas, plutôt que d'être enfreint en
  silence. (dit)
- **Retour** : rien n'est corrigé d'office. Le verdict est présenté **avec** le plan, dans le même
  `ExitPlanMode`. (dit)
- **Le rapport ne s'écrit dans aucun fichier** — contrairement à `implementation-auditor`. Un plan
  pas encore accepté peut changer plusieurs fois ; un historique de verdicts sur des versions
  mortes n'a pas de valeur. (dit)
- **Périmètre de `QUALITÉ`** : contrôle de contrat — atomicité, fichiers nommés, commande de
  vérification présente, ordre des dépendances. **Pas** de critique d'architecture : le plan sort
  d'`ExitPlanMode`, son fond est déjà validé. (dit)
- **Bloc de sortie** de `plan-reviewer`, sur le modèle des deux agents existants : (dit)

  ```
  VERDICT : CONFORME | RÉSERVES | NON CONFORME
  CRITÈRES : chaque critère du brief → étape(s) qui le sert, ou NON SERVI
  HORS-PÉRIMÈTRE : RESPECTÉ | entamé par étape N
  DÉRIVE : aucun | signal « … » déclenché par étape N
  INCERTITUDES : chacune → tranchée par étape N | toujours ouverte
  QUALITÉ : Q1, Q2, … constats numérotés
  ```

  Sans brief, les quatre lignes du milieu passent en `SANS OBJET`.
- **Outils de l'agent** : `Read, Grep, Glob, Bash` — aucun droit d'écriture. (dit)

## Incertitudes à lever en plan

- **Le plan mode autorise-t-il l'appel d'un sous-agent ?** Non vérifié. Si non, la revue avant
  présentation est impossible et il faut se rabattre sur une revue après `ExitPlanMode`, sur le
  fichier de plan persisté. **À tester en premier.**
- **Risque du brief orphelin** : `intent-brief` ne livrant plus ni plan ni confrontation, un
  utilisateur qui n'invoque pas le tracker (`disable-model-invocation: true`) repart avec un brief
  seul. L'étape de sortie d'`intent-brief` devient la sortie unique — reste à décider de sa
  formulation.
