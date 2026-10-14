+++
id = "test-fill-ecrit-sans-encodage"
title = "Un test de `test_fill.py` écrit un élément sans `encoding=\"utf-8\"`"
date = 2026-10-14
severite = "note"
chantier = "list-dir-fill-override"
reference = "R3"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le 2026-10-14, `test_override_refuse_sans_rien_ecrire`, dans
`skills/list-dir/scripts/tests/test_fill.py`, crée l'élément `c` par `write_text` sans
`encoding="utf-8"`, là où les autres écritures du fichier le disent. Relevé à l'audit
`01-3ec5803`.

## Pourquoi c'est gênant

L'élément écrit ne porte que de l'ASCII : aucun test ne casse, sous Linux comme ailleurs. Une
modification de son contenu vers un caractère accentué ferait dépendre le test de la locale de la
machine.

## Pour solder

Ajouter `encoding="utf-8"` à l'appel de `write_text` de `c.md` dans
`test_override_refuse_sans_rien_ecrire`.

## Assumé

<OPTIONNEL>
