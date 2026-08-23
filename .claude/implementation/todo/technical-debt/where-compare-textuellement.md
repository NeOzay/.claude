+++
id = "where-compare-textuellement"
title = "`where` compare les valeurs sous forme textuelle, y compris l'absence"
date = 2026-08-23
source = "chantier `format-registres`, R10 des audits de clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`ListStore.where` compare `str(it.fields.get(k)) == str(v)`. Un champ absent vaut donc la chaîne
`"None"`, et `list --where category=None` filtre sur les éléments **qui n'ont pas** de `category`.
Le comportement n'est documenté nulle part.

## Pourquoi c'est gênant

C'est un piège pour qui filtre sur un champ facultatif : `--where category=None` a l'air d'une faute
de frappe et rend pourtant un résultat plausible, ce qui est la pire des deux issues. Un filtre qui
répond quelque chose de faux se croit sur parole, là où un filtre qui échoue se corrige.

La comparaison textuelle elle-même est un choix défendable — elle évite d'avoir à typer la valeur de
la ligne de commande — mais elle n'est écrite nulle part, donc personne ne peut s'y fier ni s'en
méfier.

## Pour solder

Documenter la règle dans `references/contrat-liste.md` (une valeur est comparée à sa forme
textuelle), **et** décider du cas de l'absence : soit `None` devient une valeur réservée qui filtre
explicitement les champs non renseignés, soit la comparaison refuse de matcher un champ absent et
`--where` gagne une forme dédiée.

## Assumé

<OPTIONNEL>
