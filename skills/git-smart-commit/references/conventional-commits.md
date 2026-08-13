# Référence Conventional Commits

Source : [conventionalcommits.org](https://www.conventionalcommits.org/fr/v1.0.0/)

## Format

```
<type>[(<scope>)][!]: <description>

[corps]

[footer(s)]
```

Types : `feat` (MINOR en SemVer), `fix` (PATCH), `docs`, `style`, `refactor`, `perf`, `test`,
`build`, `ci`, `chore`, `revert`.

## Breaking changes

Deux notations, équivalentes — le footer quand la migration demande une explication :

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

## Contrôles avant de committer

- Le type correspond à la nature réelle des changements.
- Le scope est cohérent avec les commits précédents du dépôt.
- Titre à l'impératif, ≤ 50 caractères.
- Le corps explique le **pourquoi**, pas le quoi — le diff dit déjà le quoi.
- **Aucun `.env`, secret ou clé** dans le diff.
- Un seul sujet par commit.
