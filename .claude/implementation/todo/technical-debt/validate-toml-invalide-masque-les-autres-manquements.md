+++
id = "validate-toml-invalide-masque-les-autres-manquements"
title = "`list-dir validate` ne rapporte qu'un front matter TOML invalide, et tait les manquements des autres éléments"
date = 2026-10-08
severite = "avertissement"
chantier = "registre-de-dette-severite-chantier-pin"
reference = "journal du Suivi"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le 2026-10-08, sur le registre de dette, un élément portait `pin = pin`.
`list-dir validate --filled` n'a rapporté que « front matter TOML invalide » sur cet élément. Une
fois le TOML corrigé sur une copie, il a rapporté cinq autres manquements (`severite` hors des
valeurs déclarées), dont quatre sur d'autres éléments.

## Pourquoi c'est gênant

Qui corrige ce que `validate` rapporte croit la liste réparée et découvre d'autres erreurs au
passage suivant. Le compte rendu ne dit pas qu'il est partiel.

## Pour solder

Un élément illisible est rapporté comme tel, et `validate` continue sur les autres : les manquements
de tous les éléments lisibles sortent au même passage.

## Assumé

<OPTIONNEL>
