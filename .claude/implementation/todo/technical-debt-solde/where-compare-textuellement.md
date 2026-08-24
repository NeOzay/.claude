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

## Soldé le

**2026-08-24, chantier `tests-listdir`** — la comparaison reste textuelle, ce qui est voulu et
désormais écrit dans la docstring de `ListStore.where` : un critère doit fonctionner sans que
l'appelant connaisse le type déclaré. Ce qui est corrigé est l'accident : un champ absent ne vaut
plus la chaîne `"None"`. La forme explicite de l'absence est le **critère vide**. Le fondement est
énoncé dans `_correspond` — TOML n'a pas de valeur nulle, donc un `None` lu signifie toujours
« champ non écrit », jamais « vaut None ».

Établi par :

```
$ uvx pytest skills/list-dir/scripts/tests/test_store_lecture.py -q \
      -k "chaine_none or critere_vide"
2 passed, 28 deselected                                           code 0
```

Les deux cas sont « un champ absent ne vaut pas la chaîne none » — un élément sans `category` et un
élément dont `category` vaut littéralement `"None"`, seul le second remontant sur
`where(category="None")` — et « le critère vide sélectionne les champs absents ».

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
