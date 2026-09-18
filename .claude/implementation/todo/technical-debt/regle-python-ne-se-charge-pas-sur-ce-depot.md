+++
id = "regle-python-ne-se-charge-pas-sur-ce-depot"
title = "`rules/claude-python-style.md` ne se charge pas sur le Python de ce dépôt"
date = 2026-09-18
source = "chantier `skill-convention`, audit de clôture R2 (`cea0665`) — report assumé par l'utilisateur"
+++

## Constat

`rules/claude-python-style.md` porte `paths: ["**/.claude/**/*.py"]`. D'après
`https://code.claude.com/docs/en/memory.md`, le motif est apparié au chemin **relatif à la racine
du projet**. Quand la racine du projet est `/home/debian/.claude` — le cas de ce dépôt —, les
chemins relatifs valent `scripts/check_pipeline.py`, `skills/gabarit/scripts/…` : aucun segment
`.claude`, aucune correspondance.

La règle se charge donc correctement sur le `.claude/**/*.py` de tout **autre** projet, et jamais
sur le Python de ce dépôt-ci, où vit la quasi-totalité du Python concerné.

L'appariement relatif est déduit des exemples de la documentation, qui ne l'énonce pas ; il n'a pas
été observé en session.

## Pourquoi c'est gênant

La convention de code existe, elle est citée par `skill-convention`, et elle ne se présente jamais
au modèle quand celui-ci écrit du Python ici : une règle qu'on croit active et qui ne l'est pas est
pire qu'une règle absente, parce que personne ne va vérifier.

## Pour solder

D'abord constater : ouvrir un `.py` de ce dépôt en session et lire `/context` pour voir si la règle
est chargée. Si elle ne l'est pas, ajouter au `paths` les chemins de ce dépôt (`scripts/**/*.py`,
`skills/**/*.py`, `*.py`) en acceptant qu'ils puissent apparier des répertoires homonymes ailleurs,
ou revenir à `"**/*.py"` comme `rules/lua-style.md`.

## Assumé

Report délibéré à la clôture du 2026-09-18 : la restriction à `.claude/**` est voulue, et
l'alternative connue — `"**/*.py"` — chargerait la règle sur le Python de tous les projets, ce que
l'utilisateur ne veut pas.
