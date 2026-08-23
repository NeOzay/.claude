+++
id = "quatre-trous-procedure-debt-review"
title = "Quatre trous de procédure de `debt-review` sont connus et non traités"
date = 2026-08-17
source = "Identifié par `revue-dette`, R5 à R8 des rapports d'audit."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

l'audit de clôture les a relevés, la première passe réelle les a tous rencontrés, et
aucun n'a été corrigé :

- **la somme « avant » du contrôle de conservation n'est mesurée nulle part** : l'Étape 0 ne compte
  pas les registres et le préambule ne porte que le compte de `technical-debt.md`. Le point de
  comparaison a dû être reconstitué de la conversation ;
- **rien ne dit quoi faire d'un marqueur déjà présent** quand une entrée est reclassée `aggravee` ou
  `inverifiable` à une revue ultérieure : remplacer la ligne, ou en ajouter une seconde. Trois
  entrées en portent un depuis cette revue ;
- **la ligne de tête n'a pas de forme pour une revue sans chantier** : `dette.md`, § *Tête du
  registre*, impose `(chantier <slug>)`, et une revue n'a pas de slug. Cette passe s'en est tirée
  parce qu'elle **était** un chantier ;
- **une clause résiduelle du gabarit** dit de recopier l'intitulé « marqueur de catégorie exclu s'il
  y en a déjà un », alors que le marqueur vit sous le titre depuis l'amendement du 2026-08-16 et
  qu'aucun intitulé ne peut en porter.

## Pourquoi c'est gênant

les trois premiers se paieront à la **deuxième** revue, pas dans un an :
c'est elle qui rencontrera les marqueurs déjà posés et qui n'aura pas de chantier pour donner un
slug à sa ligne de tête. Un dispositif conçu pour être rejoué périodiquement a ses défauts au
deuxième tour, pas au premier.

## Pour solder

les quatre sont des corrections d'une à trois lignes. Le premier demande le bloc
de comptage à l'Étape 0 avec report du TOTAL au préambule.

## Assumé

arbitrés à la clôture. Aucun n'est bloquant, aucun n'a faussé la passe du 2026-08-17.
