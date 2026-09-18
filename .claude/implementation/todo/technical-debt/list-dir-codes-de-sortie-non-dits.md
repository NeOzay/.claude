+++
id = "list-dir-codes-de-sortie-non-dits"
title = "Le SKILL.md de list-dir n'énonce pas ses codes de sortie"
date = "2026-09-17"
source = "chantier `skill-convention`, confrontation des skills à `references/prose.md`"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/skill-convention/references/prose.md`, section « Les codes de sortie sont dits », énonce
qu'une commande documente ses codes : 0 succès, 1 refus ou échec, 2 erreur d'appel, avertissement
sur stderr sans changement de code.

`skills/gabarit/SKILL.md` les donne en une ligne. `skills/list-dir/SKILL.md` ne les donne nulle
part : il énonce « Échec fermé : sortie non nulle et message nommant la cause » (ligne 115) et
mentionne un avertissement sur stderr sans changer le code de retour (ligne 80), mais **le code 2
n'y figure pas**, et aucune ligne ne récapitule les trois. Les treize commandes du skill rendent
pourtant les mêmes codes que `gabarit`, dont le paquet porte la CLI.

## Pourquoi c'est gênant

Un appelant qui ne connaît pas les codes lit la sortie pour décider, et une sortie vide sous un
code 0 se lit comme un succès. `list-dir` est le skill le plus appelé depuis d'autres skills — le
registre de dette, la road-map, la revue —, et c'est précisément là que la distinction entre « refus »
(1) et « erreur d'appel » (2) change la conduite à tenir : la première se corrige dans le contenu,
la seconde dans la commande.

## Pour solder

Ajouter à `skills/list-dir/SKILL.md` la ligne de codes de sortie, sur le modèle de celle de
`skills/gabarit/SKILL.md`, et vérifier qu'elle décrit bien ce que rendent les commandes.

## Assumé

<OPTIONNEL>
