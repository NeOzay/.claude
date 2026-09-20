---
slug: pipeline-gabarit
---

## 2026-09-19 — intermédiaire — `d4d7206`

**Verdict** : DÉFAVORABLE

Périmètre audité : étapes 1 à 3, cochées `[x]` et commitées (`7ed4d90`, `b51524a`, `d4d7206`).
L'étape 4 est marquée `[>]`, mais l'arbre est propre : elle n'a encore rien produit. Les étapes 4 à
10 ne sont pas jugées. Le verdict tient à un seul constat, R1 : une commande de la « Vérification
d'ensemble », que le suivi désigne comme vérification, échoue sur du code livré à l'étape 1. Le
défaut se corrige en un tour. Tout le reste relèverait de `RÉSERVES`.

### Vérifications exécutées

- `.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests` (étape 1) → 11 passés,
  0 échec
- `.venv/bin/python -m pytest scripts/tests` (étape 2) → 118 passés, 0 échec
- `python3 scripts/check_pipeline.py` (étape 2, Python 3.14.7 du PATH) → code 0, « Pipeline
  conforme ». Contrôle 5 : « 25 archives, tous les champs plan/brief/audit résolvent »
- `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests` (étape 3) → 28 passés, 0 échec
- `commit-chantier lettre` (étape 3) → `B`, code 0
- Vérification d'ensemble, pytest sur les quatre dossiers de tests → 208 passés, 0 échec
- Vérification d'ensemble, `uvx ruff check scripts skills/implementation-tracker/scripts
  skills/git-smart-commit/scripts` → **ÉCHEC**, 1 erreur (voir R1). Même commande sur l'arbre de
  `master` extrait : « All checks passed! »
- Vérification d'ensemble, `uvx --with pytest basedpyright`. Pour comparer à conditions égales, la
  commande a tourné sur les deux arbres extraits par `git archive` : `master` → 2638 erreurs ;
  `d4d7206` → 77 erreurs, aucune dans les fichiers touchés par le chantier (voir R5). Lancée
  depuis la racine du dépôt : 5536 erreurs, dont 5511 sous `skills/synced/` (dette connue
  `pyrightconfig-racine-inclut-les-skills-synced`). Aucune dans `fiche.py`, `commit_chantier.py`,
  `check_pipeline.py` ou leurs tests.
- `gabarit check .claude/implementation/pipeline-gabarit.md --filled` → « rempli et conforme à la
  semence « suivi » », code 0
- `gabarit check .claude/implementation/pipeline-gabarit.brief.md --filled` → code 1, « front
  matter absent ». C'est attendu : le brief reste en YAML jusqu'à l'étape 6, comme le prévoient le
  brief et le suivi. Ce n'est pas un constat.
- Tests de `git-smart-commit` lancés sans `~/.claude/bin` dans le PATH : 25 échecs sur 28 sur
  `d4d7206`, 26 passés sur 26 sur `master` (voir R2)

### Conformité à l'intention

Audit intermédiaire : les critères qui dépendent d'étapes encore `[ ]` ne sont pas reprochés.

- Critère « `gabarit check --filled` avant la validation du brief » : pas encore traité (étape 5).
- Critère « `gabarit check --filled` après le premier remplissage du suivi, et il conditionne
  l'implémentation » : pas encore branché dans la skill (étape 7). Pour ce chantier, le suivi passe
  déjà la vérification (exécutée ci-dessus).
- Critère « dettes soldées » : pas encore traité (étape 9). La condition de solde de
  `frontmatter-suivi-lu-par-regex` est remplie sur le fond. Un seul module lit le front matter pour
  les deux appelants. `test_toml_cle_en_double_refusee` et `test_refus_d_une_cle_en_double`
  refusent une valeur ambiguë au lieu de la tronquer. Nuance en R4.
- Critère « fiches de ce chantier au nouveau format » : le suivi est en TOML `+++` et conforme ; le
  brief sera converti à l'étape 6.
- Critère « entrée `road-map/` » : pas encore traité (étape 10).
- Hors-périmètre : respecté. `git diff master...pipeline-gabarit -- .claude/implementation/done`
  est vide, et `audit.md` n'est pas touché.
- Signaux de dérive : aucun ne s'est matérialisé. Aucune skill n'a encore été modifiée.
- Symptôme d'origine : en partie résorbé. Les deux regex du front matter ont disparu : lecture par
  `fiche.lire_front` (tomllib), réécriture par `gabarit.items`. La double écriture de la structure
  du suivi (modèle Markdown et semence) demeure jusqu'à l'étape 7.
- Décisions du journal : tenues. `fiche.py` n'utilise que la bibliothèque standard, et
  `check_pipeline.py` tourne sous le python3 du PATH. Les `extraPaths` de Q8 sont ajoutés à
  `pyrightconfig.json`. Q7 est tenu : le vrai lecteur est recopié dans le dépôt-jouet.

### Qualité du code

- **R1** — `skills/implementation-tracker/scripts/fiche.py:17-23` — `uvx ruff check` rend
  `I001 Import block is un-sorted or un-formatted`. `skills/implementation-tracker/` n'a pas de
  `ruff.toml`. Ruff y applique donc sa `target-version` par défaut, qui ne classe pas `tomllib`
  parmi les modules standard. Avec `--target-version py312`, la vérification passe. C'est la dette
  connue `impl-list-sans-configuration-de-linters` qui se manifeste pour la première fois. Mais la
  commande de la Vérification d'ensemble échoue, et elle passait sur `master`. **Bloquant pour la
  clôture.**
- **R2** — `skills/git-smart-commit/scripts/tests/test_commit_chantier.py:64-67`. `lancer` passe au
  script le PATH ambiant. `commit_chantier.bibliotheques()` localise `fiche` et `gabarit` par
  `shutil.which("impl-list"|"gabarit")`. Deux effets s'ensuivent :
  1. Sans `~/.claude/bin` dans le PATH (CI, shell sans profil), 25 tests sur 28 échouent, alors que
     tous passaient sur `master`.
  2. Sur un clone situé ailleurs, les tests éprouvent les bibliothèques installées sous `$HOME`, pas
     celles du clone. C'est précisément ce que `check_pipeline.charger` refuse de faire (« Copie du
     dépôt, jamais la skill installée »).

  Le comportement d'exécution suit OUTILLAGE.md, comme le plan le prévoyait. Ce sont les tests qui
  ne fixent pas leur environnement.
- **R3** — `skills/git-smart-commit/scripts/commit_chantier.py:153`. `from gabarit.items import …`
  n'est importé qu'au premier appel de `reecrire`, c'est-à-dire dans `executer`, après `preparer`
  et après la sortie `--dry-run`. Si `gabarit` ne s'importe pas (`tomlkit` absent parce que le
  `.venv` est introuvable), le résultat est une trace Python non capturée, et non un `Refus`.
  `--dry-run` annonce alors une clôture qui échouera. La docstring promet pourtant « TOUS LES REFUS
  PRÉCÈDENT LA PREMIÈRE ÉCRITURE ». Aucune écriture n'a lieu avant l'échec, puisque `reecrire` est
  le premier geste de `finaliser`. Le fichier ne se corrompt donc pas, mais le mode de défaillance
  n'est pas celui que le script annonce.
- Style : conforme aux fichiers voisins (docstrings de module en paragraphes à tête majuscule,
  messages en français, `cast` sur les objets chargés dynamiquement, commentaire « Nommer CE
  défaut » repris). Rien à signaler.

### Dette induite

- **R4** — `fiche.lire_front` et `gabarit.items.split_front` découpent le `+++` chacun de leur
  côté, avec une logique identique écrite deux fois. `commit_chantier` passe par les deux pour un
  même fichier : il lit par `fiche` et réécrit par `gabarit.items` (Q12 du plan). La duplication
  est justifiée, puisque `items.py` importe `tomlkit` et que `fiche` doit rester en bibliothèque
  standard. Mais c'est de nouveau deux découpeurs alignés à la main, le motif même que dénonce
  `frontmatter-suivi-lu-par-regex`. La grammaire TOML est désormais commune, seul le découpage des
  délimiteurs peut diverger. Coût futur : une évolution du découpage (BOM, espaces, fence) faite
  d'un seul côté ne fera rien échouer. Il faut le mentionner au solde de la dette, pour ne pas la
  déclarer soldée sans réserve.
- **R5** — `pyrightconfig.json` : ajouter `skills/gabarit/scripts` aux `extraPaths` rend `gabarit`
  résoluble et fait apparaître 11 erreurs jusque-là masquées dans `skills/list-dir/`
  (`listdir/provenance.py`, `tests/test_prefill.py`). Ces erreurs ne sont pas introduites par le
  chantier : le bilan net passe de 2638 à 77. Elles sont en revanche désormais visibles et n'ont
  pas de fiche de dette.
- Le vérificateur `check_pipeline.charger` enregistre le module audité dans `sys.modules` sous
  `_audite_<stem>`. C'est nécessaire pour `dataclass` et c'est commenté. Rien à signaler.

### Bloquants

- R1 : `uvx ruff check scripts skills/implementation-tracker/scripts
  skills/git-smart-commit/scripts` échoue (I001 sur `fiche.py`). Il bloque la clôture, pas la
  poursuite des étapes 4 à 10.

## 2026-09-19 — intermédiaire — `d32eeda`

**Verdict** : RÉSERVES

Périmètre audité : étapes 1 à 4, cochées `[x]` et commitées. Le jugement porte d'abord sur
l'étape corrective 4 (`d32eeda`), qui devait corriger R1, R2 et R3 de l'audit `d4d7206`. Les
étapes 1 à 3 ont été revérifiées par leurs commandes. L'étape 5 est marquée `[>]`, mais l'arbre est
propre : elle n'a encore rien produit. Les étapes 5 à 11 ne sont pas jugées.

Dans ce rapport, les numéros `R1` à `R4` sont ceux de la présente section. Les constats de l'audit
précédent sont cités sous la forme « R1 de `d4d7206` ».

Les trois constats corrigés sont levés, chacun vérifié par exécution. Aucune vérification n'échoue.
Il reste quatre réserves mineures, dont aucune ne bloque. Deux concernent la tenue du registre et
du suivi.

### Vérifications exécutées

- Vérification de l'étape 4 : `uvx ruff check scripts skills/implementation-tracker/scripts
  skills/git-smart-commit/scripts` → « All checks passed! », code 0. Sur `d4d7206`, la même
  commande échouait en I001.
- Vérification de l'étape 4 : `PATH=/usr/bin:/bin .venv/bin/python -m pytest
  skills/git-smart-commit/scripts/tests` → 29 passés, 0 échec. Sur `d4d7206` : 25 échecs sur 28.
- Vérification d'ensemble, pytest sur les quatre dossiers de tests → 209 passés, 0 échec. C'était
  208 sur `d4d7206` ; le test en plus est `test_refus_si_une_bibliotheque_manque`.
- `python3 scripts/check_pipeline.py` (Python 3.14.7 du PATH) → « Pipeline conforme », code 0. Les
  9 contrôles sont verts. Contrôle 5 : 25 archives, tous les champs résolvent.
- `commit-chantier lettre` → `B`, code 0.
- `uvx --with pytest basedpyright`, lancé sur les arbres extraits par `git archive` avec le `.venv`
  du dépôt en lien symbolique :
  - `master` → 2586 erreurs ;
  - `d4d7206` → 25 erreurs ;
  - `d32eeda` → 25 erreurs.

  Les 25 erreurs sont identiques d'un commit à l'autre et restent hors des fichiers du chantier :
  12 dans `scripts/tests/test_sante_skills.py`, 13 dans `skills/list-dir/` (R5 de `d4d7206`).
  L'étape 4 n'introduit aucune régression de typage. Les décomptes diffèrent de ceux de l'audit
  précédent (2638, 77) parce que l'environnement n'est pas le même, ici le `.venv` en lien. La
  comparaison entre commits se fait à conditions égales.
- `uvx --with pytest basedpyright` lancé depuis `skills/implementation-tracker/` → 4 fichiers
  analysés, 0 erreur. `uvx ruff check .` depuis la même skill → « All checks passed! ».
- `gabarit check .claude/implementation/pipeline-gabarit.md --filled` → « rempli et conforme à la
  semence « suivi » », code 0.
- `gabarit check .claude/implementation/pipeline-gabarit.brief.md --filled` → code 1, « front
  matter absent ». C'est attendu : le brief sera converti à l'étape 7. Ce n'est pas un constat.
- Contrôle de R2 de `d4d7206` sur un clone : arbre `d32eeda` extrait hors du dépôt, et son
  `fiche.py` rendu volontairement défaillant, avec `~/.claude/bin` présent dans le PATH. Résultat :
  25 échecs. Les tests chargent donc bien le `fiche` du clone, et non celui installé sous `$HOME`.
  Sans ce sabotage, et avec un PATH réduit, le même clone donne 29 passés.
- Contrôle de R3 de `d4d7206` dans son propre scénario : clone sans `.venv`, où `python3` n'a pas
  `tomlkit`. `commit_chantier.py cloture … --dry-run` → `REFUS : bibliothèque introuvable depuis
  les commandes de bin/ : No module named 'tomlkit'`, code 1. On obtient un refus, et non plus une
  trace Python.

### Conformité à l'intention

Audit intermédiaire : les critères qui dépendent d'étapes encore `[ ]` ne sont pas reprochés.

- Critère « `gabarit check --filled` avant la validation du brief » : pas encore traité (étape 6).
- Critère « `gabarit check --filled` après le premier remplissage du suivi, et il conditionne
  l'implémentation » : pas encore branché dans la skill (étape 8). Pour ce chantier, le suivi passe
  déjà la vérification (exécutée ci-dessus).
- Critère « dettes soldées » : pas encore traité (étape 10). Pour `frontmatter-suivi-lu-par-regex`,
  l'état est inchangé depuis `d4d7206` : la condition de solde est remplie sur le fond, et la nuance
  R4 de `d4d7206` doit être dite au solde, comme le journal le prévoit.
- Critère « fiches de ce chantier au nouveau format » : le suivi est en TOML `+++` et conforme ; le
  brief sera converti à l'étape 7.
- Critère « entrée `road-map/` » : pas encore traité (étape 11).
- Hors-périmètre : respecté. `git diff master...pipeline-gabarit` est vide sur
  `.claude/implementation/done`, sur `skills/implementation-tracker/references` (donc sur
  `audit.md`), sur `skills/intent-brief` et sur `skills/gabarit`.
- Signaux de dérive : aucun ne s'est matérialisé. Aucune `SKILL.md` ni aucune référence n'a encore
  été modifiée.
- Symptôme d'origine : inchangé depuis `d4d7206`. Il est résorbé côté lecture du front matter, et
  la double écriture de la structure du suivi demeure jusqu'à l'étape 8.
- Correctif de l'étape 4, point par point :
  - R1 de `d4d7206` : **levé**. `skills/implementation-tracker/ruff.toml` est identique, aux
    commentaires près, à celui de `gabarit`, et la vérification d'ensemble ruff passe.
  - R2 de `d4d7206` : **levé**. Le `bin/` du dépôt testé passe en tête du PATH de chaque
    sous-processus (`ENV`, `test_commit_chantier.py:23-27`). Le test est indépendant du profil
    (PATH réduit) et du `$HOME` (clone saboté).
  - R3 de `d4d7206` : **levé**. `fiche` et `gabarit.items` sont importés dans `bibliotheques()`, qui
    s'exécute avant `preparer` et avant la sortie `--dry-run` (`commit_chantier.py:132-139`, appel
    l. 409). Un `ImportError` devient un `Refus`.

### Qualité du code

- **R1** — `skills/git-smart-commit/scripts/commit_chantier.py:139`. Le message de refus est le
  même, que `fiche` soit introuvable ou que la dépendance `tomlkit` manque : « bibliothèque
  introuvable depuis les commandes de bin/ : No module named 'tomlkit' ». Dans le second cas, qui
  est précisément le scénario de R3 de `d4d7206`, la cause est un `.venv` absent. Or le message
  oriente vers `bin/`. Le nom du module cité permet de rectifier, d'où une réserve mineure et non
  un défaut.
- **R2** — `skills/git-smart-commit/scripts/tests/test_commit_chantier.py:396-414`.
  `test_refus_si_une_bibliotheque_manque` éprouve le cas « `fiche` introuvable », avec de faux
  exécutables dans un `bin/` factice. Il n'éprouve pas le cas « `tomlkit` absent », qui a motivé
  R3. Ce cas passe aujourd'hui, comme l'a montré le contrôle manuel ci-dessus, mais aucun test ne
  le tient. Une réécriture qui ne capturerait que `ModuleNotFoundError` sur `fiche`, par exemple,
  ne ferait rien échouer.
- Style : conforme aux fichiers voisins.
  - Le commentaire en tête majuscule « IMPORTÉES ICI, AVANT TOUTE ÉCRITURE » reprend l'idiome du
    fichier.
  - `# noqa: …  # pyright: ignore[…]` suit l'usage de `gabarit-cli.py:24-25` et de
    `list-dir.py:22-23`.
  - `ruff.toml` et `pyrightconfig.json` suivent le modèle de `gabarit`, avec un commentaire
    d'en-tête qui justifie leur place.

### Dette induite

- **R3** — `.claude/implementation/todo/technical-debt/impl-list-sans-configuration-de-linters.md`.
  L'étape 4 pose `ruff.toml` et `pyrightconfig.json` dans `skills/implementation-tracker/`, et les
  deux linters lancés depuis la skill sortent à 0 (vérifié ci-dessus). C'est **exactement** la
  condition « Pour solder » de cette fiche. Pourtant la fiche reste dans `technical-debt/`, et son
  « Constat » (« La skill ne contient ni `ruff.toml` ni `pyrightconfig.json` ») est désormais faux.
  Ni le suivi ni le journal ne mentionnent ce solde de fait. Aucun critère ne l'exige, puisque le
  brief ne nomme que deux dettes. Mais le registre affirme maintenant une dette qui n'existe plus.
  Coût futur : un `debt-review` ou un futur chantier la reprendra pour rien. Il faut décider
  explicitement : la solder dans ce chantier (étape 10), ou la signaler à la clôture.
- **R4** — Le suivi et le plan ne sont plus alignés depuis l'insertion de l'étape 4.
  - Les « Notes » de l'État courant disent encore « Le brief reste en YAML `---` jusqu'à l'étape
    6 ». Après la renumérotation, la conversion est l'étape 7, et l'étape 6 est le branchement
    d'`intent-brief`.
  - Le plan garde sa numérotation d'origine, de 1 à 10 : son étape 4 est l'étape 5 du suivi, et
    ainsi de suite.

  Le suivi fait foi et le journal date la renumérotation : ce n'est donc pas une dérive. Mais un
  `step-implementer` qui lirait « étape 6 » dans les Notes, puis « étape 6 » dans le plan, tomberait
  sur trois contenus différents.
- R4 et R5 de `d4d7206` restent ouverts, comme le journal le prévoit : R4 sera dit au solde de la
  dette, R5 ira au registre à la clôture. Rien de nouveau.

### Bloquants

Aucun. R1 de `d4d7206`, seul bloquant de l'audit précédent, est levé.

## 2026-09-19 — clôture — `5e8df3a`

**Verdict** : DÉFAVORABLE

Périmètre audité : les étapes 1 à 12, toutes cochées `[x]` et commitées. L'arbre est propre.

Dans ce rapport, les numéros `R1` à `R5` sont ceux de la présente section. Les constats des audits
précédents sont cités sous la forme « R1 de `d4d7206` ».

Les cinq critères de réussite sont atteints et vérifiés par exécution. Le hors-périmètre est
respecté, et toutes les commandes des étapes passent. Le verdict tient à un seul constat, R1. Le
suivi désigne la « Vérification d'ensemble » du plan comme vérification. Cette vérification
comprend la commande qui contrôle le signal de dérive, et cette commande échoue. L'échec vient d'un
fichier que le chantier n'a pas touché, et relève peut-être d'une commande trop large plutôt que
d'une vraie dérive. Mais c'est à l'utilisateur de trancher, pas à l'auditeur : d'où le verdict le
plus sévère. Il se lève en un tour.

### Vérifications exécutées

- Vérification d'ensemble, `.venv/bin/python -m pytest scripts/tests
  skills/implementation-tracker/scripts/tests skills/git-smart-commit/scripts/tests
  skills/gabarit/scripts/tests` → 210 passés, 0 échec.
- Étape 5, `PATH=/usr/bin:/bin .venv/bin/python -m pytest -rs skills/git-smart-commit/scripts/tests`
  → 30 passés, 0 échec, aucun test ignoré.
- Étape 4 et vérification d'ensemble, `uvx ruff check scripts skills/implementation-tracker/scripts
  skills/git-smart-commit/scripts` → « All checks passed! ».
- Vérification d'ensemble, `uvx --with pytest basedpyright` sur les arbres extraits par `git
  archive`, avec le `.venv` du dépôt en lien symbolique : `master` → 2586 erreurs ; `5e8df3a` → 25
  erreurs. Ce sont les mêmes 25 qu'à l'audit `d32eeda` : `scripts/tests/test_sante_skills.py` et
  `skills/list-dir/`. Aucune ne touche un fichier du chantier.
- Depuis `skills/implementation-tracker/` : `uvx --with pytest basedpyright` → « 0 errors » ;
  `uvx ruff check .` → « All checks passed! ».
- Étapes 2, 7, 9 et 10, puis vérification d'ensemble : `python3 scripts/check_pipeline.py` (Python
  3.14.7 du PATH) → « Pipeline conforme », code 0.
- Étape 3, `commit-chantier lettre` → `B`, code 0.
- Étapes 6 et 8, puis vérification d'ensemble : `gabarit check
  .claude/implementation/pipeline-gabarit.brief.md --filled` → « rempli et conforme à la semence
  « brief » », code 0.
- Vérification d'ensemble : `gabarit check .claude/implementation/pipeline-gabarit.md --filled` →
  « rempli et conforme à la semence « suivi » », code 0.
- Étape 6 (dans le scratchpad) : `gabarit new brief`, puis `gabarit check` → « conforme à la
  semence « brief » », code 0. `gabarit new suivi` pose bien la semence.
- Étape 7 : `! grep -rn "gabarit-brief" skills agents` → code 0. Étape 9 : `! grep -rn
  "gabarit-suivi" skills agents` → code 0.
- Étape 10 : `! grep -rnE` sur les citations `` `champ: valeur` `` → code 0.
- Étape 11 : `list-dir validate .claude/implementation/todo/technical-debt-solde --filled` → 27
  éléments remplis et conformes, code 0.
- Étape 12 : `list-dir validate .claude/implementation/todo/road-map --filled` → 2 éléments remplis
  et conformes, code 0.
- Vérification d'ensemble, contrôle du signal de dérive, `! grep -rn '^```markdown'
  skills/intent-brief skills/implementation-tracker --exclude=audit.md` → **ÉCHEC**, code 1 :
  `skills/implementation-tracker/references/dette.md:222` et `:251`. Voir R1.
- Vérification d'ensemble : `test ! -e skills/intent-brief/references/gabarit-brief.md && test ! -e
  skills/implementation-tracker/references/gabarit-suivi.md` → code 0.
- Preuves des soldes rejouées :
  - `pytest test_fiche.py -k "double or diese"` → 3 passés ;
  - `grep -c` des anciens lecteurs regex dans `commit_chantier.py` et `check_pipeline.py` → 0 et 0 ;
  - les trois fiches sont absentes de `technical-debt/`, et leur historique suit le déplacement
    jusqu'à `2456640`. Le déplacement et la preuve sont dans deux commits séparés (`604acca`,
    `0dc47b4`).
- `commit-chantier cloture pipeline-gabarit --message <scratch> --dry-run` → code 0, « rien n'a été
  modifié ». Le suivi TOML est accepté, et les trois champs à réécrire comme les quatre
  déplacements sont annoncés. `git status` reste vide et `HEAD` inchangé.
- Réécriture de clôture simulée sur une copie du suivi, par `gabarit.items`
  (`statut`/`maj`/`plan`), puis `gabarit check --filled` → conforme, corps intact au `diff`.
- Brief converti : `diff` contre `a6d0ebf` → seul le front matter change, le corps est identique.
- `git diff master...pipeline-gabarit -- .claude/implementation/done` → vide.

### Conformité à l'intention

- Critère « `gabarit check --filled` exécuté avant la validation du brief » : **atteint**.
  - `skills/intent-brief/SKILL.md`, Étape 5, point 2 : un échec empêche de présenter le brief à la
    validation.
  - La sortie anticipée renvoie désormais à l'Étape 5, et non plus à l'Étape 6 : un brief minimal
    passe donc aussi par la vérification.
- Critère « `gabarit check --filled` après le premier remplissage du suivi, et il conditionne le
  début de l'implémentation » : **atteint**. Voir `skills/implementation-tracker/SKILL.md`, Étape 2,
  point 8 : « Un échec arrête la création : pas de commit de l'état initial, pas
  d'implémentation ». Ce chantier passe le contrôle (exécuté ci-dessus).
- Critère « dettes `suivi-pose-depuis-un-gabarit-markdown` et `frontmatter-suivi-lu-par-regex`
  soldées » : **atteint**.
  - Les deux fiches sont dans `technical-debt-solde/`, avec une section `Soldé le` dont les
    commandes ont été rejouées.
  - La nuance R4 de `d4d7206`, le double découpage `+++`, est dite en « Reste, assumé », comme le
    journal le prévoyait.
  - La troisième dette, `impl-list-sans-configuration-de-linters` (R3 de `d32eeda`), est soldée
    aussi, et sa preuve est rejouée.
- Critère « fiches de ce chantier converties au nouveau format » : **atteint**. Brief et suivi sont
  en TOML `+++`, et tous deux sont conformes à leur semence avec `--filled`. Le rapport d'audit
  garde son `---` : il est hors-périmètre.
- Critère « une entrée `road-map/` porte le rapport d'audit en liste `list-dir` » : **atteint**.
  `todo/road-map/rapport-audit-en-liste.md` est validée `--filled`, et son contenu reprend l'idée
  du brief (préremplissage par les audits précédents, à discuter).
- Hors-périmètre : **respecté**.
  - `done/` est intact.
  - Dans `audit.md`, seules les lignes 23, 46, 61, 62 et 76 changent, pour citer les champs du
    suivi en TOML (Q1, retenue au journal). Le « Gabarit du rapport » n'est pas touché.
- Symptôme d'origine : **disparu**.
  - Le modèle Markdown du suivi est supprimé : la semence est la seule structure, et elle est
    vérifiée à la création.
  - Le front matter a un lecteur unique, `fiche.lire_front`, sur une grammaire (`tomllib`). Il est
    partagé par `commit_chantier.py` et le contrôle 5.
- Signal de dérive « une skill garde un élément de fiche Markdown… » : non matérialisé dans le
  diff. Mais sa commande de contrôle échoue :
  - **R1** — La commande de la Vérification d'ensemble `! grep -rn '^```markdown'
    skills/intent-brief skills/implementation-tracker --exclude=audit.md` sort en code 1.
    - Ce qu'elle trouve : `skills/implementation-tracker/references/dette.md:222` et `:251`, deux
      blocs recopiables des sections `## Soldé le` et `## Écartée le` des entrées du registre de
      dette. Ces sections sont déclarées par les contrats de liste, par exemple
      `.claude/implementation/todo/technical-debt-solde/.list/contract.toml`, `[sections."Soldé
      le"]`.
    - `dette.md` n'est pas dans le diff : la commande échouait déjà sur `master`. Ni le suivi ni le
      journal ne mentionnent cet échec. La commande n'a donc pas été lancée en fin de chantier, ou
      son échec n'a pas été consigné.
    - Deux lectures sont possibles, et l'auditeur ne peut pas trancher :
      1. La commande est trop large. Le brief vise les fichiers « créés depuis un gabarit », et
         les entrées de dette sont déjà posées par `list-dir` depuis leur contrat. Ces blocs
         montrent la forme d'une preuve, pas la structure d'une fiche. Dans ce cas, il faut
         exclure `dette.md` de la commande et le noter au journal.
      2. Le signal s'applique à la lettre : une skill garde le modèle recopiable d'une section
         dont la semence existe. La dérive est alors avérée, hors du diff mais dans le périmètre
         du but.

    **Bloquant pour la clôture**, jusqu'à ce que l'utilisateur ait tranché et que le journal
    l'ait consigné.
  - **R2** — Deux passages de skill énumèrent encore les cinq blocs de `Objectif et périmètre`
    (symptôme, but, critères, hors-périmètre, signaux de dérive) :
    - `skills/implementation-tracker/SKILL.md`, Étape 2, point 7 ;
    - `skills/intent-brief/SKILL.md:231-233`.

    Depuis l'étape 6, la semence `suivi` porte cette même liste (« en cinq blocs »). Les deux
    passages existaient déjà sur `master`. Ils disent d'où vient le contenu (du brief) plutôt
    qu'ils ne prescrivent une structure. Il y a pourtant de nouveau deux endroits qui énumèrent les
    blocs, et c'est le motif même du signal. Réserve, à trancher avec R1.

### Qualité du code

- **R3** — `skills/implementation-tracker/SKILL.md:236` : « Comparer `branche:` du frontmatter ».
  C'est la dernière citation de champ au format YAML dans les skills du pipeline. La regex de
  l'étape 10 ne liste pas `branche` et exige une valeur après les deux-points : elle ne pouvait pas
  la voir. Réserve mineure.
- **R4** — Les dates du suivi ne sont pas écrites de la même façon.
  - `gabarit new suivi` pose `"créé" = "2026-09-19"` et `maj = "2026-09-19"` en chaînes (vérifié
    dans le scratchpad, et c'est le cas du suivi de ce chantier).
  - `commit_chantier.finaliser` réécrit `maj` en date TOML nue
    (`datetime.date.fromisoformat(c.date)`). Le suivi archivé mêlera donc les deux formes (simulé :
    `"créé" = "2026-09-19"` et `maj = 2026-09-20`).
  - Les fixtures de `test_commit_chantier.py:49-50` écrivent des dates nues : elles ne reproduisent
    pas ce que `gabarit new` produit.

  `gabarit check` et `fiche` acceptent les deux formes, donc rien ne casse. En revanche, le format
  d'un même champ dépend de celui qui l'a écrit en dernier. Réserve mineure.
- Style : conforme aux fichiers voisins. Commentaires en tête majuscule (« LECTEUR UNIQUE »,
  « IMPORTÉES ICI »), messages en français, `cast` sur les objets chargés dynamiquement,
  réexécution dans le venv reprise de `list-dir.py`. Rien à signaler.
- Cas limites de `fiche.lire_front` : refus nommés couverts par les tests (absent, non fermé,
  délimiteurs croisés, TOML invalide, non scalaire, clé en double dans les deux formats). Rien à
  signaler.

### Dette induite

- **R5** — R5 de `d4d7206` (13 erreurs `basedpyright` dans `skills/list-dir/`, rendues visibles
  par les `extraPaths`) reste sans fiche au registre. Le journal prévoit de l'y verser à la
  clôture, et c'est à faire au point 2 de `cloture.md`. Rappel, pas un défaut.
- Le double découpage `+++` (`fiche` / `gabarit.items`) est assumé et écrit au solde de la dette.
  Rien de nouveau.

### Bloquants

- R1 : la commande du signal de dérive, dans la Vérification d'ensemble, échoue (code 1 sur
  `dette.md:222,251`). La clôture reste bloquée tant que l'utilisateur n'a pas choisi entre deux
  voies, avec une trace au journal : restreindre la commande, ou traiter `dette.md`.

## 2026-09-20 — clôture — `14d6464`

**Verdict** : RÉSERVES

Périmètre audité : les étapes 1 à 14, toutes cochées `[x]` et commitées. L'arbre est propre, `HEAD`
est bien `14d6464`.

Dans ce rapport, les numéros `R1` à `R3` sont ceux de la présente section. Les constats des audits
précédents sont cités sous la forme « R1 de `5e8df3a` ».

Les cinq critères de réussite sont atteints et vérifiés par exécution. Le hors-périmètre est
respecté, l'élargissement du 2026-09-20 est daté au suivi et accepté par l'utilisateur. **Le
bloquant de l'audit précédent est levé** : la commande du signal de dérive sort maintenant en code
0. Toutes les commandes de vérification des quatorze étapes et de la « Vérification d'ensemble »
passent. Les trois constats restants sont mineurs et n'interdisent pas la clôture ; ils sont dits
parce que l'utilisateur doit les connaître avant de trancher.

### Vérifications exécutées

Toutes les commandes ci-dessous ont été lancées depuis `/home/debian/.claude`.

- Vérification d'ensemble, `.venv/bin/python -m pytest scripts/tests
  skills/implementation-tracker/scripts/tests skills/git-smart-commit/scripts/tests
  skills/gabarit/scripts/tests` → **220 passés**, 0 échec.
- Étape 14, `.venv/bin/python -m pytest scripts/tests skills/*/scripts/tests` → **667 passés**, 0
  échec.
- Étape 5, `PATH=/usr/bin:/bin .venv/bin/python -m pytest -rs skills/git-smart-commit/scripts/tests`
  → 30 passés, 0 échec, aucun test ignoré.
- Étape 4 et vérification d'ensemble, `uvx ruff check scripts skills/implementation-tracker/scripts
  skills/git-smart-commit/scripts` → « All checks passed! ».
- Depuis `skills/implementation-tracker/` : `uvx ruff check .` → « All checks passed! » ;
  `uvx --with pytest basedpyright` → « 0 errors, 0 warnings, 0 notes ». C'est la preuve de solde de
  `impl-list-sans-configuration-de-linters`, rejouée.
- Depuis `skills/gabarit/` : `uvx --with pytest basedpyright` → « 0 errors, 0 warnings, 0 notes » ;
  `uvx ruff check .` → « All checks passed! ». C'est le répertoire touché par l'étape 14.
- Depuis `skills/list-dir/` : `uvx --with pytest basedpyright` → 13 erreurs ; `uvx ruff check .` →
  3 erreurs E501. Comparé à l'arbre de `master` extrait par `git archive` : **les 13 erreurs de
  typage sont identiques, fichier par fichier et message par message** (`diff` des deux sorties
  normalisées → aucune différence), et les 3 erreurs `ruff` sont les mêmes. Aucune régression. Voir
  R3.
- Étapes 2, 7, 9, 10, 13 et vérification d'ensemble : `python3 scripts/check_pipeline.py` (python3
  du PATH) → « Pipeline conforme », code 0, les 9 contrôles au vert.
- Étape 3, `commit-chantier lettre` → `B`, code 0.
- Vérification d'ensemble : `gabarit check .claude/implementation/pipeline-gabarit.brief.md
  --filled` → « rempli et conforme à la semence « brief » », code 0 ; `gabarit check
  .claude/implementation/pipeline-gabarit.md --filled` → « rempli et conforme à la semence
  « suivi » », code 0.
- **Signal de dérive, vérification d'ensemble** : `! grep -rn '^```markdown' skills/intent-brief
  skills/implementation-tracker --exclude=audit.md` → **code 0, aucune occurrence**. R1 de
  `5e8df3a` est levé. `test ! -e skills/intent-brief/references/gabarit-brief.md && test ! -e
  skills/implementation-tracker/references/gabarit-suivi.md` → code 0.
- Étape 10 : `! grep -rnE` sur les citations `` `champ: valeur` `` → code 0.
- Étapes 11 et 14 : `list-dir validate .claude/implementation/todo/technical-debt-solde --filled` →
  **28 éléments** remplis et conformes, code 0 (27 au dernier audit, +1 pour la dette soldée à
  l'étape 14). `list-dir validate .claude/implementation/todo/technical-debt --filled` → 68
  éléments, code 0.
- Étape 12 : `list-dir validate .claude/implementation/todo/road-map --filled` → 2 éléments remplis
  et conformes, code 0.
- Preuve de solde de `prefill-date-preremplie-ecrite-guillemetee`, rejouée :
  `.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_date.py` → **10 passés**, conforme à
  ce que la fiche annonce ; `gabarit new suivi "$T/s.md"` → le front matter posé porte
  `"créé" = 2026-09-20` et `maj = 2026-09-20`, **nus**, sans guillemets. `gabarit new brief` de
  même. Le déplacement (`27660a4`) et la preuve (`14d6464`) sont dans deux commits séparés, et
  `git log --follow` remonte l'historique de l'entrée jusqu'à `4db0a9e`.
- `commit-chantier cloture pipeline-gabarit --message <scratch> --dry-run` → code 0, « rien n'a été
  modifié ». Les 17 commits sont réunis, les quatre déplacements et les trois champs à réécrire
  sont annoncés. `git status` reste vide, `HEAD` inchangé à `14d6464`.
- Hors-périmètre : `git diff master...pipeline-gabarit -- .claude/implementation/done` → **0 ligne**.
- `git diff master...pipeline-gabarit -- skills/implementation-tracker/references/audit.md` → 5
  lignes, toutes des citations de champ passées au TOML (Q1 du journal). Le « Gabarit du rapport »
  n'est pas touché.

### Conformité à l'intention

- Critère « `gabarit check --filled` exécuté avant la validation du brief » : **atteint**.
  `skills/intent-brief/SKILL.md`, Étape 5 : un échec empêche de présenter le brief à la validation.
  Inchangé depuis `5e8df3a`, où il était déjà vérifié.
- Critère « `gabarit check --filled` après le premier remplissage du suivi, et il conditionne le
  début de l'implémentation » : **atteint**. `skills/implementation-tracker/SKILL.md`, Étape 2 :
  « Un échec arrête la création : pas de commit de l'état initial, pas d'implémentation ». Le suivi
  de ce chantier passe le contrôle (exécuté ci-dessus).
- Critère « dettes `suivi-pose-depuis-un-gabarit-markdown` et `frontmatter-suivi-lu-par-regex`
  soldées » : **atteint**. Les deux fiches sont dans `technical-debt-solde/`, leurs preuves ont été
  rejouées aux audits précédents et la liste valide `--filled`. Deux dettes de plus ont été soldées
  au passage : `impl-list-sans-configuration-de-linters` et, à l'étape 14,
  `prefill-date-preremplie-ecrite-guillemetee` — preuve rejouée ci-dessus.
- Critère « fiches de ce chantier converties au nouveau format » : **atteint**. Brief et suivi sont
  en TOML `+++` et conformes à leur semence avec `--filled`. Le rapport d'audit garde son `---` :
  il est hors-périmètre, et l'entrée `road-map/` porte sa reprise.
- Critère « une entrée `road-map/` porte le rapport d'audit en liste `list-dir` » : **atteint**.
  `todo/road-map/rapport-audit-en-liste.md`, validée `--filled`.
- Hors-périmètre : **respecté**. `done/` est intact, le « Gabarit du rapport » d'`audit.md` n'est
  pas touché. L'élargissement du 2026-09-20 vers `skills/gabarit` et `skills/list-dir` est écrit et
  daté dans `## Objectif et périmètre` du suivi, et dit accepté par l'utilisateur : c'est un
  périmètre légitime, pas un débordement.
- Signal de dérive « une skill garde un élément de fiche Markdown… » : **non matérialisé**, et sa
  commande de contrôle passe désormais. L'étape 13 a tranché dans le sens du signal :
  - `references/dette.md` a perdu ses deux blocs ```` ```markdown ```` recopiables ; ils sont
    remplacés par un renvoi au contrat de liste (`list-dir contract …`) plus un exemple en
    citation, qui montre la forme de la preuve sans redéclarer la structure. La correction tient :
    ce qui reste est un exemple de contenu, pas un modèle de sections ;
  - `implementation-tracker/SKILL.md:195` et `intent-brief/SKILL.md:231-233` n'énumèrent plus les
    cinq blocs d'`Objectif et périmètre` et renvoient à la semence `suivi`. R2 de `5e8df3a` est
    levé ;
  - `implementation-tracker/SKILL.md:236` dit maintenant « le champ `branche` du front matter ».
    R3 de `5e8df3a` est levé.
- Symptôme d'origine : **disparu**. Le modèle Markdown du suivi et celui du brief sont supprimés ;
  la semence est la seule déclaration de structure, et elle est vérifiée à la création. Le front
  matter a un lecteur unique, `fiche.lire_front`, sur une grammaire (`tomllib`), partagé par
  `commit_chantier.py` et le contrôle 5 de `check_pipeline.py`.

### Levée des constats de `5e8df3a`

- R1 (bloquant) : **levé**, commande exécutée, code 0.
- R2 : **levé**, les deux énumérations renvoient à la semence.
- R3 : **levé**, `branche` n'est plus cité au format YAML.
- R4 : **levé à la source**. `gabarit.prefill.initial_field` convertit en `datetime.date` une valeur
  de champ `date` issue de `text` ou de `command`, **après** `check_value` et en laissant passer les
  marqueurs (`is_marker`). Le commentaire en place explique le pourquoi, pas le comment. La
  correction est dans `gabarit`, donc `list-dir` en profite par délégation
  (`listdir/prefill.py:74-76`), et les deux tests de `list-dir` qui figeaient l'ancienne graphie ont
  été mis à jour, pas contournés. `skills/gabarit/scripts/tests/test_date.py` couvre les deux
  origines, le refus nommé d'une sortie non-ISO (4 cas paramétrés, dont la chaîne vide), la
  conservation du marqueur, la graphie écrite et l'aller-retour écriture/relecture. Voir R2
  ci-dessous pour le résidu.
- R5 (13 erreurs `basedpyright` dans `skills/list-dir/`) : **couvert**. Contrairement à ce que
  l'audit `5e8df3a` supposait, une fiche existe déjà au registre depuis `2456640` :
  `todo/technical-debt/basedpyright-treize-erreurs-non-tenues.md`, datée du 2026-09-05. Rien n'est
  à verser.

### Qualité du code

- **R1** — `skills/implementation-tracker/SKILL.md:196` se termine par une espace en fin de ligne,
  introduite à l'étape 13. C'est la seule ligne du dépôt dans ce cas parmi les trois fichiers de
  prose modifiés. Aucun contrôle ne l'attrape, rien ne casse ; c'est une coquille d'édition.
  Réserve cosmétique.
- Style de `prefill.py` : conforme au fichier. Commentaire en tête majuscule (« UNE DATE SE POSE
  NUE », « APRÈS `check_value` »), qui dit le pourquoi et la contrainte d'ordre, comme les
  commentaires voisins. Import `datetime` en stdlib, `is_marker` importé du module où il vit. Rien
  à signaler.
- Cas limites du correctif : `isinstance(value, str)` protège d'une double conversion, `is_marker`
  protège les marqueurs `<À REMPLIR>`/`<OPTIONNEL>`, et le placement après `check_value` garantit
  qu'aucune `fromisoformat` ne peut lever sur une valeur non validée. Les tests couvrent chacun de
  ces trois points. Rien à signaler.
- Style de `test_date.py` : docstring de module qui dit « ce que ce fichier prouve » et « pourquoi
  la graphie est l'enjeu », séparateurs en commentaire, noms de tests en phrase française —
  identique aux tests voisins de la skill.

### Dette induite

- **R2** — Le suivi de ce chantier garde ses dates guillemetées : `"créé" = "2026-09-19"` et
  `maj = "2026-09-20"`. Il a été posé avant le correctif de l'étape 14, et rien ne l'a réécrit.
  À la clôture, `commit_chantier.finaliser` réécrira `maj` en date TOML nue : **le suivi archivé
  portera les deux graphies du même type de champ**, ce qui est exactement le constat R4. La source
  est corrigée et tous les fichiers posés désormais sont homogènes ; il ne reste que cet
  exemplaire-là, et le brief, dont le `"créé"` est dans le même cas. Rien ne casse — `fiche`,
  `gabarit check` et `tomllib` acceptent les deux formes. À trancher : réécrire les deux champs à
  la main avant la clôture, ou laisser. Réserve.
- **R3** — Depuis `skills/list-dir/`, `uvx ruff check .` sort 3 erreurs E501 (`scripts/tests/
  test_contract.py:108`, `scripts/tests/test_fusion.py:266` et `:292`) et
  `uvx --with pytest basedpyright` en sort 13. **Ce n'est pas une régression** : l'arbre de `master`
  extrait donne exactement les mêmes, et aucun des fichiers fautifs n'est dans le diff. Les 13
  erreurs de typage ont leur fiche au registre ; les 3 E501 n'en ont pas. Le chantier n'avait pas à
  les traiter, et ce n'est donc pas un manquement — mais l'élargissement du 2026-09-20 a fait entrer
  `skills/list-dir` dans le diff, et l'utilisateur doit savoir que les linters de cette skill ne
  sortent pas à zéro. Réserve, ou entrée au registre s'il le souhaite.
- Le double découpage `+++` (`fiche` pour lire, `gabarit.items` pour réécrire) reste assumé et écrit
  au solde de la dette `frontmatter-suivi-lu-par-regex`. Rien de nouveau.
- Le correctif de l'étape 14 n'introduit ni duplication, ni abstraction, ni couplage nouveau : il
  ajoute 10 lignes au point unique où la valeur initiale d'un champ est fabriquée, et supprime de
  fait la divergence au lieu d'en gérer les deux branches.

### Bloquants

Aucun. R1 de `5e8df3a`, seul bloquant du précédent audit, est levé par exécution.
