+++
id = "repli-section-marker-jamais-exerce"
title = "Le repli de section_marker sur un titre inconnu n'est plus atteignable ni testé"
date = 2026-08-31
source = "chantier sections-en-forme-longue, audit R4"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`Contract.section_marker`, `listdir/types.py`, rend `<OPTIONNEL>` quand le titre demandé n'est pas
au contrat — `return section.marker if section is not None else OPTIONAL`.

Ses trois appelants, tous dans `listdir/store.py`, itèrent désormais sur `contract.sections`
lui-même : la construction du squelette d'un élément neuf, et les deux points de `migrate` qui
ajoutent une section manquante. Aucun ne peut donc lui passer un titre absent du contrat. La
branche `section is None` est morte pour le code de production, et aucun test ne l'exerce
directement.

Vérifié sur `752449e` : `grep -rn section_marker` ne rend que ces trois appels et la définition.

## Pourquoi c'est gênant

C'est un filet légitime — un repli permissif sur un titre inconnu est le bon comportement — mais
un filet que rien ne tend. Un futur appelant qui passerait un titre venu d'ailleurs (une entrée
lue sur disque, un gabarit, un argument de commande) dépendrait d'un comportement qu'aucun test ne
garantit : l'inverser en refactorisant ne ferait échouer aucune suite.

Le cas est d'autant plus facile à manquer que le code *a l'air* couvert : les 307 tests passent par
`section_marker` à chaque création d'élément, sans jamais emprunter cette branche.

## Pour solder

Deux issues, à trancher plutôt qu'à cumuler :

- **garder le filet et le tester** : un test unitaire sur `section_marker("titre inconnu")` qui
  fixe le repli à `<OPTIONNEL>` et la raison de ce choix ;
- **le retirer** et rendre le contrat explicite — `sections[title].marker`, qui lèvera sur un titre
  inconnu — si l'on juge qu'un appelant hors contrat est un défaut d'appelant, pas un cas à
  absorber.

La première est la moins coûteuse et conserve l'intention d'origine, que le plan exigeait
nommément. La seconde n'a de sens que si l'on constate qu'aucun appelant légitime ne pourra jamais
présenter un titre inconnu.

## Assumé

<OPTIONNEL>

## Soldé le

2026-08-31, par le chantier `2026-08-31-champs-preremplis` — seconde issue de « Pour solder » :
`Contract.section_marker` retiré, ses appelants itérant désormais sur `contract.sections` et
appelant `prefill.initial_section` avec la `Section` elle-même.

```
$ grep -rn "section_marker" skills/list-dir/ --include='*.py' --include='*.md' | grep -v __pycache__
(aucune occurrence)
```
