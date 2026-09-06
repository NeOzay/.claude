+++
id = "etape-corrective-cochee-avant-audit"
title = "Une étape corrective née d'un audit ne peut pas être cochée avant l'audit"
date = 2026-08-14
source = "Identifié par `audit-integre`, R8 du rapport d'audit ; élargi par `contrat-pipeline`, R3 puis R13."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`references/cloture.md` demande, sous « Vérifier ensuite que toutes les étapes sont
cochées », que **toutes** les étapes le soient avant d'auditer. Or une étape née d'un audit
précédent a pour vérification « nouvel audit complet FAVORABLE », qui ne peut être satisfaite
qu'après. L'étape est donc `[>]` au moment où l'audit
tourne — c'est ce qui s'est passé pour l'étape 8 d'`audit-integre`.

## Pourquoi c'est gênant

l'ordre correct (auditer, puis cocher) fonctionne, mais l'appelant doit
y penser à chaque fois. Chaque étape corrective née d'un audit rejouera la même gêne, et la règle
écrite dit littéralement le contraire de ce qu'il faut faire.

## Pour solder

formuler ces étapes avec une vérification portant sur le **correctif** plutôt que
sur le verdict à venir (`grep -n "rev-parse" agents/implementation-auditor.md`), et le dire dans
`cloture.md`.

**Élargi le 2026-08-14 par `contrat-pipeline`** — le même ordonnancement rend **structurellement
invérifiable** tout critère de réussite portant sur le registre de dette. Le solde s'écrit au point 2
de `cloture.md`, donc après l'audit : aucun audit ne pourra jamais constater que les entrées sont
passées dans `technical-debt-solde.md`. Les trois audits du chantier ont chacun signalé ce critère
comme non atteint, sans qu'aucune correction soit possible.

**Pour solder, complété** — les critères de réussite portant sur un geste postérieur à l'audit
doivent être écrits comme tels au brief, ou déplacés vers une vérification post-clôture. La
formulation actuelle oblige tout auditeur à rendre `RÉSERVES` sur un point que le dispositif interdit
d'atteindre au moment où il juge.

## Assumé

<OPTIONNEL>
