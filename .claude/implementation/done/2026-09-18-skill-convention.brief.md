---
slug: skill-convention
titre: Une skill qui consigne mes conventions, extraites de mes skills
statut: validé
execution: direct
créé: 2026-09-17
---

## Intention

**Symptôme** : — non abordé
**But** : « créer ma propre skill-convention avec mes pratiques » (dit), en extrayant les
conventions « à partir de mes skills » (dit), et y ajouter la road-map
`commandes-locales-au-projet` (dit).
Deux volets (dit) : la prose des skills, et les conventions de code — Python typé strict, doc
compacte au format Google. La skill inclut `commandes-locales-au-projet` pour indiquer comment une
skill peut mettre localement des commandes à disposition d'un agent (dit) : l'entrée de road-map
est livrée par ce chantier (road-map: commandes-locales-au-projet).

## Critères de réussite

Tous retenus (dit) :

- `scripts/check_pipeline.py` passe toujours
- chaque convention cite au moins une skill où elle est pratiquée
- une entrée de dette par skill en écart, conforme à `list-dir validate`
- l'entrée `commandes-locales-au-projet` sort de la road-map à la clôture

## Hors-périmètre

- les skills existantes ne sont pas corrigées : la skill décrit les conventions, et les écarts
  des skills à corriger sont consignés dans une dette (dit)

## Signaux de dérive

- la nouvelle skill recopie des règles au lieu d'y renvoyer (dit)
- une skill existante est éditée (dit)

## Contraintes connues de l'utilisateur

- **Réutiliser** : une règle n'est définie qu'à un seul endroit, les autres y renvoient
  (dépôt: e9f6a81)
- **Réutiliser** : `scripts/check_pipeline.py` vérifie déjà mécaniquement cette unicité et les
  renvois (dépôt: scripts/check_pipeline.py)
- **Réutiliser** : `OUTILLAGE.md` porte déjà les règles d'outillage du dépôt, et
  `rules/lua-style.md` une convention de code à portée par chemins (dépôt)
- **Nom** : la skill s'appelle `skill-convention`, dans `skills/skill-convention/` (dit)
- **Existant** : la skill renvoie à `OUTILLAGE.md` et `rules/lua-style.md` sans les déplacer ;
  ces fichiers restent inchangés (dit)
- **Portée** : des commandes globales ne peuvent être déclarées que dans `~/.claude/skills` (dit)

## Incertitudes à lever en plan

- la convention de code passe par `rules/` (dit — « roles/ » était `rules/`) ; reste à placer
  la frontière entre ce qui va dans `rules/` et ce qui reste dans la skill
- couverture des sous-agents par `CLAUDE_ENV_FILE` et cohabitation avec les hooks
  `SessionStart` et RTK — points ouverts de l'entrée de road-map, non vérifiés
