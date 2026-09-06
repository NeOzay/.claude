+++
id = "controle-completude-revue-sans-code-sortie"
title = "Le contrôle de complétude d'une revue signale par `echo`, sans code de sortie"
date = 2026-08-23
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n 'ÉCHEC : autant de fiches' skills/debt-review/SKILL.md
187:  || echo "ÉCHEC : autant de fiches que d'entrées attendu"
255:  || echo "ÉCHEC : autant de fiches que d'entrées attendu"
```
Les deux occurrences sont inchangées : `|| echo`, sans `; false`, donc code de sortie 0 sur échec.

## Verdict

Le constat tient aux deux endroits exacts qu'il nomme. Le `Pour solder` proposait le remplacement
par `|| { echo "…"; false; }` — il n'a pas été appliqué. Le voisinage confirme d'ailleurs que le
dispositif sait faire autrement : le bloc de comptage des piles de l'Étape 3 se termine bien par
`false`, ce qui rend l'exception d'autant plus visible. Deux occurrences au constat, deux
aujourd'hui : aucune extension, donc `pertinent` et non `aggravee`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
