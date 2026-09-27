---
slug: lexique-nvim
---

## 2026-09-27 — clôture — `5312cb8`

**Verdict** : RÉSERVES

Brief, Suivi et Plan lus ; diff `master...lexique-nvim` lu en entier (9 fichiers, +813 −39).
L'écart que le Suivi a journalisé au sujet de la parenthèse du Brief (« local = global » depuis `~`,
pas depuis `~/.claude`) est légitime : il est daté et motivé.

### Vérifications exécutées

- `/home/debian/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests` (depuis la racine,
  la commande du Brief) → 64 passés, 0 échec.
- `cd skills/lexique && …/python -m pytest scripts/tests` → 64 passés, 0 échec.
- `uvx ruff check scripts` → « All checks passed! ».
- `uvx --with pytest basedpyright` (dans `skills/lexique`) → 0 errors, 0 warnings, 0 notes. Même
  résultat sur un arbre `master` extrait par `git archive` : aucune régression de typage.
- `git diff --quiet master -- skills/lexique/scripts/tests/{conftest,test_amorcer,test_cli,test_controler,test_lire,test_projet,test_session}.py`
  → « tests existants intacts ».
- Étape 3, les dix commandes `nvim --headless` du Plan (NVIM v0.13.0-dev), toutes passées :
  - `Lexique suivi` → `Suivi (global) : Fichier d'un Chantier qui porte…` ;
  - `Lexique signal  de dérive` → `Signal de dérive (global) : Indice, lisible dans le diff…` ;
  - `getcompletion("Lexique Signal de ", "cmdline")` → `{ "dérive" }` ;
  - `Lexique!` → le tampon est `/home/debian/.claude/LEXIQUE.md` ;
  - `Lexique` depuis `~/.claude` → `/home/debian/.claude/.claude/LEXIQUE.md n'existe pas.`, `buf=`
    vide, rien d'ouvert ;
  - `Lexique` depuis `/home/debian` → `pas de lexique local : /home/debian/.claude/LEXIQUE.md est le
    lexique global.`, rien d'ouvert ;
  - dans un projet amorcé par `lexique init` avec `Zorglubage` en local : `Lexique` ouvre
    `$P/.claude/LEXIQUE.md` ; `getcompletion("Lexique Zorg")` → `{ "Zorglubage" }` ;
    `Lexique zorglubage` → `Zorglubage (local) : Un terme local.`
- Complétion réelle à `<Tab>` dans la ligne de commande (`feedkeys` puis `getcmdline()`), au-delà
  de `getcompletion` : `Lexique Signal de d` → `Lexique Signal de dérive` ; `Lexique signal de ` →
  `Lexique signal de dérive` ; `Lexique sig` → `Lexique Signal de dérive` ; `Lexique élé` →
  `Lexique Élément` ; `Lexique ÉTA` → `Lexique Étape`. `getcompletion("Lexique ")` dans le projet
  à lexique local rend les 19 termes du global puis `Zorglubage`.
- `init`, `liste`, `session` comparées entre deux arbres extraits (`git archive master` et
  `git archive lexique-nvim`, chemins d'arbre normalisés) : sortie et code **identiques** pour
  `liste` et `session` depuis `~/.claude`, `~`, le projet à local, et six projets fabriqués (lignes
  fautives + doublon + terme réservé, non UTF-8, en-tête fautif, séparation absente, deux tableaux,
  sans lexique) ; `init` identique (pose, contenu, refus d'écraser, codes 0 puis 1) ; appel sans
  commande : code 2 des deux côtés.
- Signal de dérive 2, grep du Plan → « signal 2 : rien » ; aucun littéral de chemin ni `.md` hors
  commentaires dans le Lua.
- `lexique termes` / `definition` / `chemin` sur les six projets fabriqués : lignes valides servies,
  fautes et constats sur stderr, code 0 ; local non UTF-8 → code 1, global servi quand même ;
  `chemin` sans local → code 1, « n'existe pas ».
- Chemin de projet avec espace et `#` : `:Lexique` ouvre le bon fichier (7 lignes lues).

### Conformité à l'intention

- Critère « `:Lexique` ouvre le local, `:Lexique!` le global, après `:source` » : atteint, vérifié.
- Critère « sans lexique local, `:Lexique` affiche que le fichier n'existe pas, sans rien ouvrir » :
  atteint, vérifié (tampon vide après la commande).
- Critère « `:Lexique <Tab>` propose les termes des deux lexiques » : atteint, vérifié.
- Critère « `:Lexique <terme>` affiche la définition avec `vim.print()` » : atteint, vérifié.
- Critère « `:Lexique Signal de dérive` défini, `:Lexique Signal de <Tab>` complété » : atteint,
  vérifié, y compris à la touche réelle.
- Critère « nouvelles commandes testées, suite verte » : atteint — `test_nvim.py` (11) et
  `test_cli_nvim.py` (7), 64/64.
- Critère « `init`, `liste`, `session` inchangées » : atteint, vérifié par comparaison de sorties
  sur neuf projets. Le redécoupage de `lire()` en `_tableau()` / `_ligne()` garde messages et ordre.
- Hors-périmètre : respecté. `~/.config/nvim` ne mentionne pas `lexique`, aucun mappage dans le Lua.
- Signaux de dérive : aucun matérialisé. Le dispatch de `main()` n'ajoute que des branches ; le Lua
  ne lit ni ne construit aucun chemin.
- Symptôme d'origine : disparu, sous réserve d'un essai interactif réel, que le mode headless
  approche sans le remplacer.

### Qualité du code

- **R1** — `skills/lexique/scripts/lexique.py:236-243` — le comportement sur un en-tête fautif
  s'écarte du Plan sans trace au journal, et la docstring de `lire_valides()` le décrit mal. Le
  Plan (étape 1) dit : « Une structure fautive (aucun tableau, plusieurs, en-tête) donne zéro
  terme ». La docstring dit « en-tête ou séparation absente ». Le code sert les lignes sous un
  en-tête fautif : `| Mot | Def | Lien |` puis `| Zorg | ok | [x](x) |` donne `termes` → `Zorg`,
  code 0. Ce comportement suit mieux l'arbitrage de l'utilisateur (« un fichier malformé sert ses
  lignes valides »), mais il n'est ni journalisé ni testé, et un en-tête ne peut pas être
  « absent » (la première ligne d'un bloc tient toujours ce rôle). Le prochain lecteur croira
  qu'un en-tête fautif vide le niveau.
- **R2** — `skills/lexique/nvim/lexique.lua:51` et `skills/lexique/scripts/lexique-cli.py`
  (`definition`) — le terme est passé à `argparse` sans `--`. `:Lexique --global` rend
  `error: the following arguments are required: terme` en ERROR. `:Lexique -h` écrit l'aide sur
  stdout avec un code 0 : le Lua n'y trouve aucune ligne tabulée et rien ne s'affiche, un échec
  silencieux. Aucun terme valide ne commence par `-` (majuscule obligatoire), donc la portée est
  faible, mais une saisie fautive doit produire un message.
- **R3** — `skills/lexique/nvim/lexique.lua:86` — si `lexique` est absent du `PATH`, `complete()`
  passe par `run()`, qui émet un `vim.notify` ERROR à chaque `<Tab>`. En headless, cela remonte en
  exception : `E5108: Lua: Vim:commande `lexique` introuvable…` depuis `getcompletion`. Le Plan
  demandait ce `notify` pour les commandes, pas pour la complétion, où un retour vide suffirait.
- **R4** — `skills/lexique/scripts/tests/test_nvim.py:47-57` — le Plan demandait `lire_valides`
  sur « une ligne sans lien parmi des lignes valides ». Le test écrit `| Autre | sans lien |`, une
  ligne à deux cellules, et vérifie la faute « cellules ». La règle du lien n'est donc pas
  exercée en lecture tolérante. `_ligne()` est partagée avec `lire()`, que `test_lire.py` couvre,
  d'où un risque faible, mais le nom du test annonce une autre règle que celle qu'il vérifie.
  Autres cas non testés (non exigés par le Plan) : plusieurs correspondances pour `definition`,
  `termes` en code 1 au niveau CLI, en-tête fautif (R1).

Le style des fichiers voisins est respecté : nommage français, docstrings « pourquoi », `Result`,
lignes à 100 colonnes, tabulations dans le Lua comme dans `~/.config/nvim`.

### Dette induite

- **R5** — `skills/lexique/scripts/lexique.py:203-265` — `lire()` et `lire_valides()` dupliquent
  une vingtaine de lignes à l'identique : test d'existence, lecture, deux `except` avec leurs
  messages, appel de `_tableau()`, boucle sur `_ligne()`. Le redécoupage devait éviter de
  dupliquer les règles du format ; il le fait pour les règles, pas pour le parcours. Coût futur :
  tout changement du message « illisible » ou de la lecture devra être fait deux fois, sans test
  qui signale un oubli. `lire()` peut s'écrire comme `lire_valides()` suivie d'un repli des fautes
  en échec.
- **R6** — `skills/lexique/SKILL.md:20-21` et la docstring de `lexique-cli.py` nomment
  `skills/lexique/nvim/lexique.lua`, un fichier déclaré temporaire par le Brief. Le chantier
  d'intégration aura lieu dans un autre dépôt (`~/.config/nvim`). Coût futur : la suppression du
  fichier laissera ces deux références périmées dans celui-ci, sans rien qui le rappelle. Il
  faudrait l'inscrire au registre de dette ou à la road-map. Accessoirement, la phrase « la
  commande `:Lexique` d'un chantier en cours » vise un Chantier au sens du lexique global, mais
  écrit le mot en minuscule.

### Bloquants

Aucun.

## 2026-09-27 — clôture — `a30c7ce`

**Verdict** : RÉSERVES

Audit complet après l'étape 4, qui traite R1 à R5 de l'audit précédent. Brief, Suivi et Plan lus ;
diff `master...lexique-nvim` relu en entier (10 fichiers, +962 −42, dont 6 sous `skills/lexique`),
et le commit `a30c7ce` lu à part. Les constats de cette section continuent la numérotation de
l'audit précédent (R7 et suivants), pour que chaque étiquette reste unique dans ce fichier.

### Vérifications exécutées

- `/home/debian/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests` (depuis la racine,
  la commande du Brief) → 67 passés, 0 échec.
- `cd skills/lexique && …/python -m pytest scripts/tests` → 67 passés, 0 échec.
- `uvx ruff check scripts` → « All checks passed! ».
- `uvx --with pytest basedpyright` (basedpyright 1.40.1, dans `skills/lexique`, mode `all`) →
  0 errors, 0 warnings, 0 notes. Même résultat sur l'arbre `master` extrait par `git archive` :
  aucune régression de typage.
- `git diff --quiet master -- skills/lexique/scripts/tests/{conftest,test_amorcer,test_cli,test_controler,test_lire,test_projet,test_session}.py`
  → « tests existants intacts ».
- Étape 3, les dix commandes `nvim --headless` du Plan (NVIM v0.13.0-dev), toutes passées :
  `Lexique suivi` → `Suivi (global) : Fichier d'un Chantier…` ; `Lexique signal  de dérive` →
  `Signal de dérive (global) : Indice…` ; `getcompletion("Lexique Signal de ")` → `{ "dérive" }` ;
  `Lexique!` → tampon `/home/debian/.claude/LEXIQUE.md` ; `Lexique` depuis `~/.claude` →
  `…/.claude/.claude/LEXIQUE.md n'existe pas.`, aucun tampon `buf=/` ; `Lexique` depuis
  `/home/debian` → `pas de lexique local : /home/debian/.claude/LEXIQUE.md est le lexique global.` ;
  projet amorcé par `lexique init` avec `Zorglubage` : `Lexique` ouvre `$P/.claude/LEXIQUE.md`,
  `getcompletion("Lexique Zorg")` → `{ "Zorglubage" }`, `Lexique zorglubage` →
  `Zorglubage (local) : Un terme local.`
- `<Tab>` réel par `nvim_feedkeys` : `Lexique Signal de d` → `Lexique Signal de dérive` ;
  `Lexique signal de ` → `Lexique signal de dérive` ; `Lexique sig` → `Lexique Signal de dérive` ;
  `Lexique élé` → `Lexique Élément` ; `Lexique ÉTA` → `Lexique Étape`. `getcompletion("Lexique ")`
  → 19 termes (le global). `getcompletion("Lexique signal de")` → `{ "de dérive" }`.
- Levée de R2 : `:Lexique -h`, `:Lexique --global`, `:Lexique --` → chacun
  `« <saisie> » : aucun terme correspondant.` en erreur, plus aucun échec silencieux.
- Levée de R3 : `PATH=/usr/bin:/bin`, `getcompletion("Lexique Sig")` → `{}` sans erreur ;
  `:Lexique suivi` et `:Lexique!` → `commande `lexique` introuvable : …ENOENT…`, rien d'ouvert.
- `:Lexique! suivi` → « `!` ouvre le lexique global et ne prend pas de terme » ; `:Lexique Zorgloub`
  → « aucun terme correspondant » en erreur.
- `liste` et `session`, comparées entre deux arbres extraits (`git archive master` et
  `git archive lexique-nvim`, chemins d'arbre normalisés), sortie et code : **26 comparaisons, 0
  différence** — depuis `~/.claude`, `~`, le projet à local, dix projets fabriqués (lignes fautives +
  doublon + terme réservé, non UTF-8, en-tête fautif, séparation absente, en-tête fautif et
  séparation absente, deux tableaux, aucun tableau, en-tête seul, sans lexique), et le cas « local =
  global » reproduit sur les deux arbres (arbre extrait sous un répertoire `.claude`, projet = son
  parent). Sorties inspectées : non triviales (fautes, constats, alertes de `session`).
- `init` : pose, chemin rendu, refus d'écraser (codes 0 puis 1), contenu posé — identiques sur les
  deux arbres. Appel sans commande : code 2 des deux côtés ; seule la ligne `usage:` diffère, par
  l'ajout des trois sous-commandes au choix de `argparse`, ce qui est l'objet du Chantier.
- `lexique termes` / `definition` / `chemin` sur les projets fabriqués : lignes valides servies
  (dont `Zorg` sous un en-tête fautif), fautes et constats sur stderr, code 0 ; local non UTF-8 →
  code 1 ; `definition zorg` sur un doublon → deux lignes, code 0 ; `chemin` sans local → code 1,
  « n'existe pas » ; depuis `~`, `chemin --global` → code 0, `chemin` → code 1, « pas de lexique
  local ».
- Signal de dérive 2, grep du Plan → « signal 2 : rien » ; seuls littéraux de chemin du Lua : deux
  lignes de commentaire d'en-tête.
- Hors-périmètre : `grep -rni lexique ~/.config/nvim` → rien.

### Conformité à l'intention

- Critère « `:Lexique` ouvre le local, `:Lexique!` le global, après `:source` » : atteint, vérifié.
- Critère « sans lexique local, `:Lexique` affiche que le fichier n'existe pas, sans rien ouvrir » :
  atteint, vérifié.
- Critère « `:Lexique <Tab>` propose les termes des deux lexiques » : atteint, vérifié (global seul
  depuis `~/.claude`, global puis `Zorglubage` dans le projet à local).
- Critère « `:Lexique <terme>` affiche la définition avec `vim.print()` » : atteint, vérifié.
- Critère « `:Lexique Signal de dérive` défini, `:Lexique Signal de <Tab>` complété » : atteint,
  vérifié, à la touche réelle.
- Critère « nouvelles commandes testées, suite verte » : atteint — `test_nvim.py` (13) et
  `test_cli_nvim.py` (8), 67/67.
- Critère « `init`, `liste`, `session` inchangées » : atteint, vérifié par comparaison de sorties
  et de codes. `lire()` repose désormais sur `lire_valides()` : même texte, même ordre de fautes.
- Hors-périmètre : respecté.
- Signaux de dérive : aucun matérialisé.
- Symptôme d'origine : disparu, sous la réserve déjà faite qu'un essai interactif réel reste à la
  main de l'utilisateur ; `feedkeys` en approche l'essentiel.

Suite de l'audit précédent :
- R1 — levée : le comportement sous un en-tête fautif est journalisé au Suivi (2026-09-27),
  décrit dans la docstring de `lire_valides()`, et testé
  (`test_lire_valides_sert_les_lignes_sous_un_en_tete_fautif`, `…_sans_ligne_de_separation`).
  Voir R7 pour la docstring restée en retrait.
- R2 — levée : `--` avant le terme dans le Lua, test CLI `…_en_tiret_apres_double_tiret`.
- R3 — levée : `run(args, quiet)`, la complétion rend `{}` sans notification.
- R4 — levée : la ligne fautive du test est `| Autre | sans lien | pas de lien |`, la faute vérifiée
  est « sans lien Markdown ».
- R5 — levée : `lire()` est `lire_valides()` suivie d'un repli des fautes en échec ; la lecture,
  les deux `except` et leurs messages n'existent plus qu'une fois.

### Qualité du code

- **R7** — `skills/lexique/scripts/lexique.py:181-186`, docstring de `_tableau()` — l'étape 4 a
  corrigé la docstring de `lire_valides()` mais pas celle de `_tableau()`, qui dit deux choses
  inexactes. « pour que `lire()` la combine à celles des lignes » : depuis R5, c'est
  `lire_valides()` qui appelle `_tableau()` et combine les fautes, `lire()` ne la voit plus. « Une
  séparation absente est la seule faute de structure qui coupe court » : un nombre de tableaux
  autre qu'un coupe court aussi (`return Result(1, …)` trois lignes plus bas), comme le dit
  d'ailleurs la docstring de `lire_valides()`. C'est le défaut que visait R1, déplacé d'une
  fonction : le prochain lecteur de `_tableau()` se fera une idée fausse de ses sorties.
- **R8** — `skills/lexique/nvim/lexique.lua:91` — la complétion isole le texte tapé par
  `^%s*%a+!?%s+(.*)$`, c'est-à-dire en supposant que `Lexique` est le premier mot de la ligne. Sous
  un modificateur, elle ne rend rien : `getcompletion("silent Lexique ")` → `{}`, `getcompletion("silent
  Lexique Sig")` → `{}`, alors que la commande elle-même s'exécute. Aucun critère ne le demande et
  l'usage est rare ; à connaître pour l'intégration dans `~/.config/nvim`, où le fichier sera
  repris.

Le style des fichiers voisins est respecté dans le code de l'étape 4 : docstrings « pourquoi »,
`Result`, annotations `---@param` / `---@type` dans le Lua, noms de test en phrase.

### Dette induite

- **R6** (maintenu) — `skills/lexique/SKILL.md:20-21` et la docstring de `lexique-cli.py` nomment
  `skills/lexique/nvim/lexique.lua`, fichier déclaré temporaire par le Brief, dont la suppression
  aura lieu depuis un autre dépôt. Inchangé par l'étape 4 ; le Suivi prévoit de l'inscrire au
  registre de dette à la Clôture, ce qui n'est pas encore fait à ce SHA.

Aucune autre dette induite : la duplication de R5 a disparu, sans abstraction nouvelle.

### Bloquants

Aucun.
