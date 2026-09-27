+++
gabarit = "suivi"
slug = "lexique-nvim"
titre = "Commande Neovim :Lexique, alimentée par la commande lexique"
branche = "lexique-nvim"
base = "master"
statut = "terminé"
session = 1
lettre = "A"
execution = "délégué"
plan = ".claude/implementation/done/2026-09-27-lexique-nvim.plan.md"
brief = ".claude/implementation/done/2026-09-27-lexique-nvim.brief.md"
audit = ".claude/implementation/done/2026-09-27-lexique-nvim.audit.md"
"créé" = 2026-09-27
maj = 2026-09-27
+++

## Objectif et périmètre

**Symptôme** : en relisant des diffs et en parcourant les fichiers du projet dans Neovim, obtenir
le sens d'un terme demande de quitter l'éditeur ou d'aller fouiller les lexiques.

**But** : obtenir rapidement, depuis Neovim, la définition d'un terme dans le projet du cwd, et
ouvrir d'une commande le lexique local ou global.

**Critères de réussite** :
- Après `:source <fichier Lua>` dans Neovim, lancé depuis un projet doté d'un lexique local :
  `:Lexique` ouvre ce lexique local, `:Lexique!` ouvre le global.
- Depuis un projet sans lexique local, `:Lexique` affiche que le fichier n'existe pas, sans rien
  ouvrir.
- `:Lexique <Tab>` propose les termes des lexiques global et local.
- `:Lexique <terme>` affiche la définition du terme avec `vim.print()`.
- `:Lexique Signal de dérive` affiche la définition du terme composé, et
  `:Lexique Signal de <Tab>` le complète.
- Les nouvelles commandes de `lexique` ont leurs tests, et la suite passe :
  `/home/debian/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests`.
- `init`, `liste` et `session` rendent la même sortie et le même code qu'avant, sur les mêmes
  lexiques.

**Hors-périmètre** :
- L'intégration de `:Lexique` dans la configuration Neovim (`~/.config/nvim`) : elle fera l'objet
  de son propre chantier, dans ce dépôt-là.
- Les mappages, dont celui qui donnerait la définition du mot sous le curseur : ils viendront
  après, sur la commande livrée ici.

**Signaux de dérive** :
- Le diff change le comportement ou la sortie d'une commande existante de `lexique` (`init`,
  `liste`, `session`) : les besoins de Neovim passent par de nouvelles commandes.
- Le Lua lit, parse ou cherche lui-même dans un `LEXIQUE.md` ou en construit le chemin : tout ce
  qu'il sait d'un lexique vient de la commande `lexique`.

## Étapes

- [x] 1. Bibliothèque : localiser, servir, définir — `skills/lexique/scripts/lexique.py`, `skills/lexique/scripts/tests/test_nvim.py` — vérif: `cd /home/debian/.claude/skills/lexique && /home/debian/.claude/.venv/bin/python -m pytest scripts/tests && uvx ruff check scripts && uvx --with pytest basedpyright`
- [x] 2. CLI : `chemin`, `termes`, `definition`, et la doc — `skills/lexique/scripts/lexique-cli.py`, `skills/lexique/scripts/tests/test_cli_nvim.py`, `skills/lexique/SKILL.md` — vérif: même commande que l'étape 1, puis `git diff --quiet master` sur les tests existants (plan, étape 2)
- [x] 3. Commandes Neovim — `skills/lexique/nvim/lexique.lua` — vérif: les commandes `nvim --headless` du plan, étape 3
- [x] 4. Réserves R1 à R5 de l'audit de clôture — `skills/lexique/scripts/lexique.py`, `skills/lexique/scripts/tests/test_nvim.py`, `skills/lexique/scripts/tests/test_cli_nvim.py`, `skills/lexique/nvim/lexique.lua` — vérif: la commande de l'étape 1, les commandes `nvim --headless` de l'étape 3, et la « Vérification d'ensemble »

## État courant

**Prochaine action** : aucune — chantier clos, aplati sur `master`.
**Vérification** : la « Vérification d'ensemble » du plan — tests existants intacts, sorties de `liste` et `session` comparées à `master`, grep du signal 2 sur le Lua. La comparaison se fait entre deux copies extraites (`git archive master` contre une copie de l'arbre courant) : un seul `git archive` face à la commande installée déplace le global et fausse le cas lancé depuis `~`.
**Dernier audit** : a30c7ce — RÉSERVES — 2026-09-27
**Notes** : plan relu par plan-reviewer (NON CONFORME), levé par les arbitrages de l'utilisateur inscrits au plan.

## Journal de décisions

- **2026-09-27** — Seul un fichier non UTF-8 ou inaccessible est « illisible » ; un lexique malformé sert ses lignes valides, fautes signalées à part. *Pourquoi* : une faute de frappe ne doit pas couper tout un niveau de la complétion. *Rejeté* : tout échec de `lire()` vaut illisible.
- **2026-09-27** — Le projet est la racine git du cwd de Neovim (CLI lancée sans `--projet`), comme `liste`. *Pourquoi* : cohérence avec les commandes existantes. *Rejeté* : le cwd tel quel en `--projet`.
- **2026-09-27** — Écart au brief : sa parenthèse « local = global (cwd = `~/.claude`) » est inexacte ; ce cas se produit depuis `~`, hors dépôt. *Pourquoi* : depuis `~/.claude`, le local est `~/.claude/.claude/LEXIQUE.md`. *Rejeté* : modifier le brief figé.
- **2026-09-27** — Audits de clôture : `5312cb8` RÉSERVES (R1–R5 traités en étape 4), `a30c7ce` RÉSERVES (R7, docstring de `_tableau()`, corrigée sans nouvel audit sur décision de l'utilisateur) ; R6 et R8 au registre de dette. *Pourquoi* : aucun bloquant, R7 ne touche qu'une docstring. *Rejeté* : un troisième audit.
- **2026-09-27** — Un en-tête fautif n'empêche pas de servir les lignes valides dessous ; seuls une séparation absente ou un nombre de tableaux ≠ 1 donnent zéro terme. *Pourquoi* : fidèle à l'arbitrage « un fichier malformé sert ses lignes valides » (R1). *Rejeté* : zéro terme sous un en-tête fautif, comme l'écrivait le plan.
