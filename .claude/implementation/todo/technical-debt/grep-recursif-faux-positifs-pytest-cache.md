+++
id = "grep-recursif-faux-positifs-pytest-cache"
title = "Un critère de suppression formulé en grep -rn rend des faux positifs depuis .pytest_cache"
date = 2026-09-10
source = "chantier supprimer-dump-value, rapport d'audit R8"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`grep -rn` ne respecte pas `.gitignore`. Sous `skills/list-dir/scripts/`, le répertoire
`.pytest_cache` n'est pas suivi par git et son fichier `v/cache/nodeids` garde en mémoire les noms
des tests exécutés lors des dernières passes — y compris ceux qui ont été supprimés depuis.

Un critère de réussite formulé « `grep -rn "<symbole>" <chemin>` ne rend plus rien » est donc en
échec apparent dès que la suite a tourné avant lui, alors que le symbole a bel et bien disparu du
code suivi. Le brief de ce chantier portait cette formulation ; le fichier de suivi et le plan
portaient la forme `git grep`, et c'est elle qui a fait foi.

Établi par : sur `skills/list-dir/scripts/`, `git grep -n "dump_value\|ESCAPES"` → aucune sortie,
tandis que `grep -rn "dump_value\|ESCAPES"` → 14 lignes, toutes dans `.pytest_cache`.

## Pourquoi c'est gênant

Le mode de défaillance va dans les deux sens, et le second est le mauvais. Un critère en échec
apparent se diagnostique en quelques minutes. Mais la même racine produit l'inverse : un `grep -rn`
qui ne trouve **plus** un symbole parce qu'il n'a cherché que dans les fichiers présents, alors
qu'un fichier ignoré le porte encore.

Plus général : c'est un critère de réussite qui dépend de l'état d'un cache, donc du fait que la
suite ait tourné ou non avant lui. Un critère qui change de verdict sans que le code change n'est
pas un critère.

## Pour solder

Poser la règle une fois, là où les critères de réussite s'écrivent — `intent-brief` et le contrat
d'`implementation-tracker` : **un critère d'absence se formule en `git grep`**, qui ne voit que le
suivi. Ne réserver `grep -rn` qu'aux recherches où le non-suivi compte réellement.

Vérification : le prochain brief portant un critère de suppression le formule en `git grep`.

## Assumé

Rien à corriger sur ce chantier : le brief est figé une fois validé, et la forme correcte figurait
déjà dans le suivi et le plan.
