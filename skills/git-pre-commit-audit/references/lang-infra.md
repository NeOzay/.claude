# Qualité — Infrastructure (Docker, CI/CD, YAML)

## Patterns bloquants ❌

```dockerfile
# Secret dans le build
ARG API_KEY=sk-prod-xxxxx
ENV DATABASE_URL=postgres://user:password@host/db

# Exécution en root
# (absence de USER instruction)
```

```yaml
# GitHub Actions — secret hardcodé
env:
  TOKEN: ghp_xxxxxxxxxxxxx

# Action tierce non pinnée (supply chain)
- uses: actions/checkout@v3   # préférer @sha256:abc123...
```

## Avertissements ⚠️

```dockerfile
FROM node:latest          # tag flottant, build non reproductible
COPY . .                  # avant COPY package.json (cache invalidé à chaque changement)
RUN npm install && ...    # layer trop chargé
```

```yaml
# Permissions trop larges
permissions:
  contents: write
  packages: write
  # Devrait être le minimum nécessaire
```

## Points à vérifier — Dockerfile

- L'image de base est-elle taguée avec une version précise (pas `latest`) ?
- `COPY package*.json ./` est-il avant `COPY . .` (optimisation du cache) ?
- Un `USER` non-root est-il défini ?
- Les secrets sont-ils injectés via des ARG sans valeur par défaut ?
- Le `.dockerignore` exclut-il `node_modules`, `.env`, `.git` ?

## Points à vérifier — GitHub Actions / CI

- Les actions tierces sont-elles pinnées à un hash de commit (`@sha256:...`) ?
- Les `permissions` sont-elles au minimum requis (`contents: read` par défaut) ?
- Les secrets sont-ils référencés via `${{ secrets.NAME }}` et non hardcodés ?
- Les workflows déclenchés sur PR extérieures utilisent-ils `pull_request_target` avec précaution ?
- Les jobs qui publient en prod ont-ils une protection (`environment: production`) ?

## Points à vérifier — YAML config général

- Les valeurs sensibles sont-elles référencées depuis l'environnement ?
- Les ancres YAML (`&anchor`) sont-elles claires et non dupliquées excessivement ?
- La syntaxe YAML est-elle valide (indentation, types) ?
