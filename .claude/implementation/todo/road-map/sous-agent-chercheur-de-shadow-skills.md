+++
id = "sous-agent-chercheur-de-shadow-skills"
title = "Un sous-agent Haiku choisit les Shadow-skills d'un Chantier ou d'une discussion"
date = 2026-10-14
source = "relecture de la dette `cherche-par-sous-chaine`, discussion du 2026-10-14"
+++

## À faire

Un agent `model: haiku` reçoit l'intention d'un Chantier (Brief) ou le résumé d'une discussion,
lit `shadow-skill liste` et inspecte le contenu des Shadow-skills candidats pour affiner son choix ;
il rend des noms, chacun avec sa raison en une ligne, et ne charge rien : l'agent principal fait
`shadow-skill charge`. Le choix se juge sur le sens, pas sur des mots, et le contexte principal ne
reçoit que la réponse.

Décidé : lancé **systématiquement en début de Chantier, à l'élaboration du Plan**, à la place de la
recherche par `tags` et `cherche` du point 2 de la création ; ses noms vont au champ `skills` du
Suivi. Hors Chantier, il sert à la demande, à côté de `shadow-skill cherche`.

À trancher : biais vers le rappel (un skill de trop plutôt qu'un manqué), `omitClaudeMd` avec ou
sans `injectLexique`, les commandes `shadow-skill` que la consigne lui permet.

## Références

- `skills/implementation-tracker/references/creation.md`, point 2 : « Chercher les Shadow-skills du
  Chantier », que le sous-agent remplace ; point 7 : le champ `skills`
- `skills/implementation-tracker/references/contrat.md` : le champ `skills` du Suivi, lu par
  `shadow-skill depuis-suivi`
- `skills/shadow-skill/instructions.md` : la recherche avant une tâche, hors Chantier
- `agents/migrateur-de-liste.md`, `agents/plan-reviewer.md` : forme d'un agent de ce dépôt
- `skills/lexique/SKILL.md`, « Ce que reçoit un sous-agent » : `omitClaudeMd` et `injectLexique`
- Dette `cherche-par-sous-chaine` : la correction de `cherche`, entrée distincte
