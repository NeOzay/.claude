+++
id = "typage-strict-non-tenu-dans-scripts-tests"
title = "Les tests de `scripts/` ne tiennent pas le typage strict du dépôt"
date = 2026-09-18
source = "chantier `skill-convention`, étape 7 — confrontation du Python à `rules/claude-python-style.md`"
+++

## Constat

`uvx --with pytest basedpyright scripts` rend **12 erreurs**, toutes dans
`scripts/tests/test_sante_skills.py`, toutes `reportPrivateUsage` : le test atteint `_dependances`,
privé du module qu'il vérifie. Les autres fichiers de `scripts/` et les paquets `gabarit` et
`list-dir` passent sans erreur sous la même commande.

`rules/claude-python-style.md` pose le typage strict — basedpyright en `typeCheckingMode: "all"` — sans
exempter les tests, et `pyrightconfig.json` de la racine inclut bien `scripts`.

## Pourquoi c'est gênant

Un répertoire qui sort en erreur sous la commande d'`OUTILLAGE.md` apprend à son lecteur à ignorer
le verdict : la douzième erreur cache la treizième, qui sera peut-être réelle. Et l'exception au
typeur que `rules/claude-python-style.md` admet — `cast` ou `# pyright: ignore[<règle>]`, ciblée et
justifiée — n'est ici ni posée ni refusée : le code reste dans un état que la convention ne prévoit
pas.

## Pour solder

Deux voies, à trancher : exposer ce dont le test a besoin sous un nom public, ou marquer chaque
accès d'un `# pyright: ignore[reportPrivateUsage]` avec le motif, comme la convention l'exige.
Renoncer au typage strict sur `scripts/tests/` serait une troisième voie, qui demande alors de
l'écrire dans `rules/claude-python-style.md`.
