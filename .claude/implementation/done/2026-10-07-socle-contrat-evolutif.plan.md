# Plan — socle-contrat-evolutif

Brief : `.claude/implementation/socle-contrat-evolutif.brief.md` (validé le 2026-10-07).

## Contexte

Les Marqueurs sont deux chaînes, `<À REMPLIR>` et `<OPTIONNEL>`, quel que soit le type du champ :
le modèle qui remplit `reviewed = "<OPTIONNEL>"` garde les guillemets et écrit une date en chaîne.
Une List-dir sait ajouter un champ (`reseed` puis `migrate`), pas en retirer un sans perdre la
donnée ni dire quoi en faire. Ce Chantier pose le socle `gabarit`/`list-dir` qui manque — Marqueurs
typés, type `bool`, clé `deprecated`, tri typé et décroissant — pour le Chantier suivant, celui du
registre de dettes.

Rappel du Brief :

- **Critères** : Marqueurs typés posés, reconnus et convertis par `migrate` ; ancien Marqueur
  toléré avec avertissement ; `bool` déclarable, `text = "false"` posé en booléen ; `deprecated`
  sur champs et sections ; `list --sort` décroissant, `enum` dans l'ordre déclaré, `int` en
  nombre ; règle des guillemets dans `contract` et dans la référence de format ; tests et
  linters verts.
- **Hors-périmètre** : le registre de dettes (sévérité, chantier, référence, pin, découpage de
  `source`, migration des listes du pipeline) ; l'adaptation de Neovim.
- **Signal de dérive** : le diff modifie un contrat existant (semence ou `.list/contract.toml`).
- **Incertitude levée ici** : voir « Décisions du Plan », point 1.

## Écart au Brief, décidé à la relecture du Plan

`plan-reviewer` a rendu **NON CONFORME** : le critère « linters propres » est déjà faux sur la
base (`ruff check` : 2 E501 dans `skills/list-dir/scripts/tests/test_fusion.py` ;
`basedpyright` : 6580 erreurs, surtout `skills/synced/`), documenté par les dettes
`ruff-echoue-sur-les-tests-de-list-dir` et `basedpyright-treize-erreurs-non-tenues`.
**Décision de l'utilisateur (2026-10-07)** : le critère devient « **aucune erreur nouvelle par
rapport à la base** ». Le Brief reste figé ; l'écart s'écrit dans le Suivi, section Décisions.
Les constats de qualité Q2 à Q9 sont intégrés ci-dessous, la règle des guillemets restant sur
stderr.

## Décisions du Plan

1. **Types à Marqueur typé** : tous ceux dont la valeur TOML ne s'écrit pas entre guillemets —
   `int`, `date`, `bool`, `list`. `text`, `enum` et `slug` gardent `<À REMPLIR>` / `<OPTIONNEL>`.
   C'est la règle des guillemets elle-même : un Marqueur générique ne reste que là où la valeur
   finale est aussi une chaîne. Les sections, sans type, gardent les Marqueurs génériques.
2. **Forme** : `<À REMPLIR <type>>` / `<OPTIONNEL <type>>`, construite par une seule fonction de
   `gabarit/types.py` à partir des deux constantes existantes — aucune troisième constante
   recopiée.
3. **Reconnaissance** : `is_marker` reconnaît les formes générique et typées. `check_value`
   suspend le contrôle de type sur le Marqueur typé **du type du champ** et sur un Marqueur
   générique (ancien, toléré) ; un Marqueur typé d'un autre type (`<OPTIONNEL int>` sur un `date`)
   est un manquement nommé.
4. **`deprecated`** : chaîne non vide (la consigne). Refusée avec `required = true`, `text` ou
   `command` — un champ qu'on ne pose plus ne se préremplit pas et ne se réclame pas ; le contrat
   contradictoire est nommé plutôt que corrigé en silence. Aucune pose ne le crée : ni `new`
   (`compose`), ni `migrate` (`_realign`), ni `derive` (`_project`).
5. **Avertissements** : une fonction de `gabarit/check.py` rend, pour un fichier, ses notes
   (ancien Marqueur sur un champ typé ; champ ou section `deprecated` encore porté, avec sa
   consigne). `gabarit check` l'appelle sur le fichier lu ; côté liste, une méthode
   `ListStore.notes()` de `store.py` relit les éléments et l'appelle sur chacun, et
   `commands/validate.py` joint le résultat aux notes de provenance. Sortie sur stderr par le
   canal `ok(value, message)` existant, code de retour inchangé.
6. **Tri** : `--sort a,-b` — un `-` en tête de colonne la trie en décroissant. Clé typée par le
   contrat : `int` en nombre, `enum` par rang dans `values`, `bool` faux avant vrai, `date` et
   texte en chaîne. Clé à trois groupes : valeur conforme au type, puis valeur non conforme
   (comparée en texte), puis absente ou au Marqueur — toujours en fin, quel que soit le sens.
   Deux groupes ne se comparent jamais au-delà de leur rang : un type mêlé ne fait pas lever le
   tri, comme la docstring de `_key` le garantit aujourd'hui.
7. **Forme texte d'une valeur** : une fonction publique de `listdir/store.py` (`forme_texte`)
   rend `true`/`false` pour un `bool`, `str()` sinon ; `store.py::_correspond` et
   `commands/list.py::_cell` l'appellent — `--where pin=true` et l'affichage disent la même chose.
8. **Règle des guillemets** : `gabarit contract` et `list-dir contract` (sans `--values`)
   l'écrivent sur stderr ; stdout reste le contrat verbatim, pipable.

## Étapes

Commande de test commune, dite « pytest » plus bas :

```bash
~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/ skills/list-dir/scripts/tests/
```

### 1. Type `bool`

- `skills/gabarit/scripts/gabarit/types.py` : `"bool"` dans `FieldType` (la liste dérivée suit).
- `skills/gabarit/scripts/gabarit/contract.py::check_value` : un `bool` exige
  `isinstance(value, bool)`.
- `skills/gabarit/scripts/gabarit/prefill.py::initial_field` : `text`/`command` valant `true` ou
  `false` posent le booléen ; toute autre sortie est refusée en la nommant, sur le modèle de
  `int`.
- `skills/list-dir/scripts/listdir/store.py` : `forme_texte` (décision 7), appelée par
  `_correspond` et par `commands/list.py::_cell`.
- Tests : `skills/gabarit/scripts/tests/test_bool.py` (sur le modèle de `test_int.py`) ;
  `list --where … =true` et l'affichage dans `skills/list-dir/scripts/tests/test_entree_cli.py`.
- vérif : pytest.

### 2. Marqueurs typés : pose et reconnaissance

- `types.py` : fonction `marker(required, type)` (décision 2), ensemble des types à Marqueur typé
  (décision 1) ; `Field.marker` l'appelle, `Section.marker` inchangé.
- `contract.py` : `is_marker`, `check_value` (décision 3).
- `prefill.py` n'a rien à changer : `initial_field` rend déjà `f.marker`, et la conversion de
  date est gardée par `is_marker`. `store.py::_project` (derive) prend `f.marker` : idem.
- Tests :
  - `skills/gabarit/scripts/tests/test_marqueurs.py` : pose par `new` pour `int`, `date`,
    `bool`, `list` (requis et facultatif) et Marqueur générique pour `text`, `enum`, `slug` ;
    `check` et `check --filled` ; Marqueur d'un autre type refusé ;
  - `skills/list-dir/scripts/tests/test_store_ecriture.py` : `list-dir new` ;
  - `skills/list-dir/scripts/tests/test_store_lecture.py` : `validate` et `validate --filled`
    sur des Marqueurs typés, requis et facultatifs.
- vérif : pytest.

### 3. Ancien Marqueur : avertissement

- `skills/gabarit/scripts/gabarit/check.py` : fonction de notes (décision 5), partie « ancien
  Marqueur ».
- `skills/gabarit/scripts/gabarit/commandes.py::check` : notes sur le fichier lu.
- `store.py` : `ListStore.notes()` ; `skills/list-dir/scripts/listdir/commands/validate.py` :
  notes jointes à celles de provenance.
- Tests : avertissement présent, code de retour inchangé, rien sur un fichier à jour — par
  `gabarit check` et par `list-dir validate`.
- vérif : pytest.

### 4. `migrate` convertit les anciens Marqueurs

- `store.py::_realign` : une valeur générique sur un champ typé devient sa forme typée **en
  gardant son statut** (`<À REMPLIR>` → `<À REMPLIR date>`) ; un `Change` appliqué la nomme.
  Aucune autre valeur touchée ; la reprojection ne réécrit que ce champ.
- Tests (`test_store_ecriture.py`) : conversion, `--dry-run`, rejouabilité (second appel vide),
  commentaires et mise en forme préservés.
- vérif : pytest.

### 5. `deprecated` : lecture, pose, migration, contrôle

- `types.py` : `deprecated: str | None` sur `Field` et `Section`.
- `contract.py::parse_field` / `parse_section` : lecture et refus (décision 4).
- `prefill.py::compose` : saute un champ ou une section `deprecated`.
- `store.py::_project` (derive) : saute un champ `deprecated` du contrat dérivé.
- `store.py::_realign` : ne l'ajoute pas s'il manque ; le garde, à sa place, s'il est présent ;
  `--drop` ne le retire pas (il est déclaré).
- `check.py` : jamais réclamé ni « non déclaré » ; type encore contrôlé s'il est présent.
- Tests : contrat refusé (consigne vide, avec `required`, avec `text`) ; `new` et `derive` sans
  le champ ; `migrate` sans ajout ; `validate` muet sur son absence.
- vérif : pytest.

### 6. `deprecated` : avertissement

- `check.py` : partie « `deprecated` porté » des notes, avec la consigne ; reprise par
  `gabarit check` et `ListStore.notes()` sans autre changement.
- Tests : `gabarit check` et `list-dir validate` avertissent sur stderr, code inchangé, une note
  par fichier qui le porte.
- vérif : pytest.

### 7. Tri typé et décroissant

- `skills/list-dir/scripts/listdir/commands/list.py` : syntaxe `-champ`, clé typée à trois
  groupes (décision 6) ; refus nommé de `-` seul ou d'un champ inconnu ; docstring de `_key` mise
  à jour.
- Tests (`test_entree_cli.py`) : `int` 9 avant 10, `enum` dans l'ordre déclaré, décroissant,
  `bool`, valeur non conforme (`"12"` sur un `int`) sans erreur, Marqueurs et absents en fin dans
  les deux sens, tri multi-colonnes.
- vérif : pytest.

### 8. Règle des guillemets dans `contract`

- `gabarit/commandes.py::contract` et `skills/list-dir/scripts/listdir/commands/contract.py` :
  la règle sur stderr (décision 8), rien avec `--values`.
- Tests : stdout égal au contrat, règle sur stderr.
- vérif : pytest.

### 9. Documentation et lexique

- `skills/gabarit/references/format.md` : sept types, Marqueurs typés, `bool` prérempli,
  `deprecated`, règle des guillemets.
- `skills/gabarit/SKILL.md` : ce qui y cite les Marqueurs.
- `skills/list-dir/references/format.md` et `operations.md` : tables de `validate` et de
  `migrate`, tri de `list`.
- `skills/list-dir/SKILL.md:59` : la syntaxe `--sort` (décroissant).
- `skills/debt-review/references/gabarit-rapport.md` : l'exemple de fiche dérivée porte
  `reviewed = "<À REMPLIR date>"`.
- `LEXIQUE.md` : définition de Marqueur — proposée par la procédure de la skill `lexique`,
  écrite **seulement avec l'accord de l'utilisateur**. Proposition : « Valeur provisoire
  (`<À REMPLIR>`, `<OPTIONNEL>`, ou leur forme typée comme `<OPTIONNEL date>`) qui dit qu'un champ
  ou une section reste à écrire. »
- vérif : `uvx rumdl fmt --check .` (la forme ; le contenu se relit contre les décisions
  ci-dessus).

### 10. Vérification d'ensemble, sans régression

- Aucun contrat touché : `git diff --stat master -- '*contract.toml'` vide.
- Tests complets verts.
- `ruff check`, `ruff format --check` et `basedpyright` : **aucune erreur nouvelle** par rapport
  à la base, comparée sur un arbre extrait (`OUTILLAGE.md`, « Comparer à la base ») — jamais par
  `git stash`.
- vérif :

  ```bash
  ~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/ \
    skills/list-dir/scripts/tests/ scripts/tests/
  TMP=$(mktemp -d); git archive master | tar -x -C "$TMP"
  for d in . "$TMP"; do (cd "$d" && uvx ruff check . --output-format concise | sort); done
  for d in . "$TMP"; do (cd "$d" && uvx --with pytest basedpyright | tail -1); done
  ```

  Les relevés de la branche ne comptent aucune ligne absente de ceux de la base.

## Hors de ce Chantier, à reporter

- `skills/implementation-tracker/references/dette.md:164` cite `reviewed` « resté à
  `<OPTIONNEL>` » : à revoir au Chantier du registre, qui migrera ses listes.
- Neovim (`plugins/listdir/lua/listdir/picker/items.lua:12`, `lua/chantier.lua:14`) ne
  reconnaîtra pas les Marqueurs typés : son propre Chantier.

## Shadow-skills

`skill-convention` (prose des références, style Python).

## Modèle

Sonnet : travail surtout de code, vérifié par des tests à chaque Étape, dix Étapes, et le Plan
tranche l'unique incertitude du Brief.
