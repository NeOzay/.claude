+++
id = "git-smart-commit-sans-pyrightconfig"
title = "`git-smart-commit` porte un `ruff.toml` mais aucun `pyrightconfig.json`"
date = 2026-09-18
source = "chantier `skill-convention`, étape 7 — confrontation du Python à `rules/claude-python-style.md`"
+++

## Constat

`skills/git-smart-commit/` contient `ruff.toml` et `scripts/commit_chantier.py` (16 Ko), mais pas de
`pyrightconfig.json`. `gabarit` et `list-dir` portent les deux fichiers.

`rules/claude-python-style.md` demande que `pyrightconfig.json` **et** `ruff.toml` vivent dans la skill,
pour que sa configuration voyage avec elle.

## Pourquoi c'est gênant

Le typage de `commit_chantier.py` n'est vérifié que par le `pyrightconfig.json` de la racine. Sortie
du dépôt — et une skill est faite pour être déployée ailleurs —, la skill perd son mode de
vérification : `basedpyright` y tournerait dans son mode par défaut, qui rend un décompte
d'apparence normale sans vérifier ce que le dépôt exige.

## Pour solder

Poser `skills/git-smart-commit/pyrightconfig.json` sur le modèle de celui de `gabarit`, puis
vérifier que `uvx --with pytest basedpyright` lancé depuis la skill sort à 0.
