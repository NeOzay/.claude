---
name: git-pre-commit-audit
description: >
  Réalise un audit complet des changements Git avant un commit : sécurité, qualité du code,
  régressions potentielles, cohérence. Produit un rapport GO / NO-GO structuré.
  Déclencher dès que l'utilisateur dit "auditer mes changements", "vérifier avant de committer",
  "audit pre-commit", "review mes changements", "valider mon code", "qu'est-ce que j'ai changé",
  "check avant commit", ou toute formulation similaire. Se déclenche aussi automatiquement
  en amont de git-smart-commit si aucun audit n'a encore été réalisé.
---

# Git Pre-Commit Audit

Audit des changements Git en cours. Produit un rapport **GO / NO-GO** avant tout commit.
S'exécute *avant* `git-smart-commit`.

---

## Étape 1 — Collecter les données

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
git status --short
git diff --staged --stat && git diff --staged
git diff --stat && git diff
git ls-files --others --exclude-standard
git branch --show-current && git log --oneline -5
```

Stopper immédiatement si `NON_GIT` ou si des conflits (`UU`, `AA`, `DD`) sont présents.

---

## Étape 2 — Identifier les langages et charger les annexes

```bash
git diff --name-only HEAD | sed 's/.*\.//' | sort -u
```

**Charger uniquement les annexes correspondantes** aux extensions détectées :

| Extensions | Annexe à lire |
|-----------|--------------|
| `.js` `.ts` `.jsx` `.tsx` | `references/lang-js-ts.md` |
| `.py` | `references/lang-python.md` |
| `.php` | `references/lang-php.md` |
| `.go` | `references/lang-go.md` |
| `.java` `.kt` | `references/lang-java-kotlin.md` |
| `.sql` ou fichiers `migration` | `references/lang-sql.md` |
| `Dockerfile` `.yml` `.yaml` `workflows/` | `references/lang-infra.md` |
| `.lua` | `references/lang-lua-neovim.md` |

> Charger `references/security-patterns.md` **dans tous les cas** (sécurité universelle).

---

## Étape 3 — Audit sécurité (PRIORITÉ ABSOLUE)

Scanner le diff avec les patterns de `references/security-patterns.md`.

```bash
# Fichiers sensibles stagés
git diff --staged --name-only | grep -iE "(\.env|\.pem|\.key|id_rsa|secrets\.)"

# Secrets dans le contenu
git diff HEAD | grep -iE "(password|api.?key|secret|token|AKIA[0-9A-Z]{16})" --color=never
```

🔴 **NO-GO immédiat** si : secret détecté, fichier `.env` stagé, vulnérabilité critique.

---

## Étape 4 — Audit qualité du code

```bash
# Code de débogage
git diff HEAD | grep -nE "(console\.log|debugger;|binding\.pry|dd\(|var_dump\(|TODO|FIXME)"

# Tests présents ?
git diff --name-only HEAD | grep -iE "(\.test\.|\.spec\.|_test\.)"

# Fichiers à haut risque
git diff --name-only HEAD | grep -iE "(migration|schema|auth|payment|config|package\.json|requirements\.txt|Dockerfile)"

# Taille du diff
git diff HEAD --shortstat
```

Appliquer les critères spécifiques au langage depuis l'annexe chargée à l'étape 2.

---

## Étape 5 — Produire le rapport

```
╔══════════════════════════════════════════════════════════╗
║  AUDIT PRÉ-COMMIT  |  branch  |  Nx modifiés  |  +L/-L  ║
╚══════════════════════════════════════════════════════════╝

🔐 SÉCURITÉ       ✅/⚠️/❌  [résultats]
🐛 QUALITÉ        ✅/⚠️/❌  [résultats]
🧪 TESTS          ✅/⚠️/❌  [résultats]
💥 IMPACT         ✅/⚠️/❌  [résultats]
📦 COHÉRENCE      ✅/⚠️/❌  [résultats]

─────────────────────────────────────────────────────────
VERDICT : ✅ GO  |  ⚠️ GO AVEC RÉSERVES  |  🔴 NO-GO
─────────────────────────────────────────────────────────
```

**Règles de verdict :**
- 🔴 **NO-GO** : au moins un ❌ (secret, vulnérabilité critique, conflit, `debugger;` en prod)
- ⚠️ **GO avec réserves** : des ⚠️ présents, l'utilisateur confirme
- ✅ **GO** : aucun problème bloquant, ≤ 2 avertissements mineurs

**Sévérités :** ❌ Bloquant · ⚠️ Avertissement · ℹ️ Info · ✅ OK

---

## Étape 6 — Proposition de suite

**Si NO-GO :** lister les actions correctives précises, puis relancer l'audit.

**Si GO / GO avec réserves :**
```
→ 1. Procéder au commit  (enchaîner avec git-smart-commit)
→ 2. Corriger les avertissements d'abord
→ 3. Détailler un point spécifique
```

---

## Annexes disponibles

| Fichier | Contenu |
|---------|---------|
| `references/security-patterns.md` | Patterns secrets, vulnérabilités (tous langages) |
| `references/lang-js-ts.md` | Qualité JS / TS / React |
| `references/lang-python.md` | Qualité Python |
| `references/lang-php.md` | Qualité PHP |
| `references/lang-go.md` | Qualité Go |
| `references/lang-java-kotlin.md` | Qualité Java / Kotlin |
| `references/lang-sql.md` | Migrations et requêtes SQL |
| `references/lang-infra.md` | Docker, CI/CD, YAML |
| `references/lang-lua-neovim.md` | Qualité Lua / Neovim |
