+++
id = "lexique-blocs-de-code-imbriques"
title = "`lexique` ne suit pas les clôtures de bloc de code imbriquées, et son message induit en erreur"
date = 2026-09-23
source = "Identifié par `lexique`, R12 du rapport d'audit de clôture."
+++

## Constat

`_blocs`, dans `skills/lexique/scripts/lexique.py`, bascule l'état « dans un bloc de code » à
chaque ligne qui commence par ```` ``` ```` ou `~~~`, sans distinguer le type ni la longueur de la
clôture. Un bloc ```` ```` ```` qui contient un ```` ``` ````, ou un `~~~` qui contient ```` ``` ````,
inverse l'état au milieu du bloc : le vrai tableau du lexique est alors lu comme un exemple, et la
commande répond « aucun tableau ».

Établi par : l'audit de clôture de `lexique` (`6b06ca6`) a reproduit le cas sur un lexique
temporaire.

## Pourquoi c'est gênant

Le message désigne une absence de tableau alors que le tableau est là : on cherche la faute au
mauvais endroit. Le cas est rare — un lexique porte rarement des exemples de code imbriqués —,
mais un contrôle qui ment sur sa cause coûte plus cher qu'un contrôle qui échoue franchement.

## Pour solder

Suivre la clôture ouvrante (caractère et longueur) et ne fermer que sur une clôture du même
caractère et au moins aussi longue, comme CommonMark ; ajouter un test à `test_lire.py` pour les
deux imbrications.
