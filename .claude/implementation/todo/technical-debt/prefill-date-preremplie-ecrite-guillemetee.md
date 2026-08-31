+++
id = "prefill-date-preremplie-ecrite-guillemetee"
title = "Un champ date prérempli est écrit entre guillemets, contre la forme nue des dates saisies"
date = 2026-08-31
source = "chantier 2026-08-31-champs-preremplis, audit de clôture R5"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`listdir/prefill.py` rend une chaîne ; `dump_value` (`listdir/items.py`) écrit donc
`jour = "2026-08-31"` avec guillemets, là où il rend `2026-08-31` nu pour un `datetime.date`.

Une même liste porte deux graphies du même champ selon l'origine de la valeur — sur le cas porteur
du chantier, `command = "date +%F"`.

## Pourquoi c'est gênant

Les deux formes sont valides pour `check_value`, qui accepte `str` comme `datetime.date` : rien
n'échoue, et c'est bien le problème. Un `grep '^date = 2026'` sur une liste en attrape la moitié.
L'incohérence est invisible tant qu'on ne compare pas deux éléments d'origines différentes.

## Pour solder

Convertir la sortie en `datetime.date` dans `initial_field` quand le champ est de type `date`, une
fois `check_value` passé. Le même raisonnement vaudrait pour un futur type numérique.

## Assumé

<OPTIONNEL>
