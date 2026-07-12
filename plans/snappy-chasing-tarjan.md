# Plan : couverture de tests parser + renderer markdown

## Contexte

L'audit de couverture a révélé que le parser (`lua/markview/parser.lua`, 303 lignes) et le renderer markdown (`lua/markview/renderers/markdown.lua`, 2904 lignes) sont très partiellement couverts. Les fonctions testées sont les plus simples (atx_heading, code_block, hr, block_quote, list_item, inline code span). Tout le reste — fonctions utilitaires du parser, setext_heading, indented_code_block, métadonnées YAML, link_ref_definition, checkbox, clear — est sans test.

## Ce qu'on ne couvrira pas (trop complexe / faible ROI)

- `parser.should_ignore` / `should_ignore_yaml` : nécessitent un objet TSTree réel difficile à construire sans le nœud TS complet
- `markdown.__block_quote` / `__list_item` / `__section` : fonctions de post-rendu qui s'appuient sur `markview.wrap`, logique de wrapping très dépendante de la fenêtre
- `markdown.render` / `post_render` : déjà testés indirectement via tous les autres tests (H.render() les appelle)
- `parser.should_ignore_yaml` : même raison que should_ignore

## Organisation des nouveaux fichiers

### Fichier 1 : `tests/test_parser_utils.lua` (nouveau)

Cible : fonctions pures du parser testables sans tree-sitter.

| Test group | Cas |
|---|---|
| `deep_extend` | table vide + table remplie → table remplie ; clés communes → valeur tbl_2 gagne ; tables imbriquées fusionnées récursivement |
| `create_ignore_range` | retourne table avec `row_start`/`row_end` corrects ; plusieurs items triés ; table vide → résultat vide |
| `parse_links` | buffer avec `[label]: url` → entrée dans content.link_ref ; buffer sans liens → table vide |

Setup : `H.setup_buf()` pour parse_links, appels directs `parser.deep_extend()`/`parser.create_ignore_range()` pour les pures.

### Fichier 2 : `tests/test_renderer_blocks.lua` (nouveau)

Cible : renderer fonctions non couvertes, niveau bloc.

| Test group | Cas |
|---|---|
| `setext_heading` | `===` underline → au moins 1 extmark sur row_start ; `---` underline → extmark sur sa ligne ; marker underline est concealed ou remplacé |
| `indented_code_block` | 4 espaces → extmark sur la ligne de code ; `line_hl_group` présent |
| `metadata_minus` | bloc `---\n...\n---` → extmark overlay sur row 0 et dernier row ; lignes internes ont `line_hl_group` |
| `metadata_plus` | bloc `+++\n...\n+++` → même comportement que metadata_minus |
| `link_ref_definition` | `[label]: url` → conceal ou virt_text sur la ligne du label |
| `checkbox` | `- [ ] todo` → extmark sur la ligne du checkbox ; `- [x] done` → extmark différent (state change) |

Setup : `H.setup_buf()` + `require("markview.spec")` en `pre_once`, `%bwipeout!` en `post_case`.

### Ajout dans `tests/test_renderer.lua` (fichier existant)

Nouveau groupe `clear` en fin de fichier :

| Cas |
|---|
| après `H.render()`, appel `markdown.clear(buf, 0, -1)` → `H.all_extmarks(buf)` retourne table vide |
| `clear(buf, 0, 0)` n'efface que les marks de la ligne 0, ligne 1 conserve ses marks |

## Pattern de base (réutiliser exactement ce qui existe)

```lua
-- Toujours pareil :
local buf = H.setup_buf({ "Heading", "=======" })
H.render(buf)
local marks = H.get_extmarks(buf, "markview/markdown")
-- assertions sur marks
```

Pour `clear` :
```lua
local md = require("markview.renderers.markdown")
md.clear(buf, 0, -1, false)
local marks = H.all_extmarks(buf)
expect.equality(#marks, 0)
```

## Ordre d'implémentation

1. `test_parser_utils.lua` — aucune dépendance, tests purs, démarrer là
2. `test_renderer_blocks.lua` — reproduire le pattern de test_renderer.lua
3. Groupe `clear` dans `test_renderer.lua`

## Vérification

```bash
make test                                              # tous les tests passent
make test-file FILE=tests/test_parser_utils.lua
make test-file FILE=tests/test_renderer_blocks.lua
```
