---
slug: fichier-seme
titre: Créer un fichier préstructuré depuis une semence, hors de toute liste
statut: validé
execution: direct
créé: 2026-09-15
---

## Intention

**Symptôme** : — non abordé
**But** : créer des fichiers préstructurés à remplir à partir d'une semence, comme la création d'un
élément de list-dir mais sans rattachement à une liste (dit). Première utilisation : les fichiers de
suivi d'implementation-tracker (dit).

## Critères de réussite

- la suite de tests de list-dir passe ; seuls ses imports sont modifiables sans autorisation (dit)
- une vraie semence de suivi du tracker est livrée (dit)

## Hors-périmètre

- pas de modification des skills existants ; création d'un nouveau skill (dit)
- list-dir : comportement et documentation identiques, seul le code interne bouge (dit)
- implementation-tracker n'est pas branché sur « gabarit » : chantier ultérieur (dit)

## Signaux de dérive

- un test de list-dir qu'on voudrait modifier au-delà des imports (dit)
- `gabarit` qui importe quoi que ce soit de `listdir` (dit)
- `gabarit` qui se met à gérer une notion de répertoire ou de liste (dit)

## Contraintes connues de l'utilisateur

- **Architecture** : nouvelle bibliothèque, nom à définir, « gabarit » pressenti (dit)
- **Architecture** : `listdir` est dans le chantier et dépend directement de « gabarit » — pas de 3e bibliothèque (dit)
- **Répartition** : `reseed` (et la copie de semence) reste propre à list-dir : un gabarit n'a pas de copie de sa semence (dit)
- **Modèle** : une list-dir est une liste de gabarits (dit)
- **Fonction** : « gabarit » a une commande qui vérifie l'intégrité d'un fichier (dit)
- **Identité** : `gabarit new` estampille le fichier créé d'un champ `gabarit = "<nom>"`, de type `slug` ; la vérification d'intégrité s'en sert pour retrouver la semence (dit)
- **Format** : front matter TOML `+++` seul, celui de list-dir ; adapter les lecteurs YAML du tracker (`commit_chantier.py`) relève du chantier de branchement (dit)
- **Identité** : l'estampille porte le nom seul, pas de version de semence (dit)
- **Emplacement** : la semence de suivi vit dans le nouveau skill, pas sous implementation-tracker (dit)
- **Résolution** : mêmes quatre racines que list-dir, sous un répertoire `gabarit/<nom>/` distinct de `list-dir/<nom>/` (dit)
- **Réutiliser** : `list-dir new` sait déjà préremplir champs et sections (`text`/`command`) depuis un
  contrat (dépôt: skills/list-dir/references/format.md)
- **Réutiliser** : les définitions se résolvent par nom dans quatre racines (dépôt:
  skills/list-dir/references/definitions.md)

## Incertitudes à lever en plan

- variables `LISTDIR_*` du préremplissage : comportement list-dir à préserver — injection d'environnement par l'appelant ?
- le suivi porte des sections sans marqueur (`## Étapes` issue du plan, journal) — que doit poser la semence ?
