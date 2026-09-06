+++
id = "quatre-trous-procedure-debt-review"
title = "Quatre trous de procédure de `debt-review` sont connus et non traités"
date = 2026-08-17
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n "wc -l" skills/debt-review/SKILL.md
82:  elif [ "$(list-dir list "$T/$l" | wc -l)" -eq 0 ]; then      # Étape 0 : vide ou non, pas un compte
381:  printf '%-26s %s\n' "$l" "$(list-dir list "$T/$l" | wc -l)" # Étape 5 : la somme « après »

$ grep -n "ligne de tête\|Tête du registre\|marqueur déjà" skills/debt-review/SKILL.md skills/implementation-tracker/references/dette.md
(aucun résultat)

$ grep -rn "marqueur de catégorie exclu\|recopier l'intitulé" skills/ .claude/implementation/todo/technical-debt/.list/
(aucun résultat)
```

## Verdict

**Un trou sur quatre subsiste.** La somme « avant » n'est toujours mesurée nulle part : l'Étape 0
ne teste que `-eq 0` (vide ou non), et le seul comptage des trois registres est à l'Étape 5,
c'est-à-dire du côté « après ». Le point de comparaison reste à reconstituer.

Les trois autres sont **devenus sans objet** par la réécriture des registres en répertoires-listes :
il n'y a plus de « ligne de tête » ni de « marqueur » sous un titre — `category` et `reviewed` sont
des champs de front matter qu'une revue ultérieure écrase sans se demander s'il faut en ajouter un
second — et la clause résiduelle du gabarit n'existe plus.

L'entrée reste donc **vraie mais mal écrite** : son Constat décrit quatre trous dont trois ont
disparu. Ce n'est pas `a-solder` (le premier tient), ni `non-pertinent` (l'entrée n'est pas
entièrement sans objet) — c'est un cas de **correction de contenu**, que la catégorie ne dit pas.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

**Correction proposée à l'arbitrage** : réduire le Constat au seul trou subsistant (la somme
« avant » non mesurée), et consigner que les trois autres sont tombés avec le passage aux
répertoires-listes. `title`, `id` et `date` inchangés.

## Arbitrage

**Correction appliquée le 2026-09-06.** Le Constat est réduit au seul trou subsistant (la somme
« avant » non mesurée) ; les trois autres sont consignés comme tombés avec le passage aux
répertoires-listes, avec les commandes qui l'établissent. *Pourquoi c'est gênant* et *Pour solder*
suivent. `title`, `id` et `date` inchangés — l'intitulé reste une clé de référence, même faux.
