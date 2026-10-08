+++
id = "migrateur-ne-selectionne-que-a-remplir"
title = "`migrateur-de-liste` sélectionne ses entrées par le texte exact `<À REMPLIR>`"
date = 2026-10-08
severite = "majeur"
chantier = "registre-de-dette-severite-chantier-pin"
reference = "R13"
pin = true
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

L'agent `migrateur-de-liste` et la procédure de `technical-debt/migrations/3.md` sélectionnent les
entrées à traiter par `list-dir list <liste> --where '<champ>=<À REMPLIR>'`. `--where` compare le
texte exact : un champ typé au Marqueur (`<À REMPLIR date>`) ou facultatif (`<OPTIONNEL>`) ne sort
pas. La migration de `technical-debt` v3 n'y était pas exposée, ses deux champs étant du texte
requis.

## Pourquoi c'est gênant

La prochaine migration dont un champ neuf est typé ou facultatif fera répondre à l'agent « rien à
traiter », sans erreur : le champ reste au Marqueur, et pour un champ facultatif `validate --filled`
passe quand même.

## Pour solder

La sélection voit tous les Marqueurs d'un champ, typés et facultatifs compris, et un essai sur un
champ typé le montre.

## Assumé

<OPTIONNEL>
