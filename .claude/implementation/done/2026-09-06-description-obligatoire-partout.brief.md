---
slug: description-obligatoire-partout
titre: « description » obligatoire sur les champs comme sur les sections
statut: validé
execution: délégué
créé: 2026-09-05
---

## Intention

**Symptôme** : un contrat déclare ses champs et ses sections sur le même modèle, mais `validate`
refuse une section sans `description` et laisse passer un champ sans. « L'asymétrie n'est pas
voulue. »
**But** : rendre la règle symétrique — `description` obligatoire sur les champs, les sections et
la racine du contrat — puis l'écrire dans `skills/list-dir/references/format.md` et solder la
dette `description-obligatoire-sur-les-sections-seulement`.

## Critères de réussite

- un contrat sans `description` sur un `[fields.*]` est refusé par `list-dir validate`, en nommant
  le champ, comme il l'est aujourd'hui pour une section
- `description = ""` reste accepté partout : c'est la **clé** qui est exigée, pas son texte
- `uv run --with pytest pytest skills/list-dir/scripts/tests` passe
- `format.md` ne décrit plus d'asymétrie et ne renvoie plus à cette dette
- la fiche de dette est passée en `technical-debt-solde`

## Hors-périmètre

- la dette `deux-conventions-de-mode-de-defaillance` — retirée du chantier : « l'autre induit une
  réécriture importante, propice à des modifications plus larges » (dit)
- aucune réécriture de prose dans `contrat.md`, `dette.md`, `debt-review/` (dit)

## Signaux de dérive

- si le chantier commence à réécrire de la prose de référence au-delà du paragraphe de `format.md`
  qui énonce la règle, s'arrêter (dit)
- si la correction des fixtures de test devient l'occasion de les remanier, s'arrêter — on ajoute
  une clé, on ne refactore pas

## Contraintes connues de l'utilisateur

- **Tranché** : obligatoire sur les champs, les sections **et la racine** du contrat (dit)
- **Coût dans les contrats : marginal.** Un seul champ sans `description` dans les 12
  `contract.toml` du dépôt — `id`, dans les 3 listes de dette × semence/backup/copie de travail.
  Tous ont déjà une description racine (dépôt: audit tomllib des 12 contrats)
- **Coût réel concentré dans les tests** : 54 des 93 déclarations `[fields.*]` / `[sections.*]`
  des fixtures n'ont pas de `description` (dépôt: skills/list-dir/scripts/tests/)
- **Le modèle à suivre existe déjà** : `contract.py:475` fait le contrôle pour les sections ;
  `contract.py:422` est l'endroit symétrique côté champs (dépôt)
- **Où écrire la règle** : `format.md:125-141`, tableau de l'asymétrie et bloc cité de la dette,
  tous deux à remplacer (dépôt)

## Incertitudes à lever en plan

- (aucune ouverte)
