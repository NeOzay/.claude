+++
id = "nvim-mini-test-redigee-en-anglais"
title = "La skill nvim-mini-test est rédigée en anglais"
date = "2026-09-17"
source = "chantier `skill-convention`, confrontation des skills à `references/prose.md`"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/skill-convention/references/prose.md`, section « La prose est en français », énonce que la
prose d'une skill est en français. `skills/nvim-mini-test/` est intégralement en anglais : le
`SKILL.md` (337 lignes, intitulés « When to use mini.test », « Common pitfalls »…), sa
`description` de frontmatter, et ses deux références `examples.md` et `mini-test-api.md`.

Relevé le 2026-09-17 : aucun autre skill du dépôt n'est dans ce cas — `emmylua-ls`, qui traite
aussi d'un outil dont la documentation amont est en anglais, est rédigé en français.

## Pourquoi c'est gênant

Le coût n'est pas la compréhension, mais la règle : une convention qu'un skill du dépôt contredit
ouvertement cesse d'en être une, et le prochain skill écrit tranchera par imitation de celui qu'il
a sous les yeux. C'est le même mécanisme que les deux conventions de mode de défaillance, qui
divergent depuis qu'aucune règle n'a été écrite.

S'y ajoute un coût de lecture pour l'utilisateur, dont toutes les autres skills lui parlent
français.

## Pour solder

Traduire `skills/nvim-mini-test/SKILL.md`, sa `description` et ses deux références, en laissant
dans leur forme d'origine les identifiants, les noms d'API `mini.test` et les extraits de code.

## Assumé

<OPTIONNEL>
