# Conventional Commits

Source : [conventionalcommits.org](https://www.conventionalcommits.org/fr/v1.0.0/)

## Format

```
<type>[(<scope>)][!]: <description>

[corps]

[footer(s)]
```

## Types

| Type | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité (MINOR en SemVer) |
| `fix` | Correction de bug (PATCH) |
| `docs` | Documentation uniquement |
| `style` | Formatage, sans changement de logique |
| `refactor` | Restructuration sans fonctionnalité ni correctif |
| `perf` | Amélioration de performance |
| `test` | Ajout ou correction de tests |
| `build` | Système de build, dépendances |
| `ci` | Configuration CI/CD |
| `chore` | Tâches diverses |
| `revert` | Annulation d'un commit précédent |

## Règles de rédaction

- **Titre** : 50 caractères au plus, impératif, minuscule après le type, sans point final.
- **Corps** : séparé du titre par une ligne vide, 72 caractères par ligne au plus. Il explique le
  **pourquoi** — le diff dit déjà le quoi.
- **Langue** : celle des commits précédents du dépôt (`git log --oneline -5`).
- **Scope** : cohérent avec les commits précédents.

## Breaking changes

Deux notations équivalentes — le footer quand la migration demande une explication :

```
feat(api)!: remove deprecated /v1 endpoints
```

```
feat(api): remove deprecated /v1 endpoints

BREAKING CHANGE: All /v1/* routes have been removed.
Migrate to /v2/* equivalents. See MIGRATION.md for details.
```

## Footers d'issues

`Closes #42` · `Fixes #89` · `Refs #100, #101` · `Closes PROJ-1234`

## Contrôles avant de proposer

- Le type correspond à la nature réelle des changements.
- Un seul sujet par commit.
- **Aucun `.env`, secret ou clé** dans le diff.
