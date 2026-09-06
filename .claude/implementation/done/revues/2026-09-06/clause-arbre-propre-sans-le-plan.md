+++
id = "clause-arbre-propre-sans-le-plan"
title = "La clause « arbre propre » du tracker ne couvre pas le plan"
date = 2026-08-14
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ sed -n '96,99p' skills/implementation-tracker/SKILL.md
**Prérequis : arbre de travail propre.** Si `git status --short` (Étape 0) n'est pas vide, **ne pas
créer** de nouvelle implémentation. **Exception : les `*.brief.md`.** Un brief produit par
`intent-brief` avant l'appel au tracker apparaît en `??` sans être une modification étrangère au
chantier — l'ignorer dans ce contrôle.

$ grep -n "plans/" skills/implementation-tracker/SKILL.md
151:   Le plan est persisté dans `.claude/plans/` (voir `plansDirectory`), sous un nom **généré par le
161:   git check-ignore -q .claude/plans/<fichier>.md && echo "IGNORÉ — le signaler"
```

## Verdict

Le constat tient intégralement. L'exception de l'Étape 2 ne nomme que les `*.brief.md`, et
`.claude/plans/` n'apparaît qu'à l'Étape 3 (L151, L161), c'est-à-dire **après** le contrôle
d'arbre propre. Le flux normal produit toujours les deux artefacts, et la clause n'en couvre
qu'un. Rien n'a été payé ni retiré : ce n'est ni `a-solder` ni `non-pertinent`, et aucune
extension n'est mesurable depuis le constat — donc pas `aggravee`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
