+++
id = "suivi-pose-depuis-un-gabarit-markdown"
title = "`implementation-tracker` pose son suivi depuis un gabarit Markdown alors que la semence `suivi` existe"
date = 2026-09-18
source = "chantier `skill-convention`, étape 9 — constat noté au journal du suivi"
+++

## Constat

`implementation-tracker` renvoie à `references/gabarit-suivi.md`, un modèle Markdown que le modèle
recopie et remplit à la main. La skill `gabarit` porte pourtant une semence `suivi`
(`skills/gabarit/gabarit/suivi/contract.toml`) faite pour ce fichier, et `gabarit check` sait le
confronter au contrat.

La convention « Un document structuré se pose depuis un gabarit » écrite par ce chantier
(`skills/skill-convention/references/prose.md`) n'est donc pas pratiquée par le tracker lui-même.

## Pourquoi c'est gênant

La structure du suivi est écrite à deux endroits — le modèle Markdown et le contrat de la semence —
et rien ne les confronte : elles divergeront. Un suivi recopié à la main n'est par ailleurs vérifié
par rien, alors que `gabarit check` rendrait le verdict.

## Pour solder

Faire poser le fichier de suivi par `gabarit new suivi`, puis `gabarit check` à la fin de l'Étape 2
d'`implementation-tracker` ; ne garder `references/gabarit-suivi.md` que si la semence ne couvre pas
tout, et dire alors laquelle des deux fait foi.
