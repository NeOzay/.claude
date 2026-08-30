+++
id = "ruff-format-jamais-applique"
title = "Le formatage ruff n'a jamais été appliqué au paquet list-dir"
date = 2026-08-30
source = "chantier semences-de-listes, journal du suivi et audit R7"
+++

## Constat

`uvx ruff format --check .` dans `skills/list-dir/` signale **cinq fichiers** à reformater :
`references/contrat-liste.md` et les suites `test_contract.py`, `test_items.py`, `test_loader.py`,
`test_move.py`. Chacun vérifié antérieur au chantier `semences-de-listes`, en confrontant sa version
`master` extraite par `git show` au même contrôle.

**Cette entrée a d'abord annoncé cinq fichiers alors qu'il y en avait six**, et affirmé que le
chantier « n'y a rien ajouté ». C'était faux : `test_entree_cli.py`, formaté sur `master`, avait été
dé-formaté par des enroulements de ligne écrits à la main pour satisfaire `E501`. Le fichier a été
repassé à `ruff format` et le compte est redescendu à cinq — mais le constat mérite d'être gardé ici
plutôt qu'effacé : c'est précisément parce que rien ne contrôle le formatage qu'une régression
introduite par un chantier a pu passer six commits sans être vue, et se faire décrire comme
antérieure à lui.

`contrat.md`, section Dépendances, ne déclare que `uvx ruff check .` et
`uvx --with pytest basedpyright` : le formatage n'est **pas** dans les contrôles du pipeline, et
rien ne le réclame aujourd'hui. Le chantier `semences-de-listes` avait inscrit
`uvx ruff format --check` à son contrôle final, puis l'a retiré en constatant qu'il échouait sur
ces cinq fichiers.

## Pourquoi c'est gênant

Le paquet est destiné à être déployé ailleurs, et sa configuration voyage avec lui : `ruff.toml`
vit dans le skill précisément pour cela. Un `ruff format` lancé par quelqu'un qui reprend le paquet
réécrit alors cinq fichiers d'un coup, et le diff de son propre travail devient illisible sous le
bruit du reformatage.

L'écart grandit aussi en silence, et pas seulement vers le passé : rien n'empêche un chantier d'en
**ajouter** un, comme celui-ci l'a fait sans s'en apercevoir. Un contrôle qu'aucune commande ne
lance ne protège de rien — c'est un fichier neuf hors format qui reste invisible, autant qu'un
ancien.

## Pour solder

Trancher d'abord la question de fond : le formatage fait-il partie du contrat du paquet ou non ?

- **Oui** → lancer `uvx ruff format .` en un commit isolé, ne touchant à rien d'autre, puis ajouter
  `uvx ruff format --check .` aux contrôles déclarés dans `contrat.md` pour que l'écart ne revienne
  pas.
- **Non** → le dire dans `contrat.md`, pour qu'un prochain chantier ne réinscrive pas ce contrôle
  au motif qu'il paraît évident — ce que celui-ci a fait.

Ne pas mélanger le reformatage à un chantier fonctionnel : c'est ce qui rend le diff de l'un
inaudible dans l'autre.
