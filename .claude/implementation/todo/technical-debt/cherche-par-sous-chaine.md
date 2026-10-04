+++
id = "cherche-par-sous-chaine"
title = "`shadow-skill cherche` compare des sous-chaînes, sans frontière de mot"
date = "2026-10-04"
source = "chantier `shadow-skill`, essai des sous-commandes en session 2"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`shadow-skill cherche` retient un skill dès que le mot figure comme sous-chaîne de son nom, de sa description, de son `when-to-load` ou de ses tags. Le 2026-10-04, `cherche skill` rendait `nvim-mini-test`, à cause de « This skill covers… ».

## Pourquoi c'est gênant

Le bruit croît avec le nombre de Shadow-skills : un mot court ou courant (« test », « lua ») ramène des skills sans rapport, et l'agent charge pour rien ou lit trop de lignes avant de choisir.

## Pour solder

Comparer mot à mot (frontières de mot, éventuellement préfixe), avec un test qui fixe le cas « skill » contre « This skill ».

## Assumé

<OPTIONNEL>
