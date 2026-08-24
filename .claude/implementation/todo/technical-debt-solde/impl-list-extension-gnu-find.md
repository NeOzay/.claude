+++
id = "impl-list-extension-gnu-find"
title = "`impl-list.sh` dépend d'une extension GNU de `find`"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R7 du rapport d'audit."
reviewed = 2026-08-17
category = "pertinent"
+++

## Constat

`impl-list.sh` utilise `find … -printf '%f\n'`, absent des `find` BSD. Sur macOS, le
script échoue — et il est désormais sur le chemin d'entrée de toute invocation du tracker, dans
n'importe quel dépôt.

## Soldé le

**Soldé le 2026-08-24 par le chantier `check-pipeline-python`** — `impl-list.sh` a été réécrit en
`impl_list.py` : le `find … -printf '%f\n'`, extension GNU absente des `find` BSD, a disparu au
profit de `Path.iterdir()`. Le script est désormais portable partout où Python tourne, ce qui
importait d'autant plus qu'il est sur le chemin d'entrée de toute invocation du tracker.

Établi par : sorties de l'ancien `.sh` et du nouveau `.py` comparées sur
`.claude/implementation`, `todo/`, `done/` et un répertoire absent → **identiques**, stdout comme
stderr, rc 0 des deux côtés.

## Pourquoi c'est gênant

le déplacement du script dans la skill l'a rendu global ; sa surface
d'exécution n'est plus celle d'un utilitaire local à un dépôt.

## Pour solder

remplacer `-printf '%f\n'` par un `-exec basename {} \;` ou un post-traitement.

## Assumé

l'environnement est Linux, aucune contrainte du brief ne portait sur la portabilité
système.
