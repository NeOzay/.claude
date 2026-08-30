+++
id = "correctif-r21-non-audite"
title = "Le correctif `R21` de `contrat-pipeline` n'a jamais été audité"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, décision de clôture."
reviewed = 2026-08-17
category = "inverifiable"
+++

## Constat

le chantier s'est clos sur le verdict `RÉSERVES` de `0c5a8fe`. L'étape 11, qui élargit
le `case` du contrôle 6 aux écritures `~/` et `${HOME}/`, a été écrite **après** cet audit et n'a
été jugée par personne. `references/audit.md` demandait un audit complet ; il n'a pas eu lieu.

## Écartée le

**2026-08-30 — non pertinent** — le correctif visé n'existe plus. L'étape 11 élargissait le `case`
d'un garde-fou en shell ; ce fichier a été supprimé par la réécriture du pipeline en Python, et la
logique du contrôle 6 est aujourd'hui écrite ailleurs, autrement, et couverte par des tests qui se
rejouent — ce que l'audit manquant devait justement remplacer.
Établi par :

```
$ git show --stat --oneline c71e6fe | grep '\.sh'
 scripts/check-pipeline.sh                          | 232 ---------

$ uvx pytest scripts/tests/test_controle_6.py -q
22 passed in 0.17s                                           code 0
```

## Pourquoi c'est gênant

le correctif touche la logique de décision du seul contrôle qui protège
contre le défaut ayant bloqué ce chantier. Il a été testé par injection sur neuf cas, mais par son
auteur.

## Pour solder

auditer le diff de l'étape 11, ou constater au premier usage réel que le contrôle
6 ne produit ni faux positif ni faux négatif.

## Assumé

décision explicite de l'utilisateur — trois audits successifs, un défavorable levé puis
deux fois `RÉSERVES` avec des constats de plus en plus fins, aucun bloquant. Le coût d'un quatrième
passage a été jugé supérieur au risque.
