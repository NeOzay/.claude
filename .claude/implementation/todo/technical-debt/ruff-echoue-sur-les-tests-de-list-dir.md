+++
id = "ruff-echoue-sur-les-tests-de-list-dir"
title = "`uvx ruff check .` échoue depuis `skills/list-dir/`, sur trois lignes de ses tests"
date = 2026-09-20
source = "chantier `pipeline-gabarit`, audit de clôture `14d6464` R3"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Lancé depuis `skills/list-dir/`, `uvx ruff check .` sort en code 1 sur trois `E501` : une ligne de
`scripts/tests/test_contract.py` (101 colonnes) et deux de `scripts/tests/test_fusion.py` (116 et
112). Les trois portent un contrat TOML composé en une seule chaîne littérale.

Établi par : `uvx ruff check .` depuis `skills/list-dir/` → « Found 3 errors », toutes `E501`. La
même commande depuis `skills/gabarit/` et depuis `skills/implementation-tracker/` → « All checks
passed! ».

Ce n'est pas une régression : l'arbre de `master` extrait rend exactement les mêmes trois, et
aucun de ces deux fichiers n'est dans le diff du chantier qui l'a constaté.

## Pourquoi c'est gênant

Les deux autres skills du pipeline sortent à 0 sur la même commande. `list-dir` est donc la seule
dont le linter ne peut pas servir de signal : sa sortie est non nulle en permanence, et une
quatrième erreur — celle qu'on voudrait voir — s'ajouterait aux trois sans rien changer au verdict.
Un audit qui relance ruff par skill doit à chaque fois retrouver que ces trois-là sont connues.

C'est un défaut de même nature que `trois-lignes-au-dela-de-100-colonnes`, mais sur un corpus
distinct : celui-ci porte sur du Python tenu par ruff, l'autre sur de la prose Markdown que rien
n'outille.

## Pour solder

Couper les trois chaînes littérales en concaténations sur plusieurs lignes, comme le fait déjà
`test_fusion.py` quelques lignes plus bas (`'…'\n+ CONTRAT\n+ '…'`), puis vérifier que
`uvx ruff check .` depuis `skills/list-dir/` rend « All checks passed! » et que
`.venv/bin/python -m pytest skills/list-dir/scripts/tests` reste vert.

## Assumé

Le report est délibéré : réserve d'audit de clôture que l'utilisateur a choisi de clore avec. Le
correctif touche des fichiers étrangers au chantier `pipeline-gabarit` et imposerait une passe
d'audit de plus pour trois lignes de mise en forme.
