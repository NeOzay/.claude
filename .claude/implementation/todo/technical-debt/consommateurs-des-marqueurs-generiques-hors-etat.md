+++
id = "consommateurs-des-marqueurs-generiques-hors-etat"
title = "Neovim et `dette.md` ne connaissent que les deux Marqueurs génériques"
date = 2026-10-07
source = "chantier socle-contrat-evolutif, audit de clôture (d5be681), R4"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Trois endroits tiennent les deux Marqueurs génériques pour la liste complète des Marqueurs, alors
qu'un champ `int`, `date`, `bool` ou `list` en porte désormais la forme typée
(`<OPTIONNEL date>`) :

- la configuration Neovim, `lua/chantier.lua` : sa table `PLACEHOLDERS` ne contient que
  `<À REMPLIR>` et `<OPTIONNEL>` ;
- le plugin `listdir` de Neovim, `picker/items.lua` : sa table `EMPTY`, qui met en retrait les
  valeurs « rien n'est écrit ici », ne les contient que ;
- `skills/implementation-tracker/references/dette.md`, section « La dernière vérification, entrée
  par entrée » : « Une entrée dont `reviewed` est resté à `<OPTIONNEL>` n'a **jamais** été
  confrontée au dépôt », alors qu'une entrée créée par `list-dir new` porte maintenant
  `<OPTIONNEL date>`.

Les deux premiers sont hors de ce dépôt (`~/.config/nvim/`), que le chantier ne touche pas : ils
sont dans son Hors-périmètre.

## Pourquoi c'est gênant

Une entrée neuve, au Marqueur typé, s'affiche dans Neovim comme une valeur écrite, non en retrait :
le champ `reviewed` d'une entrée jamais relue ne se distingue plus de celui d'une entrée relue. La
phrase de `dette.md` décrit un état qui n'est plus celui que `list-dir new` produit. Rien n'échoue :
c'est un affichage et une prose, que personne ne confronte au code.

## Pour solder

Reprendre les trois : faire reconnaître la forme typée aux deux tables Lua (un motif
`^<À REMPLIR` / `^<OPTIONNEL`, plutôt qu'une table de chaînes exactes), et dire dans `dette.md` que
`reviewed` non relu porte `<OPTIONNEL date>` ou, sur une liste non migrée, `<OPTIONNEL>`. L'adaptation
de Neovim est le Chantier annoncé par le Brief du chantier `socle-contrat-evolutif`.

Solde établi par `grep -rn 'OPTIONNEL' ~/.config/nvim/lua/chantier.lua
~/.config/nvim/plugins/listdir/lua/listdir/picker/items.lua`, dont les tables reconnaissent la forme
typée, et par la relecture de `dette.md`.

## Assumé

<OPTIONNEL>
