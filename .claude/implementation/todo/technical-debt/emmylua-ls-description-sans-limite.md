+++
id = "emmylua-ls-description-sans-limite"
title = "La description d'emmylua-ls ne dit pas ce que la skill ne fait pas"
date = "2026-09-17"
source = "chantier `skill-convention`, confrontation des skills à `references/prose.md`"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/skill-convention/references/prose.md`, section « La description dit quoi, quand, et ce que
la skill ne fait pas », exige trois choses de la `description` du frontmatter : ce que fait la
skill, quand elle se déclenche, et sa limite en une phrase négative.

Celle de `skills/emmylua-ls/SKILL.md` porte les deux premières (« Référence du LSP emmylua_ls… »,
« Déclencher dès que l'utilisateur mentionne… ») et **aucune limite négative**. Les autres skills
du dépôt en portent une : « Ne juge aucun contenu » (`gabarit`, `list-dir`), « Ne corrige aucun
code » (`debt-review`), « This skill covers mini.test specifically — not plenary.busted »
(`nvim-mini-test`).

## Pourquoi c'est gênant

La `description` est tout ce que le modèle voit avant de déclencher la skill. Sans limite, elle se
déclenche sur les demandes voisines qu'elle ne sait pas traiter — ici, tout ce qui touche à Lua
dans Neovim sans relever du LSP : le style de code, couvert par `rules/lua-style.md`, ou les tests,
couverts par `nvim-mini-test`. Le coût est une skill chargée pour rien, et une réponse construite
sur la mauvaise référence.

## Pour solder

Ajouter une phrase négative à la `description` d'`skills/emmylua-ls/SKILL.md`, qui écarte au moins
le style de code et les tests.

## Assumé

<OPTIONNEL>
