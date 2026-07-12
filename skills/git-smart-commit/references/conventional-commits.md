# Référence Conventional Commits

Source : [conventionalcommits.org](https://www.conventionalcommits.org/fr/v1.0.0/)

---

## Format complet

```
<type>[(<scope>)][!]: <description>

[corps]

[footer(s)]
```

Le `!` après le type/scope indique un **breaking change**.

---

## Types détaillés avec exemples

### `feat` — Nouvelle fonctionnalité
Correspond à un **MINOR** en SemVer.

```
feat(user): add profile picture upload

Users can now upload a JPEG or PNG profile picture (max 5MB).
Images are resized to 200x200 and stored in S3.

Closes #128
```

```
feat!: redesign authentication API

BREAKING CHANGE: The /auth/login endpoint now returns a JWT
instead of a session cookie. All clients must update their
auth handling logic.
```

---

### `fix` — Correction de bug

```
fix(cart): prevent duplicate items on rapid clicks

Debounce the add-to-cart button at 300ms to avoid race
conditions when users click quickly.

Fixes #89
```

---

### `docs` — Documentation

```
docs(api): update rate limiting section in README
```

---

### `style` — Formatage pur (aucun changement logique)

```
style: apply prettier formatting across src/
```

---

### `refactor` — Restructuration sans changement de comportement

```
refactor(db): extract query builder into separate module
```

---

### `perf` — Amélioration de performances

```
perf(search): add index on products.name column
```

---

### `test` — Tests uniquement

```
test(auth): add unit tests for token expiration edge cases
```

---

### `build` — Build system et dépendances

```
build(deps): upgrade react from 18.2 to 18.3
```

---

### `ci` — Intégration et déploiement continus

```
ci: add automated deployment to staging on PR merge
```

---

### `chore` — Tâches de maintenance diverses

```
chore: update .gitignore for macOS DS_Store files
```

---

### `revert` — Annulation d'un commit

```
revert: feat(user): add profile picture upload

This reverts commit a3f8b2c1d.
```

---

## Breaking Changes

**Option 1 — via `!`** :
```
feat(api)!: remove deprecated /v1 endpoints
```

**Option 2 — via footer** :
```
feat(api): remove deprecated /v1 endpoints

BREAKING CHANGE: All /v1/* routes have been removed.
Migrate to /v2/* equivalents. See MIGRATION.md for details.
```

---

## Référencer des issues

```
Closes #42
Fixes #89
Refs #100, #101
Closes PROJ-1234
```

---

## Checklist avant de committer

- [ ] Le type correspond bien à la nature des changements
- [ ] Le scope est pertinent et cohérent avec les commits précédents
- [ ] Le titre est en impératif et fait ≤50 caractères
- [ ] Le corps explique le POURQUOI (si nécessaire)
- [ ] Aucun fichier `.env` ou secret n'est inclus
- [ ] Un seul sujet par commit (pas de "fix bug + add feature")
