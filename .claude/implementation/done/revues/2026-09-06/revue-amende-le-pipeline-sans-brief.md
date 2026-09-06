+++
id = "revue-amende-le-pipeline-sans-brief"
title = "Une revue peut amender les règles du pipeline sans brief, plan ni audit"
date = 2026-08-17
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ sed -n '/Quand l.arbitrage produit une règle/,/Étape 5/p' skills/debt-review/SKILL.md | grep -n "paragraphe\|section neuve\|plafond\|borne"
(aucun résultat)
```
La section « Quand l'arbitrage produit une règle » de l'Étape 4 énumère **où** la règle s'écrit
(`dette.md`, `categories.md`, le `contract.toml`, `SKILL.md`) et **quand** (avant les corrections
qu'elle autorise). Elle ne dit rien de son **ampleur**.

## Verdict

Le constat tient sans réserve. La porte existe toujours et n'a toujours pas de plafond : la même
consigne autorise « ajouter une ligne à un gabarit » et « réécrire la tenue des registres ». Le
`Pour solder` demandait précisément la borne (un paragraphe dans une section existante d'un côté,
section neuve ou script de l'autre) — elle n'est pas écrite. Rien n'a été payé, rien n'est devenu
sans objet, et l'ampleur ne s'est pas étendue de façon chiffrable.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
