+++
id = "gabarit-porte-des-residus-de-liste"
title = "Le paquet gabarit porte encore des notions et des renvois propres à une liste"
date = 2026-09-15
source = "chantier fichier-seme, audit de clôture R4 (`fadddf1`), reconduit par R6 (`5123a3d`) — clos avec"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le paquet `gabarit` se déclare sans notion de liste (« rien ici ne connaît de répertoire ni de
liste », `gabarit/__init__.py`), mais le découpage du chantier `fichier-seme` y a laissé :

- `Item.id` dans `gabarit/types.py`, qui rend `path.stem` — la règle d'identité d'un élément de
  liste, alors que `references/semences.md` du skill dit qu'« aucun `id` n'est imposé » à un gabarit ;
- des docstrings qui citent leur consommateur : celle de `Result`/`ok` (« items() rend… », « move() »,
  `validate`), celle de `items.py` (`init_list`, `provenance.emit`).

## Pourquoi c'est gênant

`gabarit` documente `listdir` : un changement de nom ou de comportement côté list-dir rendra ces
commentaires faux sans qu'aucun contrôle le signale. `Item.id` invite un appelant de gabarit à
supposer une identité par nom de fichier, que la documentation du skill récuse — un suivi archivé
sous `done/<date>-<slug>.md` n'a plus le nom de son slug.

## Pour solder

Déplacer `id` vers `listdir` (propriété calculée côté liste, ou fonction `item_id(item)`), et
réécrire les docstrings de `gabarit/types.py` et `gabarit/items.py` sans nommer `listdir`. Vérifier :
`grep -rnE 'items\(\)|move\(\)|init_list|provenance|\.id\b' skills/gabarit/scripts/gabarit` → aucune
occurrence, et `.venv/bin/python -m pytest skills/list-dir/scripts/tests -q` → 447 passed.

## Assumé

Clos avec, le 2026-09-15 : le chantier bornait la retouche de list-dir à son code interne, et
retirer `Item.id` touche la surface que ses tests importent. Aucun signal de dérive n'est déclenché
dans le code — ce sont des traces, pas une logique de liste.
