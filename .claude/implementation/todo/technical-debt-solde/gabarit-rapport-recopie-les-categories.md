+++
id = "gabarit-rapport-recopie-les-categories"
title = "gabarit-rapport.md recopie les sept catégories que le contrat de revue déclare"
date = 2026-08-30
source = "chantier semences-de-listes, hors-périmètre assumé Q2 et audit R7"
+++

## Constat

`skills/debt-review/references/gabarit-rapport.md` énumère les sept catégories de verdict, qui sont
déjà déclarées comme `values` du champ `category` dans
`.list/templates/review.toml` — le contrat de la liste de revue engendrée par `derive`. La même
énumération vit donc à deux endroits, dont l'un est de la prose.

Le chantier `semences-de-listes` a supprimé la duplication jumelle dans
`implementation-tracker/references/dette.md`, où un tableau recopiait les champs et sections du
contrat de dette : le renvoi y passe désormais par `list-dir contract`. Ce cas-ci a été laissé de
côté par arbitrage explicite (Q2 du brief), au motif que ces catégories renvoient à
`categories.md` et décrivent ce que chaque section *attend* — du jugement, pas une structure.

## Pourquoi c'est gênant

L'argument de l'arbitrage tient pour la prose qui explique les catégories, pas pour l'énumération
elle-même : les sept identifiants, eux, sont bien une copie de la liste `values` du contrat. Une
huitième catégorie ajoutée au contrat laisserait `gabarit-rapport.md` en décrire sept, sans qu'aucune
commande échoue — `validate` juge les fiches contre le contrat, jamais la doc contre lui.

C'est exactement le mode de défaillance que le chantier a écrit dans `dette.md` : « une prose qui
décrit un contrat que l'outil n'applique pas », avec la circonstance aggravante qu'on la croit,
parce qu'elle se lit plus vite que le fichier qu'elle décrit.

## Pour solder

Faire pour la liste de revue ce que le chantier a fait pour le registre : remplacer l'énumération
des sept identifiants par un renvoi vers le contrat en vigueur, et ne garder en prose que ce que le
contrat ne porte pas — le sens de chaque catégorie et sa preuve exigée, qui vivent déjà dans
`categories.md`.

Une difficulté à traiter au passage, et c'est elle qui a motivé le report : la liste de revue
n'existe qu'après `derive`, si bien qu'un renvoi à `list-dir contract <revue>` vise une liste qui
n'existe pas encore au moment où le lecteur lit le gabarit. Le renvoi doit donc viser le gabarit
source — `.list/templates/review.toml` de `technical-debt` — et non la liste dérivée.

## Assumé

Le report lui-même est assumé : l'arbitrage Q2 a jugé que ce cas ne valait pas d'élargir le
périmètre du chantier, et cette entrée existe pour qu'il ne disparaisse pas avec lui.

## Soldé le

**2026-08-30, chantier `renvoi-contrat-des-categories`** — `list-dir contract` sait désormais viser
une définition (`--def`/`--from`), un de ses gabarits (`--template`) et les valeurs déclarées d'un
champ (`--values`). `gabarit-rapport.md` renvoie à la commande au lieu d'énumérer, et la boucle des
piles de `debt-review/SKILL.md` tire sa liste du contrat.

Établi par :

```
$ list-dir contract --def technical-debt --template review --values category
a-solder
non-pertinent
doublon
pas-une-dette
aggravee
pertinent
inverifiable

$ grep -rn "sept" skills/debt-review/ ; echo "code=$?"
code=1

$ grep -rn "a-solder non-pertinent" skills/debt-review/ ; echo "code=$?"
code=1
```

La difficulté qui avait motivé le report est levée par `--template` : le renvoi vise le gabarit
source de la définition `technical-debt`, et non la liste dérivée, qui n'existe qu'après `derive`.

Reste hors de ce solde, porté au registre sous
`sections-de-categories-jamais-confrontees-au-contrat` : les titres de section de `categories.md`
restent une copie de l'ensemble des `values`, qu'aucune commande ne confronte au contrat.
