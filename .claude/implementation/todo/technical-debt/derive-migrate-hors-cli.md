+++
id = "derive-migrate-hors-cli"
title = "`derive` et `migrate` ne sont exercés que par la bibliothèque, jamais par la ligne de commande"
date = 2026-08-24
source = "chantier `tests-listdir`, réserve Q2 du relecteur de plan, restée partielle à la clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

La suite `skills/list-dir/scripts/tests/` couvre les dix commandes côté bibliothèque, et exerce en
sous-processus huit d'entre elles — `init`, `new`, `validate --filled`, `list`, `show`, `merge`,
`move`, `help`. Deux échappent à ce second regard : `derive` et `migrate`.

Ce qui reste donc non couvert est propre à leur façade : le `register()` de chacune, le nom de
leurs drapeaux et leurs valeurs par défaut — `--template` (requis), `--drop`, `--dry-run`. Un
drapeau renommé, ou passé de `store_true` à autre chose, ne ferait échouer aucun test.

## Pourquoi c'est gênant

Ce sont précisément les deux commandes les plus destructrices du paquet : `migrate` réécrit des
fichiers en se réclamant du contrat, `derive` crée une arborescence entière. Leur `--dry-run` et
leur `--drop` sont les garde-fous que l'utilisateur tape avant de s'engager, et rien ne garantit
aujourd'hui qu'ils portent encore ce nom.

Le risque est faible mais mal placé : c'est la couche la plus fine du paquet qui est nue, et c'est
celle sur laquelle l'utilisateur agit directement.

## Pour solder

Deux ou trois cas ajoutés à `skills/list-dir/scripts/tests/test_entree_cli.py`, sur le modèle des
huit autres : `migrate <liste> --dry-run` n'écrit rien et sort 0, `migrate <liste> --drop` retire,
`derive <src> <dst> --template <nom>` crée et sort 0, `derive` sans `--template` sort 2.

Solde établi par `uvx pytest skills/list-dir/scripts/tests/test_entree_cli.py -q` vert avec ces cas.

## Assumé

<OPTIONNEL>
