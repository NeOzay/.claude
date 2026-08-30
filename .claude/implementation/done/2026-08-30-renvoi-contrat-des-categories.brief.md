---
slug: renvoi-contrat-des-categories
titre: Le renvoi au contrat remplace la recopie des catégories de verdict
statut: validé
execution: direct
créé: 2026-08-30
---

## Intention

**Symptôme** : la doc de `debt-review` porte une copie de ce que le contrat de la liste de revue
déclare — les sept catégories de verdict. Une huitième catégorie ajoutée au contrat laisserait la
prose en décrire sept, sans qu'aucune commande n'échoue (dette
`gabarit-rapport-recopie-les-categories`).
**But** : remplacer la recopie par un renvoi vers le contrat en vigueur, et doter
`list-dir contract` de quoi rendre ce renvoi exécutable avant que la liste de revue n'existe.

## Critères de réussite

- `list-dir contract --def technical-debt --template review` imprime `templates/review.toml` de la
  définition ; `--from <chemin de définition>` et `<liste réelle>` font de même sur leur cible (dit)
- `list-dir contract "$R" --values category` imprime les sept identifiants, un par ligne, **dans
  l'ordre du contrat** (dit, `AskUserQuestion` du 2026-08-30)
- la boucle des piles de `debt-review/SKILL.md:276` n'énumère plus aucun identifiant : elle les
  tire de `--values category`
- `gabarit-rapport.md` ne recopie plus le compte « sept » : il renvoie à la commande
- la suite `skills/list-dir/scripts/tests/` passe

## Hors-périmètre

- **le garde-fou sur `categories.md`** — confronter ses sept titres de section aux `values` du
  contrat. Reconnu comme un trou réel, écarté du chantier et à porter au registre de dette (dit)
- la prose de `categories.md` elle-même : elle porte le sens de chaque catégorie et sa preuve
  exigée, que le contrat ne porte pas (dit)

## Signaux de dérive

- si `contract` se met à faire autre chose qu'imprimer — filtrer, juger, reformater — c'est raté.
  `--values` extrait, il ne trie ni ne valide (dit)
- si la prose de `categories.md` se fait réécrire, s'arrêter : elle porte le sens, pas la
  structure (dit)

## Contraintes connues de l'utilisateur

- **`contract --def <nom>`** cible le `contract.toml` de la définition, pas un de ses gabarits (dit)
- **`--from`/`--def` sur `contract`** sont demandés symétriques de ceux d'`init` (dit) — `init`
  les déclare déjà mutuellement exclusifs (dépôt: skills/list-dir/scripts/listdir/commands/init.py)
- **`--template <nom>`** s'ajoute et « fonctionne dans les 3 cas : def, from et liste réelle » (dit)
- **L'ordre des piles est déjà dans le contrat** : le `values` de `review.toml` porte exactement
  l'ordre non alphabétique de la boucle — ce qui sort du registre d'abord, ce qui y reste ensuite
  (dépôt: skills/implementation-tracker/list-dir/technical-debt/templates/review.toml)
- **Ce que le renvoi doit viser** : le gabarit source de la définition, jamais la liste dérivée,
  qui n'existe qu'après `derive` (dépôt: .claude/implementation/todo/technical-debt/gabarit-rapport-recopie-les-categories.md)

## Incertitudes à lever en plan

- la doctrine « cet ordre est sémantique, pas alphabétique » vit aujourd'hui dans la prose de
  `SKILL.md` ; où l'écrire une fois la boucle dérivée — commentaire de `review.toml`, ou prose
  conservée à côté de la boucle ?
