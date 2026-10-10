+++
id = "lexique-des-sous-agents-lie-a-agent-spawn"
title = "Le lexique d'un sous-agent passe par `agent.spawn`, une API de mod récente"
date = 2026-10-05
severite = "inconnue"
chantier = "lexique-des-sous-agents"
reference = "R10"
pin = false
source = "chantier `lexique-des-sous-agents`, audit de clôture du 2026-10-05, R10"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le mod réécrit le `prompt` du sous-agent à l'événement `agent.spawn`. `classic.SubagentStart` ne
convient pas : `$.session.append` y est refusé, la boucle du sous-agent n'existant pas encore. Le
lexique arrive donc dans le premier message, sous un en-tête, et non dans un contexte système.

## Pourquoi c'est gênant

Le mécanisme dépend d'une API de mod apparue dans la build 2.1.289 : une version qui la change casse
la livraison du lexique aux sous-agents, et seul le résultat le montre. Le harnais
`claude plugin test` ne rend pas d'implémentation de `session.append`, ce qui limite aussi les
essais.

## Pour solder

Rejouer la vérification réelle (les trois agents de test dans un dépôt à lexique local) après chaque
montée de version de Claude Code, ou passer à un événement qui verse du contexte système si l'API en
offre un.

## Assumé

<OPTIONNEL>
