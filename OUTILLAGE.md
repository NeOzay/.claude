# Outillage du dépôt

Ce que ce dépôt exige de son environnement pour tourner, et **comment lancer chaque outil**. Ces
règles valent pour tout le dépôt — skills, scripts, agents — et pas pour un skill en particulier :
elles vivaient dans le contrat du pipeline d'implémentation, où deux autres skills allaient déjà
les chercher.

Ce fichier n'est pas chargé dans les sessions : `CLAUDE.md`, lui, l'est pour tous les projets, et
l'outillage d'un dépôt n'a rien à y faire.

---

## Ce dont le dépôt dépend

Le dépôt dépend de sept commandes, d'un interpréteur, de git, de deux linters et d'un formateur
Markdown — et de rien d'autre :

| Dépendance | Ce qui en dépend | Contrôle |
|---|---|---|
| `list-dir` | les six registres de `todo/`, `debt-review` | `command -v list-dir` |
| `impl-list` | la Phase 0 du tracker, le listing des suivis | `command -v impl-list` |
| `gabarit` | le paquet que `list-dir` importe, la semence `suivi` | `command -v gabarit` |
| `shadow-skill` | la recherche des Shadow-skills au brief, au plan et à la reprise d'un Chantier | `command -v shadow-skill` |
| `contexte` | la taille du contexte d'une session, écrite par la statusline, lue par l'agent d'un Chantier | `command -v contexte` |
| `commit-chantier` | la lettre des tags d'étape et l'aplatissement d'un Chantier à sa Clôture, par `git-smart-commit` | `command -v commit-chantier` |
| `lexique` | la tenue des lexiques, et `:Lexique` dans Neovim | `command -v lexique` |
| Python ≥ 3.12 | `list-dir`, `gabarit` et `shadow-skill` (syntaxe PEP 695) | chacune sort non nul en nommant la version trouvée |
| `git` | `move`, l'aplatissement de clôture | déclaré par `REQUIRES` dans la commande, vérifié avant appel |
| `ruff`, `basedpyright` | la vérification et le formatage du code Python versionné | **absents du `PATH`** : se lancent par `uvx ruff check .`, `uvx ruff format --check .` et `uvx --with pytest basedpyright` |
| `rumdl` | le formatage du Markdown versionné | **absent du `PATH`** : se lance par `uvx rumdl fmt .`, et `uvx rumdl fmt --check .` pour vérifier |

**Ces commandes sont des liens de `bin/`, résolus par le `PATH`.** Rien ne les cite par leur
chemin : un chemin de plus serait un point d'édition de plus, que le prochain déplacement
casserait en silence. Leur présence, la validité de chaque lien et le fait qu'aucun homonyme ne
gagne dans le `PATH` sont vérifiés **une fois par session** par `scripts/sante_skills.py`, branché
sur `SessionStart` — et non par une garde recopiée dans chaque bloc.

> **Un exécutable de skill invoqué depuis un `.md` s'expose dans `bin/`, et s'appelle par sa
> commande.** Il n'y a pas d'autre forme correcte, et les deux contrôles du garde-fou le
> démontrent ensemble : le contrôle 6 refuse le chemin relatif — inopérant hors du dépôt de
> skills, où il rend 127 et une sortie vide — et le contrôle 7 refuse l'ancrage sur le `HOME`,
> qui suppose une installation dans `~/.claude`. Un script qu'aucun `.md` n'invoque n'a pas
> besoin de lien ; dès qu'un `.md` l'appelle, il lui en faut un.

**Une machine neuve demande un geste, et un seul** : ajouter `bin/` au `PATH` depuis le profil du
shell, `export PATH="$HOME/.claude/bin:$PATH"`. C'est la seule chose que le dépôt ne peut pas se
donner à lui-même — un fichier versionné ne modifie pas l'environnement de son lecteur. Sans elle,
`scripts/sante_skills.py` le dit au démarrage de la session suivante, en nommant la ligne à
ajouter.

> *Mode de défaillance* — de tout le `stderr` d'un hook en échec, l'hôte n'affiche que la
> **première ligne** (constaté le 2026-08-29). Un diagnostic étalé sur plusieurs lignes y perd
> tout sauf son en-tête. D'où la forme du script : une ligne unique et complète sur `stderr` pour
> l'utilisateur, le détail sur `stdout` — que `SessionStart` reprend dans le contexte du modèle,
> lequel est le premier concerné puisque c'est lui qui lance les commandes.

Un chemin de skill **cité** — un répertoire, un module, un fichier de référence — s'écrit
relativement à la racine du dépôt (`skills/list-dir/scripts/`), et un renvoi documentaire vers un
autre skill s'écrit relativement au fichier courant. Une bibliothèque importée se localise depuis
la commande qui l'expose — son lien de `bin/`, trouvé en remontant ou par `shutil.which` —, jamais
par une constante.

> *Mode de défaillance* — les deux linters n'étant pas installés, un audit qui les appelle par leur
> nom les rapporte « non exécutés » et rend un verdict amputé sans que rien n'échoue. C'est arrivé
> à l'audit du 2026-08-23. Le lanceur fait partie de la dépendance : l'écrire ici est ce qui la rend
> exécutable par quelqu'un d'autre.
>
> *Mode de défaillance* — `--with pytest` n'est pas un ornement : depuis que le dépôt porte des
> tests, `uvx basedpyright` seul rend 52 erreurs d'import `pytest` non résolu, qui noient les
> vraies. Constaté à l'audit du 2026-08-24. `uvx` monte l'environnement le temps de l'appel : rien
> n'est installé, et la commande reste rejouable par quelqu'un d'autre.

**Une dépendance se déclare, elle ne se suppose pas.** Une commande de `list-dir` nomme les outils
externes dont elle a besoin dans son `REQUIRES`, et le chargeur les cherche dans le `PATH` **avant**
d'appeler la commande : outil absent → sortie non nulle qui le nomme, jamais un travail à moitié
fait.

> *Mode de défaillance* — `hooks/intent-brief-gate.sh` gardait sur `jq`. Absent, la garde sortait
> **0** en silence : le hook laissait passer ce qu'il existait pour bloquer, et rien ne le disait.
> C'est ce précédent qui a fait de la déclaration de dépendance une règle plutôt qu'un usage.

`list-dir` ne connaît en revanche **aucun de ses consommateurs** : le registre de dette est un
répertoire-liste comme un autre, et le skill ignore jusqu'au mot « dette ». C'est ce qui le rend
déployable ailleurs, et c'est mécaniquement vérifiable :

```bash
grep -ril 'dette\|debt' skills/list-dir/ ; echo "attendu : aucune sortie"
```

---

## Vérifier le code Python

**`ruff` et `basedpyright`, et eux seuls.** Le tableau ci-dessus donne leurs lanceurs ; ce qui suit
dit pourquoi il n'y a pas d'alternative.

**`pyright` ne remplace pas `basedpyright`.** Le `pyrightconfig.json` de `skills/list-dir` déclare
`"typeCheckingMode": "all"`, un mode que seul `basedpyright` connaît. Lancé dessus, `pyright`
répond sur sa première ligne :

```
Config "typeCheckingMode" entry must contain "off", "basic", "standard", or "strict".
```

puis vérifie **en mode par défaut** et rend un décompte d'apparence normale. L'écart est mesurable
sur le même arbre : 4 erreurs sous `pyright`, 13 sous `basedpyright`.

> *Mode de défaillance* — les trois audits de clôture du chantier
> `tableaux-toml-aplatis-a-l-ecriture` ont lancé `pyright` et conclu « aucune régression de
> typage ». Une comparaison ultérieure sous `basedpyright` en a montré **trois**, induites par ce
> chantier. Un garde-fou qui répond toujours oui coûte plus cher que pas de garde-fou : on cesse de
> vérifier ce qu'on croit vérifié.

**Le formatage fait partie du contrat : `uvx ruff format .` avant de commiter du Python.** Le
`ruff.toml` de la racine couvre `scripts/` et `statusline-command.py`, celui de chaque skill son
propre code ; tous enroulent à 100 colonnes. Tous excluent aussi les `.md` : ruff formate leurs
blocs de code, dont les commentaires sont alignés à la main.

> *Mode de défaillance* — tant que rien ne lançait `ruff format --check`, des chantiers ont ajouté
> des fichiers hors format sans le voir : 5 fichiers de `list-dir` le 2026-08-30, 8 le 2026-09-06,
> 21 sur tout le dépôt au premier formatage. Un formatage qu'aucune commande ne vérifie ne tient
> pas.

**Comparer à la base se fait sur un arbre extrait, jamais par `git stash`.** Un fichier déjà
commité sur la branche de chantier n'est pas annulé par un `stash` : la comparaison est faussée
sans que rien ne le signale.

```bash
TMP=$(mktemp -d); git archive <base> | tar -x -C "$TMP"
```

> *Mode de défaillance* — deux relevés du même chantier ont été publiés faux pour cette raison :
> « ruff, 5 erreurs toutes préexistantes » (deux étaient induites) et « 551 tests avant » (545).

**Les sous-agents portent ces règles en dur**, recopiées dans `agents/*.md` plutôt que renvoyées
ici : le garde-fou leur interdit tout renvoi au contrat du pipeline, pour qu'ils restent lisibles
seuls. C'est la seule duplication voulue de ce fichier.

## Formater le Markdown

**`uvx rumdl fmt .` avant de commiter du Markdown, et `rumdl fmt` seul.** Le formateur ne touche
qu'aux espaces et à l'enroulement : lignes vides autour des listes, des titres et des blocs de code,
espaces en fin de ligne, et prose réenroulée à 100 colonnes dès qu'une ligne dépasse. Tableaux,
blocs de code et titres n'en sont pas réenroulés. `.rumdl.toml`, à la racine, désactive chaque
règle qui réécrivait le sens d'un document, en nommant pourquoi, et exclut les archives figées de
`done/` et `archive/`.

**`rumdl check` n'est pas un contrôle du dépôt.** Il signale des écarts que le formateur ne corrige
pas — ancres HTML, fichiers sans titre de tête — et sort non nul sur un dépôt sain. Un contrôle qui
échoue toujours apprend à ignorer son verdict.

> *Mode de défaillance* — mdformat et Prettier ont été essayés avant lui, le 2026-10-04. mdformat
> échappait les Marqueurs (`<À REMPLIR>` devenait `\<À REMPLIR>`, que `gabarit check` ne reconnaît
> plus) ; Prettier réalignait chaque tableau, si bien qu'une ligne modifiée réécrivait le tableau
> entier. Avant d'élargir la configuration, vérifier sur une copie que `list-dir validate`,
> `gabarit check` et les tests rendent le même résultat qu'avant.

## Les tests

Le venv du dépôt porte `pytest` et `tomlkit`, épinglés dans `requirements.txt` :

```bash
uv venv ~/.claude/.venv
uv pip install --python ~/.claude/.venv/bin/python -r ~/.claude/requirements.txt
~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/
```

`uv venv` ne pose pas de `pip` dans l'environnement : l'installation passe par `uv pip install`.
`scripts/sante_skills.py` contrôle à chaque démarrage de session que le venv existe, qu'il porte ce
que `requirements.txt` déclare, et que les versions **épinglées par `==`** correspondent.
`list-dir.py` s'y ré-exécute de lui-même : `#!/usr/bin/env python3` désigne un interpréteur où
`tomlkit` n'est pas installé.
