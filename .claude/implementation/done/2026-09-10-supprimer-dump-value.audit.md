---
slug: supprimer-dump-value
---

## 2026-09-10 — clôture — `471d58b`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `git grep -n "dump_value\|ESCAPES" -- skills/list-dir/scripts/` → aucune sortie (exit 1). Étendu à
  tout le dépôt hors `.claude/implementation` et `.claude/plans` : aucune occurrence non plus.
- `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` → **445 passés**,
  0 échec, 11,75 s.
- `uvx ruff check skills/list-dir/scripts/` → 3 erreurs `E501` (`test_contract.py:108`,
  `test_fusion.py:266`, `test_fusion.py:292`). **Identiques sur `master`** (arbre extrait par
  `git archive master`) : préexistantes, non imputables au chantier (R5).
- `uvx --with pytest basedpyright` depuis `/home/debian/.claude` → **25 erreurs** : 12 dans
  `scripts/tests/test_sante_skills.py`, 4 dans `listdir/provenance.py` (lignes 198, 199, 620 —
  hors des lignes modifiées), 9 dans `tests/test_prefill.py`. Même run sur l'arbre `master`
  (avec `--with tomlkit`, sans quoi les imports ne résolvent pas et le décompte est faussé) →
  **25 erreurs, même répartition**. Aucune régression de typage ; `items.py` et `store.py` restent
  à zéro.
- Script de vérification d'ensemble du plan (règle des chaînes de bout en bout) → `ok` :
  `dump_front({"texte": "deux\nlignes"})` rend `texte = """deux⏎lignes"""` ;
  `dump_front({"liste": ["a\nb", "court"]})` rend `liste = ["a\nb", "court"]` sans `"""` et se relit
  `["a\nb", "court"]` ; `toml_text("a\tb", "k") == '"a\\tb"'` ; `\x00` refusé par `toml_text` **et**
  `dump_front`, message portant `U+0000`.
- Sondes de cas limites (script ad hoc, hors plan) sur `toml_text` + `tomllib.loads` : `\r` seul,
  `\f`, `\v`, `\t`, `a"""b`, `ab"`, `a\b`, `a\nb"`, `a\nb"""c`, `a\nb""""c`, blancs de bord,
  saut en tête et en fin → tous relus à l'identique **sauf CRLF** (voir R2).

### Conformité à l'intention

- Critère « `grep`/`git grep` sur `dump_value|ESCAPES` ne rend plus rien » : **atteint, vérifié**.
- Critère « la suite `skills/list-dir/scripts/tests/` reste verte » : **atteint, vérifié**
  (445 passés).
- Critère « l'en-tête d'`items.py` n'annonce plus deux écrivains » : **atteint, vérifié**. Le
  paragraphe « DEUX ÉCRIVAINS COHABITENT » est remplacé par « UN SEUL ÉCRIVAIN, et c'est tomlkit »
  suivi de « LA RÈGLE DES CHAÎNES, ET ELLE EST GÉNÉRALE ».
- Critère « scalaire multiligne en `"""…"""`, la même valeur dans une liste échappée sur une ligne
  et relue identique » : **atteint, vérifié** par exécution.
- Hors-périmètre : **respecté**. `flatten`, `_couper`, `_cle` sont inchangés dans leur corps ;
  `reseed` et la détection de conflits ne sont pas touchés ; `contract.py` n'est pas au diff ;
  aucun contrat du dépôt n'est réécrit.
- Signaux de dérive : **aucun matérialisé**.
  - `_cle` **apparaît** au diff, mais seulement par son docstring (le paragraphe qui justifiait
    l'emprunt d'`ESCAPES`), réécriture explicitement prescrite par l'étape 2 du plan validé. Aucune
    ligne de code de `_cle`, `_couper` ou `flatten` n'a changé — vérifié au diff. L'option B n'est
    pas rentrée par la fenêtre.
  - `test_reseed.py` et `test_fusion.py` ne sont pas au diff (`--stat` : seul `test_items.py` est
    modifié côté tests) ; `test_store_ecriture.py` non plus, alors que ses tests `:389` et `:394`
    devaient survivre au changement d'écrivain — ils passent sans retouche.
  - `ESCAPES` n'existe plus en un seul exemplaire, encore moins deux : la table vit désormais dans
    `provenance.py` sous `ECHAPPEMENTS_DE_NOM`, unique définition du dépôt.
  - Diff limité à `items.py`, `store.py`, `provenance.py`, `test_items.py` — plus le suivi, le brief
    et le plan.
- Symptôme d'origine : **disparu**. Un seul écrivain répond désormais à « comment s'écrit cette
  valeur ? » ; le cas `\x00`, sur lequel les deux écrivains divergeaient sur le fond, est tranché
  dans le sens du refus nommé, conformément à la décision du 2026-09-10 portée au journal du suivi.

### Qualité du code

- **R1** — `skills/list-dir/scripts/listdir/provenance.py:344` — le docstring de `_refus`, réécrit
  par ce chantier, ouvre sur « LE MÊME REFUS QUE L'ÉCRIVAIN SUR UNE VALEUR, appliqué au nom ». Cette
  équivalence est **fausse depuis le commit qui l'écrit** : `_refus` refuse tout caractère de
  contrôle (`ord(c) < 0x20 or ord(c) == 0x7F`), tandis que l'écrivain accepte désormais les
  contrôles blancs dans une valeur (`\t`, `\n`, `\f`, `\v`, `\r` — vérifié par exécution). Le refus
  sur les noms est plus strict que celui sur les valeurs, et c'est justifié (un nom vit sur une
  ligne) ; c'est la phrase qui ne l'est plus. Dans un paquet où les commentaires portent la
  doctrine, une équivalence affirmée à tort se paiera au prochain lecteur qui s'y fiera pour
  modifier l'un des deux côtés.
- **R2** — `skills/list-dir/scripts/listdir/items.py:200` (`multiline=multiline and "\n" in value`)
  — une valeur contenant **CRLF** ne se relit plus à l'identique : `toml_text("a\r\nb", "k")` rend
  `"""a␍␊b"""`, que `tomllib` relit `'a\nb'` — le `\r` est perdu **en silence**. Vérifié par
  exécution. Sur `master`, `dump_value` échappait `\r` et les deux appelants contrats
  (`store.init_list`, `provenance.emit`) round-trippaient exactement ; ils héritent aujourd'hui de
  cette perte. Le comportement préexistait dans `toml_value` pour le front matter des éléments, donc
  ce n'est pas une invention du chantier, mais son périmètre s'élargit. Portée pratique : un
  `--description` ou un champ collé depuis une source Windows. Aucun test ne pinne ce cas, ni dans
  un sens ni dans l'autre. Ce n'est contraire à aucun critère écrit — d'où une réserve et non un
  défavorable — mais la doctrine « TOUT CE QUI EST ÉCRIT DOIT SE RELIRE », que le paquet revendique,
  admet ici une exception que personne n'a formulée.
- **R3** — `\b` (U+0008) passe d'accepté (échappé par `ESCAPES`) à refusé. Le plan l'a vu, écrit et
  assumé (étape 1, « Note »), et le journal du suivi tranche « contrôles non blancs refusés
  partout ». Rien à corriger : signalé pour mémoire, parce que ce durcissement touche
  `listdir init --description` et le front matter des éléments sans qu'aucun test ne le distingue du
  cas `\x00`.
- **R4** — `skills/list-dir/scripts/tests/test_items.py` — la suppression de
  `test_dump_value_couvre_les_types_du_contrat` emporte la seule assertion directe sur la
  sérialisation d'une `datetime.date` (`2026-08-24`). Le nouveau
  `test_toml_text_rend_le_membre_droit_du_egal` couvre `str`, `bool` et `list`, pas `date`. La
  branche `isinstance(value, (int, datetime.date))` de `toml_value` n'est plus couverte
  qu'indirectement, par l'aller-retour de `test_store_ecriture.py:216`. Le cas `bool` avant `int`,
  lui, reste pinné (`toml_text(True, "k") == "true"`).

### Dette induite

- **R5** — Rien d'imputable au chantier. Les 3 `E501` de `ruff` sont préexistantes et identiques sur
  `master` ; les 25 erreurs `basedpyright` aussi, à la répartition près qui est inchangée. Aucune
  duplication introduite : `ECHAPPEMENTS_DE_NOM` est un **déménagement**, pas une copie, et
  `toml_text` ne porte aucune règle propre (une ligne de délégation), donc n'est pas un second
  écrivain déguisé.
- **R6** — Tâche de clôture restant due, annoncée par le plan et par les « Notes » du suivi :
  `.claude/implementation/todo/technical-debt/deux-ecrivains-toml-coexistent.md` et
  `.claude/implementation/todo/road-map/supprimer-dump-value.md` portent toujours l'affirmation
  fausse (« un saut de ligne lève `SerialiseError` »). Elles sont encore dans `todo/` au SHA audité.
  Solder ces entrées sans corriger leur énoncé laisserait dans l'historique du dépôt une dette
  déclarée payée sur un motif qui n'a jamais existé.

### Bloquants

Aucun.

---

## 2026-09-10 — clôture — `f6ca5b8`

**Verdict** : RÉSERVES

Deuxième audit de clôture. Le SHA audité ajoute un seul commit de code au précédent
(`f6ca5b8`, « R1 et R2 de l'audit 471d58b traités »). Les constats R1 à R6 du 2026-09-10 sont
repris et statués un par un ci-dessous ; un constat neuf, **R7**, est introduit par le commit
correctif lui-même.

### Vérifications exécutées

- `git grep -n "dump_value\|ESCAPES" -- skills/list-dir/scripts/` → **aucune sortie** (exit 1).
- `grep -rn "dump_value\|ESCAPES" skills/list-dir/scripts/` (la forme littérale du brief, celle que
  le plan disait polluée par `.pytest_cache`) → **aucune sortie non plus** au SHA audité.
- `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` → **447 passés**,
  0 échec, 12,45 s (445 au précédent audit ; +2 tests d'étape correctifs).
- Vérifs des quatre étapes du suivi, une par une : `test_items.py` 42 passés, `test_fusion.py` 24,
  `test_provenance.py` 38, `test_reseed.py` 24, `test_store_ecriture.py` 47. Toutes vertes.
- `uvx ruff check skills/list-dir/scripts/` → **3 erreurs `E501`** (`test_contract.py:108`,
  `test_fusion.py:266`, `test_fusion.py:292`). Arbre `master` extrait par
  `git archive master | tar -x` → **mêmes 3 erreurs**. Préexistantes (R5).
- `uvx --with pytest basedpyright` depuis `/home/debian/.claude` → **25 erreurs, 0 avertissement**.
  Répartition : 12 `scripts/tests/test_sante_skills.py`, 4 `listdir/provenance.py`
  (lignes 198, 199, 622 — hors des lignes touchées par le diff), 9 `tests/test_prefill.py`.
  Décompte et répartition identiques au relevé `master` du précédent audit. `items.py` et
  `store.py` restent à zéro. Aucune régression de typage.
- Script de vérification d'ensemble du plan (règle des chaînes de bout en bout) → `ok`.
- Sondes de relecture ad hoc sur `toml_text` + `tomllib.loads`, et sur `dump_front` en **liste**,
  pour 15 valeurs (`a\r\nb`, `a\rb`, `\r` seul, `a\n\rb`, `a\nb\r`, `é\r\nx`, `a\r\n\r\nb`, `\t`,
  `\f`, `\v`, `a"""b`, `a\\b`, blancs de bord, `\na\n`, `a\nb"""c`, `a\nb""""c`, `a\nb"`) →
  **tous relus à l'identique, aucune perte, dans les deux contextes**.
- Sondes sur `emit(flatten(...))` avec une valeur de contrat multiligne puis CRLF → contrat rendu
  `description = """ligne1⏎ligne2"""` d'un côté, `description = "crlf\r\nsuite"` de l'autre ;
  `flatten(tomllib.loads(texte)) == plat` dans les trois cas.

### Suite donnée aux constats du précédent audit

- **R1** (docstring de `_refus` affirmant à tort un refus identique à celui de l'écrivain) —
  **corrigé**. Le paragraphe s'ouvre désormais sur « PLUS STRICT QUE LE REFUS PORTÉ SUR UNE
  VALEUR, et ce n'est pas un alignement manqué », et dit pourquoi (un nom de table vit sur une
  ligne). L'énoncé est juste. *Mais la forme de ce même paragraphe introduit R7, ci-dessous.*
- **R2** (perte silencieuse du `\r` en forme multiligne) — **corrigé et pinné**.
  `items.py:207` : `en_bloc = multiline and "\n" in value and "\r" not in value`, accompagné d'un
  commentaire qui nomme la règle de grammaire TOML en cause. Deux tests neufs le tiennent
  (`test_crlf_reste_relisible_donc_ne_part_pas_en_multiligne`,
  `test_retour_chariot_seul_reste_relisible`). Vérifié par exécution indépendante : plus aucune
  valeur, scalaire ou en liste, ne perd de caractère à l'aller-retour. La doctrine « TOUT CE QUI
  EST ÉCRIT DOIT SE RELIRE » n'a plus d'exception.
- **R3** (`\b` passe d'accepté à refusé) — **assumé**, comme annoncé. Écrit au plan (étape 1,
  « Note ») et tranché au journal du suivi. Inchangé, rien à reprocher.
- **R4** (couverture directe du type `date` perdue) — **toujours ouvert**. Vérifié :
  `datetime.date` n'apparaît plus nulle part dans `tests/test_items.py`, et la branche
  `isinstance(value, (int, datetime.date))` de `toml_value` n'est couverte qu'indirectement, par
  l'aller-retour de `test_store_ecriture.py:216`. Le suivi le reconnaît comme restant à traiter à
  la clôture ; il ne l'a pas été.
- **R5** (rien d'imputable au chantier côté linters) — **confirmé** par relevé refait ci-dessus.
- **R6** (les deux registres portent une affirmation fausse) — **toujours ouvert, et c'est la
  réserve principale**. Vérifié au SHA audité :
  `.claude/implementation/todo/technical-debt/deux-ecrivains-toml-coexistent.md:37` affirme encore
  qu'une valeur à saut de ligne « lève `SerialiseError` par l'autre », et `:41` qu'un
  `--description` multiligne « fait échouer `init` ». Les deux entrées sont encore dans `todo/`.
  Le brief a été rouvert et corrigé sur ce point ; les registres, non. Solder la dette en l'état
  laisse au dépôt une dette déclarée payée sur un mode de défaillance qui n'a jamais existé — et
  c'est précisément ce que le plan (« Dette à consigner à la clôture ») et les « Notes » du suivi
  s'engageaient à éviter.

### Conformité à l'intention

Les quatre critères de réussite du brief, un par un :

1. « `grep -rn "dump_value\|ESCAPES" skills/list-dir/scripts/` ne rend plus rien » —
   **atteint, vérifié** sous les deux formes (`grep -rn` et `git grep`).
2. « `pytest skills/list-dir/scripts/tests/` reste vert » — **atteint, vérifié** (447 passés).
3. « l'en-tête d'`items.py` n'annonce plus deux écrivains » — **atteint, vérifié**. Le paragraphe
   « DEUX ÉCRIVAINS COHABITENT » est remplacé par « UN SEUL ÉCRIVAIN, et c'est tomlkit » suivi de
   « LA RÈGLE DES CHAÎNES, ET ELLE EST GÉNÉRALE », laquelle porte désormais aussi l'exception `\r`.
4. « une chaîne scalaire à saut de ligne s'écrit `"""…"""` ; la même dans une liste s'écrit
   échappée sur une ligne et se relit identique » — **atteint, vérifié par exécution** :
   `dump_front({"texte": "deux\nlignes"})` rend `"""…"""` ; `dump_front({"liste": ["a\nb","court"]})`
   ne contient aucun `"""` et se relit `["a\nb", "court"]`.

**Hors-périmètre** : respecté. `flatten`, `_couper`, `_cle` ont un corps inchangé ; `reseed` et la
détection de conflits ne sont pas touchés ; `contract.py` n'est pas au diff ; aucun contrat du
dépôt n'est réécrit.

**Signaux de dérive** : aucun matérialisé. `_cle` n'apparaît au diff que par son docstring,
réécriture prescrite par l'étape 2 du plan validé. `test_reseed.py`, `test_fusion.py` et
`test_store_ecriture.py` ne sont pas au diff — leurs tests `:389` et `:394` passent sans retouche,
ce qui est la meilleure preuve que le changement d'écrivain a préservé le contrat de comportement.
`ECHAPPEMENTS_DE_NOM` est l'unique table du dépôt : un déménagement, pas une copie. Le diff se
limite à `items.py`, `store.py`, `provenance.py`, `test_items.py`, plus le suivi, le brief, le plan
et ce rapport.

**Symptôme d'origine** : disparu, et davantage qu'au précédent audit. Un seul écrivain répond à
« comment s'écrit cette valeur ? » ; la divergence de forme est résorbée ; la divergence de fond
(`\x00`) est tranchée dans le sens du refus nommé, conformément au journal ; et la question que
personne n'avait posée — le `\r` — est tranchée dans le sens de la relecture exacte.

### Qualité du code

- **R7** *(neuf, introduit par `f6ca5b8`, le commit correctif de R1 et R2)* — trois docstrings
  écrites dans ce commit ne sont pas des chaînes brutes et portent des échappements **simples**, si
  bien que Python les résout en vrais caractères de contrôle au lieu du texte voulu. Vérifié par
  exécution (`provenance._refus.__doc__`) :

  ```
  "… admet les contrôles blancs dans une valeur — `\t`, et `\n` par\n    la forme multiligne — …"
                                                    ^^ tabulation réelle  ^^ saut de ligne réel
  ```

  Le docstring de `_refus` (`provenance.py:344-346`) contient donc une tabulation et un saut de
  ligne littéraux au milieu d'une phrase, et le docstring de module d'`items.py` (`:26`) contient
  un **retour chariot réel** là où il voulait écrire le texte `\r`. Rendu par `help()`, par une
  bulle d'éditeur ou par tout outil qui lit `__doc__`, la phrase est cassée.
  Les voisins immédiats font l'inverse et le font bien : `items._controle_non_blanc` écrit
  `` `\\t \\n \\r \\f \\v` `` et `items.toml_value` écrit `` un `\\r` ``, tous deux doublés. C'est
  donc un écart au style du fichier, pas une préférence. Ironie mineure mais réelle : un module
  dont la doctrine est « tout ce qui est écrit doit se relire » loge un caractère de contrôle non
  voulu dans sa propre documentation. Correction mécanique (doubler trois antislashs), aucun impact
  sur le comportement, aucun test concerné — mais c'est un défaut **entré par le correctif**, donc
  jamais passé sous un audit avant celui-ci.
- Pour le reste, la qualité relevée au précédent audit tient : la garde de type reste explicite, le
  message de refus conserve la forme `U+{ord:04X}` que `test_store_ecriture.py:397` assère,
  `toml_text` est une ligne de délégation sans règle propre, et le commentaire de sept lignes qui
  justifie `en_bloc` est dans la densité et le ton des fichiers voisins.

### Dette induite

- Rien de neuf par rapport à R5. Pas de duplication : `ECHAPPEMENTS_DE_NOM` est une définition
  unique, `toml_text` n'est pas un second écrivain déguisé. Pas d'abstraction gratuite : le
  paramètre `multiline` est interne et sert une règle nommée. Pas de couplage nouveau —
  `provenance.py` et `store.py` importent depuis `.items` comme avant, un symbole de moins.
- R4 et R6 restent les deux dettes que ce chantier laisse derrière lui, l'une de couverture de
  test, l'autre de tenue des registres.

### Bloquants

Aucun. Les quatre critères de réussite sont atteints et vérifiés par exécution. R4, R6 et R7 sont
des réserves : elles n'interdisent pas la clôture, mais R6 doit être traité **avant** de solder
l'entrée de dette et l'entrée de road-map, faute de quoi le dépôt archive une dette payée sur un
motif inexistant.

---

## 2026-09-10 — clôture — `a866453`

**Verdict** : RÉSERVES

Troisième audit de clôture. Le SHA audité ajoute au précédent un unique commit de code
(`a866453`, « R7 de l'audit `f6ca5b8` traité »), qui touche deux lignes : un antislash doublé dans
le docstring de module d'`items.py:26` et un dans celui de `provenance._refus:344`. Les constats R1
à R7 sont statués un par un ci-dessous. Aucun constat neuf n'est introduit par ce commit ; un
constat d'outillage, **R8**, est ajouté sur la formulation littérale du premier critère.

### Vérifications exécutées

- `git rev-parse HEAD` → `a86645381173f08608912c457c05c7f5fddce076`, arbre de travail propre
  (`git status --porcelain` vide) : l'audité est bien le commité.
- `git grep -n "dump_value\|ESCAPES" -- skills/list-dir/scripts/` → **aucune sortie** (exit 1).
- `grep -rn "dump_value\|ESCAPES" skills/list-dir/scripts/` → **14 lignes**, toutes dans
  `.pytest_cache/v/cache/nodeids` (fichiers non suivis, régénérés par ma propre exécution de la
  suite). Aucun fichier source. Voir R8.
- `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` → **447 passés**,
  0 échec, 12,50 s.
- `uvx ruff check skills/list-dir/scripts/` → **3 erreurs `E501`** (`test_contract.py:108`,
  `test_fusion.py:266`, `test_fusion.py:292`). Arbre `master` extrait par `git archive master |
  tar -x` → **mêmes 3 erreurs**. Préexistantes (R5).
- `uvx --with pytest basedpyright` depuis `/home/debian/.claude` → **25 erreurs, 0 avertissement** :
  12 `scripts/tests/test_sante_skills.py`, 9 `tests/test_prefill.py`, 4 `listdir/provenance.py`
  (hors des lignes du diff). Même outil sur l'arbre `master` extrait (avec `--with tomlkit`, sans
  quoi les imports ne résolvent pas) → **29 erreurs**, mêmes fichiers **plus 5 dans
  `tests/test_items.py`** que la branche n'a plus. Aucune régression de typage ; le chantier en
  **retire** au contraire. `items.py` et `store.py` restent à zéro dans les deux arbres.
- Script de vérification d'ensemble du plan (règle des chaînes de bout en bout) → **`ok`** :
  `dump_front({"texte": "deux\nlignes"})` rend `"""…"""` et se relit exact ;
  `dump_front({"liste": ["a\nb", "court"]})` ne contient aucun `"""` et se relit
  `["a\nb", "court"]` ; `toml_text("a\tb", "k") == '"a\\tb"'` ; `\x00` refusé par `toml_text` **et**
  par `dump_front`, message portant `U+0000`.
- Sonde AST + `__doc__` sur les docstrings de `items.py`, `provenance.py`, `store.py` et
  `contract.py` (module, fonctions, classes) : recherche d'un caractère de contrôle réel autre que
  le saut de ligne structurel → **aucune occurrence**. R7 est éteint, et éteint partout, pas
  seulement aux deux lignes du correctif.

### Suite donnée aux constats des audits précédents

- **R1** (docstring de `_refus` affirmant à tort un refus identique à celui de l'écrivain) —
  **corrigé** en `f6ca5b8`, confirmé ici : le paragraphe dit « PLUS STRICT QUE LE REFUS PORTÉ SUR
  UNE VALEUR » et en donne la raison.
- **R2** (perte silencieuse du `\r` en forme multiligne) — **corrigé et pinné**.
  `items.py:207` : `en_bloc = multiline and "\n" in value and "\r" not in value`, sous un
  commentaire de six lignes qui nomme la règle de grammaire TOML en cause. Réexécuté ici : aucune
  perte à l'aller-retour, ni en scalaire ni en liste.
- **R3** (`\b` passe d'accepté à refusé) — **assumé**, écrit au plan (étape 1, « Note ») et tranché
  au journal du suivi. Rien à reprocher.
- **R4** (couverture directe du type `date` perdue) — **toujours ouvert**. Vérifié au SHA audité :
  `grep -rn "datetime.date" skills/list-dir/scripts/tests/` ne rend rien dans `test_items.py`. La
  branche `isinstance(value, (int, datetime.date))` de `toml_value` n'est couverte qu'indirectement,
  par l'aller-retour de `test_store_ecriture.py:216`. Le suivi annonçait ce point « à traiter à la
  clôture » ; il ne l'a pas été. Portée réelle limitée — le cas est couvert de bout en bout, pas
  unitairement — mais c'est une couverture que `master` avait et que la branche n'a plus.
- **R5** (rien d'imputable au chantier côté linters) — **confirmé**, relevé refait ci-dessus, et le
  décompte `basedpyright` s'améliore de 5 unités.
- **R6** (les deux registres portent une affirmation fausse) — **toujours ouvert, et c'est la
  réserve principale**. Vérifié au SHA audité :
  `.claude/implementation/todo/technical-debt/deux-ecrivains-toml-coexistent.md` affirme encore
  qu'une valeur à saut de ligne « lève `SerialiseError` par l'autre » et qu'un `--description`
  multiligne « fait échouer `init` ». Les deux entrées sont encore dans `todo/`. Le brief a été
  rouvert et corrigé sur ce point ; les registres, non. Solder ces entrées sans corriger leur
  énoncé archiverait une dette payée sur un mode de défaillance qui n'a jamais existé — ce que le
  plan (« Dette à consigner à la clôture ») et les « Notes » du suivi s'engageaient à éviter.
- **R7** (échappements simples dans trois docstrings écrites par le correctif) — **corrigé**. Les
  deux lignes du diff `f6ca5b8..a866453` doublent les antislashs de `items.py:26` (`\\r`) et de
  `provenance.py:344` (`\\t`, `\\n`). La sonde `__doc__` ne trouve plus aucun caractère de contrôle
  réel dans les docstrings du paquet. Le style s'aligne désormais sur les voisins immédiats
  (`_controle_non_blanc`, `toml_value`), qui doublaient déjà.

### Conformité à l'intention

Les quatre critères de réussite du brief, un par un :

1. « `grep -rn "dump_value\|ESCAPES" skills/list-dir/scripts/` ne rend plus rien » —
   **atteint** dans le suivi git (`git grep` : aucune sortie). La forme littérale du brief rend des
   lignes de `.pytest_cache`, artefact non suivi — voir R8. Le suivi, qui fait foi, énonce le
   critère avec `git grep` ; il est satisfait sans réserve.
2. « `pytest skills/list-dir/scripts/tests/` reste vert » — **atteint, vérifié** : 447 passés,
   0 échec.
3. « l'en-tête d'`items.py` n'annonce plus deux écrivains » — **atteint, vérifié** (`items.py:20-28`) :
   « UN SEUL ÉCRIVAIN, et c'est tomlkit », suivi de « LA RÈGLE DES CHAÎNES, ET ELLE EST GÉNÉRALE »,
   qui porte l'exception `\r` et le refus des contrôles non blancs.
4. « une chaîne scalaire à saut de ligne s'écrit `"""…"""` ; la même dans une liste s'écrit échappée
   sur une ligne et se relit identique » — **atteint, vérifié par exécution**.

**Hors-périmètre** : respecté. `flatten`, `_couper` et `_cle` ont un corps inchangé ; `reseed` et la
détection de conflits ne sont pas touchés ; `contract.py` n'est pas au diff ; aucun contrat déjà
présent dans le dépôt n'est réécrit.

**Signaux de dérive** : **aucun matérialisé**. `_cle` n'apparaît au diff que par son docstring,
réécriture prescrite par l'étape 2 du plan validé. `test_reseed.py`, `test_fusion.py` et
`test_store_ecriture.py` ne sont pas au diff et passent sans retouche — c'est la meilleure preuve
que le changement d'écrivain a préservé le contrat de comportement, en particulier
`test_store_ecriture.py:389` et `:394`. `ECHAPPEMENTS_DE_NOM` est l'unique table du dépôt
(`provenance.py:301`, unique usage `:336`) : un déménagement, pas une copie ; `ESCAPES` n'existe
en aucun exemplaire. Le diff se limite à `items.py`, `store.py`, `provenance.py`, `test_items.py`,
plus le suivi, le brief, le plan et ce rapport.

**Symptôme d'origine** : **disparu**. Un seul écrivain répond à « comment s'écrit cette valeur ? ».
La divergence de forme est résorbée ; la divergence de fond (`\x00`) est tranchée dans le sens du
refus nommé, conformément au journal ; et le cas que personne n'avait posé (`\r`) est tranché dans
le sens de la relecture exacte.

### Qualité du code

- Les quatre étapes du suivi sont cochées et leurs vérifications passent, réexécutées une par une
  au sein de la suite complète.
- Les sites d'appel sont conformes à l'arbitrage de cadrage : `emit` garde son assemblage de texte
  et ne change que le membre droit du `=` (`provenance.py:441`) ; `store.init_list` appelle
  `toml_text` sous son `try/except SerialiseError` inchangé (`store.py:810-811`).
- `toml_text` reste une ligne de délégation sans règle propre — ce n'est pas un second écrivain.
  Le paramètre `multiline` est interne, nommé, et sert une règle écrite.
- **R8** *(neuf, mineur, d'outillage et non de code)* — le premier critère de réussite du brief est
  formulé avec `grep -rn`, qui ne respecte pas `.gitignore` : dès que la suite a tourné,
  `skills/list-dir/scripts/.pytest_cache/v/cache/nodeids` et son homologue sous `tests/` rendent
  14 lignes portant `dump_value`, noms des tests supprimés. Le plan avait vu le piège et prescrit
  `git grep` ; le suivi a repris le critère sous cette forme. Aucun impact sur le code : c'est le
  critère du brief figé qui est imprécis, pas le résultat. Signalé pour que la clôture ne rejoue
  pas la forme littérale et n'en conclue pas à un échec.

### Dette induite

- Rien de neuf. Pas de duplication (`ECHAPPEMENTS_DE_NOM` est une définition unique), pas
  d'abstraction gratuite, pas de couplage nouveau — `provenance.py` et `store.py` importent depuis
  `.items` comme avant, un symbole de moins. Le décompte `basedpyright` baisse de 29 à 25.
- Les deux dettes que le chantier laisse derrière lui restent **R4** (couverture unitaire du type
  `date`) et **R6** (énoncé faux des deux registres).

### Bloquants

Aucun. Les quatre critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre
est respecté, aucun signal de dérive ne s'est matérialisé, et R1, R2 et R7 sont éteints. R4, R6 et
R8 sont des réserves : elles n'interdisent pas la clôture, mais **R6 doit être traité avant de
solder** l'entrée de dette `deux-ecrivains-toml-coexistent` et l'entrée de road-map
`supprimer-dump-value`, sans quoi le dépôt archive une dette payée sur un motif inexistant.
