+++
id = "amorcage-gabarit-en-trois-exemplaires"
title = "Le bloc qui trouve le paquet gabarit et relance dans le venv existe en trois exemplaires"
date = "2026-10-04"
source = "chantier `shadow-skill`, audit de clôture, constat R5"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

La découverte du paquet gabarit par `bin/gabarit`, en tête de
`skills/shadow-skill/scripts/shadow_skill.py`, et la ré-exécution dans le venv de
`shadow-skill-cli.py` copient `skills/list-dir/scripts/listdir/__init__.py` et les points d'entrée
de list-dir et gabarit. Les commentaires renvoient à l'original ; le Plan du Chantier l'a voulu
ainsi.

## Pourquoi c'est gênant

Au prochain changement de résolution du venv ou de `bin/`, il faudra modifier les trois copies
ensemble. Une copie oubliée ne casse qu'à l'exécution de son skill, dans l'environnement où la
résolution diffère.

## Pour solder

Extraire l'amorçage en un module partagé que les trois skills importent, ou ajouter à
`check_pipeline.py` un contrôle qui compare les trois blocs.

## Assumé

Le Plan a préféré la copie au partage : chaque skill reste déployable seule.
