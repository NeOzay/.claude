+++
id = "version-de-gabarit-comparee-a-rien"
title = "La version d'un gabarit n'est comparée à rien, faute de liste qui la suive"
date = 2026-09-05
source = "chantier provenance-listes-derivees, audit R5 — hors-périmètre assumé au brief"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Depuis le chantier `provenance-listes-derivees`, un gabarit déclare sa propre estampille
(`templates/review.toml`, `[origin] def = "technical-debt/review"`, `version`, `frozen = true`) et
`derive` la recopie dans la liste engendrée. Cette `version` n'est **jamais confrontée à quoi que
ce soit** : `contrat-liste.md` le dit en toutes lettres — « la version d'un gabarit ne se compare à
rien ». Deux chemins la ferment, et ils se recouvrent : le gel déclaré par le gabarit fait sortir
`warnings()` avant tout contrôle, et `_peremption` refuse par ailleurs de résoudre un nom composite
dans les quatre rangs.

Conséquence observable : corriger `review.toml` puis relancer `list-dir validate` sur une liste de
revue déjà dérivée ne produit **aucun** avertissement, quel que soit l'écart de version.

## Pourquoi c'est gênant

Le champ `version` d'un gabarit est aujourd'hui décoratif : on peut l'oublier, le laisser à 1
indéfiniment ou le faire reculer sans qu'aucune commande ne le remarque. C'est un invariant que
rien ne tient, et un lecteur qui le voit peut légitimement croire qu'il sert — l'erreur coûteuse
étant de s'y fier pour dater un gabarit.

Le coût reste théorique tant que les listes dérivées sont jetables : une revue de dette vit une
journée. Il devient réel le jour où un gabarit sème une liste qu'on garde — la filiation serait
alors dite mais toujours pas suivie, et rien ne signalerait que la liste a décroché.

## Pour solder

Deux issues, exclusives :

- soit retirer `version` de l'estampille d'un gabarit, puisque rien ne la lit — ce qui suppose
  d'assouplir `_origin`, qui l'exige aujourd'hui dès que `def` est un nom ;
- soit la faire suivre : sur une liste dérivée non gelée, résoudre la définition-mère, lire le
  `templates/<nom>.toml` et comparer, comme `_peremption` le fait déjà pour une définition.

## Assumé

Le report est délibéré et daté du 2026-09-05. Le brief du chantier écartait explicitement toute
commande qui suivrait l'estampille, et posait `frozen = true` comme norme d'une liste dérivée :
suivre la version d'un gabarit n'aurait servi aucun consommateur existant. La dette est notée pour
que le coût soit su le jour où une liste dérivée durable apparaîtra, pas pour être contestée.
