---
paths:
  - "**/*.lua"
---

# Convention de style et typage Lua (EmmyLua)

## Typage

- Toute variable `local` doit avoir un type inférable par emmylua_ls. Annoter avec `@type` quand l'inférence échoue : tables vides (`{}`), tables construites progressivement, retours de fonctions non annotées, résultats de `require` sans annotations.
- Les tables construites par ajouts successifs de champs doivent être précédées d'un `@class` + `@field`.
- Préférer `unknown` à `any` quand un type est inconnu mais qu'on veut forcer la vérification avant usage.

## Fonctions

- Annoter tous les paramètres avec `@param` et tous les retours avec `@return`. Omettre `@return` uniquement pour les procédures (pas de valeur de retour).
- Marquer les paramètres optionnels avec `?` après le nom (`@param timeout? number`).
- Ordre des annotations : documentation `---`, puis `@generic`, `@param` (ordre de la signature), `@return`, `@nodiscard`/`@async`/`@deprecated`, `@overload`.
- Préférer `@overload` quand le type de retour change selon les paramètres. Préférer les unions (`string|number`) quand seul le type d'entrée varie.

## Classes et structures

- Nommage : `PascalCase` pour les classes et enums, `camelCase` ou `snake_case` pour les champs et méthodes (cohérent dans tout le projet).
- Utiliser `@class` + `@field` pour les structures partagées (paramètres, retours, héritage). Utiliser `@type {k: v}` pour les structures locales ponctuelles.
- Marquer les champs et méthodes internes avec `@private` ou `@protected`. Convention : les noms préfixés par `_` doivent porter une annotation de visibilité.
- Utiliser `?` sur les `@field` qui acceptent `nil`.

## Modules

- Tout module exporte via `return`. Le conteneur doit être typé (`---@class MonModule` / `local M = {}` / `return M`).

## Enums et constantes

- `@enum` pour les valeurs existant au runtime, `@alias` avec littéraux pour les types qui n'existent qu'à l'analyse.
- `@nodiscard` sur les fonctions pures dont le retour ne doit pas être ignoré.
- `@deprecated` avec message de remplacement sur les fonctions obsolètes.

## Tables dynamiques

- Déclarer l'indexeur typé (`@field [string] ValueType`) pour les tables à clés dynamiques.

## Callbacks

- Typer les callbacks avec `fun(...)`. Créer un `@alias` pour les signatures de callback réutilisées.

## Diagnostics

- Déclarer les globaux connus dans `.emmyrc.json` (`diagnostics.globals`) plutôt que désactiver `undefined-global`.
- `---@diagnostic disable-next-line` uniquement pour des suppressions ponctuelles justifiées. Ne jamais désactiver un diagnostic globalement dans le code sans raison.
