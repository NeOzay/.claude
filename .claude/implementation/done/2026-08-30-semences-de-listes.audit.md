---
slug: semences-de-listes
---

## 2026-08-30 — clôture — `334927f`

**Verdict** : RÉSERVES

### Vérifications exécutées

Arbre propre sur `334927f` (`git status --short` muet), toutes les commandes lancées depuis
`/home/debian/.claude` ou `skills/list-dir/` selon ce que le suivi déclare.

- `cd skills/list-dir && uvx pytest scripts/tests/ -q` → **277 passed in 5.61s** (étape 10)
- `cd skills/list-dir && uvx ruff check .` → **All checks passed!**
- `cd skills/list-dir && uvx --with pytest basedpyright` → **0 errors, 0 warnings, 0 notes**
- `python3 scripts/check_pipeline.py` → **Pipeline conforme.** (sortie 0)
- `python3 scripts/sante_skills.py` → sortie 0, aucune anomalie
- `grep -ril 'dette\|debt' skills/list-dir/` → **aucune sortie** (sortie 1) — critère 7 atteint
- `grep -c 'douze commandes' skills/list-dir/SKILL.md` → **2** (étape 6 ; le plan attendait 1, les
  deux occurrences sont le frontmatter et le titre de section — pas un échec)
- `grep -c 'list-dir contract' skills/implementation-tracker/references/dette.md` → **2** (étape 8)
- `grep -c '| \`title\` | requis |' …/dette.md` → **0** ; `grep -c 'init .*--def' …/dette.md` → **1**
- `sed -n '68,90p' skills/debt-review/SKILL.md | grep -c 'dette.md'` → **1** (étape 9)
- `list-dir help` → **« Commandes génériques (12) »**, `defs` et `contract` présentes
- Bout en bout dans un projet neuf hors dépôt (`$TMP/projet/.claude`, `PATH` sur `bin/list-dir`) :
  - `list-dir defs` → ancrages imprimés (`projet : …/projet/.claude`, `config : /home/debian/.claude`),
    les trois définitions en `rang 4  config:implementation-tracker`, sortie 0
  - `list-dir init .claude/todo/<l> --def <l>` × 3 → sortie **0** chacune
  - `list-dir validate .claude/todo/<l>` × 3 → **« 0 élément(s) conformes au contrat »**, sortie 0
    (l'amorçage ne crée aucune entrée — signal de dérive non matérialisé)
  - `ls …/technical-debt/.list/templates/` → `review.md`, `review.toml` (les gabarits ont suivi)
  - `list-dir new … essai` puis `list-dir derive … --template review` → **« 1 fiche(s) à
    instruire »**, sortie 0
  - `list-dir contract …/technical-debt` → imprime le contrat en vigueur, sortie 0
- Fidélité des semences : `diff` de chacun des trois `contract.toml` et des deux
  `templates/review.{toml,md}` entre `.claude/implementation/todo/…/.list/` et
  `skills/implementation-tracker/list-dir/…` → **identiques** (hors-périmètre « les contrats ne
  changent pas » respecté)
- Précédence : définition `technical-debt` posée en `<projet>/.claude/list-dir/` →
  `defs` affiche `rang 1  projet  (masque config:implementation-tracker)` et
  `init --def technical-debt` amorce bien celle du rang 1 (`name = "surcharge-projet"`), sortie 0
- Définition sans skill porteur (`<projet>/.claude/list-dir/maison/`) → `init --def maison` sortie 0,
  `validate` sortie 0
- Ambiguïté à rang égal (`skills/a` et `skills/b` du projet, même nom) → sortie **1**, message
  **« définition « dupe » ambiguë — 2 racines de même rang : …/a/list-dir/dupe, …/b/list-dir/dupe »**
- `init --def inexistante` → sortie 1, **« introuvable ; connues : maison, technical-debt, … »**
- `init --def X --from Y` → sortie **2**, `argparse` : « argument --from: not allowed with --def »
- `init --from /nexistepas` et `--from <répertoire sans contrat>` → sortie 1, et **la cible n'est pas
  créée** (`ls .claude/t8` → No such file or directory) : rien de bâti à moitié
- Contrat de définition invalide → sortie 1, message nommant le fichier **de la définition**, cible
  non créée
- `list-dir init <cible>` sans option → contrat squelette **identique octet pour octet** à celui de
  `master` (`name`/`description`, `[fields.id]`, `[fields.title]`, `[sections] required=["Constat"]
  optional=[]`)

Aucune commande de vérification déclarée n'est restée non exécutée.

### Conformité à l'intention

Un par un, les sept critères de réussite du brief (repris à l'identique dans le suivi) :

1. « amorcer une liste par le nom de sa définition produit une liste dont `validate` sort 0 » —
   **atteint, vérifié**.
2. « les trois registres s'amorcent dans un projet vide, puis `validate` passe sur les trois » —
   **atteint, vérifié** dans un `$TMP` hors dépôt.
3. « `derive` fonctionne après amorçage : `templates/review.{toml,md}` ont suivi » — **atteint,
   vérifié**. À noter, sans que ce soit un défaut du chantier : sur une liste fraîchement amorcée et
   donc vide, `derive` sort **1** (« aucun élément — il n'y a rien à projeter »), comportement
   antérieur au chantier. Voir **R6**.
4. « une définition posée dans `<projet>/.claude/list-dir/<nom>/` s'amorce sans qu'aucun skill la
   porte » — **atteint, vérifié**.
5. « `init` sans définition nommée produit le squelette actuel, inchangé » — **atteint, vérifié** par
   comparaison avec la sortie de `master`.
6. « deux définitions de même rang portant le même nom font sortir la commande non nul, en les
   nommant toutes les deux » — **atteint, vérifié** pour `init --def`. Réserve sur `defs`, qui rend
   0 et présente la paire comme un masquage : voir **R2**.
7. « `grep -ril 'dette\|debt' skills/list-dir/` ne rend toujours aucune sortie » — **atteint,
   vérifié** (sortie vide, code 1).

**Hors-périmètre** : respecté sur les quatre points. Les contrats ne changent pas (prouvé par
`diff`) ; aucune commande existante autre que `init` n'est modifiée — le diff ne touche que
`commands/init.py`, plus deux modules neufs et la seule `init_list` dans `store.py` ; aucun rang
« plugins » n'a été ajouté ; `debt-review/references/gabarit-rapport.md` n'est pas touché. La
commande neuve `contract`, exclue par la lettre du brief (« aucune commande existante autre que
`init` n'est modifiée » laissait la porte ouverte à une commande neuve), est explicitement ratifiée
par le suivi et le plan (Q1/exception d'étape 8) : le suivi fait foi, ce n'est pas une dérive.

**Signaux de dérive** : aucun matérialisé.
- `list-dir` ne connaît pas le mot « dette » (grep vide) ; le journal montre que le signal s'est
  déclenché en cours de route sur les exemples et qu'il a été traité (renommés en `recettes`).
- Découverte par arborescence, pas par registre : `definitions.py` n'a que `is_dir()`, `iterdir()`
  et `glob`, aucun index persisté.
- Aucune composition de contrats : `_read_definition` lit un texte et `init_list` l'écrit tel quel —
  ni héritage, ni fusion, ni surcharge de champs.
- Aucune entrée créée à l'amorçage (`validate` → 0 élément).
- Documentation décrivant un contrat que l'outil n'applique pas : c'est précisément ce que l'étape 8
  supprime dans `dette.md`. Deux résidus mineurs subsistent malgré tout — **R2** et **R4**.

**Symptôme d'origine** — « dans un projet neuf, l'Étape 0 de `debt-review` rend trois `ÉCHEC` et
aucune étape ne dit quoi faire ensuite » : **traité, mais imparfaitement refermé**. Le chemin de
sortie existe et fonctionne bout en bout, mais l'Étape 0 porte désormais deux consignes
contradictoires — voir **R1**, qui est la réserve principale de cet audit.

**Divergence brief / suivi** : le brief fixait les rangs 3/4 par
`Path(which("list-dir")).resolve().parents[3]` ; l'implémentation ancre par remontée jusqu'à un
répertoire nommé `.claude`. La divergence est datée, motivée et ratifiée au journal de décisions du
suivi (2026-08-30) et au plan (Q1). Le suivi faisant foi, **ce n'est pas un écart** : je le consigne
pour la trace, pas comme constat. J'ai vérifié le motif invoqué — le paquet appelé par chemin rend
bien les rangs 3/4 par `Path(__file__)` sans dépendre du `PATH`.

### Qualité du code

- **R1** — `skills/debt-review/SKILL.md`, Étape 0 — **contradiction laissée en place**. Le bloc
  ajouté dit « Les amorcer depuis les définitions embarquées, puis reprendre cette étape », tandis
  que la puce préexistante, une douzaine de lignes plus bas et dans la même étape, dit toujours :
  « **Registre absent** → le dire et s'arrêter. Ce skill relit un registre existant ; il n'en crée
  pas ». Un lecteur de l'Étape 0 reçoit donc deux instructions inconciliables pour le même état.
  L'étape 9 du suivi ne visait que l'ajout du renvoi ; la réconciliation de l'ancienne puce n'a pas
  été faite, et c'est ce qui empêche de dire que le symptôme d'origine est proprement refermé.
  La commande de vérification de l'étape 9 (`sed -n '68,80p' … | grep -c 'dette.md'`) ne pouvait pas
  l'attraper : elle ne regarde que la fenêtre qui vient d'être écrite.

- **R2** — `skills/list-dir/scripts/listdir/commands/defs.py:_ligne` — **`defs` annonce un vainqueur
  là où `init --def` refuse de choisir**. Sortie réelle avec deux définitions homonymes de rang 2 :
  `dupe  rang 2  projet:a  (masque projet:b)`, code de sortie 0 ; puis `init --def dupe` sort 1 en
  déclarant l'ambiguïté. `_ligne` prend `portee[0]` comme gagnante et traite tout le reste comme
  masqué, sans jamais comparer les rangs — alors que `resolve()`, lui, teste l'égalité de rang. La
  seule commande faite pour rendre la résolution découvrable décrit donc un comportement que l'outil
  n'applique pas, ce qui est exactement le mode de défaillance que `contrat-liste.md` met en garde
  deux paragraphes plus haut (« choisir en silence ferait dépendre le contrat d'une liste de l'ordre
  de parcours d'un répertoire »). Aucun test ne couvre ce cas : `test_defs_dit_qu_une_definition_en
  _masque_une_autre` n'exerce que des rangs différents.

- **R3** — `skills/list-dir/scripts/listdir/commands/init.py:command` — **`--name` et
  `--description` sont acceptés puis jetés en silence avec `--def`/`--from`**. Vérifié :
  `init .claude/t7 --def maison --name "MonNom" --description "Ma desc"` sort **0** et produit
  `name = "surcharge-projet"`. Le choix de ne pas écraser le contrat d'une définition est juste et
  motivé dans la docstring de `init_list` ; ce qui est en cause est le silence. Le paquet se donne
  pour doctrine de supprimer les échecs ouverts — la docstring de `init_list` le dit mot pour mot
  (« un échec ouvert, exactement ce que ce paquet existe pour supprimer ») — et un argument accepté,
  sans effet et sans un mot, en est un. Un refus par `argparse` (troisième branche du groupe
  d'exclusion) ou un message auraient tenu la même règle. Cas voisin, plus bénin : `--def ""`
  retombe silencieusement sur le squelette.

- **R4** — `skills/implementation-tracker/references/dette.md` — **la phrase de remplacement est
  moins exacte que le tableau qu'elle remplace**. L'ancien texte disait « rendent facultatives les
  deux du milieu » (`Pourquoi c'est gênant`, `Pour solder`) ; le nouveau dit « rendent facultatives
  celles qui disent le problème ». Or `## Constat` — qui dit le problème — reste `required` dans
  `technical-debt-solde/contract.toml` et `technical-debt-ecarte/contract.toml` (vérifié :
  `required = ["Constat", "Soldé le"]`). La formulation vague peut se lire comme rendant `Constat`
  facultatif, c'est-à-dire décrire un contrat que l'outil n'applique pas — le signal de dérive que
  l'étape visait justement à éteindre. Le renvoi à `list-dir contract` rattrape le lecteur qui
  exécute la commande, pas celui qui lit.

- **R5** — `skills/list-dir/scripts/listdir/store.py:_read_definition` — **le contenu de
  `templates/` est aplati sans le dire**. `sorted((definition / TEMPLATES).glob("*"))` filtré par
  `f.is_file()` ignore silencieusement tout sous-répertoire. Cas limite non couvert par les tests et
  non documenté ; il ne se manifeste sur aucune des trois semences actuelles (deux fichiers plats),
  mais une définition tierce y perdrait des gabarits sans un message. Le reste de la gestion
  d'erreur du module est en revanche exemplaire : validation en mémoire avant tout `mkdir`, garde
  « contrat déjà présent » en tête, `OSError` nommant le chemin fautif — tous vérifiés à
  l'exécution.

Sur le reste : le style des modules neufs suit fidèlement celui de leurs voisins — imports absolus
justifiés en en-tête comme dans les autres commandes, `register()` + appel de bibliothèque sans
logique dans les façades, `Result`/`fail`/`ok` partout, densité de commentaires « pourquoi » du
même ordre que `loader.py` et `store.py`, nommage français cohérent. Les 22 tests ajoutés couvrent
les cas listés au plan, y compris la déduplication du cas `~/.claude` imbriqué et le « rien créé »
après refus.

### Dette induite

- **R6** — `derive` sur une liste fraîchement amorcée sort **1** (« aucun élément — il n'y a rien à
  projeter »). Le comportement est antérieur au chantier et délibéré (`contrat-liste.md` :
  « projeter zéro élément se lirait comme rien à traiter »), mais le chantier crée la situation qui
  le rend courant : une liste amorcée est vide par construction. Conséquence concrète et vérifiée —
  la boucle de vérification de l'**étape 7 du plan** enchaîne `init --def`, `validate` puis
  `derive` sur les listes tout juste créées ; rejouée telle qu'elle est écrite, elle imprime
  « ÉCHEC derive ». La vérification déclarée de l'étape 7 est donc inopérante en l'état, alors que
  le critère qu'elle sert est bel et bien atteint (établi ici en insérant un `new` avant le
  `derive`). Coût futur : une procédure d'amorçage documentée qui se terminerait par un `derive`
  ferait croire à un échec là où il n'y en a pas.

- **R7** — **deux dettes promises « à la clôture » ne sont pas encore inscrites**, vérifié par
  `ls .claude/implementation/todo/technical-debt/` et
  `grep -ril 'ruff format\|gabarit-rapport' .claude/implementation/todo/` (aucune sortie) :
  (a) le formatage non appliqué du dépôt — `uvx ruff format --check` échoue sur 5 fichiers
  antérieurs au chantier, retiré du contrôle final au journal du 2026-08-30 ;
  (b) `debt-review/references/gabarit-rapport.md`, écarté au plan (Q2). Ce n'est pas un manquement
  d'implémentation — la clôture inscrit la dette après l'audit — mais les deux engagements sont
  datés et doivent survivre à cet audit, sans quoi ils disparaissent avec le plan archivé.

- **R8** — **Q3 reste ouvert et non borné** : la remontée s'arrête au premier `.claude` trouvé, qui
  n'est pas nécessairement le bon en dépôt imbriqué. Le plan l'assume et compense en rendant
  l'ancrage retenu visible dans `defs` — ce qui fonctionne, je l'ai constaté à l'exécution. Ce n'est
  pas un défaut au regard du contrat du chantier, mais c'est un coût reporté : le jour où le
  mauvais projet sera visé, rien n'échouera, une liste sera simplement amorcée du mauvais contrat.
  Aucun marqueur explicite ni ancrage sur la racine git n'a été posé.

### Bloquants

Aucun. Les sept critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
respecté et aucun signal de dérive ne s'est matérialisé. Les huit constats sont des réserves :
**R1** est celle à traiter avant de considérer le symptôme d'origine comme refermé, **R2** et **R3**
touchent la surface publique neuve et se corrigent chacune en quelques lignes, **R7** est un rappel
de tenue pour la clôture elle-même.

---

## 2026-08-30 — clôture — `25bcb47`

**Verdict** : RÉSERVES

Second audit de clôture, portant sur **le diff entier depuis `master`** (`git diff master...25bcb47`,
21 fichiers, +2050/−43) et non sur le seul correctif `334927f..25bcb47`. Arbre propre sur `25bcb47`
(`git status --short` muet).

### Vérifications exécutées

Toutes relancées sur le nouveau SHA, aucune reprise de l'audit précédent sur parole.

- `cd skills/list-dir && uvx pytest scripts/tests/ -q` → **282 passed in 6.08s** (étape 10 ;
  277 → 282, les cinq tests neufs du correctif)
- `cd skills/list-dir && uvx ruff check .` → **All checks passed!** (sortie 0)
- `cd skills/list-dir && uvx --with pytest basedpyright` → **0 errors, 0 warnings, 0 notes**
- `python3 scripts/check_pipeline.py` → **Pipeline conforme.** (sortie 0, huit contrôles)
- `python3 scripts/sante_skills.py` → sortie 0
- `grep -ril 'dette\|debt' skills/list-dir/` → **aucune sortie** (sortie 1) — critère 7
- `grep -c 'douze commandes' skills/list-dir/SKILL.md` → **2** ; `list-dir help` →
  « Commandes génériques (12) » (étape 6)
- `grep -c 'list-dir contract' …/dette.md` → **2** ; `grep -c '| \`title\` | requis |'` → **0** ;
  `grep -c 'init .*--def'` → **1** (étape 8)
- `sed -n '68,80p' skills/debt-review/SKILL.md | grep -c 'dette.md'` → **1** (étape 9)
- Fidélité des semences — `diff` des trois `contract.toml` et des deux `templates/review.{toml,md}`
  entre `.claude/implementation/todo/…/.list/` et `skills/implementation-tracker/list-dir/…` →
  **identiques** sur les cinq
- Bout en bout dans un projet neuf hors dépôt (`$TMP/projet/.claude`, `PATH` sur `bin/list-dir`) :
  - `list-dir defs` → ancrages imprimés, les trois définitions en `rang 4  config:implementation-tracker`, sortie 0
  - `init --def <l>` × 3 → sortie **0** ; `validate` × 3 → « 0 élément(s) conformes au contrat », sortie 0
  - `ls …/technical-debt/.list/templates/` → `review.md`, `review.toml`
  - `new … essai` puis `derive … --template review` → « 1 fiche(s) à instruire », sortie 0
  - `contract …/technical-debt` → imprime le contrat en vigueur, sortie 0
  - précédence : définition posée en `<projet>/.claude/list-dir/technical-debt/` →
    `defs` → `rang 1  projet  (masque config:implementation-tracker)` ; `init --def` amorce bien
    celle du rang 1 (`name = "surcharge-projet"`)
  - définition sans skill porteur (`<projet>/.claude/list-dir/maison/`) → `init` et `validate` sortie 0
  - `init --def inexistante` → sortie 1, « introuvable ; connues : dupe, maison, technical-debt, … »
  - `init --def a --from b` → sortie **2**, argparse « not allowed with argument --def »
  - `init --from /nexistepas` → sortie 1, « définition sans contrat — contract.toml attendu »,
    **cible non créée**
- **Contrôle du traitement de R2** — deux définitions homonymes de rang 2 (`skills/a`, `skills/b`) :
  `defs` → `dupe  rang 2  AMBIGUË — projet:a, projet:b ; \`init --def\` refusera`, sortie 0 ;
  `init --def dupe` → sortie **1**, « ambiguë — 2 racines de même rang : …/a/…, …/b/… ». Les deux
  commandes disent désormais la même chose.
- **Contrôle du traitement de R3** — `init … --def technical-debt --name "MonNom"` → sortie **2**,
  « --name et --description ne s'appliquent qu'au squelette », **cible non créée** ;
  `init … --from <def> --description "x"` → sortie **2** ; `init … --name "MonNom"` seul (squelette)
  → sortie 0 et `name = "MonNom"` écrit.
- **Contrôle du traitement de R1** — lecture intégrale de l'Étape 0 de `skills/debt-review/SKILL.md`
  (lignes 63-100) : la puce « Registre absent → le dire et s'arrêter » a bien disparu, remplacée par
  trois puces distinguant les trois états. Voir toutefois **R9**.
- **R6 rejoué** — boucle de vérification de l'étape 7 du plan, telle qu'elle est écrite :
  `derive "$D/technical-debt" …` → « aucun élément — il n'y a rien à projeter », sortie **1**,
  « ÉCHEC derive » imprimé. Inchangé.
- **R7 rejoué** — `ls .claude/implementation/todo/technical-debt/` (20 entrées) et
  `grep -ril 'ruff format\|gabarit-rapport' .claude/implementation/todo/` → **aucune sortie**.
- `list-dir validate <répertoire absent>` → « répertoire introuvable », sortie **1** — même code et
  même `ÉCHEC : $l` que sur une liste non conforme. Sert **R9**.

Aucune commande de vérification déclarée n'est restée non exécutée.

### Conformité à l'intention

Les sept critères de réussite, un par un, tous revérifiés par exécution sur `25bcb47` :

1. amorcer par le nom de la définition → `validate` sort 0 — **atteint, vérifié**.
2. les trois registres dans un projet vide, `validate` sur les trois — **atteint, vérifié**.
3. `derive` après amorçage, `templates/review.{toml,md}` ont suivi — **atteint, vérifié**
   (les deux gabarits copiés ; `derive` sort 0 dès qu'un élément existe). Réserve de forme : **R6**.
4. définition posée en `<projet>/.claude/list-dir/<nom>/`, sans skill porteur — **atteint, vérifié**.
5. `init` sans définition → squelette actuel inchangé — **atteint, vérifié** (contrat identique à
   celui produit par `master`, et le test `test_name_reste_accepte_sur_le_squelette` le borne).
6. deux définitions de même rang, même nom → sortie non nulle les nommant toutes les deux —
   **atteint, vérifié**. La réserve R2 du précédent audit est **levée** : `defs` ne désigne plus de
   vainqueur là où `init --def` refuse de choisir.
7. `grep -ril 'dette\|debt' skills/list-dir/` sans sortie — **atteint, vérifié**.

**Hors-périmètre** : respecté sur les cinq points du suivi. Les contrats ne changent pas (prouvé par
`diff` sur les cinq fichiers) ; hors `init.py`, aucune commande existante n'est modifiée — le
correctif ne touche que `commands/init.py` et `commands/defs.py`, tous deux du chantier ; aucun rang
« plugins » ; `debt-review/references/gabarit-rapport.md` intact ; aucun chemin de re-semis.

**Signaux de dérive** : aucun matérialisé. Pas de mot « dette » dans `list-dir` ; découverte par
`is_dir()`/`iterdir()`/`glob`, aucun registre persisté ; `_read_definition` lit un texte et
`init_list` l'écrit tel quel, sans héritage ni fusion ; aucune entrée créée à l'amorçage ; le
renvoi documentaire passe par `list-dir contract`, jamais par un fichier de semence.

**Symptôme d'origine** : le chemin de sortie existe, fonctionne bout en bout et est désormais écrit
dans l'Étape 0 sans la contradiction de R1. Je le tiens pour **traité**. Une ambiguïté résiduelle
subsiste sur un état voisin — **R9** — mais elle ne porte plus sur le cas du projet neuf.

**Suivi des constats du précédent audit** :

| | État sur `25bcb47` |
|---|---|
| R1 | **levé** — vérifié par lecture intégrale de l'Étape 0 |
| R2 | **levé** — vérifié à l'exécution, et couvert par deux tests |
| R3 | **levé** — vérifié à l'exécution, et couvert par trois tests |
| R4 | **ouvert**, inchangé |
| R5 | **ouvert**, inchangé |
| R6 | **ouvert**, rejoué et reproduit |
| R7 | **ouvert** — geste de clôture, encore à faire |
| R8 | **ouvert**, inchangé |

### Qualité du code

- **R9** — `skills/debt-review/SKILL.md`, Étape 0 — **le correctif de R1 laisse trois consignes pour
  un même signal observable**. Le bloc ajouté dit : « Un `ÉCHEC` sur **un seul** registre est autre
  chose : une liste existe et ne respecte plus son contrat. Là, `list-dir migrate` avant toute
  revue ». Douze lignes plus bas, la puce neuve dit : « **Un registre absent parmi les trois** → le
  dire et s'arrêter ». Et le paragraphe préexistant, entre les deux, dit : « Sortie ≠ 0 → le dire et
  s'arrêter, **la remise en conformité n'est pas le travail d'une revue** » — ce que le nouveau
  `list-dir migrate` contredit frontalement. Or les deux états ne se distinguent pas depuis
  l'Étape 0 : `list-dir validate` sort **1** aussi bien sur un répertoire absent (vérifié :
  « répertoire introuvable ») que sur une liste non conforme, et la boucle n'imprime dans les deux
  cas que `ÉCHEC : $l`. Un lecteur qui voit un seul `ÉCHEC` doit donc choisir entre *migrer*,
  *s'arrêter* et *s'arrêter* sans rien pour trancher. C'est le même mode de défaillance que R1 —
  deux instructions inconciliables dans une même étape — déplacé du cas « trois absents » vers le
  cas « un seul ». La commande de vérification de l'étape 9 ne peut toujours pas l'attraper : elle
  ne compte qu'une occurrence de `dette.md` dans une fenêtre de treize lignes.

- **R10** — `skills/list-dir/scripts/listdir/commands/init.py:command` — **`--def ""` retombe sur le
  squelette en silence**, cas voisin explicitement nommé en fin de R3 et non traité. Vérifié :
  `list-dir init .claude/t9 --def ""` → sortie **0**, contrat squelette avec `name = "t9"`. La
  doctrine retenue pour R3 — « rendre 0 sur un contrat qui ne porte pas ce qui a été demandé est un
  échec ouvert » — s'applique mot pour mot ici : l'utilisateur a demandé une définition et reçoit un
  squelette, sans un mot. La cause est structurelle et tient en une ligne : `default=""` sur `--def`
  rend l'option vide indiscernable de l'option absente (`if nom:`). Portée réelle faible — il faut
  écrire l'option vide à la main — d'où le classement en réserve et non en bloquant.

- **R4** *(reporté du 334927f, inchangé — vérifié à nouveau)* —
  `skills/implementation-tracker/references/dette.md` : « Les listes soldée et écartée … rendent
  facultatives **celles qui disent le problème** », alors que `## Constat` — qui dit le problème —
  reste `required = ["Constat", "Soldé le"]` / `["Constat", "Écartée le"]` dans les deux contrats
  (relu sur les semences et sur les listes vivantes). La phrase peut se lire comme décrivant un
  contrat que l'outil n'applique pas, ce que l'étape 8 visait précisément à éteindre.

- **R5** *(reporté, inchangé)* — `store.py:_read_definition` : `sorted((definition /
  TEMPLATES).glob("*"))` filtré par `f.is_file()` **ignore silencieusement tout sous-répertoire** de
  `templates/`. Aucune des trois semences n'est concernée (deux fichiers plats), aucun test ne le
  couvre, la docstring ne le dit pas ; une définition tierce y perdrait des gabarits sans message.

Sur le reste du diff, y compris les deux modules touchés par le correctif : le style tient. Les
docstrings ajoutées à `defs._ligne` et à `init.command` documentent le *mode de défaillance* corrigé
plutôt que la mécanique, ce qui est l'idiome du paquet (`store.py`, `loader.py`) ; le code 2 retenu
pour le refus est cohérent avec celui qu'`argparse` rend déjà pour `--def`/`--from` ensemble ; les
façades de commande restent des façades — `_ligne` met en page, la comparaison de rang qu'il fait
duplique trois lignes de `resolve()` sans appeler la bibliothèque, ce qui est le seul endroit du
correctif où la règle « aucune logique dans un module de commande » est effleurée, sans conséquence
observable puisque les deux implémentations sont désormais couvertes par des tests jumeaux.
`ruff check` et `basedpyright` passent, aucune ligne au-delà de 100 colonnes.

### Dette induite

- **R6** *(reporté, rejoué et reproduit)* — `derive` sur une liste fraîchement amorcée sort **1**
  (« aucun élément — il n'y a rien à projeter »). Comportement antérieur au chantier et délibéré,
  mais le chantier rend la situation courante. La boucle de vérification de l'**étape 7 du plan**,
  rejouée telle qu'elle est écrite, imprime « ÉCHEC derive » : la vérification déclarée reste
  inopérante alors que le critère qu'elle sert est atteint.

- **R7** *(reporté — geste de clôture)* — **deux dettes promises « à la clôture » ne sont toujours
  pas inscrites** (vérifié : aucune sortie sur `grep -ril 'ruff format\|gabarit-rapport'
  .claude/implementation/todo/`) : (a) le formatage non appliqué du dépôt — `uvx ruff format
  --check` échoue sur 5 fichiers antérieurs, retiré du contrôle final au journal du 2026-08-30 ;
  (b) `debt-review/references/gabarit-rapport.md`, écarté au plan (Q2). Les deux engagements sont
  datés et disparaissent avec le plan archivé s'ils ne sont pas portés au registre.

- **R8** *(reporté, inchangé)* — Q3 ouvert et non borné : la remontée s'arrête au premier `.claude`,
  qui n'est pas nécessairement le bon en dépôt imbriqué. Compensé par l'impression de l'ancrage dans
  `defs` (constaté à l'exécution), mais le jour où le mauvais projet sera visé, rien n'échouera :
  une liste sera simplement amorcée du mauvais contrat.

### Bloquants

Aucun. Les sept critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
respecté, aucun signal de dérive ne s'est matérialisé, et **R1, R2 et R3 sont effectivement levés**,
chacun contrôlé à l'exécution et non sur déclaration. Restent six réserves : **R9** est la seule
neuve et la seule qui touche le chemin que le chantier existe pour ouvrir — elle se corrige par une
phrase dans `debt-review` ; **R4** et **R5** sont des réserves de rédaction et de cas limite non
traitées depuis le premier audit ; **R7** est un geste de clôture qui doit être fait avant
l'archivage du plan, sans quoi deux engagements datés se perdent.

---

## 2026-08-30 — clôture — `8f916df`

**Verdict** : DÉFAVORABLE

Troisième audit de clôture, portant sur **le diff entier depuis `master`**
(`git diff master...8f916df` : 21 fichiers, +2260/−47) et non sur le seul correctif
`25bcb47..8f916df`. Arbre propre sur `8f916df` (`git status --short` muet), branche
`semences-de-listes` à la bonne tête.

### Vérifications exécutées

Toutes relancées sur le nouveau SHA, aucune reprise des audits précédents sur parole.

- `cd skills/list-dir && uvx pytest scripts/tests/ -q` → **282 passed in 5.78s** (étape 10 ;
  inchangé depuis `25bcb47` — le correctif R9/R4 est documentaire et n'ajoute aucun test)
- `cd skills/list-dir && uvx ruff check .` → **All checks passed!**
- `cd skills/list-dir && uvx --with pytest basedpyright` → **0 errors, 0 warnings, 0 notes**
- `python3 scripts/check_pipeline.py` → **Pipeline conforme.** (sortie 0, huit contrôles, dont
  « 30 renvois vers le contrat, tous résolvent » et « 15 renvois entre skills, tous résolvent »)
- `python3 scripts/sante_skills.py` → sortie 0
- `grep -ril 'dette\|debt' skills/list-dir/` → **aucune sortie** (sortie 1) — critère 7
- `grep -c 'douze commandes' skills/list-dir/SKILL.md` → **2** ; `list-dir help` →
  « Commandes génériques (12) », `contract` et `defs` en tête de liste (étape 6)
- `grep -c 'list-dir contract' skills/implementation-tracker/references/dette.md` → **2** (étape 8)
- `sed -n '68,80p' skills/debt-review/SKILL.md | grep -c 'dette.md'` → **0, sortie 1** (étape 9) —
  **ÉCHEC**. Voir **R11**.
- `grep -n 'dette.md' skills/debt-review/SKILL.md` → l'occurrence de l'Étape 0 est à la **ligne 92**
- Fidélité des semences — `diff` des trois `contract.toml` et des deux `templates/review.{toml,md}`
  entre `skills/implementation-tracker/list-dir/…` et `.claude/implementation/todo/…/.list/` →
  **identiques sur les cinq** (hors-périmètre « les contrats ne changent pas »)
- Bout en bout dans un projet neuf hors dépôt (`$SCRATCH/e2e/projet/.claude`, `PATH` sur
  `bin/list-dir`, `cwd` hors du dépôt) :
  - `list-dir defs` → ancrages imprimés (`projet : …/e2e/projet/.claude`, `config :
    /home/debian/.claude`), les trois définitions en `rang 4  config:implementation-tracker`,
    sortie 0
  - `init .claude/implementation/todo/<l> --def <l>` × 3 → sortie **0** ; `validate` × 3 →
    « 0 élément(s) conformes au contrat », sortie **0** (aucune entrée créée à l'amorçage)
  - `ls …/technical-debt/.list/templates/` → `review.md`, `review.toml`
  - `new … essai` puis `derive … --template review` → « .claude/rev — 1 fiche(s) à instruire »,
    sortie 0
  - `contract …/technical-debt` → imprime le contrat en vigueur (`name = "technical-debt"`,
    `[fields.id]`, …), sortie 0
  - définition sans skill porteur (`<projet>/.claude/list-dir/maison/`) → `init` sortie 0,
    `validate` sortie 0, `name = "maison"` écrit
  - précédence : `<projet>/.claude/list-dir/technical-debt/` → `defs` →
    `rang 1  projet  (masque config:implementation-tracker)` ; `init --def technical-debt` amorce
    bien celle du rang 1 (`name = "surcharge-projet"`)
  - ambiguïté à rang égal (`skills/a`, `skills/b`) → `defs` →
    `dupe  rang 2  AMBIGUË — projet:a, projet:b ; \`init --def\` refusera`, sortie 0 ;
    `init --def dupe` → sortie **1**, message nommant **les deux chemins**, cible **non créée**
  - `init --def inexistante` → sortie 1, « introuvable ; connues : dupe, maison, technical-debt,
    technical-debt-ecarte, technical-debt-solde »
  - définition à contrat invalide (`type = "string"`) → sortie **1**, message nommant le fichier
    **de la définition** et le type fautif, cible **non créée**
  - `init … --def maison --name "MonNom"` → sortie **2**, « --name et --description ne s'appliquent
    qu'au squelette », cible **non créée** (R3 tient)
- Critère 5 — `list-dir init .claude/skel` sans option → contrat squelette **identique** à celui que
  produit le code de `master` (comparé au littéral de `store.py:674-689` sur `master` :
  `name`/`description`, `[fields.id] type="slug"`, `[fields.title] type="text" required=true`,
  `[sections] required=["Constat"] optional=[]`)
- **R9 rejoué** — lecture intégrale de l'Étape 0 (lignes 63-125) : l'instruction `list-dir migrate`
  a disparu, le bloc distingue `ABSENT` de `NON CONFORME`, et les quatre puces donnent une consigne
  par état sans se contredire. **R9 est levé sur le point qui le constituait.** Voir toutefois
  **R12**, qui porte sur le même correctif.
- **Bloc de l'Étape 0 rejoué tel qu'il est écrit**, dans le projet neuf, les trois registres
  **présents, conformes et vides** → **aucune sortie du tout**. Sert **R12**.
- `list-dir validate <liste vide>` sans le `>/dev/null` → « … : 0 élément(s) conformes au contrat »,
  sortie 0. Sert **R12**.
- **R4 rejoué** — `grep -A3 '[sections]'` sur les deux contrats de solde/écart →
  `required = ["Constat", "Soldé le"]` / `["Constat", "Écartée le"]`,
  `optional = ["Pourquoi c'est gênant", "Pour solder", "Assumé"]` ; contrat de `technical-debt` →
  `required = ["Constat", "Pourquoi c'est gênant", "Pour solder"]`. La phrase corrigée de
  `dette.md` ne fait plus dire à la doc que `Constat` est facultatif : **R4 est levé sur son
  défaut central**. Résidu : **R13**.
- **R5 rejoué** — définition portant `templates/plat.md` **et** `templates/sous/x.toml` →
  `init --def` sortie **0**, `ls -R` de la liste créée → `plat.md` seul. Le sous-répertoire est
  perdu **sans un mot**. Reproduit, inchangé.
- **R6 rejoué** — `derive` sur une liste fraîchement amorcée → « aucun élément — il n'y a rien à
  projeter », sortie **1**. La boucle de vérification de l'étape 7 du plan
  (`.claude/plans/tidy-crunching-cupcake.md:178-190`), rejouée telle qu'elle est écrite, imprime
  toujours « ÉCHEC derive ». Reproduit, inchangé.
- **R7 rejoué** — `grep -ril 'ruff format\|gabarit-rapport' .claude/implementation/todo/` →
  **aucune sortie** (sortie 1) ; `ls .claude/implementation/todo/technical-debt/ | wc -l` → **20**.
  Les deux dettes promises ne sont toujours pas inscrites.
- **R10 rejoué** — `list-dir init .claude/t9 --def ""` → sortie **0**, contrat squelette
  `name = "t9"`. Reproduit, inchangé.
- Contrainte du brief « à réécrire : `store.py:652-657` » → la docstring de `init_list` porte
  désormais « POURQUOI UNE DÉFINITION PEUT CE QU'UN GABARIT NE POUVAIT PAS » et « ELLE FAIT AUTORITÉ
  LE TEMPS DE CET APPEL, ET PAS AU-DELÀ ». **Honorée.**
- Longueur de ligne des cinq fichiers Python touchés → 1 ligne > 100 colonnes dans `definitions.py`
  (l. 204), contre 3 déjà présentes dans `store.py` sur `master` : conforme au style du voisinage,
  et `ruff check` l'accepte.

Aucune commande de vérification déclarée n'est restée non exécutée. **Une est en échec** : celle de
l'étape 9.

### Conformité à l'intention

Les sept critères de réussite du brief, un par un, tous revérifiés par exécution sur `8f916df` :

1. « amorcer une liste par le nom de sa définition produit une liste dont `validate` sort 0 » —
   **atteint, vérifié**.
2. « les trois registres s'amorcent dans un projet vide, puis `validate` passe sur les trois » —
   **atteint, vérifié** hors dépôt.
3. « `derive` fonctionne après amorçage : `templates/review.{toml,md}` ont suivi » — **atteint,
   vérifié** (les deux gabarits copiés, `derive` sort 0 dès qu'un élément existe). Réserve de
   forme inchangée : **R6**.
4. « une définition posée dans `<projet>/.claude/list-dir/<nom>/` s'amorce sans qu'aucun skill la
   porte » — **atteint, vérifié**.
5. « `init` sans définition nommée produit le squelette actuel, inchangé » — **atteint, vérifié**
   par comparaison au littéral de `master`.
6. « deux définitions de même rang portant le même nom font sortir la commande non nul, en les
   nommant toutes les deux » — **atteint, vérifié**, et `defs` dit désormais la même chose.
7. « `grep -ril 'dette\|debt' skills/list-dir/` ne rend toujours aucune sortie » — **atteint,
   vérifié**.

**Hors-périmètre** : respecté sur les cinq points du suivi. Les contrats ne changent pas (prouvé par
`diff` sur les cinq fichiers) ; hors `commands/init.py`, aucune commande existante de `list-dir`
n'est modifiée ; aucun rang « plugins » ; `debt-review/references/gabarit-rapport.md` intact
(vérifié : absent du `--stat` du diff complet) ; aucun chemin de re-semis. Les commandes neuves
`defs` et `contract` sont ratifiées par le suivi, qui fait foi.

**Signaux de dérive** : aucun matérialisé. Pas de mot « dette » dans `list-dir` ; découverte par
`is_dir()` / `iterdir()` / `glob`, aucun registre persisté (`definitions.py` relu en entier) ;
`_read_definition` lit un texte et `init_list` l'écrit tel quel — ni héritage, ni surcharge, ni
fusion ; aucune entrée créée à l'amorçage ; le renvoi documentaire passe par `list-dir contract`,
jamais par un fichier de semence.

**Symptôme d'origine** — « dans un projet neuf, l'Étape 0 rend trois `ÉCHEC` et aucune étape ne dit
quoi faire ensuite » : **traité**. Le bloc rend `ABSENT : <l>` trois fois et la première puce route
vers `dette.md`. C'est l'état *voisin* — registres présents, conformes et vides — qui est devenu
muet : **R12**.

**Suivi des constats antérieurs** :

| | État sur `8f916df` |
|---|---|
| R1 | **levé** (25bcb47), revérifié par lecture intégrale de l'Étape 0 |
| R2 | **levé** (25bcb47), revérifié à l'exécution |
| R3 | **levé** (25bcb47), revérifié à l'exécution |
| R4 | **levé** sur son défaut central — `Constat` n'est plus dit facultatif. Résidu : **R13** |
| R5 | **ouvert**, rejoué et reproduit — réserve assumée par l'utilisateur |
| R6 | **ouvert**, rejoué et reproduit — réserve assumée |
| R7 | **ouvert** — geste de clôture, non encore exécuté |
| R8 | **ouvert**, inchangé — réserve assumée |
| R9 | **levé**, revérifié |
| R10 | **ouvert**, rejoué et reproduit — réserve assumée |

### Qualité du code

- **R11** — `.claude/implementation/semences-de-listes.md`, étape 9 — **la vérification déclarée de
  l'étape est en échec sur `HEAD`**, alors que l'étape est cochée `[x]`. Sortie réelle :
  `sed -n '68,80p' skills/debt-review/SKILL.md | grep -c 'dette.md'` → **0**, code de sortie **1**.
  Le correctif `8f916df` a réécrit l'Étape 0 et déplacé le renvoi de la fenêtre 68-80 vers la
  **ligne 92** ; la commande, qui repose sur des numéros de ligne absolus, ne le voit plus.
  Le fond est intact — je l'ai établi par `grep -n 'dette.md' skills/debt-review/SKILL.md` et par
  lecture de la puce « `ABSENT` sur les trois », qui route bien vers `dette.md` — mais **c'est
  précisément la démonstration que la commande ne démontre plus rien**. Le premier audit avait déjà
  signalé que cette vérification « ne regarde que la fenêtre qui vient d'être écrite » ; deux
  correctifs plus tard, la fenêtre a bougé et la commande est passée d'inutile à fausse.
  Conséquence si rien n'est fait : la clôture aplatit et archive un suivi dont une étape cochée
  porte une vérification qui échoue, c'est-à-dire une trace mensongère dans l'historique du dépôt.
  C'est le seul constat de cet audit qui interdit la clôture, et il se corrige dans le seul suivi —
  une vérification sans numéro de ligne (`grep -c 'dette.md' skills/debt-review/SKILL.md` ou un
  `sed` ancré sur le titre de l'étape).

- **R12** — `skills/debt-review/SKILL.md`, Étape 0 — **le correctif de R9 a rendu muet l'un des
  quatre états qu'il prétend distinguer**. Le bloc écrit désormais
  `elif ! list-dir validate "$T/$l" >/dev/null;` — la redirection est neuve, ajoutée par `8f916df`.
  Or la sortie standard de `validate` était le **seul** signal observable de l'état « registre
  conforme mais vide » : elle imprime « … : 0 élément(s) conformes au contrat ». Vérifié à
  l'exécution, trois registres présents, conformes et vides dans un projet neuf : **le bloc
  n'imprime rien du tout**. Et douze lignes plus bas, une puce prescrit pourtant une suite pour cet
  état : « **Registre conforme mais vide** → le dire et s'arrêter ». Le lecteur qui suit l'étape
  n'a plus rien pour la déclencher, et une sortie vide se lit comme « tout va bien, continuer » —
  exactement l'inverse.
  C'est le mode de défaillance que la note ajoutée par le même commit met en garde deux paragraphes
  plus bas (« une règle ajoutée ici se relit **contre toutes les autres** ») : le bloc a été
  réécrit contre les trois états qu'il visait, pas contre le quatrième. Ce n'est pas une régression
  contre `master` seulement en principe : sur `master` comme sur `25bcb47`, le bloc était
  `list-dir validate "$T/$l" || echo "ÉCHEC : $l"`, sans redirection, et le compte s'affichait.
  Je ne le classe pas bloquant parce qu'aucun critère de réussite ne porte sur cet état et que la
  puce « conforme mais vide » est elle-même un ajout du chantier — mais c'est la réserve de fond de
  cet audit, et elle touche le fichier que le chantier existe pour réparer.

- **R13** — `skills/implementation-tracker/references/dette.md` (correctif de R4) — **la phrase
  corrigée dit maintenant moins que ce que le contrat applique**. Elle affirme que les listes soldée
  et écartée « rendent facultatif le **plan** de solde ». Les contrats, relus sur les semences et
  sur les listes vivantes, rendent facultatives **deux** sections d'un coup : `Pourquoi c'est
  gênant` **et** `Pour solder` passent de `required` (dans `technical-debt`) à `optional`. La
  formulation d'origine — « rendent facultatives les deux du milieu » — était exacte sur ce point.
  Le correctif a échangé une inexactitude (`Constat` implicitement dit facultatif, ce qui était
  grave) contre une omission (`Pourquoi c'est gênant` passé sous silence, ce qui l'est beaucoup
  moins). Réserve de rédaction, pas de comportement : `list-dir contract` rattrape le lecteur qui
  exécute la commande, et le renvoi est en place.

Sur le reste du diff, y compris le dernier correctif : le style tient. `definitions.py` est le
module le mieux tenu du chantier — docstring de tête qui dit les rangs, les deux remontées et
*pourquoi pas* `shutil.which`, ancrages passés en paramètres pour rester testables sur `tmp_path`,
déduplication sur chemin résolu commentée par le cas réel qui la motive. `resolve()` énonce ses
trois issues et les tient. Les façades de commande restent des façades. Le nommage français, la
densité de commentaires « pourquoi » et le motif `Result`/`fail`/`ok` suivent `loader.py` et
`store.py`. Les 22 tests ajoutés couvrent les cas du plan, y compris le `~/.claude` imbriqué et le
« rien créé » après refus ; `ruff` et `basedpyright` sont propres.

### Dette induite

- **R5** *(reporté, reproduit — réserve assumée par l'utilisateur)* — `store.py:_read_definition`
  aplatit `templates/` : un sous-répertoire est ignoré sans message, `init --def` sort 0. Vérifié à
  l'exécution cette fois avec une définition portant `templates/sous/x.toml` — seul `plat.md` est
  copié. Aucune des trois semences n'est concernée ; une définition tierce y perdrait des gabarits
  en silence.
- **R6** *(reporté, reproduit — réserve assumée)* — `derive` sort 1 sur une liste fraîchement
  amorcée. La boucle de vérification de l'étape 7 du plan imprime « ÉCHEC derive » telle qu'elle est
  écrite. Le plan part à l'archivage avec une vérification inopérante ; c'est la même famille que
  **R11**, en moins grave puisque l'étape 7 est vérifiée par ailleurs.
- **R7** *(reporté — geste de clôture non exécuté)* — deux dettes promises « à la clôture » ne sont
  toujours pas inscrites (`grep -ril 'ruff format\|gabarit-rapport' .claude/implementation/todo/` →
  aucune sortie) : (a) le formatage non appliqué du dépôt, `uvx ruff format --check` échouant sur
  5 fichiers antérieurs, retiré du contrôle final au journal du 2026-08-30 ; (b)
  `debt-review/references/gabarit-rapport.md`, écarté au plan (Q2). Ces engagements disparaissent
  avec le plan archivé s'ils ne sont pas portés au registre.
- **R8** *(reporté — réserve assumée)* — Q3 ouvert : la remontée s'arrête au premier `.claude`, qui
  n'est pas nécessairement le bon en dépôt imbriqué. Compensé par l'impression de l'ancrage dans
  `defs`, constatée à l'exécution ; le jour où le mauvais projet sera visé, rien n'échouera.
- **R10** *(reporté — réserve assumée)* — `--def ""` retombe sur le squelette en silence, sortie 0.
  Reproduit. Cause structurelle : `default=""` rend l'option vide indiscernable de l'option absente.

### Bloquants

- **R11** — la commande de vérification déclarée de l'étape 9, cochée `[x]`, **échoue** sur `HEAD`
  (sortie 1, compte 0). Une étape ne peut pas être close sur une vérification qui ne passe pas, même
  quand le fond qu'elle est censée établir est vrai par ailleurs : le suivi part à l'archivage tel
  quel. Corriger la commande dans le suivi — sans numéro de ligne — puis la relancer.

Rien d'autre n'interdit la clôture : les sept critères de réussite sont atteints et vérifiés par
exécution, le hors-périmètre est respecté, aucun signal de dérive ne s'est matérialisé, et R4 comme
R9 sont effectivement levés sur ce qui les constituait. **R12** est la réserve de fond — une puce de
l'Étape 0 dont l'état déclencheur n'est plus observable, régression introduite par ce même correctif
— et **R13** un résidu de rédaction du correctif de R4. R5, R6, R8 et R10 restent ouverts par
arbitrage ; R7 est un geste de clôture encore à faire.

---

## 2026-08-30 — clôture — `f17ed2a`

**Verdict** : DÉFAVORABLE

### Vérifications exécutées

Arbre propre sur `f17ed2a` (`git status --short` muet). Diff jugé en entier
(`git diff master...semences-de-listes` — 21 fichiers, +2535/-47), pas seulement le dernier commit.

Suite et outillage :

- `cd skills/list-dir && uvx pytest scripts/tests/ -q` → **282 passed in 5.82s** (étape 10)
- `uvx ruff check .` → **All checks passed!** ; `uvx --with pytest basedpyright` → **0 errors, 0 warnings, 0 notes**
- `python3 scripts/check_pipeline.py` → **Pipeline conforme.** (8 contrôles, sortie 0)
- `python3 scripts/sante_skills.py` → sortie 0, aucune anomalie

Les vérifications déclarées, étape par étape, dans leur forme exacte :

- étape 1 → **14 passed** ; étape 2 → **36 passed** ; étape 3 (`-k init_def`) → **3 passed** ;
  étape 4 → **1 passed** ; étape 5 → **1 passed**
- étape 6 → `grep -c 'douze commandes' skills/list-dir/SKILL.md` → **2**, sortie 0
- étape 7 → `diff` des trois contrats et du `templates/` contre les listes vivantes →
  **identiques**, sortie 0
- étape 8 → `grep -c 'list-dir contract' …/dette.md` → **2** ; `grep -c '| \`title\` | requis |'` → **0** ;
  `grep -c 'init .*--def'` → **1**
- étape 9 → `awk '/## Étape 0/,/## Étape 1/' skills/debt-review/SKILL.md | grep -c 'dette.md'` →
  **1**, sortie 0. **R11 est levé** : la commande ne dépend plus d'aucun numéro de ligne, et
  `grep -n "sed -n '[0-9]"` sur le suivi, le plan, `debt-review/SKILL.md` et `dette.md` ne rend
  plus aucune sortie.
- critère 7 → `grep -ril 'dette\|debt' skills/list-dir/` → **aucune sortie**, sortie 1

Bout en bout dans un projet neuf hors dépôt (`$TMP/projet/.claude`, `PATH` sur `bin/list-dir`) :

- `list-dir defs` → ancrages imprimés (`projet : …/projet/.claude`, `config : /home/debian/.claude`),
  les trois définitions en `rang 4  config:implementation-tracker`, sortie 0
- `init --def` × 3 → sortie **0** ; `validate` × 3 → « 0 élément(s) conformes au contrat », sortie 0
- `ls …/technical-debt/.list/templates/` → `review.md`, `review.toml`
- `derive` après une entrée → « 1 fiche(s) à instruire », sortie 0
- `init` sans `--def` → squelette **identique** au littéral de `master:store.py` (`name`,
  `description`, `fields.id`, `fields.title`, `sections.required = ["Constat"]`)
- définition posée au rang 1 sans aucun skill → amorcée, `validate` sortie 0 ; le rang 1 masque le
  rang 4 (contrat `RANG1` copié), `defs` l'affiche « (masque config:implementation-tracker) »
- deux définitions de même rang, même nom → `init --def` sortie **1**, message nommant **les deux
  chemins** ; `defs` affiche `AMBIGUË — projet:a, projet:b ; init --def refusera`
- `--def` inconnu → sortie 1, noms connus listés ; `--def` + `--from` → sortie 2 ;
  `--name` avec `--def` → sortie 2

Les quatre états de l'Étape 0 de `debt-review`, rejoués un à un avec le bloc **tel qu'il est écrit** :

- trois registres amorcés, conformes et vides → `VIDE : …` × 3. **R12 est levé** : l'état n'est plus
  muet. La sortie de `validate` en erreur passe par `stderr`, que le `>/dev/null` ne mange pas — le
  message de non-conformité reste visible.
- un registre absent, un cassé, un peuplé → `OK`, `NON CONFORME : …` (avec le détail de `validate`),
  `ABSENT : …`. Les quatre étiquettes sont donc toutes atteignables.
- dans ce dépôt → `OK` × 3.

Reproductions des constats reportés : R5 (`templates/sous/x.toml` ignoré, sortie 0), R6 (`derive`
sur liste fraîchement amorcée → sortie 1), R7 (`grep -ril 'ruff format\|gabarit-rapport'
.claude/implementation/todo/` → aucune sortie), R10 (`--def ""` → squelette, sortie 0).

### Conformité à l'intention

Les sept critères de réussite, un par un :

1. **amorcer par le nom → `validate` sort 0** — **atteint**, vérifié sur quatre définitions
   distinctes dont une posée au rang 1.
2. **les trois registres dans un projet vide, puis `validate`** — **atteint**, exécuté hors dépôt.
3. **`derive` après amorçage, `templates/review.{toml,md}` ont suivi** — **atteint** : les deux
   gabarits sont copiés et `derive` rend une fiche dès qu'il y a une entrée. Réserve inchangée R6 :
   sur une liste **vide**, `derive` sort 1, et la boucle de vérification de l'étape 7 du plan
   imprime « ÉCHEC derive » telle qu'elle est écrite.
4. **une définition au rang 1, sans skill porteur** — **atteint**, y compris la précédence sur le
   rang 4.
5. **`init` sans définition → squelette inchangé** — **atteint**, comparé au littéral de `master`.
6. **deux définitions de même rang → sortie non nulle, les deux nommées** — **atteint** (sortie 1,
   les deux chemins absolus dans le message) ; `defs` annonce le même refus, correctif de R2 tenu.
7. **`grep -ril 'dette\|debt' skills/list-dir/` muet** — **atteint**.

**Hors-périmètre** : respecté. Les trois contrats de semence sont **bit à bit** ceux des listes
vivantes ; aucune commande existante autre que `init` n'est modifiée (`defs` et `contract` sont
neuves, exception ouverte au plan et ratifiée au suivi) ; aucun cinquième rang plugin ;
`gabarit-rapport.md` intact ; aucun re-semis.

**Signaux de dérive** : aucun matérialisé du côté `list-dir`. Pas de registre de définitions —
`definitions.py` découvre par `iterdir()` ; pas de composition de contrats — `_read_definition` lit
un texte et le recopie tel quel ; aucune entrée créée à l'amorçage (constaté : « 0 élément(s) ») ;
`list-dir` ne nomme aucun consommateur ; `contrat-liste.md` et `SKILL.md` décrivent exactement ce
que j'ai observé à l'exécution.

**Symptôme d'origine** — *partiellement refermé*. Le trou d'origine (« l'Étape 0 rend trois `ÉCHEC`
et aucune étape ne dit quoi faire ensuite ») est comblé : trois `ABSENT` routent vers une procédure
d'amorçage qui existe, qui est une commande, et que j'ai exécutée avec succès. Mais l'état
**immédiatement suivant** — projet amorcé, une première dette au registre — est désormais bloqué par
une règle de la même étape : voir **R14**. Le projet neuf sait maintenant créer ses registres, et ne
sait toujours pas faire sa première revue.

### Qualité du code

- **R14** — `skills/debt-review/SKILL.md`, Étape 0 — **la règle `VIDE` bloque la revue dans l'état
  le plus courant d'un projet fraîchement amorcé, et contredit l'Étape 5 du même fichier.** Le bloc
  imprime une étiquette **par registre**, et les puces disent : « **`VIDE`** → le dire et
  s'arrêter » puis « **`OK` sur les trois** → continuer ». Or `technical-debt-solde` et
  `technical-debt-ecarte` sont des **destinations** : ils sont vides tant qu'aucune revue n'a rien
  soldé ni écarté. Exécuté dans un projet neuf amorcé avec **une** dette au registre, la sortie
  réelle est :

  ```
  OK : technical-debt
  VIDE : technical-debt-solde
  VIDE : technical-debt-ecarte
  ```

  « OK sur les trois » n'est pas satisfait et deux registres sont `VIDE` : la revue s'arrête, alors
  qu'il y a exactement une entrée à instruire. Le même fichier dit pourtant l'inverse à l'Étape 5 :
  « Une liste vide compte 0 et ne fait pas échouer le contrôle — `technical-debt-ecarte` reste vide
  tant qu'aucune revue n'a écarté d'entrée. » Et l'Étape 1 ne dérive que depuis `technical-debt` :
  l'état des deux autres registres n'a aucune incidence sur ce qu'il y a à instruire.

  La contradiction logique date de `25bcb47` (« Registre conforme mais vide → le dire et
  s'arrêter »), mais elle était **inerte** : aucun état n'était observable, et à `8f916df` le bloc
  était muet (R12). C'est `f17ed2a` qui la rend opérante, en imprimant `VIDE` par registre et en
  ajoutant la clause de passage « `OK` sur les trois ». C'est le **troisième** correctif successif
  à introduire un défaut neuf dans cette étape, et exactement le mode de défaillance que la note
  ajoutée par ce même commit met en garde douze lignes plus bas : « une règle ajoutée ici se relit
  contre toutes les autres ». La règle « VIDE » a été relue contre le projet neuf, pas contre le
  projet qui vient de poser sa première dette.

  Conséquence si rien n'est fait : le chantier livre un chemin d'amorçage qui marche et une revue
  qui refuse de partir juste après — c'est-à-dire que le symptôme d'origine se déplace d'un cran au
  lieu de disparaître. Correctif attendu dans la seule prose : distinguer le registre `technical-debt`
  (vide → rien à instruire, s'arrêter) des deux registres de sortie (vides → état normal, continuer),
  et reformuler la clause de passage en conséquence.

- **R15** *(réserve mineure)* — `skills/debt-review/SKILL.md`, Étape 0 — **`list-dir` indisponible se
  lit `NON CONFORME`.** Si la commande n'est pas sur le `PATH`, `! list-dir validate "$T/$l"` est
  vrai par code 127 et le registre est étiqueté `NON CONFORME`, ce qui route vers « le dire et
  s'arrêter » avec le mauvais motif — un registre parfaitement sain accusé de structure fautive.
  Cas peu probable dans ce dépôt, mais le chantier vise précisément les projets tiers, où le lien
  `bin/list-dir` n'est pas garanti. Le message d'erreur du shell reste visible sur `stderr`, ce qui
  limite la portée : réserve, pas bloquant.

Sur le reste du diff, y compris le code : rien à ajouter aux trois audits précédents, et je
confirme leur jugement après relecture intégrale. `definitions.py` reste le module le mieux tenu du
chantier — docstring qui dit les quatre rangs, les deux remontées et *pourquoi pas* `shutil.which`,
ancrages passés en paramètres, déduplication sur chemin résolu motivée par le cas réel. `resolve()`
énonce trois issues et les tient ; un nom ne peut pas servir de traversée de chemin, puisqu'il est
confronté aux noms rendus par `iterdir()`. `_read_definition` valide en mémoire avant tout `mkdir`,
comme `derive`. Les modules de commande restent des façades. Nommage français, densité de
commentaires « pourquoi », motif `Result`/`fail`/`ok` : conformes à `loader.py` et `store.py`.
`contrat-liste.md` et `SKILL.md` décrivent le comportement que j'ai constaté, sans écart.

**R13 est levé** : la phrase de `dette.md` nomme désormais les **deux** sections rendues facultatives
(« pourquoi elle gênait, et ce qu'il faudrait faire »), ce que les contrats confirment —
`technical-debt` requiert `["Constat", "Pourquoi c'est gênant", "Pour solder"]`, les deux registres
de sortie requièrent `["Constat", "Soldé le"]` / `["Constat", "Écartée le"]` et déclarent
`optional = ["Pourquoi c'est gênant", "Pour solder", "Assumé"]`. `Constat` reste requis, et la prose
le dit.

### Dette induite

- **R5** *(reporté, reproduit — réserve assumée)* — `store.py:_read_definition` aplatit `templates/` :
  un sous-répertoire est ignoré sans message, `init --def` sort 0. Aucune des trois semences n'est
  concernée ; une définition tierce y perdrait des gabarits en silence.
- **R6** *(reporté, reproduit — réserve assumée)* — `derive` sort 1 sur une liste fraîchement
  amorcée ; la boucle de vérification de l'étape 7 du plan imprime « ÉCHEC derive » telle qu'elle
  est écrite, et part à l'archivage ainsi.
- **R7** *(reporté — geste de clôture toujours non exécuté)* — les deux dettes promises « à la
  clôture » ne sont pas inscrites : (a) le formatage non appliqué du dépôt, `uvx ruff format --check`
  échouant sur 5 fichiers antérieurs, retiré du contrôle final au journal ; (b)
  `debt-review/references/gabarit-rapport.md`, écarté au plan (Q2). Elles disparaissent avec le plan
  archivé si elles ne sont pas portées au registre.
- **R8** *(reporté — réserve assumée)* — Q3 ouvert : la remontée s'arrête au premier `.claude`, qui
  n'est pas nécessairement le bon en dépôt imbriqué. Compensé par l'impression de l'ancrage dans
  `defs`, constatée à l'exécution.
- **R10** *(reporté — réserve assumée)* — `--def ""` retombe sur le squelette en silence, sortie 0.
  Reproduit. `--from ""` se comporte de même, par la même cause (`default=""`).

### Bloquants

- **R14** — l'Étape 0 de `debt-review` arrête la revue d'un projet amorcé dès sa première dette,
  parce que ses deux registres de sortie sont légitimement vides. La règle contredit l'Étape 5 du
  même fichier et le fait que l'Étape 1 ne dérive que depuis `technical-debt`. Le chantier existe
  pour rendre ces skills utilisables dans un projet neuf : livrer l'amorçage et bloquer la revue
  immédiatement après revient à déplacer le symptôme d'un cran.

Rien d'autre n'interdit la clôture : les sept critères de réussite sont atteints et vérifiés par
exécution, le hors-périmètre est respecté, aucun signal de dérive ne s'est matérialisé, et **R11,
R12 et R13 sont effectivement levés** sur ce qui les constituait. **R15** est une réserve mineure de
diagnostic. R5, R6, R8 et R10 restent ouverts par arbitrage de l'utilisateur ; R7 est un geste de
clôture encore à faire.

## 2026-08-30 — clôture — `dbbd216`

**Verdict** : RÉSERVES

### Vérifications exécutées

Arbre propre sur `dbbd216` (`git status --short` muet). Diff jugé **en entier**
(`git diff master...semences-de-listes` — 21 fichiers, +2753/-47), pas seulement le dernier commit.

Suite et outillage :

- `cd skills/list-dir && uvx pytest scripts/tests/ -q` → **282 passed in 5.92s** (étape 10)
- `uvx ruff check .` → **All checks passed!**
- `uvx --with pytest basedpyright` → **0 errors, 0 warnings, 0 notes**
- `python3 scripts/check_pipeline.py` → **Pipeline conforme.** (8 contrôles, sortie 0)
- `python3 scripts/sante_skills.py` → sortie **0**

Vérifications déclarées aux étapes, dans leur forme exacte :

- étape 6 → `grep -c 'douze commandes' skills/list-dir/SKILL.md` → **2** ; contrôlé contre le réel :
  `ls scripts/listdir/commands/` rend **12** modules et `list-dir` inconnue liste
  « contract, defs, derive, help, init, list, merge, migrate, move, new, show, validate »
- étape 7 → `diff` des trois `contract.toml` de semence contre les listes vivantes → **identiques** ;
  `templates/review.toml` et `review.md` → **identiques**
- étape 8 → `grep -c 'list-dir contract' …/dette.md` → **2**
- étape 9 → `awk '/## Étape 0/,/## Étape 1/' skills/debt-review/SKILL.md | grep -c 'dette.md'` → **1**
- étape 10 → ci-dessus
- critère 7 → `grep -ril 'dette\|debt' skills/list-dir/` → **aucune sortie**, sortie 1

Bout en bout, dans deux projets neufs hors dépôt (`$SCRATCH/proj`, `$SCRATCH/p3`) :

- `init --def` × 3 → sortie **0** ; `validate` × 3 → « 0 élément(s) conformes au contrat », sortie 0
- `ls …/technical-debt/.list/templates/` → `review.md`, `review.toml` ; `derive … --template review`
  après une entrée remplie → « 1 fiche(s) à instruire », sortie **0**, `r1.md` produit
- `init` nu → squelette `name` / `description = "<OPTIONNEL>"` / `fields.id` / `fields.title` /
  `sections.required = ["Constat"]` — **inchangé**, le chemin squelette de `store.init_list` n'a pas
  bougé au diff
- définition posée en `<projet>/.claude/list-dir/monreg/`, aucun skill porteur → amorcée,
  `validate` sortie 0
- précédence : `technical-debt` posé au rang 1 masque le rang 4 (contrat `RANG1GAGNE` copié),
  `defs` l'affiche « (masque config:implementation-tracker) »
- deux définitions **de même rang** (`projet:a`, `projet:b`) → `init --def dup` sortie **1**,
  message nommant **les deux chemins absolus** ; `defs` annonce
  « AMBIGUË — projet:a, projet:b ; `init --def` refusera »
- `--from /nope` → sortie 1, « définition sans contrat — contract.toml attendu »

**Étape 0 de `debt-review` — correspondance bloc ↔ puces, contrôlée dans les deux sens.**

Les quatre étiquettes du bloc, chacune produite à l'exécution :

| État rejoué | Sortie réelle | Puce qui la prend |
|---|---|---|
| projet vide, hors dépôt | `ABSENT` × 3 | « `ABSENT` sur les trois → amorcer » |
| après `init --def` × 3 | `VIDE` × 3 | « `VIDE` sur `technical-debt` → s'arrêter » (+ destinations) |
| une entrée remplie au registre | `OK` / `VIDE` / `VIDE` | « `OK` sur `technical-debt` → **continuer** » |
| un `.md` sans front matter, un répertoire supprimé | `OK` / `NON CONFORME` / `ABSENT` | « `NON CONFORME` → s'arrêter » puis « `ABSENT` sur un ou deux » |
| ce dépôt-ci | `OK` × 3 | idem |

Sens inverse — chaque puce renvoie à une étiquette réellement produite : les six puces citent
`ABSENT`, `NON CONFORME`, `VIDE` et `OK`, et le bloc n'imprime rien d'autre ; aucune puce ne
s'appuie sur un état mort. Le seul cas non doté d'une puce propre, `OK` sur `-solde` / `-ecarte`,
est traité dans la seconde phrase de la puce `OK` (« les deux autres n'ont qu'à exister et être
conformes ») : couverture explicite, pas un trou.

Cohérence avec les Étapes 1 et 5, relues intégralement :

- Étape 1 dérive **de `technical-debt` seul** (`list-dir derive "$T/technical-debt" …`) — l'état des
  deux autres registres n'entre dans aucun de ses contrôles. Conforme à la puce.
- La puce affirme « `derive` refuse une liste sans élément » : **vérifié**,
  `list-dir derive <liste vide> … --template review` → sortie **1**, « aucun élément — il n'y a rien
  à projeter ». L'affirmation n'est pas une supposition.
- Étape 5 écrit dans `-solde` et `-ecarte` par `move` et dit textuellement « `technical-debt-ecarte`
  reste vide tant qu'aucune revue n'a écarté d'entrée ». La puce « destinations → continuer » cite
  cette phrase et ne la contredit plus.
- La puce `NON CONFORME` conserve « la remise en conformité n'est pas le travail d'une revue »,
  règle préexistante ; aucune instruction `migrate` n'est réintroduite (`grep` sur la section : nulle
  part sinon pour dire pourquoi on ne l'utilise pas).
- La puce `ABSENT` × 3 renvoie à `dette.md` sans recopier la procédure : `dette.md` porte bien le
  bloc `init --def` correspondant (vérifié par lecture).

Reproductions des constats reportés : **R5** (`templates/nested/profond.toml` ignoré,
`init --def` sortie **0**, seul `plat.toml` copié), **R6** (`derive` sur liste fraîchement amorcée →
sortie 1 ; la boucle de vérification de l'étape 7 du plan, rejouée telle quelle, imprime
« ÉCHEC derive »), **R7** (`grep -ril 'ruff format\|gabarit-rapport' .claude/implementation/todo/` →
aucune sortie), **R10** (`init vide --def ""` → squelette, sortie **0**), **R15** (aucune détection
de `list-dir` absent dans le bloc — le code 127 reste indiscernable d'une non-conformité).

### Conformité à l'intention

Les sept critères de réussite, un par un, tous constatés à l'exécution sur ce SHA :

1. **amorcer par le nom → `validate` sort 0** — **atteint** (quatre définitions distinctes, dont une
   au rang 1).
2. **les trois registres dans un projet vide, puis `validate`** — **atteint**, exécuté hors dépôt.
3. **`derive` après amorçage, `templates/review.{toml,md}` ont suivi** — **atteint** : les deux
   gabarits sont copiés, `derive` rend « 1 fiche(s) à instruire » dès qu'une entrée existe. Réserve
   inchangée **R6** sur la liste encore vide.
4. **une définition au rang 1, sans skill porteur** — **atteint**, précédence sur le rang 4 comprise.
5. **`init` sans définition → squelette inchangé** — **atteint** ; le chemin squelette de
   `init_list` est intact au diff, seule une branche `definition is not None` le précède.
6. **deux définitions de même rang → sortie non nulle, les deux nommées** — **atteint** (sortie 1,
   deux chemins absolus), et `defs` annonce le même refus.
7. **`grep -ril 'dette\|debt' skills/list-dir/` muet** — **atteint**.

**Hors-périmètre** : respecté. Les trois contrats de semence et les deux gabarits sont **bit à bit**
ceux des listes vivantes (`diff` muet) ; la structure aussi — seul `technical-debt` porte un
`templates/`, comme la liste vivante. Aucune commande existante autre que `init` n'est modifiée ;
`defs` et `contract` sont neuves, exception ouverte au plan et ratifiée au suivi. Aucun cinquième
rang plugin. `debt-review/references/gabarit-rapport.md` intact. Aucun chemin de re-semis.

**Signaux de dérive** : aucun matérialisé. Pas de registre de définitions — `definitions.py`
découvre par `iterdir()` ; pas de composition — `_read_definition` lit un texte et le recopie tel
quel ; aucune entrée créée à l'amorçage (« 0 élément(s) » constaté) ; `list-dir` ne nomme aucun
consommateur (critère 7 muet) ; `SKILL.md`, `contrat-liste.md` et `dette.md` décrivent exactement le
comportement observé, et `dette.md` renvoie à `list-dir contract` plutôt qu'à un fichier de semence.

**Symptôme d'origine — refermé.** Le trou d'origine (« l'Étape 0 rend trois `ÉCHEC` et aucune étape
ne dit quoi faire ensuite ») est comblé, et l'état immédiatement suivant l'est aussi : projet neuf →
`ABSENT` × 3 → amorçage par commande → première dette → `OK` / `VIDE` / `VIDE` → **continuer**.
C'est exactement le chemin que **R14** bloquait, et je l'ai parcouru bout en bout.

### Qualité du code

- **R14 est levé**, et sur sa cause, pas sur son symptôme. La distinction source / destinations est
  posée au bon endroit — dans les puces, pas dans le bloc — et le bloc n'a pas eu à changer, ce qui
  est le signe qu'il était juste et que seule son interprétation était fautive. Le mode de
  défaillance ajouté nomme les deux pièges structurels (dissymétrie des registres, vieillissement
  séparé du bloc et des puces) plutôt que le dernier symptôme en date, et impose une relecture
  contre les Étapes 1 et 5 : c'est la bonne portée pour une note qui a échoué trois fois à empêcher
  la récidive.

- **R16** *(nouveau — réserve mineure)* — `skills/debt-review/SKILL.md`, Étape 0, puce
  « `ABSENT` sur les trois » — **« reprendre l'étape » aboutit toujours à un arrêt, et ce n'est pas
  dit.** Vérifié à l'exécution : après l'amorçage, le bloc rend `VIDE` × 3, ce que la puce suivante
  route vers « le dire et s'arrêter ». Le résultat est correct — un projet qui vient de créer ses
  registres n'a rien à instruire — mais l'enchaînement « amorcer, puis reprendre l'étape » suggère
  une reprise qui continue. Une demi-phrase (« la reprise dira `VIDE` : c'est la fin normale d'un
  premier passage ») lèverait l'ambiguïté. Prose seule, aucun code en cause.

- **R15** *(reporté du `f17ed2a`, inchangé et non traité)* — `list-dir` absent du `PATH` se lit
  `NON CONFORME`. `! list-dir validate "$T/$l"` est vrai par code 127, et un registre sain est
  accusé de structure fautive. Le message du shell reste sur `stderr`, ce qui limite la portée.
  À signaler surtout parce que le suivi ne le mentionne nulle part : ni journal, ni « restent
  ouverts », alors qu'il énumère R5, R6, R8, R10 et R7. Un constat non repris dans le suivi
  disparaît à l'archivage.

Sur le reste du diff : rien à ajouter aux quatre audits précédents, dont je confirme le jugement
après relecture intégrale. `definitions.py` reste le module le mieux tenu du chantier — quatre rangs
énoncés, deux remontées distinctes motivées par le cas imbriqué réel, *pourquoi pas* `shutil.which`,
ancrages passés en paramètres pour être testables, déduplication sur chemin résolu. `resolve()`
énonce trois issues et les tient ; un nom ne peut pas servir de traversée de chemin puisqu'il est
confronté aux noms rendus par `iterdir()`. `_read_definition` valide en mémoire avant tout `mkdir`,
comme `derive`, et le dit. `commands/defs.py` et `commands/contract.py` restent des façades sans
logique, imports absolus, motif `Result`/`fail`/`ok`, nommage français, commentaires qui disent le
*pourquoi* — conformes à `loader.py`, `store.py` et aux commandes voisines.

### Dette induite

- **R17** *(nouveau — réserve mineure)* — `.claude/implementation/semences-de-listes.md`, « État
  courant » — **le compte de tests déclaré est périmé** : « 277 passed », alors que la suite en rend
  **282** sur ce SHA, chiffre que le message de `dbbd216` donne d'ailleurs correctement. Sans
  conséquence sur le résultat, mais le suivi est ce qui reste après l'archivage du plan : un chiffre
  faux y survit à ce qui pouvait le corriger.
- **R5** *(reporté, reproduit — réserve assumée)* — `store.py:_read_definition` aplatit
  `templates/` : un sous-répertoire est ignoré sans message, `init --def` sort 0. Aucune des trois
  semences n'est concernée ; une définition tierce y perdrait des gabarits en silence.
- **R6** *(reporté, reproduit — réserve assumée)* — `derive` sort 1 sur une liste fraîchement
  amorcée ; la boucle de vérification de l'étape 7 du plan imprime « ÉCHEC derive » telle qu'elle
  est écrite, et part à l'archivage ainsi. `contrat-liste.md` documente pourtant le comportement
  (« une erreur pour `merge` et `derive` ») : c'est la boucle du plan qui est fausse, pas l'outil.
- **R7** *(reporté — geste de clôture toujours non exécuté)* — les deux dettes promises « à la
  clôture » ne sont pas inscrites : (a) le formatage non appliqué du dépôt, `uvx ruff format --check`
  échouant sur 5 fichiers antérieurs, retiré du contrôle final au journal ; (b)
  `debt-review/references/gabarit-rapport.md`, écarté au plan (Q2). Elles disparaissent avec le plan
  archivé si elles ne sont pas portées au registre.
- **R8** *(reporté — réserve assumée)* — Q3 ouvert : la remontée s'arrête au premier `.claude`, qui
  n'est pas nécessairement le bon en dépôt imbriqué. Compensé par l'impression de l'ancrage dans
  `defs`, constatée à l'exécution.
- **R10** *(reporté — réserve assumée)* — `--def ""` retombe sur le squelette en silence, sortie 0 ;
  `--from ""` de même, par la même cause (`default=""`).

### Bloquants

Aucun. **R14 est levé**, contrôlé à l'exécution et non sur déclaration : les sept critères de
réussite sont atteints, le hors-périmètre est respecté, aucun signal de dérive ne s'est matérialisé,
et le chemin complet « projet neuf → amorçage → première revue » se parcourt sans arrêt indu.
Restent ouverts par arbitrage de l'utilisateur R5, R6, R8 et R10 ; **R7** est un geste de clôture à
faire avant l'archivage, sous peine de perdre deux dettes promises ; **R15** est une réserve mineure
que le suivi ne mentionne pas ; **R16** et **R17** sont neufs et mineurs, l'un de prose, l'autre de
tenue du suivi.

---

## 2026-08-30 — clôture — `ea7235a`

Sixième audit. Le commit traite **R7**, **R15** et **R17**. Les cinq constats laissés ouverts par
arbitrage de l'utilisateur — **R5**, **R6**, **R8**, **R10**, **R16** — sont désormais nommés dans
la section « Dernier audit » du suivi et marqués « à porter au registre de dette pendant la
clôture » ; ils sont donc traités ici en **réserves assumées**, pas en manquements neufs.

Diff entier rejoué depuis `master` (23 fichiers, +3062/−47), pas seulement le dernier commit.

### Vérifications exécutées

Contrôle final, étape 10 du suivi, depuis `skills/list-dir/` :

- `uvx pytest scripts/tests/ -q` → **282 passed** (le chiffre du suivi, corrigé par R17, est exact) ;
- `uvx ruff check .` → `All checks passed!` ;
- `uvx --with pytest basedpyright` → `0 errors, 0 warnings, 0 notes`.

Vérifications déclarées des étapes 1 à 5, une à une, telles qu'écrites :

- `pytest scripts/tests/test_definitions.py -q` → 14 passed ;
- `pytest scripts/tests/test_store_ecriture.py -q` → 36 passed ;
- `pytest scripts/tests/test_entree_cli.py -q -k "init_def"` → 3 passed, 35 deselected ;
- `pytest …::test_defs_liste_et_origine -q` → 1 passed ;
- `pytest …::test_contract_imprime_le_contrat -q` → 1 passed.

Étapes 6, 8 et 9 :

- `grep -c 'douze commandes' skills/list-dir/SKILL.md` → **2** (attendu ≥ 1) ;
- `grep -ril 'dette\|debt' skills/list-dir/` → **aucune sortie** ;
- `grep -c 'list-dir contract' …/dette.md` → **2** ; `grep -c '| \`title\` | requis |'` → **0** ;
  `grep -c 'init .*--def'` → **1** ;
- `awk '/## Étape 0/,/## Étape 1/' skills/debt-review/SKILL.md | grep -c 'dette.md'` → **1**.

Étape 7 — fidélité des semences :

- `diff` du contrat de chacun des trois registres, arbre de données contre semence → **identiques**
  sur les trois ; `diff -r` des `templates/` de `technical-debt` → **identiques**.

Bout en bout, dans un projet neuf hors dépôt (`$D/projet/.claude`) :

- `list-dir defs` → imprime les deux ancrages puis les trois définitions en `rang 4
  config:implementation-tracker` ;
- `init --def` × 3 → 0 ; `validate` × 3 → `0 élément(s) conformes au contrat` ;
- `new` → 0 ; `derive … --template review` → `1 fiche(s) à instruire`, code 0 ;
- `contract` → imprime le contrat en vigueur ;
- définition posée en `<projet>/.claude/list-dir/technical-debt/` → `defs` la donne
  `rang 1 projet (masque config:implementation-tracker)`, et `init --def technical-debt` amorce bien
  `name = "local"` ;
- deux skills de rang 2 portant `dup` → `définition « dup » ambiguë — 2 racines de même rang : …a…,
  …b…`, code **1**, les deux nommées ;
- `init` sans `--def` → squelette `id` / `title` / `[sections] required = ["Constat"]`, identique à
  celui de `master`.

Les **cinq** étiquettes de l'Étape 0 de `debt-review`, produites à l'exécution du bloc tel qu'il est
écrit, dans un projet temporaire :

- trois registres absents → `ABSENT` × 3 ;
- trois registres amorcés et vides → `VIDE` × 3 ;
- une entrée créée → `OK : technical-debt`, `VIDE` sur les deux destinations ;
- une fiche cassée déposée dans `-solde` → `NON CONFORME : technical-debt-solde`, les deux autres
  conservant leur état ;
- `PATH=/nonexistent` → **`OUTIL ABSENT : list-dir`**, une seule ligne, boucle interrompue.

**Le correctif de R15 est donc effectif, et il n'ajoute aucune garde de présence** : ni `command
-v`, ni `type`, ni `which` n'apparaissent dans le bloc — seule la lecture de `rc`. La contrainte de
`contrat.md` (§ Dépendances : la vérification de présence appartient à `sante_skills.py`, une fois
par session) est respectée à la lettre.

Correspondance bloc / puces, revérifiée dans les deux sens après l'ajout de la cinquième étiquette :

- bloc → puces : `ABSENT`, `OUTIL ABSENT`, `NON CONFORME`, `VIDE`, `OK` — les cinq ont une consigne
  (`ABSENT` en a deux, selon le nombre de registres touchés ; `VIDE` en a deux, selon source ou
  destination) ;
- puces → bloc : aucune puce d'état sans déclencheur. `OK` sur `-solde`/`-ecarte` n'a pas de puce
  propre mais est explicitement couvert par la fin de la puce `OK sur technical-debt`.

Registre et dépôt :

- `list-dir validate` sur les trois registres du dépôt → **22 / 15 / 2 éléments conformes**, code 0 ;
- aucun `id` en double parmi les 22, et les deux titres neufs ne recouvrent aucun des vingt
  existants — vérifié entrée par entrée, y compris contre
  `quatre-trous-procedure-debt-review`, le seul qui parle aussi de `debt-review` ;
- `python3 scripts/check_pipeline.py` → **Pipeline conforme** ;
- `python3 scripts/sante_skills.py` → code 0, aucune sortie.

### Conformité à l'intention

Les sept critères de réussite du brief, un par un :

1. **amorcer par le nom → `validate` sort 0** — **atteint**, exécuté sur quatre définitions
   distinctes, dont une posée au rang 1 et une au rang 2.
2. **les trois registres s'amorcent dans un projet vide, `validate` passe sur les trois** —
   **atteint**, exécuté hors dépôt.
3. **`derive` fonctionne après amorçage, `templates/review.{toml,md}` ont suivi** — **atteint** :
   `derive` rend 0 et `1 fiche(s) à instruire` sur la liste amorcée puis remplie.
4. **une définition de `<projet>/.claude/list-dir/<nom>/` s'amorce sans skill porteur** —
   **atteint**, et la précédence sur le rang 4 est constatée dans `defs` comme dans `init`.
5. **`init` sans définition rend le squelette actuel, inchangé** — **atteint**, contrat comparé au
   générateur de `master`.
6. **deux définitions de même rang, même nom → sortie non nulle les nommant toutes les deux** —
   **atteint**, code 1, les deux chemins imprimés.
7. **`grep -ril 'dette\|debt' skills/list-dir/` sans sortie** — **atteint**.

**Symptôme d'origine** — refermé, et vérifié de bout en bout : un projet neuf voit `ABSENT` × 3,
la puce l'envoie à `dette.md`, `dette.md` porte la boucle `init --def` + `validate`, les trois
registres s'amorcent et la revue peut partir. La seule interruption qui subsiste sur ce chemin est
R16, arbitrée.

**Hors-périmètre** — respecté sur les cinq points. Les contrats ne changent pas (prouvé par `diff`) ;
aucune commande existante autre que `init` n'est modifiée (`defs` et `contract` sont neuves, et
`contract` est l'exception ouverte au brief) ; aucun rang « plugins » ; `gabarit-rapport.md` est
intact et son report est désormais **inscrit au registre** ; aucun chemin de re-semis.

**Signaux de dérive** — aucun matérialisé. Pas de mot « dette » dans `list-dir`, découverte par
`iterdir()` et non par registre, copie sans composition, liste amorcée vide (`0 élément(s)`), et la
documentation renvoie à `list-dir contract` plutôt qu'à une semence.

### Qualité du code

**R18** *(nouveau)* — `skills/debt-review/SKILL.md`, Étape 0 — **la phrase de comptage n'a pas suivi
la cinquième étiquette**. Le paragraphe sous le bloc affirme toujours : « Chaque registre imprime
son état, **et il y en a quatre**. » Le bloc en imprime cinq depuis `ea7235a` : `ABSENT`,
`OUTIL ABSENT`, `NON CONFORME`, `VIDE`, `OK`. C'est exactement le mode de défaillance que la même
étape s'écrit deux paragraphes plus bas — « le bloc et les puces vieillissent séparément » — appliqué
cette fois à la phrase qui les compte. Le coût est faible mais direct : un lecteur qui vérifie la
correspondance se fie au nombre annoncé et cherche une étiquette de trop.

La formulation elle-même supporte mal `OUTIL ABSENT` : ce n'est pas l'état *d'un registre*, et le
`break` fait qu'aucun autre registre n'imprime le sien. Un décompte exact dirait « quatre états de
registre, plus un état de l'outil ».

**R19** *(nouveau, mineur)* — `skills/debt-review/SKILL.md`, Étape 0 — **dans un projet neuf,
`ABSENT` masque `OUTIL ABSENT`**. Le test `[ ! -d "$T/$l" ]` précède l'appel à `list-dir` : si les
registres n'existent pas *et* que `list-dir` est introuvable, le bloc imprime trois `ABSENT` et
jamais `OUTIL ABSENT`. Le lecteur suit alors la puce « amorcer, puis reprendre l'étape », et
l'amorçage échoue à son tour sur le même 127 — cette fois de façon visible, ce qui borne le coût.
C'est précisément la conjonction que rencontre un projet neuf sur une machine où le paquet n'est
pas installé, c'est-à-dire le cas d'usage que ce chantier vise. Reste mineur : l'échec est bruyant,
pas silencieux.

Sur le reste du diff, relu intégralement : rien à ajouter aux cinq audits précédents, dont je
confirme le jugement. `definitions.py` reste le module le mieux tenu du chantier — les deux
remontées distinctes, la déduplication sur chemin résolu, le *pourquoi pas* `shutil.which`, et les
trois issues de `resolve()` sont toutes documentées à l'endroit où elles s'appliquent.
`_read_definition` valide en mémoire avant tout `mkdir`, conformément au motif de `derive`.
`init.py`, `defs.py` et `contract.py` respectent la règle de façade et le style des modules voisins.

Une seule scorie de forme, non numérotée parce qu'elle ne relève d'aucun critère :
`references/contrat-liste.md`, bloc bash de la section « Définitions de listes » — la ligne
`list-dir init <cible> --def recettes` n'aligne pas son commentaire sur les deux autres du bloc.

### Dette induite

**R20** *(nouveau)* — `.claude/implementation/todo/technical-debt/ruff-format-jamais-applique.md` —
**le Constat de l'entrée neuve est faux sur `HEAD`, et il l'est dans le sens qui dédouane le
chantier**. L'entrée écrit : « signale **cinq fichiers** à reformater, tous antérieurs au chantier
[…] l'état précède le chantier, qui n'y a rien ajouté. »

Exécuté sur `HEAD`, `uvx ruff format --check .` dans `skills/list-dir/` rend :

```
6 files would be reformatted, 30 files already formatted
  references/contrat-liste.md
  scripts/tests/test_contract.py
  scripts/tests/test_entree_cli.py
  scripts/tests/test_items.py
  scripts/tests/test_loader.py
  scripts/tests/test_move.py
```

Six, et non cinq. Le sixième est `scripts/tests/test_entree_cli.py`, que le chantier a modifié de
225 lignes. Contrôlé : la version de `master` de ce fichier, extraite par `git show` et passée au
même `ruff format --check` avec le `ruff.toml` du skill, rend `1 file already formatted`. **Le
chantier a donc bien ajouté un fichier à la dette qu'il décrit**, sur deux appels de test que
l'auteur a enroulés à la main là où `ruff format` les tiendrait sur une ligne (`test_entree_cli.py`
lignes 454 et 479).

Le geste — porter la dette au registre — est le bon, et l'entrée est par ailleurs bien instruite :
elle pose la question de fond plutôt qu'un geste, et écrit les deux issues. Mais une entrée de
registre est une **mesure**, et celle-ci est fausse d'une unité dans le sens qui arrange : la
prochaine revue lira « rien ajouté par ce chantier » là où le chantier a ajouté. C'est le même
défaut que `trois-lignes-au-dela-de-100-colonnes`, déjà au registre pour avoir sous-mesuré son
propre constat — cette fois avec le précédent sous les yeux.

**R21** *(nouveau — geste de clôture)* — **les cinq constats arbitrés ne sont pas au registre.**
Le suivi les nomme et les marque « à porter au registre de dette pendant la clôture » : R5
(`_read_definition` aplatit `templates/`), R6 (la boucle de l'étape 7 du plan imprime « ÉCHEC
derive »), R8 (Q3 non bordé), R10 (`--def ""` et `--from ""` retombent sur le squelette), R16
(« amorcer puis reprendre l'étape » aboutit à un arrêt sans le dire). Ils ne sont inscrits nulle
part ailleurs que dans le suivi et dans ce fichier, tous deux archivés en `done/` à la clôture.
Ce n'est pas un manquement — la promesse porte sur la clôture, qui n'est pas encore faite — mais
c'est la condition à laquelle R7 a été soldé pour deux autres constats, et elle vaut identiquement
pour ces cinq. **Rien ne doit être archivé avant que ce port soit fait.**

**R5** *(reporté — réserve assumée)* — `store.py:_read_definition` aplatit `templates/` : le
`glob("*")` filtré `is_file()` perd un sous-répertoire sans message.
**R6** *(reporté — réserve assumée)* — `derive` sort 1 sur une liste fraîchement amorcée ; la boucle
de vérification de l'étape 7 du plan imprime « ÉCHEC derive » dans ce cas.
**R8** *(reporté — réserve assumée)* — Q3 : la remontée s'arrête au premier `.claude`, compensée par
l'impression de l'ancrage dans `defs`, constatée à l'exécution.
**R10** *(reporté — réserve assumée)* — `--def ""` retombe sur le squelette en silence, sortie 0 ;
`--from ""` de même, par la même cause (`default=""`).
**R16** *(reporté — réserve assumée)* — « amorcer, puis reprendre l'étape » aboutit à un arrêt qui
ne se dit pas comme tel.

### Bloquants

Aucun. Les sept critères de réussite sont atteints et vérifiés à l'exécution, le hors-périmètre est
respecté sur ses cinq points, aucun signal de dérive ne s'est matérialisé, toutes les commandes de
vérification déclarées passent, et le correctif de R15 fait ce qu'il annonce sans la garde de
présence que `contrat.md` interdit.

Le verdict reste **RÉSERVES** pour trois raisons, toutes levables en un tour : **R20** est une
mesure fausse *déjà inscrite au registre*, qui trompera la prochaine revue si elle n'est pas
corrigée avant l'archivage ; **R21** est le port des cinq constats arbitrés, à faire pendant la
clôture et non après ; **R18** et **R19** sont deux scories de l'Étape 0, la première étant
littéralement le mode de défaillance que cette étape s'est elle-même écrit.

## 2026-08-30 — clôture — `3f12f2a`

Septième audit. Le commit traite **R20** et **R18**. Sept constats — **R5**, **R6**, **R8**, **R10**,
**R16**, **R19**, **R21** — restent ouverts par arbitrage explicite de l'utilisateur ; ils sont
nommés dans la section « Dernier audit » du suivi et marqués « à porter au registre de dette pendant
la clôture ». Ils sont donc repris ici en **réserves assumées**, jamais en manquements neufs.

Diff entier rejoué depuis `master` (23 fichiers, +3307/−47), pas seulement le dernier commit.
Arbre propre (`git status --short` muet) sur `3f12f2a`.

### Vérifications exécutées

Contrôle final, étape 10 du suivi, depuis `skills/list-dir/` :

- `uvx pytest scripts/tests/ -q` → **282 passed in 6.13s** — le chiffre du suivi est exact ;
- `uvx ruff check .` → `All checks passed!` ;
- `uvx --with pytest basedpyright` → `0 errors, 0 warnings, 0 notes`.

Vérifications déclarées des étapes 1 à 5, une à une, telles qu'écrites :

- `pytest scripts/tests/test_definitions.py -q` → 14 passed ;
- `pytest scripts/tests/test_store_ecriture.py -q` → 36 passed ;
- `pytest scripts/tests/test_entree_cli.py -q -k "init_def"` → 3 passed, 35 deselected ;
- `pytest …::test_defs_liste_et_origine -q` → 1 passed ;
- `pytest …::test_contract_imprime_le_contrat -q` → 1 passed.

Étapes 6, 8 et 9, et le test d'indépendance du brief :

- `grep -c 'douze commandes' skills/list-dir/SKILL.md` → **2** ;
- `grep -c 'list-dir contract' …/dette.md` → **2** ;
- `awk '/## Étape 0/,/## Étape 1/' skills/debt-review/SKILL.md | grep -c 'dette.md'` → **1** ;
- `grep -ril 'dette\|debt' skills/list-dir/` → **aucune sortie**.

Dépôt et registre :

- `list-dir validate` sur les trois registres → **22 / 15 / 2 éléments conformes**, code 0 ;
- `python3 scripts/check_pipeline.py` → **Pipeline conforme**, `16 renvois entre skills, tous
  résolvent` ;
- `python3 scripts/sante_skills.py` → code 0, aucune sortie.

Étape 7 — fidélité des semences : `diff` des trois `contract.toml` (semence contre registre du
dépôt) → **identiques** sur les trois ; `diff -r` des `templates/` de `technical-debt` →
**identiques**.

Bout en bout rejoué dans un projet neuf hors dépôt (`$D/projet/.claude`) :

- `list-dir defs` → imprime les deux ancrages, puis les trois définitions en
  `rang 4  config:implementation-tracker` ;
- `init --def` × 3 → 0 ; `validate` × 3 → `0 élément(s) conformes au contrat`, code 0 ;
- `templates/review.md` et `review.toml` présents dans `.list/templates/` de la liste amorcée ;
- `new` → 0 ; `derive … --template review` → `1 fiche(s) à instruire`, code 0 ;
- `contract` → imprime le contrat en vigueur ;
- définition posée en `<projet>/.claude/list-dir/technical-debt/` → `defs` la donne
  `rang 1  projet  (masque config:implementation-tracker)`, et `init --def technical-debt` amorce
  bien `name = "local"` ;
- deux skills de rang 2 portant `dup` → `définition « dup » ambiguë — 2 racines de même rang : …a…,
  …b…`, code **1**, les deux chemins imprimés ;
- `init` sans `--def` → squelette `name` / `description = "<OPTIONNEL>"` / `id` / `title` /
  `[sections] required = ["Constat"] optional = []`, identique au générateur de `master`.

Bloc de l'Étape 0 de `debt-review`, extrait tel qu'il est écrit et exécuté dans trois états :

- registres amorcés, une entrée → `OK : technical-debt`, `VIDE` × 2 sur les destinations ;
- `PATH=/nonexistent`, registres présents → **`OUTIL ABSENT : list-dir`**, une seule ligne, boucle
  interrompue ;
- registres absents **et** `PATH=/nonexistent` → `ABSENT` × 3, jamais `OUTIL ABSENT` (R19, arbitré).

Codes de retour mesurés, à l'appui de R22 ci-dessous :

- `list-dir validate <répertoire absent>` → **1** ;
- `list-dir validate …` avec `PATH=/nonexistent` → **127**.

#### R20 — vérifié en propre

`uvx ruff format --check .` dans `skills/list-dir/` sur `3f12f2a` :

```
5 files would be reformatted, 31 files already formatted
  references/contrat-liste.md
  scripts/tests/test_contract.py
  scripts/tests/test_items.py
  scripts/tests/test_loader.py
  scripts/tests/test_move.py
```

**Cinq, et le compte de l'entrée de dette est désormais exact.** L'antériorité de chacun est
vérifiée et non supposée : les six fichiers ont été extraits de `master` par `git show` dans un
répertoire de travail portant le `ruff.toml` du skill, et le même contrôle y rend
`5 files would be reformatted, 1 file already formatted` — **les cinq mêmes**, le formaté étant
`test_entree_cli.py`. La régression que R20 dénonçait est donc bien éteinte à sa source, et
l'affirmation « chacun vérifié antérieur au chantier » est vraie fichier par fichier.

Contrôlé aussi que le seul défaut de `references/contrat-liste.md` — que le chantier modifie de
+85 lignes — est **antérieur** : `ruff` ne signale que la ligne 240, dans un bloc `python` que
`git blame` attribue au commit `feat(list-dir): registres en répertoires-listes`, hors chantier.
Les 85 lignes ajoutées n'introduisent aucun bloc mal formaté.

Le reformatage de `test_entree_cli.py` est **sans effet sur le comportement** : le diff se réduit à
deux appels dépliés sur une ligne (`lancer(...)` ligne 451, `read_text(encoding="utf-8")` ligne
477), aucune assertion, aucun argument, aucun code de retour touché. Aucune ligne du fichier ne
dépasse les 100 colonnes de `ruff.toml` (`awk 'length>100'` muet), et `ruff check` reste propre :
le correctif ne rouvre pas l'`E501` qui avait causé l'enroulement manuel.

L'entrée `ruff-format-jamais-applique.md` conserve l'erreur au lieu de l'effacer, et étend le
« Pourquoi c'est gênant » dans le bon sens — « l'écart ne grandit pas que vers le passé ». C'est le
traitement le plus utile possible d'une mesure fausse : la mesure est corrigée, la raison pour
laquelle elle a pu l'être est conservée comme argument.

#### R18 — vérifié en propre

La phrase de comptage a disparu. Le paragraphe dit désormais « Chaque registre imprime son état, et
**chaque état a sa puce plus bas** », et un second paragraphe interdit explicitement d'y remettre un
nombre, en donnant le motif. C'est le bon geste : il supprime la classe entière du défaut, pas
l'occurrence.

Correspondance bloc / puces revérifiée dans les deux sens :

- **bloc → puces** : `ABSENT` (deux puces, selon un ou trois registres touchés), `OUTIL ABSENT`,
  `NON CONFORME`, `VIDE` (deux puces, source contre destinations), `OK` — les cinq étiquettes
  imprimables ont une consigne ;
- **puces → bloc** : aucune puce d'état sans déclencheur dans le bloc. `OK` sur `-solde`/`-ecarte`
  n'a pas de puce propre, mais est couvert par la fin de la puce `OK sur technical-debt`.

### Conformité à l'intention

Les sept critères de réussite du brief, un par un, tous vérifiés à l'exécution sur ce SHA :

1. **amorcer par le nom → `validate` sort 0** — **atteint**, sur quatre définitions distinctes dont
   une au rang 1 et une au rang 2.
2. **les trois registres s'amorcent dans un projet vide, `validate` passe sur les trois** —
   **atteint**, exécuté hors dépôt, code 0 les trois fois.
3. **`derive` après amorçage, `templates/review.{toml,md}` ont suivi** — **atteint** : les deux
   gabarits sont dans `.list/templates/` de la liste amorcée, et `derive` rend `1 fiche(s) à
   instruire`, code 0.
4. **une définition de `<projet>/.claude/list-dir/<nom>/` s'amorce sans skill porteur** —
   **atteint**, précédence constatée dans `defs` comme dans le contrat écrit.
5. **`init` sans définition rend le squelette actuel, inchangé** — **atteint**, contrat comparé au
   générateur de `master`.
6. **deux définitions de même rang, même nom → sortie non nulle les nommant toutes les deux** —
   **atteint**, code 1, les deux chemins imprimés.
7. **`grep -ril 'dette\|debt' skills/list-dir/` sans sortie** — **atteint**.

**Symptôme d'origine** — refermé, et vérifié de bout en bout : un projet neuf voit `ABSENT` × 3, la
puce l'envoie à `dette.md`, `dette.md` porte la boucle `init --def` + `validate`, les trois
registres s'amorcent et la revue peut partir. Les seules interruptions résiduelles sur ce chemin
sont R16 et R19, toutes deux arbitrées.

**Hors-périmètre** — respecté sur ses cinq points. Les contrats ne changent pas (prouvé par `diff`
sur les trois semences et les gabarits) ; aucune commande existante autre qu'`init` n'est modifiée
(`defs` et `contract` sont neuves, `contract` étant l'exception ouverte au brief) ; aucun rang
« plugins » ; `debt-review/references/gabarit-rapport.md` est intact et son report est inscrit au
registre ; aucun chemin de re-semis.

**Signaux de dérive** — aucun matérialisé. Pas de mot « dette » dans `list-dir` ; découverte par
`iterdir()`, aucun registre de définitions ; copie sans composition — `_read_definition` lit, ne
fusionne rien ; liste amorcée vide (`0 élément(s)`) ; la documentation renvoie à `list-dir contract`
et jamais à un fichier de semence.

### Qualité du code

**R22** *(nouveau)* — `skills/debt-review/SKILL.md`, Étape 0 — **le correctif de R18 a introduit une
affirmation fausse sur le code de retour, que son propre bloc contredit deux lignes plus haut.** La
phrase réécrite dit :

> `list-dir validate` sort **1** aussi bien sur un répertoire absent que sur des éléments non
> conformes **ou sur un `list-dir` introuvable**, et rend 0 sur une liste vide comme sur une liste
> pleine : **aucun de ces états ne se déduit de son seul code de retour.**

Mesuré : un `list-dir` introuvable rend **127**, pas 1 ; un répertoire absent rend bien 1. Le
membre ajouté est faux deux fois. D'abord sur le chiffre. Ensuite sur la conclusion : le 127 se
déduit précisément de son code de retour, et c'est exactement ce que le bloc au-dessus fait —
`if [ "$rc" -eq 127 ]`. Le mode de défaillance en bas de la même section le dit encore : « `!
list-dir validate` était vrai pour n'importe quel code non nul, **y compris le 127** d'une commande
introuvable ». La prose qui introduit le bloc affirme donc l'inverse de ce que le bloc fait et de ce
que la note de bas de section explique.

Le coût est direct et de la même famille que R15 : un lecteur qui se fie à cette phrase croit que
127 est indiscernable, alors que la seule raison d'être de la branche `-eq 127` est qu'il l'est.
Un correctif futur qui relit cette phrase avant le bloc — l'ordre naturel de lecture — pourrait
supprimer la branche comme inutile et rétablir le diagnostic faux que R15 venait d'éteindre.

C'est le **septième correctif d'affilée à produire un constat neuf sur cette même Étape 0**, et il
le fait cette fois dans la phrase qui vient d'être écrite pour clore le même mode de défaillance —
le paragraphe qui suit dit « le compte s'est déjà périmé une fois » et interdit le nombre ; c'est
la phrase d'à côté, non le nombre, qui a vieilli faux. Le bon geste n'est pas de retirer le
membre ajouté sans le remplacer : la phrase avait de bonnes raisons de mentionner l'outil absent,
puisqu'il produit une étiquette du bloc. Elle doit le nommer pour ce qu'il est — un code **127**,
qui **se** déduit du code de retour, contrairement aux quatre autres états.

**R19** *(reporté — réserve assumée)* — dans un projet neuf sans `list-dir` dans le `PATH`, le test
`[ ! -d "$T/$l" ]` précède l'appel : le bloc imprime `ABSENT` × 3 et jamais `OUTIL ABSENT`.
Reconstaté à l'exécution sur ce SHA. L'échec reste bruyant, pas silencieux.

Sur le reste du diff, relu intégralement : rien à ajouter aux six audits précédents, dont je
confirme le jugement. `definitions.py` reste le module le mieux tenu du chantier — deux remontées
distinctes et motivées, déduplication sur chemin résolu, le *pourquoi pas* `shutil.which`, les trois
issues de `resolve()` documentées là où elles s'appliquent. `_read_definition` valide en mémoire
avant tout `mkdir`, sur le motif de `derive`, et son commentaire dit pourquoi. `init.py` porte la
règle d'exclusion `--def` / `--from` et le refus en code 2 de `--name`/`--description`, chacun avec
son motif. `defs.py` et `contract.py` respectent la règle de façade et le style des modules voisins.

Scorie de forme, non numérotée parce qu'elle ne relève d'aucun critère et déjà signalée à l'audit
`ea7235a` : `references/contrat-liste.md`, bloc bash de « Définitions de listes » — la ligne
`list-dir init <cible> --def recettes` n'aligne toujours pas son commentaire sur les deux autres.

### Dette induite

**R21** *(reporté — geste de clôture, toujours ouvert)* — **les constats arbitrés ne sont pas au
registre.** Contrôlé sur ce SHA : le registre compte 22 entrées, et aucune ne porte trace de R5,
R6, R8, R10, R16 ni R19 (`grep` sur les motifs de chacun → aucune sortie). Ils ne vivent que dans
le suivi et dans ce fichier, tous deux archivés en `done/` à la clôture. Ce n'est pas un manquement
— la promesse porte sur la clôture, qui n'est pas faite — mais c'est la condition à laquelle R7 a
été soldé pour deux autres constats, et elle vaut identiquement pour ceux-là. **Rien ne doit être
archivé avant que ce port soit fait**, R22 y compris.

**R5** *(reporté — réserve assumée)* — `store.py:_read_definition` aplatit `templates/` : le
`glob("*")` filtré `is_file()` perd un sous-répertoire sans message.
**R6** *(reporté — réserve assumée)* — `derive` sort 1 sur une liste fraîchement amorcée ; la boucle
de vérification de l'étape 7 du plan imprime « ÉCHEC derive » dans ce cas. La boucle publiée dans
`dette.md`, elle, ne fait pas de `derive` et n'a pas ce défaut — vérifié à l'exécution.
**R8** *(reporté — réserve assumée)* — Q3 : la remontée s'arrête au premier `.claude`, compensée par
l'impression de l'ancrage dans `defs`.
**R10** *(reporté — réserve assumée)* — `--def ""` et `--from ""` retombent sur le squelette en
silence, sortie 0, par la même cause (`default=""` lu en booléen).
**R16** *(reporté — réserve assumée)* — « amorcer, puis reprendre l'étape » aboutit à un arrêt qui
ne se dit pas comme tel.

### Bloquants

Aucun. Les sept critères de réussite sont atteints et vérifiés à l'exécution, le hors-périmètre est
respecté sur ses cinq points, aucun signal de dérive ne s'est matérialisé, et **toutes** les
commandes de vérification déclarées passent — y compris `ruff format --check`, dont R20 exigeait
que le compte redescende réellement à cinq.

Le verdict reste **RÉSERVES** pour deux raisons. **R22** est un défaut introduit par ce commit :
une phrase de documentation que le code qu'elle introduit contredit, et dont la correction naïve
rouvrirait R15. Il est levable en une ligne, mais il doit être levé avant l'archivage, faute de
quoi il devient un constat de plus à porter au registre. **R21** est le port au registre des sept
constats arbitrés, à faire **pendant** la clôture et non après — c'est la seule chose qui les
sauvera de l'archivage.
