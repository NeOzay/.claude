+++
id = "gabarit-sections-a-motif"
title = "Déclarer au Contrat le format d'une section en prose structurée, et le vérifier"
date = 2026-10-15
source = "discussion du 2026-10-15 sur les ajouts aux Gabarits"
+++

## À faire

Trois sections de Gabarit sont parsées par des regex écrites hors de gabarit, alors que leur
format n'est déclaré qu'en prose, dans la `description` du Contrat. Le format existe donc deux
fois, et `gabarit check` ne voit pas une ligne mal formée : l'erreur n'apparaît qu'à `audit pose`,
ou jamais quand la ligne est simplement ignorée.

Il s'agit de déclarer ce format dans le Contrat, d'en faire vérifier chaque ligne par `check`, et
de fournir `parse_section(item, nom) -> list[dict]` aux consommateurs, qui abandonneraient leurs
regex. Deux formes couvrent les cas actuels :

- **les puces à motif** : un gabarit de ligne plutôt qu'une regex,
  `"[{etat}] {n:int}. {intitule} — {fichiers} — vérif: {verif}"`, que le modèle lit comme
  l'exemple de la ligne à écrire, et dont chaque capture est typée par les types du Contrat ;
- **les blocs étiquetés** `**Label** :`, avec la liste des étiquettes attendues.

À trancher :

- la syntaxe du motif : le gabarit de ligne (`{n:int}`), une regex, ou les deux ;
- les types d'une capture : ceux du Contrat, une enum en ligne (`{etat:Literal[" ", "x"]}`), ou
  l'`annotation` de l'entrée `gabarit-type-object` ;
- les lignes coupées par le formateur : `pose.py` les rejoint aujourd'hui, et le parseur commun
  devra le faire aussi ;
- une section restée au Marqueur, et une liste vide (`Dettes écartées` sans dette) ;
- ce qui sépare les puces, et la prose permise entre elles ou autour d'elles ;
- les blocs étiquetés : l'ordre des étiquettes, une étiquette facultative, une étiquette en trop,
  un bloc sur plusieurs lignes ;
- le sort de la `description` en prose, qui décrit aujourd'hui le format : allégée, ou complétée
  par le motif dans `gabarit contract` ;
- le passage de `rapport_audit` (`pose.py`, `dettes.py`) au parseur commun : dans le même
  Chantier, ou ensuite ;
- le plugin Neovim `listdir` (`contract.lua`) face à une nouvelle clé de section.

## Références

- `skills/gabarit/gabarit/suivi/contract.toml` : `Étapes`, `État courant`, `Passation`,
  `Dettes écartées`, `Objectif et périmètre`, au format écrit en prose
- `skills/implementation-tracker/scripts/rapport_audit/pose.py` : `COCHEE` (Étapes), `NUMEROTEE`
  et `SOURCE` (puces du Brief), et la jonction des lignes coupées
- `skills/implementation-tracker/scripts/rapport_audit/dettes.py` : `ECARTEE` (Dettes écartées)
- `~/.config/nvim/plugins/listdir/lua/listdir/contract.lua` : lit `.list/contract.toml`, une
  nouvelle clé de section ne doit pas le casser
- Entrée `gabarit-type-object` : l'autre ajout tiré de la même discussion

## Fait le

2026-10-17, chantier `gabarit-sections-structurees` — archive :
`.claude/implementation/done/2026-10-17-gabarit-sections-structurees.md`.
