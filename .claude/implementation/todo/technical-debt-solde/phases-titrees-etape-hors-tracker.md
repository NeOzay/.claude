+++
id = "phases-titrees-etape-hors-tracker"
title = "`intent-brief` et `debt-review` titrent leurs phases « Étape N », en collision avec le Lexique"
date = "2026-10-04"
source = "chantier `contexte-tracker`, journal du Suivi et audits de clôture, constat R8"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le Lexique global réserve « Étape » à l'unité de travail d'un Chantier. `implementation-tracker`
titre désormais ses phases « Phase N ». `skills/intent-brief/SKILL.md` et
`skills/debt-review/SKILL.md` titrent encore les leurs « Étape N », renvois compris.

## Soldé le

**2026-10-04, hors chantier** (`ff139c9`) — les titres « Étape 0 » à « Étape 6 » des deux skills
sont devenus « Phase 0 » à « Phase 6 », avec leurs renvois, l'ancre de
`skills/debt-review/references/gabarit-rapport.md` et les deux renvois extérieurs : le commentaire
de la Semence `brief` et `shadow-skills/skill-convention/references/prose.md`. Les « étapes » qui
restent dans `intent-brief` désignent celles d'un Chantier.

```
$ git grep -n -E "[Éé]tapes? [0-9]|#étape-" -- skills/intent-brief skills/debt-review
                                                             (aucune sortie) code 1
$ git grep -c -E "Phases? [0-9]" -- skills/intent-brief skills/debt-review
skills/debt-review/SKILL.md:19
skills/debt-review/references/exemple-revue.md:2
skills/debt-review/references/gabarit-rapport.md:1
skills/intent-brief/SKILL.md:17
skills/intent-brief/references/grille-questions.md:1
$ .venv/bin/python scripts/check_pipeline.py
  ✓ 59 renvois entre skills, tous résolvent           Pipeline conforme.  code 0
```

Reste hors de ce solde : des entrées actives du Registre citent encore « Étape 0 », « Étape 3 » ou
« Étape 5 » de `debt-review`. Comme le numéro n'a pas changé, le repère reste trouvable.

## Pourquoi c'est gênant

Un lecteur ne distingue plus une phase d'un skill d'une Étape de Chantier, et la règle du
Lexique, qui réserve la majuscule au sens défini, y est enfreinte à chaque titre.

## Pour solder

Renommer les titres « Étape N » de ces deux skills en « Phase N », ainsi que leurs renvois,
comme `contexte-tracker` l'a fait pour le tracker.

## Assumé

Hors-périmètre du Brief de `contexte-tracker`, qui ne touchait `intent-brief` qu'à ses renvois
vers le tracker.
