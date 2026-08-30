+++
id = "correctifs-etape-9-non-audites"
title = "Les correctifs de l'étape 9 de `dette-technique` n'ont jamais été audités"
date = 2026-08-14
source = "Identifié par `dette-technique`, R8 à R11 du rapport d'audit."
reviewed = 2026-08-17
category = "inverifiable"
+++

## Constat

le chantier `dette-technique` s'est clos sur le verdict `RÉSERVES` de `343f180`. Ses
quatre derniers correctifs (R8 lecture du rapport entier, R9 chemin d'écriture de l'abandon dans le
cas *garder la branche*, R10 note périmée, R11 mise en forme) ont été écrits **après** cet audit et
n'ont été jugés par personne. `references/audit.md` demandait de « relancer un audit complet » ; il
n'a pas eu lieu.

## Écartée le

**2026-08-30 — non pertinent** — l'audit que **Pour solder** demandait est devenu impossible, et sa
voie alternative a été prise. Le diff `master…dette-technique` n'est plus auditable : la branche
n'existe plus. Restait « constater au premier emploi réel » — les procédures de clôture et
d'abandon ont depuis alimenté les trois registres à répétition, sans qu'aucun des chemins
silencieux de R8 et R9 ait failli.
Établi par :

```
$ git branch -a --list '*dette-technique*'
(aucune sortie)

$ list-dir list .claude/implementation/todo/technical-debt        → 20 entrées
$ list-dir list .claude/implementation/todo/technical-debt-solde  → 15 entrées
$ list-dir list .claude/implementation/todo/technical-debt-ecarte →  2 entrées
```

## Pourquoi c'est gênant

R8 et R9 touchent deux chemins d'échec silencieux de la procédure de
clôture et d'abandon. Ce sont précisément les endroits où un défaut ne se manifeste par aucune
erreur, et ils n'ont jamais été relus par un tiers. Le premier usage réel du dispositif sera aussi
son premier test.

## Pour solder

auditer le diff `master…dette-technique` de l'étape 9, ou constater au premier
emploi réel que la clôture et l'abandon versent bien au registre ce qu'ils annoncent.

## Assumé

décision explicite de l'utilisateur — trois audits successifs, tous `RÉSERVES`, aucun
bloquant, des constats de plus en plus fins. Le coût d'une quatrième passe a été jugé supérieur au
risque.
