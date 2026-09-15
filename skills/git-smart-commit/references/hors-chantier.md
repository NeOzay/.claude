# Type 1 — commit ordinaire

Analyser les changements en cours, proposer un message, committer après accord.

## 1. Vérifier le dépôt

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
```

`NON_GIT` → arrêter et le dire.

## 2. Observer tous les changements

Lancer ces commandes **dans l'ordre**, et analyser les quatre sorties : chacune montre ce que les
autres ne montrent pas.

```bash
git status --short                          # statut global
git diff --staged --stat && git diff --staged   # déjà indexé
git diff --stat && git diff                 # modifié, non indexé
git ls-files --others --exclude-standard    # non suivi
```

Cas qui arrêtent ou changent la suite :

- **Aucun changement** (`git status --short` vide) → dire « Aucun changement détecté » et
  s'arrêter.
- **Conflit de merge en cours** (entrées `UU`, `AA` ou `DD` dans `git status --short`) → avertir
  et ne pas committer.
- **Plus de 20 fichiers modifiés** → proposer de découper en commits thématiques.
- **Dépôt sans commit** (`git rev-parse --verify HEAD` échoue) → `feat: initial commit` par défaut.

## 3. Catégoriser

| `git status` | Signification |
|---|---|
| `M` | Modifié |
| `A` | Ajouté |
| `D` | Supprimé |
| `R` | Renommé |
| `C` | Copié |
| `??` | Non suivi |

Puis regrouper par **domaine fonctionnel** en lisant le diff : quelle fonctionnalité est touchée ?
Correctif, fonctionnalité, refactor, docs, tests, config ? Y a-t-il un breaking change ?

Des sujets distincts → proposer plusieurs commits, un par sujet.

## 4. Rédiger le message

Format, types et règles de rédaction :
[`conventional-commits.md`](conventional-commits.md).

## 5. Proposer, puis committer après accord

Présenter le message, les chemins à stager et un résumé des changements :

```
Message de commit proposé :
─────────────────────────────────────────
feat(auth): add OAuth2 Google login support

Users can now sign in with their Google account.
Sessions are persisted via JWT tokens.

Closes #42
─────────────────────────────────────────
Chemins stagés : src/auth/google.ts, routes/login.ts
3 fichiers modifiés, 2 ajoutés, 0 supprimé
```

Ce qui compte comme accord et ce qu'on propose à l'utilisateur :
[`confirmation.md`](confirmation.md).

Sur accord, stager les chemins présentés et committer — forme de la commande :
[`staging.md`](staging.md). Confirmer par `git log --oneline -1`.
