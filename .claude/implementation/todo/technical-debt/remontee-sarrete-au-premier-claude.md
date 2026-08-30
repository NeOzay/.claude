+++
id = "remontee-sarrete-au-premier-claude"
title = "La racine de projet retenue par list-dir est le premier .claude trouvé, pas forcément le bon"
date = 2026-08-30
source = "chantier semences-de-listes, incertitude Q3 du brief et audit R8"
+++

## Constat

`definitions.py:project_root` remonte les parents du répertoire courant jusqu'au **premier**
répertoire contenant un `.claude/`, et s'arrête là. Dans un dépôt imbriqué dans un autre, ou lancé
depuis un sous-projet, ce premier `.claude` n'est pas nécessairement celui que l'utilisateur avait
en tête : les rangs 1 et 2 des définitions viseront alors une racine surprenante.

Le comportement a été retenu sciemment à l'arbitrage du brief (question Q3), contre deux
alternatives : `git rev-parse --show-toplevel`, qui ajoutait une dépendance à `git` pour `init`, et
`cwd/.claude` seul, qui échouait dès qu'on appelait depuis un sous-répertoire.

Rien ne le borne aujourd'hui. La seule atténuation est que `list-dir defs` **imprime** la racine
retenue, ce qui rend le choix visible pour qui pense à regarder.

## Pourquoi c'est gênant

L'effet est silencieux et du bon côté de la vraisemblance : la commande réussit, amorce une liste,
et c'est le contrat d'un autre projet qui a servi. Rien n'échoue, et le contrat obtenu ressemble
assez à celui attendu pour ne pas alerter.

## Pour solder

Décider si la règle doit être bornée, et par quoi :

- un **marqueur explicite** dans le `.claude/` d'un projet, que la remontée cherche en priorité ;
- ou la racine du dépôt git, en déclarant `git` dans les `REQUIRES` de la commande concernée — ce
  que le paquet sait faire proprement, `move` le fait déjà ;
- ou rien, et alors l'écrire comme une limite assumée dans `contrat-liste.md`, plutôt que de la
  laisser se découvrir.

## Assumé

L'arbitrage Q3 a explicitement laissé ce point ouvert, en choisissant de le rendre **visible**
plutôt que de le trancher. Cette entrée existe pour que la décision reste réversible.
