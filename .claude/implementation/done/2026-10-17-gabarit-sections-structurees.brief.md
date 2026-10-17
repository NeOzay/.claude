+++
gabarit = "brief"
slug = "gabarit-sections-structurees"
titre = "Déclarer au Contrat le format d'une section structurée — motif ou label — et le vérifier"
statut = "validé"
"créé" = 2026-10-16
+++

## Intention

**Symptôme** : le format de certaines sections (`Étapes`, `Dettes écartées`, critères du Brief,
`État courant`, `Objectif et périmètre`, `Passation`) n'est déclaré qu'en prose, dans la
`description` du Contrat, et parsé par des regex écrites hors de gabarit. Le format existe deux
fois, et `gabarit check` ne voit pas une ligne mal formée : l'erreur n'apparaît qu'à `audit pose`,
ou jamais quand la ligne est ignorée.

**But** : qu'un Contrat déclare la structure d'une section — puces à motif ou blocs étiquetés —,
que `check` en vérifie chaque puce ou bloc, et que gabarit fournisse le parseur dont les
consommateurs auront besoin.

## Critères de réussite

- **C1** — Sur une section `type = "motif"`, `gabarit check` passe un fichier conforme et nomme
  section, puce et capture pour chaque faute : `fin` manquante, texte hors puce, puce imbriquée,
  valeur hors `values`, `int` hors min-max, `sequence` rompue ou mal partie. Une puce multiligne
  ou un « ; » intérieur ne fautent pas.
- **C2** — Sur une section `type = "label"`, en `bold` comme en `title` (rangs 3 à 6, imbrication,
  motif dans un label), `check` nomme : label `required` absent, `order` violé, prose avant le
  premier sans `prefix`, labels non séparés d'une ligne vide, étiquette non déclarée (en note).
- **C3** — Le chargement refuse, en nommant le chemin, un Contrat dont une capture n'a pas de
  `captures.x` ou de `description`, une `enum` sans `values`, un type de capture inconnu, un
  `title` dans un `bold`, deux formes à un niveau, un rang au-delà de 6.
- **C4** — `gabarit new` pose une section structurée au Marqueur portant son type et son motif ;
  `gabarit check --filled` la signale à remplir.
- **C5** — Une fonction publique de gabarit rend les captures typées de chaque puce d'une section,
  ou les blocs d'une section `label`, testée.
- **C6** — `list-dir validate` signale une faute de structure dans un Élément.
- **C7** — Les Contrats sans `type` se comportent comme avant :
  `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/ skills/list-dir/scripts/tests/ scripts/tests/`
  vert, tests existants inchangés ; `uvx ruff check .`, `uvx ruff format --check .` et
  `uvx --with pytest basedpyright` sans erreur ajoutée.

## Hors-périmètre

- L'adoption par les Semences `brief` et `suivi` : un Chantier à part, qui pourra toucher d'autres
  fichiers (dit).
- Le passage de `rapport_audit` (`pose.py`, `dettes.py`) au parseur commun : même Chantier à part
  (dit).
- Les puces imbriquées dans une section à motif (dit).
- La prose mêlée aux puces d'une section à motif (dit).

## Signaux de dérive

- **S1** — Le diff touche les Semences `brief` ou `suivi`, ou `rapport_audit/` : c'est
  l'intégration, Chantier suivant (dit).
- **S2** — Une capture vérifiée hors `check_value`, ou un motif accepté en regex : une seconde
  définition d'un type, ou une seconde syntaxe (dit).
- **S3** — L'espace admise dans les `values` d'un champ, au-delà des captures (dit).
- **S4** — Un test existant modifié pour passer (dit).
- **S5** — Le diff touche `~/.config/nvim/`, ou introduit `table`, `object` ou Pydantic (dit).

## Contraintes connues de l'utilisateur

- **Décision** : deux structures de section, déclarées par `type = "motif"` ou `type = "label"`
  sur `[sections.X]`, qui garde `required`, `description`, `deprecated`, `text` et `command` dans
  leur sens habituel (dit).
- **Décision** : le motif est un gabarit de ligne, pas une regex —
  `"[{etat: enum}] {n: int}. {intitule} — {fichiers} — vérif: {verif}"`. Une capture s'écrit
  `{nom: type}` avec les sept types existants ; type omis = `text` (dit).
- **Décision** : chaque capture se déclare par `[sections.X.captures.<nom>]`, qui porte sa
  `description`, obligatoire, et ses contraintes : les `values` d'une `enum`, obligatoires ; un
  min-max d'un `int` (dit).
- **Décision** : une `enum` de capture admet l'espace en valeur : `["x", ">", "!", " "]` (dit).
- **Décision** : une puce va d'un `debut` à une `fin`, configurables, par défaut « - » et « ;; ».
  Elle peut courir sur plusieurs lignes (dit).
- **Décision** : la `fin` est exigée sur chaque puce, la dernière comprise, sans exception. Une
  puce se clôt par `<fin>`, saut de ligne, `<debut>`, les autres blancs ignorés ; la dernière par
  `<fin>` et la fin de la section (dit).
- **Décision** : une section à motif ne porte que des puces : tout texte hors puce est une faute
  de `check` (dit).
- **Décision** : un `int` de capture peut porter un min-max, sans obligation, et une option
  `sequence` : ses valeurs sont croissantes et se suivent d'une puce à l'autre, à partir du `min`,
  sinon de 1 (dit).
- **Décision** : l'espace en valeur d'`enum` n'est admise que pour une capture ; les champs gardent
  la règle actuelle (dit).
- **Décision** : une section sans `type` est en prose libre (dit).
- **Décision** : un bloc étiqueté se déclare par `[sections.X.labels.<nom>]`, équivalent à toute
  autre `[sections.X]`. La table qui porte les labels déclare `forme = "bold"` (`**Nom** :`) ou
  `"title"` (titre de rang inférieur) : tous ses labels prennent cette forme, jamais les deux à un
  même niveau. Un label `title` peut déclarer ses propres labels, du rang 3 au rang 6 ; un label
  `bold` n'en contient aucun. Un label peut porter un motif (dit).
- **Décision** : un label va de son étiquette au label suivant ou à la fin de la section ; il est
  séparé du précédent par une ligne vide. Le corps d'un `bold` commence après l'étiquette ou à la
  ligne (dit).
- **Décision** : l'ordre des labels se déclare par `order` sur chacun ; la prose avant le premier
  n'est permise que si la section déclare `prefix = "<description>"` (dit).
- **Décision** : une étiquette non déclarée n'est pas une faute, mais le signe d'un Contrat mal
  construit : `check` émet une note (dit).
- **Décision** : `order` est un rang entier ; un label qui n'en porte pas prend n'importe quelle
  place (dit).
- **Décision** : une section à motif sans puce reste au Marqueur ; `required`, elle est une faute
  (dit).
- **Décision** : une section restée au Marqueur porte son type et son motif (dit).
- **Décision** : les blancs d'une capture sont rognés et réduits à une espace (dit).
- **Décision** : la `description` en prose d'une section reste telle quelle (dit).
- **Décision** : `list-dir validate` vérifie la structure des sections des Éléments (dit).
- **Décision** : ce Chantier est indépendant de l'entrée `gabarit-type-object`, qui n'est pas une
  priorité (dit).
- **Existant** : le « ; » apparaît à l'intérieur de puces d'Étapes archivées —
  `` vérif: `bash scripts/check-pipeline.sh; echo $?` `` —, « ;; » nulle part
  (dépôt: `.claude/implementation/done/`).
- **Existant** : une valeur d'`enum` vide ou portant une espace refuse le Contrat
  (dépôt: `skills/gabarit/scripts/gabarit/contract.py:233`).
- **Existant** : le nom `parse_section` est déjà pris par la lecture d'une déclaration de section
  (dépôt: `skills/gabarit/scripts/gabarit/contract.py:301`).
- **Existant** : le plugin Neovim `listdir` ignore toute table `[sections.*]`, sous-tables
  comprises : une clé de section nouvelle ne le casse pas
  (dépôt: `~/.config/nvim/plugins/listdir/lua/listdir/contract.lua`).

## Incertitudes à lever en plan

- Les contraintes de chaque type de capture, à discuter au cas par cas.
- La forme du Marqueur d'une section structurée, qui porte son type et son motif.
- Le nom de la fonction fournie aux consommateurs, `parse_section` étant pris, et la forme de son
  retour : à définir au Plan (dit).
