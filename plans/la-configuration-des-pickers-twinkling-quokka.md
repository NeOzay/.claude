# Regroupement de la config des pickers Snacks

## Contexte

La config picker de Snacks est actuellement fragmentée :
- `lua/plugins/snacks/picker.lua` — config générique (layouts, win, actions globales, tous les keymaps `Snacks.picker.*`).
- `lua/pickers/tabpages.lua` et `lua/tabpage.lua` — nouveaux fichiers non trackés (picker custom tabpages).
- `lua/pickers/harpoon_snacks.lua` — picker harpoon custom, référencé directement depuis `lua/plugins/harpoon.lua` (pas via un module central).
- `lua/pickers/init.lua` — module d'agrégation **cassé** : `require("pickers.harpoon")` pointe vers un fichier inexistant, et rien dans le repo ne fait `require("pickers")` de toute façon. Code mort.
- `lua/pickers/jumplist.lua` — picker **Telescope** (pas Snacks) pour la jumplist, doublon obsolète de `Snacks.picker.jumps()` déjà mappé sur `<leader>fj`. Telescope est désactivé selon `CLAUDE.md`. Code mort.

Objectif : regrouper tout ce qui définit un picker Snacks autonome (config générique + pickers custom réutilisables) sous un seul module cohérent `lua/plugins/snacks/picker/`, supprimer le code mort, et mettre à jour la doc en conséquence. `picker.sources.explorer` et `picker.sources.notifications` restent dans `explorer.lua`/`notifier.lua` (config intrinsèque à ces features, pas des pickers autonomes). `lua/lsp/ai-rename.lua` reste en l'état (feature LSP, hors périmètre).

## Structure cible

```
lua/plugins/snacks/picker/
  init.lua              -- ex picker.lua : opts génériques (prompt, actions, layout, win, layouts) + agrégation des keys
  sources/
    tabpages.lua         -- ex lua/pickers/tabpages.lua
    harpoon.lua           -- ex lua/pickers/harpoon_snacks.lua
```

`require("plugins.snacks.picker")` continue de fonctionner tel quel (résolution de `init.lua` dans un dossier) — aucun changement requis dans `lua/plugins/snacks/init.lua`.

`lua/pickers/` est supprimé entièrement (4 fichiers : `init.lua`, `jumplist.lua`, `harpoon_snacks.lua`, `tabpages.lua`).

`lua/tabpage.lua` reste à la racine `lua/` (module générique réutilisé par lualine, pas spécifique aux pickers).

## Étapes

1. **Créer `lua/plugins/snacks/picker/sources/tabpages.lua`** avec le contenu actuel de `lua/pickers/tabpages.lua` (inchangé, le `require("tabpage")` reste valide).

2. **Créer `lua/plugins/snacks/picker/sources/harpoon.lua`** avec le contenu actuel de `lua/pickers/harpoon_snacks.lua` (inchangé).

3. **Créer `lua/plugins/snacks/picker/init.lua`** = contenu actuel de `lua/plugins/snacks/picker.lua`, avec les deux `require` mis à jour :
   - `require("pickers.tabpages")` → `require("plugins.snacks.picker.sources.tabpages")` (keymap `<leader>tt`)
   - Ajout d'une entrée keymap pour harpoon si on veut la centraliser (voir étape 4) — sinon le require reste dans `harpoon.lua`.

4. **Mettre à jour `lua/plugins/harpoon.lua`** : `require("pickers.harpoon_snacks")` → `require("plugins.snacks.picker.sources.harpoon")`.

5. **Supprimer `lua/plugins/snacks/picker.lua`** (remplacé par le dossier) et tout `lua/pickers/` (les 4 fichiers).

6. **Mettre à jour la doc** :
   - `docs/plugins/snacks-picker-custom.md` : chemins `lua/pickers/harpoon_snacks.lua` → `lua/plugins/snacks/picker/sources/harpoon.lua` (ligne 10 et titre section ligne 298).
   - `docs/plugins/harpoon.md` : chemin picker ligne 9 → `lua/plugins/snacks/picker/sources/harpoon.lua`.
   - `docs/plugins/snacks.md` :
     - Mettre à jour le chemin `lua/pickers/tabpages.lua` → `lua/plugins/snacks/picker/sources/tabpages.lua` dans l'entrée changelog du 2026-07-08.
     - Mettre à jour la section `Files` pour refléter la nouvelle structure `lua/plugins/snacks/picker/` (init.lua + sources/).
     - Ajouter une entrée changelog documentant ce regroupement/refactor et la suppression du code mort (`lua/pickers/init.lua`, `lua/pickers/jumplist.lua`).
     - Combler le trou identifié pendant l'exploration : la section Explorer ne documente pas encore le finder "fichiers > 300 lignes" (`<leader>el`, commit `aef6a02`) — l'ajouter au passage.

## Vérification

- Ouvrir Neovim, vérifier absence d'erreur au chargement (`:messages`).
- Tester `<leader>tt` (picker tabpages), `<leader>tr` (rename tab), `<C-e>` (picker harpoon) — doivent fonctionner comme avant.
- `:Pickers` doit toujours lister les pickers.
- `grep -rn "pickers\." lua/ docs/` ne doit plus renvoyer aucune référence à l'ancien chemin `lua/pickers/`.
