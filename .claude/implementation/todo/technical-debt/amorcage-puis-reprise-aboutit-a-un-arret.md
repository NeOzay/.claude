+++
id = "amorcage-puis-reprise-aboutit-a-un-arret"
title = "« Amorcer puis reprendre l'étape » aboutit toujours à un arrêt, sans que la puce le dise"
date = 2026-08-30
source = "chantier semences-de-listes, audit R16"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`skills/debt-review/SKILL.md`, Étape 0, puce « `ABSENT` sur les trois » : elle prescrit d'amorcer
les registres puis de reprendre l'étape. Vérifié à l'exécution — après l'amorçage, le bloc rend
`VIDE` sur les trois, que la puce suivante route vers « le dire et s'arrêter ».

Le résultat est juste : un projet qui vient de créer ses registres n'a rien à instruire. Mais
l'enchaînement « amorcer, puis reprendre l'étape » laisse attendre une reprise qui **continue**,
alors qu'elle s'arrête.

## Pourquoi c'est gênant

Le lecteur qui suit la consigne et voit la revue s'arrêter juste après avoir amorcé cherchera une
erreur là où il n'y en a pas. Au mieux il perd du temps ; au pire il conclut que l'amorçage a
échoué et le recommence, ce que `init` refusera avec « contrat déjà présent » — un second message
d'erreur pour une situation parfaitement normale.

## Pour solder

Une demi-phrase à la fin de la puce : la reprise dira `VIDE`, et c'est la fin normale d'un premier
passage. Prose seule, aucun code en cause.
