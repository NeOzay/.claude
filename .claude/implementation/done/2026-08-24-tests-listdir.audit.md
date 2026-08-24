---
slug: tests-listdir
---

## 2026-08-24 — clôture — `f1923d2`

**Verdict** : RÉSERVES

### Vérifications exécutées

Toutes lancées depuis la racine du dépôt (`/home/debian/.claude`), sur `f1923d2`.

- `uvx pytest skills/list-dir/scripts/tests -q` → **241 passed** en 3.68 s
- `uvx pytest scripts/tests -q` → **67 passed** (suite existante intacte)
- `(cd skills/list-dir && uvx ruff check .)` → **All checks passed!**
- `(cd skills/list-dir && uvx --with pytest basedpyright)` → **0 errors, 0 warnings, 0 notes**
- `uvx --with pytest basedpyright` (racine) → **0 errors, 0 warnings, 0 notes**
- `grep -ril 'dette\|debt' skills/list-dir/` → **aucun résultat**, code 1 (invariant tenu)
- `python3 scripts/check_pipeline.py` → **Pipeline conforme**, code 0
- `uvx pytest skills/list-dir/scripts/tests -q` depuis `/tmp` (chemin absolu) → **241 passed**
  (aucune dépendance au répertoire courant)
- `uvx pytest scripts/tests -q` depuis `skills/list-dir/` → **241 passed** — voir **R3**
- `uvx pytest scripts/tests skills/list-dir/scripts/tests -q` → **ÉCHEC de collecte, 3 erreurs**
  — voir **R3**
- `uvx pytest skills/list-dir/scripts/tests scripts/tests -q` → **308 passed** (ordre inverse)
- `uvx --with pytest-cov pytest … --cov=…/listdir` → **95 %** sur la bibliothèque
  (`store.py` 94 %, `items.py` 98 %, `contract.py` 96 %, `types.py` 98 %, `loader.py` 95 %).
  Mesure d'information seulement : le brief écarte explicitement tout seuil chiffré.
- `uvx ruff check .` (racine) → 3 erreurs, **toutes sur `statusline-command.py`**, présentes sur
  `master` et déjà consignées au registre (`statusline-hors-des-linters.md`). Sans rapport avec ce
  chantier ; le brief ne porte l'exigence `ruff` que sur le skill.
- `git diff --stat master...tests-listdir` → 18 fichiers, 2752 insertions, 6 suppressions.
  Part `listdir/` : **74 lignes changées sur 2 fichiers**. Part `tests/` : **2270 lignes sur 11
  fichiers**.
- Reproduction manuelle de la fence en préambule (script ad hoc sur `tmp_path`) → voir **R2**.

Aucune commande du suivi ni du brief n'est restée non exécutée.

### Conformité à l'intention

Les dix étapes sont cochées ; l'audit juge le chantier entier.

- **Critère « les tests couvrent la logique métier et les commandes »** : *atteint, vérifié*.
  214 fonctions de test / 241 cas, répartis sur les huit modules de la bibliothèque et exerçant par
  la CLI `init`, `new`, `validate --filled`, `list`, `show`, `merge`, `move` et `help`. Réserve
  partielle sur `derive` et `migrate` : voir **R4**.
- **Critère « garantir et cadrer le comportement du module »** : *atteint*. Les tests fixent des
  comportements nommés, pas des lignes : l'aller-retour octet pour octet de `read_item`/
  `render_item`, la frontière de resérialisation de `with_fields`, la suspension du contrôle de type
  sur un marqueur, le rejeu sans écriture de `migrate`, l'atomicité de `derive`, le renommage pur
  vérifié par `git log --follow`. C'est du cadrage de comportement, pas de la couverture de ligne.
- **Critère « pas de seuil de couverture chiffré »** : *respecté*. Aucune configuration `--cov`,
  aucun `fail_under`, aucune dépendance `pytest-cov` introduite (je l'ai ajoutée hors dépôt pour
  mesurer, et j'ai supprimé l'artefact `.coverage` produit).
- **Critère « les tests vivent dans `skills/list-dir/scripts/tests/`, lancés par
  `uvx pytest skills/list-dir/scripts/tests -q` »** : *atteint, vérifié*.
- **Critère « le gros des cas par la bibliothèque, la CLI en sous-processus pour ce qu'elle seule
  porte »** : *atteint*. Un seul fichier passe par le sous-processus (`test_entree_cli.py`, 19 cas
  sur 214), et il n'y exerce que codes de sortie, canal de sortie, énumération des commandes,
  refus de surcharge, absence de `git` du `PATH` et garde de version. Aucun doublon de logique
  métier.
- **Critère « `uvx ruff check .` et `uvx --with pytest basedpyright` verts sur le skill »** :
  *atteint, vérifié* (ci-dessus).
- **Critère « un comportement jugé faux se corrige DANS ce chantier »** : *atteint pour deux des
  trois entrées visées, avec un solde partiel* — voir **R1** et **R2**. La troisième
  (`source-verbatim-perd-italiques`) porte sur le contrat du registre `technical-debt`, pas sur
  `listdir` : elle relève du hors-périmètre « les trois registres de `todo/` », et ne pas la traiter
  est conforme. Le journal du suivi annonçait pourtant « on corrige » pour les trois sans jamais
  consigner ce qu'il est advenu de celle-là — voir **R6**.
- **Hors-périmètre** : *respecté*. `grep -ril 'dette\|debt' skills/list-dir/` sans résultat, aucun
  fichier de `.github/workflows` créé, aucun découpage ni renommage de module de `listdir/`, aucun
  seuil de couverture. Les deux seuls fichiers de `listdir/` touchés le sont uniquement pour deux
  comportements que des tests nomment.
- **Signaux de dérive** : *aucun matérialisé*. 74 lignes sur `listdir/` contre 2270 sur les tests —
  le rapport est de 1 à 30, la ligne n'a jamais été approchée. Aucun test ne lit le vrai dépôt :
  les trois seuls `__file__` de la suite visent le `sys.path` du `conftest`, le chemin de
  `list-dir.py` à lancer, et le `__file__` d'un module-jouet posé sous `tmp_path` ; tout le reste
  monte sur `tmp_path`. Vérifié en pratique par l'exécution depuis `/tmp`.
- **Symptôme d'origine** : *disparu*. Les deux défauts trouvés à la lecture sont désormais tenus par
  des tests nommés — le guillemet dans `init_list` (`test_store_ecriture.py`) et le `## ` en bloc de
  code (`test_items.py`, `test_derive_merge.py`) — et la non-régression se rejoue en une commande.

### Qualité du code

- **R1** — *solde partiel de `where-compare-textuellement`.* L'entrée de dette demande deux choses :
  « **Documenter la règle** dans `references/contrat-liste.md` […] **et** décider du cas de
  l'absence ». Le chantier a fait la seconde (le critère vide devient la forme explicite de
  l'absence, `store.py:_correspond`) et pas la première. Le passage de
  `skills/list-dir/references/contrat-liste.md` qui décrit `list --where` (ligne ~228) est inchangé,
  et le `help=` de `--where` dans `listdir/commands/list.py:26` ne mentionne ni la comparaison
  textuelle ni le critère vide. La règle n'existe que dans la docstring de `ListStore.where` — donc
  invisible à l'utilisateur de la CLI, qui est exactement la personne que l'entrée de dette dit
  piégée (« elle n'est écrite nulle part, donc personne ne peut s'y fier ni s'en méfier »). Le
  comportement livré est le bon ; c'est sa moitié documentaire qui manque.

- **R2** — *solde partiel de `fence-non-fermee-diagnostic-trompeur`.* `fence_ouverte` n'est appelée
  que sur le **corps d'une section** (`store.py`, boucle `for title, corps in item.sections.items()`).
  Un bloc de code ouvert **avant le premier `## `** — dans le préambule du corps, que
  `parse_sections` ignore par construction — n'est vu par aucun contrôle : il absorbe toutes les
  sections, `item.sections` est vide, et `validate` rend le diagnostic trompeur d'origine. Mesuré
  sur une liste-jouet montée en `tmp_path` :

  ```
  élément dont le corps commence par ``` non refermée, puis « ## Constat »
  → item.sections = dict_keys([])
  → validate : « section « Constat » — manquante »
  ```

  C'est mot pour mot le message que l'entrée de dette qualifie de faux : « section manquante sur une
  section qui est pourtant écrite dans le fichier, sous les yeux du lecteur ». Le déclencheur est
  plus étroit que celui traité (il faut une fence avant tout titre), et le solde annoncé dans
  l'entrée ne parle que de sections — la lettre est donc tenue, l'esprit à moitié. Aucun test ne
  nomme ce cas.

- **R3** — *les deux suites du dépôt ne se lancent plus dans une même invocation de `pytest`,
  et le résultat dépend de l'ordre des arguments.* Mesuré :

  ```
  $ uvx pytest scripts/tests skills/list-dir/scripts/tests -q
  ERROR scripts/tests/test_bout_en_bout.py
  ERROR scripts/tests/test_controle_1.py
  ERROR scripts/tests/test_controle_2.py
  E   ImportError: cannot import name 'CONTRAT_MINIMAL' from 'conftest'
      (/home/debian/.claude/skills/list-dir/scripts/tests/conftest.py)
  Interrupted: 3 errors during collection

  $ uvx pytest skills/list-dir/scripts/tests scripts/tests -q
  308 passed
  ```

  Aucun `__init__.py` n'existe dans l'une ni l'autre suite : le nouveau `conftest.py` occupe le nom
  de module `conftest` dans `sys.modules` et masque celui de la suite préexistante, dont trois
  fichiers font `from conftest import …`. Le chantier a diagnostiqué exactement cette collision
  (journal du 2026-08-24, d'où la création de `jouet.py`) mais ne l'a résolue que dans le sens qui
  gênait sa propre suite. La commande contractuelle du brief lance chaque suite séparément et reste
  verte, donc aucun critère n'est en échec ; la fragilité est réelle et non consignée. Le même piège
  frappera la prochaine suite ajoutée au dépôt.

- **R4** — *`derive` et `migrate` ne sont exercés par aucun test de la CLI.* Leurs `register()` et
  leurs drapeaux (`--template`, `--drop`, `--dry-run`) ne passent que par la bibliothèque, quand les
  huit autres commandes sont exercées bout en bout. Constat **déjà identifié et consigné par le
  chantier** (suivi, « Constats à verser au registre »), reste de la réserve Q2 du relecteur de plan.
  Je le confirme et le maintiens ouvert : c'est le seul écart au critère « couvrir les commandes ».

- **R5** — *la garde de version de `list-dir.py` est vérifiée par son rang dans l'AST, pas par son
  effet.* `test_entree_cli.py:245` prouve que le contrôle de version précède tout import de
  `listdir` ; le message qu'il imprime et le code qu'il rend ne sont jamais exécutés, faute d'un
  interpréteur antérieur à 3.12 sur la machine. Constat **déjà consigné par le chantier**. Le
  contournement est honnête et le test attrape la seule régression plausible (un import remonté
  au-dessus de la garde) ; la réserve tient au fait que le brief cite la garde de version parmi ce
  que la CLI seule porte et devait exercer.

- **R6** — *`source-verbatim-perd-italiques` sort du chantier sans trace.* Le journal du suivi
  annonce, pour les trois entrées de dette décrivant des comportements jugés faux, une « application
  par défaut : on corrige ». Deux sont ensuite déclarées soldées avec leur raisonnement ; la
  troisième disparaît du journal sans une ligne. Elle est légitimement hors-périmètre — elle porte
  sur la description d'un champ du registre `technical-debt`, pas sur `listdir` — mais rien dans le
  suivi ne le dit, et un lecteur ultérieur ne peut pas distinguer un arbitrage d'un oubli.

- **R7** — *`--where champ=` ne distingue pas un champ absent d'un champ valant la chaîne vide.*
  `_correspond(None, "")` rend `True`, et `_correspond("", "")` aussi. TOML n'a pas de valeur nulle,
  donc l'ambiguïté ne peut naître que d'un champ explicitement écrit `champ = ""` — cas légal, non
  interdit par le contrat, non couvert par un test. Coin sombre mineur, à connaître avant de faire
  reposer un flux sur ce filtre.

Hors ces constats : le style des tests suit fidèlement `scripts/tests/` — `from __future__ import
annotations` en tête, fixtures et helpers nommés en français, dépôt-jouet monté sur `tmp_path`,
docstrings qui expliquent *pourquoi* le cas existe plutôt que ce qu'il fait, en-têtes de fichier qui
justifient l'existence du fichier. Les deux correctifs de `listdir/` reprennent la densité et le ton
des commentaires en majuscules du paquet. Les fixtures git de `test_move.py` posent leur identité en
configuration **locale** : aucun test ne dépend de la machine.

### Dette induite

- **R8** — *`_scan_fences` est bien la source unique, mais `fence_ouverte` la parcourt en entier
  pour n'en garder que la dernière valeur.* `items.py:fence_ouverte` itère toutes les lignes du
  texte et écrase `ouverte` à chaque tour. Le coût est linéaire et négligeable à cette échelle, et
  le choix est explicitement argumenté (une seule définition de ce qu'est un bloc de code) : je le
  note pour mémoire, pas comme un défaut. C'est le bon arbitrage.
- **R9** — *deux `pyrightconfig.json` élargis, hors de la liste « Fichiers touchés » du plan.* Le
  plan annonçait que `pyrightconfig.json` serait couvert « sans retouche » ; `extraPaths` a dû être
  élargi dans les deux fichiers pour que `from jouet import …` résolve. L'écart est **daté,
  justifié et consigné au journal du suivi**, donc légitime au sens du contrat (le suivi fait foi) ;
  il vaut d'être connu parce qu'il contredit un argument de cadrage — l'emplacement des tests avait
  été choisi *précisément* pour ne toucher aucune configuration, et il en a touché deux. La
  décision d'emplacement reste la bonne, sa justification est simplement moins forte qu'annoncée.
- Aucune duplication introduite, aucune abstraction créée sans nécessité, aucun couplage nouveau de
  `listdir/` vers ses consommateurs (invariant de généricité vérifié). Les helpers de test sont
  centralisés dans `jouet.py` plutôt que recopiés d'un fichier à l'autre.

### Bloquants

Aucun. Tous les critères de réussite sont atteints et vérifiés par exécution ; le hors-périmètre est
intact ; aucun signal de dérive ne s'est matérialisé. Les neuf constats sont des réserves : deux
soldes de dette incomplets (**R1**, **R2**), une fragilité d'outillage non consignée (**R3**), deux
lacunes de couverture déjà reconnues par le chantier (**R4**, **R5**), une trace manquante au
journal (**R6**), un coin sombre mineur (**R7**), et deux notes de dette assumée (**R8**, **R9**).

Point d'attention pour la clôture : **R1** et **R2** portent sur des entrées du registre que le
chantier déclare soldées. Elles sont encore présentes dans
`.claude/implementation/todo/technical-debt/`. Les sortir du registre en l'état inscrirait comme
réglé ce qui ne l'est qu'en partie — soit compléter le solde, soit consigner le reste plutôt que de
retirer l'entrée.
