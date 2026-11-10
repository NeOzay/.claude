+++
gabarit = "suivi"
slug = "semences-a-sections-structurees"
titre = "Mettre à jour les Semences avec les motifs et labels"
branche = "semences-a-sections-structurees"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-11-10-semences-a-sections-structurees.plan.md"
brief = ".claude/implementation/done/2026-11-10-semences-a-sections-structurees.brief.md"
audit = ".claude/implementation/done/2026-11-10-semences-a-sections-structurees.audit"
road-map = "<OPTIONNEL>"
skills = ["skill-convention"]
"créé" = 2026-11-08
maj = 2026-11-10
+++

## Objectif et périmètre

**Symptôme** : les Semences `brief`, `suivi` et `shadow-skill` n'emploient pas les motifs et
labels livrés par f100580. Le format de leurs sections reste écrit en prose dans la
`description`, et redit par les regex de `rapport_audit` : une ligne d'Étape mal formée passe
`gabarit check` (dépôt: `.claude/implementation/todo/technical-debt/semences-sans-sections-structurees.md`).

**But** : ces trois Semences déclarent le format de leurs sections structurées par
`type = "motif"` ou `type = "label"`, `gabarit check` le vérifie sur les fichiers vivants, et
`rapport_audit` lit ces sections par `section_values` au lieu de ses regex.

**Critères de réussite** :

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

**Hors-périmètre** :

- Les Contrats des registres `road-map*` et `technical-debt*` : les toucher entraînerait la
  migration de toutes les listes (dit).
- La mise à niveau des archives de `done/` (dit).
- La dette `merge-aplatit-les-labels-title`, propre à `list-dir merge` (dit).

**Signaux de dérive** :

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

**Élargissements** :

- 2026-11-10 — Corriger la collision de noms de modules de test qui interrompt la collecte de C7,
  antérieure au Chantier, sur décision de l'utilisateur après l'audit de Clôture 834440b.

## Étapes

- [x] 1. Solder la dette du squelette — `gabarit/structure.py`, `tests/test_squelette.py`,
  `list-dir/scripts/tests/test_structure.py`, `references/format.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_squelette.py skills/list-dir/scripts/tests/test_structure.py`
- [x] 2. Semence `brief` structurée — `brief/contract.toml`, `tests/test_semences.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_semences.py && gabarit check .claude/implementation/semences-a-sections-structurees.brief.md --filled`
- [x] 3. Semence `suivi` structurée — `suivi/contract.toml`, `tests/test_semences.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_semences.py && gabarit check .claude/implementation/semences-a-sections-structurees.md --filled`
- [x] 4. Semence `shadow-skill` structurée — `shadow-skill/contract.toml`,
  `tests/test_semences.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_semences.py && rc=0; for f in shadow-skills/*/SKILL.md; do gabarit check "$f" --filled || rc=1; done; test $rc = 0`
- [x] 5. `pose.py` lit par `section_values` — `rapport_audit/pose.py`, `tests/conftest.py`,
  `tests/test_pose.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/`
- [x] 6. `dettes.py` lit par `section_values` — `rapport_audit/dettes.py`, `rapport_audit/pose.py`,
  `tests/test_dettes.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/ && ! grep -nE 'COCHEE|NUMEROTEE|ECARTEE' skills/implementation-tracker/scripts/rapport_audit/*.py`
- [x] 7. La prose du pipeline — `intent-brief/SKILL.md`, `intent-brief/references/grille-questions.md`,
  `implementation-tracker/references/contrat.md`, `implementation-tracker/references/execution.md` — vérif: `uvx rumdl fmt --check skills/intent-brief skills/implementation-tracker/references`
- [x] 8. Mettre à niveau les Gabarits vivants — `shadow-skills/*/SKILL.md`,
  `.claude/implementation/compaction-de-la-prose.brief.md` — vérif: `rc=0; for f in shadow-skills/*/SKILL.md; do gabarit check "$f" --filled || rc=1; done; gabarit check .claude/implementation/compaction-de-la-prose.brief.md || rc=1; test $rc = 0`
- [x] 9. Vérification d'ensemble contre la Base — aucun fichier — vérif: C2, C5, C7, puis les
  quatre linters sur la branche et sur l'arbre extrait de `master`
- [x] 10. Traiter R2 et R3 de l'audit 834440b — `rapport_audit/dettes.py`, `tests/test_dettes.py`,
  `implementation-tracker/references/execution.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_dettes.py && uvx rumdl check skills/implementation-tracker/references/execution.md`
- [x] 11. Lever la collision de modules de test (R1) — `session-dump/scripts/tests/test_cli_session_dump.py`,
  `shadow-skill/scripts/tests/test_cli_shadow_skill.py`, `shadow-skill/scripts/tests/test_lire_shadow_skill.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/ scripts/tests/`

## État courant

**Prochaine action** : aplatir et archiver le Chantier (Clôture, point 4).

**Vérification** :
`~/.claude/.venv/bin/python -m pytest skills/ scripts/tests/`

**Dernier audit** : 0f71b4a — FAVORABLE — 2026-11-10

**Notes** : —

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien — état initial commité, l'Étape 1 n'a pas commencé.

**À savoir** : `compaction-de-la-prose.brief.md` n'est suivi par git sur aucune branche : il est
exclu de chaque commit du Chantier, et sa mise à niveau à l'Étape 8 pose la question de son
commit à l'utilisateur. Les captures d'un motif se compilent paresseuses (`.+?`) sous `fullmatch`
(`gabarit/motif.py`, `compile_motif`) : un texte qui contient le littéral suivant se coupe au
premier, d'où la source laissée dans la capture de texte. `section_values` ne juge que la section
demandée : les fixtures `BRIEF` et `SUIVI` de `conftest.py`, au front matter incomplet, s'y lisent
pourvu que l'estampille résolve la Semence (`trouver_semence(<estampille>, None)`).
`gabarit contract` rend le TOML brut, commentaires et motifs compris.

## Dettes écartées

<OPTIONNEL>

## Journal de décisions

- **2026-11-08** — S3 ne vise pas `SOURCE` (`pose.py`), qui juge une valeur capturée et non le
  format d'une ligne ; la source reste dans la capture de texte. *Pourquoi* : réponse de
  l'utilisateur à Q5 de la relecture du Plan. *Rejeté* : une capture de source dédiée.
- **2026-11-08** — S1 ne vise que le diff des Étapes : le solde de
  `semences-sans-sections-structurees` et `squelette-ignore-un-label-text-reecrit` relève de la
  Clôture. *Pourquoi* : réponse de l'utilisateur à Q6 de la relecture du Plan. *Rejeté* : solder
  ces dettes à part.
- **2026-11-08** — Le justificatif d'une Dette écartée ne contient pas « — » entouré d'espaces :
  le motif le coupe au premier, et `check` refuse la date. *Pourquoi* : S4 interdit de toucher au
  moteur, et l'échec est nommé. *Rejeté* : la date avant le justificatif, hors du Plan.
- **2026-11-09** — Les MD013 que rumdl ajoute par rapport à `master` restent : ils ne touchent
  que le Brief, le Plan et le Suivi du Chantier, posés à AE0, sur des lignes qui portent une
  commande ou un chemin insécables. *Pourquoi* : `rumdl fmt` ne les résout pas et décale les
  suites des Étapes ; le Brief est figé. *Rejeté* : reformater ces trois documents.
- **2026-11-10** — La collecte de C7 s'interrompait sur trois modules de test de même nom,
  défaut antérieur au Chantier : d'abord laissé hors périmètre, il a valu à l'audit de Clôture
  834440b un DÉFAVORABLE (R1). L'utilisateur l'a fait corriger en élargissement, Étape 11 : les
  deux `test_cli.py` de session-dump et de shadow-skill et le `test_lire.py` de shadow-skill
  portent le nom de leur skill. R2 et R3 de cet audit sont traités à l'Étape 10. *Pourquoi* : le
  correctif que pytest nomme, local aux deux skills. *Rejeté* : `--import-mode=importlib` dans un
  `pytest.ini` racine, qui changerait l'import de chaque skill ; écarter R1.
