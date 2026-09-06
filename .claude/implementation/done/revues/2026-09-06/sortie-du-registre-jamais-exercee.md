+++
id = "sortie-du-registre-jamais-exercee"
title = "La moitié « sortie du registre » de `debt-review` n'a jamais été exercée"
date = 2026-08-17
reviewed = 2026-09-06
category = "a-solder"
+++

## Vérifié par

```
$ list-dir list .claude/implementation/todo/technical-debt-ecarte
correctif-r21-non-audite 2026-08-14
correctifs-etape-9-non-audites 2026-08-14

$ git show --stat --find-renames 6754ac1
 .../{technical-debt => technical-debt-ecarte}/correctif-r21-non-audite.md | 0
 .../correctifs-etape-9-non-audites.md                                     | 0
 2 files changed, 0 insertions(+), 0 deletions(-)

$ list-dir show .claude/implementation/todo/technical-debt-ecarte correctif-r21-non-audite | grep -A2 "Écartée le"
## Écartée le
**2026-08-30 — non pertinent** — le correctif visé n'existe plus. […] Établi par :

$ for l in technical-debt technical-debt-solde technical-debt-ecarte; do \
    printf '%-26s %s\n' "$l" "$(list-dir list .claude/implementation/todo/$l | wc -l)"; done
technical-debt             51
technical-debt-solde       19
technical-debt-ecarte      2
```

## Verdict

Le `Pour solder` demandait de **constater au premier écartement réel** que l'entrée atterrit bien
dans `technical-debt-ecarte` avec son motif et sa preuve, et que le contrôle de conservation reste
juste. Les trois conditions sont réunies : deux entrées y sont, arrivées par un `move` (git le voit
comme un renommage pur, `0 insertions`, dans un commit séparé de la réécriture — exactement la
procédure de `dette.md`), chacune porte sa section `## Écartée le` avec motif `non pertinent` et
« Établi par ». Le chemin de sortie a donc été exercé pour de vrai.

Ce n'est pas `non-pertinent` : rien n'a disparu, c'est bien le mécanisme décrit qui a fonctionné.

## Action

Sortie du registre : `list-dir move .claude/implementation/todo/technical-debt
sortie-du-registre-jamais-exercee .claude/implementation/todo/technical-debt-solde`, puis section
`## Soldé le` datée du 2026-09-06, citant le commit `6754ac1` et la commande de conservation
ci-dessus.

## Arbitrage

**Différée.** L'arbitrage du 2026-09-06 a porté sur le contenu des entrées, pas sur les sorties de
registre : le `move` vers `technical-debt-solde` et la section `## Soldé le` attendent un accord
explicite. Le verdict `a-solder` est maintenu, l'entrée reste au registre actif en attendant, et
ses champs `category`/`reviewed` ne sont donc pas écrits — ils le seront par le geste de solde.
