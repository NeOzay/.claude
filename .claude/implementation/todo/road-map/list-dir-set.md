+++
id = "list-dir-set"
title = "Ajouter à list-dir une commande `set` qui change la valeur écrite d'un champ"
date = 2026-10-14
source = "Brief du Chantier `listdir-dettes-roadmap` de `~/.config/nvim`, qui en dépend pour basculer le pin d'une dette"
+++

## À faire

`list-dir` n'a aucune commande pour changer une valeur déjà écrite : `fill` ne pose une valeur que
sur un champ resté au Marqueur, et refuse en le nommant un `--id` dont le champ est rempli. Le
picker `:Dettes` de Neovim doit basculer le champ `pin` d'une dette, et Neovim n'écrit jamais
directement dans une entrée : il appellerait `list-dir set`.

`set` poserait une valeur sur un champ déclaré d'un élément désigné, écrite ou non, avec le même
contrôle du type que `fill` et la même reprojection du front matter — le diff ne montre que la
ligne du champ.

## Références

- `skills/list-dir/references/operations.md`, « Remplir un champ resté au Marqueur » : `fill`,
  dont `set` reprendrait le contrôle de type et l'écriture
- `skills/list-dir/SKILL.md`, « Les quatorze commandes »
- `skills/implementation-tracker/list-dir/technical-debt/contract.toml` : le champ `pin`, `bool`
- Brief `~/.config/nvim/.claude/implementation/listdir-dettes-roadmap.brief.md`
