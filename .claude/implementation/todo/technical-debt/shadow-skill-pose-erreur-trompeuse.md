+++
id = "shadow-skill-pose-erreur-trompeuse"
title = "Un Shadow-skill tout juste posé échoue sur un message de type au lieu d'un Marqueur"
date = "2026-10-04"
source = "chantier `shadow-skill`, essai des sous-commandes en session 2"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Après `gabarit new shadow-skill <chemin>`, `shadow-skill liste` et `verifie` rendent « champ « tags
» — une liste de chaînes est attendue ». La Semence pose `tags = "<À REMPLIR>"`, une chaîne dans un
champ de type liste ; le message ne dit pas qu'il reste un Marqueur à remplir.

## Pourquoi c'est gênant

Celui qui pose un Shadow-skill croit à une faute de format, alors qu'il n'a simplement pas encore
rempli le champ.

## Pour solder

Reconnaître un Marqueur dans `_tags` et le signaler comme tel, ou faire poser par la Semence une
liste qui porte le Marqueur.

## Assumé

<OPTIONNEL>
