+++
id = "impl-list-sans-configuration-de-linters"
title = "`implementation-tracker` porte du Python sans aucune configuration de linters"
date = 2026-09-18
source = "chantier `skill-convention`, étape 7 — confrontation du Python à `rules/claude-python-style.md`"
+++

## Constat

`skills/implementation-tracker/scripts/impl_list.py` est versionné et exposé par `bin/` sous le nom
`impl-list`. La skill ne contient ni `ruff.toml` ni `pyrightconfig.json`.

`rules/claude-python-style.md` demande les deux dans la skill. Sans `ruff.toml` local, `uvx ruff check`
appliqué à ce fichier retombe sur les valeurs par défaut de ruff — ni `line-length = 100`, ni
`target-version = "py312"`, ni le jeu de règles `E F I UP B SIM RUF` du dépôt.

## Pourquoi c'est gênant

La skill est vérifiée par une configuration qu'elle n'emporte pas : déployée seule, elle n'est plus
vérifiée du tout, et rien ne le signale. Le fichier passe aujourd'hui les deux linters, ce qui rend
l'écart invisible tant qu'il n'est pas modifié.

## Pour solder

Copier `ruff.toml` et `pyrightconfig.json` depuis `gabarit`, les ajuster aux chemins de la skill, et
vérifier que les deux linters lancés depuis `skills/implementation-tracker/` sortent à 0.
