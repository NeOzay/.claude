+++
id = "supprimer-dump-value"
title = "Supprimer dump_value : faire passer ses deux derniers appelants par tomlkit"
date = 2026-09-09
source = "décision de l'utilisateur au 2026-09-09 — « dump_value est déprécié et sera supprimé dans les prochains chantiers »"
+++

## À faire

`dump_value` est **déprécié**. Depuis le chantier `tableaux-toml-aplatis-a-l-ecriture`, le front
matter des éléments est écrit par `dump_front` via tomlkit ; `dump_value` ne survit que pour les
contrats et les semences, qui n'ont rien à préserver.

La tâche est de payer l'entrée de dette `deux-ecrivains-toml-coexistent`, qui porte l'énoncé
complet et la marche à suivre. En résumé : faire passer `store.init_list` et `provenance` par
tomlkit, puis retirer `dump_value`, `ESCAPES` et leurs tests.

Le point d'attention est que ce chantier **touchera l'écriture des contrats et `provenance.py`** —
zones que le chantier précédent s'était explicitement interdites. Ce n'est plus une dérive ici,
c'est l'objet même de la tâche : il faudra le poser comme tel au cadrage, sinon le prochain brief
reconduira le signal de dérive qui l'empêche.

À décider en le rouvrant : le contrat de semence réémis par `provenance` est construit par
interpolation de chaînes, morceau par morceau. Le faire passer par tomlkit peut vouloir dire le
construire comme un document plutôt que comme un texte — plus gros que le simple remplacement d'un
appel.

## Références

- l'entrée de dette qui l'énonce et le plaide : `deux-ecrivains-toml-coexistent`
- les deux appelants restants : `skills/list-dir/scripts/listdir/store.py` (`init_list`, les deux
  valeurs libres du contrat créé) et `skills/list-dir/scripts/listdir/provenance.py` (import et
  réémission du contrat de semence)
- la constante partagée : `ESCAPES`, définie dans `items.py` et empruntée par `provenance` pour
  échapper un **nom** de champ — cas distinct d'une valeur, à traiter à part
- ce qui a rendu `dump_value` inutile pour les éléments : `dump_front` et `toml_value`
  (`skills/list-dir/scripts/listdir/items.py`), et l'en-tête du module qui explique aujourd'hui
  pourquoi les deux écrivains cohabitent — à corriger quand il n'y en aura plus qu'un
- le chantier d'origine, une fois archivé : `tableaux-toml-aplatis-a-l-ecriture`
