+++
id = "basedpyright-treize-erreurs-non-tenues"
title = "`basedpyright` rend treize erreurs là où le dépôt en attend zéro"
date = 2026-09-05
source = "chantier provenance-listes-derivees, journal du suivi et audit R1"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`(cd skills/list-dir && uvx --with pytest basedpyright)` rend **13 erreurs**, réparties ainsi :

- `scripts/listdir/provenance.py` — 4 erreurs, sur `_fichiers` (`trouves` et son type de retour,
  « partially unknown ») et sur la variable `ancien` de `reseed` ;
- `scripts/tests/test_prefill.py` — 9 erreurs sur une seule ligne, celle qui déballe un tuple
  hétérogène et appelle `.split` sur chacun de ses membres.

Elles sont **préexistantes** : l'audit de clôture du 2026-09-05 les a comparées à une extraction
de `master` faite hors dépôt par `git archive`, et la sortie est ligne pour ligne identique.
L'audit de clôture du 2026-09-03 relevait pourtant `0 errors, 0 warnings, 0 notes` sur le même
paquet. Rien dans le code n'a bougé entre les deux sur ces lignes ; la version installée est
`basedpyright 1.39.10` / `pyright 1.1.412`, et une montée de version de l'outil est la cause la
plus probable — non vérifiée, la version d'alors n'ayant pas été consignée.

## Pourquoi c'est gênant

Plusieurs briefs de ce dépôt portent « `basedpyright` → 0 error » comme critère de réussite, et ce
critère est désormais **faux dans sa lettre** dès l'ouverture d'un chantier. Chaque chantier doit
alors le renégocier en « aucune erreur ajoutée » et le justifier par une extraction de la base —
un travail refait à chaque fois, qui finit par ne plus être fait du tout. Un seuil qu'on sait
dépassé cesse d'être lu : le jour où une quatorzième erreur apparaît, elle passera pour le bruit
de fond des treize autres.

## Pour solder

Traiter les deux foyers, qui n'ont rien à voir l'un avec l'autre :

- `test_prefill.py` — annoter le déballage du tuple hétérogène, ou le découper, pour que
  `.split` ne soit appelé que sur les membres qui sont des `str` ;
- `provenance.py` — annoter `trouves` dans `_fichiers` et `ancien` dans `reseed`, dont
  l'inférence part de `set()` et d'un `ok({})` vides.

Puis consigner la version de l'outil dans le contrôle, faute de quoi le même écart se rejouera au
prochain saut de version.

## Assumé

<OPTIONNEL>
