+++
id = "listdir-sans-suite-de-tests"
title = "Le paquet `listdir` n'a aucune suite de tests"
date = 2026-08-23
source = "chantier `format-registres`, constaté à la clôture — question de l'utilisateur, aucun rapport d'audit ne l'avait relevé"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le paquet compte **19 modules et 2254 lignes** de Python, et le dépôt ne contient **aucun** test :

```
$ find . -path ./plugins -prune -o \( -name 'test_*.py' -o -name '*_test.py' \
       -o -name 'conftest.py' -o -name 'tests' -type d \) -print
(aucune sortie)
$ grep -rn 'pytest\|unittest\|doctest' skills/ scripts/
(aucune sortie)
```

Ce qui tient lieu de vérification aujourd'hui : `ruff`, `basedpyright` en mode `all`, et des
**exécutions manuelles** consignées dans la section *Preuves d'exécution* du suivi de chantier. Les
linters ne jugent que la forme et les types ; les preuves d'exécution ne se rejouent pas seules —
elles sont recopiées à la main dans un fichier archivé à la clôture.

## Soldé le

**2026-08-24, chantier `tests-listdir`** — le paquet porte une suite de 241 tests dans
`skills/list-dir/scripts/tests/`, couvrant `items`, `contract`, `store` (lecture, écriture,
`derive`, `merge`, `move`), `loader`, `utils` et le point d'entrée en sous-processus. Les cinq
priorités que cette entrée listait sont couvertes : aller-retour octet et frontière des deux règles,
les deux verdicts de `validate`, `derive`/`merge` (report par `from`, conservation, refus d'une
destination existante), `migrate` (complétion, réordonnancement, rejeu sans écriture), et les échecs
fermés (un code de sortie et un message par cas nommé). `move` tourne sur un dépôt git jetable
(`tmp_path` + `git init`) et vérifie que `git log --follow` remonte au commit de création.

Établi par :

```
$ uvx pytest skills/list-dir/scripts/tests -q
241 passed                                                        code 0
$ uvx pytest scripts/tests -q
67 passed                                                         code 0
$ cd skills/list-dir && uvx ruff check .
All checks passed!
$ cd skills/list-dir && uvx --with pytest basedpyright
0 errors, 0 warnings, 0 notes
```

Couverture mesurée à 95 % des modules du paquet lors de l'audit de clôture — information seule,
aucun seuil n'ayant été retenu au brief : « la couverture n'est pas l'objectif, le comportement
l'est ».

Deux constats subsistent et sont au registre actif : `derive-migrate-hors-cli` et
`garde-version-jamais-executee`.

## Pourquoi c'est gênant

Deux défauts de comportement ont été trouvés par un **auditeur qui lisait le code**, non par une
commande : `init` écrivait un `contract.toml` invalide en rendant 0 sur un `--name` contenant un
guillemet, et `parse_sections` découpait sur les `## ` situés à l'intérieur d'un bloc de code. Les
deux touchent le cœur du paquet, les deux ont survécu à toutes les vérifications d'étape, et rien ne
garantit qu'un troisième ne dort pas.

Le coût réel est celui de la **non-régression** : à chaque correctif, il faut rejouer à la main les
13 contrôles du plan pour établir que rien n'a bougé. C'est long, c'est facultatif, et donc ce sera
un jour sauté — sur un paquet dont tout le pipeline dépend désormais, puisque les trois registres de
dette et `debt-review` passent par lui.

Le paquet est par ailleurs conçu pour être testable : `Result[T]` rend les échecs inspectables sans
capturer de sortie, et la bibliothèque est importable sans la CLI. Rien ne s'oppose aux tests que
leur absence.

## Pour solder

Une suite `pytest` dans `skills/list-dir/tests/`, lancée par `uvx pytest`, couvrant en priorité ce
que les preuves d'exécution établissent déjà à la main :

- l'aller-retour octet pour octet et la frontière entre les règles 1 et 2 de `items.py` ;
- les deux verdicts de `validate`, avec et sans `--filled` ;
- `derive` / `merge` : report par `from`, conservation, refus d'une destination existante ;
- `migrate` : complétion, réordonnancement, rejeu sans écriture ;
- les échecs fermés — un code de sortie et un message par cas d'erreur nommé.

`move` demande un dépôt git jetable (`tmp_path` + `git init`), sur le modèle de ce qui a été fait à
la main pour l'étape 9.

Le solde s'établit par `uvx pytest` vert **et** par la mesure de couverture des modules du paquet.

## Assumé

<OPTIONNEL>
