+++
id = "dates-entre-guillemets-acceptees"
title = "Une date écrite entre guillemets passe `list-dir validate`"
date = 2026-10-04
source = "hors chantier, à l'adoption de rumdl (2026-10-04), sur l'entrée `suivis-archives-sans-champ-skills`"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Un champ de type `date` s'écrit sous deux formes dans les Registres, et toutes deux sont valides :
`date = 2026-10-04`, une date TOML, et `date = "2026-10-04"`, une chaîne. Le contrôle de type de
`gabarit`, que `list-dir` emploie, accepte les deux : dans `gabarit/contract.py`, la branche
`case "date"` de la vérification d'une valeur rend conforme une chaîne qui se lit comme une date
ISO.

`prefill.py` connaît pourtant le problème. Son commentaire « UNE DATE SE POSE NUE » convertit en
date TOML une valeur que le préremplissage obtient sous forme de chaîne. Mais il ne couvre que ce
cas. Une entrée remplie à la main, ou par le modèle, garde ses guillemets. `list-dir new` pose en
effet `date = "<À REMPLIR>"` : le Marqueur est une chaîne, et le remplacer par la date en laissant
les guillemets en place donne la forme fautive.

Établi par, le 2026-10-04 :

```
$ git grep -lE '^[a-z_-]+ = "[0-9]{4}-[0-9]{2}-[0-9]{2}"$' -- .claude/implementation/todo | wc -l
16                       (15 dans technical-debt/, 1 dans technical-debt-solde/)

$ list-dir validate .claude/implementation/todo/technical-debt
.claude/implementation/todo/technical-debt : 81 élément(s) conformes au contrat
```

rumdl ne voit pas cet écart non plus : il ne lit pas le front matter.

## Pourquoi c'est gênant

C'est le mode de défaillance que le commentaire de `prefill.py` décrit : une même liste porte deux
écritures du même champ, rien n'échoue, et `grep '^date = 2026'` n'attrape que les entrées sans
guillemets. Un tri ou un filtre écrit contre l'une des deux formes manque l'autre en silence.

L'écart ne fait que croître. Les 16 entrées concernées sont toutes récentes : chaque entrée remplie
depuis un Marqueur peut en ajouter une, et aucune commande ne le signale.

## Pour solder

Faire refuser par `check_value` une date écrite comme chaîne, sauf un Marqueur, avec un message qui
dit la forme attendue (« une date s'écrit sans guillemets : 2026-10-04 »). Puis retirer les
guillemets des 16 entrées, et vérifier que les tests de `gabarit` et de `list-dir` passent toujours.

Solde établi par la commande `git grep` du Constat, qui ne rend plus aucune ligne, et par
`list-dir validate`, qui refuse une entrée de test portant `date = "2026-10-04"`.

Le changement touche la bibliothèque que `list-dir` importe : c'est un Chantier, avec son Brief.

## Assumé

<OPTIONNEL>
