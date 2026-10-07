+++
gabarit = "brief"
slug = "socle-contrat-evolutif"
titre = "Socle gabarit/list-dir : type bool, marqueurs typés, champs et sections dépréciés, tri"
statut = "validé"
"créé" = 2026-10-07
+++

## Intention

**Symptôme** : les Marqueurs actuels induisent le modèle en erreur — il écrit
`reviewed = "2026-10-07"` sans omettre les guillemets ; et une List-dir ne sait pas faire évoluer
ses champs (les modifier, pas seulement en ajouter).

**But** : un socle `gabarit`/`list-dir`, couvert par des tests, qui donne au modèle des Marqueurs
du type du champ, un type `bool`, une clé `deprecated` sur champs et sections, et un tri utile à
la priorisation — base du Chantier du registre de dettes.

## Critères de réussite

- `gabarit new` et `list-dir new` posent `<À REMPLIR int>` / `<OPTIONNEL int>` sur un `int` sans
  préremplissage, et `<À REMPLIR date>` / `<OPTIONNEL date>` sur un `date` ; `check`/`validate` les
  tiennent pour des Marqueurs, `--filled` réclame les seuls requis.
- Un champ `bool` est déclarable ; `text = "false"` pose le booléen TOML `false`, pas la chaîne.
- `migrate` remplace un Marqueur générique sur un champ `int` ou `date` par sa forme typée, et ne
  touche à aucune valeur écrite ; non migré, ce Marqueur est accepté par `validate`, qui avertit
  sur stderr sans changer son code de retour.
- Un champ ou une section `deprecated` : absent d'un fichier neuf, jamais ajouté par `migrate`,
  jamais réclamé ni signalé comme non déclaré ; tant qu'un élément le porte, `validate` avertit sur
  stderr avec la consigne, sans changer son code de retour.
- `list --sort` trie en décroissant sur demande, un `enum` dans l'ordre de ses `values`, un `int`
  en nombre.
- `contract` et la référence de format disent que seuls `text`, `enum` et `slug` gardent leurs
  guillemets.
- Tests verts, linters propres :
  `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ skills/gabarit/scripts/tests/ scripts/tests/`,
  `uvx ruff check .`, `uvx ruff format --check .`, `uvx --with pytest basedpyright`.

## Hors-périmètre

- Le registre de dettes : champs sévérité (enum `note`/`avertissement`/`majeur`/`critique`),
  chantier, référence, pin, découpage de `source`, migration des listes du pipeline — Chantier
  distinct, qui s'appuie sur ce socle. (dit)
- L'adaptation de Neovim aux nouveaux Marqueurs et au type `bool` — son propre Chantier. (dit)

## Signaux de dérive

- Le diff modifie un contrat existant — une semence (`skills/*/list-dir/*/contract.toml`,
  `skills/*/gabarit/*/contract.toml`) ou le `.list/contract.toml` d'une liste. (dit)

## Contraintes connues de l'utilisateur

- **Décision** : nouveau type `bool` ; un préremplissage `text = "false"` est casté en booléen à
  la pose. (dit)
- **Décision** : une clé `deprecated = "<consigne>"` vaut sur `[fields.*]` comme sur
  `[sections.*]` : ni `new` ni `migrate` ne la posent, elle n'est pas requise, et la consigne dit
  quoi faire de la donnée. (dit)
- **Décision** : Marqueurs typés, en chaînes dédiées : `<À REMPLIR int>` / `<OPTIONNEL int>`,
  et de même `<À REMPLIR date>` / `<OPTIONNEL date>` — préférés aux dates sentinelles
  `0001-01-01` / `9999-01-01`. (dit)
- **Décision** : le Chantier inclut le tri décroissant dans `list --sort` et le tri d'un `enum`
  dans l'ordre de déclaration de ses `values`. (dit)
- **Décision** : `migrate` remplace un Marqueur générique posé sur un champ typé par sa forme
  « <OPTIONNEL type> » (resp. « <À REMPLIR type> »). (dit)
- **Décision** : seuls `text`, `enum` et `slug` conservent les guillemets ; c'est dit dans la
  sortie de `gabarit contract` / `list-dir contract` et dans la référence de format. (dit)
- **Décision** : un ancien Marqueur générique sur un champ `int` ou `date`, non migré, est accepté
  par `validate`, qui avertit sur stderr en renvoyant à `migrate`, sans changer son code de
  retour. (dit)
- **Existant** : la définition de Marqueur au lexique global cite `<À REMPLIR>` et `<OPTIONNEL>` ;
  la changer exige l'accord de l'utilisateur. (dépôt: LEXIQUE.md)
- **Historique** : le modèle, voyant `reviewed = "<OPTIONNEL>"`, écrit `reviewed = "2026-10-07"`
  avec les guillemets — la date devient une chaîne. (dit)
- **Existant** : Neovim tient les deux Marqueurs pour du vide, en dur —
  `plugins/listdir/lua/listdir/picker/items.lua:12`, `lua/chantier.lua:14`. (dépôt:
  ~/.config/nvim)
- **Décision** : le format des commandes peut changer pour s'adapter aux besoins, sortie de
  `list` comprise ; Neovim suivra dans son propre Chantier. (dit)
- **Existant** : `list --sort` compare les valeurs en texte et seulement en ordre croissant.
  (dépôt: skills/list-dir/scripts/listdir/commands/list.py `_key`)

## Incertitudes à lever en plan

- Quels types reçoivent un Marqueur typé : `int` et `date` sont dits ; `bool` et `list` ?
