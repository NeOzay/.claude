# Plan : mise en évidence dans les fenêtres hover

## Contexte

Le plugin met en évidence les sections de docstrings Python dans les buffers `filetype=python`. L'utilisateur veut que le même rendu fonctionne dans les fenêtres hover LSP (fenêtres flottantes qui affichent le docstring comme texte brut ou markdown).

Les fenêtres hover ont `buftype=nofile`, souvent `filetype=markdown`, et leur contenu est déjà du texte pur (les balises markdown `**...**` sont retirées par `stylize_markdown`). Le treesitter Python est inutilisable ici — on applique directement les regex existantes sur toutes les lignes.

## Approche

Deux ajouts dans `lua/docstring-highlight/init.lua` :

### 1. Fonction `refresh_hover(bufnr)`

Après la fonction `refresh()` (ligne ~360), avant les timers :

```lua
local function refresh_hover(bufnr)
    vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)
    local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
    local in_fenced = false
    local current_section = nil
    ---@type DocstringLineCtx
    local ctx = {
        section = nil,
        known_params = nil,      -- pas de filtrage sur signature
        param_annotations = nil,
        has_var_keyword = false,
        is_function = false,
    }
    for i, line in ipairs(lines) do
        if line:match("^%s*```") then
            in_fenced = not in_fenced
        end
        if not in_fenced then
            local sec = detect_section_name(line)
            if sec then current_section = sec end
            ctx.section = current_section
            highlight_line(bufnr, i - 1, line, ctx)
        end
    end
end
```

- Pas de treesitter, pas de debounce (la fenêtre hover ne se modifie pas)
- Skip les blocs fencés ` ``` ` (signature Python en début de hover)
- `known_params = nil` → `highlight_line` n'effectue aucun filtrage sur les noms de params

### 2. Autocmd `BufWinEnter` dans `setup()`

Après l'autocmd `ColorScheme` (ligne ~440) :

```lua
vim.api.nvim_create_autocmd("BufWinEnter", {
    group = augroup,
    callback = function(ev)
        local bufnr = ev.buf
        if vim.bo[bufnr].buftype ~= "nofile" then return end
        local win = vim.fn.bufwinid(bufnr)
        if win == -1 then return end
        local wincfg = vim.api.nvim_win_get_config(win)
        if wincfg.relative == "" then return end
        refresh_hover(bufnr)
    end,
})
```

Filtre : `buftype=nofile` + fenêtre flottante (`relative ~= ""`). Couvre les hover LSP sans toucher telescope, nvim-cmp, etc. (qui ont leurs propres filetypes ou buftype différents).

## Fichier modifié

`lua/docstring-highlight/init.lua` uniquement — deux blocs ajoutés.

## Vérification

```bash
nvim src/example.py
# Placer le curseur sur un appel de fonction documentée
# K (ou :lua vim.lsp.buf.hover())
# → Les sections Args:, Returns:, Raises: doivent être colorées
# → Les noms de paramètres et types doivent être colorés
# → Le bloc de signature (```python ... ```) ne doit pas être coloré
```

Vérification via extmarks si besoin :
```lua
:lua local ns = vim.api.nvim_get_namespaces()["docstring_highlight"]; local wins = vim.api.nvim_list_wins(); for _, w in ipairs(wins) do local cfg = vim.api.nvim_win_get_config(w); if cfg.relative ~= "" then local b = vim.api.nvim_win_get_buf(w); local marks = vim.api.nvim_buf_get_extmarks(b, ns, 0, -1, {}); print("hover buf " .. b .. " marks: " .. #marks) end end
```
