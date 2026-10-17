# Plan — gabarit-sections-structurees

## Relecture

```
VERDICT : NON CONFORME
CRITÈRES :
C1 — Sur une section `type = "motif"`, `gabarit check` passe un fichier conforme et nomme section, puce et capture pour chaque faute → Étape 3
C2 — Sur une section `type = "label"`, en `bold` comme en `title` […], `check` nomme : label `required` absent, `order` violé, prose avant le premier sans `prefix`, labels non séparés d'une ligne vide, étiquette non déclarée (en note) → Étape 4
C3 — Le chargement refuse, en nommant le chemin, un Contrat dont une capture n'a pas de `captures.x` ou de `description`, une `enum` sans `values`, un type de capture inconnu, un `title` dans un `bold`, deux formes à un niveau, un rang au-delà de 6 → Étapes 1 et 2 (lacune : Q2)
C4 — `gabarit new` pose une section structurée au Marqueur portant son type et son motif ; `gabarit check --filled` la signale à remplir → Étape 5
C5 — Une fonction publique de gabarit rend les captures typées de chaque puce d'une section, ou les blocs d'une section `label`, testée → Étape 6
C6 — `list-dir validate` signale une faute de structure dans un Élément → Étape 7
C7 — Les Contrats sans `type` se comportent comme avant […] tests existants inchangés ; ruff, ruff format et basedpyright sans erreur ajoutée → Étape 9 (et les tests « Contrat sans type inchangé » de l'Étape 1)
HORS-PÉRIMÈTRE : RESPECTÉ
DÉRIVE : aucun déclenché (le risque proche de S2 est décrit en Q3)
INCERTITUDES :
Les contraintes de chaque type de capture → § Contexte et Étape 1 ; tranchée, mais en excluant `bool` et `list`, ce qui contredit la décision « avec les sept types existants » : à ratifier par l'utilisateur (Q1)
La forme du Marqueur d'une section structurée → § Le Marqueur et la pose, Étape 5
Le nom de la fonction fournie aux consommateurs et la forme de son retour → `section_values` dans `gabarit.structure`, § `section_values`, Étape 6
MODÈLE : opus → SOUTENU — conception fine de la grammaire et de la récursion des labels, une Étape de prose, et la règle « au moindre doute, Opus »
QUALITÉ :
Q1 — Décision du Brief contredite : « Une capture s'écrit `{nom: type}` avec les sept types existants ». Le Plan refuse `bool` et `list` au chargement — cause du verdict NON CONFORME ; l'accord de l'utilisateur invoqué doit être ratifié face au Brief.
Q2 — C3 exige le refus de « deux formes à un niveau ». Le Plan le rend structurellement impossible (une seule `forme` sur la table parente) mais aucun refus ni test ne le nomme ; et il ne prévoit pas de refuser une clé `forme`, `labels` ou `prefix` sur une section qui n'est pas `label`, alors qu'il le prévoit pour `captures`/`motif`/`debut`/`fin` hors `motif`. Un label qui déclarerait sa propre `forme` sous un parent `title` serait ignoré en silence.
Q3 — La conversion `int` teste `[+-]?\d+` avant `int()`, hors `check_value` : inévitable, `check_value` (`contract.py:420`) n'acceptant qu'un `int` Python, mais c'est une définition lexicale de l'entier hors `check_value`, à surveiller pour S2. Le texte non converti doit aller à `check_value` pour y être refusé, non rejeté par la regex.
Q4 — Ordre des dépendances : les Étapes 3 et 4 jugent « hors Marqueur » / « au Marqueur avec `--filled` », mais le Marqueur de motif et `is_section_marker` n'arrivent qu'à l'Étape 5. Les Étapes 3-4 devront se contenter de `is_marker` et l'Étape 5 reprendre `check.py` : faisable, mais non dit.
Q5 — L'Étape 7 et le tableau des modules parlent de `merge` ; la fonction qui teste `is_marker` sur le corps d'une section est `merge_text` (`store.py:793`), `merge` (ligne 829) ne fait que l'appeler.
Q6 — L'Étape 9 contrôle S5 par `git diff master --stat` sur `~/.config/nvim/`, hors du dépôt : ce contrôle ne peut rien voir. Elle ne cherche pas non plus `table`, `object` ou Pydantic dans le diff.
Q7 — L'Étape 5 prévoit une « Semence de test » sans dire où ; sous `skills/gabarit/gabarit/`, elle ferait échouer le contrôle S1 de l'Étape 9.
Q8 — La vérification de l'Étape 8 ne contrôle que le formatage (`rumdl fmt --diff`), pas le contenu ; OUTILLAGE.md donne `rumdl fmt --check` comme forme de contrôle.
Q9 — La commande de l'Étape 5 ne couvre pas la tenue du Marqueur de motif face à rumdl (échappement de `<`, `[`, `{`, cf. OUTILLAGE.md l. 158) : elle reste un contrôle manuel.
Q10 — Exigence absente du Brief : le refus au chargement d'un `order` « dont les valeurs ne croissent pas dans l'ordre de déclaration ». Le Brief dit seulement que `order` est un rang entier ; à ratifier.
Q11 — Le Plan dit qu'une puce close est « suivie d'une ligne qui commence par `debut` » sans préciser si une ligne vide entre deux puces est admise ; le Brief dit « les autres blancs ignorés ».
```

Réponses de l'utilisateur (2026-10-16) :

- **Q1** — écart ratifié : cinq types de capture (`slug`, `text`, `date`, `enum`, `int`), `bool`
  et `list` refusés. L'écart au Brief s'écrit au Journal de décisions du Suivi.
- **Q10** — refus ratifié : un `order` qui ne croît pas dans l'ordre de déclaration refuse le
  Contrat.
- **Q2** — refus et tests ajoutés : `forme`, `labels`, `prefix` hors `type = "label"` refusés,
  `order` hors d'un label refusé, et un test nomme le cas « deux formes à un niveau ».
- **Q4** — Marqueur d'abord : le Marqueur de motif, `is_section_marker` et `--filled` passent en
  Étape 3, avant les vérifications.

Corrigés sans arbitrage (rédaction) : Q3 (le texte qui ne suit pas `[+-]?\d+` part en chaîne à
`check_value`, qui le refuse), Q5 (`merge_text`), Q6 (S5 contrôlé par recherche dans le diff, et
`~/.config/nvim/` par `git -C ~/.config/nvim status`), Q7 (Semences de test sous `tmp_path`),
Q8 (`uvx rumdl fmt --check`), Q11 (lignes vides admises entre deux puces). Q9 reste un contrôle
manuel, à l'Étape 6.

## Contexte

Brief validé : `.claude/implementation/gabarit-sections-structurees.brief.md` (entrée de
road-map `gabarit-sections-a-motif`).

Le format de certaines sections n'est écrit qu'en prose, dans la `description` du Contrat, et
parsé par des regex hors de gabarit : `gabarit check` ne voit pas une ligne mal formée. Ce
Chantier donne au Contrat deux structures de section, `type = "motif"` (des puces suivant un
gabarit de ligne typé) et `type = "label"` (des blocs étiquetés), les fait vérifier par `check`
et `list-dir validate`, les pose au Marqueur, et fournit `section_values` aux consommateurs.

Rappels du Brief :

- **Critères** : C1 (check d'un motif), C2 (check des labels), C3 (refus au chargement), C4 (pose
  au Marqueur), C5 (`section_values`), C6 (`list-dir validate`), C7 (rien ne change sans `type`,
  tests et linters verts).
- **Hors-périmètre** : les Semences `brief` et `suivi`, `rapport_audit/` (Chantier suivant) ;
  puces imbriquées ; prose mêlée aux puces d'un motif.
- **Signaux** : S1 (Semences ou `rapport_audit/` touchées), S2 (type vérifié hors
  `check_value`, motif en regex), S3 (espace admise dans les `values` d'un champ), S4 (test
  existant modifié), S5 (`~/.config/nvim/`, `table`, `object`, Pydantic).

Incertitudes du Brief, levées au Plan avec l'utilisateur (2026-10-16) :

- **types de capture** : `slug`, `text`, `date`, `enum`, `int` ; `bool` et `list` refusés au
  chargement — écart aux « sept types » du Brief, ratifié (Q1) ;
- **propriétés d'une capture** (`[sections.X.captures.<nom>]`) : `description` (obligatoire, non
  vide), `required` (vrai par défaut ; faux, la capture peut rester vide), `values` (enum,
  obligatoires), `min`, `max`, `sequence` (int). `type`, `text`, `command` et toute autre clé y
  sont refusés : le type ne se déclare que dans le motif ;
- **Marqueur** : une section à motif reçoit `<À REMPLIR motif: <debut> <motif> <fin>>` (ou
  `<OPTIONNEL motif: …>`) ; une section à labels est posée en **squelette** de ses labels, chacun
  à son Marqueur ou à son `text`/`command` ;
- **fonction publique** : `section_values(contract, item, titre) -> Result[...]`, dans
  `gabarit.structure`, en écho à `field_values`.

Shadow-skill retenu : `skill-convention` (code Python et documentation d'une skill).

## Modèle

**Opus** — la grammaire du motif et la récursion des labels sont un travail de conception fin, et
l'Étape de documentation est de la prose ; au moindre doute, Opus.

## Conception

### Modules

| Module | Rôle |
|---|---|
| `gabarit/types.py` | `Capture(Field)` (+ `min`, `max`, `sequence`) ; `Section` gagne `type`, `motif`, `debut`, `fin`, `captures`, `labels`, `forme`, `order`, `prefix` ; `Section.marker` construit le Marqueur d'un motif — `marker` reste la seule construction |
| `gabarit/motif.py` (nouveau) | découpe d'un motif en littéraux et captures `{nom}` / `{nom: type}`, compilation en regex ancrée ; `CAPTURE_TYPES`, `DEBUT = "-"`, `FIN = ";;"`. Ne dépend que de `types` |
| `gabarit/contract.py` | `parse_section` récursif (labels), `parse_capture` ; refus nommés |
| `gabarit/structure.py` (nouveau) | découpe et vérification d'une section structurée, notes, `section_values`, `is_section_marker` |
| `gabarit/check.py` | `check_sections` et `notes` délèguent à `structure` quand la section a un `type` |
| `gabarit/prefill.py` | `initial_section` pose le squelette d'une section à labels |
| `listdir/store.py` | `merge_text` (appelée par `merge`) reconnaît le Marqueur d'une section à motif (`is_section_marker`) |

Une section sans `type` suit exactement le chemin actuel (C7).

### Le motif

- **Déclaration** : `motif` obligatoire avec `type = "motif"`, `debut`/`fin` facultatifs (défauts
  « - » et « ;; »), chaînes non vides. Refus au chargement, chemin nommé : capture sans
  `captures.<nom>` ou `captures.<nom>` absente du motif, `description` absente ou vide, type de
  capture inconnu ou `bool`/`list`, `enum` sans `values`, `min`/`max`/`sequence` hors `int`,
  `min > max`, deux captures de même nom, deux captures sans littéral entre elles, accolade non
  appariée, clé `captures`/`motif`/`debut`/`fin` sur une section qui n'est pas `motif`.
- **Espace dans `values`** : admise pour une capture seulement (`parse_capture` ne passe pas par
  la règle de `contract.py:233`, que `parse_field` garde intacte — S3).
- **Découpe du corps** : une puce commence sur une ligne qui commence, blancs ignorés, par
  `debut` suivi d'un blanc ; elle se clôt par une ligne terminée par `fin`, suivie d'une ligne qui
  commence par `debut`, ou de la fin de la section ; des lignes vides peuvent séparer deux puces
  (« les autres blancs ignorés »). Fautes : texte non blanc avant la première
  puce ; nouvelle puce ouverte avant la `fin` de la précédente (couvre les puces imbriquées) ;
  dernière puce sans `fin`. Un « ; » ou un « ;; » intérieur ne ferme rien.
- **Correspondance** : le texte d'une puce, `debut` et `fin` retirés, a ses blancs réduits à une
  espace ; le motif compilé (littéraux échappés et réduits de même, capture requise `(.+?)`,
  facultative `(.*?)`) doit le couvrir entièrement — sinon « ne suit pas le motif ».
- **Captures** : rognées, sauf une `enum`, comparée d'abord brute puis rognée — c'est ce qui
  laisse « [ ] » valoir `" "`. Conversion avant `check_value` : une capture `int` qui suit
  `[+-]?\d+` passe par `int()`, toute autre valeur part en chaîne — y compris un `int` mal écrit,
  que `check_value` refuse alors. **Le type est jugé par `check_value` et lui seul** (S2) ;
  `min`/`max` et `sequence` sont des contraintes en plus. `sequence` : la puce *i* (depuis 0)
  vaut `min + i`, ou `1 + i` sans `min`.
- **Message** : `section « X », puce N, capture « c » — raison`.

### Les labels

- **Déclaration** : `type = "label"` exige `forme` (`bold` ou `title`) et une table `labels`
  non vide ; chaque `[….labels.<nom>]` se lit comme une section (`description`, `required`,
  `text`, `command`, `deprecated`, `type`…) plus `order` (entier). `prefix`, chaîne non vide,
  permet la prose avant le premier label. Refus : `forme` absente ou inconnue, label `type =
  "label"` sous une `forme = "bold"`, rang de titre au-delà de 6, `order` non entier ou dont les
  valeurs ne croissent pas dans l'ordre de déclaration (Q10 : le squelette posé passe ainsi
  `check`), `forme`/`labels`/`prefix` sur une table qui n'est pas `type = "label"` — c'est ce
  refus qui nomme « deux formes à un niveau » : un label qui déclare sa `forme` sans être
  `label` (Q2) —, `order` hors d'un label.
- **Écriture** : `bold` — `**Nom** :` ou `**Nom**:` en début de ligne, le corps sur la même
  ligne ou les suivantes ; `title` — `#` répété au rang 3 + profondeur des labels `title`
  englobants. Un label court jusqu'au label suivant de même niveau ou la fin de son parent ;
  lecture hors blocs de code (`outside_fences`).
- **Fautes** : label `required` absent, vide, ou au Marqueur avec `--filled` ; label précédé
  d'une ligne non vide ; `order` violé entre deux labels qui en portent ; label en double ;
  prose avant le premier sans `prefix` ; fautes du motif d'un label, préfixées du chemin
  `section « X », label « Y »`.
- **Notes** (pas des fautes) : étiquette non déclarée ; label `deprecated` encore présent.

### Le Marqueur et la pose

- `Section.marker` d'un motif : `f"{base[:-1]} motif: {debut} {motif} {fin}>"`.
- `is_section_marker(texte)` : vrai pour un Marqueur générique ou de motif, **blancs réduits**
  avant comparaison — rumdl réenroule à 100 colonnes une ligne qui dépasse. Utilisé par
  `check_sections` (`--filled`, et pour ne pas juger la structure d'une section restée au
  Marqueur) et par `merge`.
- Section `label` : squelette des labels non dépréciés, dans l'ordre de déclaration, séparés
  d'une ligne vide, chacun à son `text`/`command` ou à son Marqueur — celui d'un motif pour un
  label à motif, le squelette des sous-labels pour un label à labels. Un `text`/`command` sur la
  section l'emporte sur le squelette.

### `section_values`

- Motif : `list[dict[str, str | int | None]]`, une entrée par puce, `None` pour une capture
  facultative vide.
- Label : `dict[str, str | list | dict]` — corps rogné, liste d'un label à motif, dict d'un label
  à labels ; un label absent n'a pas de clé.
- Section au Marqueur : liste vide ou dict vide. Section mal formée ou sans `type` : échec nommé.

### Limite admise

`list-dir merge` rend chaque section sous `### <titre>` : les labels `title` d'une section y
deviennent des titres de même rang. Non traité ici ; proposé en dette à la Clôture.

## Étapes

- [ ] 1. Déclarer le motif et ses captures au Contrat — `types.py`, `motif.py`, `contract.py`,
  `tests/test_motif_contrat.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_motif_contrat.py`
- [ ] 2. Déclarer les labels au Contrat — `types.py`, `contract.py`,
  `tests/test_label_contrat.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_label_contrat.py`
- [ ] 3. Marqueur d'une section à motif et `--filled` — `types.py`, `structure.py`, `check.py`,
  `tests/test_marqueur_structure.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_marqueur_structure.py`
- [ ] 4. Vérifier une section à motif — `structure.py`, `check.py`, `tests/test_motif.py` —
  vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_motif.py`
- [ ] 5. Vérifier une section à labels, notes comprises — `structure.py`, `check.py`,
  `tests/test_label.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_label.py`
- [ ] 6. Poser une section structurée — `prefill.py`, `tests/test_pose_structure.py` — vérif:
  `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_pose_structure.py`
- [ ] 7. Lire une section par `section_values` — `structure.py`,
  `tests/test_section_values.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_section_values.py`
- [ ] 8. Faire valider la structure par list-dir — `listdir/store.py`,
  `skills/list-dir/scripts/tests/test_structure.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_structure.py`
- [ ] 9. Documenter les sections structurées — `skills/gabarit/references/format.md`,
  `skills/gabarit/SKILL.md`, `skills/list-dir/references/format.md` — vérif: `uvx rumdl fmt --check skills/gabarit/references/format.md skills/gabarit/SKILL.md skills/list-dir/references/format.md`
- [ ] 10. Vérification d'ensemble contre la Base — aucun fichier — vérif: la commande de C7 et
  les trois linters, sur la branche et sur l'arbre extrait de `master`

### Contenu des Étapes

Les Semences de test vivent sous `tmp_path`, jamais sous `skills/gabarit/gabarit/` (S1).

1. `Capture`, champs de `Section` liés au motif, `motif.py` (découpe, compilation,
   constantes), `parse_capture` et la branche `motif` de `parse_section`. Tests : chaque refus
   de « Déclaration » (§ Le motif), un `" "` admis dans les `values` d'une capture et toujours
   refusé sur un champ, un Contrat sans `type` inchangé.
2. Champs de `Section` liés aux labels, branche `label` récursive de `parse_section`. Tests :
   chaque refus de « Déclaration » (§ Les labels), dont « deux formes à un niveau » et les clés
   hors de leur type ; récursion `title` → `title` → `bold` ; rang 6 admis, 7 refusé.
3. `Section.marker` d'un motif, `is_section_marker` (blancs réduits) ; `check_sections` s'en sert
   pour `--filled` et pour ne pas juger la structure d'une section restée au Marqueur. Tests :
   Marqueur requis et facultatif, générique toujours accepté, Marqueur réenroulé sur deux lignes
   reconnu, « à remplir » avec `--filled`.
4. Découpe en puces, correspondance, captures, `min`/`max`, `sequence` ; `check_sections`
   appelle `structure` pour une section `motif`. Tests : un fichier conforme (puces
   multilignes, lignes vides entre puces, « ; » intérieur, `[ ]`), puis chaque faute de C1
   nommée par section, puce et capture.
5. Découpe en labels `bold` et `title`, fautes et notes ; motif dans un label. Tests : chaque
   point de C2, en `bold` et en `title`, imbrication, note d'étiquette non déclarée sur le canal
   des notes et verdict inchangé, label au Marqueur avec `--filled`.
6. Squelette d'une section à labels dans `initial_section` ; une section à motif reçoit le
   Marqueur de l'Étape 3. Tests : `gabarit new` sur une Semence de test pose les deux formes,
   `check` passe, `check --filled` dit « à remplir ». Contrôle manuel (Q9) : `uvx rumdl fmt` sur
   un fichier posé dans le scratchpad, puis `gabarit check` rend le même verdict.
7. `section_values` pour les deux types et les cas limites (§ `section_values`).
8. `merge_text` sur `is_section_marker` ; test d'une List-dir dont le Contrat déclare une section
   à motif : `validate` signale une puce fautive, accepte un Élément conforme ; `merge` omet une
   section facultative restée au Marqueur de motif.
9. Section « Les sections structurées » dans `format.md` (motif, captures, labels, `forme`,
   `order`, `prefix`, Marqueur, pose), mise à jour de « Les marqueurs » ; une ligne et un renvoi
   dans `SKILL.md` ; un renvoi dans le `format.md` de list-dir. Prose selon
   `shadow-skills/skill-convention/references/prose.md`. Aucun terme n'entre au lexique. Le
   contenu se relit à l'audit ; la commande ne juge que le formatage.
10. Méthode de `OUTILLAGE.md` (« Comparer à la base » : `git archive master` extrait dans un
    répertoire temporaire). Relever sur la branche et sur la Base le nombre de tests passés et
    les erreurs de `uvx ruff check .`, `uvx ruff format --check .` et
    `uvx --with pytest basedpyright` : aucune erreur ajoutée. Signaux :
    - S4 : `git diff master --name-status -- '*/tests/test_*.py'` ne montre que des `A` ;
    - S1 : `git diff master --stat -- skills/gabarit/gabarit/ skills/implementation-tracker/scripts/rapport_audit/` vide ;
    - S5 : `git diff master | grep -nE '^\+.*(pydantic|"table"|"object")'` vide, et
      `git -C ~/.config/nvim status --short` inchangé depuis le début du Chantier.

## Vérification d'ensemble

```bash
~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/ skills/list-dir/scripts/tests/ scripts/tests/
uvx ruff check . && uvx ruff format --check . && uvx --with pytest basedpyright
gabarit check .claude/implementation/gabarit-sections-structurees.brief.md --filled
```
