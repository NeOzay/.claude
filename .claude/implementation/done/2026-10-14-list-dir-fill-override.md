+++
gabarit = "suivi"
slug = "list-dir-fill-override"
titre = "Permettre à list-dir de réécrire une valeur écrite, et de basculer un booléen"
branche = "list-dir-fill-override"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "sonnet"
plan = ".claude/implementation/done/2026-10-14-list-dir-fill-override.plan.md"
brief = ".claude/implementation/done/2026-10-14-list-dir-fill-override.brief.md"
audit = ".claude/implementation/done/2026-10-14-list-dir-fill-override.audit"
road-map = "list-dir-set"
skills = ["skill-convention"]
"créé" = 2026-10-14
maj = 2026-10-14
+++

## Objectif et périmètre

**Symptôme** : `list-dir` n'a aucune commande pour changer une valeur déjà écrite : `fill` ne pose
une valeur que sur un champ resté au Marqueur, et refuse en le nommant un `--id` dont le champ est
rempli ; le picker `:Dettes` de Neovim doit pourtant basculer le champ `pin` d'une dette (entrée de
road-map `list-dir-set`). « `fill` et `set` font doublon » (dit).

**But** : que `fill` réécrive, sur option, la valeur d'un champ déjà écrit d'un élément désigné,
et qu'une commande `toggle` bascule un booléen écrit, sous le contrôle du contrat, de sorte que
Neovim bascule un pin sans jamais écrire dans une entrée.

**Critères de réussite** :

- **C1** — Sur un pin écrit à `false`, `list-dir fill <dettes> pin true --override --id <id>` le
  passe à `true`, et `git diff` ne montre que la ligne `pin`.
- **C2** — `fill --override --all` sort en code 2 sans rien écrire ; `fill --id` sans `--override`
  refuse toujours une valeur écrite.
- **C3** — `--override` échoue sans rien écrire sur un champ `list`, un champ `deprecated`, le champ
  `id`, un champ absent de l'élément, et une valeur que le contrat refuse (hors `values`, date non
  ISO, `bool` autre que `true`/`false`).
- **C4** — Une valeur identique à la valeur écrite ne touche aucun fichier : `git status --short`
  reste vide.
- **C5** — `list-dir toggle <dettes> pin --id <id>` inverse le pin, et le diff ne montre que la
  ligne `pin` ; la commande échoue sur un champ non `bool`, un `bool` resté au Marqueur ou un champ
  absent, et ne connaît pas `--all`.
- **C6** — `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` passe, avec des
  tests neufs pour chacun des cas de C1 à C5 ; `uvx ruff check .`, `uvx ruff format --check .` et
  `uvx --with pytest basedpyright` sont propres. Amendé le 2026-10-14 : rien de neuf par rapport à
  la Base (voir le Journal de décisions).
- **C7** — `list-dir help` liste `toggle` ; `SKILL.md` dit « quinze commandes », dans sa
  description et dans son titre de section ; `references/operations.md` décrit `--override` et
  `toggle`.

**Hors-périmètre** :

- Une commande `set` distincte : `fill` existe déjà, l'option s'y ajoute (dit).
- Réécrire un champ de type `list`, un champ `deprecated`, ou le champ `id` (dit).
- Ajouter un champ absent de l'élément : la liste se migre d'abord (dit).
- Basculer un champ qui n'est pas un booléen, ou un booléen resté au Marqueur (dit).
- La touche de `:Dettes` qui appelle la bascule, et l'écart entre le Brief de ce Chantier, qui
  attend `list-dir set`, et la commande `toggle` livrée ici : ils se traitent à la reprise du
  Chantier `listdir-dettes-roadmap` de `~/.config/nvim` (dit).

**Signaux de dérive** :

- **S1** — Le diff ajoute une commande `set`, ou un fichier `commands/set.py` (dit).
- **S2** — `toggle` ou `--override` écrit sans passer par le contrôle de type de `fill`
  (`typed_value`) ou sans reprojeter le front matter : un second chemin d'écriture (dépôt:
  `skills/list-dir/scripts/listdir/store.py`, `ListStore.fill` ; validé : dit).
- **S3** — Un test ou un appel combine `--override` et `--all` et attend un succès (dit).
- **S4** — Le diff touche `~/.config/nvim/` (dit).
- **S5** — `toggle` accepte `--all`, ou un type autre que `bool` (dit).

## Étapes

- [x] 1. `fill --override` : `_poser`, option de bibliothèque et de CLI, tests —
  `skills/list-dir/scripts/listdir/store.py`, `skills/list-dir/scripts/listdir/commands/fill.py`,
  `skills/list-dir/scripts/tests/test_fill.py`, `skills/list-dir/scripts/tests/test_entree_cli.py` —
  vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ -q -k fill`
- [x] 2. Commande `toggle` : méthode de bibliothèque, commande, tests —
  `skills/list-dir/scripts/listdir/store.py`, `skills/list-dir/scripts/listdir/commands/toggle.py`,
  `skills/list-dir/scripts/tests/test_toggle.py`, `skills/list-dir/scripts/tests/test_entree_cli.py`
  — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ -q`
- [x] 3. Documentation, et contrôle complet — `skills/list-dir/SKILL.md`,
  `skills/list-dir/references/operations.md` — vérif: le bloc de l'Étape 3 du Plan, d'un seul
  tenant

## État courant

**Prochaine action** : les trois Étapes sont livrées — lancer l'audit de Clôture.

**Vérification** : le bloc de l'Étape 3 du Plan.

**Dernier audit** : 3ec5803 — FAVORABLE — 2026-10-14

**Notes** : `basedpyright`, lancé dans `skills/list-dir`, rend 13 erreurs sur la Base ; `uvx ruff
check .` y relève deux E501 dans `test_fusion.py`. Ni l'un ni l'autre ne se corrige ici.

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien.

**À savoir** :

- Les tests ont déjà leurs outils :
  - `jouet.monter_liste` et `jouet.element` ;
  - `CONTRAT_FILL` dans `test_fill.py`, qui déclare `pin`, `compte` et `ancien` (`deprecated`) ;
  - `CONTRAT_BOOL` et `lancer` dans `test_entree_cli.py`.

  Le `CONTRAT` de `jouet.py` déclare déjà des champs `text`, `date`, `enum` et `list`.
- `test_help_seul_ne_montre_que_les_generiques` attend aujourd'hui « Commandes génériques
  (14) » : il casse dès que `commands/toggle.py` existe, et c'est l'Étape 2 qui le met à jour.
- `agents/migrateur-de-liste.md` n'écrit que par `fill --id`, et compte sur son refus d'une valeur
  écrite. `--override` doit donc rester opt-in : le comportement sans l'option ne change pas.

## Dettes écartées

<OPTIONNEL>

## Journal de décisions

- **2026-10-14** — C6 se lit « rien de neuf par rapport à la Base » : `ruff check` sur les seuls
  fichiers Python touchés, `basedpyright` dans `skills/list-dir` à 13 erreurs au plus, et
  `rumdl fmt --check` sur les seuls fichiers touchés. *Pourquoi* : ces contrôles échouent ou
  signalent déjà des écarts sur `master`, avant toute modification (relecture du Plan, Q1 ;
  `rumdl fmt --check .` sort en 0 malgré 18 problèmes de lint, tous hors du Chantier).
  *Rejeté* : corriger les écarts de la Base ici ; élargir le Brief à un `skills/list-dir` propre.
- **2026-10-14** — Après l'audit FAVORABLE, R1 et R2 sont corrigés (Retouche `AE3.1`) sans nouvel
  audit, à la demande de l'utilisateur ; R3 et R4 vont au registre de dette. *Pourquoi* :
  correctifs de documentation, sans effet sur le code audité. *Rejeté* : relancer un audit complet.
