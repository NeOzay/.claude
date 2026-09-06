+++
id = "sortie-du-registre-jamais-exercee"
title = "La moitié « sortie du registre » de `debt-review` n'a jamais été exercée"
date = 2026-08-17
source = "Identifié par `revue-dette`, R12 du rapport d'audit de clôture."
reviewed = 2026-09-06
category = "a-solder"
+++

## Constat

la première passe réelle du skill n'a produit aucune des quatre catégories qui font
sortir une entrée : ni `a-solder`, ni `non-pertinent`, ni `doublon`, ni `pas-une-dette`. Le fichier
`technical-debt-ecarte.md` n'existe donc pas, son préambule n'a jamais été rédigé, le champ
`**Écartée le <date> — <motif>**` jamais écrit, et le déplacement vers `technical-debt-solde.md`
jamais effectué par ce skill.
Établi par : `ls .claude/implementation/todo/` → `README.md`, `technical-debt.md`,
`technical-debt-solde.md` — trois fichiers, pas quatre.

## Soldé le

**2026-09-06, revue de dette** — le chemin de sortie du registre a été exercé pour de vrai, ce que
le **Pour solder** demandait de constater : deux entrées sont arrivées dans
`technical-debt-ecarte` par un `move`, chacune porte sa section `## Écartée le` avec son motif et
sa preuve, et le contrôle de conservation reste juste.

Établi par :

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
technical-debt             49
technical-debt-solde       21
technical-debt-ecarte      2
```

Le `0 insertions` du renommage établit que la procédure a été suivie jusqu'au bout : déplacement
d'abord, preuve dans un second commit — c'est-à-dire le chemin complet, pas seulement le `move`.

## Pourquoi c'est gênant

quatre catégories sur sept sont validées par le seul tri de l'exemple
fictif. Le premier écartement réel sera aussi le premier test de ce chemin, et il s'exécutera sur
une entrée qu'on **retire** d'un fichier : le mode de défaillance y est la perte, pas l'erreur
visible.

## Pour solder

constater au premier écartement réel que l'entrée atterrit bien dans
`technical-debt-ecarte.md` avec son motif et sa preuve, et que le contrôle de conservation reste
juste. C'est le même mode de solde que pour les deux entrées d'audit jamais mené : un usage réel,
pas une relecture.

## Assumé

la revue du 2026-08-17 n'avait rien à écarter — les 14 entrées tiennent toutes. On ne
fabrique pas une sortie de registre pour éprouver un chemin de code.
