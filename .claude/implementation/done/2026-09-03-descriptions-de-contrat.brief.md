---
slug: descriptions-de-contrat
titre: Rédiger les descriptions des contrats de dette
statut: validé
execution: direct
créé: 2026-09-03
---

## Intention

**Symptôme** : « Plusieurs contrats ont leurs champs remplis avec des descriptions vides. » (dit)
**But** : que le contrat d'une liste dise ce qu'est une dette — son contenu et sa structure —
champ par champ et section par section, et que `dette.md` renvoie à lui au lieu de le redire.

## Critères de réussite

- `grep -rn 'description = ""' skills/implementation-tracker/list-dir .claude/implementation/todo`
  ne rend rien, et aucune description de champ ne recopie la description de sa liste
- semence et copie restent identiques, gabarit `review.toml` compris (`diff` muet sur les trois
  registres)
- `list-dir validate` passe sur les trois registres
- `list-dir contract "$T/technical-debt-solde"` n'affiche plus quatre fois la même phrase
- les règles de `dette.md` qui décrivent le contenu d'une section ont laissé place à un renvoi
  au contrat

## Hors-périmètre

- aucune modification de code : la recopie vient d'une rédaction à la main, pas du préremplissage
- pas de réécriture des entrées de dette existantes pour les conformer aux descriptions rédigées

## Signaux de dérive

- si une `description` devient un paragraphe : le contrat déclare, il n'argumente pas
- si `dette.md` cesse d'expliquer comment fonctionnent les dettes et comment les manipuler, c'est
  qu'on a déplacé la mauvaise prose (dit)
- si semence et copie divergent en fin de passe, la règle des deux exemplaires a été oubliée
  (dépôt: `semence-et-copie-divergent-sans-controle`)

## Contraintes connues de l'utilisateur

- **Périmètre** : les deux défauts sont à traiter, pas seulement la dette déjà écrite (dit)
- **Autorité** : « Le contract est la source de vérité d'une liste. » (dit)
- **Ligne de partage** : « dette.md explique comment fonctionnent les dettes et comment les
  manipuler. Le fichier contract définit la façon dont se décrit une dette, son contenu et sa
  structure. Une modification de l'une entraîne souvent des ajustements sur l'autre. » (dit)
- **Deux exemplaires** : semence et copie en vigueur ne sont resynchronisées par rien, elles
  s'écrivent dans la même passe (dépôt:
  technical-debt/sections-declarees-sans-description-redigee.md)
- **Sources de doctrine** : `skills/implementation-tracker/references/dette.md` pour les trois
  registres, `skills/debt-review/` pour `review.toml` (dépôt)
- **Aucun code en cause** : la recopie des descriptions de champ date de d8a06ac, écrite à la
  main ; `prefill.py` ne touche qu'aux valeurs des éléments (dépôt: `git log -S`, prefill.py)
- **review.toml dans le périmètre** : ses 4 sections sont traitées, `skills/debt-review/` devenant
  renvoyant à son tour (tranché)
- **Registre de dette** : rien n'est soldé avant le verdict de `implementation-auditor` ; si
  l'audit juge la rédaction incomplète, `sections-declarees-sans-description-redigee` reste
  ouverte et amendée (tranché)

## Incertitudes à lever en plan

- le second défaut (descriptions de champ recopiées de la description de liste) n'a aucune entrée
  au registre : à la clôture, décider s'il en mérite une rétroactive ou si le journal du suivi suffit
