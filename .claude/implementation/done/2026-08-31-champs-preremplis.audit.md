---
slug: 2026-08-31-champs-preremplis
---

## 2026-08-31 — clôture — `32918ab`

**Verdict** : DÉFAVORABLE

### Vérifications exécutées

- `cd skills/list-dir/scripts && uvx pytest tests -q` → **340 passés, 0 échec** (307 annoncés avant
  chantier, +33)
- `cd skills/list-dir && uvx ruff check scripts` → **All checks passed!**
- `cd skills/list-dir/scripts && uvx pytest tests/test_contract.py -q` → couvert par la suite
  complète ci-dessus
- Bloc « Vérification de bout en bout » du plan, extraits de contrat **recopiés depuis
  `references/contrat-liste.md`** :
  - `list-dir new` avec `command = "date +%F"` → `date = "2026-08-31"` (date du jour), pas de
    marqueur → **conforme**
  - section `text = "…"` → `## Origine` porte le texte → **conforme**
  - `list-dir validate ma-liste --filled` → réclame `title` et `Constat`, **pas** `date` ni
    `Origine` → **conforme**
  - `command = "false"` → `ma-liste: champ « date » — commande « false » a échoué (code 1) :`,
    code 1, `second.md` non créé → **conforme**
- `list-dir migrate` sur un champ et une section ajoutés au contrat après coup → valeurs posées,
  `date` déjà écrite non recalculée ; `LISTDIR_ID`, `LISTDIR_NAME`, `LISTDIR_CONTRACT` corrects
  (`premier-auteur-essai`) → **conforme**
- `LISTDIR_ROOT` → absente hors dépôt (`root=ABSENTE`), présente et absolue dans un dépôt
  (`root=/tmp/…/depot`) → **conforme**
- Refus au chargement du contrat (`list-dir validate`) : `text`+`command` ensemble, `text = ""`,
  `command = ""`, `text` sur un champ `list` → les quatre refusés, le champ nommé → **conforme**
- `list-dir derive` avec `command = "date +%F"` sur un champ sans `from` → **ÉCHEC** :
  `champ « date » — commande « date +%F » : bash introuvable — [Errno 2] No such file or
  directory: PosixPath('/tmp/…/revues')`, code 1, aucune liste engendrée (voir **R1**)
- `cd skills/list-dir && uvx ruff format --check scripts` → **6 fichiers** à reformater, contre
  **4 sur `master`** (vérifié sur une extraction de `master`) — non-critère, mais régression
  (voir **R7**)

### Conformité à l'intention

- Critère « `uvx pytest tests -q` passe » : **atteint**, vérifié — 340 passés.
- Critère « `command = "date +%F"` sur un champ `date` produit la date du jour à `list-dir new` » :
  **atteint**, vérifié de bout en bout.
- Critère « `text` produit ce texte à la place du marqueur, champ comme section » : **atteint**,
  vérifié (champ et section, à `new` et à `migrate`).
- Critère « `migrate` et `derive` posent la même valeur pour un champ absent » : **NON ATTEINT**.
  `text` fonctionne des deux côtés ; `command` fonctionne en `migrate` et **échoue
  systématiquement en `derive`** — voir **R1**. Le test ajouté à `test_derive_merge.py` n'exerce
  que `text`, ce qui explique que la suite reste verte.
- Critère « une `command` qui échoue fait échouer la création, rien n'est écrit, le message nomme
  la commande » : **atteint**, vérifié à `new` et à `migrate` (fichier existant inchangé octet pour
  octet dans le test, et absence de création vérifiée à la main).
- Critère « `text` et `command` sur un même champ refusés par `parse_contract`, en nommant le
  champ » : **atteint**, vérifié — message
  `l/.list/contract.toml: champ « x » — « text » et « command » ne peuvent être déclarés ensemble`.
- Hors-périmètre : **respecté**. Aucun `[fields.*.env]`, aucune définition livrée (`defs`) touchée,
  aucun nouveau `type` ni nouvelle commande — `git diff --stat` ne sort de `listdir/` que pour
  `SKILL.md`, `references/contrat-liste.md`, les tests et les fichiers de suivi.
- Signaux de dérive : **aucun matérialisé**. `text` est strictement littéral (aucune substitution
  dans `prefill.py`) ; l'exécution ne touche que `create`, `_realign` et `_project` ; `prefill.py`
  est un module dédié, documenté en tête comme « le second et dernier appel de processus du
  paquet » ; le diff reste dans le périmètre annoncé.
- Symptôme d'origine : **partiellement disparu**. Le cas porteur — un champ `date` qui vaut la date
  du jour — fonctionne à `new` et à `migrate`. Il reste hors d'atteinte en `derive`.

### Qualité du code

- **R1** *(bloquant)* — `skills/list-dir/scripts/listdir/store.py:494-499` et `prefill.py:60-70` —
  **`command` est inutilisable en `derive`, par construction.** Le `PrefillContext` de `derive` est
  bâti sur `target`, dont `derive` vient de garantir la **non-existence** (`store.py:479-482` :
  « `{target}: existe déjà — derive ne fusionne ni ne met à jour` »). `subprocess.run(...,
  cwd=ctx.list_dir)` sur un répertoire inexistant lève `FileNotFoundError`, attrapé par la branche
  `OSError` de `_run` — donc **tout** champ sans `from` portant `command` échoue, toujours, quel que
  soit le contrat. Corollaire silencieux : `git rev-parse` subit le même sort, si bien que
  `LISTDIR_ROOT` est **toujours absente en `derive`**, y compris au cœur d'un dépôt. La
  documentation écrite à l'étape 4 affirme pourtant l'inverse : « Seuls les champs sans `from` y
  passent par `text`/`command` » (`references/contrat-liste.md`). Reproduit ci-dessus.

- **R2** — `prefill.py:84-89` — **le message d'échec ment sur la cause.** Le commentaire de la
  branche `OSError` pose explicitement la distinction (« C'est `bash` qui manque, pas la
  commande : celle-ci, introuvable, ressort en code 127 ») ; le message, lui, attribue à `bash`
  toute `OSError`, y compris un `cwd` inexistant (R1) ou une permission refusée. Un contrat
  parfaitement valide envoie l'utilisateur chercher un `bash` qui est là. Le test censé couvrir ce
  cas, `test_prefill.py::test_champ_command_binaire_absent`, passe `command="/inexistant/binaire"`
  à `bash -c` : il exerce le **code 127**, pas la branche `OSError`, qui reste non testée sous un
  nom qui laisse croire le contraire.

- **R3** — `store.py:328-334` et `:357-366` — **une valeur préremplie multi-lignes casse la sortie
  de `migrate`.** Le libellé du `Change` interpole désormais la valeur posée
  (`f"ajoutée, {valeur}"`) là où il interpolait un marqueur d'un seul mot. Constaté : une section
  portant `command = "printf 'ligne1\nligne2\n'"` produit `l/a.md: section « Notes » — ajoutée,
  ligne1` puis `ligne2` sur une ligne à part, rompant l'invariant « un changement, une ligne » sur
  lequel se lit et se grep la sortie de `migrate`. Rien ne tronque ni n'aplatit la valeur.

- **R4** — `prefill.py:118` (`check_value`) — **une sortie de commande qui vaut un marqueur passe en
  silence.** `check_value` suspend le contrôle de type sur `is_marker(value)`
  (`contract.py:384-385`) : une commande qui imprime `<À REMPLIR>` sur un champ `date` est acceptée
  et écrite telle quelle. Symétriquement, `initial_section` ne confronte rien : une commande dont
  la sortie est vide pose une section vide, sans marqueur et sans un mot — un chemin d'échec
  silencieux, alors que tout le reste du module est en échec fermé.

- **R5** — `prefill.py:99-123` — **un champ `date` prérempli est écrit comme une chaîne TOML.** La
  sortie de `command` (ou le `text`) reste un `str` ; `dump_value` l'écrit `date = "2026-08-31"`,
  quand une date saisie à la main est un vrai `datetime.date` et sort `date = 2026-08-31`. Les deux
  formes sont acceptées par `check_value`, mais une même liste porte désormais deux graphies du
  même champ selon l'origine de la valeur — sur le cas porteur du chantier, précisément.

- **R6** — `prefill.py:60-70` (`context`) — **plan tenu à la lettre près : `LISTDIR_LIST` n'est pas
  absolue.** Le plan annonce « chemin absolu du répertoire-liste » ; `str(ctx.list_dir)` restitue le
  chemin tel que l'appelant l'a donné. Vérifié : `list-dir new ma-liste …` pose
  `LISTDIR_LIST=ma-liste`. La documentation écrite dit « le chemin du répertoire-liste » — l'exigence
  a été adoucie sans entrée au journal de décisions. `LISTDIR_ROOT`, elle, est bien absolue.

### Dette induite

- **R7** — `store.py:221`, `:277`, `:499` — **`create`, `migrate` et `derive` lancent désormais
  `git` inconditionnellement.** Avant ce chantier, ces trois opérations n'engendraient aucun
  processus (`git` n'apparaissait dans `store.py` qu'en `move`). `prefill_context()` est appelé en
  tête d'opération même quand **aucun** champ ni section du contrat ne porte `text` ou `command` —
  c'est-à-dire pour la quasi-totalité des listes existantes. Le calcul de `root` est paresseusable
  (aucune commande à lancer → aucun `rev-parse`) ; ne pas l'avoir fait fait payer un `fork`/`exec`
  à chaque `new` d'un contrat qui n'utilise pas la fonctionnalité.

- **R8** — `uvx ruff format --check` — **la dette de formatage annoncée s'est aggravée pendant le
  chantier.** Le suivi note « 4 fichiers **avant** le chantier — ce n'est pas un critère » ; il y en
  a 6 sur `32918ab`. Les deux ajoutés sont ceux qu'écrit le chantier :
  `tests/test_prefill.py` (parenthèses superflues autour de `cmd`) et `tests/test_derive_merge.py`
  (chaînage d'appels). L'excuse porte sur l'héritage, pas sur ce qu'on vient d'écrire.

- **R9** — `.claude/implementation/todo/technical-debt/repli-section-marker-jamais-exerce.md` —
  **une fiche de dette soldée de fait, laissée en `todo/`.** Cette fiche pose deux issues, dont
  « **le retirer** et rendre le contrat explicite ». Le chantier a pris la seconde :
  `Contract.section_marker` est supprimé de `types.py` (le suivi le note en « Notes »), et
  `grep -rn section_marker` ne rend plus que des documents. La fiche décrit désormais du code qui
  n'existe plus, sans trace du chantier qui l'a résolue.

### Bloquants

- **R1** — `command` échoue systématiquement en `derive` : le critère de réussite « `migrate` et
  `derive` posent la même valeur pour un champ absent » n'est pas tenu, et la documentation livrée
  affirme le contraire de ce que fait le code.

## 2026-08-31 — clôture — `29e423c`

**Verdict** : RÉSERVES

Deuxième audit de clôture, après le correctif de R1 (`29e423c`). **R1 est levé.** Les huit autres
constats du rapport précédent (`32918ab`) n'ont reçu aucun correctif et sont **repris tels quels** :
ils restent des réserves, plus des bloquants. Trois constats nouveaux, propres au correctif ou
révélés par lui : **R10**, **R11**, **R12**.

### Vérifications exécutées

- `cd skills/list-dir/scripts && uvx pytest tests -q` → **342 passés, 0 échec** (340 sur `32918ab`,
  307 annoncés avant chantier)
- `cd skills/list-dir && uvx ruff check scripts` → **All checks passed!**
- Bloc « Vérification de bout en bout » du plan, extraits de contrat **recopiés depuis
  `references/contrat-liste.md`** :
  - `list-dir new` avec `command = "date +%F"` → `date = "2026-08-31"`, pas de marqueur →
    **conforme**
  - section `text = "Créé automatiquement."` → `## Origine` porte le texte → **conforme**
  - `list-dir validate ma-liste --filled` → réclame `title` et `Constat`, **pas** `date` ni
    `Origine` → **conforme**
  - `command = "false"` → `ma-liste: champ « date » — commande « false » a échoué (code 1) :`,
    code 1, `second.md` non créé → **conforme**
- **Le cas de R1, rejoué** — `list-dir derive src revues --template revue`, champ sans `from`
  portant `command`, dans un dépôt git → **succès**, `verdict = "id=premier list=revues
  contract=revue root=/…/depot pwd=/…/depot"`. La commande s'exécute, `LISTDIR_ROOT` est
  **présente** — les deux symptômes de R1 ont disparu.
- **Parité `migrate` / `derive`**, même `command = "date +%F"` sur un champ `date` absent des deux
  côtés → `jour = "2026-08-31"` **des deux côtés, à l'identique** → critère **atteint**
- `list-dir migrate` sur un champ et une section ajoutés après coup → valeurs posées, valeur déjà
  écrite non recalculée → **conforme**
- Refus au chargement du contrat : `text`+`command` ensemble, `text = ""`, `command = ""`,
  `text`/`command` sur un champ `list`, valeur non-chaîne → refusés, sujet nommé → **conforme**
- `cd skills/list-dir && uvx ruff format --check scripts` → **7 fichiers**, contre **4 sur
  `master`** (recompté sur une extraction de `master` **avec** `ruff.toml`). Les trois ajoutés sont
  écrits par le chantier : `listdir/prefill.py`, `tests/test_prefill.py`,
  `tests/test_derive_merge.py`. Non-critère, mais **la régression s'est aggravée** depuis
  `32918ab` (6) — voir **R8**.
- Comptage des appels à `git` par interposition d'un `git` traçant dans le `PATH` : un `list-dir
  new` sur un contrat **sans aucun** `text`/`command` → `GITCALL rev-parse --show-toplevel` →
  **R7 confirmé**
- `list-dir migrate l --dry-run` avec `command = "touch …/EFFET && echo v"` → **le fichier `EFFET`
  existe après coup** → voir **R10**

### Conformité à l'intention

- Critère « `uvx pytest tests -q` passe » : **atteint**, vérifié — 342 passés.
- Critère « `command = "date +%F"` sur un champ `date` produit la date du jour à `new` » :
  **atteint**, vérifié de bout en bout.
- Critère « `text` produit ce texte à la place du marqueur, champ comme section » : **atteint**,
  vérifié (champ et section, à `new` et à `migrate`).
- Critère « `migrate` et `derive` posent la même valeur pour un champ absent » : **ATTEINT**, ce
  qui lève le bloquant du rapport précédent. Vérifié avec `command`, sur un champ `date`, dans un
  dépôt git : la même valeur des deux côtés. Le trou de couverture est comblé —
  `test_derive_merge.py` exerce désormais `command` en `derive`, et son échec.
- Critère « une `command` qui échoue fait échouer la création, rien n'est écrit, le message nomme
  la commande » : **atteint**, vérifié à `new`, à `migrate` et — nouveau — à `derive`
  (`test_une_command_qui_echoue_en_derive_n_ecrit_rien` assère `not cible.exists()`).
- Critère « `text` et `command` sur un même champ refusés par `parse_contract`, en nommant le
  champ » : **atteint**, vérifié.
- Hors-périmètre : **respecté**. Aucun `[fields.*.env]`, aucune définition livrée (`defs`) touchée,
  aucun nouveau `type` ni nouvelle commande.
- Signaux de dérive : **aucun matérialisé**. `text` reste strictement littéral ; l'exécution ne
  touche que `create`, `_realign` et `_project` ; `prefill.py` est un module dédié et documenté ;
  le diff reste dans `types.py`, `contract.py`, `store.py`, `prefill.py`, la doc et les tests.
- Symptôme d'origine : **disparu**. Le cas porteur — un champ `date` qui vaut la date du jour —
  fonctionne à `new`, à `migrate` et à `derive`.

### Qualité du code

- **R1** — *(levé)* — `prefill.py:47-61`, `:71-76`, `:103`. Le `PrefillContext` porte désormais un
  `cwd` distinct de `list_dir`, reculé jusqu'au premier ancêtre existant ; `subprocess.run` et
  `git rev-parse` s'en servent. Reproduit en conditions réelles : `derive` exécute la commande et
  voit `LISTDIR_ROOT`. Deux tests l'exercent. Décision consignée au journal du suivi.

- **R2** — *(non traité, maintenu)* — `prefill.py:106-110` — **le message d'échec ment sur la
  cause.** Toute `OSError` reste rapportée « bash introuvable ». Le cas le plus probable — le `cwd`
  inexistant — a disparu avec le correctif de R1, ce qui **réduit la portée** du constat sans le
  lever : une permission refusée sur le `cwd`, un `bash` non exécutable ou un `ENOMEM` enverront
  toujours chercher un `bash` qui est là. Le test
  `test_prefill.py::test_champ_command_binaire_absent` (`:88-91`) exerce toujours le **code 127**
  et non la branche `OSError`, sous un nom qui laisse croire le contraire, et n'assère que
  `not r` — pas le message. La branche `except OSError` du module reste **entièrement non
  couverte**.

- **R3** — *(non traité, maintenu)* — `store.py:334`, `:366` — **une valeur préremplie multi-lignes
  casse la sortie de `migrate`.** Reproduit à nouveau sur `29e423c` : une section portant
  `command = "printf 'ligne1\nligne2\n'"` rend
  `l/a.md: section « Notes » — ajoutée, ligne1` puis `ligne2` sur une ligne à part. L'invariant
  « un changement, une ligne » — sur lequel la sortie de `migrate` se lit et se grep — est rompu.
  Rien ne tronque ni n'aplatit `{valeur}`.

- **R4** — *(non traité, maintenu)* — `prefill.py:138`, `:147-154` — **deux chemins d'échec
  silencieux.** Reproduit : `command = "echo '<À REMPLIR>'"` sur un champ `date` est **accepté** et
  écrit `jour = "<À REMPLIR>"`, parce que `check_value` suspend le contrôle de type sur
  `is_marker(value)`. Un champ que le contrat annonce prérempli ressort donc au marqueur, sans un
  mot. Symétriquement, `initial_section` ne confronte rien : une commande à sortie vide pose une
  section vide, ni marquée ni signalée — dans un paquet dont `prefill.py` proclame en tête
  « ÉCHEC FERMÉ […] Rien n'est avalé ».

- **R5** — *(non traité, maintenu)* — `prefill.py:128-144`, `items.py:187-188` — **un champ `date`
  prérempli est écrit comme une chaîne TOML.** Vérifié : `jour = "2026-08-31"` (guillemets), là où
  `dump_value` rend `2026-08-31` nu pour un `datetime.date`. Les fiches de dette du dépôt portent
  précisément la forme nue (`date = 2026-08-31`). Une même liste porte donc deux graphies du même
  champ selon l'origine de la valeur — sur le cas porteur du chantier.

- **R6** — *(non traité, maintenu)* — `prefill.py:85` — **`LISTDIR_LIST` n'est pas absolue**, contre
  le plan qui annonce « chemin absolu du répertoire-liste ». Vérifié : `list-dir derive src revues`
  pose `LISTDIR_LIST=revues`. La documentation livrée a été adoucie en « le chemin du
  répertoire-liste » sans entrée au journal de décisions. `LISTDIR_ROOT`, elle, est bien absolue —
  les deux variables du même tableau n'ont donc pas la même garantie.

- **R10** *(nouveau)* — `store.py:277`, `:305-320` — **`migrate --dry-run` exécute les commandes du
  contrat.** Le contexte de préremplissage est construit et `_realign` appelé avant le test
  `if dry_run:` (`store.py:298`), de sorte que chaque champ ou section absent portant `command` est
  **réellement lancé** pour construire le libellé du `Change`. Reproduit :
  `command = "touch …/EFFET && echo v"` sur un champ absent, `list-dir migrate l --dry-run` → code
  0, « 1 changement **serait** appliqué », et le fichier `EFFET` **existe**. Un mode d'essai qui
  promet de ne rien faire lance du shell arbitraire ; c'est le seul endroit du paquet où `--dry-run`
  a un effet de bord. Ni le brief, ni le plan, ni la documentation ne l'évoquent.

- **R11** *(nouveau)* — `references/contrat-liste.md` (« La commande tourne **dans le répertoire de
  la liste** »), `SKILL.md` (« lancée dans le répertoire de la liste »), contre `prefill.py:47-61`
  — **le correctif de R1 a rendu la documentation fausse, et une contrainte de l'utilisateur
  approximative.** Le brief pose « exécuter dans le répertoire de la liste » (dit). Depuis `_cwd`,
  la commande tourne dans le **premier ancêtre existant**, ce qui en `derive` n'est jamais la
  liste. Vérifié : `pwd=/…/depot` alors que `LISTDIR_LIST=revues`. Le compromis est défendable et
  consigné au journal, mais il n'a été porté ni dans `contrat-liste.md` ni dans `SKILL.md`, écrits
  avant le correctif : un contrat qui fait `command = "ls | wc -l"` obtiendra un résultat différent
  selon la commande qui l'invoque. Corollaire non documenté : `LISTDIR_ROOT` est résolue depuis cet
  ancêtre, pas depuis la liste visée.

- **R12** *(nouveau)* — `prefill.py:61` — **`return Path.cwd()` est mort.** La boucle parcourt
  `(list_dir, *list_dir.parents)` ; la chaîne des parents se termine toujours par `/` pour un
  chemin absolu et par `.` pour un chemin relatif, tous deux `is_dir()`. Le repli n'est donc
  atteignable que si le répertoire courant du processus a été supprimé sous ses pieds. Aucun test
  ne l'exerce — c'est très exactement le motif de la fiche de dette
  `repli-section-marker-jamais-exerce.md` (voir **R9**), rejoué dans le module que ce chantier
  vient d'écrire.

### Dette induite

- **R7** — *(non traité, maintenu)* — `store.py:224`, `:277`, `:499` — **`create`, `migrate` et
  `derive` lancent `git` inconditionnellement.** Confirmé cette fois par interposition d'un `git`
  traçant dans le `PATH` : un `list-dir new` sur un contrat ne portant **ni `text` ni `command`**
  produit un `git rev-parse --show-toplevel`. Avant ce chantier, ces trois opérations
  n'engendraient aucun processus. Le calcul de `root` est paresseusable — aucune commande à lancer,
  aucun `rev-parse` — et ne pas l'avoir fait fait payer un `fork`/`exec` à chaque `new` de la
  quasi-totalité des listes existantes.

- **R8** — *(non traité, aggravé)* — `uvx ruff format --check` — **la dette de formatage annoncée
  continue de croître.** Le suivi note « 4 fichiers **avant** le chantier — ce n'est pas un
  critère » ; il y en avait 6 sur `32918ab`, il y en a **7 sur `29e423c`**. Les trois ajoutés sont
  tous écrits par le chantier : `listdir/prefill.py`, `tests/test_prefill.py`,
  `tests/test_derive_merge.py` — ce dernier ajouté par le correctif de R1 lui-même, après que le
  rapport précédent eut signalé le point. L'excuse porte sur l'héritage, pas sur ce qu'on vient
  d'écrire.

- **R9** — *(non traité, maintenu)* —
  `.claude/implementation/todo/technical-debt/repli-section-marker-jamais-exerce.md` — **une fiche
  de dette soldée de fait, laissée en `todo/`.** Le chantier a pris la seconde issue qu'elle
  proposait : `Contract.section_marker` est supprimé de `types.py`, et `grep -rn section_marker` ne
  rend plus que des documents. La fiche décrit du code qui n'existe plus, sans trace du chantier
  qui l'a résolue.

### Bloquants

Aucun. Tous les critères de réussite sont atteints et vérifiés par exécution. Les onze constats
restants (**R2**–**R12**) sont des réserves : l'utilisateur doit les connaître avant de clôturer,
aucun n'interdit la clôture. Les plus coûteux si laissés en l'état sont **R10** (effet de bord d'un
`--dry-run`), **R4** (échec silencieux là où le module promet l'échec fermé) et **R11** (la
documentation livrée décrit un comportement que le correctif a changé).

## 2026-08-31 — clôture — `0804ab0`

**Verdict** : RÉSERVES

Troisième audit de clôture, après le commit `0804ab0` « traiter les réserves R10, R11, R12 et R8 ».
**R8, R10, R11 et R12 sont levés**, vérifiés par exécution. **R2, R3, R4, R5, R6, R7 et R9 n'ont
reçu aucun correctif** et sont repris tels quels — le suivi ne les revendique pas. Un constat
nouveau, **R13**, est un effet direct du correctif de R10 ; **R14** relève du style.

### Vérifications exécutées

- `cd skills/list-dir/scripts && uvx pytest tests -q` → **343 passés, 0 échec** (342 sur
  `29e423c`, 307 annoncés avant chantier)
- `cd skills/list-dir && uvx ruff check scripts` → **All checks passed!**
- `cd skills/list-dir && uvx ruff format --check scripts` → **4 fichiers**
  (`tests/test_contract.py`, `test_items.py`, `test_loader.py`, `test_move.py`), contre **4 sur
  `master`** — recompté sur une extraction de `master` : **exactement la même liste**. R8 est
  **levé**, la régression de formatage est effacée.
- Bloc « Vérification de bout en bout » du plan, extraits de contrat **recopiés depuis
  `references/contrat-liste.md`** :
  - `list-dir new` avec `command = "date +%F"` → `date = "2026-08-31"`, pas de marqueur →
    **conforme**
  - section `text = "Créé automatiquement."` → `## Origine` porte le texte → **conforme**
  - `list-dir validate ma-liste --filled` → réclame `title` et `Constat`, **pas** `date` ni
    `Origine` → **conforme**
  - `command = "false"` → `ma-liste: champ « date » — commande « false » a échoué (code 1) :`,
    code 1, `second.md` non créé, `ls` ne montre que `premier.md` → **conforme**
- **Le cas de R10, rejoué** — `command = "touch …/EFFET && echo v"` sur un champ absent :
  `migrate l --dry-run` → code 0, libellé `ajouté, sortie de « touch …/EFFET && echo v »`, et
  **`EFFET` n'existe pas**. `migrate l` ensuite → `ajouté, v`, `EFFET` existe. R10 **levé**.
- **Le cas de R12** — `prefill.py:62` : le repli `Path.cwd()` est supprimé, remplacé par un
  `next(...)` et un commentaire qui motive l'absence de repli. R12 **levé**.
- **Parité `migrate` / `derive`**, même `command = "date +%F"` sur un champ `date` absent des deux
  côtés → `jour = "2026-08-31"` **des deux côtés** → critère **atteint**
- `list-dir derive src revues --template revue` dans un dépôt git, champ sans `from` portant
  `command` → succès, `verdict = "list=revues root=/…/dv/depot pwd=/…/dv/depot"` : la commande
  s'exécute, `LISTDIR_ROOT` est présente, et le cwd est bien l'ancêtre — **exactement ce que la
  documentation décrit désormais**. R11 **levé**.
- Refus au chargement du contrat (`list-dir validate`) : `text`+`command` ensemble, `text = ""`,
  `command = ""`, `text` sur un champ `list` → les quatre refusés, le sujet nommé → **conforme**
- Comptage des appels à `git` par interposition d'un `git` traçant dans le `PATH` : `list-dir new`
  sur un contrat **sans aucun** `text`/`command` → `GITCALL rev-parse --show-toplevel` → **R7
  toujours présent**
- `command = "echo '<À REMPLIR>'"` sur un champ `date` → accepté, `marque = "<À REMPLIR>"` écrit →
  **R4 toujours présent**
- `command = "printf 'ligne1\nligne2\n'"` sur une section → `l/a.md: section « Notes » — ajoutée,
  ligne1` puis `ligne2` sur une ligne à part → **R3 toujours présent**
- `LISTDIR_LIST` → `list=ma-liste` (relatif, tel que donné par l'appelant) → **R6 toujours
  présent**
- `text = "pas une date"` sur un champ `date` : `migrate --dry-run` → **code 0**, « 2 changements
  seraient appliqués » ; `migrate` → **code 1**, `valeur issue de « text » refusée` → voir **R13**

### Conformité à l'intention

- Critère « `uvx pytest tests -q` passe » : **atteint**, vérifié — 343 passés.
- Critère « `command = "date +%F"` sur un champ `date` produit la date du jour à `new` » :
  **atteint**, vérifié de bout en bout.
- Critère « `text` produit ce texte à la place du marqueur, champ comme section » : **atteint**,
  vérifié (champ et section, à `new` et à `migrate`).
- Critère « `migrate` et `derive` posent la même valeur pour un champ absent » : **atteint**,
  vérifié avec `command` sur un champ `date`, dans un dépôt git.
- Critère « une `command` qui échoue fait échouer la création, rien n'est écrit, le message nomme
  la commande » : **atteint**, vérifié à `new`, à `migrate` et à `derive`.
- Critère « `text` et `command` sur un même champ refusés par `parse_contract`, en nommant le
  champ » : **atteint**, vérifié.
- Hors-périmètre : **respecté**. Aucun `[fields.*.env]`, aucune définition livrée (`defs`) touchée,
  aucun nouveau `type` ni nouvelle commande. `git diff --stat master...0804ab0` ne sort de
  `listdir/` que pour `SKILL.md`, `references/contrat-liste.md`, les tests et les fichiers de
  suivi.
- Signaux de dérive : **aucun matérialisé**. `text` reste strictement littéral ; l'exécution ne
  touche que `create`, `_realign` et `_project` ; `prefill.py` est un module dédié et documenté en
  tête ; le diff reste dans `types.py`, `contract.py`, `store.py`, `prefill.py`, la doc et les
  tests.
- Symptôme d'origine : **disparu**. Le champ `date` qui vaut la date du jour fonctionne à `new`, à
  `migrate` et à `derive`.

### Qualité du code

- **R2** — *(non traité, maintenu)* — `prefill.py:105-109` — **le message d'échec ment sur la
  cause.** Toute `OSError` reste rapportée « bash introuvable » : permission refusée sur le `cwd`,
  `bash` non exécutable, `ENOMEM` enverront chercher un `bash` qui est là. Le test
  `test_prefill.py::test_champ_command_binaire_absent` exerce toujours le **code 127** et non la
  branche `OSError`, sous un nom qui laisse croire le contraire. La branche `except OSError` reste
  **entièrement non couverte** — ce qui est le motif exact de la fiche de dette invoquée pour
  supprimer le repli de R12 : « un chemin jamais exercé est un chemin dont on ne sait rien »
  (`prefill.py:60-61`). Le chantier vient d'écrire cette phrase et laisse une branche dans ce cas
  dix lignes plus haut.

- **R3** — *(non traité, maintenu)* — `store.py:343`, `:379` — **une valeur préremplie multi-lignes
  casse la sortie de `migrate`.** Reproduit sur `0804ab0` : `command = "printf 'ligne1\nligne2\n'"`
  sur une section rend deux lignes de sortie pour un seul changement. L'invariant « un changement,
  une ligne » — sur lequel la sortie de `migrate` se lit et se grep — reste rompu ; rien ne tronque
  ni n'aplatit `{corps}`. Le correctif de R10 a réécrit ces deux lignes exactes sans traiter le
  point.

- **R4** — *(non traité, maintenu)* — `prefill.py:151`, `:160-167` — **deux chemins d'échec
  silencieux.** Reproduit : `command = "echo '<À REMPLIR>'"` sur un champ `date` est **accepté** et
  écrit `marque = "<À REMPLIR>"`, `check_value` suspendant le contrôle de type sur `is_marker`. Un
  champ que le contrat annonce prérempli ressort au marqueur, sans un mot. Symétriquement,
  `initial_section` ne confronte rien : une commande à sortie vide pose une section vide, ni
  marquée ni signalée — dans un module dont l'en-tête proclame « ÉCHEC FERMÉ […] Rien n'est avalé ».

- **R5** — *(non traité, maintenu)* — `prefill.py:141-157` — **un champ `date` prérempli est écrit
  comme une chaîne TOML.** Vérifié : `date = "2026-08-31"` (guillemets), là où `dump_value` rend
  `2026-08-31` nu pour un `datetime.date` — forme que portent précisément les fiches de dette du
  dépôt. Une même liste porte deux graphies du même champ selon l'origine de la valeur, sur le cas
  porteur du chantier.

- **R6** — *(non traité, maintenu)* — `prefill.py:84` — **`LISTDIR_LIST` n'est pas absolue**, contre
  le plan qui annonce « chemin absolu du répertoire-liste ». Vérifié : `list-dir new ma-liste x`
  pose `LISTDIR_LIST=ma-liste`. `LISTDIR_ROOT` est absolue — les deux variables du même tableau
  n'ont pas la même garantie, et la documentation a été adoucie en « le chemin du répertoire-liste »
  sans entrée au journal de décisions.

- **R13** *(nouveau)* — `store.py:287`, `:337-341`, `:372-376`, `prefill.py:118-129` —
  **`migrate --dry-run` n'annonce plus ce que la migration ferait : il annonce un succès là où la
  migration échoue.** En `dry_run`, `preview()` court-circuite `initial_field` — donc aussi
  `check_value`. Reproduit : contrat portant `text = "pas une date"` sur un champ `date` →
  `migrate l --dry-run` sort en **code 0** avec « 2 changements seraient appliqués », puis
  `migrate l` sort en **code 1** (`valeur issue de « text » refusée : … n'est pas une date ISO`)
  sans rien écrire. Le contrat du mode d'essai — que le test
  `test_dry_run_annonce_ce_que_la_migration_ferait` assère par `actes(sec) == actes(reel)` — est
  désormais faux dès qu'un préremplissage est en jeu, et ce test ne l'exerce pas. Le cas `text` est
  le plus net : il est **littéral**, ne lance aucun shell, et pouvait donc être confronté à
  `check_value` en dry-run sans rien exécuter. Le correctif de R10 a traité l'effet de bord en
  supprimant aussi la validation, alors que seul le second exigeait un court-circuit.

- **R14** *(nouveau)* — `SKILL.md:87` (171 colonnes) — **la ligne réécrite par `0804ab0` rompt
  l'enroulement du fichier.** Toutes les autres lignes de `SKILL.md` tiennent sous ~105 colonnes,
  sur `master` comme sur la branche ; celle-ci est la seule au-delà de 110. L'édition a inséré du
  texte sans réenrouler le paragraphe. Défaut de style, sans conséquence fonctionnelle.

### Dette induite

- **R7** — *(non traité, maintenu)* — `store.py:224`, `:277`, `:510` — **`create`, `migrate` et
  `derive` lancent `git` inconditionnellement.** Reconfirmé sur `0804ab0` par interposition d'un
  `git` traçant : un `list-dir new` sur un contrat ne portant **ni `text` ni `command`** produit un
  `git rev-parse --show-toplevel`. Avant ce chantier, ces trois opérations n'engendraient aucun
  processus. Le calcul de `root` est paresseusable — aucune commande à lancer, aucun `rev-parse` —
  et ne pas l'avoir fait fait payer un `fork`/`exec` à chaque `new` de la quasi-totalité des listes
  existantes.

- **R9** — *(non traité, maintenu)* —
  `.claude/implementation/todo/technical-debt/repli-section-marker-jamais-exerce.md` — **une fiche
  de dette soldée de fait, laissée en `todo/`.** Le chantier a pris la seconde issue qu'elle
  proposait : `Contract.section_marker` est supprimé de `types.py`, et `grep -rn section_marker` ne
  rend plus que des documents (vérifié sur `0804ab0`). La fiche décrit du code qui n'existe plus,
  sans trace du chantier qui l'a résolue.

- **R15** *(nouveau, mineur)* — `references/contrat-liste.md:301-308` — **« Deux limites à
  connaître » en introduit trois.** Le correctif de R11 a ajouté un troisième point à une liste
  dont la phrase d'amorce annonce le compte. Corriger le compte, ou l'amorce.

### Bloquants

Aucun. Les six critères de réussite sont atteints et vérifiés par exécution ; le hors-périmètre est
respecté ; aucun signal de dérive n'est matérialisé. Restent **neuf réserves** : R2, R3, R4, R5, R6,
R7 et R9 non traitées depuis le premier rapport, plus R13 et R15 introduites par le correctif de
`0804ab0`, plus R14 de style. La plus coûteuse est **R13** — un `--dry-run` qui rend code 0 sur une
migration qui échouera à coup sûr est plus trompeur que l'effet de bord qu'il a remplacé — suivie de
**R4** (échec silencieux là où le module promet l'échec fermé).

---

## 2026-08-31 — clôture — `4c55392`

**Verdict** : RÉSERVES

Quatrième audit de clôture, après le commit `4c55392` « garder le contrôle de type sur `text` en
dry-run ». **R13 est levé**, vérifié par exécution. **R2, R3, R4, R5, R6, R7, R9, R14 et R15 n'ont
reçu aucun correctif** et sont repris tels quels — le suivi ne les revendique pas, il les destine au
registre de dette. Quatre constats nouveaux, tous mineurs, sont des effets directs du correctif de
R13 ou de la nouvelle voie de câblage : **R16**, **R17**, **R18**, **R19**.

### Vérifications exécutées

- `cd skills/list-dir/scripts && uvx pytest tests -q` → **344 passés, 0 échec** (343 sur `0804ab0`,
  307 annoncés avant chantier)
- `cd skills/list-dir/scripts && uvx pytest tests/test_contract.py tests/test_prefill.py -q` →
  **87 passés, 0 échec** (vérifs des étapes 1 et 2)
- `cd skills/list-dir && uvx ruff check scripts` → **All checks passed!** (vérif de l'étape 5)
- `cd skills/list-dir && uvx ruff format --check scripts` → **4 fichiers**
  (`tests/test_contract.py:52`, `test_items.py:123`, `test_loader.py:38`, `test_move.py:27`),
  recompté sur une extraction de `master` munie du même `ruff.toml` : **exactement la même liste**.
  R8 reste **levé**, aucune régression de formatage. Non-critère, rappelé pour mémoire.
- Bloc « Vérification de bout en bout » du plan, extraits de contrat **recopiés depuis
  `references/contrat-liste.md`** :
  - `list-dir new` avec `command = "date +%F"` → `date = "2026-08-31"` (date du jour), pas de
    marqueur → **conforme**
  - section `text = "Rien d'assumé à ce jour."` → `## Origine` porte le texte → **conforme**
  - `list-dir validate ma-liste --filled` → réclame `title` et `Constat`, **pas** `date` ni
    `Origine` → **conforme**
  - `command = "false"` → `ma-liste: champ « date » — commande « false » a échoué (code 1) :`,
    code 1, `ls ma-liste/` ne montre que `premier.md` → **conforme**
- **Le cas de R13, rejoué** — `text = "pas une date"` sur un champ `date` : `migrate l --dry-run`
  → **code 1**, `valeur issue de « text » refusée : « pas une date » n'est pas une date ISO` ;
  `migrate l` → **code 1**, même message, `a.md` inchangé. Le dry-run et le réel s'accordent.
  R13 **levé**.
- **Le cas de R10, revérifié** — `command = "touch EFFET && echo v"` sur un champ absent :
  `migrate l --dry-run` → code 0, libellé `ajouté, sortie de « touch EFFET && echo v »`, et
  `ls l/` ne montre que `a.md` : **aucun effet de bord**. R10 reste **levé**.
- **Parité `migrate` / `derive`** — même `command = "date +%F"` sur un champ `date` absent des deux
  côtés, dans un dépôt git → `jour = "2026-08-31"` **des deux côtés** → critère **atteint**
- `list-dir derive src revues --template revue`, champ sans `from` portant `command` → succès,
  `verdict = "list=revues root=/…/dv/depot pwd=/…/dv/depot"` : `LISTDIR_LIST` nomme la liste
  engendrée, `LISTDIR_ROOT` est présente, le cwd est l'ancêtre existant — conforme à la
  documentation. Section `text` sans effet en `derive` → conforme à la limite documentée.
- Refus au chargement du contrat (`list-dir validate`), **cinq cas** : `text`+`command` ensemble,
  `text = ""`, `command = ""`, `text = 12`, `text` sur un champ `list` → les cinq refusés, le champ
  nommé → **conforme**
- `LISTDIR_ROOT` → `ABSENTE` hors dépôt, absolue dans un dépôt → **conforme**
- Comptage des appels à `git` par interposition d'un `git` traçant dans le `PATH` : `list-dir new`
  sur un contrat **sans aucun** `text`/`command` → `GITCALL rev-parse --show-toplevel` → **R7
  toujours présent**
- `command = "echo '<À REMPLIR>'"` sur un champ `date` → accepté, `marque = "<À REMPLIR>"` écrit,
  et `validate --filled` le réclame ensuite → **R4 toujours présent**
- `command = "true"` sur une section → `section « Vide » — ajoutée, ` puis un `## Vide` vide dans la
  fiche → **R4 toujours présent, second volet**
- `command = "printf 'ligne1\nligne2\n'"` sur une section → le libellé de `migrate` s'étale sur deux
  lignes pour un seul changement → **R3 toujours présent**
- `LISTDIR_LIST` → `list=l` (relatif, tel que donné par l'appelant), quand `LISTDIR_ROOT` et le
  `pwd` sont absolus → **R6 toujours présent**
- `jour = "2026-08-31"` (guillemets) sur un champ `date` prérempli → **R5 toujours présent**
- `awk 'length>110'` sur `SKILL.md` → une seule ligne, **`:87` (171 colonnes)**, absente de `master`
  → **R14 toujours présent**

Aucune commande de vérification n'est restée non exécutée.

### Conformité à l'intention

- Critère « `uvx pytest tests -q` passe » : **atteint**, vérifié — 344 passés, 0 échec.
- Critère « `command = "date +%F"` sur un champ `date` produit la date du jour à `new` » :
  **atteint**, vérifié de bout en bout depuis la doc écrite.
- Critère « `text` produit ce texte à la place du marqueur, champ comme section » : **atteint**,
  vérifié champ et section, à `new` et à `migrate`.
- Critère « `migrate` et `derive` posent la même valeur pour un champ absent » : **atteint**,
  vérifié avec `command = "date +%F"` de part et d'autre, dans un dépôt git.
- Critère « une `command` qui échoue fait échouer la création, rien n'est écrit, le message nomme
  la commande » : **atteint**, vérifié à `new` (`second.md` non créé), à `migrate` et à `derive`.
- Critère « `text` et `command` sur un même champ refusés par `parse_contract`, en nommant le
  champ » : **atteint**, vérifié.
- Hors-périmètre : **respecté**. `git diff --stat master...4c55392` ne sort de `listdir/` que pour
  `SKILL.md`, `references/contrat-liste.md`, les tests et les fichiers de suivi. Aucun
  `[fields.*.env]`, aucune définition livrée (`defs`) touchée, aucun nouveau `type`, aucune
  nouvelle commande.
- Signaux de dérive : **aucun matérialisé**. `text` est strictement littéral, aucune substitution ;
  l'exécution ne touche que `create`, `_realign` et `_project` ; `prefill.py` est le module dédié,
  documenté en tête, second et dernier site d'exécution du paquet ; le diff reste dans `types.py`,
  `contract.py`, `store.py`, `prefill.py`, la doc et les tests.
- Symptôme d'origine : **disparu**. Le champ `date` qui vaut la date du jour fonctionne à `new`, à
  `migrate` et à `derive`.

### Qualité du code

- **R13** — **LEVÉ**. `store.py:339`, `:373` conditionnent désormais le court-circuit à
  `f.command is not None` / `s.command is not None` ; `text` et le marqueur repassent par
  `initial_field` / `initial_section`, donc par `check_value`. Vérifié : le dry-run et la migration
  réelle rendent le même code et le même message sur `text = "pas une date"`. Le test
  `test_dry_run_refuse_un_text_que_la_migration_refuserait` exerce le cas. Le correctif est le plus
  étroit possible — il n'a pas rouvert l'effet de bord de R10, revérifié.

- **R16** *(nouveau, mineur)* — `prefill.py:131-133` — **la garde de `preview()` n'est exercée par
  aucun test.** `preview` lève désormais un `ValueError` quand `decl.command is None`. Aucun test du
  paquet n'appelle `preview` — `grep -n preview tests/*.py` ne rend **rien** ; la fonction n'est
  atteinte qu'indirectement, par `migrate --dry-run`, et jamais sur la branche qui lève. C'est le
  motif exact que le chantier invoque dix lignes plus haut pour supprimer le repli de R12 : « un
  chemin jamais exercé est un chemin dont on ne sait rien » (`prefill.py:60-61`). Coût faible — la
  branche n'est joignable que par une erreur de programmation — mais le paquet vient d'écrire la
  règle qu'il enfreint ici.

- **R17** *(nouveau, mineur)* — `store.py:319-323` — **la docstring de `_realign` décrit le
  comportement d'avant `4c55392`.** Elle dit encore, sans nuance, que `prefill.preview` compose le
  libellé et que « l'élément rendu n'est plus écrivable ». C'est désormais vrai **des seules
  déclarations portant `command`** : sur `text` et sur un marqueur, le dry-run passe par le chemin
  normal et valide. Le commentaire en ligne (`:334-338`) est juste ; la docstring qui le surplombe
  ne l'a pas suivi. Un lecteur qui s'arrête à la docstring conclut qu'un dry-run ne valide jamais.

- **R18** *(nouveau)* — `store.py:339`, `prefill.py:118-134` — **le dry-run annonce toujours un
  succès sur une `command` qui fera échouer la migration.** Reproduit : `command = "false"` sur un
  champ absent → `migrate l --dry-run` sort en **code 0** avec « 1 changement serait appliqué » ;
  `migrate l` sort en **code 1**. C'est le résidu assumé de R13 : le journal de décisions tranche
  que seul `text` pouvait être validé sans lancer de shell, et le raisonnement tient — on ne peut
  pas savoir si `false` échouera sans la jouer. La réserve porte sur ce qui n'a pas été fait
  **autour** : ni `references/contrat-liste.md:305-306`, ni `SKILL.md:87` n'avertissent que le mode
  d'essai peut rendre code 0 sur une migration vouée à l'échec. La doc dit « ne lance aucune
  commande », ce qui est exact, et laisse croire que le reste de la promesse du dry-run tient.
  Arbitrage à assumer explicitement, pas défaut de correction.

- **R19** *(nouveau, mineur)* — `contract.py:396-397` atteint depuis `prefill.py:157` — **un message
  qui parle de « champ requis » sur un champ facultatif.** Reproduit : `command = "true"` (sortie
  vide) sur un champ `type = "text"`, `required = false` → `valeur issue de commande « true »
  refusée : vide — un champ requis se remplit ou porte son marqueur`. La chaîne préexiste sur
  `master` et n'est pas du chantier ; c'est le nouveau câblage qui la rend atteignable dans un cas
  où elle est fausse — l'utilisateur cherchera un `required = true` qu'il n'a pas écrit. À noter :
  ce refus vaut pour un champ, jamais pour une section (voir R4).

- **R2** — *(non traité, maintenu)* — `prefill.py:105-109` — **le message d'échec ment sur la
  cause.** Toute `OSError` reste rapportée « bash introuvable » : permission refusée sur le `cwd`,
  `bash` non exécutable, `ENOMEM` enverront chercher un `bash` qui est là. Vérifié sur `4c55392` :
  `test_champ_command_binaire_absent` (`test_prefill.py:88`) passe un `command =
  "/inexistant/binaire"` — donc le **code 127** de bash, pas la branche `OSError` —, sous un nom qui
  laisse croire le contraire. La branche `except OSError` reste **entièrement non couverte**.

- **R3** — *(non traité, maintenu)* — `store.py:347`, `:383` — **une valeur préremplie multi-lignes
  casse la sortie de `migrate`.** Reproduit sur `4c55392` : `command = "printf 'ligne1\nligne2\n'"`
  sur une section rend deux lignes de sortie pour un seul changement, et `section « Vide » —
  ajoutée, ` laisse un libellé qui se termine sur un blanc. L'invariant « un changement, une
  ligne » — sur lequel la sortie de `migrate` se lit et se grep — reste rompu.

- **R4** — *(non traité, maintenu)* — `prefill.py:151`, `:160-167` — **deux chemins d'échec
  silencieux.** Reproduits tous les deux : `command = "echo '<À REMPLIR>'"` sur un champ `date` est
  **accepté** et écrit `marque = "<À REMPLIR>"` (`check_value` suspend le contrôle de type sur
  `is_marker`), le champ ressortant réclamé par `validate --filled` alors que le contrat l'annonçait
  prérempli ; et `command = "true"` sur une **section** pose un `## Vide` vide, ni marqué ni
  signalé, `initial_section` ne confrontant rien. Le tout dans un module dont l'en-tête proclame
  « ÉCHEC FERMÉ […] Rien n'est avalé ».

- **R5** — *(non traité, maintenu)* — `prefill.py:141-157` — **un champ `date` prérempli est écrit
  comme une chaîne TOML.** Revérifié : `jour = "2026-08-31"` avec guillemets, là où `dump_value`
  (`items.py:163`) rend `2026-08-31` nu pour un `datetime.date`. Une même liste porte deux graphies
  du même champ selon l'origine de la valeur, sur le cas porteur du chantier.

- **R6** — *(non traité, maintenu)* — `prefill.py:84` — **`LISTDIR_LIST` n'est pas absolue**, contre
  le plan qui annonce « chemin absolu du répertoire-liste ». Revérifié : `list-dir new l a` pose
  `LISTDIR_LIST=l`, quand `LISTDIR_ROOT` et le `pwd` de la commande sont absolus. Les deux variables
  du même tableau n'ont pas la même garantie ; la documentation a été adoucie en « le chemin du
  répertoire-liste » sans entrée au journal.

- **R14** — *(non traité, maintenu)* — `SKILL.md:87` (171 colonnes) — **la ligne rompt l'enroulement
  du fichier.** Recompté sur `4c55392` : c'est la **seule** ligne de `SKILL.md` au-delà de 110
  colonnes, et `master` n'en a aucune. Défaut de style, sans conséquence fonctionnelle.

### Dette induite

- **R7** — *(non traité, maintenu)* — `store.py:224`, `:277`, `:510` — **`create`, `migrate` et
  `derive` lancent `git` inconditionnellement.** Reconfirmé sur `4c55392` par interposition d'un
  `git` traçant : un `list-dir new` sur un contrat ne portant **ni `text` ni `command`** produit un
  `git rev-parse --show-toplevel`. Avant ce chantier, ces trois opérations n'engendraient aucun
  processus. Le calcul de `root` est paresseusable et ne l'a pas été : un `fork`/`exec` payé à
  chaque `new` de la quasi-totalité des listes existantes.

- **R9** — *(non traité, maintenu)* —
  `.claude/implementation/todo/technical-debt/repli-section-marker-jamais-exerce.md` — **une fiche
  de dette soldée de fait, laissée en `todo/`.** Le chantier a pris la seconde issue qu'elle
  proposait : `Contract.section_marker` est supprimé de `types.py`, et `grep -rn section_marker`
  sur `4c55392` ne rend plus que des documents (le suivi, le plan, un plan clos et la fiche
  elle-même). La fiche décrit du code qui n'existe plus.

- **R15** — *(non traité, maintenu)* — `references/contrat-liste.md:301-308` — **« Deux limites à
  connaître » en introduit trois.** Revérifié sur `4c55392` : la liste porte bien trois puces
  (`derive` et les sections, `migrate --dry-run`, rien n'est mémorisé) sous une amorce qui en
  annonce deux.

### Bloquants

Aucun. Les six critères de réussite sont atteints et vérifiés par exécution ; le hors-périmètre est
respecté ; aucun signal de dérive n'est matérialisé ; aucune commande de vérification n'est en
échec. Restent **treize réserves** : R2, R3, R4, R5, R6, R7, R9, R14 et R15, non traitées depuis les
rapports précédents et explicitement destinées au registre de dette par le suivi, plus R16, R17, R18
et R19 introduites ou révélées par `4c55392`. La plus coûteuse reste **R4** — un échec silencieux
dans le module qui promet l'échec fermé —, suivie de **R18**, qui n'est pas un défaut mais un
arbitrage que la documentation ne dit pas.
