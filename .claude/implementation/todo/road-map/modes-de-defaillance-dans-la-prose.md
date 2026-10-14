+++
id = "modes-de-defaillance-dans-la-prose"
title = "Intégrer à la prose les 45 blocs cités de mode de défaillance, sous un contrôle à plafond"
date = 2026-10-14
source = "relecture de la dette `deux-conventions-de-mode-de-defaillance`, discussion du 2026-10-14"
+++

## À faire

La convention veut le mode de défaillance dans le corps du texte, et 45 blocs cités subsistent ;
leur nombre a crû depuis que la règle est écrite. D'abord un contrôle de `check_pipeline.py` qui
compte ces blocs et échoue au-delà d'un plafond, abaissé à chaque réécriture, pour arrêter la
dérive ; puis la réécriture, fichier par fichier, sans perte de fond. Un travail éditorial :
`debt-review` et `contrat.md` portent les deux tiers des blocs, et peuvent faire chacun leur Étape.

## Références

- Dette `deux-conventions-de-mode-de-defaillance` : le décompte par fichier et sa commande
- `shadow-skills/skill-convention/references/prose.md`, « Chaque règle porte son motif, dans la
  prose » : la règle
- Les références de `skills/list-dir/` : la forme cible, déjà pratiquée
- `scripts/check_pipeline.py` : où vit le contrôle ; `OUTILLAGE.md` pour le lancer
