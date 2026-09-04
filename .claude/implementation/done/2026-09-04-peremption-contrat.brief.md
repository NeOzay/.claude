---
slug: peremption-contrat
titre: Provenance et péremption du contrat d'une liste semée
statut: validé
execution: direct
créé: 2026-09-03
---

## Intention

**Symptôme** : une skill s'attend à ce que le contrat d'une liste soit identique à sa semence ;
dès que la semence est modifiée, il y a divergence, et rien ne la signale (dit).
**But** : « on conserve la main locale, tout en surveillant le risque de péremption » (dit) — la
copie reste la seule appliquée, mais on sait d'où elle vient, à quelle version, et si la
définition a bougé depuis.

## Critères de réussite

- après `list-dir init <cible> --def <nom>`, `diff <définition>/contract.toml
  <cible>/.list/contract.toml` reste muet — `[origin]` compris
- `list-dir validate` sur une liste dont la semence a été incrémentée affiche l'avertissement de
  péremption **et conserve son code de retour**, que les éléments soient conformes ou non
- `frozen = true` dans `[origin]` fait disparaître l'avertissement de péremption, et fait
  **refuser** `reseed` sur cette liste ; `reseed --force` passe outre
- `list-dir reseed <liste>` sauvegarde le contrat d'origine, injecte les apports de la semence,
  et sort **non nul en nommant les clés** dès qu'une même clé a bougé des deux côtés
- `pytest` du paquet passe ; `ruff` et `pyright` restent propres
- `list-dir reseed <liste> --def <nom>` sur une liste **sans** `[origin]` l'estampille à la
  version de la semence, apports injectés — et refuse de même sur conflit
- le squelette d'`init` sans `--def` porte `def = false` : une liste née à la main n'avertit jamais
- `init --def <nom>` sur une semence qui déclare un autre nom **échoue en code 2**
- `list-dir validate` sur une liste sans `[origin]` signale qu'aucune provenance n'est déclarée ;
  `def = false` fait taire cet avertissement
- les trois définitions d'`implementation-tracker` portent une version, et les trois listes de
  `.claude/implementation/todo/` sont estampillées sans être modifiées autrement

## Hors-périmètre

- **aucun re-semis automatique** : rien ne resynchronise une liste sans qu'on l'ait demandé (dit)
- une liste qui **référence** sa semence — écarté, la résolution dépend de la machine (dit)
- `reseed` ne touche pas aux éléments `*.md` : les remettre en ligne reste le travail de
  `migrate` (dépôt: skills/list-dir/references/contrat-liste.md, « Quand le contrat change »)
- `debt-review`, `road-map` et le reste du pipeline ne sont pas retouchés

## Signaux de dérive

- si une commande **autre que** `reseed` et l'avertissement de `validate` se met à résoudre une
  définition, c'est raté : le contrat de la liste reste la seule règle appliquée
- si l'avertissement de péremption devient un échec, c'est raté — il n'a jamais à faire tomber un
  `validate` dont les éléments sont conformes
- si `reseed` résout un conflit tout seul, c'est raté : il refuse et nomme les clés
- si `reseed` écrit dans une liste `frozen` sans `--force`, c'est raté
- si la copie cesse d'être octet pour octet égale à sa semence pour une autre raison que
  `frozen`, c'est raté

## Contraintes connues de l'utilisateur

- **Rejeté d'emblée** : une liste qui *référence* sa semence — la résolution passe par les quatre
  rangs, donc dépend de la machine ; deux machines rendraient deux contrats (dépôt:
  skills/list-dir/references/contrat-liste.md, « Qui gagne »). Solution B retenue (dit).
- **Forme de l'estampille** : `[origin]` va dans le `contract.toml`, et la **semence le porte
  aussi** — « pour être égalé à la semence, il suffit de lui ajouter `[origin]` aussi » (dit).
  L'invariant « la copie est octet pour octet sa semence » est ainsi préservé (dépôt:
  scripts/listdir/store.py:744, docstring d'`init_list`).
- **Où se dit la péremption** : un avertissement affiché par `validate`, aussi bien sur son succès
  que sur son échec — les éléments d'une liste périmée restent conformes au contrat qu'elle
  porte (dit).
- **Comment on la fait taire** : `frozen = true` dans `[origin]` — la reprise en main délibérée se
  déclare, elle ne se devine pas (dit). Nommé `frozen` plutôt que `pinned` parce qu'il ne tait pas
  seulement l'avertissement : **`reseed` refuse de tourner sur une liste gelée**, `--force`
  autorisant le passage en force (dit).
- **Portée de la version** : la définition entière, gabarits compris — « l'avertissement doit aussi
  fonctionner sur les templates » (dit).
- **`reseed` n'écrase pas** : il sauvegarde le fichier d'origine, puis « injecte les diffs dans le
  contrat en comparant la source et la cible » — les ajouts locaux survivent (dit).
- **Conflit** : `reseed` refuse et s'arrête en nommant les clés ; aucune résolution automatique (dit).
- **Suppression côté semence** : la clé est **gardée et signalée**, comme `migrate` conserve un
  champ que le contrat ne déclare plus (dit).
- **Listes antérieures** : elles n'ont aucun `[origin]` ; c'est `reseed --def <nom>` qui les
  adopte — un seul geste, qui injecte et estampille, et refuse comme d'habitude sur conflit (dit).
- **Absence de provenance** : `validate` la signale et rappelle le geste d'adoption ; une liste
  née à la main portera donc cet avertissement (dit, coût nommé et accepté).
- **Liste sans semence** : `def = false` dans `[origin]` — « pour les listes sans seed il suffit
  de mettre `def` sur `false` » (dit). C'est la déclaration qui fait taire l'avertissement
  d'adoption, distincte de `frozen`, qui fait taire celui de péremption et verrouille `reseed`.
- **`init` n'écrit jamais `[origin]`, il le reçoit** : la semence porte le sien, la copie est
  octet pour octet la semence, donc `--from` estampille comme `--def`. `def` **nomme** la
  définition, il ne dit pas où elle était ; `reseed` rerésout ce nom dans les quatre rangs, et
  `reseed --from <chemin>` reste la porte de sortie quand elle n'y est installée nulle part.
  Un répertoire essayé en `--from` sans `[origin]` sème donc une liste sans provenance (dit).
- **La semence obéit aux mêmes contraintes que ses listes filles** (dit) — rien ne les distingue
  une fois la base obtenue (dépôt: scripts/listdir/contract.py, docstring de `list_base`).
- **État de départ sain** : les trois registres d'`implementation-tracker` sont aujourd'hui
  identiques à leurs semences (dépôt: `diff` muet sur les trois `contract.toml`).

## Incertitudes à lever en plan

- forme exacte de la sauvegarde de `reseed` (nom, emplacement sous `.list/`, sort d'une
  sauvegarde précédente)
- granularité de l'injection et de la détection de conflit : la clé TOML, ou le bloc `[fields.x]`
  entier
