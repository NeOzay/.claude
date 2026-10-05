+++
id = "tsconfig-du-mod-etend-un-fichier-genere"
title = "`tsconfig.json` du mod étend un fichier que le moteur génère"
date = 2026-10-05
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, R3 (conservé, choix de l'utilisateur)"
+++

## Constat

`skills/lexique/mod/tsconfig.json` est versionné et étend `./.claude-plugin/types/tsconfig.json`, que
le moteur génère au chargement du mod et qui s'ignore lui-même (`.gitignore` à `*`).

## Pourquoi c'est gênant

Dans un clone neuf, la référence pointe dans le vide jusqu'au premier chargement du mod : l'éditeur et
`tsc -p` échouent sans explication.

## Pour solder

Ignorer `tsconfig.json` dans `.gitignore`, ou le versionner avec les types qu'il étend.

## Assumé

Conservé versionné par choix de l'utilisateur.
