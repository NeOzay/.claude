+++
id = "definition-aplatit-les-sous-repertoires-de-templates"
title = "L'amorçage depuis une définition perd les sous-répertoires de templates/"
date = 2026-08-30
source = "chantier semences-de-listes, audit R5"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

La lecture des gabarits d'une définition — `_read_definition`, aujourd'hui dans
`listdir/provenance.py` — les collecte par `sorted((definition / TEMPLATES).glob("*"))`, filtré par
`f.is_file()`. Tout **sous-répertoire** de `templates/` est donc ignoré, sans message et sans code
non nul : `init --def` sort 0 et rend une liste à laquelle il manque des gabarits.

Aucune des définitions embarquées n'est concernée — `technical-debt/templates/` ne porte que
`review.toml` et `review.md`, deux fichiers plats. Aucun test ne couvre le cas, et la docstring ne
le mentionne pas.

Établi par : `grep -rn "definition / TEMPLATES" skills/list-dir/scripts/listdir/` →
`provenance.py:232`, `glob("*")` non récursif suivi de `if f.is_file()`. Vérifié le 2026-09-06 —
le code a migré de `store.py` vers `provenance.py` depuis le constat d'origine, sans changer de
comportement ; l'entrée le nomme désormais par sa fonction plutôt que par son fichier.

## Pourquoi c'est gênant

La convention `list-dir/<nom>/` est publique : elle est documentée dans `definitions.md` pour que
des définitions tierces s'y rangent. La première qui organisera ses gabarits en sous-répertoires les
verra disparaître à l'amorçage, et l'échec ne se manifestera qu'au premier `derive`, loin de la
commande qui l'a causé.

C'est un succès silencieux sur un travail à moitié fait, exactement ce que le paquet dit exister
pour supprimer — `list-dir.py` : « ÉCHEC FERMÉ […] Jamais de succès silencieux ».

## Pour solder

Trancher ce que `templates/` accepte, et le faire dire par le code :

- **arborescence plate seulement** → `_read_definition` refuse en nommant le sous-répertoire
  trouvé, et la docstring comme `definitions.md` le déclarent ;
- **arborescence libre** → la copie devient récursive, et un test monte une définition à
  sous-répertoire pour le prouver.

Dans les deux cas, un test : c'est son absence qui a laissé le comportement indéterminé.
