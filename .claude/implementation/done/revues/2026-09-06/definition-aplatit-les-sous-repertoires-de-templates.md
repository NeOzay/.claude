+++
id = "definition-aplatit-les-sous-repertoires-de-templates"
title = "L'amorçage depuis une définition perd les sous-répertoires de templates/"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -rn "definition / TEMPLATES" skills/list-dir/scripts/listdir/
skills/list-dir/scripts/listdir/provenance.py:232:            for f in sorted((definition / TEMPLATES).glob("*"))

$ sed -n '229,234p' skills/list-dir/scripts/listdir/provenance.py
        gabarits = {
            f.name: f.read_text(encoding="utf-8")
            for f in sorted((definition / TEMPLATES).glob("*"))
            if f.is_file()
        }
```

## Verdict

Le comportement est inchangé : `glob("*")` non récursif, filtré `f.is_file()`, donc tout
sous-répertoire de `templates/` est ignoré en silence et `init --def` sort 0 sur un travail à
moitié fait. Ni le refus explicite ni la copie récursive n'ont été écrits, et aucun test ne monte
une définition à sous-répertoire.

**La lecture a bougé de fichier** : l'entrée situe le code dans `store.py:_read_definition`, il vit
aujourd'hui dans `provenance.py`. Le repère est donc périmé, mais le texte qu'il décrivait a été
retrouvé à l'identique — c'est bien la même dette, pas une disparition.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

**Correction proposée à l'arbitrage** : remplacer « `store.py:_read_definition` » par
« la lecture des gabarits d'une définition (`provenance.py`) », ou décrire la ligne sans nommer
son fichier — même raison que l'interdiction des numéros de ligne au registre.

## Arbitrage

**Correction appliquée le 2026-09-06.** Le repère `store.py:_read_definition` est remplacé par la
fonction et son fichier actuel (`_read_definition`, `listdir/provenance.py`), et la migration du
code est consignée pour qu'une revue future ne reprenne pas le déplacement pour une disparition.
