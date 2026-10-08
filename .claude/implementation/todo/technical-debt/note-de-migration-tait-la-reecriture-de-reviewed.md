+++
id = "note-de-migration-tait-la-reecriture-de-reviewed"
title = "La note de migration du registre ne dit pas que `migrate` réécrit le Marqueur de `reviewed`"
date = 2026-10-08
severite = "note"
chantier = "registre-de-dette-severite-chantier-pin"
reference = "R9"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`technical-debt/migrations/3.md` dit que `migrate` pose au Marqueur les champs et sections
facultatifs absents et réordonne les sections. Il ne dit pas qu'il réécrit aussi
`reviewed = "<OPTIONNEL>"` en `"<OPTIONNEL date>"` : 39 entrées de `technical-debt`, 22 de `-solde`
et 2 de `-ecarte` l'ont été à la migration.

## Pourquoi c'est gênant

Qui lit le diff de `migrate` dans un autre projet y trouve une ligne que la note n'annonce pas, et
doit établir seul qu'elle est sans effet sur le contenu.

## Pour solder

La note nomme la réécriture des anciens Marqueurs génériques en leur forme typée.

## Assumé

<OPTIONNEL>
