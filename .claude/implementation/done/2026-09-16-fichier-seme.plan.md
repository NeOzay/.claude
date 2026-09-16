# Plan — fichier-seme : le skill « gabarit »

Brief : `.claude/implementation/fichier-seme.brief.md` (validé 2026-09-15).

## Relecture par `plan-reviewer` — VERDICT : NON CONFORME

- **Hors-périmètre** — l'étape 6 contredit le brief : « list-dir : comportement et documentation
  identiques ».
  - Le type `int` devient accepté dans list-dir, et `skills/list-dir/references/format.md`
    (« Types admis ») change.
  - L'accord est oral, donné en plan mode : il reste **à trancher** entre retirer `int` de list-dir
    et ratifier l'élargissement.
  - Sur le fond, l'agent ne trouve aucun test de list-dir qui attende le refus d'`int`, et aucun
    signal de dérive n'est déclenché.
- **Critères** : couverts, par les étapes 1 à 6 et 10. **Incertitudes** : levées, aux étapes 4 et 10.
- **Défauts de rédaction relevés, et corrigés sans arbitrage** :
  - Q1 : vérification de l'étape 5 inopérante ; la garde « dérive » est désormais rejouée à chaque étape.
  - Q2 : ordre `create`/préremplissage, déplacé à l'étape 4.
  - Q3 : conversion d'`int` tranchée à l'étape 6.
  - Q4 : imports de tests à l'étape 2, où aucun ne change.
  - Q5 : `new` et `check` séparés, avec un nom de fichier ferme.
  - Q6 : vérification de la semence renforcée.
  - Q7 : diffs de contrôle réels, qui couvrent tous les skills et la documentation de list-dir.
  - Q8 : phrase d'introduction d'`OUTILLAGE.md`.

## Contexte

Créer un fichier préstructuré à remplir depuis une semence ne sait se faire aujourd'hui que dans une
list-dir (`list-dir new <liste> <id>`). On extrait de `listdir` tout ce qui concerne **un fichier**
dans un nouveau paquet `gabarit`, porté par un nouveau skill `skills/gabarit/`. `listdir` en dépend
directement : une list-dir est une liste de gabarits. Le chantier livre aussi une première vraie
semence, celle du suivi d'implementation-tracker. Le tracker ne sera branché dessus que dans un
chantier ultérieur.

### Rappel du cadre (brief)

- **Critères** : la suite de tests de list-dir passe (base : **447 passed**), et seuls ses imports
  sont retouchés. Une vraie semence `suivi` est livrée.
- **Hors-périmètre** :
  - aucun skill existant n'est modifié ;
  - list-dir garde son comportement et sa documentation, seul son code interne bouge ;
  - le tracker n'est pas branché.
- **Signaux de dérive** :
  - un test de list-dir à modifier au-delà des imports ;
  - `gabarit` qui importe quoi que ce soit de `listdir` ;
  - `gabarit` qui gère une notion de répertoire ou de liste.
- **Incertitudes du brief levées ici** :
  - `LISTDIR_*` : injectées par `listdir`, voir étape 4 ;
  - sections sans marqueur du suivi : voir étape 10.

### Élargissement du périmètre (dit, 2026-09-15, en plan mode)

- **Type `int` autorisé**, dans `gabarit` comme dans list-dir : « il n'y a pas de raison
  d'interdire ce type dans list-dir ». Cela modifie le comportement **et** la documentation de
  list-dir (`references/format.md`, « Types admis »). C'est la seule entorse au hors-périmètre ; elle
  sera écrite dans le suivi et au journal, pas dans le brief.

### Arbitrages pris en plan mode (dits)

- **Commandes de `gabarit`** : `new`, `check`, `contract`, `defs`.
- **Localisation de `gabarit` par `listdir`** : par la commande du PATH, `shutil.which("gabarit")`,
  dans `listdir/__init__.py`, avant tout import relatif.

## Principes de découpage

| `gabarit` — un fichier | reste dans `listdir` — une collection |
|---|---|
| `Result`/`ok`/`fail`, marqueurs, `FieldType`/`FieldValue`, `Field`, `Section`, `Violation`, `Item` | `Field.source` (`from`), `Contract.origin`, `Origin`, `nom_mal_forme` à deux segments — par sous-classes ou types propres |
| `items.py` entier : front matter `+++`, fences, sections, sérialiseur tomlkit | `.list/`, `contract_path`, `SEED`/`BACKUP`/`TEMPLATES` |
| parsing d'un champ, d'une section, de `text`/`command`, `check_value`, `is_marker` | `parse_contract` de liste : message « une liste se nomme », ancien format, `[origin]`, `from` |
| confrontation d'un fichier à un contrat (champs, sections, fences) | règle `id` = nom de fichier, ordre des manquements inchangé |
| préremplissage avec un environnement **fourni par l'appelant** | `LISTDIR_*`, `context(list_dir, contract)` à signature inchangée |
| racines de résolution **paramétrées par le nom de répertoire** | `DEFS = "list-dir"`, refus d'un nom de gabarit `a/b` et ses messages |
| `gitcmd.py` | `loader`, `commands/`, `Toolbox`, `store`, `provenance` |

**Règle de conservation** : un module `listdir.X` que les tests importent garde ses noms et ses
signatures. Soit il réexporte depuis `gabarit`, soit il enveloppe le code de `gabarit`. On ne
retouche un import de test que pour un symbole réellement déplacé, **sans** sémantique de liste.
Tout message que les tests vérifient reste produit à l'identique.

## Étapes

Garde « dérive » rejouée **à chaque étape à partir de la 2** (noté `GARDE` ci-dessous) :
`! grep -rnE '^\s*(from|import)\s+listdir' skills/gabarit/scripts`

1. **Squelette du skill et amorce de dépendance**
   - Fichiers : `skills/gabarit/{ruff.toml,pyrightconfig.json}`, `skills/gabarit/scripts/gabarit.py`,
     `skills/gabarit/scripts/gabarit/__init__.py`, `bin/gabarit` (lien relatif),
     `skills/list-dir/scripts/listdir/__init__.py`, `skills/list-dir/pyrightconfig.json` (`extraPaths`).
   - `gabarit.py` reprend les deux gardes de `list-dir.py` : version de Python, ré-exécution dans le venv.
   - L'amorce de `listdir/__init__.py` échoue fermé, en le nommant, si `gabarit` est introuvable dans le PATH.
   - Vérification : `command -v gabarit && .venv/bin/python scripts/sante_skills.py && .venv/bin/python -m pytest skills/list-dir/scripts/tests -q`

2. **Types et I/O d'un fichier vers `gabarit`**
   - Fichiers : `gabarit/{types,items,gitcmd}.py`, `listdir/{types,items,gitcmd}.py`.
   - `listdir.types`, `listdir.items` et `listdir.gitcmd` réexportent : **aucun import de test ne change**.
   - Vérification : `.venv/bin/python -m pytest skills/list-dir/scripts/tests -q && GARDE`

3. **Parsing de contrat et confrontation d'un fichier**
   - Fichiers : `gabarit/{contract,check}.py`, `listdir/{contract,store}.py`.
   - `ListStore.check_item` et `validate` délèguent à `gabarit`.
   - `create` ne bouge pas ici : il dépend du préremplissage, qui passe à l'étape 4.
   - Vérification : `.venv/bin/python -m pytest skills/list-dir/scripts/tests -q && GARDE`

4. **Préremplissage à environnement injecté**
   - Fichiers : `gabarit/prefill.py`, `listdir/{prefill,store}.py`.
   - `gabarit` reçoit `cwd` et un `Mapping[str, str]` d'environnement.
   - `listdir.prefill` garde `PrefillContext`, `context`, `initial_field`, `initial_section` et `preview`, et y met `LISTDIR_*`.
   - `ListStore.create` délègue à ce moment-là.
   - Vérification : `.venv/bin/python -m pytest skills/list-dir/scripts/tests -q && GARDE`

5. **Résolution des semences paramétrée**
   - Fichiers : `gabarit/definitions.py`, `listdir/definitions.py`.
   - `roots(…, dirname)`, `definitions`, `resolve` génériques ; `listdir` fournit `"list-dir"` et garde le refus `a/b`.
   - Vérification : `.venv/bin/python -m pytest skills/list-dir/scripts/tests -q && GARDE`

6. **Type `int`** (élargissement)
   - Fichiers : `gabarit/{types,contract}.py`, `skills/gabarit/scripts/tests/test_int.py`, `skills/list-dir/references/format.md`.
   - Un booléen n'est pas un entier.
   - `text`/`command` sur un `int` : une sortie entière en base 10 est **convertie** en entier à la pose ; toute autre sortie est refusée en la nommant.
   - Vérification : `.venv/bin/python -m pytest skills/gabarit/scripts/tests skills/list-dir/scripts/tests -q && GARDE`

7. **Commande `new`**
   - Fichiers : `skills/gabarit/scripts/gabarit/commandes.py`, `skills/gabarit/scripts/gabarit.py`, `skills/gabarit/scripts/tests/test_new.py`.
   - `gabarit new <nom|--from chemin> <fichier>` :
     - refuse un fichier existant ;
     - refuse une semence qui déclare un champ `gabarit` ;
     - pose tout le contrat avec ses marqueurs et son préremplissage, cwd = premier ancêtre existant du fichier ;
     - estampille `gabarit = "<nom>"` (type `slug`).
   - Vérification : `.venv/bin/python -m pytest skills/gabarit/scripts/tests -q && GARDE`

8. **Commande `check`**
   - Fichiers : `gabarit/commandes.py`, `gabarit.py`, `skills/gabarit/scripts/tests/test_check.py`.
   - `gabarit check <fichier> [--filled] [--def nom|--from chemin]` :
     - retrouve la semence par l'estampille ;
     - un fichier non estampillé sans `--def`/`--from` est un échec nommé ;
     - l'estampille est exclue des champs « non déclarés ».
   - Vérification : `.venv/bin/python -m pytest skills/gabarit/scripts/tests -q && GARDE`

9. **Commandes `contract` et `defs`**
   - Fichiers : `gabarit/commandes.py`, `gabarit.py`, `skills/gabarit/scripts/tests/test_contract_defs.py`.
   - Même contrat de sortie que leurs homologues list-dir, sur les racines `gabarit/`.
   - Vérification : `.venv/bin/python -m pytest skills/gabarit/scripts/tests -q && GARDE`

10. **Semence `suivi`**
    - Fichier : `skills/gabarit/gabarit/suivi/contract.toml` (rang 4).
    - Champs repris de `implementation-tracker/references/contrat.md#frontmatter` : `slug`, `titre`, `branche`, `base`, `statut` (enum), `session` (int, `text = "1"` converti à la pose), `lettre`, `execution` (enum `délégué`/`direct`), `plan`, `brief`, `audit` et `road-map` (facultatifs), `"créé"`/`maj` (date, `command = "date +%F"`).
    - Sections :
      - `Objectif et périmètre`, `Étapes` et `État courant` sont requises, au marqueur ;
      - `Journal de décisions` est facultative ;
      - chaque description dit d'où vient le contenu (brief, plan…).
    - Vérification :
      ```bash
      T=$(mktemp -d) && gabarit new suivi "$T/essai.md" && gabarit check "$T/essai.md" \
      && .venv/bin/python -c "import tomllib,sys; t=open(sys.argv[1]).read().split('+++')[1]; d=tomllib.loads(t); assert d['gabarit']=='suivi' and d['session']==1 and type(d['session']) is int, d" "$T/essai.md" \
      && { gabarit check "$T/essai.md" --filled 2>&1; test $? -eq 1; } | grep -q 'à remplir'
      ```

11. **Documentation et outillage**
    - Fichiers : `skills/gabarit/SKILL.md`, `skills/gabarit/references/*.md`, `OUTILLAGE.md`.
    - Dans `OUTILLAGE.md` : une ligne `gabarit` dans « Ce dont le dépôt dépend », **et** la phrase d'introduction du tableau (« deux commandes ») mise à jour.
    - Vérification : `.venv/bin/python scripts/check_pipeline.py && grep -n 'gabarit' OUTILLAGE.md && ! grep -n 'deux commandes' OUTILLAGE.md`

## Vérification d'ensemble

```bash
.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q
uvx ruff check skills/list-dir skills/gabarit        # base list-dir : 3 erreurs — pas une de plus
uvx --with pytest basedpyright -p skills/list-dir    # base : 13 erreurs — pas une de plus
uvx --with pytest basedpyright -p skills/gabarit     # 0
.venv/bin/python scripts/check_pipeline.py && .venv/bin/python scripts/sante_skills.py
! grep -rnE '^\s*(from|import)\s+listdir' skills/gabarit/scripts
# tests de list-dir : seules des lignes d'import ont changé (sortie vide attendue)
git diff master -- skills/list-dir/scripts/tests | grep -E '^[+-][^+-]' | grep -vE '^[+-]\s*(from|import) |^[+-]\s*$|^[+-]\s+[A-Za-z_]+,?$|^[+-]\s*\)$'
# documentation de list-dir : seul format.md a changé (élargissement int)
git diff master --name-only -- skills/list-dir/SKILL.md skills/list-dir/references | grep -vx 'skills/list-dir/references/format.md'
# aucun autre skill touché (sortie vide attendue)
git diff master --name-only -- skills | grep -vE '^skills/(list-dir|gabarit)/'
```
