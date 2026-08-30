---
slug: renvoi-contrat-des-categories
titre: Le renvoi au contrat remplace la recopie des catégories de verdict
branche: renvoi-contrat-des-categories
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-30-renvoi-contrat-des-categories.plan.md
brief: .claude/implementation/done/2026-08-30-renvoi-contrat-des-categories.brief.md
audit: .claude/implementation/done/2026-08-30-renvoi-contrat-des-categories.audit.md
créé: 2026-08-30
maj: 2026-08-30
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : la doc de `debt-review` porte une copie de ce que le contrat de la liste de revue
déclare — les sept catégories de verdict. Une huitième catégorie ajoutée au contrat laisserait la
prose en décrire sept, sans qu'aucune commande n'échoue (dette
`gabarit-rapport-recopie-les-categories`).

**But** : remplacer la recopie par un renvoi vers le contrat en vigueur, et doter
`list-dir contract` de quoi rendre ce renvoi exécutable avant que la liste de revue n'existe.

**Critères de réussite** :

- `list-dir contract --def technical-debt --template review` imprime `templates/review.toml` de la
  définition ; `--from <chemin de définition>` et `<liste réelle>` font de même sur leur cible
- `list-dir contract "$R" --values category` imprime les sept identifiants, un par ligne, dans
  l'ordre du contrat
- la boucle des piles de `debt-review/SKILL.md:276` n'énumère plus aucun identifiant : elle les
  tire de `--values category`
- `gabarit-rapport.md` ne recopie plus le compte « sept » : il renvoie à la commande
- la suite `skills/list-dir/scripts/tests/` passe

**Hors-périmètre** :

- **le garde-fou sur `categories.md`** — confronter ses sept titres de section aux `values` du
  contrat. Reconnu comme un trou réel, écarté du chantier et à porter au registre de dette
- la prose de `categories.md` elle-même : elle porte le sens de chaque catégorie et sa preuve
  exigée, que le contrat ne porte pas

**Signaux de dérive** :

- si `contract` se met à faire autre chose qu'imprimer — filtrer, juger, reformater — c'est raté.
  `--values` extrait, il ne trie ni ne valide
- si la prose de `categories.md` se fait réécrire, s'arrêter : elle porte le sens, pas la structure

## Étapes

- [x] 1. `contract` accepte trois cibles et un gabarit — `skills/list-dir/scripts/listdir/commands/contract.py`, `scripts/tests/test_entree_cli.py` — vérif: `cd skills/list-dir/scripts && uvx --from pytest pytest tests/ -q`
- [x] 2. `contract --values <champ>` — mêmes fichiers — vérif: `cd skills/list-dir/scripts && uvx --from pytest pytest tests/ -q`
- [x] 3. Documenter la commande étendue — `skills/list-dir/SKILL.md`, `skills/list-dir/references/contrat-liste.md` — vérif: `grep -n "Ce que \`contract\` vise" skills/list-dir/references/contrat-liste.md && list-dir help | grep contract`
- [x] 4. L'ordre des `values` s'écrit dans le contrat — les deux `review.toml` — vérif: `diff skills/implementation-tracker/list-dir/technical-debt/templates/review.toml .claude/implementation/todo/technical-debt/.list/templates/review.toml`
- [x] 5. La boucle des piles cesse d'énumérer — `skills/debt-review/SKILL.md` — vérif: bloc `mktemp`/`derive`/`--values` du plan, étape 5
- [x] 6. Le renvoi dans `gabarit-rapport.md`, et les comptes — `skills/debt-review/` — vérif: `grep -rn "sept" skills/debt-review/ && echo ÉCHEC`
- [x] 7. Solder la dette, ouvrir celle du garde-fou — `.claude/implementation/todo/technical-debt{,-solde}` — vérif: `list-dir validate .claude/implementation/todo/technical-debt --filled`

## État courant

**Prochaine action** : aucune, le chantier est clos.

**Réserves closes avec le chantier** : R4, déjà couverte par l'entrée `ruff-format-jamais-applique`
— son compte de cinq fichiers est exact, l'audit en mesurait quatre depuis `scripts/` et non depuis
`skills/list-dir/`. R6 portée au registre sous `semence-et-copie-divergent-sans-controle`. R11
corrigé avant clôture (docstring de `test_entree_cli.py:538`).

**Vérification** : `cd skills/list-dir/scripts && uvx --from pytest pytest tests/ -q && uvx ruff check .`

**Dernier audit** : `f7c15b9` — RÉSERVES — 2026-08-30

**Notes** : plan relu par `plan-reviewer` avant présentation — verdict `RÉSERVES`. Défauts de
rédaction corrigés (repères de ligne, état courant de l'étape 5, trois vérifications non
concluantes). Réserve restante ratifiée par l'utilisateur à l'approbation : l'étape 6 touche les
comptes « sept » de `categories.md`, que le brief ne carve pas explicitement.

Étape 1 : 294 tests verts, `ruff check` propre, `pyright` sans erreur nouvelle (les 4 restantes
sont des `Import "pytest" could not be resolved`, préexistantes).

Étape 2 : 300 tests verts. Fumée sur le vrai dépôt — `--values category` sur le gabarit `review`
de la définition rend les sept identifiants dans l'ordre du contrat, et la boucle des piles tourne
dessus.

Étape 3 : la vérification prévue au plan était inopérante (voir journal). La prose de
`contrat-liste.md:106` n'était pas devenue fausse — elle parle de `contract_path`, que la commande
ne traverse plus pour une définition. Conservée, et complétée par une section sur les trois cibles.

Étapes 4 à 6 : les deux `review.toml` restent identiques ; la boucle rejouée sur une dérivation
réelle rend 29 fiches et sept piles dans l'ordre du contrat ; `grep -rn "sept" skills/debt-review/`
et `grep -rn "a-solder non-pertinent" skills/debt-review/` sortent muets — **rejoués après chaque
correctif d'audit**, la première fois ne suffisant pas (R7).

Étape 7 : renommage commité seul (`git log --follow` remonte à `d8a06ac`), preuve écrite ensuite.
Les deux registres passent `validate --filled` — 29 entrées actives, 16 soldées. La commande de
`Pour solder` de la nouvelle entrée a été jouée : elle rend `IDENTIQUES` aujourd'hui, donc elle est
exécutable et le garde-fou n'a rien à rattraper dans l'immédiat.

## Journal de décisions

- **2026-08-30** — les blocs shell de la doc affectent, testent, puis lisent ligne à ligne
  (`if ! VAR=$(…); then … ; false; else … while read …`). *Pourquoi* : R1/R9/R10 — une substitution
  avale le code de retour, zsh ne découpe pas une variable, et un `exit` tue le shell de qui colle
  le bloc. *Rejeté* : `|| exit 1`, et `for c in $VAR`.
- **2026-08-30** — audit de clôture `bd85bc7` : DÉFAVORABLE, un bloquant. *Pourquoi* : le
  correctif R1 a réintroduit « sept » dans `SKILL.md:289`, annulant l'étape 6 ; et le suivi
  déclarait passante une vérification jamais rejouée après le correctif.
- **2026-08-30** — la logique de résolution d'un contrat (`list_base`, `source_path`,
  `load_source`, `field_values`) vit dans `listdir/contract.py`, pas dans la commande. *Pourquoi* :
  R5 de l'audit — `init.py` énonce « aucune logique ici », un script tiers doit pouvoir viser « une
  liste ou une définition ». *Rejeté* : la laisser dans la commande, qui aurait fait dupliquer au
  premier autre appelant.
- **2026-08-30** — une `values` ne peut être vide ni contenir d'espace, refusé à la lecture du
  contrat. *Pourquoi* : R2 — une valeur à blanc se découpe en deux pseudo-catégories dans toute
  substitution, comptées à zéro sans qu'aucune commande n'échoue. *Rejeté* : quoter côté appelant,
  qui aurait laissé le contrat produire une donnée impossible à consommer.
- **2026-08-30** — la boucle des piles passe par `while read` sur une variable testée, et non par
  `for c in $(...)`. *Pourquoi* : R1 — `$(...)` avale le code de retour ; et `for c in $VAR` ne
  découpe pas sous zsh, mesuré à une itération sur sept. *Rejeté* : garder `$(...)` en ajoutant un
  test après coup, qui n'aurait plus eu de code de retour à tester.
- **2026-08-30** — la vérification de la suite passe par `uvx --from pytest pytest`. *Pourquoi* :
  ni `python`, ni `pytest`, ni un `python3` porteur du module n'existent dans le `PATH` de cette
  machine ; la commande du plan était inopérante. *Rejeté* : installer pytest globalement, qui
  sortirait du périmètre.
- **2026-08-30** — la prose de `contrat-liste.md` sur `contract_path` est conservée, et une section
  sur les trois cibles ajoutée à côté. *Pourquoi* : elle décrit la fonction de bibliothèque, qui lit
  toujours `<liste>/.list/contract.toml` ; c'est la commande qui a changé, pas elle. *Rejeté* : la
  réécrire, ce qui aurait effacé une garantie encore vraie. *Au passage* : la vérification du plan
  (`grep -q "jamais depuis une définition"`) ne pouvait pas passer — la phrase est coupée par un
  retour à la ligne, le contrôle réussissait quel que soit l'état du fichier.
- **2026-08-30** — `contract` gagne `--def`, `--from` et `--template`, résolus via une **base**
  (`<liste>/.list` ou `<def>`) qui unifie les trois cibles. *Pourquoi* : la liste de revue n'existe
  qu'après `derive`, un renvoi doit donc pouvoir viser le gabarit source. *Rejeté* : citer le
  chemin du fichier en prose — c'est la recopie qu'on supprime.
- **2026-08-30** — `--values <champ>` imprime les valeurs déclarées, une par ligne, dans l'ordre du
  contrat. *Pourquoi* : rend la boucle des piles dérivable sans parser du TOML en shell.
  *Rejeté* : découper la sortie brute en `sed`/`grep`, qui rend une liste vide sans échouer.
- **2026-08-30** — la doctrine « cet ordre est sémantique, pas alphabétique » va en commentaire des
  deux `review.toml`, pas dans la prose de `debt-review`. *Pourquoi* : elle contraint qui édite
  `values`, et doit être sous ses yeux. *Rejeté* : la laisser dans `SKILL.md`, hors de vue.
