# Recettes Neovim pour emmylua_ls

Ce document contient des configurations concrètes et des patterns courants pour utiliser emmylua_ls dans Neovim.

## Table des matières

1. [Configuration de base](#configuration-de-base)
2. [Settings LSP vs .emmyrc.json](#settings-lsp-vs-emmyrcjson)
3. [Développement de plugins Neovim](#développement-de-plugins-neovim)
4. [Utilisation avec lazy.nvim et Mason](#utilisation-avec-lazynvim-et-mason)
5. [Désactivation sélective de capabilities](#désactivation-sélective-de-capabilities)
6. [Coexistence avec lua_ls (LuaLS)](#coexistence-avec-lua_ls-luals)
7. [Module mapping avec moduleMap](#module-mapping-avec-modulemap)
8. [Utilisation de $VIMRUNTIME et bibliothèques](#utilisation-de-vimruntime-et-bibliothèques)
9. [Intégration avec stylua](#intégration-avec-stylua)
10. [Debugging et dépannage](#debugging-et-dépannage)

---

## Configuration de base

### Neovim ≥ 0.11 (méthode native)

Fichier `lsp/emmylua_ls.lua` dans votre config :

```lua
---@type vim.lsp.Config
return {
  cmd = { "emmylua_ls" },
  filetypes = { "lua" },
  root_markers = { ".emmyrc.json", ".luarc.json", ".luacheckrc", ".git" },
  workspace_required = false,
}
```

Activation dans `init.lua` :

```lua
vim.lsp.enable("emmylua_ls")
```

### Neovim < 0.11 (via nvim-lspconfig)

```lua
require("lspconfig").emmylua_ls.setup({})
```

Note : nvim-lspconfig fournit déjà les valeurs par défaut pour `cmd`, `filetypes` et `root_markers`.

---

## Settings LSP vs .emmyrc.json

emmylua_ls accepte la configuration de deux façons, avec des nuances importantes :

### Via .emmyrc.json (recommandé)

Le fichier `.emmyrc.json` est la méthode privilégiée. Les clés sont directement au premier niveau :

```json
{
  "runtime": { "version": "LuaJIT" },
  "diagnostics": { "disable": ["unused"] },
  "workspace": { "library": ["$VIMRUNTIME"] }
}
```

### Via les settings LSP (init.lua)

Les settings LSP doivent être wrappés dans un objet `Lua` :

```lua
settings = {
  Lua = {
    runtime = { version = "LuaJIT" },
    diagnostics = { disable = { "unused" } },
    workspace = { library = { vim.env.VIMRUNTIME } },
  },
}
```

### Priorité

Quand les deux sont présents, le `.emmyrc.json` a la priorité sur les settings LSP.
Le `.emmyrc.json` est portable entre éditeurs (VSCode, Neovim, IntelliJ), les settings LSP sont spécifiques à Neovim.

### Quand utiliser quoi

- **`.emmyrc.json`** : Configuration du projet, partagée avec l'équipe (commit dans le repo).
- **Settings LSP** : Configuration globale de votre environnement Neovim, ou options spécifiques à Neovim (comme `$VIMRUNTIME`).

---

## Développement de plugins Neovim

### Configuration complète

Fichier `after/lsp/emmylua_ls.lua` :

```lua
---@type vim.lsp.Config
return {
  cmd = { "emmylua_ls" },
  filetypes = { "lua" },
  root_markers = { ".emmyrc.json", ".luarc.json", ".luacheckrc", ".git" },
  workspace_required = false,
  settings = {
    Lua = {
      runtime = {
        version = "LuaJIT",
        requirePattern = { "lua/?.lua", "lua/?/init.lua" },
      },
      workspace = {
        library = {
          vim.env.VIMRUNTIME,
        },
      },
      diagnostics = {
        globals = { "vim" },
      },
    },
  },
}
```

### Inclure les types des plugins installés

Pour la complétion sur les API des plugins (par ex. `require("telescope")`) :

```lua
workspace = {
  library = {
    vim.env.VIMRUNTIME,
    vim.fn.stdpath("data") .. "/lazy",  -- Si vous utilisez lazy.nvim
    -- vim.fn.stdpath("data") .. "/site/pack", -- Si vous utilisez packer
  },
},
```

### .emmyrc.json pour un plugin Neovim

```json
{
  "$schema": "https://raw.githubusercontent.com/EmmyLuaLs/emmylua-analyzer-rust/refs/heads/main/crates/emmylua_code_analysis/resources/schema.json",
  "runtime": {
    "version": "LuaJIT",
    "requirePattern": ["lua/?.lua", "lua/?/init.lua"]
  },
  "diagnostics": {
    "globals": ["vim", "describe", "it", "before_each", "after_each", "assert"]
  }
}
```

---

## Utilisation avec lazy.nvim et Mason

### Installation via Mason

```lua
-- lazy.nvim spec
{
  "williamboman/mason.nvim",
  opts = {
    ensure_installed = { "emmylua_ls" },
  },
}
```

Puis dans votre config LSP (sans nvim-lspconfig) :

```lua
-- S'assurer que le binaire Mason est dans le PATH
vim.env.PATH = vim.fn.stdpath("data") .. "/mason/bin:" .. vim.env.PATH

vim.lsp.enable("emmylua_ls")
```

### Avec nvim-lspconfig et Mason

```lua
{
  "neovim/nvim-lspconfig",
  dependencies = {
    "williamboman/mason.nvim",
    "williamboman/mason-lspconfig.nvim",
  },
  config = function()
    require("mason").setup()
    require("mason-lspconfig").setup({
      ensure_installed = { "emmylua_ls" },
    })
    require("lspconfig").emmylua_ls.setup({
      settings = {
        Lua = {
          runtime = { version = "LuaJIT" },
          workspace = { library = { vim.env.VIMRUNTIME } },
        },
      },
    })
  end,
}
```

---

## Désactivation sélective de capabilities

### Désactiver le formatage (utiliser stylua à la place)

```lua
---@type vim.lsp.Config
return {
  cmd = { "emmylua_ls" },
  filetypes = { "lua" },
  root_markers = { ".emmyrc.json", ".luarc.json", ".luacheckrc", ".git" },
  on_attach = function(client, bufnr)
    client.server_capabilities.documentFormattingProvider = false
    client.server_capabilities.documentRangeFormattingProvider = false
  end,
}
```

### Désactiver les semantic tokens

Si le highlighting sémantique entre en conflit avec votre thème ou treesitter :

```lua
on_attach = function(client, bufnr)
  client.server_capabilities.semanticTokensProvider = nil
end,
```

### Désactiver les inlay hints globalement

Dans les settings :

```lua
settings = {
  Lua = {
    hint = { enable = false },
  },
},
```

Ou les activer/désactiver par buffer via :

```lua
vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled())
```

---

## Coexistence avec lua_ls (LuaLS)

Il est déconseillé de faire tourner les deux simultanément sur les mêmes fichiers — les diagnostics se dédoubleraient. Voici des stratégies :

### Option 1 : Un seul LSP (recommandé)

Choisir emmylua_ls ou lua_ls et désactiver l'autre.

### Option 2 : Par projet via .emmyrc.json / .luarc.json

- Les projets avec `.emmyrc.json` déclenchent emmylua_ls.
- Les projets avec seulement `.luarc.json` peuvent être configurés pour lua_ls.
- Adapter les `root_markers` pour éviter les conflits.

### Option 3 : Désactiver l'un au lancement

```lua
-- Dans on_attach de emmylua_ls :
on_attach = function(client, bufnr)
  -- Arrêter lua_ls s'il est attaché au même buffer
  for _, c in ipairs(vim.lsp.get_clients({ bufnr = bufnr, name = "lua_ls" })) do
    c:stop()
  end
end,
```

---

## Module mapping avec moduleMap

La configuration `workspace.moduleMap` permet de remapper les noms de modules dans `require`. Utile quand l'arborescence de fichiers ne correspond pas aux noms de modules.

### Exemple : remapper `lib.*` vers `script.*`

```json
{
  "workspace": {
    "moduleMap": [
      {
        "pattern": "^lib(.*)$",
        "replace": "script$1"
      }
    ]
  }
}
```

Avec cette config, `require("lib.utils")` est résolu vers `script/utils.lua`.

### Exemple : préfixe de module personnalisé

```json
{
  "workspace": {
    "moduleMap": [
      {
        "pattern": "^myapp%.(.*)$",
        "replace": "src/$1"
      }
    ]
  }
}
```

---

## Utilisation de $VIMRUNTIME et bibliothèques

### Variables d'environnement supportées

emmylua_ls supporte `$VIMRUNTIME` dans les chemins de `workspace.library`. Cette variable est résolue vers le chemin du runtime Neovim.

### Via .emmyrc.json

```json
{
  "workspace": {
    "library": ["$VIMRUNTIME"]
  }
}
```

### Via settings Lua

```lua
workspace = {
  library = {
    vim.env.VIMRUNTIME,                          -- Runtime Neovim
    vim.fn.stdpath("data") .. "/lazy",           -- Plugins lazy.nvim
    "/chemin/vers/love2d/api",                   -- Bibliothèque externe
  },
},
```

### Bibliothèques avec filtrage

Dans `.emmyrc.json`, filtrer les fichiers d'une bibliothèque volumineuse :

```json
{
  "workspace": {
    "library": [
      {
        "path": "/chemin/vers/grosse-lib",
        "ignoreDir": ["tests", "benchmarks", "examples"],
        "ignoreGlobs": ["**/*.test.lua", "**/*.spec.lua"]
      }
    ]
  }
}
```

---

## Intégration avec stylua

### Via formateur externe dans .emmyrc.json

```json
{
  "format": {
    "externalTool": {
      "program": "stylua",
      "args": ["--stdin-filepath", "${INPUT}", "-"],
      "timeout": 5000
    },
    "externalToolRangeFormat": {
      "program": "stylua",
      "args": [
        "--stdin-filepath", "${INPUT}",
        "--range-start", "${RANGE_START}",
        "--range-end", "${RANGE_END}",
        "-"
      ],
      "timeout": 5000
    }
  }
}
```

### Via conform.nvim (alternative recommandée)

Plutôt que de passer par le LSP, utiliser conform.nvim pour le formatage :

```lua
{
  "stevearc/conform.nvim",
  opts = {
    formatters_by_ft = {
      lua = { "stylua" },
    },
  },
}
```

Et désactiver le formatage LSP dans la config emmylua_ls (voir section Désactivation sélective).

---

## Debugging et dépannage

### Vérifier que le LSP est actif

```vim
:checkhealth vim.lsp
```

Sous "Enabled Configurations", `emmylua_ls` doit apparaître avec ses paramètres.

### Vérifier les logs

Activer les logs verbose dans `init.lua` :

```lua
vim.lsp.set_log_level("DEBUG")
```

Puis consulter le fichier de log :

```vim
:lua vim.cmd('edit ' .. vim.lsp.get_log_path())
```

### Lister les clients LSP attachés

```vim
:lua print(vim.inspect(vim.lsp.get_clients()))
```

### Problèmes courants

**Le LSP ne démarre pas** :
- Vérifier que `emmylua_ls` est dans le PATH : `:!which emmylua_ls`
- Vérifier les root_markers : le fichier `.emmyrc.json` ou `.git` doit exister dans un répertoire parent.

**Diagnostics trop verbeux** :
- Ajouter les globals manquants dans `.emmyrc.json` : `"diagnostics": { "globals": ["vim"] }`
- Désactiver des diagnostics spécifiques : `"diagnostics": { "disable": ["unused", "undefined-global"] }`

**Performances lentes sur un gros workspace** :
- Utiliser `ignoreDir` et `ignoreGlobs` dans workspace pour exclure les fichiers non pertinents.
- Augmenter `diagnosticInterval` pour réduire la fréquence d'analyse.
- Limiter les bibliothèques chargées.

**Conflit avec treesitter pour le highlighting** :
- Désactiver les semantic tokens du LSP (voir section Désactivation sélective).
