# Plan — refonte-de-l-audit

Brief : `.claude/implementation/refonte-de-l-audit.brief.md` (validé), et son annexe
`refonte-de-l-audit.brief.annexe.py`. Entrée de road-map : `refonte-de-l-audit`.

## Relecture

Verdict de `plan-reviewer` : **NON CONFORME**, sur C5 seul ; les sept autres critères sont
servis, hors-périmètre respecté, aucun signal déclenché, modèle soutenu.

- **C5** — non servi tel que le Brief l'écrit : `impl_list.py:30` et `migrations/3.md` gardent le
  motif. *Tranché* : C5 se vérifie hors de ces deux fichiers ; l'écart au Brief
  se consigne au Journal de décisions du Suivi.
- **Q1** — la vérification d'E10 échoue déjà sur `master` (ruff : 2 erreurs dans `list-dir` ;
  basedpyright à la racine : 6 584). Corrigée : bornée au périmètre du Chantier, qui passe
  aujourd'hui.
- **Q2** — vérification d'E9 : le `grep` suivi de `;` ne décidait pas du code de sortie. Corrigée.
- **Q3** — `skills/implementation-tracker/pyrightconfig.json` sans `../gabarit/scripts` en
  `extraPaths` : ajouté à E2, sans quoi la vérification de typage échoue.
- **Q4** — qui donne à l'utilisateur le chemin complet de l'export. *Tranché* : l'orchestrateur,
  au retour de l'audit, dans la restitution du verdict (E9).
- **Q5** — qui écrit `## Dettes écartées` du Suivi. *Tranché* : l'orchestrateur, sur accord de
  l'utilisateur ; l'audit suivant range la dette (E9).
- **Q6** — l'agent réécrit à E8 serait-il chargé par la session qui lance l'audit de Clôture ?
  *Tranché* : redémarrer Claude Code recharge les agents ; Étape 11 ajoutée.
- **Q7** — le plan échouait à `rumdl fmt --check`. Corrigé.
- **Q8** — `statut` est le littéral de l'annexe, déduit du code de sortie. Corrigé à E4.
- **Q9** — `audit` au tableau d'`OUTILLAGE.md` passe à E2, où naît `bin/audit` ; E5 teste sur un
  Suivi jouet, la semence ne change qu'à E7. Corrigé.

## Contexte

Chaque audit s'appende à `<slug>.audit.md`, que l'auditeur relit puis réécrit en entier ; les
rapports archivés font jusqu'à 1 481 lignes, et le verdict ne conclut presque jamais (74
`RÉSERVES`, 12 `DÉFAVORABLE`, 1 `FAVORABLE`). Le Chantier remplace ce fichier par un rapport TOML
par audit, qui reprend l'état des dettes du précédent, et aligne le verdict sur la sévérité des
dettes.

Cadre rappelé du Brief :

- **Critères** : C1 `audit new` pose `01` puis `02` avec Dette précédente et cumuls ; C2 `audit new`
  exécute les vérifications des Étapes ; C3 `audit check --filled` accepte les factices et refuse
  les fautes de l'annexe ; C4 `audit range` et `audit dette` ; C5 plus de `.audit.md` produit ; C6
  `Edit` à l'auditeur, `## Dettes écartées` au Suivi, plus de « plus sévère » ; C7 Pydantic au
  venv ; C8 l'audit de Clôture de ce Chantier au nouveau format.
- **Hors-périmètre** : quand auditer en intermédiaire ; nombre d'audits et contre-audit bornés ;
  restitution du verdict ; correspondance avec le contrat du Registre ; `.audit.md` existants ; le
  Brief et sa semence.
- **Incertitudes** : le format d'`audit export` et le nom `audit`, tranchés ci-dessous.

## Modèle

**Opus** : le Chantier mêle code et prose — l'agent, quatre références —, et la prose ne se vérifie
pas au-delà des `grep` des critères.

## Shadow-skills

`skill-convention` : code Python, commande exposée dans `bin/`, prose de skill et d'agent.

## Audit intermédiaire

Aucun. Le nouveau format ne sert qu'une fois l'agent et les références réécrits (E8, E9) ; l'audit
de Clôture, au nouveau format, est le critère C8.

## Décisions de conception

- **Le nom `audit`.** Libre dans le `PATH` (`command -v audit` ne rend rien). Une commande, cinq
  sous-commandes, comme `gabarit new|check|contract`.
- **Disposition**, sur le modèle de `shadow-skill` : `skills/implementation-tracker/scripts/`
  porte `audit-cli.py` (point d'entrée sans logique, garde de version, ré-exécution dans le venv
  comme `skills/list-dir/scripts/list-dir.py`) et le paquet `rapport_audit/` — `modele.py` (les
  classes de l'annexe), `pose.py` (`new`), `dettes.py` (`range`, `dette`), `export.py`. Lien
  `bin/audit`.
- **Réutiliser gabarit**, importé par son lien de `bin/` comme
  `skills/shadow-skill/scripts/shadow_skill.py:27-45` : `items.read_item` et `parse_sections` pour
  lire le Suivi et le Brief, `contract.is_marker` et les Marqueurs de `types.py`, `Result`/`fail`/
  `ok` entre couches, tomlkit pour écrire sans perdre la mise en forme.
- **Deux validations, un modèle.** Le rapport posé porte des Marqueurs (`<À REMPLIR>`) là où
  l'auditeur écrit. `audit check` les admet ; `--filled` exige qu'il n'en reste aucun, comme
  `gabarit check --filled`. Les contrôles de cohérence (renvois, cotes d'office, verdict admis)
  sautent un champ resté au Marqueur ; ils s'appliquent tous sous `--filled`. Le contexte de
  validation Pydantic porte le mode.
- **Vérifications exécutées d'avance.** `audit new` lit les lignes `— vérif: <commande>` des Étapes
  cochées du Suivi (`contrat.md:145`), les exécute depuis la racine, sur la branche, et consigne
  `statut` (code de sortie) et `sortie` (fin bornée de la sortie). Les commandes des critères du
  Brief restent à l'auditeur : le Brief ne change pas.
- **Les points de la revue** sont posés depuis le Brief : critères `**C<n>**`, signaux `**S<n>**`
  (numérotés par la semence), puces du Hors-périmètre, ligne `**Symptôme**`. Sans Brief, la revue
  est vide.
- **`audit range <fichier> R<n> actuelle|corrigee|ecartee`**, avec `--preuve` vers `corrigee` ;
  vers `ecartee`, le justificatif et la date viennent de la ligne `R<n> — justificatif — date` de
  `## Dettes écartées` du Suivi, ligne absente → refus nommé.
- **`audit dette <fichier> --nature <nature> --severite <sévérité>`** ajoute à la Dette actuelle
  une dette dont `id` (le `R<n>` suivant, jamais servi dans le Chantier) et `trouvee` sont remplis,
  le reste au Marqueur ; affiche le `R<n>`.
- **`audit export <fichier> <destination.md>`** : Markdown — en-tête en liste, vérifications et
  revue en listes, les quatre tableaux de dettes en tableaux Markdown (`#`, nature, emplacement,
  constat, solution, depuis, sévérité, plus les colonnes propres à corrigée et écartée), le verdict
  et sa justification en dernier. La destination est donnée par l'appelant : le scratchpad.
- **Archivage.** `commit-chantier cloture` archive tout `<slug>.*` de `.claude/implementation/`
  vers `done/<date>-<slug>.*` — le répertoire `<slug>.audit/` comme l'annexe du Brief — au lieu de
  la liste fermée suivi, brief, `.audit.md`. Le champ `audit` du Suivi devient le chemin du
  répertoire ; le contrôle 5 de `scripts/check_pipeline.py` l'admet (`exists()` au lieu de
  `is_file()`).
- **`## Dettes écartées`** entre à la semence `suivi`, non requise : les Suivis archivés restent
  conformes.

## Écart au Brief

- **C5** se vérifie hors de `skills/implementation-tracker/scripts/impl_list.py`, dont le filtre
  doit continuer d'écarter les `.audit.md` existants, et de
  `skills/implementation-tracker/list-dir/technical-debt/migrations/3.md`, migration passée (tranché
  à la relecture).

## Étapes

- [ ] 1. Pydantic au venv — `requirements.txt`, `OUTILLAGE.md` — vérif:
      `~/.claude/.venv/bin/python -c 'import pydantic' && ~/.claude/.venv/bin/python -m pytest scripts/tests/test_sante_skills.py -q`
      Épingler `pydantic==<version installée>`, installer par `uv pip install`, ajouter Pydantic à
      `OUTILLAGE.md`.
- [ ] 2. Le modèle et `audit check` —
      `skills/implementation-tracker/scripts/rapport_audit/modele.py`,
      `skills/implementation-tracker/scripts/audit-cli.py`, `bin/audit`,
      `skills/implementation-tracker/pyrightconfig.json`, `OUTILLAGE.md`,
      `skills/implementation-tracker/scripts/tests/test_modele.py`,
      `skills/implementation-tracker/scripts/tests/fixtures/` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_modele.py -q`
      Reprendre les classes de l'annexe, ajouter les Marqueurs et `--filled`, `../gabarit/scripts`
      aux `extraPaths`, `audit` au tableau des dépendances, `check` avec le précédent nommé par
      `precedent` et l'affichage des verdicts admis. Fixtures : les deux audits factices et une
      faute par contrôle (C3).
- [ ] 3. `audit new`, la pose — `skills/implementation-tracker/scripts/rapport_audit/pose.py`,
      `skills/implementation-tracker/scripts/tests/test_pose.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_pose.py -q`
      En-tête depuis le Suivi et git, rang et précédent, copie de la Dette actuelle et des cumuls,
      revue depuis le Brief. Test sur un dépôt jouet : `01` puis `02` (C1).
- [ ] 4. `audit new`, les vérifications —
      `skills/implementation-tracker/scripts/rapport_audit/pose.py`,
      `skills/implementation-tracker/scripts/tests/test_pose.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_pose.py -q -k verification`
      Extraction des `— vérif:` des Étapes cochées, exécution, consignation : `statut` vaut `passée`
      ou `échouée` selon le code de sortie, `non-exécutée` si la commande n'a pu être lancée (C2).
- [ ] 5. `audit range` et `audit dette` —
      `skills/implementation-tracker/scripts/rapport_audit/dettes.py`,
      `skills/implementation-tracker/scripts/tests/test_dettes.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_dettes.py -q`
      Sur un Suivi jouet portant `## Dettes écartées` (C4).
- [ ] 6. `audit export` — `skills/implementation-tracker/scripts/rapport_audit/export.py`,
      `skills/implementation-tracker/scripts/tests/test_export.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_export.py -q`
- [ ] 7. Le Suivi et l'archivage — `skills/gabarit/gabarit/suivi/contract.toml`,
      `skills/git-smart-commit/scripts/commit_chantier.py` et ses tests, `scripts/check_pipeline.py`
      et ses tests — vérif:
      `gabarit contract suivi | grep 'Dettes écartées' && ~/.claude/.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests/ scripts/tests/ -q && python3 scripts/check_pipeline.py`
- [ ] 8. L'agent — `agents/implementation-auditor.md` — vérif:
      `grep '^tools:.*Edit' agents/implementation-auditor.md && ! grep -n 'plus sévère\|\.audit\.md' agents/implementation-auditor.md`
      `Edit` aux outils ; le rapport posé par l'appelant ; juger les vérifications consignées, les
      rejouer au besoin, exécuter celles des critères ; `audit range` pour chaque dette précédente,
      `audit dette` pour chaque neuve, remplissage par `Edit` ; natures, échelle, cotes d'office ;
      verdict en dernier sur la sévérité réelle ; `audit check --filled` avant de rendre la main ;
      bloc de sortie. Auto-suffisant : aucun renvoi à `contrat.md` (contrôle 4).
- [ ] 9. Les références — `skills/implementation-tracker/references/audit.md`, `cloture.md`,
      `contrat.md`, `dette.md`, `SKILL.md` — vérif:
      `! grep -rn '\.audit\.md' agents/ skills/ | grep -v -e scripts/impl_list.py -e list-dir/technical-debt/migrations/ && python3 scripts/check_pipeline.py && git diff --name-only --diff-filter=d master...HEAD -- '*.md' | xargs -r uvx rumdl fmt --check`
      `audit new` avant le sous-agent, `audit check --filled` et `audit export` au retour, le format
      renvoyé à `modele.py` ; les dettes restantes au Registre par défaut, sans arbitrage Rx par Rx,
      écartées exclues, aucun `bloquant` ; reprise : `<slug>.audit/` au lieu de `<slug>.audit.md`.
      Au retour, l'orchestrateur lance `audit export` vers le scratchpad et donne le chemin complet
      dans la restitution ; sur accord de l'utilisateur, il écrit `R<n> — justificatif — date` en
      `## Dettes écartées`.
- [ ] 10. Formatage et typage du périmètre — le code des Étapes 2 à 7 — vérif:
      `uvx ruff check skills/implementation-tracker skills/git-smart-commit scripts && uvx ruff format --check skills/implementation-tracker skills/git-smart-commit scripts && uvx --with pytest --with pydantic basedpyright -p skills/implementation-tracker`
      `skills/git-smart-commit` n'a pas de `pyrightconfig.json` et porte 4 erreurs aujourd'hui : sa
      part se compare à la base sur un arbre extrait (`OUTILLAGE.md`), sans erreur ajoutée.
- [ ] 11. Recharger l'agent réécrit — aucun fichier — vérif: dans la session neuve, la liste des
  agents donne à `implementation-auditor` l'outil `Edit`. Passation, puis redémarrage de Claude
  Code par l'utilisateur, puis reprise par `/implementation-tracker` : une session ne recharge
  pas l'agent qu'elle a modifié (Q6).

## Vérification de bout en bout

À la Clôture : `audit new refonte-de-l-audit --cloture`, l'audit par `implementation-auditor`, puis
`audit check --filled` sur le rapport rendu et `audit export` vers le scratchpad (C8).
