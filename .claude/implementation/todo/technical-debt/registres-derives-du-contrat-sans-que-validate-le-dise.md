+++
id = "registres-derives-du-contrat-sans-que-validate-le-dise"
title = "Trois registres ont dérivé de leur contrat sans que `validate` en dise un mot"
date = 2026-09-20
source = "chantier `deux-sens-de-gabarit`, constaté à l'étape 5 en cherchant à poser une section « Soldé le »"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`list-dir validate` déclare conformes les six listes de `.claude/implementation/todo/`, quand
`list-dir migrate --dry-run` annonce **50 changements** sur trois d'entre elles :

```
technical-debt        29 changements        technical-debt-ecarte   déjà conforme
technical-debt-solde  18 changements        road-map                déjà conforme
road-map-fait          3 changements        road-map-ecarte         déjà conforme
```

Deux natures de dérive s'y mêlent : des **sections désordonnées** par rapport à l'ordre du contrat,
et des **champs déclarés purement absents** du front matter — `reviewed` et `category` sur plusieurs
entrées de `technical-debt-solde`, par exemple.

Établi par : `list-dir migrate <liste> --dry-run` sur les six listes, et `list-dir validate` sur les
mêmes, le 2026-09-20 → 50 changements annoncés d'un côté, six fois « conformes au contrat » de
l'autre.

## Pourquoi c'est gênant

Un champ absent n'est pas un champ facultatif laissé à `<OPTIONNEL>` : le format le dit lui-même —
« un champ absent et un champ à remplir sont deux états différents ». Or `validate` ne distingue pas
les deux à la lecture, et une liste peut donc s'éloigner de son contrat indéfiniment sous un rc=0.

Le coût se paie quand on croise les deux outils. Ce chantier l'a rencontré : poser une section
« Soldé le » sur deux entrées par `migrate` aurait entraîné 18 changements sur huit entrées
étrangères au chantier, noyant la preuve du solde. La section a donc été posée à la main — une
opération mécanique faite par le modèle, exactement ce que le partage des rôles proscrit.

## Pour solder

Trancher ce que `validate` doit dire d'un champ déclaré mais absent : le signaler comme un
manquement, ou l'annoncer sur stderr comme il annonce déjà une liste périmée — sans changer son
code de retour, une liste désordonnée n'ayant aucun élément fautif.

Puis rattraper les trois listes par `list-dir migrate`, dans un commit à elles seules, pour que
l'écart ne se mêle à aucun autre diff.

Vérifier : `for l in technical-debt technical-debt-solde road-map-fait; do list-dir migrate
".claude/implementation/todo/$l" --dry-run; done` → « déjà conforme au contrat » pour les trois.

## Assumé

Non traité par le chantier `deux-sens-de-gabarit` : la dérive lui est antérieure et étrangère, et
la rattraper aurait mêlé 50 changements sans rapport au diff d'un chantier de vocabulaire.
