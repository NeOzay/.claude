+++
id = "contrat-auditeur-racine-depot"
title = "Le contrat de l'auditeur et celui de l'appelant divergent sur la racine du dépôt"
date = 2026-08-14
source = "Identifié par `audit-integre`, R6 du rapport d'audit."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/implementation-tracker/references/audit.md:43-45` range la racine du dépôt
parmi ce que l'appelant **transmet** à l'agent ; `agents/implementation-auditor.md:21-23` énumère ce
que l'appelant fournit sans la mentionner, l'agent la calculant lui-même juste après
(`git rev-parse --show-toplevel`). Les deux documents décrivent une entrée différente.

## Soldé le

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — la règle est définie une seule fois,
dans `contrat.md`, section « Contrat des sous-agents » : « l'appelant peut la donner, sinon l'agent
la calcule ». `audit.md` renvoie à cette section au lieu d'énumérer une liste divergente, et l'agent
porte la même formulation.
Établi par : `grep -n -A1 "peut te la" agents/implementation-auditor.md` → l. 26-27, « **L'appelant
peut te la donner ; sinon, calcule-la** » ; et `grep -n "Contrat des sous-agents" …/references/audit.md`
→ l. 42, renvoi ancré au lieu de la liste.

## Pourquoi c'est gênant

c'est exactement le type d'écart inter-fichiers qui avait produit R3 du
même rapport, lequel avait, lui, un mode de défaillance réel (rapport écrit à côté).

## Pour solder

une phrase dans `implementation-auditor.md` : « l'appelant peut te la donner ;
sinon, calcule-la ».

## Assumé

sans mode de défaillance connu — l'agent est autonome, et une entrée surnuméraire ne le
gêne pas.
