---
slug: description-obligatoire-partout
---

## 2026-09-05 — clôture — `e441337`

**Verdict** : RÉSERVES

Périmètre audité : `git diff master...description-obligatoire-partout` (29 fichiers, +542/-68),
plus les deux fichiers non commités signalés par l'appelant — le suivi et la fiche de dette soldée.

### Vérifications exécutées

- `uv run --with pytest pytest skills/list-dir/scripts/tests -q` → **444 passed in 10.58s**, 0 échec
  (baseline annoncée : 440 ; 4 tests neufs sur la règle).
- `list-dir validate .claude/implementation/todo/technical-debt` → « 46 élément(s) conformes ».
- `list-dir validate .claude/implementation/todo/technical-debt-solde` → « 19 élément(s) conformes ».
- `list-dir validate .claude/implementation/todo/technical-debt-ecarte` → « 2 élément(s) conformes ».
  (Total inchangé, 65 : l'entrée soldée a bien changé de registre, elle n'a pas été dupliquée.)
- `uv run scripts/check_pipeline.py` → « Pipeline conforme. », 8 contrôles verts.
- Contrat neuf, champ sans `description` :
  `printf 'name = "x"\ndescription = ""\n\n[fields.id]\ntype = "slug"\n' > $d/.list/contract.toml && list-dir validate $d`
  → `…/contract.toml: champ « id » — « description » manquante`, code 1.
- Contrat neuf, racine sans `description` → `…/contract.toml: « description » manquante — la clé se
  déclare, fût-elle vide`, code 1.
- Contrat neuf, `description = ""` à la racine, sur le champ et sur la section → accepté, code 0.
- `list-dir init "$e" && list-dir validate "$e"` → « 0 élément(s) conformes », code 0.
- `list-dir derive .claude/implementation/todo/technical-debt "$f" --template review && list-dir validate "$f"`
  → « 46 fiche(s) à instruire » puis « 46 élément(s) conformes », code 0.
- `grep -n "description-obligatoire-sur-les-sections-seulement" skills/list-dir/references/format.md` → vide.
- `grep -rn "asymétrie" skills/list-dir/` → vide.
- `git diff --stat master...description-obligatoire-partout -- '**/.list/backup/'` → vide.
- Audit `tomllib` de tous les `*.toml` du dépôt portant `name` + `fields`/`sections` : **4 seuls
  contrats fautifs, tous dans `.list/backup/`** (`field:id`), c'est-à-dire exactement le périmètre
  volontairement laissé intact.
- Audit `tomllib` de tous les blocs ```` ```toml ```` de `skills/**/*.md` et `.claude/*.md`
  déclarant des champs ou des sections : **aucun exemple de doc n'enfreint la règle**.
- `md5sum` définition / copie de travail / semence pour les 3 `contract.toml` et les 3
  `templates/review.toml` → **octets identiques** dans les quatre triplets.
- Aucune commande NON EXÉCUTÉE.

### Conformité à l'intention

- Critère « un contrat sans `description` sur un `[fields.*]` est refusé en nommant le champ » :
  **atteint, vérifié** — message `champ « id » — « description » manquante`, code 1, sur un cas neuf
  hors fixtures. Le contrôle (`contract.py:426-427`) est le calque exact de celui des sections.
- Critère « `description = ""` reste accepté partout » : **atteint, vérifié** — accepté à la racine,
  sur un champ et sur une section ; deux tests dédiés (`test_champ_description_vide_est_acceptee`,
  `test_contrat_description_vide_est_acceptee`) le figent.
- Critère « `uv run --with pytest pytest skills/list-dir/scripts/tests` passe » : **atteint,
  vérifié** — 444 passed.
- Critère « `format.md` ne décrit plus d'asymétrie et ne renvoie plus à cette dette » : **atteint,
  vérifié** — tableau et bloc cité remplacés par deux paragraphes (`format.md:125-138`), les deux
  `grep` sortent vides. Les seules occurrences résiduelles du slug dans le dépôt sont dans les
  archives `.claude/implementation/done/2026-09-05-decoupe-contrat-liste{,.audit}.md`, qui sont
  l'historique d'un chantier clos et n'avaient pas à bouger.
- Critère « la fiche de dette est passée en `technical-debt-solde` » : **atteint, vérifié** — le
  `move` est commité (`e441337`), la fiche porte sa section `## Soldé le` avec date, chantier et
  sortie de commande recopiée, conformément à `dette.md:219-231`. La séparation en deux commits
  exigée par `dette.md:216` est respectée : le déplacement est commité, la preuve reste en attente
  de l'accord de l'utilisateur.
- Hors-périmètre : **respecté**. Aucun fichier de `debt-review/`, aucun `contrat.md` ni `dette.md`
  touché ; la dette `deux-conventions-de-mode-de-defaillance` n'est pas approchée.
- Signaux de dérive : **aucun matérialisé**. `format.md` ne bouge que sur le paragraphe de la règle
  (`+11/-16`), `operations.md` que sur deux lignes d'exemple. Les fixtures ne reçoivent que des
  ajouts de clé et des reformatages de longueur de ligne — sauf un cas, voir **R5**.
- Symptôme d'origine : **disparu**. Un champ muet ne traverse plus `validate`, et la règle est
  énoncée en un seul endroit.

### Qualité du code

- Le contrôle de racine est placé **après** celui de `name` (`contract.py:372-384`), comme le plan
  l'exigeait : `test_name_manquant` continue d'échouer sur « une liste se nomme » — vérifié par
  l'exécution de la suite.
- Le contrôle de champ est placé **après** le contrôle de `type` et de `values`, exactement là où le
  plan le prévoyait ; les tests `test_type_inconnu…`, `test_enum_sans_values` gardent donc leur
  message d'origine bien que leurs fixtures aient reçu une `description`.
- Style : commentaires en capitales d'attaque, messages en français avec guillemets typographiques,
  `return fail(f"{path}: …")` — conforme aux voisins immédiats. Le commentaire de 5 lignes en tête
  du contrôle de racine est dense mais dans la norme du fichier.

- **R1** — `contract.py:384` — le message de la racine, `« description » manquante — la clé se
  déclare, fût-elle vide`, est le seul des trois à ne pas nommer son endroit : celui du champ dit
  « champ « id » », celui de la section dit « section « A » », celui-ci ne porte que le chemin du
  fichier. `format.md:126` promet pourtant « le contrat est refusé, **en nommant l'endroit** ». Sur
  un contrat qui aurait par ailleurs des champs, le lecteur doit deviner que c'est la racine qui est
  visée. Coût faible, écart réel entre la prose livrée et le code livré.

- **R2** — `skills/list-dir/scripts/tests/test_reseed.py:33` — la constante partagée `SEMENCE` reçoit
  `text = "titre par défaut"` sur `[fields.title]`, et trois tests de suppression locale basculent
  de `description` vers cette clé. C'est le seul endroit du chantier où une fixture est modifiée
  au-delà de l'ajout d'une clé `description` : un **préremplissage** est introduit dans une semence
  que d'autres tests du fichier utilisent pour créer des éléments. La substitution est nécessaire et
  le journal la documente (décision du 2026-09-05), mais elle frôle le signal de dérive « on ajoute
  une clé, on ne refactore pas ». La suite passe ; le risque est qu'un test futur écrit sur `SEMENCE`
  hérite d'un préremplissage qu'il ne demandait pas.

### Dette induite

- **R3** — `provenance.py:578` — `reseed` commence par `load_contract(list_dir)` et abandonne si le
  contrat local est invalide. Une liste dont le `contract.toml` local a perdu une `description` n'est
  donc **plus rattrapable par l'outil** : la seule voie de réparation automatique est fermée, la
  correction devient manuelle. Le journal du suivi assume explicitement cette conséquence ; elle est
  ici enregistrée comme dette, pas comme défaut.

- **R4** — `[origin].version` des trois définitions n'est pas incrémenté (décision assumée du plan).
  Dans ce dépôt, l'effet est nul : copies et semences ont reçu les mêmes octets, `md5sum` le
  confirme. Hors du dépôt, l'effet se **cumule avec R3** : une liste semée ailleurs depuis
  `skills/implementation-tracker/list-dir/*` avec l'ancien texte porte un `[fields.id]` sans
  `description` — son contrat devient invalide, `reseed` refuse d'y toucher (R3), et la version
  identique ne signalerait de toute façon aucun contrat périmé. La seule sortie est l'édition
  manuelle. Aucune telle liste n'existe dans ce dépôt (audit `tomllib` ci-dessus) ; le coût est
  purement externe et différé.

- **R5** — `.list/backup/` conserve 4 contrats que `validate` refuserait désormais
  (`technical-debt`, `-solde`, `-ecarte`, et `templates/review.toml` de `technical-debt`). C'est le
  choix délibéré et argumenté du plan — un backup est un instantané qu'on ne corrige pas sans le
  faire mentir — et rien ne les relit aujourd'hui. Noté pour mémoire : si un jour une commande venait
  à relire un backup, elle buterait sur un contrat invalide, et le message ne dirait pas qu'il
  s'agit d'un instantané légitimement périmé.

### Exactitude des chiffres consignés

- **R6** — `.claude/implementation/todo/technical-debt-solde/description-obligatoire-sur-les-sections-seulement.md`,
  section `## Soldé le` : « `list-dir derive … --template review` puis `validate` → « **47**
  élément(s) conformes » ». Ré-exécuté à l'instant : **46**. Le chiffre a été relevé avant le `move`
  qui a retiré cette entrée même du registre actif. La sortie de refus recopiée juste au-dessus est,
  elle, exacte et reproductible. `dette.md:229` exige « la sortie réelle » : un lecteur qui rejoue
  la commande obtiendra 46 et croira à une régression.

- **R7** — `.claude/implementation/description-obligatoire-partout.md`, `## État courant` : « `list-dir
  validate` sur les 3 registres (**47 / 18** / 2 conformes) ». État réel après l'étape 5 : **46 / 19
  / 2**. La ligne date d'avant le solde et contredit l'état que le même suivi déclare atteint.

### Bloquants

Aucun. Les cinq critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
respecté, aucun signal de dérive ne s'est matérialisé. Le verdict est `RÉSERVES` et non `FAVORABLE`
à cause de **R6** : une fiche de dette soldée dont la preuve chiffrée ne se reproduit plus est
précisément ce que la procédure de solde cherche à empêcher, et elle se corrige en une ligne avant
le commit de preuve, qui n'est pas encore passé.
