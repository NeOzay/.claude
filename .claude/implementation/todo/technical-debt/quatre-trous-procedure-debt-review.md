+++
id = "quatre-trous-procedure-debt-review"
title = "Quatre trous de procédure de `debt-review` sont connus et non traités"
date = 2026-08-17
source = "Identifié par `revue-dette`, R5 à R8 des rapports d'audit."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

**Un seul des quatre trous subsiste**, réduit ici le 2026-09-06 ; l'intitulé est conservé tel quel
parce qu'il sert de clé de référence.

**Ce qui reste** — la somme « avant » du contrôle de conservation n'est mesurée nulle part.
L'Étape 0 de `debt-review` ne fait que tester `-eq 0` sur chaque registre (vide ou non), et le seul
comptage des trois listes est à l'Étape 5, c'est-à-dire du côté « après ». Le point de comparaison
doit donc être reconstitué de la conversation.

**Ce qui est tombé** — les trois autres sont devenus **sans objet** avec le passage des registres en
répertoires-listes :

- *quoi faire d'un marqueur déjà présent* — il n'y a plus de marqueur sous un titre. `category` et
  `reviewed` sont des champs de front matter, qu'une revue ultérieure écrase sans avoir à choisir
  entre remplacer et ajouter ;
- *la ligne de tête n'a pas de forme pour une revue sans chantier* — il n'y a plus de ligne de
  tête : un registre est un répertoire, et `dette.md` ne porte plus de section *Tête du registre* ;
- *une clause résiduelle du gabarit* — elle n'existe plus ; aucune occurrence de « marqueur de
  catégorie exclu » ne subsiste dans `skills/` ni dans `.list/`.

Établi par : `grep -n "wc -l" skills/debt-review/SKILL.md` → l'Étape 0 ne compte pas ;
`grep -n "ligne de tête\|Tête du registre\|marqueur déjà" skills/debt-review/SKILL.md
skills/implementation-tracker/references/dette.md` et
`grep -rn "marqueur de catégorie exclu\|recopier l'intitulé" skills/ .claude/implementation/todo/technical-debt/.list/`
→ aucun résultat.

## Pourquoi c'est gênant

Le trou restant se paie à **chaque** revue, pas dans un an : celle du 2026-09-06 a dû reconstituer
sa somme « avant » de la conversation, comme celle du 2026-08-17. Un contrôle de conservation dont
un seul des deux termes est mesuré ne conserve rien — il additionne l'état d'après et le compare à
un souvenir.

## Pour solder

Une correction d'une à trois lignes : ajouter le bloc de comptage des trois registres à l'Étape 0
de `debt-review`, et en reporter le TOTAL au préambule, pour que l'Étape 5 ait un terme de
comparaison écrit plutôt que remémoré.

## Assumé

arbitrés à la clôture. Aucun n'est bloquant, aucun n'a faussé la passe du 2026-08-17.
