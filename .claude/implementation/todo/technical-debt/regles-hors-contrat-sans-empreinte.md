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
fichier. Les règles dont l'autorité est ailleurs — `format.md` « Un élément », `operations.md`
« Déplacer un élément », `dette.md` « Ce qu'une entrée porte », `templates/review.md`, `debt-review/SKILL.md`
Étape 3 — ne sont protégées par rien.

Le chantier `recopies-hors-contrat` a résorbé neuf écritures de ce type, dont deux qui se
contredisaient sur la preuve exigée d'un `doublon`.

**Complété le 2026-09-15 par `git-smart-commit-trois-commits`** (R8 et R9 de son rapport d'audit)
— la règle de staging et l'accord avant commit sont sortis de `contrat.md` vers
`skills/git-smart-commit/references/staging.md` et `confirmation.md` : ils ont perdu l'empreinte du
contrôle 2. Les critères « chaque type lisible indépendamment » et « texte commun référencé, sans
recopie » de ce chantier n'ont été jugés que par lecture et grep de motifs, faute de commande dédiée.

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
  complétude au prix d'une convention à tenir. Plus coûteux : `dette.md` et les références de
  `list-dir`
  mêlent règles d'autorité et prose locale, et la frontière demande un jugement.

Trancher entre les deux, puis étendre le contrôle 2.

## Assumé

<OPTIONNEL>
