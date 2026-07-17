---
name: git-smart-commit
description: >
  Analyse automatiquement les changements Git en cours (fichiers modifiés, ajoutés, supprimés)
  et génère un message de commit descriptif, structuré et conventionnel. Utilise cette skill
  dès que l'utilisateur mentionne "commit", "committer les changements", "sauvegarder mes modifications",
  "git commit", "enregistrer le travail", "pusher", "versionner", ou demande de créer un commit
  pour les fichiers en cours. Déclencher aussi si l'utilisateur dit "commit tout", "commit ce que j'ai fait",
  "crée un commit avec mes changements", ou toute variante. Cette skill observe le diff complet,
  catégorise les changements, et produit un message de commit suivant la convention Conventional Commits.
  Gère aussi l'aplatissement d'une branche d'implémentation (ex. clôture d'un chantier via
  implementation-tracker) : tous les commits de la branche sont réunis en un seul commit sur la
  branche principale, avec confirmation explicite avant toute réécriture.
model: Sonnet
---

# Git Smart Commit

Skill pour analyser les changements Git en cours et générer automatiquement un message de commit
clair, structuré et conforme aux conventions.

---

## Workflow complet

### Étape 1 — Vérifier que le répertoire est un dépôt Git

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
```

Si la réponse est `NON_GIT`, arrêter et informer l'utilisateur.

### Étape 2 — Observer tous les changements en cours

Lancer ces commandes **dans l'ordre** pour avoir une vue complète :

```bash
# 1. Statut global
git status --short

# 2. Diff des fichiers déjà stagés (index vs HEAD)
git diff --staged --stat
git diff --staged

# 3. Diff des fichiers modifiés non stagés (working tree vs index)
git diff --stat
git diff

# 4. Fichiers non suivis
git ls-files --others --exclude-standard
```

> **Important** : analyser les quatre sorties pour ne rater aucun changement.

### Étape 3 — Analyser et catégoriser les changements

Pour chaque fichier modifié, identifier :

| Indicateur `git status` | Signification |
|------------------------|---------------|
| `M`  | Modifié       |
| `A`  | Ajouté        |
| `D`  | Supprimé      |
| `R`  | Renommé       |
| `C`  | Copié         |
| `??` | Non suivi (nouveau) |

Puis regrouper par **domaine fonctionnel** en lisant le diff :
- Quelle fonctionnalité est impactée ?
- S'agit-il d'un bug fix, d'une nouvelle feature, d'un refactor, de docs, de tests, de config ?
- Y a-t-il des breaking changes ?

Consulter [`references/conventional-commits.md`](references/conventional-commits.md) pour les types disponibles.

### Étape 4 — Construire le message de commit

Suivre strictement le format **Conventional Commits** :

```
<type>(<scope>): <description courte en impératif>

<corps optionnel — expliquer le POURQUOI, pas le QUOI>

<footer optionnel — BREAKING CHANGE, closes #issue>
```

**Règles de rédaction** :
- La ligne de titre : **50 caractères max**, impératif, minuscules après le type
- Le corps : **72 caractères par ligne max**, séparé du titre par une ligne vide
- Pas de point final sur le titre
- En français ou en anglais selon la langue du projet (détecter via les commits précédents)

Pour détecter la langue des commits précédents :
```bash
git log --oneline -5 2>/dev/null
```

### Étape 5 — Proposer le message à l'utilisateur

Afficher le message de commit proposé clairement :

```
📝 Message de commit suggéré :
─────────────────────────────────────────
feat(auth): add OAuth2 Google login support

Implement Google OAuth2 flow using the googleapis package.
Users can now sign in with their Google account on the
login page. Sessions are persisted via JWT tokens.

Closes #42
─────────────────────────────────────────
```

Puis afficher un **résumé des changements détectés** :
```
📂 Changements inclus :
  • 3 fichiers modifiés, 2 ajoutés, 0 supprimés
  • Principaux : src/auth/google.ts, routes/login.ts
```

### Étape 6 — Demander confirmation avant de committer

**Ne jamais committer sans confirmation explicite de l'utilisateur.**

Proposer trois options :
1. ✅ **Valider** — committer avec ce message
2. ✏️ **Modifier** — l'utilisateur ajuste le message
3. 🔍 **Voir le diff complet** — afficher tous les changements avant de décider

### Étape 7 — Exécuter le commit

Selon ce que l'utilisateur veut stager :

```bash
# Option A : stager tous les changements (tracked + untracked)
git add -A
git commit -m "<titre>" -m "<corps>"

# Option B : stager seulement les fichiers trackés
git add -u
git commit -m "<titre>" -m "<corps>"

# Option C : stager des fichiers spécifiques
git add <fichiers>
git commit -m "<titre>" -m "<corps>"
```

Confirmer le succès en affichant le résultat de `git log --oneline -1`.

---

## Cas particuliers

### Aucun changement détecté
```bash
git status --short
# sortie vide → rien à committer
```
Informer l'utilisateur : "Aucun changement détecté dans le dépôt."

### Dépôt sans commits (initial commit)
```bash
git log 2>&1 | grep "fatal: your current branch"
```
Dans ce cas, utiliser `feat: initial commit` comme type par défaut.

### Changements très volumineux (>20 fichiers)
Si plus de 20 fichiers sont modifiés, suggérer de découper en plusieurs commits
thématiques plutôt qu'un seul commit monolithique.

### Conflits de merge en cours
```bash
git status | grep -E "^(UU|AA|DD)"
```
Si des conflits existent, avertir l'utilisateur et ne pas committer.

### Aplatissement d'une branche d'implémentation (ex. clôture d'implémentation)

Cas déclenché explicitement (pas par simple mention de "commit"), typiquement par
`implementation-tracker` en fin de chantier. Réunit tous les commits de la branche `<slug>` en un seul
commit sur la branche principale, puis supprime la branche — procédure dédiée : voir
[`references/squash.md`](references/squash.md).

---

## Référence rapide des types Conventional Commits

| Type       | Usage                                              |
|------------|----------------------------------------------------|
| `feat`     | Nouvelle fonctionnalité                            |
| `fix`      | Correction de bug                                  |
| `docs`     | Documentation uniquement                           |
| `style`    | Formatage, espaces, virgules (pas de logique)      |
| `refactor` | Refactoring sans nouvelle feature ni bug fix       |
| `perf`     | Amélioration de performance                        |
| `test`     | Ajout ou correction de tests                       |
| `build`    | Système de build, dépendances (npm, pip…)          |
| `ci`       | Configuration CI/CD                                |
| `chore`    | Tâches diverses, mise à jour de dépendances        |
| `revert`   | Annulation d'un commit précédent                   |

> Pour la référence complète avec exemples, voir [`references/conventional-commits.md`](references/conventional-commits.md)

---

## Bonnes pratiques rappel

- **Un commit = une idée** : si les changements couvrent plusieurs sujets distincts, proposer de les séparer
- **Message au présent impératif** : "add feature" et non "added feature" ou "adding feature"  
- **Le titre explique le QUOI**, le corps explique le **POURQUOI**
- Toujours vérifier qu'aucun fichier sensible (`.env`, secrets, clés API) n'est inclus dans le commit
