+++
gabarit = "brief"
slug = "lexique-des-sous-agents"
titre = "Donner les lexiques et leurs règles aux sous-agents"
statut = "validé"
"créé" = 2026-10-05
+++

## Intention

**Symptôme** : un sous-agent peut employer un terme hors de sa définition sans le savoir ; c'est
« plus une question d'uniformisation, destinée au Subagent utilisé dans les Chantiers ».
**But** : tout sous-agent personnalisé qui reçoit `CLAUDE.md` reçoit aussi le lexique local
(« donner le lexique local à tous les Subagents personnalisés qui utilisent le claude.md », dit) ;
et un sous-agent qui porte `omitClaudeMd: true`, quand les lexiques lui sont pertinents, peut
recevoir les lexiques et leurs instructions (« créez un mécanisme pour injecter les lexiques et
les instructions quand omitClaudeMd = true peut être pertinent », dit).

## Critères de réussite

- Un sous-agent de test, lancé dans un dépôt existant qui a un lexique local
  (`.claude/LEXIQUE.md`), montre qu'il a reçu ce lexique (dit).
- Un agent de test à `omitClaudeMd: true`, lancé dans le même dépôt, montre qu'il reste isolé :
  aucun lexique ne lui parvient (« pour tester l'isolation », dit).
- Un agent de test à `omitClaudeMd: true` dont le champ dédié demande l'injection, lancé dans le
  même dépôt, montre qu'il a reçu les lexiques global et local et leurs instructions (dit).

## Hors-périmètre

- Écrire dans les fichiers des sous-agents : ni le hook ni ses scripts n'y touchent, et les règles
  n'y sont pas recopiées ; la demande d'injection y est posée à la main par l'auteur de l'agent
  (« injectez les lexiques sans modifier les sous-agents », puis arbitrage, dit).
- Les agents intégrés, sans fichier : `Explore` et `Plan` (« jamais utilisés », dit),
  general-purpose (arbitrage, dit).

## Signaux de dérive

- Le diff modifie la sous-commande `lexique session` ou le hook `SessionStart` (dit).
- Le diff ajoute un script hors de la skill `lexique` (dit).
- Le diff retouche un agent existant de `agents/` (dit).

## Contraintes connues de l'utilisateur

- **Existant** : un sous-agent dont l'agent ne porte pas `omitClaudeMd` reçoit `CLAUDE.md` et ses
  imports, donc le lexique global et ses règles ; vérifié le 2026-10-05 par un agent de test, qui
  a cité la définition de Semence et la première règle (dépôt: Claude Code 2.1.289).
- **Existant** : `Explore`, `Plan` et `claude-code-guide` portent `omitClaudeMd` ; le lexique local
  n'entre que par le hook `SessionStart`, que les sous-agents ne reçoivent pas
  (dépôt: `settings.json`, binaire 2.1.289).
- **Existant** : le hook `SubagentStart` existe, son matcher porte sur `agent_type`, et son
  `additionalContext` est montré au sous-agent ; un champ non officiel du frontmatter d'un agent
  est accepté sans avertissement (dépôt: binaire 2.1.289, test du 2026-10-05).
- **Décision** : l'injection se règle sur le fichier de l'agent : `omitClaudeMd` absent → le
  lexique local est injecté ; `omitClaudeMd: true` → rien n'est injecté, sauf si un champ dédié
  du frontmatter le demande : alors les lexiques global et local et leurs instructions (dit,
  arbitrage pour le champ) ; les instructions sont `skills/lexique/instructions.md` (restitution
  non corrigée, dit).
- **Historique** : l'utilisateur ne se sert pas des sous-agents par défaut (dit).

## Incertitudes à lever en plan

- Forme exacte de la sortie attendue par `SubagentStart` : la description du binaire dit
  « JSON additionalContext shown to subagent », sans dire si un stdout brut suffit comme pour
  `SessionStart`.
- Nom et valeur du champ dédié qui demande l'injection.
- Chemin du dépôt existant qui servira au test : l'utilisateur le choisit (dit), il n'est pas
  encore nommé.
