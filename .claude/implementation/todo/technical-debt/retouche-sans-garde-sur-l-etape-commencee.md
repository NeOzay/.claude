+++
id = "retouche-sans-garde-sur-l-etape-commencee"
title = "`commit-chantier retouche` ne voit pas qu'une Étape suivante a commencé"
date = 2026-10-05
source = "chantier `retouches-et-modele-du-chantier`, audit de clôture, constat R7"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Une Retouche de l'Étape N n'en est une que tant que l'Étape N+1 n'a pas commencé, c'est-à-dire
n'est pas passée en `[>]` au Suivi. `commit-chantier retouche <L> <n>` ne lit pas le Suivi : il ne
refuse que si le tag `<L>E<n>` manque ou si `<L>E<n+1>` existe. Entre le passage de N+1 en `[>]`
et son commit d'Étape, le script rend donc un tag `<L>E<n>.<k>` pour un travail qui appartient à
N+1. La règle ne tient que par la prose de `etape.md` et d'`execution.md`.

Établi par : dans un dépôt jouet sans Suivi, tagué `AE0` et `AE1`, `commit-chantier retouche A 1`
→ `AE1.1`, sortie 0 (2026-10-05) : le script conclut sans rien savoir de l'état de l'Étape 2.

## Pourquoi c'est gênant

Un commit de l'Étape N+1 en cours, pris par erreur comme Retouche de N, reçoit un tag `<L>E<n>.<k>`
que rien ne refuse. Les plages de `tags-etape.md` deviennent fausses : `AE<n>.<dernier k>..AE<n+1>`
ne contient plus toute l'Étape N+1, et `AE<n>..AE<n>.<dernier k>` y mêle son début. Un tag n'étant
jamais déplacé, l'erreur reste jusqu'à la clôture.

## Pour solder

Faire lire au script l'état de l'Étape N+1 au Suivi (`[>]` → refus), au prix du chargement de la
bibliothèque `fiche` que seule la clôture fait aujourd'hui ; ou faire passer cette vérification à
l'appelant dans la procédure de `etape.md`, cas Retouche. Solde établi par un test de
`test_commit_chantier.py` où une Étape N+1 en `[>]` fait refuser `retouche`.

## Assumé

Le Plan du Chantier `retouches-et-modele-du-chantier` a voulu un script qui ne lit pas le Suivi,
comme `lettre`, pour qu'il tourne sans bibliothèque.
