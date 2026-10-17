+++
gabarit = "suivi"
slug = "gabarit-sections-structurees"
titre = "Déclarer au Contrat le format d'une section structurée — motif ou label — et le vérifier"
branche = "gabarit-sections-structurees"
base = "master"
statut = "terminé"
session = 3
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-17-gabarit-sections-structurees.plan.md"
brief = ".claude/implementation/done/2026-10-17-gabarit-sections-structurees.brief.md"
audit = ".claude/implementation/done/2026-10-17-gabarit-sections-structurees.audit"
road-map = "gabarit-sections-a-motif"
skills = ["skill-convention"]
"créé" = 2026-10-16
maj = 2026-10-17
+++

## Objectif et périmètre

**Symptôme** : le format de certaines sections (`Étapes`, `Dettes écartées`, critères du Brief,
`État courant`, `Objectif et périmètre`, `Passation`) n'est déclaré qu'en prose, dans la
`description` du Contrat, et parsé par des regex écrites hors de gabarit. Le format existe deux
fois, et `gabarit check` ne voit pas une ligne mal formée : l'erreur n'apparaît qu'à `audit pose`,
ou jamais quand la ligne est ignorée.

**But** : qu'un Contrat déclare la structure d'une section — puces à motif ou blocs étiquetés —,
que `check` en vérifie chaque puce ou bloc, et que gabarit fournisse le parseur dont les
consommateurs auront besoin.

**Critères de réussite** :

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

**Élargissement du 2026-10-17** : une section à motif peut déclarer `fin = "\n"` — la puce
finit à la ligne, sa suite s'écrit en retrait, et la faute « `fin` manquante » de C1 n'y vaut pas ;
le Marqueur d'un motif colle `fin` au motif.

**Amendement de C3, 2026-10-16** : une capture prend l'un de cinq types — `slug`, `text`, `date`,
`enum`, `int` — ; sa table `captures.x` et sa `description` sont facultatives, et seule une `enum`
sans `values` refuse le Contrat (Journal).

**Hors-périmètre** :

- L'adoption par les Semences `brief` et `suivi` : un Chantier à part, qui pourra toucher d'autres
  fichiers.
- Le passage de `rapport_audit` (`pose.py`, `dettes.py`) au parseur commun : même Chantier à part.
- Les puces imbriquées dans une section à motif.
- La prose mêlée aux puces d'une section à motif.

**Signaux de dérive** :

- **S1** — Le diff touche les Semences `brief` ou `suivi`, ou `rapport_audit/` : c'est
  l'intégration, Chantier suivant.
- **S2** — Une capture vérifiée hors `check_value`, ou un motif accepté en regex : une seconde
  définition d'un type, ou une seconde syntaxe.
- **S3** — L'espace admise dans les `values` d'un champ, au-delà des captures.
- **S4** — Un test existant modifié pour passer.
- **S5** — Le diff touche `~/.config/nvim/`, ou introduit `table`, `object` ou Pydantic.

## Étapes

- [x] 1. Déclarer le motif et ses captures au Contrat — `types.py`, `motif.py`, `contract.py`,
  `tests/test_motif_contrat.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_motif_contrat.py`
- [x] 2. Déclarer les labels au Contrat — `types.py`, `contract.py`,
  `tests/test_label_contrat.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_label_contrat.py`
- [x] 3. Marqueur d'une section à motif et `--filled` — `types.py`, `structure.py`, `check.py`,
  `tests/test_marqueur_structure.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_marqueur_structure.py`
- [x] 4. Vérifier une section à motif — `structure.py`, `check.py`, `tests/test_motif.py` —
  vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_motif.py`
- [x] 5. Vérifier une section à labels, notes comprises — `structure.py`, `check.py`,
  `tests/test_label.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_label.py`
- [x] 6. Poser une section structurée — `prefill.py`, `tests/test_pose_structure.py` — vérif:
  `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_pose_structure.py`
- [x] 7. Lire une section par `section_values` — `structure.py`,
  `tests/test_section_values.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_section_values.py`
- [x] 8. Faire valider la structure par list-dir — `listdir/store.py`,
  `skills/list-dir/scripts/tests/test_structure.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_structure.py`
- [x] 9. Documenter les sections structurées — `skills/gabarit/references/format.md`,
  `skills/gabarit/SKILL.md`, `skills/list-dir/references/format.md` — vérif: `uvx rumdl fmt --check skills/gabarit/references/format.md skills/gabarit/SKILL.md skills/list-dir/references/format.md`
- [x] 10. Vérification d'ensemble contre la Base — aucun fichier — vérif: la commande de C7 et
  les trois linters, sur la branche et sur l'arbre extrait de `master`
- [x] 11. Marqueur du `prefix`, lié au `required` de sa table — `prefill.py`, `structure.py`,
  `tests/test_prefix.py`, `references/format.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_prefix.py`
- [x] 12. Marqueur d'un motif sur sa propre ligne sous un label `bold` — `prefill.py`,
  `tests/test_pose_structure.py`, `references/format.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_pose_structure.py`
- [x] 13. Table et description de capture facultatives — `contract.py`,
  `tests/test_motif_contrat.py`, `references/format.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_motif_contrat.py`
- [x] 14. Le Marqueur d'un motif colle `fin` au motif — `types.py`, `tests/test_marqueur_structure.py`,
  `tests/test_pose_structure.py`, `references/format.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/`
- [x] 15. Une puce finie par le retour à la ligne, `fin = "\n"` — `contract.py`, `structure.py`,
  `types.py`, `tests/test_fin_de_ligne.py`, `references/format.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_fin_de_ligne.py`
- [x] 16. Réserves de l'audit 01 : squelette de labels au Marqueur (R2), constantes uniques (R4)
  — `structure.py`, `types.py`, `prefill.py`, `contract.py`, `listdir/store.py`,
  `tests/test_squelette.py`, `tests/test_prefix.py`, `tests/test_pose_structure.py`,
  `list-dir/scripts/tests/test_structure.py`, les deux `references/format.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_squelette.py skills/list-dir/scripts/tests/test_structure.py`

## État courant

**Prochaine action** : aucune — Chantier clos.

**Vérification** :
`~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/ skills/list-dir/scripts/tests/ scripts/tests/`

**Dernier audit** : 33fe07e — FAVORABLE — 2026-10-17

**Notes** : `git -C ~/.config/nvim status --short` était vide au début du Chantier (S5).
Contrôle Q9 (2026-10-16) : `uvx rumdl fmt --config .rumdl.toml` laisse intact un fichier posé,
Marqueur de motif de 107 colonnes compris ; `check` et `check --filled` rendent le même verdict.
Étape 10 (2026-10-16), contre `master` extrait : 978 tests passés contre 830 ; `ruff check`,
2 erreurs de part et d'autre (`test_fusion.py`, préexistantes) ; `ruff format --check` propre ;
basedpyright, sur les fichiers versionnés, aucun fichier n'a plus d'erreurs que sur la Base, aucun
fichier du Chantier n'en porte. S1, S3, S4, S5 : rien (la seule ligne de S5 est le Plan lui-même).

## Passation

**Écrite** : session 2, après AE13

**En cours** : rien — les 13 Étapes sont livrées ; reste l'audit de Clôture.

**À savoir** :

- Question ouverte, à poser avant l'audit : l'aperçu choisi par l'utilisateur pour le `prefix`
  posait aussi `<À REMPLIR>` à la ligne sous `**Prochaine action** :`. E12 ne met à la ligne que
  les Marqueurs de motif ; étendre aux Marqueurs simples sous un label `bold` reste à trancher.
- Les messages d'une `enum` listent les valeurs sans guillemets : `" "` y est invisible
  (« x, >, !,  »). Retouche ou dette, non tranché.
- Les tests de ce Chantier modifiés en E12 et E13 (`test_pose_structure.py`,
  `test_motif_contrat.py`, `test_label_contrat.py`) suivent des décisions ratifiées ; S4 ne vise
  que les tests antérieurs au Chantier — à dire à l'auditeur.
- basedpyright se compare à la Base sur les seuls fichiers versionnés (`git ls-files`) : l'arbre
  de travail porte `skills/synced/` et d'autres non versionnés (6 587 erreurs contre 570 sinon).
  Les 2 erreurs de `uvx ruff check .` sont dans `test_fusion.py`, préexistantes.
- `uvx rumdl fmt` réenroulerait la section `## Étapes` du Suivi, posée ainsi dès E0 : laissée telle
  quelle, pour ne pas casser le format des lignes d'Étape.
- La Semence de démonstration (motif, labels `bold` et `title`, `prefix`, captures sans table)
  vit dans le scratchpad de la session 2, hors dépôt, et disparaîtra : `conforme.md`, `fautif.md`
  et `valeurs.py` s'y trouvaient. La refaire depuis `references/format.md` si besoin.
- L'utilisateur conçoit au fil de l'échange et tranche vite. Un choix fermé passe par
  `AskUserQuestion` avec une option recommandée ; un écart au Brief se fait ratifier, puis
  s'écrit au Journal.

## Dettes écartées

<OPTIONNEL>

## Journal de décisions

- **2026-10-16** — Captures limitées à `slug`, `text`, `date`, `enum`, `int` ; leur table et leur
  `description` sont facultatives, la description manquante venant de la section ou du label.
  *Pourquoi* : `list` exigerait un séparateur, et une capture simple n'alourdit pas le Contrat ;
  écarts au Brief ratifiés (Q1, C3). *Rejeté* : les sept types ; la table seule facultative.
- **2026-10-16** — Un `order` qui ne croît pas dans l'ordre de déclaration refuse le Contrat.
  *Pourquoi* : le squelette posé dans cet ordre passe `check` (Q10). *Rejeté* : tri à la pose.
- **2026-10-16** — Une ligne finie par `fin` puis une ligne vide clôt la puce ; sans ligne vide,
  la puce continue. `fin = "\n"` (2026-10-17) finit la puce à la ligne, sa suite en retrait.
  *Pourquoi* : seul indice qui sépare les cas ; `rumdl` réenroule en retrait. *Rejeté* : clore sur
  toute ligne finie par `fin` ; `"EoL"` ; une puce par ligne.
- **2026-10-16** — L'espace qui borde une capture facultative est facultative, et `sequence`
  compte toutes les puces ouvertes, fautives comprises. *Pourquoi* : une puce rognée perd l'espace
  finale ; une puce mal close ne décale pas les suivantes. *Rejeté* : espace exigée.
- **2026-10-16** — `section_values` : un label en prose au Marqueur, vide ou non déclaré n'a pas
  de clé ; un label structuré au Marqueur vaut `[]` ou `{}`. *Pourquoi* : un Marqueur ne porte
  aucune valeur. *Rejeté* : rendre le texte du Marqueur.
- **2026-10-16** — La prose d'un `prefix` prend le `required` de sa table. *Pourquoi* : un
  `prefix` sans Marqueur n'est jamais rempli. *Rejeté* : un `required` propre au `prefix`.
- **2026-10-17** — Le Marqueur d'un motif colle `fin` au motif, et se pose à la ligne sous un label
  `bold` ; un Marqueur simple reste sur la ligne de l'étiquette. *Pourquoi* : la puce commence en
  début de ligne, la prose sur l'étiquette. *Rejeté* : espace imposée ; tout Marqueur à la ligne.
- **2026-10-17** — Le message d'une `enum` ne met entre guillemets qu'une valeur vide ou bordée de
  blanc. *Pourquoi* : `" "` s'y lit, sans changer le message d'avant (S4). *Rejeté* : toutes.
- **2026-10-17** — Une table de labels dont la prose et chaque label présent sont au Marqueur est
  laissée au Marqueur : facultative, rien n'y est réclamé, et `merge` l'omet ; un label prérempli
  n'y compte pas (R2). *Pourquoi* : les facultatifs ne sont jamais réclamés. *Rejeté* : comparer
  au squelette de `new`, faux dès qu'une `command` varie. Le `text` réécrit ignoré : R6, au
  Registre.
