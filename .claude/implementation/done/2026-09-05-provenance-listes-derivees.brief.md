---
slug: provenance-listes-derivees
titre: Provenance des listes dérivées
statut: validé
execution: direct
créé: 2026-09-04
---

## Intention

**Symptôme** : « le dernier chantier a permis de mettre à jour les contracts des list-dir, mais il
ne prend pas bien en charge les listes dérivées. `review.toml` ne possède pas d'origine. » (dit)

**But** : qu'une liste engendrée par `derive` déclare d'où elle vient, sous le format
`liste-mère/liste-dérivée` (ex. `technical-debt/review`), « pour retrouver la graine d'une liste
dérivée » (dit). L'estampille est **documentaire** : elle nomme le gabarit source pour qu'un
lecteur sache quoi taper, elle ne devient pas une définition résolvable.

## Critères de réussite

- `list-dir derive <registre> <rev> --template review` puis `list-dir validate <rev>` → rc 0 et
  **aucun avertissement** sur stderr (aujourd'hui : « aucune provenance déclarée » sur 43 fiches)
- une estampille malformée est refusée en nommant la clé — `def = "a/b/c"`, `def = "a/"`,
  `def = "../x"` font sortir `validate` non nul
- une dérivée non gelée dont l'estampille est composite ne s'entend plus dire « définition
  introuvable dans les quatre rangs » : le message dit qu'un nom composite désigne un gabarit
- `uvx pytest skills/list-dir/scripts/tests -q` passe (428 tests aujourd'hui)
- `(cd skills/list-dir && uvx --with pytest basedpyright)` → 0 error

## Hors-périmètre

- pas de `init --def technical-debt/review` : « n'a pas vraiment de sens. Les templates existent
  pour réaliser une transformation sur une liste existante » (dit)
- le nom composite n'est donc **pas** une définition résolvable : « il faudrait juste pouvoir
  remonter jusqu'à la liste mère » (dit)
- pas de `list-dir contract <rev> --seed` ni d'aucune commande qui suivrait l'estampille —
  écarté explicitement (dit)
- l'**instance** source du `derive` (quel registre, à quelle date) n'entre pas dans `[origin]` :
  elle n'est connue qu'au moment du `derive`, donc l'écrire romprait « `init` n'écrit jamais cette
  table, il la reçoit ». Sa place serait un champ prérempli, pas l'estampille (dit)
- `derive` n'écrit pas de `.list/semence/` : une dérivée gelée n'a rien à rattraper (dit)

## Signaux de dérive

- si une commande ou une option nouvelle apparaît, c'est raté : le chantier est une règle de
  format, un message honnête et de la doctrine (dit)
- si `derive` se met à écrire tout ou partie de l'estampille au lieu de la recopier, s'arrêter (dit)
- si `resolve()` doit rendre autre chose qu'un répertoire de définition, c'est qu'on refait
  l'option écartée (dit)

## Contraintes connues de l'utilisateur

- **Listes jetables** : une liste dérivée n'a « pas d'utilité à être mise à jour » ; il faut
  « pouvoir les frozen à la création » — donc `frozen = true` déclaré **dans le gabarit**, reçu
  comme le reste de l'estampille (dit)
- **Réutiliser** : `_origin` accepte déjà un nom composite et `frozen = true` fait déjà taire tous
  les avertissements — vérifié en posant la table à la main dans le contrat d'une dérivée,
  `validate` rc=0 sans un mot (dépôt: contract.py:245, provenance.py:69)
- **Ne pas recréer** : `derive` copie le gabarit `<src>/.list/templates/<nom>.toml` verbatim en
  `<dst>/.list/contract.toml` et n'écrit rien d'autre (dépôt: store.py:530)
- **Règle en vigueur** : « `init` n'écrit jamais cette table, il la reçoit » — l'estampille voyage
  avec la semence (dépôt: references/contrat-liste.md, « Provenance et péremption »)
- **Existe déjà** : `list-dir contract --def technical-debt --template review` imprime le gabarit
  source ; `debt-review` s'en sert pour lire les catégories
  (dépôt: skills/debt-review/references/gabarit-rapport.md:56)
- **Précédent de forme** : `source_path` refuse déjà qu'un nom de gabarit soit un chemin — la
  validation du second segment a son modèle (dépôt: contract.py:84)
- **Deux exemplaires du même gabarit**, aujourd'hui identiques au diff près : la définition
  `skills/implementation-tracker/list-dir/technical-debt/templates/review.toml` et la copie
  `.claude/implementation/todo/technical-debt/.list/templates/review.toml`. Aucun autre gabarit
  n'est en circulation (dépôt: find '*/templates/*.toml')
- **Consommateur** : `debt-review` enchaîne `derive` puis `validate` sur une liste créée sous
  `done/revues/$(date +%F)` (dépôt: skills/debt-review/SKILL.md:170)

## Incertitudes à lever en plan

- estampiller le gabarit fait bouger la semence de `technical-debt` : reste à trancher en plan si
  `origin.version` de la définition passe à 2 et si le registre vivant se rattrape par `reseed`,
  ou si le gabarit se corrige des deux côtés à la main
