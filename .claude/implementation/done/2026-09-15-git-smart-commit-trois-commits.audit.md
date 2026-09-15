---
slug: git-smart-commit-trois-commits
---

## 2026-09-14 — clôture — `69e5fcc`

**Verdict** : RÉSERVES

Lus : le brief, le suivi, le plan (`.claude/plans/purrfect-puzzling-bachman.md`) et le diff
`master...git-smart-commit-trois-commits` en entier (24 fichiers, +1487 −377). En cas d'écart, le
suivi fait foi : l'arbitrage Q1 du 2026-09-14 remplace le « devient un renvoi » du brief par la
suppression de `contrat.md` § Branche et commits.

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → code 0, « Pipeline conforme », contrôles 1 à 9 verts.
- `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests -q` → 14 passés, 0 échec.
- `.venv/bin/python -m pytest scripts/tests skills/list-dir/scripts/tests skills/git-smart-commit/scripts/tests -q`
  → 574 passés. Même décompte dans l'ordre inverse des suites (574). Par suite : 113 / 447 / 14,
  conforme au tableau du README.
- `uvx ruff check skills/git-smart-commit` → « All checks passed! », code 0.
- `uvx ruff check scripts skills/list-dir skills/git-smart-commit` → **code 1**, 3 E501, tous dans
  `skills/list-dir/scripts/tests`. Le même `ruff check scripts skills/list-dir` sur l'arbre `master`
  extrait donne aussi « Found 3 errors ».
- `uvx --with pytest basedpyright` (HEAD) → **code 1**, 25 erreurs, 0 dans `skills/git-smart-commit`.
  Sur `master` extrait par `git archive` (même `.venv`) → 25 erreurs. Le `diff` des deux listes,
  chemins normalisés, est **vide**.
- Vérif de l'étape 1, telle qu'écrite → **code 1**, à cause du seul `basedpyright`.
- Vérif de l'étape 2 (`check_pipeline && ! grep -n "tracker" …`) → code 0.
- Vérif de l'étape 3 (`! grep -rn "branche-et-commits\|court-circuité\|ne passent pas par" …`) → code 0.
- Vérif de l'étape 4 (`! grep -rn "merge --squash\|branch -D" skills --include="*.md" | grep -v …`),
  sous bash → code 0.
- Vérif de l'étape 5, telle qu'écrite → **code 1** (ruff et basedpyright, voir plus haut).
- Grep d'indépendance du plan (`grep -n "hors-chantier\|etape.md\|aplatissement" references/*.md`) :
  aucun renvoi d'un fichier de type vers un autre. Les seules occurrences sont des renvois vers les
  fichiers communs et le mot « aplatissement » dans la prose.
- `git diff --stat master...git-smart-commit-trois-commits -- .claude/implementation/done` → vide.
- **Clôture réelle sur un clone jetable** (`git clone --no-local` dans le scratchpad, dépôt audité non
  touché), avec un `<slug>.audit.md` non suivi : le `--dry-run` sort en 0 et laisse `git status`
  inchangé. L'exécution sort en 0 : un commit sur `master`, 4 fichiers en `done/`, champs
  `plan/brief/audit` réécrits, `statut: terminé`, branche supprimée, arbre propre.
  `check_pipeline.py` sur ce résultat → « Pipeline conforme », code 0.
  Relance après coup → `REFUS : branche courante « master »`, code 1.
- **Relance après une finalisation déjà commitée** (autre clone) → `ÉCHEC … nothing to commit`,
  code 1, rien d'autre de modifié (voir R2).

### Conformité à l'intention

- Critère « trois parties indépendantes, chacune lue seulement au besoin » : **atteint**, vérifié par
  lecture et par grep. `SKILL.md` (35 lignes) route vers `hors-chantier.md`, `etape.md` et
  `aplatissement.md` avec « lire celui du type demandé, et lui seul ». Aucun fichier de type ne
  renvoie à un autre, et `SKILL.md`, le type 1 et les fichiers communs ne citent pas le tracker.
- Critère « texte commun dans des fichiers séparés et référencés, sans recopie » : **atteint**, avec
  une réserve de méthode (R9). Chaque motif distinctif cherché n'a qu'un seul lieu de définition :
  « ramasse ce qui traîne », « Proposer, attendre, exécuter », « exclut son début », « ne vaut
  qu'accompagné ». Le staging et l'accord sont sortis de `contrat.md`, et la section a disparu.
- Critère « `check_pipeline.py` sort avec 0 » : **atteint**, vérifié.
- Critère « tests pytest sur dépôt jouet : dry-run, aplatissement, suppression des tags, refus sur
  conflit » : **atteint**, vérifié. Tests correspondants : `test_dry_run_ne_modifie_rien`,
  `test_cloture_aplatit_archive_et_nettoie`, `test_cloture_ne_supprime_que_les_tags_de_sa_lettre`
  (liste des tags vide dans le test nominal) et `test_refus_sur_conflit_avec_la_base`. S'y ajoutent
  les refus sur cible existante, titre, ligne 2, branche, fichier étranger et `lettre` absente.
- Critère « `ruff` et `basedpyright` passent sur le nouveau script » : **atteint**, vérifié. ruff
  sort en 0 sur `skills/git-smart-commit`. basedpyright ne signale aucune erreur sous ce chemin, et
  le décompte global est identique à `master`, erreur par erreur.
- Contraintes du brief :
  - trois types dans un seul skill : oui ;
  - fichiers communs sous `references/` : oui ;
  - le tracker appelle le type 2 pour les commits d'étape, de session et d'E0 : oui (`SKILL.md`
    points 3, 7 et 8, Étapes 3 et 4) ;
  - `lettre:` au frontmatter, avec la commande `lettre` : oui ;
  - tags `<L>E<n>` : oui ;
  - `--message <fichier>` transmis par `git commit -F`, et `--dry-run` : oui ;
  - `cloture.md` conservé et renvoyant au script : oui ;
  - le script ne fait que les points 3 et 4 : oui. L'élargissement de l'indexation aux annexes est
    daté au journal.
- Hors-périmètre (`done/`) : **respecté**, le diff sur `done/` est vide.
- Signaux de dérive :
  - *modification hors du système de commit* : non matérialisé. Les 24 fichiers relèvent du skill, du
    tracker, de l'outillage (`bin/`, `ruff.toml`, README des tests) ou des annexes du chantier. La
    fiche de dette `frontmatter-suivi-lu-par-regex` a été demandée par l'utilisateur (journal). Le
    README corrige au passage les décomptes périmés des deux autres suites (101→113, 241→447) :
    c'est marginal, et la valeur est juste.
  - *jugement dans le script* : non matérialisé. `commit_chantier.py` ne fait que des contrôles
    mécaniques et les opérations. Message, journal et décision restent hors du script.
  - *texte recopié* : non matérialisé, sous la réserve R9.
- Symptôme d'origine : **disparu**. L'ancien `SKILL.md` de 212 lignes mêlait workflow et
  aplatissement. Le nouveau n'est plus qu'un routeur, et `squash.md` est supprimé.

### Qualité du code

- **R1** — Vérifs des étapes 1 et 5 : elles sortent en **code 1** telles qu'écrites. La cause est
  `basedpyright` (25 erreurs) et, pour l'étape 5, `ruff` (3 E501), dans `scripts/tests` et
  `skills/list-dir`. Ces erreurs existent à l'identique sur `master`, établi par un arbre extrait et
  un diff vide des deux listes. Aucune n'est donc imputable au chantier, et aucune ne peut être
  corrigée sans sortir du périmètre, ce qui serait le premier signal de dérive. *Pourquoi RÉSERVES
  et pas DÉFAVORABLE* : la règle « commande de vérification en échec » vise une régression. Elle
  n'est pas matérialisée ici, et les critères du brief, rédigés sur le « nouveau script », sont
  tenus. L'utilisateur doit toutefois savoir que ces deux commandes, telles qu'écrites, ne peuvent
  pas passer tant que la dette de typage de `list-dir` et `scripts/tests` reste ouverte.
- **R2** — `commit_chantier.py:278` : après un `ÉCHEC` survenu au-delà du commit de finalisation
  (checkout, merge, `git mv`, commit final), **la clôture ne peut pas être relancée**. Le suivi est
  déjà en `statut: terminé` avec `maj:` du jour, la réécriture ne change rien, et
  `git commit -m "<slug>: finalisation du suivi"` échoue sur « nothing to commit ». C'est vérifié
  sur un clone. C'est cohérent avec « ne rien relancer » d'`aplatissement.md`, mais aucune
  procédure ne dit comment reprendre à la main. Le message d'`ÉCHEC` nomme la commande fautive, pas
  l'étape atteinte : il faut reconstituer depuis `git status` ce qui reste à faire parmi 4 gestes.
- **R3** — `commit_chantier.py:114-119` (`remplacer_champ`) : ce chemin d'échec est **silencieux**.
  Le motif de réécriture exige `cle: ` suivi d'une espace, alors que le lecteur (`frontmatter`,
  l. 108) accepte `cle:valeur`. Un champ `maj:` absent, ou écrit sans espace, n'est pas réécrit, et
  rien ne le signale. Le même mécanisme laisserait `statut:` inchangé sur un suivi mal formé, qui
  serait archivé « en-cours ». Le gabarit écrit toujours l'espace, donc le risque est faible, mais
  aucun refus ne le couvre.
- **R4** — `cloture.md` point 2 (« le script … indexe lui aussi `todo/`, mais seulement s'il va
  jusqu'au bout ») : l'explication est **inexacte**. Le script indexe `todo/` dès sa première
  écriture, dans le commit de finalisation (`commit_chantier.py:275-278`), pas à la fin. Les cas
  réellement non couverts sont un `REFUS` et un script jamais lancé. La consigne (`git add` immédiat)
  reste juste, son motif ne l'est plus. C'est justement le texte que le journal disait avoir corrigé.
- **R5** — Des chemins du script restent **sans test** : le chemin `Echec` (arrêt après écriture et
  affichage de l'état), l'indexation de `todo/` dans le commit de finalisation, les refus « plan
  introuvable », « hors de la racine » et « base introuvable ». Aucun critère ne les exige, mais R2
  et R4 se logent précisément dans ces zones.
- **R6** — `aplatissement.md` § Abandon, *garder la branche* : `git add .claude/implementation/done/`
  indexe un **répertoire entier**, alors que `staging.md` du même skill impose « des chemins nommés,
  jamais `-A` — ni `-u`, ni `.` ». Une archive d'un autre chantier laissée non suivie partirait dans
  ce commit. Ce n'est pas `-A` à la lettre, mais c'en est l'effet à l'échelle de `done/`. Le cas
  *tout jeter*, juste au-dessus, nomme bien le fichier archivé.

Style : il est aligné sur `list-dir`. `ruff.toml` est calqué sur le sien, le docstring de module
suit la même forme (paragraphes en capitales), les tests passent par un sous-processus sans
`conftest.py`, et le lien est dans `bin/`. Rien à signaler au-delà des constats ci-dessus.

### Dette induite

- **R7** — La dette `git-smart-commit-illisible-seul`, dont le brief annonce le solde, **n'est pas
  entièrement résorbée**. Son constat porte sur un renvoi de `git-smart-commit` vers
  `../../implementation-tracker/references/contrat.md`, qu'un déplacement du tracker casserait. Or
  `aplatissement.md:64` et `:66` portent encore exactement ce renvoi (`#arborescence-et-nommage`,
  `#frontmatter`). Ce qui a changé : la dépendance est confinée au type 3, qui ne se lit que depuis
  le tracker, et `SKILL.md`, le type 1 et les communs en sont libres. Le solde est défendable sur
  cette base, mais la section `## Soldé le` doit le dire et le prouver par une commande, par exemple
  `grep -rn "implementation-tracker" skills/git-smart-commit`, dont la sortie montrera ces deux
  lignes. Sinon, le registre affirmera une indépendance qui n'est pas tout à fait vraie.
- **R8** — Deux entrées de dette **annoncées au journal ne sont pas encore écrites** :
  - la règle de staging, sortie de `contrat.md`, a perdu la protection anti-recopie du contrôle 2 ;
  - l'abandon *garder la branche* archive un suivi dont `plan:` et `brief:` visent des fichiers
    absents de `base`, et le contrôle 5 échouera.

  Elles sont prévues à la clôture (« Prochaine action »). Le coût d'un oubli est concret : la
  seconde fera virer le garde-fou au rouge au premier abandon de ce type, sans trace de la cause.
- **R9** — Les critères « indépendance » et « pas de recopie » **n'ont aucune commande dédiée**
  (constats Q5 et Q10 du plan, restés ouverts). Je les juge atteints par lecture et par grep de
  motifs, ce qui ne protège pas l'avenir : le contrôle 2 du garde-fou ne lit que `contrat.md`, et
  une recopie future entre fichiers du skill ne sera pas détectée (voir R8). Petite redite
  constatée : « s'arrêter net » sur `REFUS`/`ÉCHEC` figure à la fois dans `aplatissement.md:30` et
  `cloture.md:117`. Elle est tolérable, puisque le tracker énonce la conduite de son côté, mais c'est
  le type de doublon que rien ne surveille.
- **R10** — **Le type 2 n'a jamais été exercé en conditions réelles.** Ce chantier est né sous
  l'ancienne procédure : pas de `AE0`, pas de tags, messages « session 1 — étape N » (décision datée
  au journal). `commit-chantier lettre` est testé en unitaire. En revanche, le point 8 du tracker
  (commit E0 et pose du tag) et la séquence de `etape.md` n'ont servi à aucun chantier. Le
  `cloture` réel a été validé sur clone avec zéro tag, jamais avec des tags. Cas limite connexe, non
  couvert : deux chantiers créés avant que l'un pose son `AE0` reçoivent la même lettre. `etape.md`
  point 5 l'arrête bien au tag, mais après le commit.
- La double lecture du frontmatter par regex (`commit_chantier.py` et contrôle 5) est **déjà versée**
  au registre (`frontmatter-suivi-lu-par-regex`). Rien à ajouter.

### Bloquants

Aucun.

## 2026-09-14 — clôture — `dca29d3`

**Verdict** : RÉSERVES

Lus : le brief, le suivi, le plan et le diff `master...git-smart-commit-trois-commits` (25 fichiers,
+1849 −378). Le commit de l'étape 6 (`69e5fcc..dca29d3`) a été lu ligne à ligne. La numérotation
reprend à R11 : les R1 à R10 de l'audit `69e5fcc` restent les étiquettes que cite le suivi.

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → code 0, « Pipeline conforme », contrôles 1 à 9 verts.
- `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests -q` → 23 passés, 0 échec.
- `.venv/bin/python -m pytest scripts/tests skills/list-dir/scripts/tests skills/git-smart-commit/scripts/tests -q`
  → 583 passés. Dans l'ordre inverse des suites, le décompte est aussi de 583, conforme au README
  (113 + 447 + 23).
- `uvx ruff check skills/git-smart-commit` → « All checks passed! », code 0.
- `uvx ruff check scripts skills/list-dir skills/git-smart-commit` → **code 1**, 3 erreurs, toutes
  hors chantier (voir R11).
- `uvx --with pytest basedpyright` sur HEAD → **code 1**, 25 erreurs, 0 ligne contenant
  `git-smart-commit`. Sur `master` extrait par `git archive` (même `.venv`) → 25 erreurs. Le `diff`
  des deux listes, chemins normalisés, est **vide**.
- Vérifications des étapes, telles qu'écrites, sous bash :
  - étape 1 → **code 1**, du seul fait de `basedpyright` ;
  - étapes 2, 3 et 4 → code 0 ;
  - étape 5 → **code 1**, du fait de `ruff` et de `basedpyright` ;
  - étape 6 → code 0.
- `git diff --stat master...git-smart-commit-trois-commits -- .claude/implementation/done` → vide.
- `grep -n "hors-chantier\|etape.md\|aplatissement" skills/git-smart-commit/references/*.md` : aucun
  renvoi d'un fichier de type vers un autre type. Seuls les communs sont cités, et le mot apparaît
  dans la prose.
- `grep -rn "implementation-tracker" skills/git-smart-commit` → 4 lignes : `etape.md:3`,
  `aplatissement.md:3`, `:67` et `:69`. Les deux dernières sont les renvois de R7, toujours présents.
- **Clôture réelle sur un clone jetable** (`git clone --no-local` dans le scratchpad, dépôt audité non
  touché), avec l'audit modifié et non commité :
  - `--dry-run` → code 0, `git status` et HEAD inchangés ;
  - exécution → code 0 ; un commit sur `master`, 4 fichiers en `done/`, `statut: terminé`, champs
    `plan/brief/audit` réécrits, branche supprimée, arbre propre ;
  - `check_pipeline.py` sur le résultat → « Pipeline conforme ».
- Sondes directes sur `remplacer_champ` et `frontmatter` (import du module, rien d'écrit dans le
  dépôt) :
  - un commentaire en fin de ligne `maj:` disparaît à la réécriture ;
  - un frontmatter non fermé est lu comme `{}`.

### Suivi des constats de l'audit `69e5fcc`

- **R2 (relance impossible)** : **levé**.
  - `executer` enchaîne des gestes nommés. Un `ÉCHEC` liste ce qui est fait et ce qui reste, et dit
    si une relance est possible.
  - `finaliser` ne commite plus quand rien n'est indexé.
  - Trois tests couvrent ces cas : échec sur la base, échec puis relance sur la branche, relance
    après une finalisation déjà commitée. `aplatissement.md` point 4 décrit la reprise.
- **R3 (réécriture silencieuse)** : **levé**.
  - Lecture et réécriture partagent désormais la tolérance `clé:` sans espace.
  - Un champ introuvable lève `Echec`, et `statut:` et `maj:` sont exigés au préalable.
  - Un champ absent n'est plus inventé. Test : `test_un_champ_colle_a_ses_deux_points_est_reecrit`.
- **R4 (motif faux dans `cloture.md`)** : **levé**. Le texte dit maintenant que `todo/` est indexé
  dès le premier commit du script, et que seuls un `REFUS` ou une clôture reportée le laissent
  dehors. C'est exact.
- **R5 (chemins sans test)** : **largement levé**. Des tests couvrent désormais le plan introuvable,
  la base introuvable, le lancement hors de la racine, `maj` absent, l'indexation de `todo/` et le
  chemin `Echec`. Le reliquat est en R15.
- **R6 (`git add done/` entier)** : **levé**. Le chemin archivé est nommé.
- **R1, R7 à R10** : non traités, comme décidé au journal. Ils sont prévus au registre de dette et
  au solde (« Prochaine action » du suivi). **R8 n'est toujours pas écrit** : les deux entrées de
  dette annoncées au journal restent à verser avant l'aplatissement.

### Conformité à l'intention

- Critère « trois parties indépendantes, chacune lue seulement au besoin » : **atteint**, vérifié par
  lecture et par grep. `SKILL.md` n'est qu'un routeur (« lire celui du type demandé, et lui seul »),
  et aucun renvoi ne croise les types.
- Critère « texte commun dans des fichiers séparés et référencés, sans recopie » : **atteint**. Le
  staging, l'accord, la branche et les tags ont chacun un seul lieu de définition. La réserve de
  méthode R9 (aucune commande dédiée) demeure.
- Critère « `check_pipeline.py` sort avec 0 » : **atteint**, vérifié.
- Critère « tests pytest sur dépôt jouet : dry-run, aplatissement, suppression des tags, refus sur
  conflit » : **atteint**, vérifié (23 tests). Le test nominal supprime désormais deux tags réels,
  `AE0` et `AE1`.
- Critère « `ruff` et `basedpyright` passent sur le nouveau script » : **atteint**, vérifié.
  - ruff sort en 0 sur `skills/git-smart-commit` ;
  - basedpyright ne relève aucune erreur sous ce chemin ;
  - le total est identique à `master`, erreur par erreur.
- Hors-périmètre (`done/`) : **respecté**, le diff est vide.
- Signaux de dérive :
  - *modification hors du système de commit* : non matérialisé. L'étape 6 ne touche que le script,
    ses tests, le README des tests, `aplatissement.md` et `cloture.md`.
  - *jugement dans le script* : non matérialisé. La nouvelle logique de reprise est mécanique : elle
    choisit un libellé selon le rang du geste en échec, et ne défait ni ne tranche rien.
  - *texte recopié* : non matérialisé.
- Symptôme d'origine : **disparu**. `SKILL.md` ne mêle plus workflow et aplatissement, et `squash.md`
  est supprimé.

### Qualité du code

- **R11** — (suite de R1) **Les vérifications des étapes 1 et 5 sortent toujours en code 1** telles
  qu'écrites. Les causes :
  - 25 erreurs `basedpyright` et 3 erreurs `ruff`, dans `scripts/tests` et `skills/list-dir` ;
  - des listes d'erreurs identiques à celles de `master` extrait.

  Ce n'est pas une régression, et la corriger sortirait du périmètre. *Pourquoi RÉSERVES et pas
  DÉFAVORABLE* : le critère du brief vise « le nouveau script », et il est tenu. L'utilisateur doit
  savoir que ces deux commandes ne peuvent pas passer à la lettre tant que cette dette de typage
  reste ouverte.
- **R12** — **`aplatissement.md` § Ce que fait le script ne suit plus le script de l'étape 6.**
  - La liste des refus (l. 42-48) omet `statut:` et `maj:`, désormais exigés
    (`commit_chantier.py:196`), et la base introuvable (`:202`).
  - Le point 1 (l. 52-53) annonce un commit de finalisation inconditionnel, alors qu'il est sauté
    quand rien n'est indexé (`:296`).

  Coût : un agent qui reçoit `REFUS : champ « maj: » absent` ne trouve pas ce refus dans la procédure
  qu'il suit.
- **R13** — `commit_chantier.py:112` : **un frontmatter non fermé est lu comme `{}`**, et le refus
  qui en sort dit `champ « base: » absent du frontmatter`. Le résultat est sûr, puisque rien n'est
  écrit, mais le message désigne le mauvais défaut : le champ est bien là, c'est la clôture `---`
  qui manque. Par ricochet, la branche `frontmatter non fermé` de `remplacer_champ` (`:125-126`)
  est inatteignable depuis la CLI.
- **R14** — `commit_chantier.py:128` : la réécriture remplace **la ligne entière**. Un commentaire
  `  # …` en fin de ligne disparaît donc, alors que le lecteur le tolère. Le gabarit en porte un sur
  `audit:` (`gabarit-suivi.md:31`), qui sera perdu dans l'archive. C'est sans conséquence
  fonctionnelle : l'archive n'est plus éditée, et le garde-fou lit la valeur. C'est signalé parce que
  la docstring affirme « le reste du fichier n'est pas touché ».
- **R15** — Des chemins de reprise restent **sans test** :
  - l'échec au rang 1 (`git checkout <base>` refusé), le seul autre rang annoncé « relançable » ;
  - l'échec au milieu d'`archiver`, avec des `git mv` partiels, où la sortie dit « le premier a pu
    être entamé ».

  Aucun critère ne les exige. C'est pourtant sur ces rangs que le conseil « relancer / finir à la
  main » engage l'utilisateur.

Style : conforme aux fichiers voisins. Il reprend les docstrings à paragraphes en capitales, les
commentaires en « pourquoi », les `_ =` sur les retours ignorés (exigés par le mode `all`) et les
tests en sous-processus sans `conftest.py`.

### Dette induite

- **R16** — `commit_chantier.py:351` : **`rang <= 1` code en dur la position de `git checkout` dans
  `gestes()`.** Un geste inséré avant le changement de branche ferait annoncer « relancée telle
  quelle » alors qu'on est déjà sur la base, ou l'inverse. Rien ne relie les deux endroits. Coût
  futur : le conseil de reprise, justement ce que R2 voulait rendre fiable, deviendrait faux en
  silence. Une marque portée par le geste lui-même (« quitte `<slug>` ») supprimerait ce couplage.
- **R7, R8, R9, R10** : inchangés depuis l'audit `69e5fcc`, et prévus au registre et au solde par la
  « Prochaine action » du suivi. R8 est un préalable de la clôture : c'est la seule trace écrite de
  deux dettes déjà identifiées.

### Bloquants

Aucun.

## 2026-09-15 — clôture — `138b35f`

**Verdict** : RÉSERVES

Lus : le brief, le suivi, le plan et le diff `master...git-smart-commit-trois-commits` (25 fichiers,
+2049 −378). Le commit de l'étape 7 (`dca29d3..138b35f`) a été lu ligne à ligne. La numérotation
reprend à R17 : les R1 à R16 des audits précédents restent les étiquettes que cite le suivi.

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → code 0, « Pipeline conforme », contrôles 1 à 9 verts.
- `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests -q` → 25 passés, 0 échec.
- `.venv/bin/python -m pytest scripts/tests skills/list-dir/scripts/tests skills/git-smart-commit/scripts/tests -q`
  → 585 passés. Dans l'ordre inverse des suites, le décompte est aussi de 585, conforme au suivi et
  au README.
- `uvx ruff check skills/git-smart-commit` → « All checks passed! », code 0.
- `uvx ruff check scripts skills/list-dir skills/git-smart-commit` → **code 1**, 3 E501, hors chantier
  (déjà au registre : `trois-lignes-au-dela-de-100-colonnes`).
- `uvx --with pytest basedpyright` sur HEAD → **code 1**, 25 erreurs, 0 ligne contenant
  `git-smart-commit`. Sur `master` extrait par `git archive` → 25 erreurs. Le `diff` des deux listes,
  chemins normalisés, est **vide**.
- Vérifications des étapes, telles qu'écrites, sous bash :
  - étape 1 → **code 1**, du seul fait de `basedpyright` ;
  - étapes 2, 3 et 4 → code 0 ;
  - étape 5 → **code 1**, du fait de `ruff` et de `basedpyright` ;
  - étapes 6 et 7 (même commande) → code 0.
- `git diff --stat master...git-smart-commit-trois-commits -- .claude/implementation/done` → vide.
- `grep -rn "implementation-tracker" skills/git-smart-commit` → 4 lignes : `etape.md:3`,
  `aplatissement.md:3`, `:69` et `:71`. Les deux dernières sont les renvois de R7.
- `grep -n "hors-chantier\|etape.md\|aplatissement" skills/git-smart-commit/references/*.md` : aucun
  renvoi d'un fichier de type vers un autre type.
- `git tag -l` → `AE7`, sur `138b35f`. Aucun `AE0`.
- Sondes directes sur `frontmatter` et `remplacer_champ` (import du module, rien d'écrit) :
  - le commentaire de fin de ligne est conservé, avec une espace comme avec une tabulation ;
  - `maj:2026-01-02` est bien réécrit ;
  - une valeur contenant ` #` est tronquée à la lecture, ce qui donne un refus sûr (plan introuvable).
- **Contrôle 5 sur une archive commentée** (`check_archives` appelé par import, sur un arbre HEAD
  extrait dans le scratchpad) :
  - archive `2026-08-14-audit-integre.md` telle quelle → `OK 22 archives` ;
  - même archive, avec le commentaire du gabarit ajouté sur `audit:` → `KO … audit: pointe dans le
    vide (… .audit.md   # créé au premier audit, cf. references/audit.md)`. Voir R17.
- Clôture réelle sur un clone jetable → **NON EXÉCUTÉE** : `git clone` et la clôture ont été refusés
  par le classifieur de permissions de la session. Le chemin nominal reste couvert par
  `test_cloture_aplatit_archive_et_nettoie` (vert), et les audits `69e5fcc` et `dca29d3` l'avaient
  exécuté sur clone. En revanche, la clôture avec un tag réel de ce dépôt (`AE7`) n'a pas été rejouée.

### Suivi des constats de l'audit `dca29d3`

- **R12 (`aplatissement.md` en retard sur le script)** : **levé** pour ce qu'il visait :
  - `statut:`, `maj:`, la base introuvable et le frontmatter non fermé sont listés ;
  - le commit de finalisation est dit conditionnel.

  Un reliquat mineur est en R19.
- **R13 (frontmatter non fermé lu comme `{}`)** : **levé**. Deux refus distincts nomment le défaut, et
  `test_refus_nomme_un_frontmatter_non_ferme` le couvre. La branche `frontmatter non fermé` de
  `remplacer_champ` (`commit_chantier.py:128-129`) reste inatteignable depuis la CLI, comme déjà dit.
  Elle ne coûte rien.
- **R14 (commentaire perdu à la réécriture)** : **levé**, mais le correctif **induit R17**.
- **R11 (vérifs des étapes 1 et 5 en code 1)** : inchangé, et toujours identique à `master` erreur par
  erreur.
- **R7 à R10, R15, R16** : inchangés, prévus au registre et au solde. **R8 n'est toujours pas écrit** :
  le registre ne porte aucune entrée sur le staging sorti du contrat, ni sur l'abandon « garder la
  branche ».

### Conformité à l'intention

- Critère « trois parties indépendantes, chacune lue seulement au besoin » : **atteint**, vérifié par
  lecture et par grep. L'étape 7 ne touche pas à la structure.
- Critère « texte commun dans des fichiers séparés et référencés, sans recopie » : **atteint**. La
  réserve de méthode R9 demeure.
- Critère « `check_pipeline.py` sort avec 0 » : **atteint**, vérifié sur HEAD. R17 montre qu'il
  virera au rouge à la clôture d'un suivi qui porte le commentaire du gabarit. Ce n'est pas le cas de
  ce chantier.
- Critère « tests pytest sur dépôt jouet : dry-run, aplatissement, suppression des tags, refus sur
  conflit » : **atteint**, vérifié (25 tests).
- Critère « `ruff` et `basedpyright` passent sur le nouveau script » : **atteint**, vérifié. ruff sort
  en 0 sous `skills/git-smart-commit`, et basedpyright n'y relève aucune erreur, à total identique à
  `master`.
- Hors-périmètre (`done/`) : **respecté**, le diff est vide.
- Signaux de dérive :
  - *modification hors du système de commit* : non matérialisé. L'étape 7 touche le script, ses
    tests, `aplatissement.md`, le README des tests et un addendum au plan.
  - *jugement dans le script* : non matérialisé. Les deux refus ajoutés et la conservation du
    commentaire sont mécaniques.
  - *texte recopié* : non matérialisé.
- Symptôme d'origine : **disparu**. `SKILL.md` n'est qu'un routeur, et `squash.md` est supprimé.

### Qualité du code

- **R17** — `commit_chantier.py:131-136` : **le correctif de R14 fait échouer le contrôle 5 du
  garde-fou sur l'archive d'un suivi conforme au gabarit.** Le mécanisme :
  - `gabarit-suivi.md:31` porte un commentaire en fin de ligne `audit:` ;
  - la réécriture le conserve désormais derrière le chemin `done/…` ;
  - le contrôle 5 (`check_pipeline.py:408`, `^audit: *(\S.*)$`) ne retire pas les commentaires, et
    lit donc le commentaire comme une partie du chemin.

  Le résultat est `pointe dans le vide`, puis `check_pipeline` sort en code 1 juste après une clôture
  pourtant réussie. Ce comportement est **établi par l'exécution** (voir plus haut). Avant l'étape 7,
  le commentaire disparaissait et le garde-fou restait vert : c'est donc une régression de
  l'interaction entre le script et le garde-fou, introduite par ce commit.

  Trois points aggravent le constat :
  - le test ajouté ne vérifie la conservation que sur `maj:`, jamais sur un champ de chemin, et ne
    lance pas le garde-fou ;
  - la docstring de `frontmatter` affirme que « le garde-fou du dépôt le lit déjà de cette façon »,
    ce qui est faux sur ce point précis ;
  - la dette `frontmatter-suivi-lu-par-regex` décrit bien la divergence des deux motifs, mais annonce
    un risque de garde-fou « resté vert », pas celui d'un garde-fou rouge après chaque clôture
    commentée.

  Exposition actuelle : nulle. Aucune des 22 archives ni le suivi de ce chantier ne portent de
  commentaire. Le risque est latent, pour le premier chantier dont le suivi garde les commentaires
  du gabarit.

  *Pourquoi RÉSERVES et pas DÉFAVORABLE* :
  - aucun critère n'est manqué sur ce chantier ;
  - la clôture elle-même aboutit ;
  - l'échec est bruyant (garde-fou rouge), pas silencieux.

  L'utilisateur doit toutefois le trancher avant d'aplatir. Les options :
  - le corriger ici : réécrire sans commentaire les champs de chemin, ou aligner le contrôle 5 ;
  - le verser explicitement dans la dette `frontmatter-suivi-lu-par-regex`, en y corrigeant le mode
    de défaillance décrit.
- **R18** — **Le suivi n'est plus à jour avec HEAD.** Trois écarts :
  - « Prochaine action » 1 dit le commit de l'étape 7 « pas encore fait », avec le message prévu
    `… session 1 — étape 7 : …`. Or `138b35f` est ce commit, sous le format de type 2
    (`<slug>: E7 — …`), et porte le tag `AE7`.
  - Ni ce changement de format ni la pose d'un tag ne sont datés au journal. La décision « `lettre: A`
    sans tags rétroactifs » ne l'interdit pas, mais `AE7` est isolé : aucune plage `AE<n>..AE7` n'est
    possible, et aucune clôture n'a encore été testée sur un dépôt qui porte des tags réels.
  - « Dernier audit » et la liste de dette de la prochaine action (qui omet R17) sont à mettre à jour
    avant la clôture.

  C'est aussi le premier usage réel partiel du type 2, ce qui entame R10 : message et tag ont servi,
  E0 et `lettre` jamais.
- **R19** — `aplatissement.md:40-49` : quelques refus du script **restent absents de la liste** :
  - suivi introuvable (`commit_chantier.py:202`) ;
  - `lettre:` qui n'est pas une lettre de A à Z (`:209`) ;
  - fichier de message introuvable (`:178`) ;
  - hors d'un dépôt git (`:192`).

  C'est mineur : chaque message du script est explicite. Mais la section se présente comme la liste
  des refus.

Style : conforme aux fichiers voisins. On y retrouve le commentaire en capitales qui dit « pourquoi »
(« Nommer CE défaut »), les refus en français avec guillemets, et des tests en sous-processus
nommés comme les autres. Rien d'autre à signaler.

### Dette induite

- R17 relève de la dette `frontmatter-suivi-lu-par-regex`. Il la rend concrète et en change le mode
  de défaillance : un garde-fou rouge, et non plus un garde-fou resté vert.
- **R7, R8, R9, R10, R15, R16** : inchangés. R8 reste un préalable de la clôture, puisque les deux
  dettes annoncées au journal ne sont écrites nulle part.
- Rien d'autre à signaler pour l'étape 7 : ni duplication, ni abstraction nouvelle, ni couplage
  ajouté.

### Bloquants

Aucun.

## 2026-09-15 — clôture — `9513ccd`

**Verdict** : RÉSERVES

Lus : le brief, le suivi, le plan et le diff `master...git-smart-commit-trois-commits` (26 fichiers,
+2243 −379). Le commit de l'étape 8 (`138b35f..9513ccd`) a été lu ligne à ligne. La numérotation
reprend à R20 : les R1 à R19 des audits précédents restent les étiquettes que cite le suivi.

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → code 0, « Pipeline conforme », contrôles 1 à 9 verts
  (contrôle 5 : 22 archives, tous les champs résolvent).
- `.venv/bin/python -m pytest scripts/tests skills/list-dir/scripts/tests skills/git-smart-commit/scripts/tests -q`
  → **587 passés**, code 0, conforme au suivi et au README (114 + 447 + 26).
- Vérif de l'étape 8, telle qu'écrite, sous bash → **code 0** (140 passés, ruff « All checks
  passed! », garde-fou vert, grep basedpyright vide). Elle englobe les commandes des étapes 6 et 7.
- Vérifs des étapes 2, 3 et 4, telles qu'écrites, sous bash → code 0 chacune.
- `uvx ruff check skills/git-smart-commit scripts/check_pipeline.py scripts/tests` → code 0.
- `uvx ruff check scripts skills/list-dir skills/git-smart-commit` → « Found 3 errors », les 3 E501
  de `skills/list-dir/scripts/tests`, déjà au registre.
- `uvx --with pytest basedpyright` sur HEAD → **code 1**, 25 erreurs. `grep 'git-smart-commit\|check_pipeline\|test_controles_4_5'`
  sur sa sortie → vide. Sur `master` extrait par `git archive` → 25 erreurs. Le `diff` des deux listes,
  chemins normalisés, est **vide**. Les vérifs des étapes 1 et 5 sortent donc toujours en code 1,
  du seul fait de ces erreurs héritées (R11).
- `git diff --stat master...git-smart-commit-trois-commits -- .claude/implementation/done` → vide.
- `grep -rn "implementation-tracker" skills/git-smart-commit` → 4 lignes : `etape.md:3`,
  `aplatissement.md:3`, `:71` et `:73`. Les deux dernières sont les renvois de R7.
- `grep -n "hors-chantier\|etape.md\|aplatissement" skills/git-smart-commit/references/*.md` : aucun
  renvoi d'un fichier de type vers un autre type.
- `git tag -l` → `AE7` sur `138b35f`, `AE8` sur `9513ccd`. Aucun `AE0`.
- **Sonde des deux lecteurs** (script du scratchpad, motifs recopiés de `commit_chantier.py:109` et
  `check_pipeline.py:410`, rien d'écrit dans le dépôt). Sur six lignes `audit:` (commentaire après
  espaces, après tabulation, `#` collé dans le chemin, valeur réduite à un commentaire, clé sans
  espace, ligne nue), les deux lecteurs rendent **la même valeur dans les six cas**.
- **Clôture réelle sur un clone jetable** → **NON EXÉCUTÉE** : `git clone --no-local` a été refusé
  par le classifieur de permissions de la session, comme au troisième audit. Le chemin nominal
  reste couvert par `test_cloture_aplatit_archive_et_nettoie` (vert, suppression de `AE0` et `AE1`
  sur le dépôt jouet). En revanche, la clôture de ce dépôt, avec ses tags réels `AE7` et `AE8`, n'a
  jamais été rejouée, et le garde-fou n'a pas été lancé sur une archive produite par le script.

### Suivi des constats de l'audit `138b35f`

- **R17 (commentaire conservé, contrôle 5 rouge)** : **levé**.
  - Le contrôle 5 retire le commentaire de fin de ligne avec le même motif de fin que le lecteur du
    script. La sonde ci-dessus établit que les deux lecteurs concordent.
  - Chaque côté a son test : `test_commentaire_de_fin_de_ligne_ignore` pour le garde-fou, et
    `test_un_chemin_commente_est_reecrit_sans_perdre_son_commentaire` pour la réécriture d'un champ
    de chemin.
  - La dette `frontmatter-suivi-lu-par-regex` décrit maintenant les deux modes de défaillance
    (garde-fou vert à tort, ou rouge à tort) et cite R17.
  - Reliquat : l'alignement reste manuel, et aucun test n'enchaîne la clôture et le garde-fou. C'est
    exactement ce que porte la dette mise à jour. Rien à ajouter.
- **R19 (refus absents de la liste)** : **levé**. `aplatissement.md` liste maintenant le dépôt git
  absent, le suivi introuvable, la lettre invalide et le fichier de message introuvable. Seuls
  manquent les échecs de git lui-même (`git tag --list`, `git status`, `merge-tree` hors conflit).
  Ce sont des pannes d'outil, pas des règles de clôture, et leur message est explicite.
- **R18 (suivi en retard sur HEAD)** : **reproduit** sur ce commit, voir R20.
- **R11** : inchangé, et toujours identique à `master` erreur par erreur.
- **R7 à R10, R15, R16** : inchangés, prévus au registre et au solde par la « Prochaine action » du
  suivi. `cloture.md` place le registre (§ 2) après l'audit (§ 1) : que R8 ne soit pas encore écrit
  est donc dans l'ordre. Il reste un préalable de l'aplatissement.

### Conformité à l'intention

- Critère « trois parties indépendantes, chacune lue seulement au besoin » : **atteint**, vérifié par
  lecture et par grep. L'étape 8 ne touche pas à la structure.
- Critère « texte commun dans des fichiers séparés et référencés, sans recopie » : **atteint**. La
  réserve de méthode R9 (aucune commande dédiée) demeure.
- Critère « `scripts/check_pipeline.py` sort avec le code 0 » : **atteint**, vérifié. Le risque R17
  d'un garde-fou rouge après la clôture d'un suivi commenté est levé.
- Critère « tests pytest sur dépôt jouet : dry-run, aplatissement, suppression des tags, refus sur
  conflit » : **atteint**, vérifié (26 tests dans la suite du script).
- Critère « `uvx ruff check` et `uvx --with pytest basedpyright` passent sur le nouveau script » :
  **atteint**, vérifié. ruff sort en 0 sous `skills/git-smart-commit`. basedpyright n'y relève aucune
  erreur, ni dans `check_pipeline.py` et `test_controles_4_5.py` touchés par l'étape 8, et le total
  est identique à `master`.
- Hors-périmètre (`done/`) : **respecté**, le diff est vide. Les 22 archives sont intactes et le
  contrôle 5 les lit toutes.
- Signaux de dérive :
  - *modification hors du système de commit* : non matérialisé. L'étape 8 touche `check_pipeline.py`,
    mais uniquement le contrôle 5, qui lit les archives que produit le script de clôture. C'est la
    correction d'une interaction introduite par ce chantier, et elle est datée au journal.
  - *jugement dans le script* : non matérialisé. Le script n'est pas modifié par l'étape 8.
  - *texte recopié* : non matérialisé. Le commentaire du contrôle 5 renvoie au script au lieu de
    redéfinir la règle.
- Symptôme d'origine : **disparu**. `SKILL.md` n'est qu'un routeur, et `squash.md` est supprimé.

### Qualité du code

- **R20** — **Le suivi commité dans `9513ccd` annonce ce même commit comme restant à faire.**
  - « Prochaine action » 1 : « Commit de l'étape 8 (R17 et R19 corrigés, vérifiés, non commités) »,
    alors que `9513ccd` est ce commit et porte `AE8`.
  - « Dernier audit » donne encore `138b35f`, et le journal ne date ni ce commit ni la pose d'`AE8`,
    alors que R18 avait déjà signalé ce même écart pour `AE7`.

  Le mécanisme est structurel : le suivi est mis à jour puis commité dans l'étape qu'il décrit. Un
  commit d'étape type 2 le laissera donc toujours en retard d'un commit, sauf si sa « Prochaine
  action » est écrite au futur accompli. Coût immédiat : le commit de finalisation du script archive
  le suivi tel quel. S'il n'est pas corrigé avant la clôture (§ 2 et § 3), l'archive gardera une
  prochaine action fausse et un dernier audit périmé.
- Style de l'étape 8 : conforme aux fichiers voisins. Le commentaire du contrôle 5 dit « pourquoi »,
  comme ceux du fichier. Le nouveau test du garde-fou a une docstring d'une ligne, comme
  `test_frontmatter_sans_champ`, et le test du script réutilise `SUIVI_TEXTE`, `lancer` et `message`.
  Rien d'autre à signaler.

### Dette induite

- L'étape 8 n'introduit ni duplication, ni abstraction, ni couplage nouveau. Elle rend explicite un
  couplage qui existait déjà (deux motifs alignés à la main), et la dette `frontmatter-suivi-lu-par-regex`
  le porte désormais avec son vrai mode de défaillance.
- **R7, R8, R9, R10, R15, R16** : inchangés. La liste de dette de la « Prochaine action » les couvre
  tous. R10 progresse un peu : deux commits type 2 réels (`AE7`, `AE8`), mais toujours ni `AE0` ni
  commande `lettre` en usage réel, et aucune clôture rejouée avec des tags réels (voir la vérification
  NON EXÉCUTÉE).

### Bloquants

Aucun.
