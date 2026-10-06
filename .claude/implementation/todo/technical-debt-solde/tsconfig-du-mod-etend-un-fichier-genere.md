+++
id = "tsconfig-du-mod-etend-un-fichier-genere"
title = "`tsconfig.json` du mod étend un fichier que le moteur génère"
date = 2026-10-05
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, R3 (conservé, choix de l'utilisateur)"
+++

## Constat

`skills/lexique/mod/tsconfig.json` est versionné et étend `./.claude-plugin/types/tsconfig.json`,
que le moteur génère au chargement du mod et qui s'ignore lui-même (`.gitignore` à `*`).

## Pourquoi c'est gênant

Dans un clone neuf, la référence pointe dans le vide jusqu'au premier chargement du mod : l'éditeur
et `tsc -p` échouent sans explication.

## Pour solder

Ignorer `tsconfig.json` dans `.gitignore`, ou le versionner avec les types qu'il étend.

## Assumé

Conservé versionné par choix de l'utilisateur.

## Soldé le

**2026-10-06, chantier `mods-a-la-racine-des-skills`** — aucun `tsconfig.json` de mod n'est
versionné ; `tsc` passe par un `tsconfig.json` temporaire hors du mod (`OUTILLAGE.md`, « Le
TypeScript des mods »).

Établi par :

- `git ls-files | grep tsconfig` → une seule ligne, ce fichier de dette.
- `git check-ignore -v skills/lexique/tsconfig.json` → `.gitignore:65:skills/*/tsconfig.json`.
