+++
id = "verdict-d-audit-restitue-puis-attendu"
title = "Après le verdict de l'audit de Clôture, restituer et attendre l'utilisateur, même FAVORABLE"
date = 2026-10-11
source = "Clôture du chantier refonte-de-l-audit, demande de l'utilisateur"
+++

## À faire

Après le verdict d'un audit, l'orchestrateur restitue le résultat à l'utilisateur et attend sa
réponse, quel que soit le verdict. Aujourd'hui, `FAVORABLE` enchaîne sur la Clôture sans demander :
à la Clôture de `refonte-de-l-audit`, la dette a été versée au Registre et l'entrée de road-map
sortie avant que l'utilisateur ait vu le verdict. Le tableau des suites devient : restituer, puis
attendre la décision de l'utilisateur ; la Clôture ne commence que sur sa réponse.

## Références

- `skills/implementation-tracker/references/audit.md`, « Au retour », tableau `Verdict | Suite`,
  ligne `FAVORABLE` : « La clôture continue. »
- `skills/implementation-tracker/references/cloture.md`, « 1. Audit — obligatoire, et bloquant »,
  qui ne s'arrête que « sans avis favorable »
- chantier `refonte-de-l-audit`, audit `02-ef2b907`, archivé en `done/`
