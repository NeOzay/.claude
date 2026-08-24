# Suite de tests du paquet `listdir`

## Contexte

Le commit `53eff2d` a livré `skills/list-dir/` — 19 modules, 2306 lignes de Python — sur lequel
tout le pipeline de dette repose désormais. Il n'a **aucun test**. Ses deux seuls défauts connus
ont été trouvés par un auditeur qui *lisait le code*, pas par une commande : `init_list` écrivait
un `contract.toml` que `tomllib` refuse tout en rendant 0 sur un `--name` contenant un guillemet,
et `parse_sections` découpait sur les `## ` situés à l'intérieur d'un bloc de code. Les deux
touchent le cœur du paquet et ont survécu à toutes les vérifications d'étape.

Ce qui tient lieu de vérification aujourd'hui : `ruff`, `basedpyright`, et des exécutions manuelles
recopiées à la main dans la section *Preuves d'exécution* des suivis de chantier — qui ne se
rejouent pas seules. Le coût réel est celui de la non-régression : à chaque correctif il faut
rejouer 13 contrôles à la main, ce qui sera un jour sauté.

Résultat attendu : une suite `pytest` rejouable en une commande, qui **garantit et cadre** le
comportement du paquet — logique métier et commandes — et rend la non-régression gratuite.

Brief : `.claude/implementation/tests-listdir.brief.md`.
Entrée de dette soldée : `.claude/implementation/todo/technical-debt/listdir-sans-suite-de-tests.md`.

## Décisions de cadrage (arbitrées, non rediscutées ici)

- **Emplacement** : `skills/list-dir/scripts/tests/`. Symétrie exacte avec `scripts/tests/`
  existant ; `pyrightconfig.json` (`include: ["scripts"]`, `extraPaths: ["scripts"]`) les couvre
  sans retouche, et le skill reste déployable d'un bloc.
- **Niveau** : le gros des cas passe par la **bibliothèque importée** (`from listdir import …`) —
  `Result[T]` rend les échecs inspectables sans capturer de sortie. La CLI n'est exercée en
  sous-processus que pour ce qu'elle seule porte : codes de sortie, messages sur stderr, garde de
  version. `list-dir.py` porte un tiret : il n'est pas importable, le sous-processus est la seule
  voie.
- **Correction en même temps** : un comportement jugé faux se corrige dans ce chantier. Sinon il
  faudrait réécrire les tests en permanence. **Borne** : toute modification de `listdir/` qui n'est
  pas la correction d'un comportement qu'un test nomme s'arrête et se discute ; si le diff sur
  `listdir/` dépasse le diff sur les tests, la ligne est franchie.
- **Hors-périmètre** : `debt-review` et les trois registres de `todo/` — l'invariant
  `grep -ril 'dette\|debt' skills/list-dir/` → aucun résultat doit tenir. Pas de CI, pas de seuil
  de couverture chiffré, aucune refonte du paquet.

## Modèle à reprendre

`scripts/tests/conftest.py` (commit `c71e6fe`) pose la forme :

- **le dépôt-jouet est la brique de base** — chaque test monte sur `tmp_path` l'arborescence
  minimale qui déclenche ou non le comportement visé ;
- **aucun test ne lit le vrai dépôt** — « un contrôle qui passerait au vert seulement ici serait
  invérifiable » ;
- `sys.path.insert` dans le `conftest.py`, un helper d'écriture partagé (`ecrire`), des fixtures
  nommées en français, `from __future__ import annotations` en tête.

Ici l'insertion vise `scripts/` : `Path(__file__).resolve().parent.parent`, ce qui rend
`import listdir` disponible.

**Piège de nommage à respecter** : pytest en mode « prepend » dérive le nom de module du *basename*
du fichier. Deux suites coexistent désormais dans le dépôt, aucune ne portant de `__init__.py` :
tout fichier de test de cette suite doit porter un nom qui n'existe pas déjà dans `scripts/tests/`
(`test_controle_*`, `test_controles_4_5`, `test_bout_en_bout`). Les noms ci-dessous respectent
cette contrainte.

## Étapes

1. **Amorçage : `conftest.py` et fixtures partagées**
   Créer `skills/list-dir/scripts/tests/conftest.py` : `sys.path.insert` vers `scripts/`, helper
   `ecrire(root, rel, contenu)`, constante du texte de contrat minimal, et deux fixtures — `liste`
   (un répertoire-liste valide sur `tmp_path`, contrat à quelques champs couvrant les cinq types et
   deux sections, une requise une optionnelle) et `liste_vide` (contrat seul, aucun élément). Un
   premier `test_amorcage.py` prouve que `open_list` ouvre la fixture et que `items()` rend une
   liste vide.
   — vérif : `uvx pytest skills/list-dir/scripts/tests -q` vert

2. **`test_items.py` — lecture, sérialisation, frontière des deux règles**
   `split_front` (délimiteur absent, non fermé, cas nominal) ; `outside_fences` et `parse_sections`
   (un `## ` dans un bloc ``` ou ~~~ n'ouvre pas de section ; clôture plus courte ; clôture avec
   info string qui n'en est pas une ; ce qui précède le premier `## ` est ignoré) ; **l'aller-retour
   octet pour octet** — `read_item` puis `render_item` ne change pas un octet, guillemets et ordre
   des clés compris (règle 1) ; **la frontière** — un `with_fields` met `raw_front` à `None` et
   déclenche la resérialisation (règle 2) ; `dump_value` sur chaque type déclarable, `bool` avant
   `int`, échappement de `\n`/`\r`/`\t`/`\b`/`\f`, `SerialiseError` nommé sur caractère de contrôle
   et sur type hors contrat ; `write_item` puis `read_item` relit ce qui a été écrit.
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_items.py -q` vert

3. **`test_contract.py` — le contrat et la confrontation d'une valeur**
   `parse_contract` : chaque échec nommé (TOML invalide, `fields` non-table, type inconnu, enum sans
   `values`, `from` non-chaîne, section à la fois requise et optionnelle, `name` manquant) et le cas
   nominal. `load_contract` sur contrat absent. `check_value` sur les cinq types (`slug` avec espace
   ou bord blanc, `text` vide, `date` ISO valide/invalide et `datetime.date` accepté, `enum` hors
   valeurs, `list` non-liste et liste d'entiers) et **la suspension du contrôle de type sur un
   marqueur** — `date = "<À REMPLIR>"` se signale *à remplir*, jamais *type invalide*. `is_marker`
   ne reconnaît ni la chaîne vide, ni `None`, ni un tiret.
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_contract.py -q` vert

4. **`test_store_lecture.py` — lire, filtrer, valider**
   `paths()` ne rend que les `*.md` de la racine — un fichier posé sous `.list/` n'est jamais un
   élément, un `README.md` à la racine en est un ; `get` sur id inconnu ; `where` refuse un champ
   non déclaré en nommant les champs connus, et cumule les critères. `validate` : **les deux
   verdicts** — `filled=False`, les marqueurs sont légitimes ; `filled=True`, plus aucun marqueur
   sur un requis mais **jamais de réclamation sur un facultatif** ; une liste vide est conforme ;
   champ non déclaré, champ requis manquant, section non déclarée, section requise manquante ou
   vide ; le contrôle propre à `id` (sa valeur suit le nom du fichier).
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_store_lecture.py -q` vert

5. **`test_store_ecriture.py` — créer et migrer**
   `create` préremplit **tout** le contrat, requis comme facultatifs, chacun au marqueur de son
   statut, `id` posé au nom du fichier ; refus si le fichier existe. `migrate` : champ et section
   manquants ajoutés au bon marqueur, réordonnancement selon le contrat, **rejeu sans écriture**
   (une seconde migration rend zéro changement et ne touche aucun `mtime`), un champ non déclaré est
   *conservé et signalé* avec `applied=False` — donc rien n'est réécrit pour lui seul — et `drop=True`
   le retire ; `dry_run=True` n'écrit rien. `init_list` : contrat déjà présent refusé, et **la
   régression du guillemet** — `init_list(dir, name='ma "liste"')` produit un contrat que
   `tomllib` relit.
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_store_ecriture.py -q` vert

6. **`test_derive_merge.py` — projeter et agglomérer**
   `derive` : le corps vient du gabarit et **jamais** de la source ; un champ portant `from` reçoit
   la valeur du champ nommé, sans `from` il reçoit son marqueur ; `id` reporté d'office ; un `from`
   qui ne nomme aucun champ du contrat source échoue **sans rien créer** (atomicité : la destination
   n'existe pas après l'échec) ; destination existante refusée ; gabarit à moitié présent, le
   fichier manquant est nommé ; liste source vide refusée.
   `merge_text` : liste vide refusée ; un marqueur restant sur un requis fait échouer (`validate(filled=True)`
   implicite) ; une section restée au marqueur facultatif est omise ; le décalage `##`/`###` ; **le
   recomptage de conservation hors blocs de code** — un élément dont une section colle une sortie de
   commande contenant `## ` s'agglomère sans faux positif. `merge` écrit le fichier et crée les
   répertoires manquants.
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_derive_merge.py -q` vert

7. **`test_move.py` — déplacer, sur un dépôt git jetable**
   Fixture : `tmp_path` + `git init`, identité locale, deux listes, un commit initial. `move` est un
   **renommage pur** — après le déplacement, `git status --porcelain` montre un `R`, le fichier n'a
   pas été réécrit, et `git log --follow` sur la destination remonte au commit de création dans la
   liste de départ. Refus : élément introuvable, même liste en source et cible, destination déjà
   occupée (« rien n'est déplacé »). `check_item` sur le contrat d'arrivée rappelle sans refuser.
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_move.py -q` vert

8. **`test_loader.py` — découverte, surcharge, dépendances**
   `_read_meta` lit `DESCRIPTION`/`REQUIRES` sous les **deux** formes d'affectation (`Assign` et
   `AnnAssign` annotée) et **sans importer le module** — un module au Python cassé est rapporté
   `broken` et les autres restent listés. `discover` : une commande de liste masque une générique
   (`overrides=True`) ; une surcharge de `validate`, `help` ou `migrate` est **refusée et
   rapportée**, jamais ignorée. `check_requires` échoue en nommant l'outil absent. `Toolbox.run`
   appelle une générique depuis une commande.
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_loader.py -q` vert

9. **`test_entree_cli.py` — ce que la CLI seule porte**
   En sous-processus (`sys.executable` + chemin de `list-dir.py`), sur des listes montées dans
   `tmp_path` : aucun argument → code 2 et usage sur stderr ; commande inconnue → code 2 nommant les
   commandes connues ; surcharge protégée → code 1 ; échec de commande → code non nul, message sur
   **stderr** et stdout vide ; succès → code 0 et la valeur sur stdout ; `help` sans liste ne montre
   que les génériques, avec une liste montre ses commandes propres ; `move` sur un dépôt sans `git`
   dans le `PATH` (env restreint) sort non nul **en nommant `git`**.
   — vérif : `uvx pytest skills/list-dir/scripts/tests/test_entree_cli.py -q` vert

10. **Passe finale : linters, suite complète, invariant de généricité**
    Relancer l'ensemble, vérifier que la suite existante n'a pas été perturbée, et que le skill
    reste ignorant de ses consommateurs. Consigner au suivi les correctifs éventuellement apportés à
    `listdir/` et les constats laissés ouverts (ils iront au registre de dette à la clôture).
    — vérif, depuis la racine du dépôt, chaque ligne indépendante :
    ```
    uvx pytest skills/list-dir/scripts/tests -q
    uvx pytest scripts/tests -q
    (cd skills/list-dir && uvx ruff check .)
    (cd skills/list-dir && uvx --with pytest basedpyright)
    ! grep -ril 'dette\|debt' skills/list-dir/   # doit ne RIEN trouver : grep sort 1
    ```

## Fichiers touchés

- **Créés** : `skills/list-dir/scripts/tests/conftest.py`, `test_amorcage.py`, `test_items.py`,
  `test_contract.py`, `test_store_lecture.py`, `test_store_ecriture.py`, `test_derive_merge.py`,
  `test_move.py`, `test_loader.py`, `test_entree_cli.py`.
- **Modifiés** : `skills/list-dir/scripts/listdir/*` **uniquement** pour corriger un comportement
  qu'un test nomme, et rien d'autre. Peut rester vide.
- `.gitignore` : **rien à faire**, vérifié — la racine porte déjà `__pycache__/` sans ancrage, qui
  couvre la nouvelle arborescence (`git check-ignore skills/list-dir/scripts/__pycache__` → ignoré).

## Vérification de bout en bout

```
uvx pytest skills/list-dir/scripts/tests -q
uvx pytest scripts/tests -q
(cd skills/list-dir && uvx ruff check . && uvx --with pytest basedpyright)
```

`--with pytest` n'est pas un ornement : sans lui `basedpyright` rend des dizaines d'erreurs
d'import `pytest` non résolu qui noient les vraies (constaté à l'audit du 2026-08-24,
`skills/implementation-tracker/references/contrat.md`).

## Risque assumé

Le volume réel du chantier n'est pas connu avant d'avoir écrit les tests : on ne sait pas combien de
correctifs dorment. C'est l'incertitude reportée du brief, et ce qui impose `execution: direct`. Si
les correctifs s'accumulent au point de dépasser les tests en volume, le signal de dérive se
déclenche et l'arbitrage revient à l'utilisateur.
