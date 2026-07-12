# Différences entre emmylua_ls et lua_ls (LuaLS)

Ce document décrit les différences notables entre le serveur EmmyLua Analyzer Rust (`emmylua_ls`) et le Lua Language Server de Sumneko/LuaLS (`lua_ls`). Les deux sont des LSP pour Lua mais ils divergent sur plusieurs points.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Configuration](#configuration)
3. [Annotations partagées](#annotations-partagées)
4. [Annotations exclusives à emmylua_ls](#annotations-exclusives-à-emmylua_ls)
5. [Annotations exclusives à lua_ls](#annotations-exclusives-à-lua_ls)
6. [Système de plugins](#système-de-plugins)
7. [Performances](#performances)
8. [Diagnostics](#diagnostics)
9. [Fonctionnalités LSP](#fonctionnalités-lsp)
10. [Migration de lua_ls vers emmylua_ls](#migration-de-lua_ls-vers-emmylua_ls)

---

## Vue d'ensemble

| Aspect | emmylua_ls | lua_ls (LuaLS) |
|---|---|---|
| Langage d'implémentation | Rust | Lua |
| Fichier de config projet | `.emmyrc.json` | `.luarc.json` / `.luarc.jsonc` |
| Versions Lua supportées | 5.1–5.5, LuaJIT | 5.1–5.4, LuaJIT |
| Système de plugins | Non supporté | Oui (plugins Lua) |
| Système d'addons | Non | Oui (addon manager) |
| Format d'annotations | EmmyLua + LuaCATS | LuaCATS (basé sur EmmyLua) |
| Licence | MIT | MIT |

---

## Configuration

### Fichier de configuration

emmylua_ls utilise `.emmyrc.json` comme fichier principal, mais reconnaît aussi `.luarc.json` pour faciliter la migration.

Les structures de configuration diffèrent significativement :

**emmylua_ls** (`.emmyrc.json`) — clés au premier niveau :

```json
{
  "runtime": { "version": "LuaJIT" },
  "workspace": { "library": ["$VIMRUNTIME"] },
  "diagnostics": { "disable": ["unused"] }
}
```

**lua_ls** (`.luarc.json`) — souvent sous un objet `Lua` dans les settings :

```json
{
  "runtime": { "version": "LuaJIT" },
  "workspace": { "library": ["/path/to/lib"] },
  "diagnostics": { "disable": ["unused"] }
}
```

### Settings LSP Neovim

emmylua_ls attend les settings sous la clé `Lua` :

```lua
-- emmylua_ls
settings = { Lua = { runtime = { version = "LuaJIT" } } }

-- lua_ls
settings = { Lua = { runtime = { version = "LuaJIT" } } }
```

Les deux utilisent la même structure wrappée sous `Lua` dans les settings LSP Neovim.

### Options exclusives à emmylua_ls

- `workspace.moduleMap` : Remapping de noms de modules via regex.
- `workspace.packageDirs` : Répertoires de packages.
- `strict.typeCall`, `strict.arrayIndex`, `strict.metaOverrideFileDefine` : Options de mode strict.
- `doc.syntax` : Choix entre `md`, `rst`, `myst` pour la syntaxe de documentation.
- `doc.privateName` : Patterns de noms traités comme privés (ex: `m_*`).
- `completion.postfix` : Symbole de déclenchement postfix (`@`, `.`, `:`).
- `references.shortStringSearch`, `references.fuzzySearch` : Contrôle de la recherche de références.
- `hint.metaCallHint`, `hint.enumParamHint` : Inlay hints spécifiques.

### Options exclusives à lua_ls

- `workspace.checkThirdParty` : Vérification automatique des bibliothèques tierces.
- `workspace.userThirdParty` : Chemins vers les stubs tiers.
- `runtime.plugin` : Chemin vers le plugin Lua.
- `runtime.pluginArgs` : Arguments du plugin.
- `completion.workspaceWord` : Complétion par mots du workspace.
- `diagnostics.libraryFiles` : Diagnostic dans les fichiers de bibliothèque.
- `format.enable` : Formateur intégré activable (EmmyLuaCodeStyle est intégré dans emmylua_ls par défaut).

---

## Annotations partagées

Les annotations suivantes sont supportées par les deux serveurs avec un comportement compatible :

`@class`, `@field`, `@param`, `@return`, `@type`, `@alias`, `@generic`, `@overload`, `@async`, `@deprecated`, `@private`, `@protected`, `@package`, `@diagnostic`, `@cast`, `@operator`, `@nodiscard`, `@version`, `@see`, `@enum`, `@vararg`, `@meta`

---

## Annotations exclusives à emmylua_ls

### @namespace

Déclare un namespace pour organiser les classes et alias. Inexistant dans lua_ls.

```lua
---file1.lua
---@namespace UI

---@class Button
---@field text string
local Button = {}

---file2.lua
---@type UI.Button  -- Référence via le namespace
local btn = createButton()

-- Ou importer le namespace pour accéder directement :
---@namespace UI
---@type Button  -- Résolu comme UI.Button
local btn2 = createButton()
```

### @using

Importe un namespace, permettant d'utiliser ses types sans le préfixe.

```lua
---@using UI

---@param btn Button  -- Résolu comme UI.Button
function handleClick(btn) end
```

### @mapping

Annotation de mapping de type avancée, spécifique à emmylua_ls.

### @source

Spécifie la source d'une définition externe.

```lua
---@source "path/to/implementation.lua"#42:10
function externalFn() end
```

### namespace\<T : string\> (type spécial)

Type générique spécial qui référence un namespace. Utile pour modéliser des bindings C#/Java :

```lua
CS = {
  ---@type namespace<"UnityEngine">
  UnityEngine = {},
  ---@type namespace<"System">
  System = {},
}

-- Ensuite CS.UnityEngine.GameObject est reconnu comme un type
```

### @enum avec attribut key

L'annotation `@enum` supporte un attribut `key` pour contrôler la complétion :

```lua
---@enum (key) AAA
local AAA = {
  CS = {
    A = { B = { C = 1 } }
  }
}

-- La complétion proposera CS.A.B.C au lieu de AAA.CS.A.B.C
```

---

## Annotations exclusives à lua_ls

### @as

Cast inline dans une expression (lua_ls). emmylua_ls utilise `--[[@as Type]]` à la place (syntaxe commentaire de bloc).

```lua
-- lua_ls :
local x = getValue() --[[@as string]]

-- emmylua_ls : même syntaxe, mais ce n'est pas une annotation @ formelle
```

### @module

Spécifie le module d'un fichier (lua_ls uniquement).

### Plugins Lua

lua_ls supporte un système de plugins écrits en Lua qui peuvent modifier le comportement du serveur (complétion, diagnostics, etc.). emmylua_ls ne supporte **pas** et ne prévoit **pas** de supporter les plugins, pour des raisons de performances, de taille binaire et de sécurité.

---

## Système de plugins

C'est la différence architecturale la plus importante :

**lua_ls** : Supporte des plugins Lua qui peuvent transformer l'analyse, ajouter de la complétion personnalisée, ou modifier les diagnostics. Le système d'addons permet d'installer des bibliothèques de types tierces.

**emmylua_ls** : Aucun support de plugins et aucun projet d'en ajouter. Le mainteneur a explicitement rejeté cette possibilité pour les raisons suivantes :
- Impact négatif sur les performances
- Augmentation de la taille du binaire (runtime de scripting)
- Problèmes de lifetime Rust avec le partage de données vers un runtime de scripting
- Volume d'API bindings à maintenir
- Préoccupations de sécurité liées aux scripts exécutables

---

## Performances

emmylua_ls est généralement plus rapide que lua_ls grâce à l'implémentation Rust. Les avantages les plus notables :

- Analyse initiale plus rapide sur les gros projets
- Meilleure utilisation mémoire
- Compilation incrémentale plus efficace
- Temps de réponse aux requêtes LSP plus faible

En contrepartie, lua_ls peut être plus flexible grâce à son système de plugins.

---

## Diagnostics

Les deux serveurs offrent des diagnostics similaires mais avec des noms différents dans certains cas. Voici les correspondances principales :

| Concept | emmylua_ls | lua_ls |
|---|---|---|
| Variable globale non définie | `undefined-global` | `undefined-global` |
| Champ non défini | `undefined-field` | `undefined-field` |
| Variable non utilisée | `unused` | `unused-local` |
| Paramètre manquant | `missing-parameter` | `missing-parameter` |
| Retour manquant | `missing-return` | `missing-return` |
| Type de param incorrect | `param-type-mismatch` | `param-type-mismatch` |
| Injection de champ | `inject-field` | `inject-field` |
| Nil non vérifié | `need-check-nil` | `need-check-nil` |
| Valeur non-callable | `call-non-callable` | *(pas d'équivalent direct)* |
| Attribut de diagnostic | `attribute-*` | *(pas d'équivalent)* |
| Global hors module | `global-in-non-module` | *(pas d'équivalent direct)* |

La syntaxe de contrôle inline est identique :

```lua
---@diagnostic disable-next-line: undefined-global
```

---

## Fonctionnalités LSP

| Fonctionnalité | emmylua_ls | lua_ls |
|---|---|---|
| Auto-complétion | Oui | Oui |
| Go to definition | Oui | Oui |
| Find references | Oui (+ fuzzy search) | Oui |
| Rename | Oui | Oui |
| Hover | Oui | Oui |
| Signature help | Oui | Oui |
| Code actions | Oui | Oui |
| Diagnostics | Oui (50+) | Oui (50+) |
| Formatting | Via EmmyLuaCodeStyle ou externe | Via intégré ou externe |
| Semantic tokens | Oui | Oui |
| Inlay hints | Oui | Oui |
| Code lens | Oui | Oui |
| Call hierarchy | Oui | Oui |
| Document color | Oui | Non |
| Document links | Oui | Non |
| Workspace symbols | Oui | Oui |

---

## Migration de lua_ls vers emmylua_ls

### Étapes

1. **Installer emmylua_ls** : `cargo install emmylua_ls` ou via Mason.

2. **Renommer/adapter la config** : Si vous avez un `.luarc.json`, emmylua_ls le reconnaît. Sinon, créer un `.emmyrc.json` basé sur votre configuration lua_ls.

3. **Adapter les settings Neovim** : La structure `settings.Lua.*` est compatible. Les options spécifiques à lua_ls (comme `checkThirdParty`) seront ignorées.

4. **Vérifier les annotations** : Les annotations de base sont compatibles. Si vous utilisez `@module` ou des fonctionnalités de plugins lua_ls, une adaptation sera nécessaire.

5. **Remplacer les addons** : Si vous utilisiez des addons lua_ls pour des bibliothèques tierces, convertissez-les en entrées `workspace.library` dans la configuration emmylua_ls.

6. **Désactiver lua_ls** : S'assurer qu'un seul LSP est actif pour éviter les diagnostics dupliqués.

### Correspondance des options principales

| lua_ls | emmylua_ls |
|---|---|
| `runtime.version` | `runtime.version` (mêmes valeurs) |
| `runtime.path` | `runtime.requirePattern` |
| `workspace.library` | `workspace.library` |
| `workspace.checkThirdParty` | *(pas d'équivalent, ignorer)* |
| `diagnostics.globals` | `diagnostics.globals` |
| `diagnostics.disable` | `diagnostics.disable` |
| `format.enable` | Formatage toujours disponible, configurer via `format.*` |
| `completion.callSnippet` | `completion.callSnippet` |
| `hint.enable` | `hint.enable` |
