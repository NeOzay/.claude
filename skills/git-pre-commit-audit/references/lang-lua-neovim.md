# Qualité — Lua / Neovim

## Patterns bloquants ❌

```lua
loadstring(variable)()         -- exécution arbitraire (équivalent eval)
dofile(user_input)             -- exécution de fichier externe non contrôlée
os.execute(variable)           -- injection commande
io.popen(variable)             -- injection commande
require(dynamic_variable)      -- chargement de module dynamique non contrôlé
```

## Avertissements ⚠️

```lua
print(...)                     -- debug oublié (utiliser vim.notify ou un logger)
vim.api.nvim_echo(...)         -- debug temporaire laissé en place
pcall sans gestion d'erreur    -- erreur silencieuse : pcall(fn) sans vérifier le retour
_G.ma_variable = ...           -- pollution du namespace global
```

## Points à vérifier — Lua général

- Les variables locales sont-elles déclarées avec `local` ? (éviter la pollution globale)
- Les `pcall` / `xpcall` vérifient-ils le booléen de retour ?
- Les modules retournent-ils une table plutôt que d'écrire dans `_G` ?
- Les chaînes de méthodes longues ont-elles des `nil`-checks intermédiaires ?
- Les boucles sur tables utilisent-elles `ipairs` (liste) ou `pairs` (dict) correctement ?

## Points à vérifier — Config Neovim

### Structure et organisation
- Les fichiers sont-ils dans le bon répertoire (`lua/`, `plugin/`, `after/`) ?
- Les autocommandes utilisent-elles `augroup` + `autocmd!` pour éviter les doublons au rechargement ?
- Les keymaps précisent-ils `noremap = true` et `silent = true` si approprié ?

```lua
-- ✅ Autocommande safe (pas de doublon au rechargement)
local group = vim.api.nvim_create_augroup("MonPlugin", { clear = true })
vim.api.nvim_create_autocmd("BufWritePre", {
  group = group,
  callback = function() ... end,
})

-- ❌ Doublon à chaque rechargement de config
vim.cmd("autocmd BufWritePre * lua ma_fonction()")
```

### API Neovim
- L'API `vim.api.*` est-elle préférée à `vim.cmd()` pour les appels programmatiques ?
- Les options utilisent-elles `vim.opt` / `vim.o` plutôt que `vim.cmd("set ...")` ?
- Les appels `vim.fn.*` coûteux dans des boucles sont-ils mis en cache ?

```lua
-- ✅ API moderne
vim.opt.number = true
vim.keymap.set("n", "<leader>f", ":Telescope find_files<CR>", { silent = true })

-- ⚠️ Style ancien, encore fonctionnel mais moins idiomatique
vim.cmd("set number")
vim.cmd("nnoremap <leader>f :Telescope find_files<CR>")
```

### Plugins (lazy.nvim / packer)
- Les dépendances entre plugins sont-elles déclarées (`dependencies = { ... }`) ?
- Les plugins lourds utilisent-ils le chargement différé (`lazy = true`, `event`, `ft`, `cmd`) ?
- Les configurations de plugin sont-elles dans `config = function() ... end` plutôt qu'en dehors ?

```lua
-- ✅ Chargement différé correct
{
  "nvim-telescope/telescope.nvim",
  cmd = "Telescope",
  dependencies = { "nvim-lua/plenary.nvim" },
  config = function()
    require("telescope").setup({ ... })
  end,
}
```

### Performance
- Les fonctions appelées sur chaque frappe (`TextChangedI`, `CursorMoved`) sont-elles légères ?
- Les `require()` dans des callbacks fréquents sont-ils mis en cache dans une variable locale ?

```lua
-- ✅ require mis en cache
local ts_utils = require("nvim-treesitter.ts_utils")
vim.api.nvim_create_autocmd("CursorMoved", {
  callback = function() ts_utils.get_node_at_cursor() end
})

-- ⚠️ require répété à chaque déplacement du curseur
vim.api.nvim_create_autocmd("CursorMoved", {
  callback = function() require("nvim-treesitter.ts_utils").get_node_at_cursor() end
})
```

## Taille et complexité

- Fonction > 40 lignes → ⚠️ à découper
- Fichier de config principal (`init.lua`) > 100 lignes → ⚠️ à séparer en modules
- Module > 250 lignes → ℹ️ envisager une séparation
