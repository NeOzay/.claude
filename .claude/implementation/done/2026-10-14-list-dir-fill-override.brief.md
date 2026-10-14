+++
gabarit = "brief"
slug = "list-dir-fill-override"
titre = "Permettre à list-dir de réécrire une valeur écrite, et de basculer un booléen"
statut = "validé"
"créé" = 2026-10-14
+++

## Intention

**Symptôme** : `list-dir` n'a aucune commande pour changer une valeur déjà écrite : `fill` ne pose
une valeur que sur un champ resté au Marqueur, et refuse en le nommant un `--id` dont le champ est
rempli ; le picker `:Dettes` de Neovim doit pourtant basculer le champ `pin` d'une dette (entrée de
road-map `list-dir-set`). « `fill` et `set` font doublon » (dit).

**But** : que `fill` réécrive, sur option, la valeur d'un champ déjà écrit d'un élément désigné,
et qu'une commande `toggle` bascule un booléen écrit, sous le contrôle du contrat, de sorte que
Neovim bascule un pin sans jamais écrire dans une entrée.

## Critères de réussite

- **C1** — Sur un pin écrit à `false`, `list-dir fill <dettes> pin true --override --id <id>` le
  passe à `true`, et `git diff` ne montre que la ligne `pin`.
- **C2** — `fill --override --all` sort en code 2 sans rien écrire ; `fill --id` sans `--override`
  refuse toujours une valeur écrite.
- **C3** — `--override` échoue sans rien écrire sur un champ `list`, un champ `deprecated`, le champ
  `id`, un champ absent de l'élément, et une valeur que le contrat refuse (hors `values`, date non
  ISO, `bool` autre que `true`/`false`).
- **C4** — Une valeur identique à la valeur écrite ne touche aucun fichier : `git status --short`
  reste vide.
- **C5** — `list-dir toggle <dettes> pin --id <id>` inverse le pin, et le diff ne montre que la
  ligne `pin` ; la commande échoue sur un champ non `bool`, un `bool` resté au Marqueur ou un champ
  absent, et ne connaît pas `--all`.
- **C6** — `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` passe, avec des
  tests neufs pour chacun des cas de C1 à C5 ; `uvx ruff check .`, `uvx ruff format --check .` et
  `uvx --with pytest basedpyright` sont propres.
- **C7** — `list-dir help` liste `toggle` ; `SKILL.md` dit « quinze commandes », dans sa
  description et dans son titre de section ; `references/operations.md` décrit `--override` et
  `toggle`.

## Hors-périmètre

- Une commande `set` distincte : `fill` existe déjà, l'option s'y ajoute (dit).
- Réécrire un champ de type `list`, un champ `deprecated`, ou le champ `id` (dit).
- Ajouter un champ absent de l'élément : la liste se migre d'abord (dit).
- Basculer un champ qui n'est pas un booléen, ou un booléen resté au Marqueur (dit).
- La touche de `:Dettes` qui appelle la bascule, et l'écart entre le Brief de ce Chantier, qui
  attend `list-dir set`, et la commande `toggle` livrée ici : ils se traitent à la reprise du
  Chantier `listdir-dettes-roadmap` de `~/.config/nvim` (dit).

## Signaux de dérive

- **S1** — Le diff ajoute une commande `set`, ou un fichier `commands/set.py` (dit).
- **S2** — `toggle` ou `--override` écrit sans passer par le contrôle de type de `fill`
  (`typed_value`) ou sans reprojeter le front matter : un second chemin d'écriture (dépôt:
  `skills/list-dir/scripts/listdir/store.py`, `ListStore.fill` ; validé : dit).
- **S3** — Un test ou un appel combine `--override` et `--all` et attend un succès (dit).
- **S4** — Le diff touche `~/.config/nvim/` (dit).
- **S5** — `toggle` accepte `--all`, ou un type autre que `bool` (dit).

## Contraintes connues de l'utilisateur

- **Décision** : pas de commande `set` ; `fill` reçoit une option `--override` qui l'autorise à
  réécrire un champ sans Marqueur (dit).
- **Décision** : `--all` est incompatible avec `--override` (dit).
- **Décision** : la bascule est une commande à part, `list-dir toggle <liste> <champ> --id <id>…`,
  pour les seuls champs `bool` sans Marqueur, sans `--all` (dit).
- **Décision** : la réécriture ne vaut que pour les champs `slug`, `text`, `int`, `bool`, `date` et
  `enum` non `deprecated`, `id` excepté, et respecte le contrat (dit).
- **Décision** : `fill --override --id` sur un champ resté au Marqueur y pose la valeur, comme
  sans l'option (dit).
- **Décision** : `--override` ou `toggle` sur un champ absent de l'élément échoue en le nommant,
  et rien n'est écrit (dit).
- **Décision** : une valeur réécrite identique à la valeur écrite ne touche aucun fichier (dit).
- **Existant** : `fill` contrôle déjà la valeur contre le type déclaré, par `typed_value`, avant
  toute écriture, refuse un champ non déclaré ou `deprecated`, et reprojette le front matter pour
  que le diff ne montre que la ligne du champ (dépôt: `skills/list-dir/scripts/listdir/store.py`,
  `ListStore.fill`).
- **Existant** : les types déclarables sont `slug`, `text`, `date`, `enum`, `int`, `bool`, `list`
  (dépôt: `skills/gabarit/scripts/gabarit/contract.py`, l. 437-467).
- **Existant** : le Brief validé du Chantier Neovim nomme `list-dir set` dans son critère C5 et
  dans ses contraintes (dépôt:
  `~/.config/nvim/.claude/implementation/listdir-dettes-roadmap.brief.md`).
- **Existant** : `SKILL.md` de list-dir annonce « quatorze commandes », dans sa description et un
  titre de section ; `toggle` en fait quinze (dépôt: `skills/list-dir/SKILL.md`).

## Incertitudes à lever en plan

— aucune
