+++
id = "etape-corrective-cochee-avant-audit"
title = "Une étape corrective née d'un audit ne peut pas être cochée avant l'audit"
date = 2026-08-14
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n "toutes les étapes sont cochées" skills/implementation-tracker/references/cloture.md
23:Vérifier ensuite que toutes les étapes sont cochées — sinon demander quoi faire des restantes ;

$ sed -n '23,24p' skills/implementation-tracker/references/cloture.md
Vérifier ensuite que toutes les étapes sont cochées — sinon demander quoi faire des restantes ;
auditer un chantier inachevé fait juger du travail que personne n'a fini.
```

## Verdict

La phrase visée est inchangée, mot pour mot, et rien autour d'elle ne prévoit le cas d'une étape
dont la vérification est le verdict d'audit à venir. La contradiction que l'entrée décrit — la
règle écrite dit littéralement le contraire de l'ordre praticable — se rejoue à chaque étape
corrective née d'un audit. Aucune extension chiffrable depuis le constat : `pertinent`, pas
`aggravee`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
