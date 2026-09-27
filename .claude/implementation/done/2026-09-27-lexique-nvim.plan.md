# Plan — lexique-nvim : commande Neovim `:Lexique`, alimentée par `lexique`

Brief : `.claude/implementation/lexique-nvim.brief.md` (validé).

## Contexte

Dans Neovim, en relisant des diffs, obtenir le sens d'un terme oblige à aller fouiller les
lexiques. On ajoute `:Lexique` (ouvre le local), `:Lexique!` (ouvre le global) et
`:Lexique <terme>` (affiche la définition, avec complétion). Neovim ne sait rien des lexiques :
tout lui vient de **nouvelles** sous-commandes de `lexique`. Les commandes Neovim vivent dans
`skills/lexique/nvim/lexique.lua`, sourcé à la main, et supprimé une fois l'intégration faite
dans `~/.config/nvim` (autre chantier).

Rappels du brief :
- **Critères** : `:Lexique` / `:Lexique!` ouvrent local / global ; sans local, message « le
  fichier n'existe pas », rien d'ouvert ; `:Lexique <Tab>` propose les termes des deux niveaux ;
  `:Lexique <terme>` affiche la définition par `vim.print()` ; terme composé (`Signal de dérive`)
  défini et complété ; nouvelles commandes testées, pytest vert ; `init`, `liste`, `session`
  inchangées.
- **Hors-périmètre** : l'intégration dans `~/.config/nvim` ; les mappages (mot sous le curseur).
- **Signaux de dérive** : le diff change une commande existante (`init`, `liste`, `session`) ;
  le Lua lit, parse ou cherche dans un `LEXIQUE.md`, ou en construit le chemin.
- **Décisions** : projet = cwd de Neovim ; local = global (cwd `~/.claude`) → « pas de lexique
  local » ; correspondance à la casse et aux espaces près (`normaliser`) ; lexique non conforme →
  termes lisibles servis, anomalie signalée à part, lexique illisible → erreur.
- **Incertitudes** : aucune.

Arbitrages de l'utilisateur sur la relecture (plan-reviewer : NON CONFORME, levé) :
- **Projet** : la CLI est lancée avec `cwd = vim.uv.cwd()` et sans `--projet` ; elle remonte à
  la racine git de ce cwd, comme `liste` et `init`.
- **Illisible** : seul un fichier non UTF-8 ou inaccessible est illisible, et donne une erreur.
  Un fichier malformé sert ses lignes valides ; ses fautes (ligne sans lien, terme sans
  majuscule, cellules, structure du tableau) sont signalées à part, comme les constats de
  `controler()`. Un niveau illisible n'empêche pas de servir l'autre.
- **Note** : la parenthèse du brief « local = global (cwd = `~/.claude`) » est inexacte — depuis
  `~/.claude`, le local est `~/.claude/.claude/LEXIQUE.md` ; le cas se produit depuis `~`, hors
  dépôt. La décision tient ; l'écart va au journal du suivi.

## Existant réutilisé (`skills/lexique/scripts/lexique.py`)

`chemin_global()`, `chemin_local(projet)`, `racine_projet(depart)`, `lire(chemin, niveau)`,
`controler(global_, local)`, `normaliser(terme)`, `_est_le_global(local, global)`, `Result`,
`Terme` (porte `definition`). Aucune de ces fonctions ne change de comportement ; `lire()` est
seulement redécoupé (voir étape 1).

## Interface des nouvelles sous-commandes

Toutes prennent `[--projet DIR]` (défaut : `racine_projet(cwd)`, comme `liste`). Sortie en
lignes tabulées, comme `liste`.

| Commande | stdout | stderr | Code |
|---|---|---|---|
| `lexique chemin [--global]` | le chemin du lexique | pourquoi il n'y en a pas | 0 le fichier existe ; 1 absent, ou local = global |
| `lexique termes` | un terme par ligne, global puis local | constats, fautes de lecture | 0 servi, constats et lignes fautives compris ; 1 un niveau illisible (les termes de l'autre sortent quand même) |
| `lexique definition TERME` | `niveau\tterme\tdéfinition`, une ligne par correspondance | constats, fautes, erreurs, « aucun terme » | 0 au moins une correspondance ; 1 aucune |

`definition` reçoit le terme en un seul argument (`"Signal de dérive"`) et compare par
`normaliser`. Plusieurs correspondances n'arrivent que sur un lexique non conforme : toutes
sortent, et le constat va sur stderr.

## Étapes

### Étape 1 — Bibliothèque : localiser, servir, définir

Fichiers : `skills/lexique/scripts/lexique.py`, `skills/lexique/scripts/tests/test_nvim.py`.

Dans `lexique.py` :
- **Redécoupage de `lire()` sans changement de comportement** : la validation d'une ligne
  (cellules, lien, majuscule) et celle de la structure (un seul tableau, en-tête, séparation)
  sortent en deux fonctions privées, `_ligne()` et `_tableau()`, que `lire()` appelle ; mêmes
  messages, même ordre. Évite de dupliquer les règles du format dans la lecture tolérante.
- `lire_valides(chemin, niveau) -> Result[tuple[list[Terme], list[str]]]` — 1 si le fichier est
  illisible (UTF-8, `OSError`), avec le message de `lire()` ; sinon 0, les termes des lignes
  valides et les fautes des autres. Une structure fautive (aucun tableau, plusieurs, en-tête)
  donne zéro terme et sa faute. Fichier absent : aucun terme, aucune faute.
- `localiser(fichier_global, fichier_local, niveau) -> Result[Path]` — global : 0 si le fichier
  existe, sinon 1 « aucun lexique global (<chemin> absent) » ; local : 1 « pas de lexique
  local : <chemin> est le lexique global » si `_est_le_global`, 1 « <chemin> n'existe pas » si
  absent, sinon 0.
- `@dataclass Service(termes, signalements, erreurs)` et `servir(fichier_global,
  fichier_local) -> Service` — `lire_valides()` par niveau (local ignoré s'il est le global) ;
  signalements = fautes de lignes + `controler()` sur les termes servis ; erreurs = niveaux
  illisibles.
- `definir(termes, terme) -> list[Terme]` — les termes dont `cle == normaliser(terme)`.

Tests (`test_nvim.py`, fixture `ecrire` de `conftest.py`, termes inventés comme
`Zorglubage`) : localiser global / local présent, absent, égal au global ; `lire_valides` sur une ligne sans lien
parmi des lignes valides (valides servies, faute rapportée), sur un fichier non UTF-8
(erreur) ; servir avec un niveau illisible (l'autre servi) et avec un doublon (constat
rapporté) ; definir
à la casse et aux espaces près, terme composé, aucune correspondance.

Vérification :
```bash
cd /home/debian/.claude/skills/lexique && /home/debian/.claude/.venv/bin/python -m pytest scripts/tests && uvx ruff check scripts && uvx --with pytest basedpyright
```

### Étape 2 — CLI : `chemin`, `termes`, `definition`, et la doc

Fichiers : `skills/lexique/scripts/lexique-cli.py`, `skills/lexique/scripts/tests/test_cli_nvim.py`,
`skills/lexique/SKILL.md`.

- Trois sous-parseurs et trois fonctions `_chemin`, `_termes`, `_definition` selon le tableau
  d'interface ; les branches `init`, `liste`, `session` et leurs fonctions ne bougent pas.
  Mettre à jour la docstring du module (régimes d'échec).
- Tests CLI par `subprocess`, sur le modèle de `test_cli.py` : codes et sorties des trois
  commandes, dont `definition "zorglubage  composé"` qui trouve `Zorglubage composé`, et
  `chemin` sur un projet sans local (code 1, « n'existe pas ») ; `termes` sur un local à ligne fautive
  (lignes valides sur stdout, faute sur stderr, code 0).
- `SKILL.md` : les trois commandes dans « La commande » avec leurs codes, une phrase disant
  qu'elles servent `nvim/lexique.lua` ; `init, liste, session` de la description complété.
  Prose selon `skills/skill-convention/references/prose.md`.

Vérification :
```bash
cd /home/debian/.claude/skills/lexique && /home/debian/.claude/.venv/bin/python -m pytest scripts/tests && uvx ruff check scripts && uvx --with pytest basedpyright
cd /home/debian/.claude && git diff --quiet master -- skills/lexique/scripts/tests/test_cli.py skills/lexique/scripts/tests/test_session.py skills/lexique/scripts/tests/test_amorcer.py && echo "tests existants intacts"
```

### Étape 3 — Commandes Neovim : `skills/lexique/nvim/lexique.lua`

Fichier : `skills/lexique/nvim/lexique.lua` (seul).

- `run(args)` : `vim.system({ "lexique", ... }, { text = true, cwd = vim.uv.cwd() }):wait()`
  sous `pcall` (commande absente du `PATH` → `vim.notify` ERROR).
- `nvim_create_user_command("Lexique", …, { nargs = "?", bang = true, complete = … })` :
  - sans argument : `lexique chemin` (`--global` si `!`) ; code 0 → `vim.cmd.edit` du chemin
    rendu (`fnameescape`) ; sinon stderr en `vim.notify` WARN, rien d'ouvert ;
  - avec argument : `lexique definition <args>` ; chaque ligne → `vim.print("<terme> (<niveau>)
    : <définition>")` ; stderr non vide → `vim.notify` WARN (code 0) ou ERROR (code 1) ;
  - `!` avec un argument : refusé par un message (le `!` choisit un fichier à ouvrir).
- Complétion : texte tapé = ce qui suit `Lexique!?` dans `CmdLine` ; candidats = sortie de
  `lexique termes` (stderr ignoré) dont la forme normalisée (`vim.fn.tolower`, espaces réduits)
  commence par celle du texte tapé ; comme Neovim ne remplace que le dernier mot (`ArgLead`),
  rendre pour chaque candidat ses mots à partir du rang du mot en cours.
- Aucune lecture de fichier, aucun chemin construit, aucun `fs_stat` : tout vient de `lexique`.
- En-tête : fichier temporaire, `:source skills/lexique/nvim/lexique.lua` pour l'essayer.

Vérification (lexique global présent ; depuis `/home/debian/.claude`, le local
`.claude/.claude/LEXIQUE.md` est absent ; depuis `/home/debian`, hors dépôt, le local est le global) :
```bash
L=/home/debian/.claude/skills/lexique/nvim/lexique.lua
cd /home/debian/.claude
nvim --headless --clean -c "source $L" -c 'Lexique suivi' -c 'qa!' 2>&1 | grep -F 'Suivi (global) :'
nvim --headless --clean -c "source $L" -c 'Lexique signal  de dérive' -c 'qa!' 2>&1 | grep -F 'Signal de dérive (global) :'
nvim --headless --clean -c "source $L" -c 'lua print(vim.inspect(vim.fn.getcompletion("Lexique Signal de ", "cmdline")))' -c 'qa!' 2>&1 | grep -F '"dérive"'
nvim --headless --clean -c "source $L" -c 'Lexique!' -c 'lua print(vim.api.nvim_buf_get_name(0))' -c 'qa!' 2>&1 | grep -F '/home/debian/.claude/LEXIQUE.md'
nvim --headless --clean -c "source $L" -c 'Lexique' -c 'lua print("buf=" .. vim.api.nvim_buf_get_name(0))' -c 'qa!' 2>&1 | tee /dev/stderr | grep -F "n'existe pas" && ! nvim --headless --clean -c "source $L" -c 'Lexique' -c 'lua print("buf=" .. vim.api.nvim_buf_get_name(0))' -c 'qa!' 2>&1 | grep -F 'buf=/'
(cd /home/debian && nvim --headless --clean -c "source $L" -c 'Lexique' -c 'lua print("buf=" .. vim.api.nvim_buf_get_name(0))' -c 'qa!' 2>&1) | grep -F 'pas de lexique local'
P=$(mktemp -d) && lexique init --projet "$P" && printf '| Zorglubage | Un terme local. | [x](x) |\n' >> "$P/.claude/LEXIQUE.md"
(cd "$P" && nvim --headless --clean -c "source $L" -c 'Lexique' -c 'lua print(vim.api.nvim_buf_get_name(0))' -c 'qa!' 2>&1) | grep -F "$P/.claude/LEXIQUE.md"
(cd "$P" && nvim --headless --clean -c "source $L" -c 'lua print(vim.inspect(vim.fn.getcompletion("Lexique Zorg", "cmdline")))' -c 'qa!' 2>&1) | grep -F '"Zorglubage"'
(cd "$P" && nvim --headless --clean -c "source $L" -c 'Lexique zorglubage' -c 'qa!' 2>&1) | grep -F 'Zorglubage (local) : Un terme local.'
```

## Vérification d'ensemble

- Les suites de commandes des étapes passent.
- Critère « `init`, `liste`, `session` inchangées » et signal de dérive 1 (dont le redécoupage
  de `lire()`, couvert par `test_lire.py` inchangé) — tests existants
  intacts, puis sorties et codes comparés à ceux de `master` :
  ```bash
  cd /home/debian/.claude
  git diff --quiet master -- skills/lexique/scripts/tests/{conftest,test_amorcer,test_cli,test_controler,test_lire,test_projet,test_session}.py && echo "tests existants intacts"
  T=$(mktemp -d) && git archive master LEXIQUE.md skills/lexique | tar -x -C "$T"
  for d in /home/debian/.claude /home/debian "$P"; do
    cmp <(cd "$d" && python3 "$T/skills/lexique/scripts/lexique-cli.py" liste 2>&1; echo "code $?") \
        <(cd "$d" && lexique liste 2>&1; echo "code $?") || echo "liste diffère : $d"
    cmp <(CLAUDE_PROJECT_DIR="$d" python3 "$T/skills/lexique/scripts/lexique-cli.py" session 2>&1; echo "code $?") \
        <(CLAUDE_PROJECT_DIR="$d" lexique session 2>&1; echo "code $?") || echo "session diffère : $d"
  done
  ```
  (`$P` : le projet à lexique local de l'étape 3 ; `init` est couvert par `test_amorcer.py`.)
  Au diff, la réécriture du dispatch de `main()` (`lexique-cli.py`) ne doit qu'ajouter des
  branches.
- Signal de dérive 2 — rien hors commentaires :
  ```bash
  grep -nE 'io\.open|readfile|fs_stat|fs_open|LEXIQUE' skills/lexique/nvim/lexique.lua | grep -vE '^[0-9]+:\s*--' ; test $? -eq 1 && echo "signal 2 : rien"
  ```
