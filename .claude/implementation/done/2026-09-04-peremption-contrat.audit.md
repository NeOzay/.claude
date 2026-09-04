---
slug: peremption-contrat
---

## 2026-09-04 — clôture — `5d4a4d8`

**Verdict** : DÉFAVORABLE

### Vérifications exécutées

Depuis `skills/list-dir/`, sauf mention contraire.

- `uvx pytest scripts/tests -q` → **407 passés, 0 échec** (le plan en annonçait 346 avant chantier)
- `uvx ruff check scripts` → **All checks passed!**
- `uvx ruff format --check --diff scripts` → 4 fichiers à reformater :
  `tests/test_contract.py`, `tests/test_items.py`, `tests/test_loader.py`, `tests/test_move.py` —
  **aucun n'est touché par la branche**, écart préexistant et annoncé dans le suivi
- `uvx pyright` → **9 erreurs**, toutes dans `tests/conftest.py`, `test_contract.py`,
  `test_items.py`, `test_move.py`, `test_prefill.py` — fichiers **non touchés** par la branche ;
  aucun des fichiers du chantier ne produit d'erreur. Écart préexistant et annoncé.
- Boucle de vérification de l'étape 8 (depuis la racine du dépôt : `diff -r` semence, `diff`
  contrat, `validate` code + stderr sur les trois registres) → **aucune ligne d'écart, code 0,
  stderr vide** sur `technical-debt`, `technical-debt-solde`, `technical-debt-ecarte`
- Étape 7 : `grep -rn "douze" skills/list-dir/SKILL.md` → **sans résultat** ;
  `grep -c "semence/" references/contrat-liste.md` → 5 ;
  `grep -n "contenu \*\*est\*\* le futur" references/contrat-liste.md` → sans résultat
- Bac d'essai complet monté à la main (projet jetable, définition `monseed` au rang 1, liste semée
  puis versions 1→4) : `init --def`, `validate` sur les huit états du tableau d'avertissements,
  `reseed` nominal, en conflit, `--force`, `--dry-run`, adoption d'une liste sans `[origin]` —
  sorties détaillées ci-dessous.

### Conformité à l'intention

Critère par critère, dans l'ordre du brief.

1. **`init --def` → `diff` muet, `[origin]` compris** : **atteint, vérifié**. `diff` muet sur la
   définition du dépôt (`technical-debt`) comme sur la définition d'essai ; `.list/semence/` est
   `diff -r`-identique à la définition.
2. **`validate` sur une liste dont la semence a été incrémentée : avertissement + code de retour
   conservé** : **atteint, vérifié**. Liste conforme → stdout `0 élément(s) conformes`, code 0,
   stderr `contrat périmé — semé en v1, « monseed » est en v2 ; « list-dir reseed liste »
   rattrape`. Liste avec violation → code 1, le bilan des manquements **et** l'avertissement.
3. **`frozen = true` tait la péremption, fait refuser `reseed`, `--force` passe outre** :
   **atteint, vérifié**. `validate` muet, `reseed` refusé code 1 avec message nommé, `reseed
   --force` appliqué.
4. **`reseed` sauvegarde, injecte, sort non nul en nommant les clés sur conflit** : **atteint,
   vérifié**. `.list/backup/{contract.toml,templates/}` écrit, apports injectés sans écraser la
   description locale, conflit → code 1 listant `fields.priorite.values — modifiée des deux côtés`
   et `gabarit note.md — modifiée des deux côtés`, contrat **intact à l'octet** après la tentative,
   avec comme sans `--force`.
5. **`pytest` passe ; `ruff` et `pyright` restent propres** : **atteint** pour `pytest` et `ruff
   check` ; **atteint au sens du suivi** pour `ruff format` et `pyright` — les écarts constatés sont
   préexistants et cantonnés à des fichiers que la branche ne touche pas (vérifié fichier par
   fichier).
6. **`reseed --def <nom>` sur une liste sans `[origin]` : estampille + injection, refus sur
   conflit** : **atteint, vérifié**. Adoption d'une liste identique à `[origin]` près → recopie
   verbatim, commentaires de la semence préservés, `origin.def`/`origin.version` posés ;
   `.list/semence/` créé au passage ; liste divergente → injection ; clé divergente → refus.
7. **Squelette d'`init` sans `--def` porte `def = false`, et n'avertit jamais** : **atteint,
   vérifié** (stderr vide sur `validate`).
8. **`init --def <nom>` sur une semence qui déclare un autre nom échoue en code 2** : **NON
   ATTEINT** — voir **R1**. Le message est bien celui attendu, le **code de retour observé est 1**.
9. **`validate` sans `[origin]` signale l'absence de provenance ; `def = false` la tait** :
   **atteint, vérifié** (message d'adoption complet, geste rappelé ; `def = false` → stderr vide).
10. **Les trois définitions portent une version, les trois listes sont estampillées sans autre
    modification** : **atteint, vérifié**. `+4` lignes par contrat (la table `[origin]`), plus les
    `.list/semence/` versionnées ; aucun élément `*.md` touché.

**Hors-périmètre** : respecté. Aucun re-semis automatique ; aucune liste ne référence sa semence
(`def` ne porte qu'un nom) ; `reseed` n'écrit que sous `.list/` — vérifié par `find` avant/après ;
`debt-review`, `road-map` et le pipeline ne sont pas retouchés (le seul fichier
d'`implementation-tracker` modifié hors `list-dir/*/contract.toml` est `references/dette.md`, que
l'étape 7 du plan prévoit).

**Signaux de dérive** : aucun matérialisé. `grep -rn "resolve("` ne montre que trois appelants :
`commands/init.py`, `commands/contract.py` (préexistant, sur `--def` explicite) et les deux voies
autorisées — `commands/reseed.py` et `provenance._peremption`. L'avertissement ne fait jamais
tomber un `validate` conforme (vérifié). `--force` ne tranche aucun conflit (vérifié). La copie
reste octet pour octet égale à sa semence après `init` (vérifié).

**Symptôme d'origine** : disparu. Une divergence semence/liste est désormais dite par `validate`,
et rattrapable sur ordre.

### Qualité du code

- **R1** — `scripts/listdir/commands/init.py:86` et `scripts/listdir/commands/reseed.py:86` —
  **le code 2 est perdu à la sortie de la CLI**. `store.init_list` et `provenance.reseed` rendent
  bien `fail(..., 2)` sur un nom discordant, et les tests l'assertent au niveau bibliothèque
  (`test_provenance.py:203`, `test_reseed.py:203`). Mais les deux commandes ré-emballent l'échec en
  `utils.fail(r.message)`, dont le statut vaut 1 par défaut, et `list-dir.py:111` propage ce 1.
  Constaté :

  ```
  $ list-dir init nouvelle --def autre    # la semence déclare « monseed »
  …/autre/contract.toml: semée sous « autre », mais « origin.def » y déclare « monseed » — …
  code=1                                   # attendu : 2
  $ list-dir init x --def monseed --name toto
  --name et --description ne s'appliquent qu'au squelette : …
  code=2                                   # le câblage marche quand le code est transmis
  ```

  La documentation écrite dans ce même chantier affirme le contraire :
  `skills/list-dir/references/contrat-liste.md:195` — « un autre nom est refusé en code 2 ». Le
  brief en fait un critère explicite. Aucun test CLI ne couvre ce code de retour, ce qui est
  précisément par où la régression est passée.

- **R2** — `scripts/listdir/provenance.py:315-316` — **le sentinelle `MISSING` fuit dans le
  résultat de la fusion**, et fait planter `reseed` par traceback Python. Branche fautive :

  ```python
  elif s == b:
      plat[cle] = l      # l vaut MISSING quand la clé a été SUPPRIMÉE localement
  ```

  Cas : une clé présente dans la base et inchangée dans la semence, mais retirée du contrat local
  (retirer un `[fields.x]` chez soi est le geste que « le local gagne, aucun bruit » promet de
  respecter). `l is MISSING`, `s == b`, donc `plat[cle] = MISSING`, puis `emit` appelle
  `dump_value(MISSING)`. Constaté :

  ```
  listdir.items.SerialiseError: champ « type » : type object hors contrat — …
  code=1
  ```

  **Variante plus grave, côté gabarits** : un gabarit supprimé localement produit le même
  `MISSING`, mais il n'est découvert que dans `_ecrire` → `_poser` →
  `Path.write_text(MISSING)` → `TypeError`. À ce point, **la sauvegarde a été écrite et le contrat
  a déjà été réécrit** : la liste reste dans un état à moitié appliqué (contrat réémis,
  commentaires perdus, gabarit non reposé, `.list/semence/` resté périmé). C'est exactement ce que
  la docstring de `reseed` promet d'exclure — « Rien n'est jamais écrit à moitié ». État constaté
  après le crash :

  ```
  sup2/.list/backup/contract.toml
  sup2/.list/contract.toml              # réémis, commentaires perdus
  sup2/.list/semence/contract.toml      # non rafraîchi
  sup2/.list/templates/                 # vide
  ```

- **R3** — `scripts/listdir/provenance.py:441-447` — `emit` n'est protégé contre aucune
  `SerialiseError`. `parse_contract` tolère les clés de premier niveau inconnues (`validate` rend 0
  sur un contrat portant `seuil = 1.5`), mais `dump_value` ne sait pas les réécrire : `reseed` sort
  alors par traceback plutôt que par un échec nommé. Rien n'est écrit dans ce cas précis (le crash
  précède `_ecrire`), donc c'est un défaut de forme — mais c'est la même famille que R2, et le
  paquet se donne partout pour règle de nommer ses échecs.

- **R4** — `scripts/tests/test_entree_cli.py` — la seule vérification CLI ajoutée porte sur
  l'avertissement de provenance. Aucun test de bout en bout sur `reseed` : ni le code de retour du
  refus de nom (R1), ni le conflit, ni `--force`, ni `--dry-run`. Toute la confiance repose sur des
  tests de bibliothèque, qui ne voient pas la couche qui a perdu le code 2.

- **R5** — `scripts/listdir/commands/reseed.py:65-72` — quand la semence est désignée par
  l'`origin.def` de la liste (le cas courant, sans option), `expected_name` reste vide et le
  contrôle de discordance ne mord pas. Une définition rangée sous le répertoire `A` mais dont le
  contrat déclare `def = "B"` renomme alors silencieusement l'estampille de la liste en `B`
  (la clé `origin.def` locale égale la base, donc la semence gagne). Cas de bord ; le contrôle
  existe déjà, il ne s'applique simplement pas à cette voie.

- **Style** : conforme aux fichiers voisins — docstrings en capitales portant le pourquoi, messages
  en français avec guillemets typographiques, `Result` partout, aucun `print` hors `list-dir.py`,
  `noqa` motivé sur le `l` de la triade `b/l/s`. Rien à redire.

### Dette induite

- **R6** — `validate` résout désormais une définition à chaque appel
  (`provenance._peremption`). Sur une machine où le skill portant la définition n'est pas installé,
  **tout** `validate` d'une liste estampillée écrit une ligne sur stderr (« définition introuvable
  dans les quatre rangs — péremption invérifiable »). Le motif de vérification employé par ce dépôt
  lui-même — `ERR=$(list-dir validate "$L" 2>&1 >/dev/null); [ -z "$ERR" ]`, la boucle de l'étape 8
  du plan — devient donc faux-positif hors de la machine d'origine. Coût nommé, pas un défaut :
  mais il vaut d'être dit aux appelants de la chaîne dette.

- **R7** — `emit` réécrit `[sections."Constat"]` en `[sections.Constat]` et perd les commentaires.
  Conséquence : après un `reseed` non verbatim, `.list/contract.toml` ne peut plus jamais égaler
  `.list/semence/contract.toml`, et l'avertissement « modifié localement depuis le semis » devient
  permanent sur cette liste — y compris pour la part de l'écart qui n'est que de la mise en forme.
  Le comportement est correct au sens strict (la liste EST modifiée), mais l'avertissement perd de
  sa valeur de signal à mesure que les listes sont rattrapées.

- **R8** — `_poser` (`provenance.py:529`) n'efface jamais : un gabarit ne peut pas être retiré par
  un re-semis. C'est cohérent avec la règle « retirée de la semence, gardée sur place », mais rien
  ne le documente côté gabarits, là où la table du plan ne parle que de clés.

### Bloquants

- **R1** — critère de réussite explicite du brief et du suivi non atteint, vérifié par exécution :
  `init --def` sur un nom discordant sort en 1, pas en 2. La documentation livrée dans ce même
  chantier affirme le 2.
- **R2** — `reseed` plante par traceback sur une suppression locale, et laisse la liste à moitié
  écrite dans la variante gabarit. Un rattrapage interrompu au milieu est précisément le mode
  d'échec que ce dispositif existe pour supprimer.

## 2026-09-04 — clôture — `ddebb2b`

**Verdict** : RÉSERVES

Second audit de clôture, après le correctif `ddebb2b` (« traiter une absence comme une valeur dans
la fusion »). Le **diff entier** `master...peremption-contrat` a été rejugé, pas seulement les deux
bloquants du `5d4a4d8`.

### Vérifications exécutées

Depuis `skills/list-dir/`, sauf mention contraire.

- `uvx pytest scripts/tests -q` → **413 passés, 0 échec** (407 au `5d4a4d8` ; +6 tests apportés par
  le correctif)
- `uvx ruff check scripts` → **All checks passed!**
- `uvx ruff format --check --diff scripts` → 4 fichiers à reformater : `tests/test_contract.py`,
  `tests/test_items.py`, `tests/test_loader.py`, `tests/test_move.py`. **Aucun n'est dans la liste
  des fichiers touchés par la branche** (vérifié par `git diff --name-only master...`). Écart
  préexistant, annoncé dans le suivi.
- `uvx pyright` → **9 erreurs**, réparties sur `tests/conftest.py`, `test_contract.py`,
  `test_items.py`, `test_move.py`, `test_prefill.py` — **aucun fichier touché par la branche**.
  Huit sont des `pytest` non résolu dans l'environnement `uvx`, la neuvième est le défaut ancien de
  `test_prefill.py:127`. Écart préexistant, annoncé dans le suivi.
- Boucle de vérification de l'étape 8 (depuis la racine : `diff -r` semence, `diff` contrat,
  `validate` code + stderr sur les trois registres) → **aucune ligne d'écart** sur
  `technical-debt`, `technical-debt-solde`, `technical-debt-ecarte`.
- Étape 7 : `grep -rn "douze" skills/list-dir/SKILL.md` → sans résultat ;
  `grep -c "semence/" references/contrat-liste.md` → 5 ;
  `grep -n 'contenu \*\*est\*\* le futur' references/contrat-liste.md` → sans résultat.
  `list-dir help` annonce bien « Commandes génériques (13) », `reseed` compris.
- `git status --short` → arbre propre avant et après l'audit ; rien n'a été écrit hors du bac.
- Bac d'essai monté à la main (définition `monseed` au rang 1, versions 1 → 11) : `init --def`,
  `init` nu, `init --def` discordant, `validate` sur liste conforme / non conforme / gelée / sans
  `[origin]`, `reseed` nominal, en conflit, `--force`, `--dry-run`, adoption, suppression locale de
  clé et de gabarit, clé de premier niveau inconnue, définition renommée.

### Conformité à l'intention

Critère par critère, dans l'ordre du brief.

1. **`init --def` → `diff` muet, `[origin]` compris** : **atteint, vérifié**. `diff` muet entre
   `monseed/contract.toml` et `liste/.list/contract.toml` ; `diff -r` muet entre la définition et
   `.list/semence/`.
2. **`validate` sur une semence incrémentée : avertissement + code de retour conservé** :
   **atteint, vérifié**. Liste conforme → stdout `liste : 0 élément(s) conformes au contrat`,
   code 0, stderr `contrat périmé — semé en v1, « monseed » est en v2 ; …`. Liste non conforme et
   périmée → code 1, stdout **vide**, stderr portant le manquement, le bilan **et** l'avertissement.
   Les deux flux sont bien séparés.
3. **`frozen = true` tait la péremption, fait refuser `reseed`, `--force` passe outre** :
   **atteint, vérifié**. `validate` d'une liste gelée et périmée → aucun avertissement de
   péremption ; `reseed` → code 1, message nommé ; `reseed --force` → code 0, appliqué.
4. **`reseed` sauvegarde, injecte, sort non nul en nommant les clés sur conflit** : **atteint,
   vérifié**. Conflit → code 1, `fields.priorite.description — modifiée des deux côtés`, contrat
   **inchangé à l'octet** (sha256 identique avant/après) et `.list/backup/` **non créé**, avec
   comme sans `--force`.
5. **`pytest` passe ; `ruff` et `pyright` restent propres** : **atteint** pour `pytest` et
   `ruff check` ; **atteint au sens du suivi** pour `ruff format` et `pyright`, dont les écarts sont
   préexistants et cantonnés à des fichiers que la branche ne touche pas (vérifié fichier par
   fichier).
6. **`reseed --def <nom>` sur une liste sans `[origin]` : estampille + injection, refus sur
   conflit** : **atteint, vérifié**. Adoption d'une liste identique à `[origin]` près →
   `origin.def` et `origin.version` posés, `diff` avec la semence **muet octet pour octet**,
   commentaires de la semence préservés, `.list/semence/` créé ; `validate` ensuite muet, code 0.
7. **Squelette d'`init` sans `--def` porte `def = false`, et n'avertit jamais** : **atteint,
   vérifié** (`validate` code 0, stderr vide).
8. **`init --def <nom>` sur une semence qui déclare un autre nom échoue en code 2** : **atteint,
   vérifié — R1 du précédent audit est levé**. Constaté : `code=2`, message nommant les deux noms.
   Le correctif reporte `r.status` au lieu de retomber sur 1 (`commands/init.py:91`), et le
   test CLI `test_init_def_discordant_sort_en_code_2_depuis_la_cli` verrouille la couche par où la
   régression était passée.
9. **`validate` sans `[origin]` signale l'absence de provenance ; `def = false` la tait** :
   **atteint, vérifié**.
10. **Les trois définitions portent une version, les trois listes sont estampillées sans autre
    modification** : **atteint, vérifié**. `+4` lignes par contrat, la seule table `[origin]` ;
    aucun élément `*.md` touché.

**Hors-périmètre** : respecté. Aucun re-semis automatique ; `def` ne porte qu'un nom, jamais un
chemin ; `reseed` n'écrit que sous `.list/` ; hors `list-dir/*/contract.toml`, le seul fichier
d'`implementation-tracker` modifié est `references/dette.md`, que l'étape 7 prévoit.

**Signaux de dérive** : aucun matérialisé. `grep -rn "resolve("` ne montre que les appelants
autorisés — `commands/reseed.py:70`, `provenance.py:82` (l'avertissement) — plus `commands/init.py`
et `commands/contract.py`, préexistant et sur `--def` explicite. L'avertissement ne fait jamais
tomber un `validate` conforme (vérifié). `--force` ne tranche aucun conflit (vérifié). La copie
reste octet pour octet égale à sa semence après `init` (vérifié).

**Symptôme d'origine** : disparu, et vérifié de bout en bout dans le bac.

### Ce que le correctif a levé

- **R1 — levé.** Vérifié par exécution CLI : `code=2`.
- **R2 — levé.** Le sentinelle `MISSING` ne descend plus dans l'émetteur. Suppression locale d'une
  clé → `reseed` code 0, la clé reste absente, la version est reprise
  (`fields.priorite.description — supprimée localement, laissée supprimée`). Suppression locale
  d'un gabarit → code 0, le gabarit reste absent, aucune liste à moitié écrite. Le contrat produit
  est **stable** au re-semis suivant (sha256 identique).
- **R4 — partiellement levé.** Un test CLI de bout en bout existe désormais pour le code 2 d'`init`.
  Aucun n'a été ajouté pour `reseed` (conflit, `--force`, `--dry-run`) : la réserve subsiste, sans
  être bloquante.

### Ce qui subsiste du précédent audit

- **R3 — persiste.** `emit` n'est protégé contre aucune `SerialiseError`. Reproduit :
  `seuil = 1.5` ajouté au contrat local passe `validate` (code 0), puis `reseed` sort **par
  traceback** — `listdir.items.SerialiseError: champ « seuil » : type float hors contrat`. Rien
  n'est écrit (`emit` est évalué avant `_ecrire`, `.list/backup/` absent après le crash), donc c'est
  un défaut de forme — mais le paquet se donne partout pour règle de nommer ses échecs, et c'est la
  même famille que R2, qui vient d'être corrigée.
- **R5 — persiste, et est reproductible.** Sans option, `expected_name` reste vide et le contrôle
  de discordance ne mord pas. Une définition dont le contrat se renomme (`def = "monseed"` →
  `def = "renomme"`) fait **re-estampiller la liste** au nom nouveau. Constaté : après
  `list-dir reseed r5c`, `origin.def = "renomme"`, et le `validate` suivant rend
  `définition introuvable dans les quatre rangs — péremption invérifiable`. Atténuation par rapport
  au constat initial : le changement **est** listé (`origin.def — reprise de la semence`), il n'est
  donc pas silencieux — mais rien ne le distingue d'un changement anodin, et son effet est de
  couper la liste de sa semence. Même effet par `reseed --from <chemin>`, où la version peut en
  outre **reculer** (v9 → v2 constaté).
- **R6 — persiste.** `validate` résout une définition à chaque appel : hors de la machine où le
  skill est installé, tout `validate` d'une liste estampillée écrit une ligne sur stderr, et le
  motif `ERR=$(list-dir validate "$L" 2>&1 >/dev/null); [ -z "$ERR" ]` — celui de l'étape 8 —
  devient faux-positif. Coût nommé, pas un défaut.
- **R7 — persiste.** `emit` réécrit `[sections."Constat"]` en `[sections.Constat]` (équivalent en
  TOML, mais différent à l'octet) et perd les commentaires. Après un `reseed` non verbatim,
  `.list/contract.toml` ne peut plus égaler `.list/semence/contract.toml`, et l'avertissement
  « modifié localement depuis le semis » devient permanent. Constaté sur `sup2` et `sg`.
- **R8 — persiste.** `_poser` n'efface jamais : un gabarit ne peut pas être retiré par un re-semis,
  et rien ne le documente côté gabarits.

### Constats nouveaux

- **R9** — `scripts/listdir/provenance.py:498-521` (`_ecrire`) — **`.list/backup/` est écrasé par
  un `reseed` sans effet.** `_ecrire` est appelé quelle que soit la liste de changements, et sa
  première action est `shutil.rmtree(backup)` suivi d'une recopie du contrat **en vigueur**. Un
  second `reseed` — le geste naturel de qui doute que le premier ait pris — remplace donc la
  sauvegarde par une copie de l'état courant, et la marche arrière ne remonte plus nulle part.
  Constaté :

  ```
  $ list-dir reseed nop      # premier passage : backup = contrat d'avant, commentaires compris
  $ list-dir reseed nop
  nop : déjà à jour sur …/monseed
  $ diff nop/.list/backup/contract.toml nop/.list/contract.toml   # identiques
  ```

  La commande annonce « déjà à jour » : rien ne dit à l'utilisateur qu'elle vient de détruire la
  seule chose qui lui restait de l'état précédent. La docstring de `_ecrire` affirme pourtant que
  la sauvegarde « est la seule marche arrière ». Le remède tiendrait dans une garde — ne rien
  écrire quand la fusion ne change rien — mais **corriger n'est pas mon rôle**, et ce n'est ni un
  critère du brief ni un signal de dérive : réserve, pas bloquant.

- **R10** — `scripts/listdir/provenance.py:317-319` — **une suppression locale est reportée comme
  un « changement » à chaque re-semis, indéfiniment.** Le correctif de R2 ajoute
  `f"{cle} — supprimée localement, laissée supprimée"` à `changements`. Or cette ligne décrit un
  **état** qui persiste après le re-semis, pas une action : la semence continue de porter la clé,
  le local continue de ne pas la porter. Conséquences observées sur `sup2` :

  ```
  $ list-dir reseed sup2        # rien à faire, contrat déjà stable
    fields.priorite.description — supprimée localement, laissée supprimée
  sup2 : 1 changement(s) appliqués depuis …
  Le contrat a été réémis : les commentaires de la version précédente sont dans .list/backup/.
  $ list-dir reseed sup2 --dry-run
    fields.priorite.description — supprimée localement, laissée supprimée
  sup2 : 1 changement(s) seraient appliqués depuis …
  ```

  Une telle liste ne dira **jamais** « déjà à jour », `--dry-run` annonce en permanence un
  changement qui n'en est pas un, et le message « le contrat a été réémis » s'affiche sur un
  contrat identique à lui-même. C'est aussi le déclencheur le plus probable de R9, puisque
  `changements` n'est jamais vide sur ces listes. Le comportement de fusion, lui, est **correct** —
  seul le rapport ment.

- **Style** : conforme aux fichiers voisins. Docstrings en capitales portant le pourquoi, messages
  en français avec guillemets typographiques, `Result` partout, aucun `print` hors `list-dir.py`,
  `noqa` motivé sur le `l` de la triade `b/l/s`. Les commentaires ajoutés par le correctif suivent
  le même moule et disent le pourquoi, pas le quoi. Rien à redire.

### Dette induite

Inchangée depuis le précédent audit : R6 (`validate` résout une définition à chaque appel), R7
(l'avertissement « modifié localement » devient permanent après un re-semis non verbatim), R8 (un
gabarit ne se retire pas par re-semis, et ce n'est pas documenté). S'y ajoutent R9 et R10 ci-dessus,
tous deux confinés à `reseed` et sans effet sur les données d'une liste.

### Bloquants

Aucun. Les dix critères de réussite du brief sont atteints et vérifiés par exécution, le
hors-périmètre est intact, aucun signal de dérive n'est matérialisé, et aucune commande de
vérification n'est en échec.

Le verdict est `RÉSERVES` et non `FAVORABLE` parce que R3 (sortie par traceback sur un contrat que
`validate` accepte), R5 (re-estampillage vers un nom que plus rien ne résout) et R9 (destruction
silencieuse de la seule marche arrière) sont des modes d'échec que l'utilisateur doit connaître
avant de clore — aucun n'est couvert par un critère, aucun ne rend le résultat inutilisable.

## 2026-09-04 — clôture — `3a86900`

**Verdict** : RÉSERVES

Troisième audit de clôture, après les deux commits de correctif `acf28e5` (« ne rien écrire quand
il n'y a rien à changer ») et `3a86900` (« dire ce qu'un re-semis sans effet ne fait pas »). Le
**diff entier** `master...peremption-contrat` a été rejugé, pas seulement le correctif. R3, R4, R5,
R6 et R8 sont vérifiés persistants — l'utilisateur les a arbitrés vers le registre de dette, ils
sont rappelés ici pour mémoire et non recomptés comme neufs.

### Vérifications exécutées

Depuis `skills/list-dir/`, sauf mention contraire.

- `uvx pytest scripts/tests -q` → **418 passés, 0 échec** (413 au `ddebb2b`, 407 au `5d4a4d8`)
- `uvx ruff check scripts` → **All checks passed!**
- `uvx ruff format --check scripts` → **4 fichiers seraient reformatés**. Chaque fichier `.py`
  touché par la branche a été repassé un par un à `ruff format --check` : **aucun n'est signalé**.
  Écart préexistant, annoncé dans le suivi.
- `uvx pyright` → **9 erreurs**, sur `tests/conftest.py`, `test_contract.py`, `test_items.py`,
  `test_move.py`, `test_prefill.py` — `git diff --name-only master...` ne contient aucun de ces
  fichiers. Huit sont `pytest` non résolu dans l'environnement `uvx`, la neuvième est le défaut
  ancien de `test_prefill.py:127`. Écart préexistant, annoncé dans le suivi.
- Boucle de vérification de l'étape 8 (depuis la racine : `diff -r` semence, `diff` contrat,
  `validate` code + stderr sur les trois registres) → **aucune ligne d'écart**, code 0, stderr vide
  sur `technical-debt`, `technical-debt-solde`, `technical-debt-ecarte`.
- Étape 7 : `grep -rn "douze" skills/list-dir/SKILL.md` → sans résultat ;
  `grep -c "semence/" references/contrat-liste.md` → 5 ;
  `grep -n 'contenu \*\*est\*\* le futur' references/contrat-liste.md` → sans résultat ;
  `list-dir help` annonce « Commandes génériques (13) », `reseed` compris.
- `git check-ignore -v` sur un `.list/backup/contract.toml` → couvert par `.gitignore:8`.
- `git status --short` → arbre propre avant et après l'audit ; tout le bac d'essai est sous `/tmp`.
- Bac d'essai monté à la main (rang 1, définition `monseed`, versions 1 → 8) : `init --def`, `init`
  nu, `init --def` discordant, `validate` sur liste conforme / non conforme / gelée / sans
  `[origin]` / à élément illisible, `reseed` nominal, second `reseed`, conflit avec et sans
  `--force`, `--dry-run`, adoption d'une liste antérieure, clé ajoutée localement, commentaire
  local, clé de premier niveau inconnue, définition renommée, gabarit retiré de la semence, titre
  de section porteur d'un guillemet droit.

### Conformité à l'intention

Critère par critère, dans l'ordre du brief. Tous vérifiés par exécution sur le bac.

1. **`init --def` → `diff` muet, `[origin]` compris** : **atteint**. `diff` muet entre
   `monseed/contract.toml` et `liste/.list/contract.toml` ; `diff -r` muet entre la définition et
   `.list/semence/`.
2. **`validate` sur une semence incrémentée : avertissement + code de retour conservé** :
   **atteint**. Liste conforme → stdout `liste : 0 élément(s) conformes au contrat`, code 0, stderr
   `contrat périmé — semé en v1, « monseed » est en v2 ; …`. Liste non conforme → code 1, stdout
   vide, stderr portant le manquement, le bilan **et** l'avertissement. Une réserve borde ce
   critère sur un troisième cas, l'élément illisible : voir **R11**.
3. **`frozen = true` tait la péremption, fait refuser `reseed`, `--force` passe outre** :
   **atteint**. `validate` d'une liste gelée et périmée → stderr vide, code 0 ; `reseed` → code 1,
   message nommé ; `reseed --force` → code 0, appliqué, et `origin.frozen` conservé au passage
   (`origin.frozen — retirée de la semence, gardée sur place`).
4. **`reseed` sauvegarde, injecte, sort non nul en nommant les clés sur conflit** : **atteint**.
   Conflit → code 1, `fields.titre.description — modifiée des deux côtés`, contrat **inchangé à
   l'octet** (sha256 identique) et `.list/backup/` **non créé**, avec comme sans `--force`.
5. **`pytest` passe ; `ruff` et `pyright` restent propres** : **atteint** pour `pytest` et
   `ruff check` ; **atteint au sens du suivi** pour `ruff format` et `pyright`, dont les écarts sont
   préexistants et ne touchent aucun fichier de la branche (vérifié fichier par fichier).
6. **`reseed --def <nom>` sur une liste sans `[origin]` : estampille + injection, refus sur
   conflit** : **atteint**. Adoption d'une liste antérieure identique à `[origin]` près →
   `origin.def` et `origin.version` posés, `diff` avec la semence **muet**, commentaires de la
   semence préservés, `.list/semence/` créé, `validate` ensuite muet et code 0.
7. **Squelette d'`init` sans `--def` porte `def = false`, et n'avertit jamais** : **atteint**
   (`[origin]\ndef = false` dans le squelette ; `validate` code 0, stderr vide).
8. **`init --def <nom>` sur une semence qui déclare un autre nom échoue en code 2** : **atteint**.
   Constaté `code=2`, message nommant les deux noms. R1 reste levé.
9. **`validate` sans `[origin]` signale l'absence de provenance ; `def = false` la tait** :
   **atteint**, message d'adoption complet et geste rappelé.
10. **Les trois définitions portent une version, les trois listes sont estampillées sans autre
    modification** : **atteint**. `+4` lignes par contrat, la seule table `[origin]` ; aucun
    élément `*.md` touché ; `.list/semence/` versionnées, `.list/backup/` ignoré.

**Hors-périmètre** : respecté. Aucun re-semis automatique ; `def` ne porte qu'un nom, jamais un
chemin ; `reseed` n'écrit que sous `.list/` ; hors `list-dir/*/contract.toml`, le seul fichier
d'`implementation-tracker` modifié est `references/dette.md`, que l'étape 7 prévoit.

**Signaux de dérive** : aucun matérialisé. `grep -rn "resolve("` ne montre que les appelants
autorisés — `provenance.py:82` (l'avertissement), `commands/reseed.py:70` — plus `commands/init.py`
et `commands/contract.py`, préexistant et sur `--def` explicite. L'avertissement ne fait jamais
tomber un `validate` conforme. `--force` ne tranche aucun conflit (vérifié : code 1 avec `--force`,
contrat inchangé). La copie reste octet pour octet égale à sa semence après `init`.

**Symptôme d'origine** : disparu, vérifié de bout en bout.

### Ce que le correctif a levé

- **R7 — levé.** `_differe` compare désormais le contrat par son **contenu** (`flatten` du TOML) et
  les gabarits à l'octet, et `flatten` cite systématiquement les titres de section
  (`sections."Constat"`), si bien qu'un contrat réémis n'est plus déclaré « modifié localement »
  pour une pure question d'écriture. Vérifié : après un `reseed` non verbatim, `validate` est muet
  là où il avertissait en permanence. Deux tests verrouillent la règle dans les deux sens
  (`test_une_difference_de_pure_forme_ne_se_dit_pas_modifiee`,
  `test_une_divergence_de_contenu_se_dit_toujours`).
- **R9 — levé.** `_a_ecrire` garde `_ecrire` sur les trois cibles. Constaté : un second `reseed`
  laisse `.list/backup/contract.toml` **au même sha256** et répond « déjà à jour, rien à faire ».
  Test `test_re_semis_sans_effet_ne_touche_pas_a_la_sauvegarde`.
- **R10 — levé sur son cas.** Une suppression locale n'est plus rapportée comme un changement, et
  la liste finit par dire « déjà à jour ». Test
  `test_une_liste_a_suppression_locale_finit_par_dire_qu_elle_est_a_jour`. Le motif subsiste pour
  une autre forme de divergence locale : voir **R12**.

### Ce qui subsiste, arbitré vers le registre de dette

Vérifiés persistants par exécution, non recomptés comme bloquants — l'utilisateur les a tranchés.

- **R3** — `emit` n'est protégé contre aucune `SerialiseError`. Reproduit : `seuil = 1.5` ajouté au
  contrat local passe `validate` (code 0), puis `reseed` sort **par traceback**
  (`listdir.items.SerialiseError: champ « seuil » : type float hors contrat`). Rien n'est écrit.
- **R4** — aucun test CLI de bout en bout sur `reseed` (conflit, `--force`, `--dry-run`, code 2 du
  nom discordant). Seul `init` en a un. Inchangé depuis le `ddebb2b`.
- **R5** — sans option, `expected_name` reste vide et le contrôle de discordance ne mord pas.
  Reproduit : une définition qui se renomme (`def = "monseed"` → `def = "renomme"`) fait
  **re-estampiller** la liste au nom nouveau (`origin.def — reprise de la semence`), et le
  `validate` suivant rend `définition introuvable dans les quatre rangs`.
- **R6** — `validate` résout une définition à chaque appel : hors de la machine où le skill est
  installé, toute liste estampillée écrit une ligne sur stderr, et le motif
  `ERR=$(list-dir validate "$L" 2>&1 >/dev/null); [ -z "$ERR" ]` — celui de l'étape 8 — devient
  faux-positif. Constaté incidemment en reproduisant R5.
- **R8** — `_poser` n'efface jamais : un gabarit retiré de la semence reste sur place. Reproduit :
  `gabarit note.md — retirée de la semence, gardée sur place`, fichier toujours là. Cohérent avec
  la règle des clés, mais toujours non documenté côté gabarits.

### Constats nouveaux

- **R11** — `scripts/listdir/commands/validate.py:45` — **les avertissements de provenance sautent
  quand un élément est illisible.** `warnings()` n'est appelé qu'après le `if not r: return
  utils.fail(r.message)` de `lst.validate()`. Un élément sans front matter fait donc sortir
  `validate` en 1 **sans un mot sur la péremption**, là où un simple manquement l'affiche.
  Constaté sur une liste périmée (semée en v2, semence en v3) :

  ```
  $ list-dir validate liste       # élément conforme au parseur, champ manquant
  liste/e2.md: champ « titre » — manquant
  liste : 1 manquement
  liste : contrat périmé — semé en v2, « monseed » est en v3 ; …    ← présent
  code=1
  $ list-dir validate liste       # élément sans front matter
  liste/e3.md: front matter absent — la première ligne doit être « +++ »
  code=1                                                             ← avertissement absent
  ```

  Le critère 2 du brief dit « que les éléments soient conformes ou non » ; un élément illisible est
  un troisième état, que ni le brief ni le plan ne nomment. Je ne le compte donc pas comme critère
  manqué — mais c'est précisément l'état où l'on cherche pourquoi une liste ne passe plus, et où la
  péremption est l'explication la plus probable.

- **R12** — `scripts/listdir/provenance.py:352-357` — **le motif de R10 subsiste pour une clé
  ajoutée localement**, et le rapport d'un re-semis réel devient indiscernable d'un `--dry-run`. Le
  correctif a fait taire la branche `s == b` (le local a bougé seul), mais pas la branche
  `s is MISSING` (clé absente de la semence), qui décrit elle aussi un **état durable** :

  ```
  $ list-dir reseed ajout      # premier passage : le contrat est réémis
    fields.local.type — retirée de la semence, gardée sur place
    …
  ajout : 3 changement(s) appliqués depuis …/monseed
  $ list-dir reseed ajout      # rien à écrire, et pourtant :
    fields.local.type — retirée de la semence, gardée sur place
    …
  ajout : 3 changement(s) seraient appliqués depuis …/monseed
  ```

  Deux choses à part l'une de l'autre. D'abord la phrase est fausse : un champ **ajouté** localement
  n'a jamais été « retiré de la semence ». Ensuite, depuis la garde d'`_a_ecrire`, un `reseed` réel
  qui n'écrit rien rend `ecrit=False`, et `commands/reseed.py:99` en tire le verbe **« seraient
  appliqués »** — le mot du `--dry-run`, sur un passage qui n'en est pas un. Une telle liste ne dira
  jamais « déjà à jour ».

- **R13** — `scripts/listdir/provenance.py:496` + `commands/reseed.py:95` — **un `reseed` qui
  annonce « déjà à jour » peut avoir réécrit le contrat et perdu un commentaire local.** Quand la
  divergence locale est de pure forme, `changements` est vide mais `_a_ecrire` est vrai : le contrat
  est remplacé par la semence verbatim, et le message ne dit rien. La note « le contrat a été
  réémis : les commentaires … sont dans `.list/backup/` » n'est écrite que dans la branche
  `changements` non vide. Constaté :

  ```
  $ printf '\n# note locale précieuse\n' >> com/.list/contract.toml
  $ list-dir validate com     # depuis le correctif R7, plus aucun avertissement
  com : 0 élément(s) conformes au contrat
  $ list-dir reseed com
  com : déjà à jour sur …/monseed
  $ grep -c "note locale" com/.list/contract.toml   → 0    (récupérable dans .list/backup/)
  ```

  Aucune donnée n'est perdue sans recours, et le choix de comparer le contenu plutôt que les octets
  est assumé et documenté (`references/contrat-liste.md`). Mais la conjonction est neuve : depuis
  `3a86900`, un commentaire local n'est **ni signalé par `validate`, ni annoncé par `reseed`**, et
  disparaît sous un message qui dit qu'il n'y avait rien à faire.

- **R14** — `scripts/listdir/provenance.py:250` et `_cle` (ligne 267) — **un titre de section
  portant un guillemet droit fait écrire par `reseed` un contrat que plus rien ne relit**, en
  sortant en **code 0**. Le nom est enrobé par `f'"{nom}"'` sans échappement, et l'émetteur produit
  `[sections."Un " ici"]`. `parse_contract` accepte pourtant ce titre à l'entrée. Constaté de bout
  en bout :

  ```
  $ list-dir reseed q
  … 3 changement(s) appliqués depuis …/monseed
  code=0
  $ list-dir validate q
  q/.list/contract.toml: TOML invalide — Expected ']' at the end of a table declaration (ligne 17)
  code=1
  ```

  C'est la famille de R3, mais un cran plus haut : R3 sort par traceback **avant** d'écrire, celui-ci
  **écrit** et se déclare satisfait. La liste est inutilisable jusqu'à restauration depuis
  `.list/backup/`. Le défaut préexiste au correctif (`_cle` enrobait déjà sans échapper) et il ne
  mord que sur un titre contenant `"` — aucune des trois listes de ce dépôt n'est dans ce cas.
  C'est le constat le plus lourd de cet audit, et celui sur lequel j'ai hésité à basculer le verdict.

**Style** : conforme aux fichiers voisins. Docstrings en capitales portant le pourquoi, messages en
français avec guillemets typographiques, `Result` partout, aucun `print` hors `list-dir.py`, `noqa`
motivé sur la triade `b/l/s`. Les commentaires des deux derniers commits disent le pourquoi et le
mode d'échec qu'ils suppriment, dans le même moule. La documentation (`contrat-liste.md`,
`SKILL.md`, `dette.md`) suit le correctif — la règle « le contenu, jamais les octets » et la garde
de la sauvegarde y sont écrites. Rien à redire.

**Suivi** : au commit audité, `.claude/implementation/peremption-contrat.md` porte encore
`statut: en-cours`, `Dernier audit : ddebb2b`, et une « prochaine action » d'arbitrage que
l'utilisateur a depuis tranchée ; ni `acf28e5` ni `3a86900` n'y sont journalisés. Observation, pas
constat de code : c'est le geste de clôture qui les y écrira.

### Dette induite

Inchangée pour R6 (`validate` résout une définition à chaque appel) et R8 (un gabarit ne se retire
pas par re-semis, non documenté). R7 n'est plus une dette : il est corrigé, au prix — assumé et
écrit — qu'une divergence de pure forme cesse d'être visible, ce que R13 décrit. S'y ajoutent R12
(un rapport qui décrit un état comme un changement, et le verbe du `--dry-run` sur un passage réel)
et R14 (un contrat réémis illisible sur un titre de section cité).

### Bloquants

Aucun. Les dix critères de réussite du brief sont atteints et vérifiés par exécution, le
hors-périmètre est intact, aucun signal de dérive n'est matérialisé, aucune commande de vérification
n'est en échec, et les trois réserves traitées (R7, R9, R10) le sont réellement, tests à l'appui.

Le verdict est `RÉSERVES` et non `FAVORABLE` parce que R14 (un `reseed` en code 0 qui rend une liste
illisible), R13 (une perte de commentaire silencieuse sous un « déjà à jour ») et R11 (la péremption
tue quand un élément est illisible) sont des modes d'échec que l'utilisateur doit connaître avant de
clore, en plus des cinq réserves déjà arbitrées. J'ai pesé `DÉFAVORABLE` pour R14 : je l'écarte
parce qu'aucun critère ni signal de dérive ne le couvre, qu'il préexiste au correctif de ce tour,
qu'il ne mord que sur un titre de section contenant un guillemet droit — aucune liste de ce dépôt —
et que `.list/backup/` en garde le recours. Si l'utilisateur veut un `FAVORABLE`, R14 est le seul
constat que je tiens pour incontournable.

## 2026-09-04 — clôture — `b58823f`

**Verdict** : RÉSERVES

Quatrième passage. Le diff entier a été rejugé, pas seulement le dernier commit.

### Vérifications exécutées

Depuis `skills/list-dir/`, sauf mention contraire.

- `uvx pytest scripts/tests -q` → **422 passés, 0 échec** (407 au précédent audit, 346 avant chantier)
- `uvx ruff check scripts` → **All checks passed!**
- `uvx ruff format --check --diff scripts` → 4 fichiers à reformater : `tests/test_contract.py`,
  `tests/test_items.py`, `tests/test_loader.py`, `tests/test_move.py` — **aucun touché par la
  branche**, écart préexistant et annoncé dans le suivi
- `uvx pyright` → **9 erreurs**, toutes dans `tests/conftest.py`, `test_contract.py`,
  `test_items.py`, `test_move.py`, `test_prefill.py` — **aucun fichier du chantier n'en produit**.
  Écart préexistant et annoncé.
- Étape 7 (racine du dépôt) : `grep -rn "douze" skills/list-dir/SKILL.md` → sans résultat ;
  `grep -c "semence/" references/contrat-liste.md` → 5 ;
  `grep -n "contenu \*\*est\*\* le futur" references/contrat-liste.md` → sans résultat
- Étape 8 (racine du dépôt), boucle complète du plan sur les trois registres → **aucune ligne
  d'écart, code 0, stderr vide**
- `git check-ignore -v .claude/implementation/todo/technical-debt/.list/backup/x` →
  `.gitignore:8:**/.list/backup/`
- Bac d'essai remonté à la main (projet jetable, définition `monseed` au rang 1, versions 2 → 11) :
  `init --def`, `init` nu, `init --def` discordant, `validate` sur liste conforme / à manquement /
  à élément illisible / sans `[origin]` / `frozen`, `reseed` nominal, répété, en conflit, `--force`,
  `--dry-run`, adoption verbatim et adoption avec injection, gabarit modifié puis retiré côté
  semence. Sorties reportées ci-dessous.

### Conformité à l'intention

Les dix critères du brief, un par un.

1. **`init --def` → `diff` muet, `[origin]` compris** : **atteint, vérifié**. `diff` muet sur la
   définition d'essai comme sur les trois du dépôt ; `.list/semence/` est `diff -r`-identique.
2. **`validate` sur liste périmée : avertissement et code de retour conservé** : **atteint,
   vérifié**, et sur les trois états cette fois — conforme (code 0 + avertissement sur stderr),
   à manquement (code 1 + avertissement), **élément illisible** (code 1 + avertissement). Ce
   troisième état était R11 ; il est levé.
3. **`frozen = true` tait la péremption et fait refuser `reseed` ; `--force` passe outre** :
   **atteint, vérifié**. Constaté : `validate` muet malgré v3 → v5 ; `reseed` code 1 avec le
   message nommant `--force` ; `reseed --force` code 0 ; `frozen = true` conservé après coup.
4. **`reseed` sauvegarde, injecte, et sort non nul en nommant les clés sur conflit** : **atteint,
   vérifié**. Conflit → `code=1`, `fields.categorie.description — modifiée des deux côtés`, contrat
   inchangé à l'octet, **`.list/backup/` non créé** — rien n'a été écrit. Idem avec `--force`.
5. **`pytest` passe ; `ruff` et `pyright` restent propres** : **atteint** sur `pytest` et
   `ruff check` ; **atteint sur le périmètre du chantier** pour `ruff format` et `pyright`, dont
   les écarts sont tous dans des fichiers que la branche ne touche pas et étaient déjà là.
6. **`reseed --def` sur liste sans `[origin]` : estampille + apports, refus sur conflit** :
   **atteint, vérifié**. Adoption avec injection : `origin.def`/`origin.version` posées, champ de
   la semence injecté, champ local conservé, `.list/semence/` créé. Adoption d'une liste identique
   à sa semence à `[origin]` près : recopie **verbatim**, `diff` muet. Adoption d'une liste
   divergente sur les mêmes clés : `code=1`, clés nommées, rien écrit.
7. **Squelette d'`init` sans `--def` porte `def = false`** : **atteint, vérifié** — `[origin]` puis
   `def = false` présents, `validate` muet.
8. **`init --def <nom>` sur une semence déclarant un autre nom → code 2** : **atteint, vérifié**.
   Constaté `code=2`, message nommant les deux noms. R1 reste levé.
9. **`validate` sans `[origin]` signale l'absence de provenance ; `def = false` la tait** :
   **atteint, vérifié**, texte du message porteur du geste d'adoption.
10. **Les trois définitions versionnées, les trois listes estampillées sans autre modification** :
    **atteint, vérifié** par la boucle de l'étape 8 — `diff -r` semence, `diff` contrat, `validate`
    code 0 et stderr vide sur les trois.

**Hors-périmètre** : respecté. Aucun re-semis automatique (vérifié : un `validate` n'écrit rien) ;
aucune liste ne référence sa semence — `def` nomme, `reseed` rerésout ; `reseed` ne touche aucun
`*.md` d'élément (seuls contrat, gabarits, `.list/semence/` et `.list/backup/` bougent) ;
`debt-review`, `road-map` et le reste du pipeline sont hors du diff.

**Signaux de dérive** : aucun matérialisé. Seuls `reseed` et l'avertissement de `validate`
résolvent une définition ; l'avertissement de péremption n'a jamais fait tomber un `validate`
conforme ; aucun conflit n'est résolu tout seul, `--force` compris ; aucune écriture dans une liste
`frozen` sans `--force` ; la copie reste octet pour octet sa semence à l'`init` et sur un re-semis
verbatim.

**Symptôme d'origine** : **disparu**. Une semence incrémentée est désormais annoncée par
`validate`, avec la version de départ, la version courante et le geste de rattrapage.

### Réserves du tour précédent

- **R11 — levé.** `commands/validate.py:44-51` calcule les avertissements **avant** le premier
  `return`. Constaté : sur une liste périmée dont un élément n'a pas de front matter,
  `code=1`, stdout vide, stderr porteur du manquement **et** de la péremption.
- **R12 — levé.** `provenance.py` ne rapporte plus « retirée de la semence ». Un deuxième et un
  troisième `reseed` sur la même liste rendent tous deux
  `liste : déjà à jour, rien à faire sur …` — le verbe du `--dry-run` a disparu du passage réel,
  et `.list/backup/` conserve bien l'état d'avant le premier re-semis (R9 reste levé).
- **R13 — levé.** `_texte_differe` décide de l'écriture sur le **contenu**. Constaté : un
  commentaire ajouté à la main dans `liste/.list/contract.toml`, puis `list-dir reseed liste`
  → « déjà à jour, rien à faire », et le commentaire est **toujours là**.
- **R14 — levé sur son cas.** `_titre` échappe désormais la barre inverse et le guillemet droit,
  puis applique `items.ESCAPES`. Constaté de bout en bout sur une section dont le titre porte un
  guillemet : `reseed` code 0, contrat réémis avec le titre échappé, `validate` suivant code 0.
  La famille du défaut, elle, n'est pas entièrement fermée : voir **R15**.

### Réserves arbitrées vers le registre de dette

Vérifiées persistantes à ce commit, conformément à l'arbitrage de l'utilisateur.

- **R3** — `emit` n'est protégé contre aucune `SerialiseError`. Reproduit : un `seuil = 1.5` ajouté
  au contrat local passe `validate` (code 0), puis `reseed` sort **par traceback** —
  `listdir.items.SerialiseError: champ « seuil » : type float hors contrat`. Rien n'est écrit
  (`.list/backup/` absent après le crash) ; c'est un défaut de forme, dans un paquet qui se donne
  pour règle de nommer ses échecs.
- **R4** — la couverture CLI de `reseed` (conflit, `--force`, `--dry-run`) reste absente : ces
  chemins ne sont testés qu'au niveau bibliothèque. Vérifié par lecture de `test_entree_cli.py`.
- **R5** — une définition qui se renomme fait **re-estampiller la liste** au nom nouveau, sans que
  rien ne distingue ce changement d'un autre. Reproduit : après `reseed`, `origin.def = "renomme"`,
  puis `validate` rend `définition introuvable dans les quatre rangs — péremption invérifiable`.
- **R6** — `validate` résout une définition à chaque appel : hors de la machine où le skill est
  installé, toute liste estampillée écrit une ligne sur stderr, et le motif de l'étape 8
  (`ERR=$(list-dir validate … 2>&1 >/dev/null); [ -z "$ERR" ]`) devient faux-positif.
- **R8** — `_poser` n'efface jamais : un gabarit retiré de la semence reste en place. Reproduit —
  `note.md` supprimé de la définition, `reseed` répond « déjà à jour », le fichier est toujours là.
  Atténuation constatée depuis le dernier tour : `validate` le **dit** désormais
  (`r8/.list/templates/note.md : ajouté depuis le semis`) ; la doc, elle, ne le dit toujours pas
  côté gabarits.

### Qualité du code

- **R15** — `scripts/listdir/provenance.py`, `_titre` — **le mode d'échec de R14 subsiste pour un
  caractère de contrôle** : `reseed` écrit un contrat que `tomllib` refuse, et rend **0**. `_titre`
  échappe la barre inverse, le guillemet droit et les cinq entrées d'`ESCAPES`, mais ne refuse pas
  les autres caractères de contrôle, là où `items.dump_value` lève une `SerialiseError` pour
  exactement ce cas — la docstring de `_titre` dit pourtant emprunter à `dump_value` « plutôt que
  recopier ». Constaté de bout en bout sur une semence dont un titre de section porte un `U+0007`
  écrit en échappée TOML, titre que `parse_contract` accepte :

  ```
  $ list-dir reseed ctl
  ctl : 1 changement(s) appliqués depuis …/ctlseed
  code=0
  $ list-dir validate ctl
  ctl/.list/contract.toml: TOML invalide — Illegal character '\x07' (at line 13, column 19)
  code=1
  ```

  Le même défaut vaut pour un **nom de champ** (`_cle` retombe sur `_titre`) : une définition
  portant un nom de champ à caractère de contrôle est semée sans un mot. Portée réelle très
  étroite — il faut une échappée `\u00XX` de contrôle écrite à la main dans un contrat — et
  `.list/backup/` garde le recours. C'est néanmoins le seul endroit du chantier où une écriture
  détruit un fichier sous un code de succès, ce que le paquet se donne partout pour règle
  d'interdire.

- **Style** : conforme. Docstrings en capitales portant le pourquoi et le mode d'échec supprimé,
  messages en français à guillemets typographiques, `Result` partout, aucun `print` hors
  `list-dir.py`, tests nommés par la phrase qu'ils défendent et référencés à leur réserve
  (`R11`…`R14`). `_texte_differe` et `_titre` suivent le moule des voisins. Le message du dernier
  commit dit ce qu'il supprime, dans le même moule que les précédents. Rien d'autre à redire.

- **Documentation** : `contrat-liste.md` a suivi les deux correctifs — « seul ce que le re-semis
  fait est rapporté » et « un commentaire ajouté sur place ne fait pas réécrire le contrat » sont
  écrits, la table de fusion est à jour. `SKILL.md` compte treize commandes. `dette.md` porte le
  geste de rattrapage.

- **Suivi** : au commit audité, `.claude/implementation/peremption-contrat.md` porte encore
  `statut: en-cours`, `Dernier audit : 3a86900` et une « prochaine action » d'arbitrage déjà
  tranchée ; `b58823f` n'y est pas journalisé. Observation, pas constat de code : c'est le geste
  de clôture qui l'y écrira, avec le versement de R3, R4, R5, R6 et R8 au registre de dette.

### Dette induite

Inchangée : R3, R4, R5, R6 et R8, arbitrées et destinées au registre. R12 et R13 ne sont plus des
dettes, ils sont corrigés. S'y ajoute **R15**, qui n'est pas une dette assumée mais un défaut
résiduel : c'est le seul constat neuf de ce tour.

### Bloquants

Aucun. Les dix critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
intact, aucun signal de dérive n'est matérialisé, aucune commande de vérification n'est en échec,
et les quatre réserves traitées (R11 à R14) le sont réellement, tests à l'appui.

Le verdict est `RÉSERVES` et non `FAVORABLE` à cause de **R15** seul : le correctif de R14 a fermé
le guillemet, pas la famille, et un `reseed` peut encore rendre 0 sur un contrat que plus rien ne
relit. J'ai pesé `DÉFAVORABLE` et l'écarte pour les raisons qui valaient déjà pour R14 — aucun
critère ni signal de dérive ne le couvre, le défaut préexiste à ce tour, il ne mord sur aucune liste
de ce dépôt, et `.list/backup/` en garde le recours. Une garde de trois lignes dans `_titre`, sur le
modèle du refus de caractère de contrôle de `dump_value`, lèverait la réserve.

---

## 2026-09-04 — clôture — `fd2178c`

**Verdict** : RÉSERVES

Cinquième passage. Le diff entier a été rejugé, pas seulement le dernier commit, conformément à la
demande. R1, R2, R7, R9 à R15 sont annoncés traités ; R4, R5, R6 et R8 sont arbitrés vers le
registre de dette et vérifiés persistants.

### Vérifications exécutées

Depuis `skills/list-dir/`, sauf mention contraire. Arbre de travail propre à `fd2178c`.

- `uvx pytest scripts/tests -q` → **423 passés, 0 échec** (422 au tour précédent, 346 avant chantier)
- `uvx ruff check scripts` → **All checks passed!**
- `uvx ruff format --check scripts` → **4 fichiers à reformater**, tous hors branche
  (`tests/test_contract.py`, `test_items.py`, `test_loader.py`, `test_move.py`) — écart
  préexistant, annoncé dans le suivi
- `uvx pyright` → **9 erreurs**, toutes dans `tests/conftest.py`, `test_contract.py`,
  `test_items.py`, `test_move.py`, `test_prefill.py` — **aucun fichier du chantier n'en produit**.
  Écart préexistant, annoncé
- Étape 7 (racine) : `grep -rn "douze" skills/list-dir/SKILL.md` → sans résultat ;
  `grep -c "semence/" references/contrat-liste.md` → 5 ; `grep -n "contenu **est** le futur"` →
  sans résultat ; `SKILL.md` dit « treize commandes » aux lignes 5 et 42
- Étape 8 (racine), boucle complète du plan sur les trois registres → **aucune ligne d'écart,
  code 0, stderr vide sur les trois**
- Bac d'essai remonté à la main (projet jetable, définitions `monseed`, `alias`, `ctlseed`,
  `cle2`, `leafseed`, `dotseed`, versions 2 → 5) : `init --def`, `init` nu, `init --def` sur nom
  discordant, `validate` périmé / sans `[origin]` / `frozen`, `reseed` nominal, en conflit,
  `--force`, `--dry-run`, adoption verbatim, R3, R15 et leurs variantes. Sorties ci-dessous.

### Conformité à l'intention

Les dix critères du brief, un par un, tous réexécutés à ce commit.

1. **`init --def` → `diff` muet, `[origin]` compris** : **atteint, vérifié**. `diff` muet entre la
   définition d'essai et `liste/.list/contract.toml` ; `diff -r` muet entre la définition et
   `.list/semence/`. Idem sur les trois registres du dépôt.
2. **`validate` sur liste périmée : avertissement, code de retour conservé** : **atteint,
   vérifié**. Sur liste conforme : `code=0`, stdout `liste : 0 élément(s) conformes au contrat`,
   stderr `liste : contrat périmé — semé en v2, « monseed » est en v5 ; « list-dir reseed liste »
   rattrape`. Le canal est bien stderr, stdout reste propre.
3. **`frozen = true` tait la péremption, fait refuser `reseed`, `--force` passe outre** :
   **atteint, vérifié**. `validate gel` → code 0 **sans avertissement** malgré v2 → v5 ;
   `reseed gel` → code 1, message nommant `--force` ; `reseed gel --force` → code 0 ;
   `frozen = true` conservé après coup.
4. **`reseed` sauvegarde, injecte, sort non nul en nommant les clés sur conflit** : **atteint,
   vérifié**. Conflit → `code=1`, `fields.categorie.description — modifiée des deux côtés`,
   contrat **intact à l'octet**, `.list/backup/` **non créé**. Identique avec `--force`.
5. **`pytest` passe ; `ruff` et `pyright` restent propres** : **atteint** sur `pytest` et
   `ruff check` ; **atteint sur le périmètre du chantier** pour `ruff format` et `pyright`, dont
   les neuf et quatre écarts sont tous dans des fichiers que la branche ne touche pas.
6. **`reseed --def` sur liste sans `[origin]` : estampille + apports, refus sur conflit** :
   **atteint, vérifié**. Adoption verbatim d'une liste égale à sa semence à `[origin]` près :
   `code=0`, trois changements (`origin.def`, `origin.version`, gabarit), **`diff` muet avec la
   semence** après coup, `.list/semence/` créé, `validate` suivant muet. Adoption d'une liste
   divergente sur une clé que la semence a aussi bougée : `code=1`, clé nommée, rien écrit.
7. **Squelette d'`init` sans `--def` porte `def = false`** : **atteint, vérifié** —
   `[origin]` / `def = false` présents, `validate` muet.
8. **`init --def <nom>` sur une semence déclarant un autre nom → code 2** : **atteint, vérifié**.
   `init discord --def alias` → `code=2`, message nommant les deux noms.
9. **`validate` sans `[origin]` signale l'absence de provenance ; `def = false` la tait** :
   **atteint, vérifié**, le message porte le geste d'adoption et l'échappatoire `def = false`.
10. **Les trois définitions versionnées, les trois listes estampillées sans autre modification** :
    **atteint, vérifié** par la boucle de l'étape 8, qui n'écrit aucune ligne.

**Hors-périmètre** : respecté. Aucun re-semis automatique (`validate` n'écrit rien — vérifié sur
liste périmée et sur liste sans `[origin]`) ; aucune liste ne référence sa semence, `def` nomme et
`reseed` rerésout ; `reseed` ne touche aucun `*.md` d'élément ; `debt-review`, `road-map` et le
reste du pipeline sont hors du diff.

**Signaux de dérive** : aucun matérialisé. Seuls `reseed` et l'avertissement de `validate`
résolvent une définition ; l'avertissement de péremption n'a jamais fait tomber un `validate`
conforme ; aucun conflit n'est résolu tout seul, `--force` compris ; aucune écriture dans une liste
`frozen` sans `--force` ; la copie reste octet pour octet sa semence à l'`init` et sur une adoption
verbatim.

**Symptôme d'origine** : **disparu**. Une semence incrémentée est annoncée par `validate`, avec la
version de départ, la version courante et le geste de rattrapage.

### Ce que le dernier commit a levé

- **R3 — levé.** `emit` rend un `Result` et `reseed` refuse avant toute écriture. Reproduit :
  `seuil = 1.5` ajouté au contrat local passe `validate` (code 0), puis
  `reseed r3` → `code=1`, `r3 : contrat inécrivable — champ « seuil » : type float hors contrat —
  attendus : texte, date, entier, booléen, liste`. Plus de traceback, contrat intact à l'octet,
  `.list/backup/` non créé.
- **R15 — levé sur ses deux cas connus.** Titre de section portant `U+0007` :
  `reseed ctl` → `code=1`, `ctl : contrat inécrivable — clé « sections."Con\x07stat" » : caractère
  de contrôle U+0007`, contrat inchangé, `validate` suivant `code=0`. Nom de champ portant
  `U+0007` (le second cas nommé au tour précédent) : `reseed c2` → `code=1`,
  `clé « fields."x\x07y" » : caractère de contrôle U+0007`, contrat inchangé. Le refus reprend
  exactement le seuil de `dump_value` (`ord(c) < 0x20 or ord(c) == 0x7F`) et s'applique après
  échappement, comme lui.

### Réserves arbitrées vers le registre de dette

Revérifiées persistantes à ce commit, conformément à l'arbitrage de l'utilisateur.

- **R4** — la couverture CLI de `reseed` reste absente : `grep -n reseed scripts/tests/test_entree_cli.py`
  ne rend **aucune ligne**. Conflit, `--force` et `--dry-run` ne sont testés qu'au niveau
  bibliothèque.
- **R5** — une définition qui se renomme fait re-estampiller la liste au nom nouveau, sans que rien
  ne distingue ce changement d'un autre.
- **R6** — `warnings()` appelle `resolve(nom, roots())` (`provenance.py:82`) : hors de la machine
  où le skill est installé, toute liste estampillée écrit une ligne sur stderr. Reproduit en
  supprimant la définition : `validate r8` → `code=0`, stderr
  `r8 : semée par « monseed », définition introuvable dans les quatre rangs — péremption
  invérifiable`. Le motif de l'étape 8 (`ERR=$(… 2>&1 >/dev/null); [ -z "$ERR" ]`) devient alors
  faux-positif.
- **R8** — `_poser` n'efface jamais. Reproduit : `note.md` retiré de la définition, `reseed r8` →
  `code=0`, `note.md` **toujours en place** ; `validate` le dit (`… : ajouté depuis le semis`),
  mais le rapporte désormais à chaque appel, à tort — le fichier n'a pas été ajouté, il a été
  abandonné côté semence.

### Qualité du code — constat neuf

- **R16** — `scripts/listdir/provenance.py`, `emit` — **le mode d'échec de R14/R15 subsiste sur la
  troisième et dernière sorte de clé : la feuille.** Le correctif garde l'**en-tête** de table
  (`entete`) mais laisse la clé terminale (`feuille`) passer **brute, ni échappée ni contrôlée** :

  ```python
  morceaux += [f"{feuille} = {dump_value(v, feuille)}" for feuille, v in paires]
  ```

  `dump_value` juge la **valeur** ; `feuille` ne lui sert qu'à nommer le champ dans le message. Une
  clé terminale portant une espace, un point ou un caractère de contrôle est donc écrite telle
  quelle. Deux reproductions de bout en bout, sur une semence que `parse_contract` **accepte** (le
  parseur ne refuse pas les clés inconnues à l'intérieur d'un `[fields.*]`, contrairement à
  `[origin]`) :

  ```
  # 1. clé à espace  —  "ma cle" = "x" dans [fields.id]
  $ list-dir reseed lf        -> code=0, « 1 changement(s) appliqués »
  $ list-dir validate lf      -> code=1
    lf/.list/contract.toml: TOML invalide — Expected '=' after a key in a key/value pair (line 12)

  # 2. clé à point  —  "note.libre" = "x" dans [fields.id]   (le pire des deux)
  $ list-dir reseed dt        -> code=0
  $ list-dir validate dt      -> code=0
  # le contrat écrit porte désormais une table qui n'existait pas :
  #   [fields.id.note]
  #   libre = "x"
  ```

  Le premier cas est le défaut exact que le commit `fd2178c` dit fermer — « ce qui ne se relit pas
  ne s'écrit pas », « appliqué aussi aux clés » : la garde ne couvre en fait que la moitié des
  clés, et le message de commit affirme davantage que le code ne fait. Le second est **pire que
  R15** : le fichier reste du TOML valide, `validate` rend 0, et la structure du contrat a
  silencieusement changé sans qu'aucune commande ne le dise jamais — seul `.list/backup/` garde le
  recours, et rien n'invite à y regarder.

  **Portée réelle** : étroite mais non théorique. Elle suppose une clé que le parseur tolère sans
  la déclarer — or `flatten` conserve délibérément les clés inconnues (« gardée et signalée », la
  règle de `migrate` reprise du plan, étape 4) : les porter est un comportement **prévu**, pas une
  pathologie. Aucun contrat de ce dépôt n'en porte, vérifié.

  **Ce que ça coûterait** : appliquer `_cle(feuille)` et le même refus de caractère de contrôle à
  la feuille, au même endroit que pour l'en-tête. Je ne le fais pas — je juge.

- **Style** : conforme. Le nouveau code de `emit` suit le moule des voisins — docstring en
  capitales portant le pourquoi et le mode d'échec supprimé, commentaire au point de décision,
  message d'échec en français à guillemets typographiques, `Result` partout, aucun `print` hors
  `list-dir.py`. Le partage entre `flatten` (échappe, ne refuse jamais — une clé plate est une
  adresse) et `emit` (refuse, parce qu'il écrit) est explicitement documenté dans `_titre` et tient
  la route : c'est le bon découpage, il est simplement incomplet côté `emit`.

- **Tests** : les six appels d'`emit` en test ont suivi la bascule vers `Result` (`.unwrap()`), et
  `test_fusion.py:255` couvre le refus. Aucun test ne couvre la feuille — c'est la même lacune que
  R16 vue du banc d'essai.

- **Documentation** : `contrat-liste.md` a suivi (cinq mentions de `semence/`, table de fusion à
  jour, le refus d'un contrat inécrivable ajouté par `fd2178c`) ; `SKILL.md` compte treize
  commandes ; `dette.md` porte le geste de rattrapage ; `.gitignore` porte `**/.list/backup/` avec
  son motif.

- **Suivi** : à ce commit, `.claude/implementation/peremption-contrat.md` porte encore
  `statut: en-cours`, `Dernier audit : b58823f` et une « prochaine action » d'arbitrage déjà
  tranchée ; `fd2178c` n'y est pas journalisé. Observation de tenue de dossier, pas constat de
  code : c'est le geste de clôture qui l'y écrira, avec le versement de R4, R5, R6 et R8 — et
  désormais de R16 — au registre de dette.

### Dette induite

R4, R5, R6 et R8, arbitrées et destinées au registre. R3 et R15 n'en sont plus : ils sont corrigés.
S'y ajoute **R16**, qui n'est pas une dette assumée mais un défaut résiduel — le seul constat neuf
de ce tour, et le troisième de la même famille en trois tours.

### Bloquants

Aucun. Les dix critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
intact, aucun signal de dérive n'est matérialisé, aucune commande de vérification n'est en échec,
et R3 comme R15 sont réellement levés, reproductions à l'appui.

Le verdict est `RÉSERVES` et non `FAVORABLE` à cause de **R16** seul. J'ai pesé `DÉFAVORABLE` et
l'écarte pour les raisons qui valaient déjà pour R14 et R15 : aucun critère de réussite ni signal de
dérive ne couvre ce cas, il ne mord sur aucune liste de ce dépôt, et `.list/backup/` en garde le
recours. Je le note toutefois plus sévèrement que R15, parce que la variante « clé à point » écrit
un contrat que **rien ne relit comme fautif** : c'est le premier endroit du chantier où une
corruption survit à `validate`. Une garde de trois lignes sur `feuille`, jumelle de celle qui
existe déjà sur `entete`, lèverait la réserve.

## 2026-09-04 — clôture — `a3d81ce`

**Verdict** : RÉSERVES

Sixième passage. Le diff entier a été rejugé, conformément à la demande. R16 est **levé**, ses deux
reproductions à l'appui. R4, R5, R6 et R8 sont arbitrés vers le registre de dette et vérifiés
persistants. Un constat neuf : **R17**, le même défaut que R16, au dernier endroit où il restait.

### Vérifications exécutées

Depuis `skills/list-dir/`, sauf mention contraire. Arbre de travail propre à `a3d81ce`.

- `uvx pytest scripts/tests -q` → **425 passés, 0 échec** (423 au tour précédent, 346 avant chantier)
- `uvx ruff check scripts` → **All checks passed!**
- `uvx ruff format --check scripts` → **4 fichiers à reformater** : `tests/test_contract.py`,
  `test_items.py`, `test_loader.py`, `test_move.py` — **aucun n'est touché par la branche**. Écart
  préexistant, annoncé dans le suivi
- `uvx pyright` → **9 erreurs**, dans `tests/conftest.py`, `test_contract.py`, `test_items.py`,
  `test_move.py`, `test_prefill.py` — **aucun fichier du chantier n'en produit**. Écart préexistant,
  annoncé
- Étape 7 (racine) : `grep -rn "douze" skills/list-dir/SKILL.md` → sans résultat ;
  `grep -c "semence/" references/contrat-liste.md` → 5 ; `grep -n 'contenu **est** le futur'` →
  sans résultat ; `SKILL.md` dit « treize commandes » (lignes 5 et 42) et porte `reseed` au tableau
- Étape 8 (racine), boucle complète du plan sur les trois registres → **aucune ligne d'écart, code 0,
  stderr vide sur les trois**
- Bac d'essai remonté à la main (projet jetable, définitions `monseed` et `alias`, versions 5 → 13) :
  `init --def`, `init` nu, `init --def` sur nom discordant, `validate` périmé / sans `[origin]` /
  `frozen`, `reseed` nominal, en conflit (avec et sans `--force`), `--force` sur gel, `--dry-run`,
  adoption verbatim, R16 dans ses deux variantes, R6, R8, et six aller-retours `flatten`/`emit`
  au niveau bibliothèque

### Conformité à l'intention

Les dix critères du brief, un par un, tous réexécutés à ce commit.

1. **`init --def` → `diff` muet, `[origin]` compris** : **atteint, vérifié**. `diff` muet entre la
   définition d'essai et `liste/.list/contract.toml` ; `diff -r` muet entre la définition et
   `.list/semence/`. Idem sur les trois registres du dépôt.
2. **`validate` périmé : avertissement, code de retour conservé** : **atteint, vérifié**. Code 0,
   stdout `liste : 0 élément(s) conformes au contrat`, stderr `liste : contrat périmé — semé en v5,
   « monseed » est en v7 ; « list-dir reseed liste » rattrape`. stdout reste propre.
3. **`frozen = true` tait la péremption, fait refuser `reseed`, `--force` passe outre** : **atteint,
   vérifié**. `validate` → code 0 et **stderr vide** malgré v5 → v7 ; `reseed` → code 1 nommant
   `--force` ; `reseed --force` → code 0 ; `frozen = true` conservé après coup.
4. **`reseed` sauvegarde, injecte, sort non nul en nommant les clés sur conflit** : **atteint,
   vérifié**. Conflit → code 1, `fields.categorie.description — modifiée des deux côtés`, contrat
   **intact à l'octet**, `.list/backup/` **non créé**. Identique avec `--force`.
5. **`pytest` passe ; `ruff` et `pyright` restent propres** : **atteint** sur `pytest` et
   `ruff check` ; **atteint sur le périmètre du chantier** pour `ruff format` et `pyright`, dont les
   quatre et neuf écarts sont tous dans des fichiers hors branche.
6. **`reseed --def` sur liste sans `[origin]` : estampille + apports, refus sur conflit** :
   **atteint, vérifié**. Adoption d'une liste égale à sa semence à `[origin]` près : code 0, deux
   changements (`origin.def`, `origin.version` — « posée de la semence »), **`diff` muet avec la
   semence** après coup, `.list/semence/` et `.list/backup/` créés, `validate` suivant muet.
7. **Squelette d'`init` sans `--def` porte `def = false`** : **atteint, vérifié** — `[origin]` /
   `def = false` présents, `validate` code 0 et muet.
8. **`init --def <nom>` sur une semence déclarant un autre nom → code 2** : **atteint, vérifié**.
   `init disc2 --def alias` → code 2, message nommant les deux noms.
9. **`validate` sans `[origin]` signale l'absence de provenance ; `def = false` la tait** :
   **atteint, vérifié** — le message porte le geste d'adoption et l'échappatoire.
10. **Trois définitions versionnées, trois listes estampillées sans autre modification** :
    **atteint, vérifié** par la boucle de l'étape 8, qui n'écrit aucune ligne.

**Hors-périmètre** : respecté. Aucun re-semis automatique ; aucune liste ne référence sa semence ;
`reseed` ne touche aucun `*.md` d'élément ; `debt-review`, `road-map` et le reste du pipeline sont
hors du diff.

**Signaux de dérive** : aucun matérialisé. Seuls `reseed` et l'avertissement de `validate` résolvent
une définition ; l'avertissement de péremption n'a jamais fait tomber un `validate` conforme ; aucun
conflit n'est tranché tout seul, `--force` compris ; aucune écriture dans une liste `frozen` sans
`--force` ; la copie reste octet pour octet sa semence à l'`init` comme à l'adoption verbatim.

**Symptôme d'origine** : **disparu**, vérifié de bout en bout.

### Ce que le dernier commit a levé

- **R16 — levé, dans ses deux variantes.** Semence v8 → v9, contrat local portant
  `"ma cle" = "x"` dans `[fields.id]` : `reseed lf` → code 0, contrat produit portant
  `"ma cle" = "x"` **cité**, `validate` suivant code 0. Semence v9 → v10, contrat local portant
  `"note.libre" = "x"` : le contrat réémis garde `"note.libre" = "x"` sous `[fields.id]`, et
  `tomllib` le relit en `{'type': 'text', …, 'note.libre': 'x'}` — **plus de table
  `[fields.id.note]` fantôme**. Le correctif est juste à la racine : `_cle` à l'aplatissement,
  `_couper` qui respecte les citations, `_refus` unique. Six aller-retours `flatten`/`emit`
  supplémentaires (titre à point, champ à point, champ à guillemet, sous-clé à contre-oblique)
  passent tous, structure identique après relecture.

### Constat neuf

- **R17** — `scripts/listdir/provenance.py`, `flatten` (branche finale, `plat[cle] = valeur`) —
  **le défaut de R16 survit intact sur la clé de PREMIER NIVEAU.** Les noms de champ et les titres
  de section passent désormais par `_cle`/`_titre` ; `origin.*` est borné par le parseur, qui refuse
  ses clés inconnues. Mais une clé de premier niveau autre que `name`, `description`, `fields`,
  `sections`, `origin` est recopiée **brute** : `parse_contract` ne lit ses tables que par
  `raw.get(...)` et **ne refuse aucune clé inconnue au premier niveau**, exactement comme il tolère
  l'inconnu dans un `[fields.*]`.

  Deux reproductions de bout en bout, sur un contrat que `validate` accepte avant `reseed` :

  ```
  # 1. clé à espace  —  "ma cle" = "x" au premier niveau
  $ list-dir reseed top      -> code=0, « 1 changement(s) appliqués »
  # le contrat écrit porte, ligne 3 :   ma cle = "x"
  $ list-dir validate top    -> code=1
    top/.list/contract.toml: TOML invalide — Expected '=' after a key in a key/value pair (line 3)

  # 2. clé à point  —  "note.libre" = "y" au premier niveau
  $ list-dir reseed top2     -> code=0
  $ list-dir validate top2   -> code=0
  # tomllib relit désormais une table de premier niveau que personne n'a écrite :
  #   dict_keys(['name', 'description', 'origin', 'fields', 'sections', 'note'])
  ```

  Le second est le même mode d'échec que celui que `a3d81ce` dit fermer : **la corruption traverse
  `validate` sans un mot**, code 0, et seul `.list/backup/` garde le recours. Le message de commit
  parle d'une racine (« l'adressage ») qui n'a été traitée que sur deux des trois sortes de clés.

  Vérifié au niveau bibliothèque : `emit(flatten(...))` refuse bien un caractère de contrôle en clé
  de premier niveau (`clé « macle » : caractère de contrôle U+0007`) — c'est **l'espace et le
  point** qui passent, parce que `_refus` ne juge que les caractères de contrôle et que la citation
  n'est jamais posée sur cette branche.

  **Portée réelle** : étroite, non théorique, et identique à celle de R16 — elle suppose une clé que
  le parseur tolère sans la déclarer, et `flatten` conserve délibérément l'inconnu (« gardée et
  signalée », règle de `migrate`, plan étape 4). Aucun contrat de ce dépôt n'en porte, vérifié.

  **Ce que ça coûterait** : la même citation que celle déjà posée deux lignes plus haut, sur la
  branche `else` de `flatten`. Je ne le fais pas — je juge.

- **Détail de message** (sans numéro, non bloquant) : `_refus` cite la clé **non échappée**
  (`clé « macle »` pour `ma\x07cle`), là où la variante passée par `_titre` affiche
  `« sections."Con\x07stat" »`. Le caractère fautif est nommé par son point de code, donc rien n'est
  perdu, mais les deux messages ne se ressemblent plus.

### Réserves arbitrées vers le registre de dette

Revérifiées persistantes à ce commit, conformément à l'arbitrage de l'utilisateur.

- **R4** — `grep -c reseed scripts/tests/test_entree_cli.py` → **0**. Aucune couverture CLI de
  `reseed` : conflit, `--force` et `--dry-run` ne sont testés qu'au niveau bibliothèque.
- **R5** — une définition qui se renomme fait re-estampiller la liste au nom nouveau, sans rien qui
  distingue ce changement d'un autre. Confirmé par la sortie d'adoption : `origin.def — posée de la
  semence`, une ligne comme les autres.
- **R6** — `warnings()` résout la définition : définition déplacée hors des quatre rangs →
  `validate adopt` code 0, stderr `adopt : semée par « monseed », définition introuvable dans les
  quatre rangs — péremption invérifiable`. Le motif de l'étape 8 (`[ -z "$ERR" ]`) devient
  faux-positif hors de la machine d'origine.
- **R8** — `review.md` retiré de la définition, `reseed adopt` → code 0, `adopt/.list/templates/
  review.md` **toujours en place**, et `validate` le rapporte à chaque appel comme « ajouté depuis
  le semis » — à tort : il a été abandonné côté semence, pas ajouté localement.

### Qualité du code

- **Style** : conforme. `_refus` et `_couper` reprennent le moule des voisins — docstring en
  capitales portant le pourquoi et le mode d'échec supprimé, commentaire au point de décision,
  message en français à guillemets typographiques, `Result` partout, aucun `print` hors
  `list-dir.py`. `_couper` est exact sur le guillemet échappé (compte de contre-obliques), vérifié
  par la sous-clé à contre-oblique.
- **Tests** : `test_fusion.py` gagne les cas de la clé terminale ; aucun test ne couvre la clé de
  premier niveau — c'est R17 vu du banc d'essai.
- **Documentation** : inchangée depuis le tour précédent et toujours juste.
- **Suivi** : à ce commit, `.claude/implementation/peremption-contrat.md` porte encore
  `statut: en-cours`, `Dernier audit : b58823f` et une « prochaine action » d'arbitrage périmée ;
  ni `fd2178c` ni `a3d81ce` n'y sont journalisés. Tenue de dossier, pas constat de code : c'est le
  geste de clôture qui l'y écrira, avec le versement de R4, R5, R6, R8 — et de R17 — au registre.

### Dette induite

R4, R5, R6 et R8, arbitrées et destinées au registre. R3, R15 et R16 n'en sont plus : corrigés et
vérifiés tels. S'y ajoute **R17**, quatrième occurrence de la même famille en quatre tours.

### Bloquants

Aucun. Les dix critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
intact, aucun signal de dérive n'est matérialisé, aucune commande de vérification n'est en échec.

Le verdict est `RÉSERVES` à cause de **R17** seul. J'ai pesé `DÉFAVORABLE` — la variante « clé à
point » écrit un contrat que rien ne relit comme fautif, et c'est le quatrième tour où cette famille
réapparaît ailleurs — et je l'écarte pour les raisons qui valaient déjà pour R14, R15 et R16 : aucun
critère de réussite ni signal de dérive ne couvre ce cas, il ne mord sur aucune liste de ce dépôt, et
`.list/backup/` en garde le recours. La citation manquante est au même endroit que celle qui vient
d'être posée, deux lignes plus haut.

## 2026-09-04 — clôture — `7a9fe62`

**Verdict** : RÉSERVES

Septième passage. Diff entier rejugé. **R17 est levé, et cette fois à la racine** : la famille
ouverte par R14 est refermée sur ses trois étages, vérifié par reproduction et par sondage des
variantes voisines. R4, R5, R6 et R8 sont revérifiés persistants — arbitrage assumé, destination
registre de dette. Deux constats neufs mineurs (R18, R19) et un de tenue de dossier (R20).

### Vérifications exécutées

Depuis `skills/list-dir/`, sauf mention contraire. Arbre de travail **propre** à `7a9fe62`
(`git status --short` muet).

- `uvx pytest scripts/tests -q` → **426 passés, 0 échec** (425 au tour précédent, 346 avant chantier)
- `uvx ruff check scripts` → **All checks passed!**
- `uvx ruff format --check --diff scripts` → **4 fichiers** : `tests/test_contract.py`,
  `test_items.py`, `test_loader.py`, `test_move.py` — **aucun n'est dans les 15 fichiers Python
  touchés par la branche** (croisé avec `git diff --name-only`). Écart préexistant, annoncé au suivi
- `uvx pyright` → **9 erreurs**, dans `tests/conftest.py`, `test_contract.py`, `test_items.py`,
  `test_move.py`, `test_prefill.py` — **aucun de ces fichiers n'est touché par la branche**. Écart
  préexistant, annoncé
- Étape 7 (racine) : `grep -rn "douze" skills/list-dir/SKILL.md` → **sans résultat** ; `SKILL.md`
  dit « treize commandes » (lignes 5 et 42) et porte `reseed` au tableau (ligne 60) ;
  `grep -c "semence/" references/contrat-liste.md` → **5** ;
  `grep -n 'contenu \*\*est\*\* le futur'` → **sans résultat**
- Étape 8 (racine), boucle complète du plan sur les trois registres → **aucune ligne d'écart,
  code 0, stderr vide** sur `technical-debt`, `technical-debt-solde`, `technical-debt-ecarte`
- Bac d'essai monté à la main (projet jetable, définitions `monseed` et `alias`, versions 5 → 9) :
  `init --def`, `init` nu, `init --def` sur nom discordant, `validate` périmé / en échec / sans
  `[origin]` / `def = false` / `frozen`, `reseed` nominal, en conflit (avec et sans `--force`),
  `--force` sur gel, `--dry-run`, adoption verbatim et adoption avec apport, les **deux
  reproductions de R17**, R6, R8, et huit aller-retours `flatten`/`emit` au niveau bibliothèque
  sur des formes exotiques

### Conformité à l'intention

Les dix critères du brief, un par un, tous réexécutés à ce commit.

1. **`init --def` → `diff` muet, `[origin]` compris** : **atteint, vérifié**. `diff` muet entre la
   définition d'essai et `liste/.list/contract.toml` ; `diff -r` muet entre la définition et
   `.list/semence/`. Idem sur les trois registres du dépôt (boucle de l'étape 8).
2. **`validate` périmé : avertissement, code de retour conservé** : **atteint, vérifié dans les
   deux sens**. Sur succès : code 0, stdout `per : 0 élément(s) conformes au contrat`, stderr
   `per : contrat périmé — semé en v8, « monseed » est en v9 ; « list-dir reseed per » rattrape`.
   Sur échec (élément sans front matter) : **code 1 conservé**, l'avertissement de péremption
   présent en fin de stderr. stdout reste propre dans les deux cas.
3. **`frozen = true` tait la péremption, refuse `reseed`, `--force` passe outre** : **atteint,
   vérifié**. `validate gel` → code 0 et **stderr vide** malgré v5 → v6 ; `reseed gel` → code 1,
   message nommant `--force` ; `reseed gel --force` → code 0 ; `frozen = true` **toujours présent**
   dans le contrat après coup (ligne 7).
4. **`reseed` sauvegarde, injecte, sort non nul en nommant les clés sur conflit** : **atteint,
   vérifié**. Conflit → code 1, `fields.id.description — modifiée des deux côtés`, contrat
   **intact à l'octet** (`md5sum -c` OK), `.list/backup/` **non créé**. Identique avec `--force`.
   Cas nominal : `origin.version — reprise de la semence`, backup créé, semence rafraîchie.
5. **`pytest` passe ; `ruff` et `pyright` restent propres** : **atteint** sur `pytest` (426/426) et
   `ruff check` ; **atteint sur le périmètre du chantier** pour `ruff format` et `pyright` — les 4
   et 9 écarts sont tous dans des fichiers hors branche, croisement fait.
6. **`reseed --def` sur liste sans `[origin]` : estampille + apports, refus sur conflit** :
   **atteint, vérifié sur les trois cas**. (a) Liste égale à sa semence à `[origin]` près : code 0,
   `origin.def` et `origin.version` « posées de la semence », **`diff` muet avec la semence** après
   coup, `.list/semence/` et `.list/backup/` créés, `validate` suivant code 0 stderr vide.
   (b) Liste portant un `[fields.local]` en propre : code 0, `[origin]` posé en v6 **et**
   `[fields.local]` conservé. (c) Liste divergente sur une clé que la semence porte autrement :
   **code 1, conflit nommé, rien écrit** — c'est la règle « sans base » du plan (étape 4).
7. **Squelette d'`init` sans `--def` porte `def = false`** : **atteint, vérifié** — `[origin]` /
   `def = false` en place après `description` ; `validate` code 0 et muet.
8. **`init --def <nom>` sur une semence déclarant un autre nom → code 2** : **atteint, vérifié**.
   `init disc --def alias` → **code 2**, message nommant les deux noms et la conséquence.
9. **`validate` sans `[origin]` signale l'absence de provenance ; `def = false` la tait** :
   **atteint, vérifié** — message portant le geste d'adoption et l'échappatoire ; après ajout de
   `[origin] def = false`, code 0 et **stderr vide**.
10. **Trois définitions versionnées, trois listes estampillées sans autre modification** :
    **atteint, vérifié**. `git diff master...` sur `.claude/implementation/todo/*/.list/contract.toml`
    montre exactement `+[origin] +def +version +ligne vide`, rien d'autre ; la boucle de l'étape 8
    n'écrit aucune ligne.

**Hors-périmètre** : respecté. Aucun re-semis automatique ; aucune liste ne référence sa semence ;
`reseed` ne touche aucun `*.md` d'élément ; `debt-review`, `road-map` et le reste du pipeline sont
hors du diff.

**Signaux de dérive** : **aucun matérialisé**. Seuls `reseed` et l'avertissement de `validate`
résolvent une définition ; l'avertissement de péremption n'a jamais fait tomber un `validate`
conforme (code 0 vérifié) et n'a jamais changé le code d'un `validate` fautif (code 1 vérifié) ;
aucun conflit n'est tranché tout seul, `--force` compris ; aucune écriture dans une liste `frozen`
sans `--force` ; la copie reste octet pour octet sa semence à l'`init` comme à l'adoption verbatim.

**Symptôme d'origine** : **disparu**, vérifié de bout en bout — une liste dont la semence est
passée de v8 à v9 le dit d'elle-même au premier `validate`, et `reseed` la rattrape sur ordre.

### Ce que le dernier commit a levé

- **R17 — levé, dans ses deux variantes, et à la racine cette fois.** `flatten` fait passer tout
  nom par `_cle` ou `_titre` à ses quatre points d'entrée (premier niveau, sous-clé d'`[origin]`,
  nom de table, clé terminale). Reproductions à `7a9fe62`, sur des contrats que `validate` accepte
  avant le re-semis :
  - clé à espace au premier niveau (`"ma cle" = "x"`) : `reseed top` → code 0, le contrat écrit
    porte `"ma cle" = "x"` **cité**, `validate top` → **code 0** (il rendait 1 avec
    `Expected '=' after a key`) ;
  - clé à point au premier niveau (`"note.libre" = "y"`) : `reseed top2` → code 0, et `tomllib`
    relit `['name', 'description', 'note.libre', 'origin', 'fields', 'sections']` — **plus de table
    `note` fantôme**.
- **Le correctif est vérifié au-delà de sa variante signalée**, ce qui est le point : huit
  aller-retours `flatten`/`emit` sur des formes voisines rendent tous une structure **identique**
  après relecture — section au titre vide, champ au nom vide, clé terminale à point, clé de premier
  niveau portant un crochet, champ au nom à espace, sous-table de champ, sous-table de section,
  guillemet échappé. Les formes qui ne s'écrivent pas (flottant, table inconnue, tableau de tables)
  sont **refusées avant toute écriture**, jamais écrites de travers.
- Le test `test_une_cle_exotique_traverse_l_aller_retour_a_tous_les_etages` verrouille les trois
  étages d'un coup et compare les clés de premier niveau relues — c'est la seule assertion qui
  attrape la variante `note.libre`, puisque le contrat corrompu restait du TOML valide.

### Constats neufs

- **R18** — `scripts/listdir/provenance.py`, `emit` (via `items.dump_value`) — **une liste portant
  une table de premier niveau inconnue ne peut plus jamais être re-semée, et le message la nomme
  « champ ».** `parse_contract` tolère l'inconnu au premier niveau ; `validate` rend donc 0. Mais
  `flatten` range la table entière comme une valeur, et `dump_value` la refuse :

  ```
  $ list-dir validate tab   -> code=0  (stderr : périmé v7 → v8, modifié localement)
  $ list-dir reseed tab     -> code=1
    tab : contrat inécrivable — champ « extra » : type dict hors contrat — attendus :
          texte, date, entier, booléen, liste
  ```

  **Le refus est propre** — contrat intact à l'octet, `.list/backup/` non créé — et c'est bien la
  forme d'échec que ce paquet veut. Deux réserves seulement : le mot « champ » désigne ici une
  **table**, ce qui envoie chercher un `[fields.*]` qui n'existe pas ; et la seule sortie est de
  retirer la table à la main, ce que le message ne dit pas. Aucun contrat de ce dépôt n'en porte,
  vérifié. Non bloquant : aucun critère ni signal de dérive ne le couvre, et rien n'est détruit.

- **R19** — `scripts/listdir/provenance.py`, `_refus` — **la clé fautive est citée non échappée**
  (`clé « ma\x07cle »` s'affiche `clé « macle »`), là où la même faute passée par `_titre` s'affiche
  `« sections."Con\x07stat" »`. Le caractère est nommé par son point de code, donc rien n'est perdu ;
  ce sont les deux messages qui ne se ressemblent plus. Déjà noté sans numéro au sixième audit, je
  le numérote pour qu'il soit citable au registre. Cosmétique.

- **R20** — tenue de dossier — **`.claude/implementation/peremption-contrat.md` est périmé à ce
  commit** : `statut: en-cours`, `Dernier audit : b58823f` (trois audits en retard : `fd2178c`,
  `a3d81ce`, celui-ci), et une « prochaine action » qui parle encore de R15. Le journal de décisions
  ne consigne aucun des trois derniers tours. Ce n'est pas un constat de code : c'est au geste de
  clôture de l'écrire, avec le versement de R4, R5, R6, R8 — et de R18, R19 — au registre de dette.

### Réserves arbitrées vers le registre de dette

Revérifiées **persistantes** à `7a9fe62` par exécution, conformément à l'arbitrage de l'utilisateur.

- **R4** — `grep -c reseed scripts/tests/test_entree_cli.py` → **0**. Aucune couverture CLI de
  `reseed` : conflit, `--force`, `--dry-run` et adoption ne sont testés qu'au niveau bibliothèque.
  Le code 1 d'un conflit et le code 2 d'une discordance de nom ne sont vérifiés de bout en bout par
  aucun test — je les ai constatés à la main, la suite ne les tiendra pas.
- **R5** — une définition qui se renomme fait re-estampiller la liste au nom nouveau sans qu'aucune
  ligne ne distingue ce changement d'un autre : `origin.def — posée de la semence`, au milieu du
  rapport. Confirmé par la sortie d'adoption de `ad3`.
- **R6** — `warnings()` résout la définition à chaque `validate`. Définition déplacée hors des
  quatre rangs → `validate ad3` code 0, stderr `ad3 : semée par « monseed », définition introuvable
  dans les quatre rangs — péremption invérifiable`. Le motif de l'étape 8 (`[ -z "$ERR" ]`) devient
  donc faux-positif sur toute machine où le skill n'est pas installé.
- **R8** — `review.md` retiré de la définition, `reseed ad3` → code 0, et
  `ad3/.list/templates/review.md` **toujours en place** ; le `validate` suivant le rapporte
  `ajouté depuis le semis` — à tort : il a été abandonné côté semence, pas ajouté localement.
  L'avertissement est désormais **permanent** sur cette liste.

### Qualité du code

- **Style** : conforme aux voisins. Docstring en capitales portant le pourquoi et le mode d'échec
  supprimé, commentaire au point de décision, messages en français à guillemets typographiques,
  `Result` partout, aucun `print` hors `list-dir.py`. Le commentaire de `flatten` ajouté par
  `7a9fe62` **nomme la règle plutôt que le cas** (« aucun nom n'entre ici sans passer par `_cle` ou
  `_titre` »), ce qui est précisément ce qui manquait aux trois correctifs précédents.
- **Cas limites** : la triade `MISSING` / `l == s` / `s is MISSING` de `fusionner` reste juste sur
  la suppression locale et sur la clé retirée de la semence — revérifié qu'un second `reseed` ne
  rejoue aucun changement et ne détruit pas `.list/backup/` (`_a_ecrire` garde les trois cibles).
- **Ordre d'écriture** : `_ecrire` sauvegarde avant d'écrire et rafraîchit la semence en dernier ;
  un conflit sort **avant** la sauvegarde, ce que le `md5sum -c` et l'absence de `.list/backup/`
  confirment.
- **Tests** : 426, dont le nouveau qui tient les trois étages. Reste non couvert : la clé de premier
  niveau **table** (R18) et toute la surface CLI de `reseed` (R4).
- **Documentation** : `SKILL.md` (treize commandes, `reseed` au tableau, paragraphe de péremption),
  `references/contrat-liste.md` (section provenance, `.list/semence/` et `.list/backup/` à
  l'arborescence, phrase de la ligne 41 corrigée) et `dette.md` sont justes et vérifiés par grep.

### Dette induite

R4, R5, R6 et R8, arbitrées et destinées au registre. S'y ajoutent **R18** et **R19**, tous deux
mineurs. R3, R15, R16 et **R17** n'en sont plus : corrigés et vérifiés tels. La famille ouverte par
R14 — un nom écrit à la main qui traverse la lecture et ressort de l'écriture — est refermée sur
tous ses étages, et c'est le premier tour où le correctif tient au-delà de la variante signalée.

### Bloquants

Aucun. Les dix critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
intact, aucun signal de dérive n'est matérialisé, aucune commande de vérification n'est en échec.

Le verdict est `RÉSERVES` et non `FAVORABLE` parce qu'il reste des constats que l'utilisateur doit
connaître avant de trancher : les quatre dettes arbitrées (R4, R5, R6, R8) ne sont pas encore au
registre, R18 et R19 sont neufs, et R20 dit que le suivi ne reflète pas l'état du chantier. Aucun
de ces sept points n'interdit la clôture ; leur écriture au registre de dette la conditionne.
