---
name: git-smart-commit
description: >
  Crée des commits Git. Utilise cette skill dès que l'utilisateur mentionne "commit",
  "committer les changements", "sauvegarder mes modifications", "git commit", "enregistrer le
  travail", "versionner", "commit tout", "commit ce que j'ai fait", ou demande de créer un commit
  pour les fichiers en cours. Elle observe le diff complet, catégorise les changements et propose
  un message Conventional Commits, puis ne committe qu'avec l'accord explicite de l'utilisateur.
---

# Git Smart Commit

Ce fichier ne fait qu'orienter. Chaque type de commit a sa procédure dans un fichier à part :
**lire celui du type demandé, et lui seul.**

## Choisir le type

| Demande | Type | Procédure |
|---|---|---|
| Un commit des changements en cours, sans autre précision | 1 — commit ordinaire | [`references/hors-chantier.md`](references/hors-chantier.md) |
| Un commit sur la branche d'un chantier : état initial, session ou étape terminée | 2 — commit rapide de chantier | [`references/etape.md`](references/etape.md) |
| La clôture d'un chantier (aplatir sa branche sur la base), ou son abandon | 3 — aplatissement | [`references/aplatissement.md`](references/aplatissement.md) |

Dans le doute, c'est le type 1.

## Ce qui vaut pour tous les types

Chaque procédure y renvoie au moment où elle en a besoin. Inutile de les lire d'avance.

- [`references/confirmation.md`](references/confirmation.md) — rien n'est commité sans accord
  explicite.
- [`references/staging.md`](references/staging.md) — stager des chemins nommés, jamais `-A`.
- [`references/conventional-commits.md`](references/conventional-commits.md) — format et règles de
  rédaction d'un message rédigé.
