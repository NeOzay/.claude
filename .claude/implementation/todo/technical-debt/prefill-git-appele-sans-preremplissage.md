+++
id = "prefill-git-appele-sans-preremplissage"
title = "create, migrate et derive lancent git même quand aucun champ n'est prérempli"
date = 2026-08-31
source = "chantier 2026-08-31-champs-preremplis, audit de clôture R7"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`listdir/store.py` construit un `PrefillContext` en tête de `create`, `migrate` et `derive`, et
`prefill.context` y résout `LISTDIR_ROOT` par un `git rev-parse --show-toplevel`.

Vérifié par interposition d'un `git` traçant dans le `PATH` : un `list-dir new` sur un contrat ne
portant **ni `text` ni `command`** produit un `rev-parse`. Avant ce chantier, ces trois opérations
n'engendraient aucun processus.

## Pourquoi c'est gênant

Un `fork`/`exec` est payé à chaque `new` de la quasi-totalité des listes existantes, dont aucune
n'utilise le préremplissage. Le coût est invisible à l'unité et systématique à l'usage — c'est
exactement le profil qu'on ne remarque jamais.

## Pour solder

Rendre `root` paresseux : ne résoudre la racine qu'au premier appel de `_run`, donc jamais si aucun
champ ne porte `command`. Un `PrefillContext` immuable peut le faire par un cache mutable interne,
ou `context()` peut recevoir le contrat et ne rien résoudre quand aucune déclaration ne porte
`command`.

## Assumé

<OPTIONNEL>
