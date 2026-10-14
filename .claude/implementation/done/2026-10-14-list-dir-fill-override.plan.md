# Plan — list-dir-fill-override

Brief : `.claude/implementation/list-dir-fill-override.brief.md` (validé). Entrée de road-map :
`list-dir-set`.

## Relecture

```
VERDICT : NON CONFORME
CRITÈRES :
C1 (« sur un pin écrit à false, fill … --override --id <id> le passe à true, et git diff ne montre que la ligne pin ») → Étape 1 (+ vérification de bout en bout)
C2 (« fill --override --all sort en code 2 sans rien écrire ; fill --id sans --override refuse toujours une valeur écrite ») → Étape 1
C3 (« --override échoue sans rien écrire sur un champ list, deprecated, id, absent, et une valeur que le contrat refuse ») → Étape 1
C4 (« une valeur identique à la valeur écrite ne touche aucun fichier : git status --short reste vide ») → Étape 1
C5 (« toggle … inverse le pin, diff limité à la ligne pin ; échoue sur non bool, bool au Marqueur, champ absent ; ne connaît pas --all ») → Étape 2
C6 (« pytest passe avec des tests neufs pour C1 à C5 ; uvx ruff check ., uvx ruff format --check . et uvx --with pytest basedpyright sont propres ») → NON SERVI en partie : tests servis par les Étapes 1-2, mais ruff check (2 E501 déjà présents dans test_fusion.py) et basedpyright (6587 erreurs depuis la racine, 13 dans skills/list-dir) échouent dès maintenant, et aucune étape ne les traite
C7 (« list-dir help liste toggle ; SKILL.md dit "quinze commandes" dans sa description et son titre de section ; operations.md décrit --override et toggle ») → Étapes 2 et 3
HORS-PÉRIMÈTRE : RESPECTÉ
DÉRIVE : aucun
INCERTITUDES : aucune
MODÈLE : sonnet → SOUTENU — travail délimité, surtout du code, 3 étapes, aucune incertitude au Brief
QUALITÉ :
Q1 — La vérification de l'Étape 3 ne peut pas réussir : `uvx ruff check .` (skills/list-dir/scripts/tests/test_fusion.py:268 et :295) et `uvx --with pytest basedpyright` (6587 erreurs depuis la racine, dont skills/synced/ ignoré par git ; 13 dans skills/list-dir) échouent avant toute modification. Le plan ne dit ni s'il les corrige (fichier non nommé), ni s'il compare à la Base. C'est à l'utilisateur de trancher.
Q2 — `uvx rumdl fmt --check .` échoue aujourd'hui sur le seul fichier de plan, .claude/plans/sorted-finding-sutherland.md, qui n'est pas suivi par git ; le contrôle passera une fois ce fichier mis en forme ou sorti de l'arbre.
Q3 — Sous `--override`, une valeur identique rend une liste de changements vide. La CLI affiche alors le message actuel de fill.py:71, « aucun champ « <champ> » au marqueur, aucun fichier touché », qui est trompeur dans ce cas. Le plan ne prévoit pas de l'adapter.
Q4 — Le test de l'Étape 2 vérifie le décompte « Commandes génériques (15) » mais pas que `toggle` apparaît dans `help` (C7) ; le loader le découvre seul, mais le nom n'est pas vérifié.
Q5 — Le « git diff » de C1 et C5 n'est contrôlé que dans la « Vérification de bout en bout », qui n'a pas de commande exécutable ; les tests des Étapes 1 et 2 comparent les lignes du fichier, ce qui revient au même sans être littéralement git diff.
```

Q2, défaut de rédaction : le plan est mis en forme par `rumdl fmt`, et la vérification de
l'Étape 3 passe dans un bloc de code pour tenir aux 100 colonnes ; celle de l'Étape 1 se resserre
en `-k fill`.

Réponses de l'utilisateur :

- **Q1** — Rien de neuf par rapport à la Base. `ruff check` porte sur les fichiers Python
  touchés ; `basedpyright`, lancé dans `skills/list-dir`, ne dépasse pas les 13 erreurs de la Base
  (mesurées le 2026-10-14). Rien de préexistant n'est corrigé. Vérification de l'Étape 3 modifiée.
- **Q3** — Adapter le message : sous `--override`, une valeur déjà en place se dit comme telle.
  Ajouté à l'Étape 1.
- **Q4** — Ajouter l'assertion que `help` nomme `toggle`. Ajoutée à l'Étape 2.
- **Q5** — Comparaison de lignes : les tests comparent le fichier avant et après ; la vérification
  de bout en bout reste manuelle. Plan inchangé.

## Contexte

`list-dir fill` ne pose une valeur que sur un champ resté au Marqueur ; avec `--id`, une valeur
écrite fait échouer l'appel (`ListStore.fill`, `skills/list-dir/scripts/listdir/store.py`). Le
picker `:Dettes` de Neovim doit basculer le `pin` d'une dette sans écrire dans l'entrée. Ce
Chantier ajoute à `fill` une option `--override` et une commande `toggle`, toutes deux sous le
contrôle du contrat.

Rappel du Brief :

- **Critères** C1 à C7 (C6 lu « rien de neuf par rapport à la Base », Q1) : `--override` réécrit, et
  le diff ne montre que la ligne ; il est incompatible avec `--all` (code 2) ; il refuse `list`,
  `deprecated`, `id`, un champ absent et une valeur que le contrat refuse ; une valeur identique ne
  touche aucun fichier ; `toggle` est réservé au `bool` écrit, sans `--all` ; les tests et les
  linters passent ; la doc dit « quinze commandes ».
- **Hors-périmètre** : une commande `set` ; réécrire `list`, `deprecated` ou `id` ; ajouter un champ
  absent ; basculer autre chose qu'un `bool` écrit ; tout ce qui est côté Neovim.
- **Signaux** S1 à S5 : `set` ou `commands/set.py` ; un second chemin d'écriture qui contourne
  `typed_value` ou la reprojection ; `--override` avec `--all` accepté ; le diff touche
  `~/.config/nvim/` ; `toggle` accepte `--all` ou un non-`bool`.
- **Incertitudes** : aucune.

## Modèle

Sonnet : un ajout borné, qui suit des modèles existants (`fill`, ses tests, ses commandes) sans
décision d'architecture ouverte.

## Shadow-skills

`skill-convention` : les fichiers touchés sont ceux d'une skill (prose et Python).

## Conception

**Un seul chemin d'écriture (S2).** La fin de `ListStore.fill` (les `Change`, le `dry_run`, la
boucle `self.write(it.with_fields(...))`) passe dans une méthode privée, `_poser(name, cibles,
dry_run)`. Elle reçoit une liste de paires `(Item, valeur typée)` déjà vérifiées. `fill` et `toggle`
l'appellent toutes deux, et rien d'autre n'écrit. La reprojection reste celle de `write_item`.

**`fill(..., override: bool = False)`** :

- `override` sans `ids` → échec (bibliothèque). La CLI le rend en code 2 avant l'appel.
- Avec `override`, contrôles posés avant toute lecture d'élément :
  - `decl.type == "list"` → échec ;
  - `name == "id"` → échec, en disant que `id` est le nom du fichier.
- `deprecated`, Marqueur passé en valeur et contrôle `typed_value` : inchangés.
- Par `id` :
  - champ absent → échec, comme aujourd'hui ;
  - champ au Marqueur → la valeur est posée ;
  - champ écrit sans `override` → échec, comme aujourd'hui ;
  - champ écrit avec `override` → réécrit, sauf si `forme_texte(actuel) == forme_texte(value)` :
    l'élément est alors sauté, et aucun fichier n'est touché (C4).
- Libellé du `Change` : « « ancien » remplacé par « nouveau » », comme aujourd'hui.

**`toggle(name, ids, *, dry_run=False)`** :

- `ids` vide → échec ;
- champ non déclaré, `deprecated`, ou `decl.type != "bool"` → échec ;
- par `id`, champ absent ou au Marqueur → échec en le nommant ;
- sinon, la valeur inverse est passée par `typed_value(decl, "true"|"false", …)`, ce qui garde le
  même contrôle de type (S2) ;
- tout est vérifié avant `_poser`.

**CLI.**

- `commands/fill.py` : drapeau `--override`. `--override` avec `--all` → `utils.fail(…, code=2)`.
  Le docstring et l'aide disent que l'option réécrit une valeur écrite.
- `commands/toggle.py`, nouveau : `liste`, `champ`, `--id` répétable et requis, `--dry-run`. Pas
  de `--all`. Le loader le découvre seul (`loader.GENERIC_DIR`).

## Étapes

- [ ] 1. `fill --override` : `_poser`, option de bibliothèque et de CLI, tests —
  `skills/list-dir/scripts/listdir/store.py`, `skills/list-dir/scripts/listdir/commands/fill.py`,
  `skills/list-dir/scripts/tests/test_fill.py`, `skills/list-dir/scripts/tests/test_entree_cli.py` —
  vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ -q -k fill`

  Les tests couvrent :
  - la réécriture d'un `bool`, d'un `text`, d'un `int`, d'une `date` et d'un `enum` (C1, C3) ;
  - la seule ligne du champ qui change dans le fichier (C1) ;
  - un Marqueur posé sous `--override` ;
  - une valeur identique qui ne touche aucun fichier, mtime compris (C4) ;
  - les refus sans écriture : `list`, `deprecated`, `id`, champ absent, valeur hors `values`, date
    non ISO, `bool` ambigu (C3) ;
  - `fill --id` sans `--override` qui refuse toujours une valeur écrite (C2) ;
  - en CLI, `--override --all` qui rend le code 2 sans rien écrire (C2), et une réécriture en code
    0 ;
  - en CLI, sous `--override`, une valeur déjà en place annoncée comme telle, et non comme « aucun
    champ au marqueur » (Q3).

  `commands/fill.py` distingue ce message sous `--override` : « valeur déjà en place, aucun fichier
  touché ».
- [ ] 2. Commande `toggle` : méthode de bibliothèque, commande, tests —
  `skills/list-dir/scripts/listdir/store.py`, `skills/list-dir/scripts/listdir/commands/toggle.py`,
  `skills/list-dir/scripts/tests/test_toggle.py`, `skills/list-dir/scripts/tests/test_entree_cli.py`
  — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ -q`

  Les tests couvrent :
  - `true` qui devient `false` et l'inverse, avec la seule ligne `pin` changée (C5) ;
  - plusieurs `--id` en un appel ;
  - les refus sans écriture : non-`bool`, `bool` au Marqueur, champ absent, `deprecated`, `id`
    inconnu (C5) ;
  - `--dry-run` qui n'écrit rien ;
  - en CLI, `toggle --all` qui rend le code 2 (C5), et `help` qui annonce
    « Commandes génériques (15) » et nomme `toggle` (`test_help_seul_ne_montre_que_les_generiques`).
- [ ] 3. Documentation, et contrôle complet — `skills/list-dir/SKILL.md`,
  `skills/list-dir/references/operations.md` — vérif: le bloc ci-dessous, d'un seul tenant

  ```bash
  ~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/ -q \
    && uvx ruff check $(git diff --name-only master -- '*.py') \
    && uvx ruff format --check . \
    && test "$(cd skills/list-dir && uvx --with pytest basedpyright --outputjson \
         | jq '.summary.errorCount')" -le 13 \
    && uvx rumdl fmt --check . \
    && ! grep -n quatorze skills/list-dir/SKILL.md
  ```

  Ce que l'Étape écrit :
  - dans `SKILL.md` : la description et le titre passent à « quinze commandes », `toggle` entre dans
    la liste de la description ; le bloc des commandes gagne `--override` sur la ligne `fill` et une
    ligne `toggle` ; le paragraphe « Ce que `migrate` laisse au Marqueur » dit la réécriture sur
    ordre et la bascule ;
  - dans `operations.md` : la section « Remplir ce que `migrate` laisse au Marqueur » gagne les
    lignes `--override` du tableau, et une sous-section « Basculer un booléen » décrit `toggle`
    (C7).

  Ce que l'Étape ne touche pas : `agents/migrateur-de-liste.md`. Il ne remplit que des Marqueurs,
  et doit continuer de ne rien réécrire.

## Vérification de bout en bout

Sur une copie du registre de dette dans un répertoire temporaire, avec git initialisé :

- `list-dir fill <copie> pin true --override --id <id>` réécrit le pin ;
- `list-dir toggle <copie> pin --id <id>` le bascule de nouveau ;
- après chaque appel, `git diff` ne montre que la ligne `pin` ;
- un second `fill` identique laisse `git status --short` vide.
