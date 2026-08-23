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

## Pourquoi c'est gênant

le déplacement du script dans la skill l'a rendu global ; sa surface
d'exécution n'est plus celle d'un utilitaire local à un dépôt.

## Pour solder

remplacer `-printf '%f\n'` par un `-exec basename {} \;` ou un post-traitement.

## Assumé

l'environnement est Linux, aucune contrainte du brief ne portait sur la portabilité
système.
