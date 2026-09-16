+++
id = "listerror-alias-de-gabariterror"
title = "`ListError` est un alias de `GabaritError` : une trace d'exception de list-dir affiche le nom de gabarit"
date = 2026-09-15
source = "chantier fichier-seme, audit de clôture R1 (`fadddf1`) — élargissement accepté"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Depuis le chantier `fichier-seme`, `listdir/types.py` déclare `ListError = GabaritError`.
`Result`, désormais défini dans `gabarit.types` et réexporté par list-dir, lève `GabaritError` depuis
`unwrap()`. `except ListError` rattrape toujours l'exception ; mais une trace, `__name__` et
`__module__` affichent `gabarit.types.GabaritError` au lieu de `listdir.types.ListError`.

## Pourquoi c'est gênant

Un script consommateur de la bibliothèque list-dir qui filtre ses journaux ou ses messages sur le
nom `ListError` ne le verra plus passer. C'est le seul écart observable au « comportement identique »
de list-dir promis par le brief de `fichier-seme`, hors élargissement `int`.

## Pour solder

Seule issue identifiée qui rende `ListError` aux traces sans régression : faire porter à
`Result` la classe d'exception qu'il lève, et réemballer côté list-dir chaque résultat transmis tel
quel depuis gabarit. Une simple sous-classe `ListError(GabaritError)` ne suffit pas — `unwrap()` ne
la lèverait pas, et `except ListError` ne rattraperait plus rien. Vérifier par un test qui attend
`type(exc).__name__ == "ListError"` sur `open_list(<absent>).unwrap()`.

## Assumé

Accepté par l'utilisateur le 2026-09-15 comme élargissement du périmètre, et daté dans le suivi du
chantier : le correctif est invasif et incomplet dès qu'un appel est oublié, pour un gain limité au
nom affiché.
