+++
id = "deux-ecrivains-toml-coexistent"
title = "Deux écrivains TOML cohabitent dans listdir : dump_value est déprécié"
date = 2026-09-09
source = "chantier tableaux-toml-aplatis-a-l-ecriture, journal du 2026-09-09 — « dump_value est gardé intact »"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`listdir/items.py` porte désormais deux écrivains TOML.

`dump_front` passe par tomlkit et sert le front matter des éléments : il reprojette, préserve les
tableaux mis en forme, les commentaires et les guillemets, et sait écrire une chaîne multiligne.

`dump_value` reste le sérialiseur borné à une ligne, écrit à la main. Il refuse tout caractère de
contrôle (« aucune écriture TOML sur une ligne ne le porte »), donc toute valeur contenant un saut
de ligne. Il n'a plus que deux appelants, tous deux hors du front matter :

- `store.init_list`, pour les deux valeurs libres d'un contrat créé — `nom` et `desc` ;
- `provenance`, qui importe `ESCAPES`, `SerialiseError` et `dump_value` pour réémettre un contrat
  de semence.

Sa constante `ESCAPES` est en outre partagée : `provenance` s'en sert pour échapper un **nom** de
champ, avec le commentaire « LES MÊMES ÉCHAPPEMENTS QUE `dump_value` ». Deux fonctions distinctes
dépendent donc d'une même table, dans deux modules.

Établi par : `grep -rn "dump_value\|ESCAPES" skills/list-dir/scripts/listdir/` → appels en
`store.py:807-808` et `provenance.py:431`, import en `provenance.py:45`, définition et usage
d'`ESCAPES` en `items.py:172,186` et `provenance.py:328`.

## Pourquoi c'est gênant

Deux écrivains veut dire deux comportements pour la même question — « comment s'écrit cette
valeur ? » — et rien dans le code n'oblige les deux à répondre pareil. Ils divergent déjà : une
valeur contenant un saut de ligne s'écrit en `"""…"""` par l'un et lève `SerialiseError` par
l'autre.

Le mode de défaillance qui en découle est silencieux. Un `--name` ou un `--description` contenant
un saut de ligne fait échouer `init` avec un message qui parle de « caractère de contrôle », alors
que l'écrivain d'à côté sait l'écrire depuis ce chantier. Personne ne pensera à regarder pourquoi
deux fonctions du même fichier ne s'accordent pas.

Le coût monte avec le temps : `dump_value` est le genre de code qu'on recopie parce qu'il est là.
Chaque nouvel appelant rend la suppression plus chère, et l'écart entre les deux écrivains plus
difficile à voir.

## Pour solder

Faire passer les deux appelants restants par tomlkit, puis supprimer `dump_value` et `ESCAPES`
d'`items.py`.

1. `store.init_list` (`store.py:807-808`) — le contrat créé est construit par interpolation de
   chaînes ; les deux valeurs libres peuvent passer par `toml_value` et `tomlkit.dumps`.
2. `provenance` (`provenance.py:45,431`) — même chose pour le contrat de semence réémis, en
   traitant à part l'échappement de **nom** de champ, qui n'est pas le même problème qu'une valeur.
3. Retirer `dump_value`, `ESCAPES` et leurs tests (`tests/test_items.py`, 9 occurrences), puis
   corriger l'en-tête d'`items.py` qui annonce aujourd'hui les deux écrivains et leur partage.

Vérification : `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` reste vert et
`grep -rn "dump_value\|ESCAPES" skills/list-dir/scripts/` ne rend plus rien.

## Assumé

Le report est délibéré. Ce chantier a explicitement écarté la refonte de `dump_value` : le brief
posait « si le diff touche l'écriture des contrats ou `provenance.py`, s'arrêter » comme signal de
dérive, et les contrats n'ont rien à préserver puisqu'ils sont recopiés à l'octet — le bénéfice
immédiat était donc nul.
