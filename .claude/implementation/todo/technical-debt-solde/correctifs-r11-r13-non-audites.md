+++
id = "correctifs-r11-r13-non-audites"
title = "Les correctifs R11 et R13 de `revue-dette` n'ont jamais été audités"
date = 2026-08-17
source = "Identifié par `revue-dette`, décision de clôture ; soldé le jour même, R18 du troisième audit."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

le chantier s'est clos sur le verdict `RÉSERVES` de `69fd11c`. L'étape 12, qui ouvre
dans le skill le chemin d'écriture d'une règle issue d'un arbitrage et borne la validation de date
de `trier-revue.sh`, a été écrite **après** cet audit et n'a été jugée par personne.

## Soldé le

**Soldé le 2026-08-17 par un troisième audit, demandé avant l'aplatissement** — le *Pour solder*
disait « auditer le diff de l'étape 12 ». C'est fait : `implementation-auditor` a jugé le delta
`69fd11c..be0eadf` et rendu `RÉSERVES`, aucun bloquant, les quatre vérifications de l'étape 12
reproduites par ses propres commandes.
Établi par : `grep -n '^## 2026-08-17' .claude/implementation/revue-dette.audit.md` → trois
sections, la dernière `## 2026-08-17 — clôture (2ᵉ passe) — be0eadf`, qui juge précisément le diff
de l'étape 12.

## Pourquoi c'est gênant

R11 touche la procédure d'arbitrage, c'est-à-dire l'endroit exact où le
skill décide ce qu'il a le droit d'écrire hors du registre. Un défaut y est silencieux par
construction : il ne se manifeste qu'à la revue suivante, devant un arbitrage qu'elle refusera ou
qu'elle écrira au mauvais endroit. C'est le troisième chantier de ce dépôt à se clore ainsi.

## Pour solder

auditer le diff de l'étape 12, ou constater à la deuxième revue réelle qu'un
arbitrage produisant une règle suit bien le chemin écrit à l'Étape 3, et que l'Étape 5 ne le signale
plus comme une violation.

## Assumé

décision explicite de l'utilisateur — deux audits successifs, aucun bloquant, et R11
comme R13 sont des corrections dont la vérification est mécanique et a été exécutée.
