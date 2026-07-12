# Plan : lsp_typehierarchy pour trouble.nvim

## Contexte

Trouble.nvim n'implémente pas les méthodes LSP 3.17 de type hierarchy (`textDocument/prepareTypeHierarchy`, `typeHierarchy/supertypes`, `typeHierarchy/subtypes`). Il faut un source custom.

## Mécanisme de découverte

`trouble/sources/init.lua` → `M.load()` scanne **tous** les fichiers `lua/trouble/sources/*.lua` dans le runtime path via `nvim_get_runtime_file`. Le répertoire de config (`~/.config/nvim`) est dans le rtp → un fichier déposé là est auto-découvert sans aucun enregistrement manuel.

## Fichiers à créer/modifier

### 1. Créer `lua/trouble/sources/lsp_typehierarchy.lua`

Source custom auto-découverte. Pattern calqué sur `call_hierarchy` dans `lsp.lua`.

```lua
local LspSource = require("trouble.sources.lsp")
local Promise   = require("trouble.promise")
local Item      = require("trouble.item")

local M = {}

M.config = {
  modes = {
    lsp_supertypes = {
      mode   = "lsp_base",
      title  = "{hl:Title}Supertypes{hl} {count}",
      desc   = "supertypes",
      source = "lsp_typehierarchy.supertypes",
      format = "{kind_icon} {text:ts} {pos} {hl:Title}{item.client:Title}{hl}",
    },
    lsp_subtypes = {
      mode   = "lsp_base",
      title  = "{hl:Title}Subtypes{hl} {count}",
      desc   = "subtypes",
      source = "lsp_typehierarchy.subtypes",
      format = "{kind_icon} {text:ts} {pos} {hl:Title}{item.client:Title}{hl}",
    },
    lsp_type_hierarchy = {
      desc     = "LSP Type Hierarchy (supertypes + subtypes)",
      sections = { "lsp_supertypes", "lsp_subtypes" },
    },
  },
}

---@param cb trouble.Source.Callback
---@param direction "supertypes"|"subtypes"
local function type_hierarchy(cb, direction)
  local win = vim.api.nvim_get_current_win()
  LspSource.request("textDocument/prepareTypeHierarchy", function(client)
    return vim.lsp.util.make_position_params(win, client.offset_encoding)
  end)
    :next(function(results)
      ---@type trouble.Promise[]
      local requests = {}
      for _, res in ipairs(results or {}) do
        for _, thi in ipairs(res.result or {}) do
          requests[#requests + 1] = LspSource.request(
            "typeHierarchy/" .. direction,
            { item = thi },
            { client = res.client }
          )
        end
      end
      return Promise.all(requests)
    end)
    :next(function(responses)
      ---@type trouble.Item[]
      local items = {}
      for _, results in ipairs(responses) do
        for _, res in ipairs(results) do
          vim.list_extend(items, LspSource.results_to_items(res.client, res.result or {}))
        end
      end
      Item.add_text(items, { mode = "after" })
      cb(items)
    end)
end

M.get = {}

---@param cb trouble.Source.Callback
function M.get.supertypes(cb) type_hierarchy(cb, "supertypes") end

---@param cb trouble.Source.Callback
function M.get.subtypes(cb)   type_hierarchy(cb, "subtypes")   end

return M
```

**Annotations EmmyLua** conformes à `lua-style.md` + préfixe `Ozay.` non nécessaire ici (types locaux).

### 2. Modifier `lua/lsp/mappings.lua`

Ajouter dans `M.attach`, après les mappings existants, en utilisant le helper `wrapTrouble` déjà présent :

```lua
-- Type hierarchy (LSP 3.17)
if client:supports_method("textDocument/prepareTypeHierarchy") then
  map("n", "grh", wrapTrouble("lsp_type_hierarchy"), opts("Type hierarchy"))
  map("n", "grs", wrapTrouble("lsp_supertypes"),     opts("Supertypes"))
  map("n", "grS", wrapTrouble("lsp_subtypes"),       opts("Subtypes"))
end
```

Condition `supports_method` : évite d'enregistrer les mappings pour les LSP qui ne supportent pas la méthode.

## Fonctions réutilisées

- `LspSource.request()` — `trouble.nvim/lua/trouble/sources/lsp.lua:123`
- `LspSource.results_to_items()` — `trouble.nvim/lua/trouble/sources/lsp.lua:412`
- `Promise.all()` — `trouble.nvim/lua/trouble/promise.lua`
- `Item.add_text()` — `trouble.nvim/lua/trouble/item.lua`

## Vérification

1. Ouvrir un fichier Lua/Python sur une classe avec un LSP qui supporte `typeHierarchy`
2. `:Trouble lsp_type_hierarchy toggle` → doit afficher supertypes + subtypes
3. `:Trouble lsp_supertypes toggle` → supertypes seuls
4. Si le LSP ne supporte pas la méthode → résultat vide (pas d'erreur)
