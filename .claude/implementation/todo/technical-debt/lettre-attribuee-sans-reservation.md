+++
id = "lettre-attribuee-sans-reservation"
title = "La lettre d'un chantier n'est réservée que par son tag E0, jamais exercé en conditions réelles"
date = 2026-09-14
source = "chantier `git-smart-commit-trois-commits`, R10 du rapport d'audit"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`commit-chantier lettre` rend la première lettre de A à Z sans tag d'étape `<L>E<n>` dans le dépôt.
La lettre n'est donc réservée qu'à la pose du tag `<L>E0`, au commit de l'état initial
(`implementation-tracker` Étape 2, point 8). Deux chantiers créés avant que l'un d'eux ait posé son
`E0` reçoivent la même lettre. `etape.md` (« Si le tag existe déjà, git refuse ») arrête le second,
mais après son commit.

Au 2026-09-15, ni la commande `lettre` ni le commit `E0` n'ont servi à un chantier réel : le seul
usage du type 2 est celui des étapes 7 et 8 de `git-smart-commit-trois-commits` (tags `AE7`, `AE8`),
un chantier né sous l'ancienne procédure et sans `AE0`.

## Pourquoi c'est gênant

Une collision produit un commit d'étape sans tag, puis des plages `<L>E<n>` mêlant deux chantiers,
et une clôture qui supprime les tags de l'autre (`git tag -d` des tags de sa lettre). Le chemin
n'ayant jamais été exercé, rien ne dit que la séquence du point 8 tient en pratique.

## Pour solder

Réserver la lettre à l'attribution (écriture dans `lettre:` suivie d'un contrôle d'unicité parmi les
suivis actifs, ou tag posé par `lettre` lui-même), puis mener un chantier neuf de bout en bout par le
type 2 — `lettre`, `E0`, commits d'étape, clôture — et le constater.
