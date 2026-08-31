---
slug: 2026-08-31-champs-preremplis
titre: Préremplissage des champs et sections d'un contract.toml (command / text)
branche: 2026-08-31-champs-preremplis
base: master
statut: terminé
session: 1
execution: délégué
plan: .claude/implementation/done/2026-08-31-champs-preremplis.plan.md
brief: .claude/implementation/done/2026-08-31-champs-preremplis.brief.md
audit: .claude/implementation/done/2026-08-31-champs-preremplis.audit.md
créé: 2026-08-31
maj: 2026-08-31
---

## Objectif et périmètre

**Symptôme** : à la création d'un élément, tout champ ou section non fourni reçoit un marqueur
(`<À REMPLIR>` / `<OPTIONNEL>`) qu'il faut remplir à la main, y compris quand la valeur est
mécaniquement connue — « pour une date, une commande, placer directement la date du jour ».

**But** : ajouter deux valeurs optionnelles aux `fields` et aux `sections` d'un `contract.toml` :
`command` (commande Bash dont le résultat sera utilisé comme texte) et `text` (texte utilisé à la
place du placeholder).

**Critères de réussite** :

- `cd skills/list-dir/scripts && uvx pytest tests -q` passe (307 tests verts avant chantier)
- un contrat déclarant `command = "date +%F"` sur un champ `date` produit, à `list-dir new`, un
  élément dont ce champ porte la date du jour et non `<À REMPLIR>`
- un contrat déclarant `text = "…"` produit ce texte à la place du marqueur, champ comme section
- `list-dir migrate` et `list-dir derive` posent la même valeur pour un champ absent
- une `command` qui échoue fait échouer la création : rien n'est écrit, et le message nomme la
  commande incriminée
- un contrat déclarant `text` et `command` sur un même champ est refusé par `parse_contract`, en
  nommant le champ

**Hors-périmètre** :

- pas de variables déclarées au contrat (`[fields.date.env]`)
- les définitions de listes livrées (`defs`) ne sont pas modifiées : moteur + documentation
  seulement
- aucun autre changement du contrat : pas de nouveau `type`, pas de nouvelle commande

**Signaux de dérive** :

- si un mécanisme de substitution ou de gabarit apparaît dans `text` (`{{id}}`, `$VAR`), c'est
  raté : `text` est du texte littéral, le dynamique passe par `command`
- si l'exécution des commandes s'étend au-delà des sites de pose de marqueur (`create`,
  `_realign`, `_project`), s'arrêter et en reparler
- si `gitcmd.py` cesse d'être le seul appel de processus du paquet sans qu'un module dédié à
  l'exécution ait été introduit et documenté, s'arrêter
- si le diff dépasse `types.py`, `contract.py`, `store.py`, un module d'exécution, la doc et les
  tests, s'arrêter et en reparler

## Étapes

- [x] 1. Déclarer `text` et `command` au contrat — `scripts/listdir/types.py`, `scripts/listdir/contract.py`, `scripts/tests/test_contract.py` — vérif: `cd skills/list-dir/scripts && uvx pytest tests/test_contract.py -q`
- [x] 2. Le module `prefill.py` — `scripts/listdir/prefill.py`, `scripts/tests/test_prefill.py` — vérif: `cd skills/list-dir/scripts && uvx pytest tests/test_prefill.py -q`
- [x] 3. Câbler les sites de pose — `scripts/listdir/store.py`, `scripts/tests/test_store_ecriture.py`, `scripts/tests/test_derive_merge.py` — vérif: `cd skills/list-dir/scripts && uvx pytest tests -q`
- [x] 4. Documenter — `references/contrat-liste.md`, `SKILL.md` — vérif: jouer le bloc « Vérification de bout en bout » du plan en copiant les extraits de contrat depuis la doc écrite
- [x] 5. Contrôles finaux — vérif: `cd skills/list-dir && uvx ruff check scripts && cd scripts && uvx pytest tests -q`
- [x] 6. R1 — dissocier le cwd des commandes de `LISTDIR_LIST` — `scripts/listdir/prefill.py`, `scripts/tests/test_derive_merge.py` — vérif: `cd skills/list-dir/scripts && uvx pytest tests -q`
- [x] 7. R10, R11, R12, R8 — `scripts/listdir/prefill.py`, `scripts/listdir/store.py`, `references/contrat-liste.md`, `SKILL.md`, tests — vérif: `cd skills/list-dir && uvx ruff check scripts && cd scripts && uvx pytest tests -q`
- [x] 8. R13 — `text` reste validé en dry-run — `scripts/listdir/prefill.py`, `scripts/listdir/store.py`, `scripts/tests/test_store_ecriture.py` — vérif: `cd skills/list-dir/scripts && uvx pytest tests -q`

- [x] 9. R16, R17, R18, R19, R14, R15 — garde de `preview` testée, docstring de `_realign` alignée, arbitrage du dry-run documenté, message « champ requis » corrigé — vérif: `cd skills/list-dir && uvx ruff check scripts && cd scripts && uvx pytest tests -q`
## État courant

**Prochaine action** : aucune — chantier clos.
**Vérification** : `cd skills/list-dir/scripts && uvx pytest tests -q`
**Dernier audit** : `4c55392` — RÉSERVES — 2026-08-31
**Réserves closes sans traitement** : R2 à R7 versées au registre de dette ; R9 soldée par ce
chantier. Décision de l'utilisateur : clore après traitement de R16-R19, sans cinquième audit.
**Notes** : `uvx ruff format --check` signale 4 fichiers **avant** le chantier — ce n'est pas un
critère. `Contract.section_marker` est supprimé : le câblage de
l'étape 3 lui avait retiré tout appelant.

## Journal de décisions

- **2026-08-31** — `preview()` ne couvre plus que les déclarations portant `command` ; `text` et le
  marqueur repassent par `initial_field` même en dry-run. *Pourquoi* : `text` est littéral, rien à
  exécuter, donc rien qui excuse de sauter `check_value` — un dry-run qui annonce un changement que
  la migration refusera ment. *Rejeté* : valider dans `preview`, qui dupliquerait `initial_field`.
- **2026-08-31** — Troisième audit RÉSERVES sur `0804ab0` : R8, R10, R11, R12 levés ; R13 nouveau,
  traité ; R2 à R7 et R9 restent ouverts, destinés au registre de dette.
- **2026-08-31** — `migrate --dry-run` n'exécute plus aucune `command` : `prefill.preview` nomme
  la commande au lieu de la jouer pour composer le libellé. *Pourquoi* : un mode d'essai qui lance
  du shell arbitraire ne promet plus rien. *Rejeté* : laisser l'effet de bord et le documenter.
- **2026-08-31** — R8 traité pour les seuls fichiers que ce chantier a dégradés
  (`prefill.py`, `test_prefill.py`, `test_derive_merge.py`, `test_store_ecriture.py`). *Pourquoi* :
  le reformatage n'y touche que du code du chantier. *Rejeté* : formater les 4 fichiers déjà non
  conformes sur `master`, hors périmètre.
- **2026-08-31** — Second audit de clôture RÉSERVES sur `29e423c` : R1 levé, tous les critères
  atteints ; onze constats non bloquants restent ouverts.
- **2026-08-31** — R1 corrigé : `PrefillContext` porte un `cwd` distinct de `list_dir`, reculé
  jusqu'au premier ancêtre existant. *Pourquoi* : `LISTDIR_LIST` doit nommer la liste que le champ
  instruit, même quand `derive` ne l'a pas encore créée. *Rejeté* : lancer depuis la liste source
  (`LISTDIR_LIST` mensongère), ou créer la destination avant le calcul (perte de la garantie « rien
  n'est écrit avant que tout soit calculé »).
- **2026-08-31** — Audit de clôture DÉFAVORABLE sur `32918ab` : R1, `command` échoue
  systématiquement en `derive`. *Pourquoi* : la clôture est arrêtée tant que le critère « migrate
  et derive posent la même valeur » n'est pas tenu.
- **2026-08-31** — Le calcul faillible d'une valeur initiale vit dans un module dédié
  `prefill.py` ; `Field.marker` / `Section.marker` restent des propriétés pures. *Pourquoi* : une
  commande peut échouer, une propriété ne rend pas de `Result`. *Rejeté* : rendre `marker`
  faillible, qui contaminerait tous ses appelants.
- **2026-08-31** — `bash -c` est le second et dernier appel de processus du paquet, isolé comme
  `gitcmd.py`. *Pourquoi* : « le seul appel à git du paquet » est une règle explicite du dépôt ;
  l'exécution de shell mérite la même. *Rejeté* : lancer la commande depuis `store.py`.
- **2026-08-31** — `text`/`command` lus par un helper privé unique `_prefill()` de `contract.py`,
  partagé entre les boucles fields et sections. *Pourquoi* : les quatre refus sont identiques des
  deux côtés ; deux copies divergeraient. *Rejeté* : les valider dans chaque boucle.
- **2026-08-31** — Dans `prefill._run`, `subject` (habillage des messages) et `name`
  (`LISTDIR_NAME` brut) restent deux paramètres distincts. *Pourquoi* : les conflater posait
  « champ « titre » » dans la variable d'environnement. *Rejeté* : dériver l'un de l'autre.
- **2026-08-31** — En `derive`, le `PrefillContext` porte la liste ENGENDRÉE (`list_dir = target`),
  pas la source. *Pourquoi* : `LISTDIR_LIST` / `LISTDIR_CONTRACT` désignent la liste que le champ
  instruit. *Rejeté* : le contexte de la source, qui aurait fait mentir les deux variables.
- **2026-08-31** — Validé les trois réserves de `plan-reviewer` : refus de `text`/`command` vides
  et sur un champ de type `list`, sémantique de `LISTDIR_NAME` / `LISTDIR_CONTRACT`, et absence
  d'effet des sections préremplies en `derive`. *Pourquoi* : arbitrages non couverts par le brief,
  tranchés par l'utilisateur.
