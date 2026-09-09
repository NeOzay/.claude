---
slug: tableaux-toml-aplatis-a-l-ecriture
---

## 2026-09-09 — clôture — `4f47ad1`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ -q` → **456 passés, 0 échec**
  (12.32 s)
- `~/.claude/.venv/bin/python -m pytest scripts/tests/ -q` → **107 passés, 0 échec** — total 563,
  conforme au décompte annoncé au suivi (551 avant, 563 après)
- `python3 ~/.claude/scripts/sante_skills.py; echo $?` → **aucune sortie, code 0**
- `list-dir help >/dev/null` → **OK** (le ré-amorçage `os.execv` dans le venv fonctionne depuis le
  `python3` Homebrew du PATH)
- `~/.claude/.venv/bin/python -c "import tomlkit, pytest"` → OK, tomlkit **0.15.1**
- `sante_skills._dependances()` exercé sur trois racines jouets fabriquées par mes soins → venv
  absent : anomalie nommée avec la commande `uv venv … && uv pip install …` ; tomlkit absent seul :
  anomalie citant `tomlkit` et lui seul ; venv complet : liste vide
- reproduction de bout en bout de l'entrée de road-map, refaite indépendamment (liste neuve,
  tableau sur trois lignes précédé d'un commentaire, **deux** champs ajoutés au contrat,
  `list-dir migrate`) → `diff -u` = **deux lignes ajoutées, rien d'autre** ; tableau, indentation
  et commentaire intacts
- `npx pyright` sur `skills/list-dir` → **4 erreurs**, toutes dans `tests/test_prefill.py:127`,
  toutes préexistantes ; aucune sur le code du chantier, tomlkit résolu
- `ruff` → **NON EXÉCUTÉE : outil absent** de la machine et du venv (`ruff not found`). Les
  5 erreurs préexistantes annoncées au suivi ne sont donc pas confirmées par moi.

### Conformité à l'intention

Les cinq critères de réussite, un par un :

1. « `pytest` passe sur `skills/list-dir/scripts/tests/` » — **atteint, vérifié** (456/456).
2. « un tableau écrit à la main sur plusieurs lignes ressort identique après un `migrate` qui
   ajoute un champ » — **atteint, vérifié** hors banc de test, sur une vraie liste et un vrai
   `migrate` (voir ci-dessus). Couvert aussi par
   `test_migrate_ajoute_un_champ_sans_aplatir_les_tableaux`.
3. « une entrée de tableau contenant un saut de ligne s'écrit en `"""…"""` » — **atteint, vérifié**
   (`test_saut_de_ligne_dans_une_entree_de_tableau`, relecture par `tomllib.loads` dans le test ;
   `toml_value` pose `multiline=True` récursivement).
4. « un commentaire posé au-dessus d'un champ suit ce champ quand le contrat le réordonne » —
   **atteint, vérifié** (`test_migrate_reordonne_sans_reformater`, et mon propre appel direct à
   `dump_front` avec un ordre inversé).
5. « `sante_skills.py` signale l'absence de tomlkit » — **atteint, vérifié** sur racines jouets,
   avec la commande de réparation dans le message.

**Hors-périmètre** : respecté. Le diff ne touche ni `provenance.py`, ni l'écriture des contrats
(`store.init_list` inchangé), ni les gabarits ; `dump_value` n'a vu changer que son docstring, son
corps est à l'octet celui de `master`. L'enroulement automatique n'a pas été introduit : sans
`raw_front`, `dump_front` sort canonique et sur une ligne.

**Signaux de dérive** : un seul matérialisé, celui qui était annoncé — deux tests existants
réécrits (`test_un_champ_modifie_declenche_la_reserialisation` →
`test_un_champ_modifie_ne_touche_que_lui`, `test_realigned_reserialise_et_remplace` →
`test_realigned_remplace_et_retire`). Le journal dit l'arbitrage rendu par l'utilisateur avant
l'étape 4 ; **je ne peux pas le vérifier depuis le dépôt**, je le prends au mot du suivi. Les deux
tests conservent ce qu'ils cadraient, assertions inversées mais rien de relâché : le remplacement,
le retrait et le nommage du type hors contrat restent tous testés. Les trois autres tests que le
plan croyait condamnés (`test_echappements_relisibles`,
`test_caractere_de_controle_refuse_et_nomme`, `test_dump_front_conserve_l_ordre`) sont intacts —
conséquence de la décision de garder `dump_value` et d'un `raw_front` optionnel en second
paramètre.

**Élargissement de périmètre** (venv, `requirements.txt`, ré-amorçage, `venvPath`) : daté au suivi
et justifié — sans lui rien n'est exécutable. Légitime.

**Symptôme d'origine** : **disparu**, constaté par moi et non par le suivi.

### Qualité du code

- **R1** — `skills/list-dir/scripts/listdir/items.py:302-306` — le docstring de `render_item` dit
  encore « raw_front présent → reconduit à l'octet près (règle 1). raw_front None → resérialisé
  (règle 2). » Les « deux règles » n'existent plus, leur en-tête a été réécrit quatorze lignes plus
  haut, et la ligne juste en dessous appelle `dump_front` **sans condition**. C'est la
  contradiction la plus visible du diff : le premier lecteur d'`items.py` la rencontre dans la
  fonction dont le corps a changé. L'étape 6 se donnait pour objet de « réécrire ce qui documente
  la frontière » ; ce docstring lui a échappé.
- **R2** — `skills/list-dir/references/extension.md:64-68` — « `with_fields` rend une copie dont le
  texte brut est marqué périmé : c'est ce marquage, et lui seul, qui déclenche une
  resérialisation. » Faux depuis `types.py:318`. Ce fichier n'était pas dans la liste de l'étape 6
  (qui ne citait qu'`operations.md`) et n'a pas été touché : c'est la doc d'extension, celle que
  lit quiconque écrit du code contre le paquet.
- **R3** — `store.py:300`, `store.py:319` et `references/operations.md:67-68` — la règle « ne pas
  réécrire un élément conforme » est conservée à juste titre, mais sa **raison écrite** est morte :
  « le réécrire pour rien perdrait son raw_front » / « lui coûterait son `raw_front` pour rien ».
  `raw_front` n'est plus perdu par une réécriture. `operations.md` est le plus gênant : le
  paragraphe a été réécrit jusqu'à mi-phrase, et la phrase suivante contredit ce qui vient d'être
  affirmé au-dessus.
- **R4** — `items.py:_reordonne` — **un commentaire de queue est capturé par le premier champ
  ajouté**, ce qui contredit la décision journalisée (« il reste en queue, où il a été écrit »).
  Reproduit par moi :

  ```
  entrée : id, [# légende] tags, title, # commentaire final
  fields : neuf (nouveau), title, tags, id
  sortie : # commentaire final
           neuf = "x"
           title = 'simple'
           …
  ```

  `doc[cle] = …` ajoute la clé neuve **en fin de body**, donc derrière le commentaire orphelin, que
  le regroupement rattache alors à elle et emporte au réordonnancement. Le test
  `test_le_commentaire_sans_champ_derriere_reste_en_queue` ne couvre pas cette combinaison
  (commentaire final **et** champ ajouté), pourtant la plus banale : c'est exactement ce que fait
  un `migrate` après un ajout au contrat.
- **R5** — `items.py:256` et `write_item` (`items.py:311-315`) — `dump_front` **parse** désormais
  `raw_front`, et `write_item` n'attrape que `SerialiseError`. Une `ParseError` de tomlkit sur un
  front matter que `tomllib` avait accepté remonterait en traceback nu au lieu d'un `Result` fail
  nommé — le paquet convertit partout ailleurs ses échecs en `Result`. Divergence tomllib/tomlkit
  peu probable, mode d'échec néanmoins nouveau et non couvert.
- **R6** — `items.py:259` — la comparaison `doc[cle] != valeur` ne distingue pas `True` de `1` :
  `dump_front({"x": True}, "x = 1\n")` rend `x = 1`, le champ n'est pas réécrit alors que le modèle
  dit autre chose. Le contrat admet `bool` **et** `int`, donc le cas est atteignable par un
  changement de type au contrat. Étroit, mais c'est un chemin d'échec silencieux — la valeur écrite
  cesse de refléter `fields`.
- **R7** — `items.py:_reordonne` — une ligne blanche précédant un champ voyage avec lui ; si ce
  champ passe en tête, le `strip("\n")` final la supprime. Aucune promesse n'est rompue (le front
  matter d'élément est plat et sans blanc en pratique), mais « les blocs sont déplacés, jamais
  reconstruits » n'est pas tout à fait vrai de l'espacement.

Sur le reste, le code tient le style de ses voisins : docstrings en majuscules qui disent le
pourquoi, nommage français cohérent (`blocs`, `courant`, `neuf`), `cast` explicite dans
`toml_value`, garde `bool` avant `int` commentée. La garde de type maison face à tomlkit est le bon
arbitrage, et il est écrit.

### Dette induite

- **R8** — `requirements.txt` n'épingle rien (`tomlkit`, `pytest`, nus). Tout le chantier repose
  sur des garanties de préservation propres à tomlkit, et `sante_skills` ne contrôle que la
  *présence* d'une distribution, jamais sa version. Une machine qui résout une autre version de
  tomlkit peut donc reformater silencieusement là où celle-ci préserve, sans qu'aucun contrôle ne
  parle. Coût futur : un reformatage massif reproché au paquet, non reproductible ailleurs.
- **R9** — deux écrivains TOML cohabitent. C'est **assumé, tracé et daté** (dette
  `deux-ecrivains-toml-coexistent`, road-map `supprimer-dump-value`, dépréciation dans le
  docstring de `dump_value`) : je le note pour mémoire, pas comme un reproche.
- **R10** — `skills/list-dir/pyrightconfig.json` porte `"typeCheckingMode": "all"`, que pyright
  1.1.413 **rejette** (« must contain "off", "basic", "standard", or "strict" ») et remplace par le
  mode par défaut. Préexistant au chantier, hors périmètre — mais il faut le savoir pour lire la
  vérification de l'étape 4 : le « + pyright » a porté sur un mode plus faible que celui que le
  dépôt croit appliquer.

### Bloquants

Aucun.

## 2026-09-09 — clôture (2e passe) — `07ad9a6`

**Verdict** : DÉFAVORABLE

Deuxième audit de clôture, sur le commit qui traite les réserves R1-R4 et R8 de la passe
précédente. Les réserves antérieures sont bien levées ; **un défaut bloquant, non vu à la première
passe, l'est en revanche par cette seconde** : un `migrate` qui se contente de réordonner deux
champs écrit sur le disque un front matter TOML **invalide**.

### Vérifications exécutées

- `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ -q` → **457 passés, 0 échec**
  (11.86 s)
- `~/.claude/.venv/bin/python -m pytest scripts/tests/ -q` → **107 passés, 0 échec** — total **564**,
  conforme au décompte du suivi
- `python3 ~/.claude/scripts/sante_skills.py; echo $?` → **aucune sortie, code 0**
- `list-dir.py help` → **OK** (ré-amorçage `os.execv` dans le venv depuis le `python3` du PATH)
- `~/.claude/.venv/bin/python -c "import tomlkit, pytest"` → OK, **tomlkit 0.15.1, pytest 9.1.1**,
  identiques aux versions désormais épinglées dans `requirements.txt`
- `npx pyright@1.1.413 .` depuis `skills/list-dir` → **4 erreurs**, toutes
  `tests/test_prefill.py:127`, toutes préexistantes ; aucune sur le code du chantier
- `uvx ruff check` (l'outil est atteignable, contrairement à la première passe) → **5 erreurs**,
  dont **2 nouvelles** introduites par le chantier — voir R12
- `sante_skills._dependances()` sur quatre racines jouets → sans `requirements.txt` : rien ; venv
  absent : anomalie avec la commande `uv venv … && uv pip install …` ; tomlkit absent seul :
  anomalie le nommant ; **tomlkit en 0.11.0 alors que `requirements.txt` épingle 0.15.1 : liste
  vide** — voir R14
- reproduction de bout en bout de l'entrée de road-map, refaite : liste neuve, tableau sur trois
  lignes avec légende et commentaire de queue, deux champs ajoutés au contrat, `list-dir migrate`
  → `diff -u` = **deux lignes ajoutées, rien d'autre** ; relance de `migrate` → « déjà conforme,
  aucun fichier touché »
- reproduction directe du défaut R11 sur `master` (arbre extrait par `git archive`, hors dépôt) →
  **le même scénario y produit un front matter valide** : la régression est bien du chantier

### Suivi des réserves de la passe `4f47ad1`

- **R1** (docstring de `render_item` citant les « deux règles ») — **levée**, vérifiée à
  `items.py:328-331` : « Un seul chemin, sans condition ».
- **R2** (`references/extension.md`) — **levée**, le paragraphe décrit la reprojection.
- **R3** (raison morte du « ne pas réécrire un élément conforme ») — **partiellement levée**.
  `operations.md` est réécrit, et bien : la nouvelle raison (date de modification, `git status`)
  est vraie et vérifiable. Mais les **deux occurrences dans le code** subsistent — voir R13.
- **R4** (commentaire de queue adopté par un champ ajouté) — **levée**, et c'était le bon
  correctif. Reproduit par moi sur `dump_front` et de bout en bout par `migrate` : le commentaire
  final reste en queue, y compris quand un champ neuf est ajouté puis passé en tête.
- **R5**, **R6** — écartées sur arbitrage de l'utilisateur, je n'y reviens pas.
- **R7** (l'espacement voyage avec le bloc) — **non traitée, et sous-estimée par moi à la première
  passe** : je l'avais qualifiée de cosmétique (« aucune promesse n'est rompue »). C'est faux. La
  même mécanique produit du TOML illisible — R11 en est la forme sévère.
- **R8** (`requirements.txt` sans épingle) — **levée pour la déclaration** (`tomlkit==0.15.1`,
  `pytest==9.1.1`, avec le pourquoi écrit au-dessus), **pas pour le contrôle** — voir R14.
- **R9** (deux écrivains TOML), **R10** (`typeCheckingMode: "all"` rejeté par pyright, préexistant)
  — inchangées, notées pour mémoire ; R10 reste vraie, pyright l'affiche encore à chaque appel.

### Conformité à l'intention

Les cinq critères de réussite, un par un :

1. « `pytest` passe sur `skills/list-dir/scripts/tests/` » — **atteint, vérifié** (457/457).
2. « un tableau écrit à la main sur plusieurs lignes ressort identique après un `migrate` qui
   ajoute un champ » — **atteint, vérifié** hors banc de test.
3. « une entrée de tableau contenant un saut de ligne s'écrit en `"""…"""` » — **atteint,
   vérifié** : `dump_front({"notes": ["a\nb"]})` → `notes = ["""a\nb"""]`, relu par `tomllib`.
4. « un commentaire posé au-dessus d'un champ suit ce champ quand le contrat le réordonne » —
   **atteint, vérifié** par appel direct à `dump_front` avec un ordre inversé.
5. « `sante_skills.py` signale l'absence de tomlkit » — **atteint, vérifié** sur racines jouets.

**Mais un critère atteint ne suffit pas quand une garantie voisine tombe.** Le brief pose en
signal de dérive le relâchement des garanties encodées par les tests existants, et nomme
explicitement « le réordonnancement selon le contrat » parmi elles (brief, § Signaux de dérive).
Cette garantie est **cassée dans son cas le plus banal** (R11) : les tests ne l'ont pas vu, ce qui
ne la rend pas moins cassée.

**Hors-périmètre** : respecté. Ni `provenance.py`, ni l'écriture des contrats, ni les gabarits ne
sont touchés ; `dump_value` n'a vu changer que son docstring.

**Symptôme d'origine** : **disparu**, constaté par moi. C'est le paradoxe de cet audit — le
problème visé est réglé, et un problème plus grave a pris sa place sur un chemin voisin.

### Défaut bloquant

- **R11 — un `migrate` qui réordonne deux champs écrit un front matter TOML invalide.**
  `skills/list-dir/scripts/listdir/items.py:_reordonne` (blocs déplacés) et
  `items.py:split_front:53`.

  Reproduction complète, sur une liste neuve créée par `list-dir init`, contrat squelette
  (`id`, `title`), aucun tableau, aucun commentaire :

  ```
  avant :  +++            après `list-dir migrate` :   +++
           title = "Un essai"                           id = "exemple"title = "Un essai"
           id = "exemple"                               +++
           +++
  ```

  `migrate` annonce « front matter — champs réordonnés selon le contrat », « 1 changement
  appliqué », code 0. Le `list-dir validate` qui suit rend : *« front matter TOML invalide —
  Expected newline or end of document after a statement (at line 1, column 15) »*. **Le fichier
  est cassé, et c'est l'opération elle-même qui l'a cassé.** Sur `master`, le même scénario rend
  `id` puis `title` sur deux lignes.

  *Mécanique* : `split_front` (`items.py:53`) rend `raw_front` par `"\n".join(...)`, **sans saut
  de ligne final**. Le dernier item du document tomlkit a donc un `trail` vide. `_reordonne`
  déplace les blocs sans toucher à leur trivia : dès que ce dernier champ cesse d'être le dernier,
  son absence de saut de ligne colle le champ suivant à sa suite. Vérifié isolément :

  ```
  dump_front({"b": "2", "a": "1"}, 'a = "1"\nb = "2"')   -> 'b = "2"a = "1"'   ← invalide
  dump_front({"b": "2", "a": "1"}, 'a = "1"\nb = "2"\n') -> 'b = "2"\na = "1"' ← correct
  ```

  Une ligne blanche entre deux champs donne la même corruption
  (`'a = "1"\n\nb = "2"'` → `'b = "2"a = "1"'`), ce qui est la forme grave de R7.

  *Pourquoi les 457 tests ne le voient pas* : les fixtures de réordonnancement finissent par un
  commentaire de queue ou laissent le dernier champ en dernier — le seul cas où le `trail` manquant
  ne sert jamais de séparateur. La reproduction de road-map inscrite au suivi porte, elle aussi, un
  commentaire final. **Aucun test ne réordonne un front matter dont le dernier item est un champ**,
  qui est pourtant la forme de tous les éléments réels.

  *Portée* : toute liste dont un élément porte ses champs dans un ordre différent du contrat, ce
  que `migrate` est précisément là pour corriger. Le dommage est silencieux à l'écriture et ne se
  découvre qu'à la lecture suivante.

### Qualité du code

- **R12 — deux erreurs `ruff` introduites, et un décompte de référence inexact au suivi.**
  `uvx ruff check` rend 5 erreurs. Trois sont préexistantes (`E501` dans `test_contract.py:108`,
  `test_fusion.py:266` et `:292`, déjà notées au suivi). Les **deux autres sont nouvelles** :
  `E402 Module level import not at top of file` sur `list-dir.py:59` et `:60`, causées par
  l'affectation `_venv = next(...)` posée avant les imports — ruff tolérait `sys.path.insert` et le
  garde `if sys.version_info`, pas une affectation. Vérifié par différence : le même fichier privé
  du bloc `_venv` ne rend plus d'`E402`, et la version `master` du fichier passe `ruff` sans une
  erreur. Le suivi affirme « ruff : 5 erreurs, toutes préexistantes » — c'est faux, et la première
  passe d'audit n'a pas pu le contredire faute d'outil.
- **R13 — la raison morte de R3 subsiste dans le code.** `store.py:300` (« réécrire un élément que
  la migration n'a pas eu à changer lui coûterait son `raw_front` pour rien ») et `store.py:319`
  (« le réécrire pour rien perdrait son `raw_front` ») disent encore ce que `types.py:318` a rendu
  faux : une réécriture ne perd plus `raw_front`. `operations.md` a été corrigé, le code non — les
  deux se contredisent désormais mot pour mot sur la même règle.
- **R15 — code mort dans `_reordonne`.** La ligne `neuf.body.extend(courant)` et son commentaire
  « la queue sans propriétaire, laissée où elle est » ne peuvent plus rien reprendre : depuis le
  correctif de R4, `dump_front` appelle `_detacher_queue` avant, donc le dernier item du document
  est toujours une clé et `courant` est toujours vide à la sortie de la boucle. Le docstring de
  `_reordonne` continue pourtant d'expliquer une règle de queue que la fonction n'applique plus —
  elle est appliquée par `_detacher_queue`. Deux endroits disent tenir la même règle ; un seul la
  tient.

Sur le reste, le style tient celui de ses voisins : docstrings en majuscules qui disent le
pourquoi, nommage français cohérent, `cast` explicite, commentaire de `_detacher_queue` qui
raconte le défaut qu'il empêche plutôt que le code qu'il exécute. La correction de R4 est de
bonne facture et son test nomme ce qu'il protège.

### Dette induite

- **R14 — l'épingle est déclarée, jamais contrôlée.** `requirements.txt` porte désormais
  `tomlkit==0.15.1`, et le commentaire au-dessus dit bien pourquoi. Mais `sante_skills._requises`
  découpe le nom sur `[<>=!~;\[ ]` et ne garde que `tomlkit` ; `_dependances` ne compare ensuite
  que des noms de `*.dist-info`. Vérifié sur racine jouet : un venv portant **tomlkit 0.11.0** face
  à un `requirements.txt` épinglant 0.15.1 rend **une liste vide** — aucun signalement. Le risque
  décrit en R8 (un rendu tomlkit différent reformate silencieusement tous les fronts matter)
  survit donc au correctif pour toute machine dont le venv a été amorcé avant l'épingle, ou
  installé autrement. La déclaration protège l'installation neuve, pas l'existante.
- **R9** (deux écrivains TOML) et **R10** (`typeCheckingMode: "all"` rejeté) : inchangées,
  toujours tracées, rappelées pour mémoire.

### Bloquants

- **R11** — `migrate` corrompt le front matter d'un élément dont les champs sont à réordonner et
  qui ne finit pas par un commentaire. Régression par rapport à `master`, non couverte par les
  tests, silencieuse à l'écriture.

## 2026-09-09 — clôture (3e passe) — `9e9e855`

**Verdict** : RÉSERVES

Troisième audit de clôture, sur le commit qui traite le bloquant R11 et les réserves R12 à R15.
**Le bloquant est levé, vérifié de bout en bout et par différence avec `master`.** Les quatre
autres réserves de la passe précédente sont levées elles aussi. Ce qui reste tient à la
documentation et au relevé chiffré du suivi : rien qui interdise la clôture, rien non plus qu'il
faille clore sans avoir lu.

### Vérifications exécutées

- `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ -q` → **459 passés,
  0 échec** (11.60 s)
- `~/.claude/.venv/bin/python -m pytest scripts/tests/ -q` → **111 passés, 0 échec** — total **570**
- **Base de référence mesurée sur l'arbre `master` extrait par `git archive`** (hors dépôt, avec le
  même venv) → `skills/list-dir` **444**, `scripts` **101**, total **545** — voir R16
- Comparaison des tests collectés `master` vs `HEAD` → **27 ajoutés, 2 retirés** :
  `test_un_champ_modifie_declenche_la_reserialisation` et `test_realigned_reserialise_et_remplace`,
  exactement les deux réécritures annoncées et autorisées
- `uvx ruff check skills/list-dir scripts` → **3 erreurs** (`E501` : `test_contract.py:108`,
  `test_fusion.py:266`, `:292`). Même commande sur l'arbre `master` extrait → **3 erreurs, les
  mêmes**. Les deux `E402` de R12 ont bien disparu
- `npx pyright` depuis `skills/list-dir` → **4 erreurs**, toutes `tests/test_prefill.py:127`,
  toutes préexistantes ; toujours précédées du rejet de `"typeCheckingMode": "all"` (R10)
- `python3 ~/.claude/scripts/sante_skills.py; echo $?` → **aucune sortie, code 0**
- `list-dir.py help` lancé par le `python3` de Linuxbrew **et** par `.venv/bin/python` → **code 0**
  dans les deux cas ; le ré-amorçage `os.execv` tient sous sa nouvelle forme à `if` unique
- `~/.claude/.venv/bin/python -c "import tomlkit, pytest"` → tomlkit **0.15.1**, pytest **9.1.1**,
  conformes aux épingles de `requirements.txt`
- **Reproduction du bloquant R11, refaite indépendamment** — liste neuve par `list-dir init`,
  contrat squelette, élément `title` puis `id`, aucun tableau, aucun commentaire :
  `list-dir migrate` → « champs réordonnés selon le contrat », code 0, et le fichier obtenu porte
  `id = "exemple"` puis `title = "Un essai"` sur **deux lignes** ; `list-dir validate` qui suit →
  **conforme, code 0**. Le front matter n'est plus corrompu
- Formes voisines du même défaut, par appel direct à `dump_front` :
  `('a = "1"\n\nb = "2"\n', ordre b,a)` → `'b = "2"\na = "1"'` (valide) ;
  `('i = "0"\nt = "1"\n# fin\n', champ neuf + réordonnancement)` → les trois champs séparés, `# fin`
  toujours en queue
- Bout en bout sur un cas complet — tableau sur trois lignes, légende au-dessus, ligne blanche,
  dernier item = champ — puis **deux champs ajoutés au contrat** et `migrate` → `diff -u` = **deux
  lignes ajoutées, rien d'autre** ; `validate` conforme ; `migrate` rejoué → « déjà conforme, aucun
  fichier touché », fichier identique à l'octet
- `migrate --drop` sur le champ `tags` mis en forme → champ **et sa légende** retirés ensemble,
  conformément à la décision journalisée
- `dump_front({"notes": ["a\nb", "c"]})` → `notes = ["""a\nb""", "c"]`, relu par `tomllib` ;
  `dump_front({"txt": "x\ty\rz\x00"})` → échappé et relu à l'identique
- `sante_skills._dependances()` sur huit racines jouets → sans `requirements.txt` : rien ; venv
  absent : anomalie avec la commande `uv venv … && uv pip install …` ; tomlkit absent : anomalie le
  nommant ; **tomlkit 0.11.0 face à une épingle 0.15.1 : « tomlkit 0.11.0 au lieu de 0.15.1 »** ;
  version conforme : rien ; contrainte souple `>=` : rien ; nom à tirets `ruamel-yaml` : rien ;
  extras `uvicorn[standard]` : rien

### Suivi des constats antérieurs

- **R11** (bloquant — `migrate` corrompt un front matter réordonné) — **LEVÉE**. Le correctif est
  posé au bon endroit : le saut de ligne est garanti au parsing dans `dump_front`
  (`items.py:264-267`), donc vaut pour tous les items sans que `_reordonne` ait à connaître la
  subtilité. Deux tests le cadrent (`test_reordonner_ne_colle_pas_deux_champs`,
  `test_un_champ_ajoute_ne_se_colle_pas_au_dernier`) et la fixture
  `FRONT_FINISSANT_PAR_UN_CHAMP` porte, en commentaire, la raison pour laquelle les autres
  fixtures masquaient le défaut. Reproduit levé par moi, de bout en bout et isolément.
- **R12** (deux `E402` introduites, décompte ruff faux au suivi) — **LEVÉE**. `ruff` rend
  3 erreurs sur la branche comme sur `master`, et ce sont les mêmes. La forme retenue — un `if`
  unique avec expression d'affectation — est expliquée sur place par un commentaire qui dit
  pourquoi la contrainte impose cette forme.
- **R13** (raison morte « perdrait son raw_front » dans le code) — **LEVÉE**. `store.py:296-300`,
  `store.py:318-320` et l'en-tête de `test_store_ecriture.py` disent maintenant la vraie raison
  (date de modification neuve, bruit dans `git status`), cohérente avec `operations.md`. Aucune
  occurrence de `raw_front` résiduelle hors de son usage réel dans le paquet.
- **R14** (épingle déclarée, jamais contrôlée) — **LEVÉE**. `_requises` rend désormais
  `(nom, version)` et `_dependances` compare la version lue du `*.dist-info` ; le découpage sur le
  **dernier** tiret est correct et testé sur un nom à tirets. Message d'anomalie distinct de celui
  de l'absence, avec la commande de réalignement.
- **R15** (code mort dans `_reordonne`) — **LEVÉE pour le code** (`neuf.body.extend(courant)`
  supprimé, `courant` renommé `bloc`), **partiellement pour la documentation** — voir R17.
- **R7** (l'espacement voyage avec le bloc) — **toujours ouverte, et désormais sans danger
  démontré** : j'ai vérifié que sa forme grave était bien R11 et qu'elle est corrigée. Il reste
  qu'une ligne blanche précédant un champ disparaît si ce champ passe en tête
  (`'a = "1"\n\nb = "2"\n'` → `'b = "2"\na = "1"'`). Sortie valide, données intactes ; la phrase
  « les blocs sont déplacés, jamais reconstruits » reste inexacte de l'espacement seul.
- **R5**, **R6** — écartées sur arbitrage de l'utilisateur, je n'y reviens pas.
- **R1**-**R4**, **R8** — levées à la passe précédente, revérifiées incidemment : les docstrings et
  la doc d'extension sont à jour, le commentaire de queue ne se fait pas adopter.
- **R9** (deux écrivains TOML, tracé en dette et en road-map), **R10** (`typeCheckingMode: "all"`
  rejeté par pyright, préexistant) — inchangées, rappelées pour mémoire.

### Conformité à l'intention

Les cinq critères de réussite, un par un :

1. « `pytest` passe sur `skills/list-dir/scripts/tests/` » — **atteint, vérifié** (459/459).
2. « un tableau écrit à la main sur plusieurs lignes ressort identique après un `migrate` qui
   ajoute un champ » — **atteint, vérifié** hors banc de test, sur une liste réelle : deux lignes
   ajoutées, tableau, indentation, légende et ligne blanche intacts.
3. « une entrée de tableau contenant un saut de ligne s'écrit en `"""…"""` » — **atteint,
   vérifié**, relecture par `tomllib` à l'appui.
4. « un commentaire posé au-dessus d'un champ suit ce champ quand le contrat le réordonne » —
   **atteint, vérifié** par `migrate` réel : la légende de `tags` a suivi `tags`, et le commentaire
   de queue est resté en queue.
5. « `sante_skills.py` signale l'absence de tomlkit » — **atteint, vérifié**, et il signale
   désormais aussi une version divergente.

**Hors-périmètre** : respecté. Le diff ne touche ni `provenance.py`, ni l'écriture des contrats, ni
les gabarits ; `dump_value` n'a vu changer que son docstring. Aucun enroulement automatique : sans
`raw_front`, `dump_front` sort canonique et sur une ligne.

**Signaux de dérive** : un seul matérialisé, celui qui était annoncé — deux tests existants
réécrits, et **deux seulement**, confirmé par comparaison des tests collectés entre `master` et
`HEAD`. Levée autorisée d'après le journal ; je la prends au mot du suivi, faute de pouvoir la
vérifier depuis le dépôt.

**Élargissement de périmètre** (venv, `requirements.txt`, ré-amorçage, `venvPath`) : daté au suivi,
justifié, et vérifié fonctionnel sous les deux interpréteurs.

**Symptôme d'origine** : **disparu**, constaté par moi.

### Réserves de cette passe

- **R16 — le relevé chiffré du suivi est faux, pour la seconde fois.** L'« État courant » dit
  « 551 tests avant le chantier, 570 après (19 ajoutés, 0 retiré) ». Mesuré sur l'arbre `master`
  extrait par `git archive`, avec le même venv : **545 avant**, 570 après, soit **+25**. Et la
  comparaison des tests collectés montre **27 ajouts pour 2 retraits** — les deux réécritures
  autorisées, qui ne sont pas « 0 retiré » au sens strict même si rien n'est relâché. Le fond est
  bon (la couverture augmente, aucune garantie n'est perdue) ; c'est la traçabilité qui pèche, et
  R12 avait déjà sanctionné un relevé de ce type au même endroit. Un chiffre qu'on n'a pas remesuré
  après correction est un chiffre qu'on ne peut pas citer.
- **R17 — `_reordonne` documente encore une règle qu'il n'applique plus.** `items.py:309-321` : la
  correction de R15 a **ajouté** le paragraphe « LA QUEUE A DÉJÀ ÉTÉ DÉTACHÉE par l'appelant »
  sans **retirer** celui qui suit (« CE QUI TRAÎNE EN FIN DE DOCUMENT N'A PAS DE PROPRIÉTAIRE …
  Il reste donc en queue »), lequel décrit mot pour mot ce que fait `_detacher_queue` et que dit
  déjà son propre docstring. Le lecteur trouve donc la même règle énoncée à deux endroits, dont un
  qui ne l'implémente pas — c'est la configuration exacte qui a produit R1, R3 et R13. Coût :
  faible aujourd'hui, réel au prochain changement de la règle de queue, qui devra être répercuté
  à deux endroits sans que rien ne le rappelle.
- **R18 — une épingle assortie d'un marqueur d'environnement n'est pas contrôlée.**
  `sante_skills._requises` (`scripts/sante_skills.py`) met la version à `None` dès que la partie
  droite contient un `;` : `tomlkit==0.15.1 ; python_version >= "3.12"` est donc traité comme une
  contrainte souple. Vérifié sur racine jouet — liste vide face à une version divergente. Le choix
  est défendable (le marqueur peut rendre la ligne inapplicable), mais le docstring affirme
  « SEUL `==` DONNE UNE VERSION » sans dire cette exception, et aucun test ne la cadre. Le
  `requirements.txt` du dépôt n'utilise pas de marqueur : c'est un angle mort, pas un défaut actif.

Sur le reste, la qualité tient : le correctif de R11 est posé à la bonne couche et son test dit
la régression vécue plutôt que le code exécuté ; `_detacher_queue` raconte le défaut qu'il empêche ;
le nouveau `_requises` documente pourquoi une contrainte souple ne se vérifie pas ; le nommage
français et la densité de commentaires suivent les fichiers voisins.

### Bloquants

Aucun.
