+++
id = "gabarit-type-object"
title = "Typer les tables, les dictionnaires et les listes du front matter d'un Gabarit"
date = 2026-10-15
source = "discussion du 2026-10-15 sur l'apport de Pydantic aux Gabarits"
+++

## À faire

Aujourd'hui, un Contrat ne type qu'une liste de chaînes (`list`). Il s'agit de typer les valeurs
composées par deux types nouveaux, sans toucher au reste du système :

- **`table`**, le nom que lui donne la spec TOML : une table à clés fixes, du genre
  `{debut = 2026-10-01, fin = 2026-10-15}`. Le Contrat déclare `[fields.x]` avec
  `type = "table"`, et en déclare chaque clé par une sous-table `[fields.x.keys.y]`, avec ses
  `type`, `required` et `description`. `y` prend n'importe quel type valide, `table` et `object`
  compris ;
- **`object`** : les dictionnaires à clés libres et les listes, écrits en ligne. Leur forme est
  donnée par la propriété `annotation`, qui accepte une annotation Python ou un type valide du
  Contrat, et représente une enum par `Literal` : `annotation = "list[date]"`,
  `annotation = 'dict[int, Literal["a", "b"]]'`, `annotation = "dict[slug, list[int]]"`.

Décidé :

- les noms `table`, `keys`, `object` et `annotation` ;
- `type = "list"` est conservé pour la rétrocompatibilité : aucune List-dir ni aucune Semence
  existante n'est à migrer ;
- **pas de Pydantic** : un vérificateur récursif qui renvoie chaque valeur simple au
  `check_value` existant, pour garder une seule définition de chaque type simple. Pydantic en mode
  strict en aurait une autre : `text` vide accepté, `date` en chaîne refusée. La faute nomme son
  chemin (`periode.fin`, `jalons[2]`) ;
- l'annotation se lit par `ast.parse(…, mode="eval")` et un parcours fermé des nœuds, jamais par
  `eval` : `list`, `dict`, `Literal`, les noms de types admis, les constantes d'un `Literal`.
  Tout autre nœud ou tout autre nom refuse le Contrat en le nommant ;
- `str` est un alias de `text`, avec le même sens : la chaîne vide est refusée ;
- un `dict` accepte en clé `int` et `text`, en valeur `dict`, `list`, `int`, `text`, une enum
  (`Literal`) et `date` ;
- une `table` n'entre jamais dans une annotation : `list[periode]` est interdit ;
- une `table` ne porte pas de Marqueur. Seules ses clés sont posées, chacune avec le Marqueur de
  son type, ou sa valeur de préremplissage ;
- le Marqueur d'un `object` porte son annotation : `<À REMPLIR list[date]>`,
  `<OPTIONNEL dict[int, text]>` ;
- une clé TOML est toujours une chaîne, vérifié le 2026-10-15 avec `tomllib` et `tomlkit` :
  `{1 = "a"}` se lit `{"1": "a"}`, `{3.14 = "pi"}` imbrique les clés (`{"3": {"14": "pi"}}`), et
  tomlkit refuse d'écrire une clé `int`. Un `dict[int, V]` est donc une contrainte sur la forme des
  clés : un entier en base 10, écrit en chaîne, et gardé en `str` côté Python. `check` doit
  refuser deux clés de même valeur entière (`"01"` et `"1"`). Une clé décimale est impossible.

Limites admises :

- le Marqueur d'un `object` vaut pour le champ entier, jamais à l'intérieur de sa valeur ;
- `text` et `command` sont refusés sur un `object`, comme sur `list`. Sur une `table`, ils se
  déclarent par clé ;
- dans le fichier posé, la valeur s'écrit en table en ligne. Les `[[tables]]` et les sous-tables
  devraient venir après tous les champs du front matter, ce qui casse la réécriture des champs dans
  `items.py`.

À trancher, l'annotation d'un `object` :

- les types admis comme élément d'une `list` annotée : les mêmes que les valeurs d'un `dict` ?
- `bool` et `slug`, absents des valeurs d'un `dict` : exclus de toute annotation, ou seulement là ?
- un `Literal` n'admet-il que des chaînes, comme les `values` d'une enum (des jetons, ni vides ni
  porteurs d'espace), ou aussi des entiers (`Literal[1, 2]`) ?
- `date` s'écrit-il aussi `datetime.date` ? Et `int` comme clé admet-il le signe (`"-1"`) ?
- un `Literal` vaut-il comme clé d'un `dict`, alors que seuls `int` et `text` sont admis ?

À trancher, la `table` :

- le sens de `required` sur une `table` qui n'a pas de Marqueur : il ne vaut que par clé, ou
  il refuse une table dont aucune clé n'est remplie ?
- `deprecated` sur une clé d'une `table`, et sur la `table` entière ;
- une profondeur maximale pour les `table` imbriquées dans une `table`, ou aucune.

À trancher, le Marqueur d'un `object`, qui n'est plus pris dans un ensemble fini :

- `ALL_MARKERS` et `is_marker` passent à une reconnaissance par motif ;
- l'annotation se normalise par `ast.unparse`, pour que deux graphies de la même annotation
  donnent le même Marqueur ;
- les guillemets d'un `Literal` (`<À REMPLIR dict[int, Literal["a"]]>`) imposent d'écrire le
  Marqueur en chaîne littérale TOML (`'…'`), ou de rendre le `Literal` entre apostrophes ;
- la règle des guillemets de `gabarit contract` : rappelle-t-elle comment écrire une valeur
  composée, à la place de son Marqueur ?

À trancher, les commandes de list-dir sur une `table` ou un `object` :

- `fill` sans `--override` : refusé, ou une valeur TOML en ligne lue et vérifiée avant écriture ?
- `migrate` : ajoute-t-il à une `table` existante une clé que le Contrat vient de déclarer, et
  retire-t-il une clé que `--drop` désigne ?
- `list --where` et `--sort` : un chemin vers une clé (`periode.debut`), ou aucun filtre sur une
  valeur composée ?
- `contract --values` : rend-il les valeurs d'un `Literal` d'un `object` ?

À trancher, ce qui consomme le Contrat hors de gabarit :

- le plugin Neovim `listdir` (`contract.lua`) lit le Contrat ligne à ligne, sans parseur TOML. Il
  prendrait `[fields.x.keys.y]` pour un champ `x.keys.y` : l'adapter dans le même Chantier, ou
  lui faire ignorer toute table à plus de deux niveaux ?
- l'écriture d'une table en ligne longue : TOML 1.0 l'impose sur une ligne, et rumdl ne formate
  pas le front matter. Faut-il une longueur au-delà de laquelle `check` avertit ?

## Références

- `skills/gabarit/scripts/gabarit/types.py` : `FieldType`, `Field`, `FieldValue` (à rendre
  récursif), `TYPED_MARKER_TYPES`
- `skills/gabarit/scripts/gabarit/contract.py` : le chargement d'un `[fields.*]`, `check_value`
- `skills/gabarit/scripts/gabarit/prefill.py` : le refus de `text`/`command` sur `list`
- `skills/gabarit/scripts/gabarit/items.py`, `toml_value` : il manque la branche `dict`
- `skills/list-dir/scripts/listdir/store.py`, `fill --override` : refuse `list`, à étendre
- `skills/gabarit/references/format.md`, « Les sept types » : la seule transcription des types
- `~/.config/nvim/plugins/listdir/lua/listdir/contract.lua` : lit `type` ligne à ligne, sans
  parseur TOML. Les sous-tables `[fields.x.keys.y]` y seraient prises pour des champs
- `skills/implementation-tracker/scripts/rapport_audit/modele.py` : le précédent Pydantic, et ce
  qu'il coûte pour accepter un Marqueur
- Entrée `gabarit-sections-a-motif` : l'autre ajout tiré de la même discussion
