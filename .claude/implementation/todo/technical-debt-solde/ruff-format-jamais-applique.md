+++
id = "ruff-format-jamais-applique"
title = "Le formatage ruff n'a jamais été appliqué au paquet list-dir"
date = 2026-08-30
source = "chantier semences-de-listes, journal du suivi et audit R7"
reviewed = 2026-09-06
category = "aggravee"
+++

## Constat

**Mesuré le 2026-09-06 :** `uvx ruff format --check .` dans `skills/list-dir/` signale **huit
fichiers** à reformater — `8 files would be reformatted, 39 files already formatted` :
`references/extension.md`, `test_contract.py`, `test_derive_merge.py`, `test_fusion.py`,
`test_items.py`, `test_loader.py`, `test_move.py`, `test_provenance.py`.

**Trois de plus qu'au constat d'origine**, qui en comptait cinq le 2026-08-30 :
`test_fusion.py`, `test_derive_merge.py` et `test_provenance.py` sont des suites écrites **après**
lui. C'est exactement le mode de défaillance que l'entrée annonçait — « rien n'empêche un chantier
d'en ajouter un » —, vérifié en une semaine.

L'entrée avait déjà connu ce mouvement une fois : elle a d'abord annoncé cinq fichiers alors qu'il
y en avait six, `test_entree_cli.py` ayant été dé-formaté par des enroulements écrits à la main
pour satisfaire `E501`, puis repassé à `ruff format`. Le constat mérite d'être gardé : c'est parce
que rien ne contrôle le formatage qu'une régression introduite par un chantier passe des commits
sans être vue.

`contrat.md`, section Dépendances, ne déclare toujours que `uvx ruff check .` et
`uvx --with pytest basedpyright` : le formatage n'est **pas** dans les contrôles du pipeline, et
rien ne le réclame. Le chantier `semences-de-listes` avait inscrit `uvx ruff format --check` à son
contrôle final, puis l'a retiré en constatant qu'il échouait.

## Soldé le

**2026-10-04, hors chantier** — la question de fond est tranchée par **oui** : le formatage fait
partie du contrat. Un `ruff.toml` à la racine couvre `scripts/` et `statusline-command.py` à 100
colonnes, comme les skills. Chaque `ruff.toml`, celui de la racine comme ceux des six skills, porte
`[format] exclude = ["*.md"]`. `uvx ruff format .` a reformaté 21 fichiers Python, en un commit
qui ne touche à rien d'autre (`style: appliquer ruff format au Python du dépôt`).

La déclaration du contrôle va dans `OUTILLAGE.md` et non dans `contrat.md`, comme **Pour solder**
le demandait : la section Dépendances de `contrat.md` y a été transportée entre-temps.
`OUTILLAGE.md` porte la commande dans son tableau de dépendances, et une règle dans « Vérifier le
code Python » : « Le formatage fait partie du contrat ». Le rappel de session
(`hooks/outillage-rappel.sh`) la répète.

`references/extension.md`, compté parmi les huit fichiers du constat, n'est pas reformaté mais
exclu : ruff 0.16 formate les blocs de code des `.md`, dont les commentaires sont alignés à la main.

Établi par, depuis la racine et depuis le paquet seul :

```
$ uvx ruff format --check .
95 files already formatted                                   code 0

$ cd skills/list-dir && uvx ruff format --check .
41 files already formatted                                   code 0
```

Sans régression : `uvx ruff check .` passe de 6 à 5 erreurs (un `E501` de `test_contract.py`
résorbé par le reformatage, aucune nouvelle), `uvx --with pytest basedpyright` rend 6580 erreurs
avant comme après, et les sept suites de tests rendent 783 tests verts avant comme après.

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
