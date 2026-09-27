+++
id = "lexique-references-au-lua-temporaire"
title = "`SKILL.md` et la CLI de `lexique` citent `nvim/lexique.lua`, un fichier déclaré temporaire"
date = 2026-09-27
source = "Identifié par `lexique-nvim`, R6 du rapport d'audit de clôture."
+++

## Constat

`skills/lexique/SKILL.md` (« `chemin`, `termes` et `definition` alimentent
`skills/lexique/nvim/lexique.lua` ») et la docstring de `skills/lexique/scripts/lexique-cli.py`
nomment `skills/lexique/nvim/lexique.lua`. Le brief de `lexique-nvim` déclare ce fichier
temporaire : il sera supprimé une fois `:Lexique` intégrée à `~/.config/nvim`, par un chantier
mené dans ce dépôt-là.

Établi par : les deux audits de clôture de `lexique-nvim` (`5312cb8`, `a30c7ce`).

## Soldé le

**Soldé le 2026-09-27 par le chantier `integrer-commande-lexique` de `~/.config/nvim`** — le
prototype est supprimé (`1961188`), `SKILL.md` et la docstring de `lexique-cli.py` désignent
`~/.config/nvim/lua/lexique.lua`.
Établi par : `grep -rn 'nvim/lexique.lua' skills/lexique` → aucune ligne, code 1 ;
`test -e skills/lexique/nvim/lexique.lua` → code 1.

## Pourquoi c'est gênant

La suppression se fera depuis un autre dépôt, où rien ne rappelle ces deux références : elles
resteront ici, périmées, et désigneront un consommateur qui n'existe plus.

## Pour solder

À la suppression de `skills/lexique/nvim/lexique.lua`, réécrire la phrase de `SKILL.md` et la
docstring de `lexique-cli.py` pour qu'elles désignent la configuration Neovim ; vérifier par
`grep -rn 'nvim/lexique.lua' skills/lexique` → rien.

## Assumé

Reporté à la clôture de `lexique-nvim` : le fichier doit vivre ici tant que l'intégration n'est
pas faite.
