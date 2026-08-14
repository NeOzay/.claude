# Patterns de sécurité — Tous langages

## Secrets et fichiers sensibles

**Fichiers à ne jamais committer :**
`.env`, `*.pem`, `*.key`, `*.p12`, `id_rsa`, `id_ed25519`, `secrets.json`, `credentials.json`, `service-account.json`

**Patterns dans le contenu du diff :**
```
AKIA[0-9A-Z]{16}                     → clé AWS
ghp_[a-zA-Z0-9]{36}                  → token GitHub
glpat-[a-zA-Z0-9\-]{20}             → token GitLab
sk_(live|test)_[a-zA-Z0-9]{24,}     → clé Stripe
eyJ[A-Za-z0-9\-_]+\.eyJ[...]        → JWT
(password|secret|api.?key)\s*[=:]\s*['"][^'"]{8,}['"]  → variable hardcodée
```

## Vulnérabilités universelles

| Risque | Patterns à détecter |
|--------|-------------------|
| Injection SQL | Concaténation de string dans une requête avec variable utilisateur |
| XSS | Rendu HTML non échappé avec données externes |
| Injection commande | `exec(`, `system(`, `shell=True` avec variable |
| SSL désactivé | `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true` |
| Exécution arbitraire | `eval(` avec variable dynamique |
| Path traversal | Chemin construit depuis un input utilisateur sans validation |

## Configurations sensibles modifiées

Signaler si ces fichiers apparaissent dans le diff :
`cors.*`, `csp.*`, `helmet.*`, `auth.*`, `permission.*`, `nginx.conf`, `apache.*`, `.github/workflows`

## Sévérités

| Problème | Verdict |
|----------|---------|
| Secret / credential dans le diff | 🔴 NO-GO |
| Fichier `.env` ou clé privée stagé | 🔴 NO-GO |
| Injection SQL / XSS évidente | 🔴 NO-GO |
| SSL désactivé | 🔴 NO-GO |
| CORS `*` ou config permissive | ⚠️ Avertissement |
| `console.log` de données sensibles | ⚠️ Avertissement |
| Header de sécurité supprimé | ⚠️ Avertissement |
