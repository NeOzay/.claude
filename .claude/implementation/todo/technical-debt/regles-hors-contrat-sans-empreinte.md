+++
id = "regles-hors-contrat-sans-empreinte"
title = "Les règles dont l'autorité n'est pas contrat.md ne sont couvertes par aucune empreinte"
date = "2026-09-02"
source = "chantier `recopies-hors-contrat`, étape 8 — renoncement écrit et motivé"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le contrôle 2 de `check_pipeline.py` (`EMPREINTES`) protège une phrase verbatim par section de
`contrat.md`, et vérifie qu'elle apparaît exactement une fois dans `skills/`. Il ne couvre que ce
fichier. Les règles dont l'autorité est ailleurs — `contrat-liste.md` « Un élément » et « L'API
Python », `dette.md` « Ce qu'une entrée porte », `templates/review.md`, `debt-review/SKILL.md`
Étape 3 — ne sont protégées par rien.

Le chantier `recopies-hors-contrat` a résorbé neuf écritures de ce type, dont deux qui se
contredisaient sur la preuve exigée d'un `doublon`.

## Pourquoi c'est gênant

Une recopie nouvelle passe au vert. C'est ainsi que la contradiction d'origine s'est installée :
une règle réécrite de mémoire dans un cinquième fichier, sans qu'aucune commande ne le signale,
puis divergeant lentement de sa source. Le coût ne se paie pas à l'écriture mais des mois plus
tard, quand deux fichiers donnent deux réponses et que rien ne dit lequel fait foi.

Le contrôle 8 (renvois entre skills) limite les dégâts sans les empêcher : il vérifie qu'un renvoi
résout, jamais qu'une règle n'a pas été re-développée à côté.

## Pour solder

Deux formes ont été étudiées et écartées pour ce chantier, faute d'arbitrage :

- **empreintes libres** — indexer `EMPREINTES` par `(fichier-autorité, ancre)` au lieu de la seule
  ancre de `contrat.md`, sans exiger une empreinte par section. Simple, mais perd le contrôle de
  complétude qui garantit aujourd'hui qu'aucune section n'est laissée sans filet ;
- **sections marquées** — une convention de marquage dans les fichiers d'autorité, qui garde la
  complétude au prix d'une convention à tenir. Plus coûteux : `dette.md` et `contrat-liste.md`
  mêlent règles d'autorité et prose locale, et la frontière demande un jugement.

Trancher entre les deux, puis étendre le contrôle 2.

## Assumé

<OPTIONNEL>
