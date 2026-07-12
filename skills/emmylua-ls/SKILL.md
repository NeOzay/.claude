---
name: emmylua-ls
description: >
    Référence du LSP emmylua_ls (Rust) pour Lua dans Neovim : configuration .emmyrc.json, annotations EmmyLua/LuaCATS (@class, @field, @param, @type, @enum, @generic, @namespace...), système de types, diagnostics, emmylua_check, emmylua_doc_cli. Déclencher dès que l'utilisateur mentionne emmylua, emmylua_ls, .emmyrc.json, annotations Lua, ou le type system EmmyLua. 
---

# EmmyLua Language Server (emmylua_ls)

EmmyLua Analyzer Rust (`emmylua_ls`) est un LSP pour Lua écrit en Rust. Il supporte Lua 5.1–5.5 et LuaJIT, les annotations EmmyLua/LuaCATS, 50+ diagnostics, l'inférence de types avec génériques avancés, et toutes les fonctionnalités LSP standard (complétion, hover, go-to-definition, rename, code actions, inlay hints, semantic tokens, code lens, call hierarchy, formatage via EmmyLuaCodeStyle ou outil externe).

Configuration projet via `.emmyrc.json` (ou `.luarc.json`) à la racine du workspace. Le `.emmyrc.json` a priorité sur les settings LSP Neovim. Les settings LSP sont wrappés sous `Lua` (ex: `settings = { Lua = { runtime = { ... } } }`), le `.emmyrc.json` utilise les clés au premier niveau.

Schéma JSON pour autocomplétion de la config : `"$schema": "https://raw.githubusercontent.com/EmmyLuaLs/emmylua-analyzer-rust/refs/heads/main/crates/emmylua_code_analysis/resources/schema.json"`

## Annotations

Commentaires `---` (trois tirets) enrichissant l'analyse statique. Liste complète :

`@class`, `@field`, `@param`, `@return`, `@type`, `@alias`, `@enum`, `@generic`, `@overload`, `@async`, `@deprecated`, `@private`, `@protected`, `@package`, `@diagnostic`, `@cast`, `@operator`, `@nodiscard`, `@version`, `@see`, `@namespace`, `@using`, `@mapping`, `@source`, `@vararg`, `@meta`

Annotations **exclusives à emmylua_ls** (absentes de lua_ls/LuaLS) : `@namespace`, `@using`, `@mapping`, `@source`, `@enum (key)`, et le type spécial `namespace<T>`.

> Détails et exemples : `references/annotations.md`

## Système de types

Types primitifs : `nil`, `boolean`, `number`, `integer`, `string`, `table`, `function`, `thread`, `userdata`
Types spéciaux : `any`, `unknown`, `void`, `never`, `self`
Composites : unions (`A|B`), tuples (`[A, B]`), arrays (`T[]`), dicts (`table<K,V>`), littéraux (`"hello"`, `42`), fonctions (`fun(a: T): R`), nullable (`T?`), variadic (`...T`)
Génériques avancés : `keyof`, `extends`, `infer`, `and`, `or`, `namespace<T>`

> Détails : `references/type-system.md`

## Diagnostics

50+ diagnostics configurables. Principaux : `syntax-error`, `type-not-found`, `param-type-mismatch`, `return-type-mismatch`, `assign-type-mismatch`, `undefined-global`, `undefined-field`, `unused`, `deprecated`, `missing-return`, `missing-parameter`, `missing-fields`, `redundant-parameter`, `unreachable-code`, `need-check-nil`, `inject-field`, `call-non-callable`, `access-invisible`.

Contrôle inline : `---@diagnostic disable-next-line: code` / `disable:` / `enable:` / `disable-line:`

> Liste exhaustive des codes et sévérités : `references/configuration.md`

## Outils CLI

`emmylua_check` (linter) : `emmylua_check .`, `emmylua_check ./src --verbose --format json`, `emmylua_check . -c config.emmyrc.json`
`emmylua_doc_cli` (doc generator) : `emmylua_doc_cli ./src -o ./docs --site-name "Nom"`, formats `markdown` ou `json`

## Références

| Fichier | Contenu |
|---|---|
| `references/configuration.md` | Toutes les options `.emmyrc.json` avec défauts et exemples (workspace, runtime, diagnostics, completion, hints, strict, format, doc, etc.) |
| `references/annotations.md` | 25+ annotations détaillées avec syntaxe et exemples (`@class`, `@field`, `@enum (key)`, `@namespace`, `@operator`, etc.) |
| `references/type-system.md` | Types primitifs/composites, génériques avancés (keyof, extends, infer), `namespace<T>`, narrowing, sous-typage, opérateurs |
| `references/neovim-recipes.md` | Installation (Cargo, Mason), configuration Neovim (≥0.11 et lspconfig), settings vs .emmyrc.json, lazy.nvim + Mason, $VIMRUNTIME, désactivation de capabilities, intégration stylua, debugging |
| `references/differences-luals.md` | Comparaison avec lua_ls (LuaLS) : annotations exclusives, config, plugins (non supportés), diagnostics, migration |
