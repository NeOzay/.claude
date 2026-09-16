---
slug: fichier-seme
---

## 2026-09-15 — clôture — `fadddf1`

**Verdict** : RÉSERVES

Les deux critères de réussite sont atteints et vérifiés par exécution. Le hors-périmètre est respecté,
avec un seul élargissement, celui du type `int`, daté dans le suivi. Aucun signal de dérive ne s'est
matérialisé. Les constats ci-dessous ne bloquent rien, mais l'un d'eux (R1) est un écart observable
au « comportement identique » de list-dir : dans le doute, le verdict retenu est le plus sévère.

### Vérifications exécutées

- `.venv/bin/python -m pytest skills/list-dir/scripts/tests -q` → **447 passed** (base : 447)
- `.venv/bin/python -m pytest skills/gabarit/scripts/tests -q` → 50 passed
- `.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q` → 497 passed
- `uvx ruff check skills/list-dir skills/gabarit` → 3 erreurs, toutes des E501 dans les tests de
  list-dir (`test_contract.py`, `test_fusion.py` ×2). Sur un arbre extrait de `master`, le résultat
  est identique : 3 erreurs. `skills/gabarit` n'en a aucune.
- `uvx --with pytest basedpyright`, lancé depuis `skills/list-dir` → 13 erreurs. La liste triée est
  **identique, ligne à ligne,** à celle de `master` (arbre extrait par `git archive`) : aucune
  régression.
- `uvx --with pytest basedpyright`, lancé depuis `skills/gabarit` → 0 erreur, 0 avertissement
- `.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. », rc 0
- `.venv/bin/python scripts/sante_skills.py` → rc 0
- `command -v gabarit` → `/home/debian/.claude/bin/gabarit`
- garde de dérive `! grep -rnE '^\s*(from|import)\s+listdir' skills/gabarit/scripts` → aucune
  occurrence, rc 0
- `git diff master...fichier-seme -- skills/list-dir/scripts/tests` → 0 ligne : les tests de list-dir
  sont intacts, imports compris.
- documentation de list-dir modifiée → seul `skills/list-dir/references/format.md` a changé
  (élargissement `int`).
- autres skills touchés (`git diff --name-only -- skills` hors `list-dir`/`gabarit`) → aucun
- étape 10, bloc du plan (`gabarit new suivi` puis `check`, assertion tomllib `gabarit=="suivi"` et
  `session` de type `int` égal à 1, puis `check --filled` qui sort en 1 sur « à remplir ») → rc 0.
- étape 11 : `grep -n 'gabarit' OUTILLAGE.md` → 2 lignes ; `! grep -n 'deux commandes'` → rc 0.
- Contrôles complémentaires, faits par l'auditeur :
  - `gabarit new` dans un répertoire inexistant → créé, rc 0 ;
  - fichier existant → refus nommé, rc 1 ;
  - `--from .` → estampille `suivi`, le nom du répertoire ;
  - estampille non chaîne, absente, ou inconnue → échec nommé, rc 1 ;
  - `check --def suivi` sur un fichier non estampillé → 13 manquements, rc 1 ;
  - `contract suivi --values statut` → 4 valeurs, rc 0 ;
  - `--values slug` → échec nommé, rc 1 ;
  - `defs` → `suivi rang 4 config:gabarit`.
- `int` côté list-dir :
  - un contrat `int` avec `text = "42"` → `list-dir new` pose `n = 42`, et `validate` conclut
    « conforme » ;
  - `text = "4.2"` → refus nommé, rc 1.
- Amorce de `listdir` : une copie de `scripts/` hors du dépôt, importée avec `PATH=/usr/bin:/bin`,
  lève `ImportError: listdir exige le paquet gabarit : aucun bin/gabarit…`, un échec fermé et nommé.

### Conformité à l'intention

- **Critère « la suite de tests de list-dir passe ; seuls ses imports sont modifiables »** : atteint et
  vérifié. 447 tests passent, et le diff des tests est vide : aucun import n'a même eu besoin de
  changer.
- **Critère « une vraie semence de suivi du tracker est livrée »** : atteint et vérifié.
  - `skills/gabarit/gabarit/suivi/contract.toml` reprend les 14 champs de
    `implementation-tracker/references/contrat.md#frontmatter`, avec les valeurs d'enum exactes de
    `statut` et d'`execution`.
  - `audit`, `brief` et `road-map` y sont facultatifs, comme dans le contrat du tracker.
  - Il porte aussi les quatre sections de `gabarit-suivi.md`.
  - `new` puis `check` passent réellement sur cette semence.
- **Hors-périmètre**
  - « pas de modification des skills existants » : respecté. Seul list-dir est touché, et sa
    modification est prévue par les contraintes du brief. `OUTILLAGE.md` n'est pas un skill.
  - « list-dir : comportement et documentation identiques » : respecté, à deux réserves près.
    L'élargissement `int` est légitime, puisqu'il est daté dans le suivi et que le suivi fait foi.
    L'écart R1 reste mineur.
  - « tracker non branché » : respecté. Aucun fichier sous `skills/implementation-tracker/` n'est
    modifié.
- **Signaux de dérive**
  - Test de list-dir modifié : non, aucune ligne.
  - `gabarit` qui importe `listdir` : non, la garde est vérifiée.
  - `gabarit` qui gère une notion de liste ou de répertoire : non matérialisé dans le code. Les quatre
    racines de résolution sont exigées par le brief. Il reste des traces de vocabulaire de liste dans
    les docstrings et une propriété héritée (voir « Dette induite »).
- **Symptôme d'origine** : « non abordé » dans le brief. Le but, créer un fichier préstructuré depuis
  une semence hors de toute liste, est observable : `gabarit new suivi <fichier>` le fait.
- **Contraintes connues** :
  - estampille `gabarit = "<nom>"`, de type slug et sans version ;
  - front matter `+++` seul ;
  - semences sous `gabarit/<nom>/` ;
  - `reseed` resté dans list-dir ;
  - `LISTDIR_*` injectés par l'appelant.

  Toutes sont respectées, et constatées dans le code.

### Qualité du code

- **R1** — `skills/list-dir/scripts/listdir/types.py` — `ListError` n'est plus une classe propre, mais
  l'alias `ListError = GabaritError`.
  - `except ListError` fonctionne toujours.
  - Ce qui change pour tout script consommateur de la bibliothèque list-dir : le nom affiché dans une
    trace d'exception, `gabarit.types.GabaritError` au lieu de `listdir.types.ListError`, et le
    `__name__`/`__module__` de la classe.
  - Aucun test ne le couvre, et le suivi ne l'annonce pas. C'est un écart, mineur mais réel, au
    hors-périmètre « comportement identique ». À ratifier ou à corriger, par une sous-classe
    `class ListError(GabaritError)` levée par les résultats de list-dir, si c'est jugé utile.
- **R2** — `skills/gabarit/scripts/gabarit/commandes.py`, `check()`. Quand l'estampille désigne une
  semence introuvable, le message rendu est celui de `resolve` : « semence « nope » introuvable ;
  connues : suivi ». Il ne nomme pas le fichier vérifié, alors que tous les autres échecs de `check`
  commencent par `<fichier>:`. Sur une vérification en boucle de plusieurs suivis, on ne sait pas
  lequel est en cause.
- **R3** — `skills/gabarit/scripts/gabarit-cli.py`. Le refus « nom ou --from, pas les deux » (code 2)
  de `trouver_semence` n'est pas atteignable dans l'ordre `gabarit new suivi --from P x.md`.
  argparse répond « unrecognized arguments: x.md », un message qui ne dit pas la vraie faute. Cela
  reste une erreur d'appel en code 2, donc sans échec ouvert.
- Style : le code est conforme à celui des fichiers voisins (commentaires en majuscules qui portent
  le pourquoi, `Result`, nommage français et anglais mêlés comme dans `listdir`). Les gardes de
  version et de venv de `gabarit-cli.py` sont reprises de `list-dir.py`. Rien d'autre à signaler.

### Dette induite

- **R4** — Des résidus de sémantique de liste dans `gabarit`, un paquet qui déclare « rien ici ne
  connaît de répertoire ni de liste » :
  - `gabarit.types.Item.id`, qui vaut `path.stem`, est la règle d'identité d'une liste, que le
    découpage voulait laisser à `listdir` ;
  - la docstring de `Result`/`ok` cite `items()`, `move()` et `validate` ;
  - celle de `items.py` nomme `init_list` et `provenance.emit` de `listdir`.

  Coût futur : `gabarit` documente son consommateur. Un changement dans `listdir` rendra ces
  commentaires faux sans que rien ne le signale. `Item.id` invite par ailleurs un appelant de
  gabarit à supposer une identité par nom de fichier, ce que `semences.md` récuse explicitement.
- **R5** — La dépendance de list-dir envers `gabarit` n'est écrite ni dans `skills/list-dir/SKILL.md`,
  ni dans ses références. La contrainte « documentation identique » l'interdisait, et elle figure dans
  `OUTILLAGE.md`. Un déploiement de list-dir seul, que son `ruff.toml` présente comme destiné à
  « être déployé ailleurs », échoue désormais à l'import. L'échec est fermé et nommé (vérifié), mais
  la documentation du skill n'annonce pas le prérequis. Ce point est à reprendre au chantier de
  branchement, ou à accepter comme dette.
- Duplication : aucune. Le code déplacé est supprimé de `listdir` et réexporté, pas copié. Les
  imports de réexportation (`X as X`) sont nombreux, mais c'est la règle de conservation du plan,
  pas une dette.

### Bloquants

Aucun.

## 2026-09-15 — clôture — `5123a3d`

**Verdict** : RÉSERVES

Cet audit reprend le chantier en entier sur le nouveau HEAD, après l'étape 12. Les constats R1 à R5
de l'audit précédent gardent leur numéro ; les nouveaux commencent à R6.

Les deux critères de réussite restent atteints, et vérifiés par exécution. R2 et R3 sont levés, ce
qui est constaté à l'exécution et non sur la foi du suivi. R1 est ratifié : c'est un élargissement
daté dans le suivi. Il ne reste rien de bloquant.

Le verdict reste RÉSERVES pour une raison principale : le journal envoie R4 et R5 « vers la dette »,
mais aucune entrée correspondante n'existe (R6). Tant que ce transfert n'est pas écrit quelque part,
ces deux constats ne sont consignés que dans ce rapport.

### Vérifications exécutées

- `.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q` →
  **498 passed**
  - list-dir seul → **447 passed**, comme la base ;
  - gabarit seul → 51 passed. Les 50 de l'audit précédent, plus un test ajouté par E12.
- `uvx ruff check skills/list-dir skills/gabarit` → 3 erreurs, toutes des E501 dans les tests de
  list-dir.
  - Sur l'arbre extrait de `master` (`git archive`), `skills/list-dir` donne aussi 3 erreurs.
  - `uvx ruff check skills/gabarit` → « All checks passed! ».
- `uvx --with pytest basedpyright`, lancé depuis `skills/list-dir` → **13 erreurs**, 0 avertissement.
  - Sur l'arbre extrait de `master`, le premier passage rend 65 erreurs : l'arbre n'a pas de `.venv`,
    or `venvPath` vaut `../..`. Ce chiffre n'est donc pas comparable.
  - Relancé après un lien symbolique vers le `.venv` du dépôt, placé dans le répertoire temporaire,
    il rend **13 erreurs**.
  - Les deux listes triées, chemins normalisés, sont **identiques** (`diff` vide) : aucune régression.
- `uvx --with pytest basedpyright`, lancé depuis `skills/gabarit` → 0 erreur, 0 avertissement, 0 note.
- `.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. », rc 0.
- `.venv/bin/python scripts/sante_skills.py` → rc 0.
- `command -v gabarit` → `/home/debian/.claude/bin/gabarit`.
- Garde de dérive `! grep -rnE '^\s*(from|import)\s+listdir' skills/gabarit/scripts` → rc 0, aucune
  occurrence.
- `git diff master...fichier-seme -- skills/list-dir/scripts/tests | wc -l` → 0.
- Fichiers de documentation list-dir modifiés → `skills/list-dir/references/format.md` seul.
- Skills touchés hors `list-dir`/`gabarit` → aucun.
- Étape 10, bloc exact du plan → rc 0 :
  - `new` rend son fichier ;
  - `check` répond « conforme à la semence « suivi » » ;
  - l'assertion tomllib passe ;
  - `--filled` sort en 1 sur « à remplir ».
- Étape 11 : `grep -n 'gabarit' OUTILLAGE.md` → lignes 22 et 23 ; `! grep -n 'deux commandes'` → rc 0.
- Levée de R2, vérifiée à l'exécution : un fichier estampillé `gabarit = "nope"` donne
  `z.md: estampille « nope » — semence « nope » introuvable ; connues : suivi`, rc 1. Le fichier est
  désormais nommé. Le test `test_une_estampille_qui_ne_se_resout_pas_est_nommee` le couvre.
- Levée de R3 et CLI `new` réécrite en E12, exercées sous bash par l'auditeur :

  | Appel | Résultat | rc |
  |---|---|---|
  | `new suivi --from P c.md` | « pas les deux » | 2 |
  | `new --from P suivi c.md` | « pas les deux » | 2 |
  | `new suivi b.md` | créé, `gabarit = "suivi"` | 0 |
  | `new --from P a.md` | créé, `gabarit = "suivi"` | 0 |
  | `new suivi sub/dir/g.md` | créé | 0 |
  | `new suivi b.md` (existe déjà) | « existe déjà — `gabarit new` n'écrase rien » | 1 |
  | `new a b c` | « trop d'arguments » | 2 |
  | `new` sans argument | « arguments are required » | 2 |
  | `new --from P` sans fichier | « arguments are required » | 2 |
  | `new --bogus suivi d.md` | « unrecognized arguments: --bogus » | 2 |
  | `new suivi -- e.md` | créé | 0 |
  | `new --help` | usage propre à `new` | 0 |
  | `gabarit` sans argument | « Aucune commande. » | 2 |

- Recherche d'une entrée de dette pour R4/R5 : `grep -rln 'fichier-seme\|gabarit' todo .claude/todo`
  → aucun fichier.

### Conformité à l'intention

- **Critère « la suite de tests de list-dir passe ; seuls ses imports sont modifiables »** : atteint et
  vérifié. 447 passed, et le diff des tests est vide.
- **Critère « une vraie semence de suivi du tracker est livrée »** : atteint et vérifié. La semence n'a
  pas bougé depuis `fadddf1`, et le bloc de l'étape 10 passe sur le HEAD.
- **Hors-périmètre**
  - « pas de modification des skills existants » : respecté. Aucun skill n'est touché hors
    `list-dir` et `gabarit`.
  - « list-dir : comportement et documentation identiques » : respecté, sous les deux élargissements
    datés du suivi.
    - Le type `int` : `format.md` est le seul fichier de documentation modifié.
    - L'alias `ListError = GabaritError` (R1) : toujours en place, `listdir/types.py:44`, accepté et
      daté.
  - « tracker non branché » : respecté.
- **Signaux de dérive** : aucun ne s'est matérialisé.
  - Le diff des tests de list-dir est vide.
  - La garde contre les imports de `listdir` passe.
  - E12 n'introduit dans `gabarit` aucune notion de liste ni de répertoire.
- **Symptôme d'origine** : « non abordé » dans le brief. Le but est observable, puisque
  `gabarit new suivi <fichier>` puis `gabarit check <fichier>` fonctionnent de bout en bout.
- **Étape 12** : conforme à ce qu'annonce le suivi.
  - R2 : le fichier est nommé dans l'échec de résolution de l'estampille.
  - R3 : le refus « pas les deux » est atteint dans les trois ordres, avec un test à l'appui.

### Qualité du code

- R2 et R3 sont levés, comme vérifié plus haut.
- **R7** — `skills/gabarit/scripts/gabarit-cli.py`, `main`. La correction de R3 fait passer `new` par
  un second parseur autonome, choisi par `argv[0] == "new"`.
  - Le raisonnement est écrit : `parse_intermixed_args` ne supporte pas les sous-parseurs.
    `_options_new` évite de dupliquer les arguments.
  - Mais la chaîne `usage=` de ce parseur est écrite à la main
    (`gabarit new <nom> <fichier> | --from <chemin> <fichier>`), et le texte d'aide du sous-parseur
    (« crée un fichier prérempli… ») n'apparaît pas dans `gabarit new --help`.
  - Coût : ajouter une option à `new` impose de retoucher cet usage à la main, sinon l'aide ment sans
    que rien n'échoue. Aucun test ne compare les deux.
  - Défaut mineur, sans échec ouvert : toute erreur d'appel sort en code 2, ce qui est vérifié.
- Style : les commentaires d'E12 portent le pourquoi, en majuscules, comme dans les fichiers voisins,
  et les tests suivent le nommage descriptif de `test_new.py`. Rien d'autre à signaler.

### Dette induite

- **R6** — Le journal de décisions du suivi dit « R4 et R5 vers la dette », mais cette dette n'est
  écrite nulle part. `grep` ne trouve aucune mention de `fichier-seme` ni de `gabarit` sous `todo/` ou
  `.claude/todo/`.
  - Les résidus de R4 sont toujours présents :
    - `gabarit/types.py:39`, docstring qui cite `items()` et `move()` ;
    - `gabarit/types.py:197`, `Item.id` ;
    - `gabarit/items.py:22` et `:231`, qui citent `init_list` et `provenance.emit`.
  - R5 est inchangé : ni `skills/list-dir/SKILL.md` ni ses références ne nomment la dépendance envers
    `gabarit`.
  - Coût : à la clôture, ces deux constats ne survivent que dans ce rapport d'audit. Personne ne les
    retrouvera en consultant les registres de dette.
  - Le brief n'exige pas cette inscription : c'est une réserve, pas un bloquant. Mais le suivi annonce
    un transfert qui n'a pas eu lieu.
- **R8** — Le mot « gabarit » est déjà employé dans la documentation de list-dir, par
  exemple dans `references/operations.md:96`, `:133` et `:136`, pour désigner les paires
  `.list/templates/<nom>.{toml,md}` de `derive`. Il nomme désormais aussi le paquet dont list-dir
  dépend.
  - Le nom a été choisi par l'utilisateur, et le brief le donne comme « pressenti ». Ce n'est donc pas
    un défaut du chantier.
  - Coût : le jour où la documentation de list-dir mentionnera sa dépendance, comme R5 le demande,
    le lecteur aura deux « gabarit » qui ne désignent pas la même chose. À garder en tête au chantier
    de branchement.
- Duplication : aucune nouvelle. E12 factorise les arguments de `new` dans `_options_new` plutôt que
  de les copier.

### Bloquants

Aucun.
