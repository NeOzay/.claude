+++
id = "cherche-par-sous-chaine"
title = "`shadow-skill cherche` compare des sous-chaînes, sans frontière de mot"
date = "2026-10-04"
severite = "note"
chantier = "shadow-skill"
reference = "Non précisée"
pin = true
source = "chantier `shadow-skill`, essai des sous-commandes en session 2"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`shadow-skill cherche` retient un skill dès que le mot figure comme sous-chaîne de son nom, de sa
description, de son `when-to-load` ou de ses tags. Le 2026-10-04, `cherche skill` rendait
`nvim-mini-test`, à cause de « This skill covers… ».

## Pourquoi c'est gênant

Le bruit croît avec le nombre de Shadow-skills : un mot court ou courant (« test », « lua ») ramène
des skills sans rapport, et l'agent charge pour rien ou lit trop de lignes avant de choisir.

## Pour solder

Comparer mot à mot (frontières de mot, éventuellement préfixe), avec un test qui fixe le cas « skill
» contre « This skill ».

## Assumé

<OPTIONNEL>

## Soldé le

**2026-10-15, chantier `solder-sept-dettes`** — `shadow-skill cherche` compare en début de mot : «
skill » trouve « This skill », « kill » ne le trouve plus.

Établi par :
`~/.claude/.venv/bin/python -m pytest skills/shadow-skill/scripts/tests/test_lire.py -k debut_de_mot`
→ `1 passed`, en échec sur l'ancien code. Sur les Shadow-skills réels, `shadow-skill cherche kill`
rendait `nvim-mini-test` et `skill-convention` ; il sort en 1, sans résultat.
