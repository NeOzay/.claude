+++
id = "deux-conftest-collision-collecte"
title = "Les deux suites de tests ne se collectent plus ensemble, et le résultat dépend de l'ordre des arguments"
date = 2026-08-24
source = "chantier `tests-listdir`, R3 de l'audit de clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le dépôt porte désormais deux suites, chacune avec son `conftest.py` et aucune ne portant
d'`__init__.py` : `scripts/tests/` et `skills/list-dir/scripts/tests/`. En mode d'import
« prepend », pytest dérive le nom de module du *basename* du fichier — les deux `conftest.py`
se disputent donc le nom `conftest`, et le premier collecté gagne.

Mesuré depuis la racine du dépôt :

```
$ uvx pytest scripts/tests skills/list-dir/scripts/tests -q
    from conftest import CONTRAT_REL, ecrire
E   ImportError: cannot import name 'CONTRAT_REL' from 'conftest'
    (/home/debian/.claude/skills/list-dir/scripts/tests/conftest.py)
Interrupted: 3 errors during collection                      code 2

$ uvx pytest skills/list-dir/scripts/tests scripts/tests -q
308 passed                                                   code 0
```

Le même dépôt, les mêmes fichiers, deux verdicts opposés selon l'ordre des arguments.

## Soldé le

**2026-08-30, hors chantier** — les helpers sortent de `scripts/tests/conftest.py` vers
`scripts/tests/depot_jouet.py`, au basename unique au dépôt, et les huit fichiers de test
importent depuis lui. `conftest.py` ne garde que la fixture `depot`. C'est le patron déjà retenu
côté `list-dir` avec `jouet.py`, préféré aux deux voies que **Pour solder** proposait : pas
d'`__init__.py` (qui casserait les imports par nom court), pas de fichier de configuration à la
racine (le dépôt n'en porte toujours aucun).

Établi par les deux ordres d'arguments que cette entrée oppose, plus le geste nu :

```
$ uvx pytest scripts/tests skills/list-dir/scripts/tests -q
342 passed in 4.20s                                          code 0

$ uvx pytest skills/list-dir/scripts/tests scripts/tests -q
342 passed in 4.05s                                          code 0

$ uvx pytest -q
342 passed in 4.20s                                          code 0
```

Le même compte dans les trois cas. `uvx ruff check scripts skills/list-dir` et
`uvx --with pytest basedpyright` sont verts, ce dernier après correction d'un défaut préexistant
sans rapport (`test_sante_skills.py`, fixture demandée pour son seul effet de bord).

Le mode de défaillance reste ouvert pour une troisième suite : la règle qui l'écarte — un basename
d'appui unique au dépôt — est désormais écrite dans `scripts/tests/README.md`, avec les deux
commandes qui la vérifient.

## Pourquoi c'est gênant

Les commandes contractuelles lancent chaque suite séparément et restent vertes — c'est ce qui a
permis à ce chantier de se dérouler sans rien voir. Le défaut n'apparaît qu'à celui qui essaie de
tout lancer d'un coup, geste naturel dès qu'il y a deux suites, et il lui rend une `ImportError`
qui désigne le mauvais fichier : le message accuse le `conftest.py` de `list-dir` d'un symbole qui
n'a jamais été le sien.

C'est un mode de défaillance à diagnostic trompeur, de la même famille que
`fence-non-fermee-diagnostic-trompeur` : rien n'est perdu, mais le temps passé à chercher la cause
au mauvais endroit est réel. Il empirera à chaque suite ajoutée.

`uvx pytest` nu depuis la racine était **déjà** cassé avant ce chantier — 13 erreurs de collecte
venant de `plugins/` — donc aucune régression sur ce geste-là.

## Pour solder

Un `__init__.py` vide dans chacun des deux répertoires de tests : les noms de modules se qualifient
alors par leur paquet, et la collision disparaît. Alternative, si l'on préfère ne pas faire des
tests des paquets : `[tool.pytest.ini_options] importmode = "importlib"` dans un fichier de
configuration à la racine — mais le dépôt n'en porte aucun aujourd'hui, ce qui en ferait le premier.

Solde établi par les deux ordres d'arguments ci-dessus rendant le même compte, code 0.

## Assumé

<OPTIONNEL>
