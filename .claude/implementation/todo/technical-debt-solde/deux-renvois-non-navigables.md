+++
id = "deux-renvois-non-navigables"
title = "Deux renvois du dépôt ne se suivent pas depuis l'éditeur"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R18 du rapport d'audit et incertitude ouverte au cadrage."
reviewed = 2026-08-17
category = "pertinent"
+++

## Constat

le chantier a rendu navigables les 28 renvois vers le contrat, mais deux références
restent en dehors :

- l'en-tête d'`impl-list.sh` renvoie à `skills/implementation-tracker/references/contrat.md`, chemin
  relatif à la racine du dépôt, alors que le fichier vit dans
  `skills/implementation-tracker/scripts/` — depuis là, la cible est `../references/contrat.md` ;
- `agents/implementation-auditor.md` renvoie en prose à
  `skills/implementation-tracker/references/audit.md`, section « Gabarit du rapport » — seule
  référence non ancrée subsistante.

## Soldé le

**Soldé le 2026-08-24 par le chantier `check-pipeline-python`** — les deux volets :

- l'en-tête d'`impl_list.py` renvoie à `../references/contrat.md`, chemin correct depuis
  `scripts/`, là où le `.sh` écrivait un chemin relatif à la racine du dépôt ;
- le renvoi de `agents/implementation-auditor.md` vers `audit.md` est ancré en
  `#gabarit-du-rapport`.

L'incertitude laissée ouverte au cadrage de `contrat-pipeline` est **tranchée** : ancrer un renvoi
qui existait déjà en prose ne crée aucun couplage nouveau, et le contrôle 4 — qui protège
l'auto-suffisance des agents — ne vise que `contrat.md`.

Établi par : `python3 scripts/check_pipeline.py` → contrôle 4 « 3 agents, aucun renvoi au
contrat », rc 0.

## Pourquoi c'est gênant

la navigabilité des renvois était une contrainte explicite du brief. Ces
deux-là sont exactement ce que le contrôle 1 ne regarde pas : il ne vérifie que les liens vers
`contrat.md`.

## Pour solder

corriger le chemin dans l'en-tête d'`impl-list.sh` ; pour l'agent, trancher entre
ancrer le renvoi (au prix d'une exception au hors-périmètre) et l'assumer définitivement.

## Assumé

la seconde découle du hors-périmètre — les agents ne sont pas rendus dépendants du
noyau. L'incertitude a été ouverte au cadrage et jamais tranchée.
