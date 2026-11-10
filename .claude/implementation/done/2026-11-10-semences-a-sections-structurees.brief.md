+++
gabarit = "brief"
slug = "semences-a-sections-structurees"
titre = "Mettre à jour les Semences avec les motifs et labels"
statut = "validé"
"créé" = 2026-11-02
+++

## Intention

**Symptôme** : les Semences `brief`, `suivi` et `shadow-skill` n'emploient pas les motifs et
labels livrés par f100580. Le format de leurs sections reste écrit en prose dans la
`description`, et redit par les regex de `rapport_audit` : une ligne d'Étape mal formée passe
`gabarit check` (dépôt: `.claude/implementation/todo/technical-debt/semences-sans-sections-structurees.md`).

**But** : ces trois Semences déclarent le format de leurs sections structurées par
`type = "motif"` ou `type = "label"`, `gabarit check` le vérifie sur les fichiers vivants, et
`rapport_audit` lit ces sections par `section_values` au lieu de ses regex.

## Critères de réussite

- **C1** — Une ligne d'Étape mal formée dans un Suivi fait échouer `gabarit check`, qui nomme la
  section et la puce ; de même une ligne mal formée de `Dettes écartées`, un critère ou un signal
  mal numéroté d'un Brief, une puce de `Références` d'un Shadow-skill.
- **C2** — `grep -nE 'COCHEE|NUMEROTEE|ECARTEE' skills/implementation-tracker/scripts/rapport_audit/*.py`
  ne rend rien ; `rapport_audit` lit ces sections par `section_values`.
- **C3** — `gabarit new suivi`, `brief` et `shadow-skill` posent leurs sections structurées au
  Marqueur de leur forme, et `gabarit check` juge le fichier posé conforme.
- **C4** — `gabarit check --filled` passe sur les quatre `shadow-skills/*/SKILL.md`, et
  `gabarit check` sur `.claude/implementation/compaction-de-la-prose.brief.md`.
- **C5** — `git diff --stat master -- .claude/implementation/done/` ne rend rien.
- **C6** — Une table de labels facultative dont seul un label `text` a été réécrit n'est plus
  tenue au Marqueur, et `merge` ne l'omet plus ; le cas est ajouté à `test_squelette.py` et à
  `test_structure.py`.
- **C7** — `~/.claude/.venv/bin/python -m pytest skills/ scripts/tests/` passe, les tests de
  `rapport_audit` réécrits pour le format à motifs.

## Hors-périmètre

- Les Contrats des registres `road-map*` et `technical-debt*` : les toucher entraînerait la
  migration de toutes les listes (dit).
- La mise à niveau des archives de `done/` (dit).
- La dette `merge-aplatit-les-labels-title`, propre à `list-dir merge` (dit).

## Signaux de dérive

- **S1** — Le diff touche un Contrat `road-map*` ou `technical-debt*`, ou un Élément de registre
  (dit).
- **S2** — Le diff touche un fichier de `.claude/implementation/done/` (dit).
- **S3** — Une regex de format de section reste ou apparaît dans `rapport_audit`, y compris en
  repli sur l'ancien format (dit).
- **S4** — Le moteur de `gabarit` change — nouvelle syntaxe de motif, nouveau type de capture —
  hors du correctif de la dette `squelette-ignore-un-label-text-reecrit` : l'outil plié à une
  Semence (dit).
- **S5** — Le diff touche `list-dir merge` (`merge_text`) ou `~/.config/nvim/` (dit).
- **S6** — Un test existant modifié pour passer, hors de sa réécriture au format à motifs (dit).

## Contraintes connues de l'utilisateur

- **Décision** : les Semences visées sont `suivi`, `brief` et `shadow-skill` (dit).
- **Décision** : les regex de `rapport_audit` qui redisent le format d'une section cèdent la
  place aux motifs (dit).
- **Décision** : mettre à niveau les Gabarits vivants, c'est-à-dire les quatre `SKILL.md` de
  `shadow-skills/` et `.claude/implementation/compaction-de-la-prose.brief.md` (dit).
- **Décision** : solder dans ce Chantier la dette `squelette-ignore-un-label-text-reecrit` (dit).
- **Décision** : `rapport_audit` ne lit plus que les motifs, sans repli sur l'ancien format ;
  un fichier vivant à l'ancien format se met d'abord à niveau (dit).
- **Décision** : les `description` des trois Contrats sont allégées : elles gardent le sens de
  la section, et le format des lignes n'est plus déclaré que par le motif ou les labels (dit).
- **Intouchable** : les fichiers de `done/` sont figés et ne doivent jamais être modifiés (dit).
- **Existant** : le Chantier précédent a laissé cette adoption, et le passage de `rapport_audit`
  au parseur commun, hors de son périmètre (dépôt:
  `.claude/implementation/done/2026-10-17-gabarit-sections-structurees.brief.md`).
- **Existant** : les regex de format de section sont `COCHEE`, `NUMEROTEE`, `SOURCE` dans
  `pose.py` et `ECARTEE` dans `dettes.py` ; `modele.py` et `export.py` nomment aussi ces sections
  (dépôt: `skills/implementation-tracker/scripts/rapport_audit/`).

## Incertitudes à lever en plan

- Quelles regex relèvent des motifs : `SOURCE` (le suffixe `(dit)` / `(dépôt: …)`) et `COMMANDE`
  (la commande entre accents graves d'une vérification) décrivent l'intérieur d'une capture, pas
  une ligne.
- Pour chaque section structurée, motif ou labels — `Objectif et périmètre` reprend en labels des
  critères et signaux qui, au Brief, seraient des puces à motif.
