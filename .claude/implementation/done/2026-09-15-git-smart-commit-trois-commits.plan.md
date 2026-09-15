# Plan — git-smart-commit-trois-commits

Brief : `.claude/implementation/git-smart-commit-trois-commits.brief.md` (validé).

## Context

`git-smart-commit` date d'avant `implementation-tracker`. Aujourd'hui, son `SKILL.md` (212 l.)
contient le workflow général et ne cite l'aplatissement qu'en fin de fichier, en renvoyant à
`references/squash.md`. Les commits d'étape et de session sont eux décrits côté tracker
(`contrat.md` § Branche et commits, l. 180-199), avec la mention « ne passent pas par
`git-smart-commit` ». L'aplatissement est écrit à la main dans `cloture.md` points 3-4, sous forme
d'un bloc bash de 30 lignes.

On veut trois types de commits, chacun dans un fichier lu seulement au besoin. Le texte commun est
référencé, jamais recopié. Le tracker appelle le skill pour les commits d'étape, et ceux-ci
portent des tags `<L>E<n>` utilisables en plage git. Un script lancé par l'agent fait les
opérations git et fichiers de la clôture.

**Rappel du brief**
- **Critères de réussite :**
  - les trois parties sont indépendantes ;
  - le texte commun n'est pas recopié ;
  - `check_pipeline.py` sort avec 0 ;
  - des tests pytest couvrent le script ;
  - ruff et basedpyright passent.
- **Hors-périmètre :** les chantiers clos (`done/`).
- **Signaux de dérive :**
  - une modification hors du système de commit ;
  - du jugement introduit, dans le script en particulier ;
  - du texte recopié d'un skill à l'autre.
- **Incertitudes à lever :**
  - le moment où la lettre et `AE0` sont posés ;
  - le frontmatter et le nom du champ ;
  - le cas des 26 lettres épuisées.
  Elles sont tranchées ci-dessous.

## Décisions (incertitudes levées)

- **Lettre** : champ `lettre:` du **suivi**, défini dans `contrat.md` § Frontmatter. Elle est
  attribuée à la création, juste après `git checkout -b <slug>`, par `commit-chantier lettre`.
  Cette commande rend la première lettre A–Z pour laquelle aucun tag `<L>E<n>` n'existe.
  **26 lettres prises** → le script refuse, avec la sortie 1 et un message. Il n'y a pas de lettres
  doubles.
- **`<L>E0`** : posé sur le **premier commit de la branche `<slug>`**, qui porte brief, plan et
  suivi. C'est un commit de type 2, ajouté comme point 8 de l'Étape 2 du tracker.
- **Tags** : `<L>E<n>` est posé sur le commit qui clôt l'étape n. Les commits de session n'ont pas
  de tag. Les tags sont supprimés quand la branche l'est : à l'aplatissement par le script, et à
  l'abandon « tout jeter ».
- **Messages de type 2**, prédéterminés :
  - `<slug>: E0 — état initial`
  - `<slug>: session N — <étape en cours>`
  - `<slug>: E<n> — <intitulé de l'étape>`
- **Un script, deux sous-commandes** : `commit-chantier lettre` et `commit-chantier cloture`.
  La lettre passe aussi par un script : le docstring de `impl_list.py` documente que le hook rtk
  ajoute une colonne de taille en fin de ligne, ce qui a déjà cassé un filtre `grep` ancré en `$` écrit en ligne.
- **Dépendance** : `SKILL.md`, le type 1 et les fichiers communs ne citent jamais le tracker. Seuls
  `etape.md` et `aplatissement.md` y renvoient : ils ne se lisent que depuis le tracker. La dette
  `git-smart-commit-illisible-seul` est soldée à la clôture, par `list-dir move` (point 2 de
  `cloture.md`).
- **`contrat.md` § Branche et commits est vidé** (arbitrage Q1 du 2026-09-14) :
  - la règle de branche `<slug>` va dans `references/branche-chantier.md` ;
  - le staging va dans `staging.md` ;
  - « jamais sans accord » va dans `confirmation.md`.

  La section est **supprimée** du contrat, avec sa clé `branche-et-commits` dans `EMPREINTES`
  (`scripts/check_pipeline.py:279`). Chaque renvoi du tracker vers `contrat.md#branche-et-commits`
  (`SKILL.md:204`, `:225`, `:311`) devient une ligne d'appel vers le fichier commun concerné.
  *Pourquoi pas une section réduite à un renvoi* : le contrôle 2 refuse une section sans empreinte,
  et une ligne de renvoi ne porte aucune règle.
- **Commits de l'abandon** (arbitrage Q1) : ils vont dans une section « Abandon » de
  `aplatissement.md`. C'est la fin de branche sans aplatissement : commit sur `<slug>`, commit
  d'archivage sur `base`, suppression de la branche et des tags selon le choix de l'utilisateur.
  `cloture.md` § Abandon garde la décision (raison, dette, sort du travail) et renvoie au skill pour
  les commits.
- **Jugement hors du script** : compacter le journal du suivi, rédiger le message d'aplatissement,
  décider de l'abandon. Le script ne fait que des vérifications mécaniques et les opérations.
- **Non migré, arbitré par l'utilisateur (Q1)** : la règle « déplacer puis écrire la preuve dans un
  second commit » (`dette.md`, `debt-review`, `list-dir/operations.md`).
- **Ce chantier-ci** est créé sous l'ancienne procédure : il n'a ni lettre ni `AE0`. L'étape 3
  ajoute `lettre:` à son suivi pour qu'il puisse être clos par le script. Le script accepte zéro
  tag à supprimer.

## Structure cible de `skills/git-smart-commit/`

```
SKILL.md                         routeur court : type 1 par défaut ; type 2/3 sur appel du tracker
references/hors-chantier.md      type 1 — analyse du diff, message, confirmation, commit (ex-SKILL.md)
references/etape.md              type 2 — commit rapide d'étape/session, E0, pose du tag
references/aplatissement.md      type 3 — préalables, message dans un fichier, dry-run, accord, script ; § Abandon
references/conventional-commits.md   commun 1+3 — format, types, règles 50/72, langue (enrichi)
references/confirmation.md       commun 1+2+3 — accord explicite, présentation, options
references/staging.md            commun 1+2+3 — chemins nommés, jamais -A (règle + mode de défaillance)
references/tags-etape.md         commun 2+3 — lettre, forme <L>E<n>, plages, suppression
references/branche-chantier.md   commun 2+3 — branche <slug> depuis base, aplatie en un commit
scripts/commit_chantier.py       sous-commandes lettre / cloture
scripts/tests/test_commit_chantier.py
bin/commit-chantier -> ../skills/git-smart-commit/scripts/commit_chantier.py
```

`references/squash.md` est supprimé : son contenu passe dans `aplatissement.md` et dans le script.

## Script `commit-chantier cloture <slug> --message <fichier> [--dry-run]`

Il reprend les points 3-4 de `cloture.md`.

**Refus avant toute écriture** (sortie 1, rien touché) :
- l'agent n'est pas à la racine du dépôt, ou la branche courante n'est pas `<slug>` ;
- le suivi est absent, ou il lui manque `base:` ou `lettre:` ;
- `plan:` est introuvable ;
- un fichier modifié ou non suivi n'est pas une annexe du chantier. Sont tolérés : le suivi, le
  brief, l'audit, le plan (chemin tiré de `plan:`) et `.claude/implementation/todo/` (arbitrage Q4) ;
- le fichier de message est absent ou vide, son titre dépasse 50 caractères, ou la ligne 2 n'est
  pas vide ;
- une cible `done/<date>-…` existe déjà ;
- `git merge-tree --write-tree <base> <slug>` signale un conflit (git 2.47.3 ici).

**`--dry-run`** affiche la plage `base..slug`, les déplacements, les champs réécrits, les tags à
supprimer, la branche à supprimer et le message. Il n'écrit rien.

**Exécution**
1. Point 3 :
   - passer le suivi en `statut: terminé` et mettre `maj:` à la date du jour ;
   - `git add` du suivi et de `todo/` ;
   - commit `<slug>: finalisation du suivi`.
2. `git checkout <base>`, puis `git merge --squash <slug>`.
3. Déplacer suivi, brief, audit et plan vers `done/<date>-<slug>[.brief|.audit|.plan].md`, par
   `git mv`, ou `mv` + `git add` en repli. Réécrire `plan/brief/audit` quand la cible existe.
4. `git commit -F <fichier>`, puis `git branch -D <slug>`, puis `git tag -d` sur chaque `<L>E<n>`.
5. Afficher `git log --oneline -3`.

Un échec git après la première écriture arrête le script. Il affiche l'état (`git status`) sans
rien défaire, conformément à la règle actuelle de `cloture.md` : « s'arrêter net ».

Le frontmatter se lit ligne à ligne, avec le motif `^champ: *(\S.*)$`, comme le contrôle 5 de
`check_pipeline.py:409`. Il n'y a ni dépendance ni import d'un autre skill.

## Étapes

- [ ] 1. Script `commit-chantier` et ses tests.
  - Fichiers :
    - `skills/git-smart-commit/scripts/commit_chantier.py` et `scripts/tests/test_commit_chantier.py`,
      dépôt jouet sur `tmp_path` sur le modèle de `skills/list-dir/scripts/tests/test_move.py`,
      fixtures dans le fichier de test et **pas de `conftest.py`** (collision de basename documentée
      dans `scripts/tests/depot_jouet.py`) ;
    - lien `bin/commit-chantier` ;
    - `extraPaths` de `pyrightconfig.json` ;
    - tableau des suites de `scripts/tests/README.md`.
  - Cas testés :
    - `lettre` : A sans tag, B si `AE0` existe, refus si A–Z sont prises ;
    - `cloture --dry-run` : HEAD, branches, tags et `status --porcelain` restent identiques ;
    - clôture nominale : un seul commit sur base, fichiers en `done/`, champs réécrits, branche et
      tags supprimés ;
    - refus sur conflit, cible existante, titre > 50, mauvaise branche, fichier étranger modifié ;
    - clôture qui passe avec un `<slug>.audit.md` non suivi (Q4).
  - vérif : `.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests -q && uvx ruff check skills/git-smart-commit && uvx --with pytest basedpyright`
- [ ] 2. Type 1 et fichiers communs.
  - Fichiers : `SKILL.md` réécrit en routeur, avec sa description frontmatter. Il ne route que vers
    les fichiers déjà créés, et les étapes 3 et 4 ajoutent chacune leur ligne (Q7). S'y ajoutent
    `references/hors-chantier.md`, `conventional-commits.md`, `confirmation.md`, `staging.md` et
    `branche-chantier.md`.
  - Dans le même geste, pour qu'aucune règle ne soit définie deux fois :
    - supprimer `contrat.md` § Branche et commits ;
    - retirer la clé de `EMPREINTES` ;
    - faire pointer les renvois du tracker (`SKILL.md:204`, `:225`, `:311`, `cloture.md:122`) vers
      les fichiers communs ;
    - retirer `git-smart-commit` de la liste d'en-tête de `contrat.md:3`.
  - vérif : `python3 scripts/check_pipeline.py && ! grep -rn "branche-et-commits" skills scripts/check_pipeline.py && ! grep -n "tracker" skills/git-smart-commit/SKILL.md skills/git-smart-commit/references/{hors-chantier,conventional-commits,confirmation,staging,branche-chantier}.md`
- [ ] 3. Type 2 et branchement du tracker sur les commits d'étape.
  - Fichiers dans `git-smart-commit` : `references/etape.md` et `references/tags-etape.md`.
  - Fichiers dans `implementation-tracker` :
    - `SKILL.md` : Étape 2, point 3 (commit du plan reporté au point 8) et nouveau point 8 E0 ;
      Étape 3, commit de session ; Étape 4, ligne « Étape terminée », § Commits de session et
      l. 280 « court-circuité » ;
    - `references/contrat.md` : champ `lettre` dans § Frontmatter ;
    - `references/gabarit-suivi.md` : `lettre: A`.
  - Ajouter aussi `lettre:` au suivi de ce chantier.
  - vérif : `python3 scripts/check_pipeline.py && ! grep -rn "court-circuité\|ne passent pas par" skills/implementation-tracker`
- [ ] 4. Type 3 et renvoi de la clôture vers le script.
  - Fichiers :
    - `references/aplatissement.md` créé, `references/squash.md` supprimé ;
    - `implementation-tracker/references/cloture.md` : points 3-4 remplacés par un renvoi vers
      `aplatissement.md`, en gardant les points 1, 2 et 5. Dans § Abandon, les commits des points 2
      et 4 renvoient à `aplatissement.md` § Abandon ;
    - `implementation-tracker/SKILL.md` : Étape 5.
  - vérif : `python3 scripts/check_pipeline.py && ! grep -rn "merge --squash\|branch -D" skills --include='*.md' | grep -v git-smart-commit/references/aplatissement.md`
- [ ] 5. Vérification d'ensemble.
  - Aucun fichier touché hors du système de commit : lire la liste avec
    `git diff --stat master..` et la confronter au plan.
  - vérif : `python3 scripts/check_pipeline.py && .venv/bin/python -m pytest scripts/tests skills/list-dir/scripts/tests skills/git-smart-commit/scripts/tests -q && uvx ruff check scripts skills/list-dir skills/git-smart-commit && uvx --with pytest basedpyright`

## Vérification

Critères du brief :
- **Indépendance** : chaque fichier de type ne renvoie qu'aux fichiers communs, sans renvoi croisé
  entre les types. À vérifier par `grep -n "hors-chantier\|etape.md\|aplatissement" skills/git-smart-commit/references/*.md`.
- **Pas de recopie** : les motifs distinctifs de chaque fichier commun doivent n'apparaître qu'une
  fois sous `skills/`.
- **Garde-fou** : `check_pipeline.py` sort avec 0.
- **Script** : pytest, ruff et basedpyright passent.
- **Validation en conditions réelles** : ce chantier sera lui-même clos par `commit-chantier cloture`,
  d'abord en `--dry-run`.

---

## Verdict de `plan-reviewer` : NON CONFORME

J'ai corrigé sans arbitrage trois défauts de rédaction :
- **Q2** : ruff est restreint à `scripts skills/list-dir skills/git-smart-commit`. `skills/list-dir`
  compte déjà 3 E501 hors chantier.
- **Q3** : `--include='*.md'` est mis entre guillemets. Sans eux, zsh rendait la vérification de
  l'étape 4 toujours verte.
- **Q9** : la ligne citée est désormais `check_pipeline.py:409`, et le docstring d'`impl_list.py` est
  cité exactement.

**Constats laissés tels quels, à trancher par toi :**
- **Q1 (cause du NON CONFORME)** : le brief dit « toutes les procédures qui concernent les commits »,
  mais trois éléments restent hors du skill.
  - La règle « déplacer puis écrire la preuve dans un second commit » (`dette.md`, `debt-review`,
    `list-dir`) n'est pas migrée, par choix.
  - Les commits de l'abandon (`cloture.md`, Abandon points 2 et 4) ne sont pas mentionnés.
  - Le paragraphe « Jamais de commit… » de `contrat.md` n'est pas mentionné non plus.

  De plus, le brief dit que § Branche et commits « devient un renvoi », alors que le plan y garde du
  texte sur la branche.
- **Q4** : refuser un « arbre sale » bloquerait toute clôture où `<slug>.audit.md` n'est pas suivi
  par git, et ce chantier-ci serait concerné. La liste des fichiers tolérés doit inclure brief,
  audit et plan.
- **Q5, Q10** : aucune étape ne vérifie par commande l'indépendance, l'absence de recopie, ni que le
  point 8 E0 et le champ `lettre` existent bien.
- **Q6** : le routeur « sur appel du tracker » contredit « ne cite jamais le tracker ». Le grep de
  l'étape 2 ne cherche pas le mot « tracker ».
- **Q7** : entre les étapes 2 et 4, `SKILL.md` renvoie vers `etape.md` et `aplatissement.md`, qui
  n'existent pas encore.
- **Q8** : l'étape 1 est lourde pour un tour. Le README demande aussi de vérifier que le décompte
  des tests ne dépend pas de l'ordre des arguments.

**Arbitrages de l'utilisateur, 2026-09-14** :
- **Q4** : sont tolérées les annexes du chantier (suivi, brief, audit, plan, `todo/`).
- **Q1** : les commits de l'abandon et la règle « jamais sans accord » migrent, et la section du
  contrat n'est plus qu'un renvoi. La règle du second commit n'est pas migrée.
- **Plan modifié en conséquence** : § Décisions, structure, refus du script, étapes 1, 2 et 4.
- **Q7** : le routeur grandit à chaque étape.
- **Q6** : le grep de l'étape 2 cherche aussi « tracker ».

**Étapes 2 et 3 redécoupées, 2026-09-14** : l'étape 2 ne sort de `contrat.md` § Branche et commits
que le staging et l'accord, et change l'empreinte en « une étape peut être à cheval ». La
suppression de la section, `branche-chantier.md`, la clé `EMPREINTES` et les renvois du tracker
(`SKILL.md:204`, `:225`, `:311`) passent à l'étape 3, avec `etape.md`. Le renvoi de `cloture.md:122`
passe à l'étape 4. *Pourquoi* : le format des messages de session ne doit à aucun moment rester sans
définition.

**Étapes 6 et 7, ajoutées après les audits de clôture du 2026-09-14** : leur contenu est dans le rapport
`.claude/implementation/git-smart-commit-trois-commits.audit.md`.
- **Étape 6** : constats R2 à R6 de l'audit sur `69e5fcc`.
- **Étape 7** : constats R12 à R14 de l'audit sur `dca29d3`.

Les constats non traités (R1, R7 à R11, R15, R16) sont destinés au registre de dette ou au solde,
à la clôture.

