# Plan — pipeline-gabarit

Brief : `.claude/implementation/pipeline-gabarit.brief.md` (validé 2026-09-18).

## Contexte

La structure du suivi est écrite à deux endroits : `skills/implementation-tracker/references/gabarit-suivi.md`
et la semence `skills/gabarit/gabarit/suivi/contract.toml`. Rien ne les confronte l'un à l'autre. Le
brief n'a pas de semence, seulement `skills/intent-brief/references/gabarit-brief.md`. Le front
matter YAML `---` est lu par deux regex alignées à la main : `commit_chantier.py:frontmatter` et
`remplacer_champ`, et `check_pipeline.py` contrôle 5 (l. 394). But : poser et vérifier brief et
suivi par `gabarit`, avec un seul lecteur de front matter, et solder les dettes
`suivi-pose-depuis-un-gabarit-markdown` et `frontmatter-suivi-lu-par-regex`.

**Critères de réussite repris du brief** :
- `gabarit check --filled` avant la validation du brief ;
- `gabarit check --filled` après le premier remplissage du suivi, et il conditionne le début de
  l'implémentation ;
- les deux dettes sont soldées ;
- les fiches de ce chantier sont au nouveau format ;
- une entrée `road-map/` pour le rapport d'audit en `list-dir` est créée en fin de chantier.

**Hors-périmètre** : `done/` n'est pas touché ; le rapport d'audit et son « Gabarit du rapport »
(`audit.md`) non plus.

**Signal de dérive** : une skill garde un élément de fiche Markdown (modèle recopiable, liste de
sections ou de champs) au lieu de renvoyer à la semence. Le rapport d'audit fait exception.

**Incertitudes** : aucune reportée. Les trois de cadrage ont été tranchées au brief :
- audit : hors-périmètre ;
- lecteur unique, qui lit les deux formats ;
- conversion des fiches dès que leurs semences existent.

## Choix de conception

- **Lecteur unique en bibliothèque standard** :
  - `skills/implementation-tracker/scripts/fiche.py`, à côté d'`impl_list.py`, dont il reprend le
    mode de chargement ;
  - `+++` est lu par `tomllib` ; `---` est lu par l'ancienne regex, déplacée ici, et **uniquement
    pour les archives de `done/`** ;
  - il doit rester en bibliothèque standard parce que `cloture.md` lance
    `python3 scripts/check_pipeline.py` avec le python3 du PATH, qui n'a pas `tomlkit`.
- **Écriture par l'écrivain de `gabarit`** :
  - `commit_chantier` réécrit `statut`, `maj`, `plan`, `brief` et `audit` avec `gabarit.items`
    (reprojection par tomlkit, l'« unique écrivain ») ;
  - il se réexécute dans le `.venv`, comme `gabarit-cli.py` (l. 33-46) ;
  - un suivi actif encore en YAML est refusé, avec un message qui dit de le convertir. Il n'en
    restera aucun, puisque `done/` ne s'écrit plus.
- **Semences à côté de `suivi`** : `brief` est créée dans `skills/gabarit/gabarit/brief/`. Le
  tableau « Les semences livrées » de `skills/gabarit/SKILL.md` s'étend.
- **Ce que devient le suivi de ce chantier** : la semence `suivi` existe déjà. Le suivi de ce
  chantier est donc posé par `gabarit new suivi` dès sa création (Étape 2 du tracker), et vérifié
  par `gabarit check --filled` avant le commit de l'état initial. Le brief sera converti à
  l'étape 6.

## Étapes

1. **Lecteur unique `fiche`** — `skills/implementation-tracker/scripts/fiche.py`,
   `skills/implementation-tracker/scripts/tests/test_fiche.py`.
   - `lire_front(texte) -> dict[str, str]` : TOML `+++` ou, en repli, YAML `---`. Refus nommés :
     front matter absent, non fermé, TOML invalide.
   - Tests :
     - une valeur contenant ` #`, lue intacte en TOML ;
     - une clé en double rejetée, au lieu d'être tronquée — c'est la condition de solde de la
       dette ;
     - le repli YAML avec son commentaire de fin de ligne.
   - vérif : `/home/debian/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests`

2. **Contrôle 5 sur `fiche`** — `scripts/check_pipeline.py`, `scripts/tests/test_controles_4_5.py`.
   - Charger `fiche.py` du dépôt audité par `importlib`, comme `charger_suivis`, et supprimer la
     regex de la l. 410.
   - Tests : une archive TOML et une archive YAML qui résolvent, et une archive TOML qui pointe
     dans le vide.
   - vérif : `/home/debian/.claude/.venv/bin/python -m pytest scripts/tests && python3 scripts/check_pipeline.py`

3. **`commit_chantier` : lecture par `fiche`, écriture par `gabarit`** —
   `skills/git-smart-commit/scripts/commit_chantier.py`, `skills/git-smart-commit/scripts/tests/test_commit_chantier.py`.
   - Supprimer `frontmatter()` et `remplacer_champ()`.
   - Localiser les bibliothèques depuis les liens `bin/impl-list` et `bin/gabarit`
     (`shutil.which`, OUTILLAGE.md).
   - Se réexécuter dans le `.venv`, et mettre à jour la docstring « Stdlib seule ».
   - Réécrire les fixtures de test en TOML ; ajouter un test « suivi YAML refusé ».
   - vérif : `/home/debian/.claude/.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests && commit-chantier lettre`

4. **Semence `brief`, semence `suivi` autodescriptive** — `skills/gabarit/gabarit/brief/contract.toml`,
   `skills/gabarit/gabarit/suivi/contract.toml`, `skills/gabarit/SKILL.md`.
   - `brief` porte :
     - les champs `slug`, `titre`, `statut` (`brouillon`|`validé`, prérempli `brouillon`),
       `execution`, et `créé` (`date +%F`) ;
     - les sections `Intention`, `Critères de réussite`, `Hors-périmètre`, `Signaux de dérive`,
       `Contraintes connues de l'utilisateur`, `Incertitudes à lever en plan`.
   - Les descriptions absorbent les « Notes de remplissage » des deux modèles en prose : règle du
     marqueur `(dit)`/`(dépôt: …)`, symptôme, état courant, dernier audit avec SHA.
   - Retirer de `suivi/contract.toml` les commentaires d'en-tête qui renvoient à `gabarit-suivi.md` et disent que le tracker n'est pas encore branché.
   - vérif : `gabarit contract brief && gabarit new brief "$T/b.md" && gabarit check "$T/b.md"`
     (`T` = scratchpad)

5. **Brancher `intent-brief`** — `skills/intent-brief/SKILL.md`, suppression de
   `skills/intent-brief/references/gabarit-brief.md`.
   - Étape 2 : `gabarit new brief .claude/implementation/<slug>.brief.md`, puis lire
     `gabarit contract brief` avant de remplir.
   - Étape 5 : `gabarit check <brief> --filled`. Un échec interdit de passer `statut` à
     `validé`.
   - Plus aucune liste de sections ni de champs dans la skill.
   - vérif : `! grep -rn "gabarit-brief" skills agents && python3 scripts/check_pipeline.py`

6. **Convertir le brief de ce chantier** — `.claude/implementation/pipeline-gabarit.brief.md`.
   - `gabarit new brief` vers un fichier temporaire, recopie du contenu validé sans le
     reformuler, puis remplacement du fichier.
   - Le contenu reste figé ; seul le format change. À noter au journal.
   - vérif : `gabarit check .claude/implementation/pipeline-gabarit.brief.md --filled`

7. **Brancher `implementation-tracker`** — `skills/implementation-tracker/SKILL.md`,
   `references/contrat.md`, suppression de `references/gabarit-suivi.md`.
   - Étape 2, point 4 :
     1. `gabarit new suivi .claude/implementation/<slug>.md` ;
     2. remplissage d'après `gabarit contract suivi` ;
     3. `gabarit check --filled`, dont l'échec **bloque** la branche et le commit de l'état
        initial.
   - Supprimer la section « Gabarit du fichier de suivi » de `SKILL.md`.
   - `contrat.md#frontmatter` : le tableau des champs est remplacé par un renvoi aux semences
     (`gabarit contract brief|suivi`). On garde :
     - les règles de comportement : `execution` absent vaut `direct`, `session` incrémenté à
       chaque reprise, réécriture de `plan`/`brief`/`audit` à l'archivage ;
     - leurs modes de défaillance ;
     - la ligne `<slug>.audit.md`, qui est hors-périmètre.
   - vérif : `! grep -rn "gabarit-suivi" skills agents && python3 scripts/check_pipeline.py`

8. **Citer les champs au format TOML partout où ils sont écrits** —
   `skills/git-smart-commit/references/{etape,aplatissement,branche-chantier,tags-etape}.md`,
   `skills/implementation-tracker/references/{cloture,road-map}.md`,
   `skills/implementation-tracker/SKILL.md`, `skills/intent-brief/SKILL.md`,
   `agents/{step-implementer,implementation-auditor}.md`,
   `skills/skill-convention/references/prose.md` (« Pratiqué dans »).
   - Toute valeur prescrite (`statut: abandonné`…) s'écrit `statut = "abandonné"`, et « front
     matter `---` » devient `+++`.
   - Les agents restent autosuffisants (contrôle 4).
   - vérif : `! grep -rnE '\`(statut|maj|session|lettre|base|execution|plan|brief|audit|road-map): [^\`]+\`' skills agents --exclude-dir=synced && python3 scripts/check_pipeline.py`
     (18 occurrences aujourd'hui)

9. **Solder les deux dettes** — `list-dir move` vers `technical-debt-solde/`, selon la procédure
   de `references/dette.md`, avec la commande qui établit chaque solde :
   - le test « clé en double rejetée » de l'étape 1 ;
   - le `gabarit check --filled` du suivi de ce chantier.
   - vérif : `list-dir validate .claude/implementation/todo/technical-debt-solde --filled`

10. **Entrée road-map du rapport d'audit** — `list-dir new` dans `todo/road-map/` : le rapport
    d'audit porté par une liste `list-dir`, dont chaque nouvel audit a le front matter prérempli
    par les audits précédents. Elle est à discuter et à approfondir.
    - vérif : `list-dir validate .claude/implementation/todo/road-map --filled`

## Vérification d'ensemble

```bash
cd /home/debian/.claude
.venv/bin/python -m pytest scripts/tests skills/implementation-tracker/scripts/tests skills/git-smart-commit/scripts/tests skills/gabarit/scripts/tests
uvx ruff check scripts skills/implementation-tracker/scripts skills/git-smart-commit/scripts
uvx --with pytest basedpyright
python3 scripts/check_pipeline.py
gabarit check .claude/implementation/pipeline-gabarit.brief.md --filled
gabarit check .claude/implementation/pipeline-gabarit.md --filled
```

Signal de dérive, à contrôler en fin de chantier : plus aucun bloc de fiche recopiable ni aucune
liste de sections dans `skills/intent-brief` ni `skills/implementation-tracker`, `audit.md`
excepté :

```bash
! grep -rn '^```markdown' skills/intent-brief skills/implementation-tracker --exclude=audit.md
test ! -e skills/intent-brief/references/gabarit-brief.md && test ! -e skills/implementation-tracker/references/gabarit-suivi.md
```

Le diff dépassera probablement 400 lignes vers l'étape 7 : un audit intermédiaire sera alors
proposé.

## Relecture `plan-reviewer` — verdict RÉSERVES

Le plan couvre les cinq critères, respecte le hors-périmètre, et aucun signal de dérive ne se
déclenche.

**Défauts de rédaction corrigés sans arbitrage** :
- Q4 : la regex est à la l. 410, pas à la l. 413 ;
- Q3 : l'étape 4 retire aussi l'en-tête de `contract.toml` qui cite `gabarit-suivi.md`, sans quoi
  la vérification de l'étape 7 échouait ;
- Q2 : la regex de l'étape 8 ne voyait que 2 citations sur 18 ; elle les voit maintenant toutes,
  et les deux `SKILL.md` sont ajoutés à la liste ;
- Q9 : `--filled` est ajouté aux vérifications `list-dir` ;
- Q11 : le contrôle du signal de dérive porte maintenant une commande.

**Constats à trancher** :
- **Q1** : `audit.md:61` et `audit.md:76` prescrivent des valeurs YAML dans le front matter du
  suivi (`audit: …`, `statut: bloqué`). Proposition : aligner ces deux lignes au TOML à l'étape 8,
  sans toucher au « Gabarit du rapport ».
- **Q5** : d'autres règles de `contrat.md#frontmatter` ne sont pas citées dans « On garde » :
  - `road-map` n'est pas réécrit à l'archivage ;
  - la clôture refuse un suivi sans `lettre` ;
  - `audit` n'apparaît qu'au premier audit.

  Proposition : les garder toutes, et garder mot pour mot l'empreinte « Une valeur absente vaut »
  (contrôle 2).
- **Q6** : le brief de ce chantier est converti à l'étape 6, donc après le branchement
  d'intent-brief (étape 5) et pas juste après la naissance de sa semence (étape 4).
- **Q7** : les fixtures de `test_controles_4_5.py` devront aussi écrire `fiche.py` dans le
  dépôt-jouet. Cela relève de l'étape 2.
- **Q8** : `pyrightconfig.json` doit recevoir les `extraPaths` de
  `skills/implementation-tracker/scripts` et `skills/gabarit/scripts`, aux étapes 1 et 3.
- **Q10** : solder une dette demande deux commits (d'abord le déplacement, ensuite la preuve).
  L'étape 9 prend donc deux tours.
- **Q12** : `commit_chantier` découperait le `+++` deux fois, une fois par `fiche` pour lire, une
  fois par `gabarit.items` pour réécrire.
- **Q13** : le repli YAML « réservé aux archives » n'est tenu que par l'appelant, pas par
  `lire_front`.
