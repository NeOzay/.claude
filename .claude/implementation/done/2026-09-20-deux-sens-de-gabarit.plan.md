# Renommer le moule de `derive` en « patron », et remettre la prose dans le sens de la dépendance

## Contexte

Le mot « gabarit » désigne aujourd'hui deux choses sans rapport dans le couple `gabarit` /
`list-dir` :

- **le fichier posé depuis une semence** — le skill `gabarit`, le paquet Python, la commande, et le
  champ d'estampille `gabarit = "…"` en tête de chaque fiche ;
- **le moule de `derive`** — la paire `.list/templates/<nom>.{toml,md}` qui projette une liste sur
  une liste neuve. Le code l'appelle `templates/` et `--template`, mais toute la prose et tous les
  identifiants français l'appellent « gabarit ».

Les deux sens sont contradictoires en nature : le premier est un fichier à remplir, le second est ce
qui en fabrique. Ils se croisent déjà dans un même fichier en quatre endroits —
`listdir/definitions.py:36-38` (trois occurrences, deux sens, trois lignes), `listdir/types.py:48`
vs `:84`, `listdir/store.py:147` vs `:431`, `listdir/contract.py:37` vs `:312`.

Rien n'a encore cassé parce que la prose de `list-dir` ne dit nulle part qu'elle dépend de
`gabarit`. Or c'est justement ce que ce chantier corrige : la dépendance de code va de `list-dir`
vers `gabarit` — `listdir` importe `gabarit` dans 8 modules, souvent en pure réexportation, et
`listdir/__init__.py` échoue à l'import sans lui — alors que la prose fait le chemin inverse :
`gabarit/SKILL.md:20`, `semences.md:19` et `semences.md:43` renvoient vers `list-dir/references/`
pour définir le contrat et les quatre racines, et `SKILL.md:46` emprunte à `list-dir validate` ses
deux verdicts. Les six types de
champ sont définis dans `gabarit/scripts/gabarit/types.py:80` et listés uniquement dans
`list-dir/references/format.md:114`.

Le jour où `list-dir` renverra vers `gabarit`, les deux sens se retrouveront sur la même page. D'où
l'ordre : **renommer d'abord, déplacer le socle ensuite.**

Trois entrées de dette décrivent déjà ce chantier :
`gabarit-nomme-deux-choses-dans-list-dir`, `list-dir-depend-de-gabarit-sans-le-dire`, et
`gabarit-porte-des-residus-de-liste` (laissée hors-périmètre).

Brief : `.claude/implementation/deux-sens-de-gabarit.brief.md`.

## Le mot

**patron** — vocabulaire de la couture : ce dont on découpe une forme, et qui ne se remplit jamais.
Le renommage descend jusqu'aux données sur disque et à l'interface : `.list/patrons/` et `--patron`.
Le fichier posé depuis une semence, lui, reste un **gabarit** : ni le skill, ni le paquet, ni la
commande, ni le champ d'estampille ne changent.

---

## Étape 1 — Renommer le moule dans le code, sur le disque et à l'interface

Tout tient dans une seule étape parce que le paquet, les données et les appelants doivent rester
cohérents à chaque commit : la constante qui nomme le répertoire est unique, et si elle change sans
que le disque suive, `_gabarits()` rend un dictionnaire vide des deux côtés d'un `reseed` — les
patrons disparaissent sans qu'aucune commande n'échoue.

**Relever la base avant de toucher quoi que ce soit** — le critère « sans régression » de l'étape 5
n'a sinon aucun référent, le dépôt sortant déjà non nul sur `ruff check` (road-map
`contrat-de-forme-du-paquet`) :

```bash
uvx ruff check skills/list-dir skills/gabarit > /tmp/base-ruff.txt 2>&1; echo "rc=$?"
uvx --with pytest basedpyright > /tmp/base-pyright.txt 2>&1; echo "rc=$?"
```

**Le point d'appui** : `TEMPLATES = "templates"` (`listdir/contract.py:32`) est la seule définition
du nom de répertoire. `source_path`, `_gabarits`, `_poser`, `_ecrire` et `store.py` en dépendent
tous. Elle devient `PATRONS = "patrons"`.

**Identifiants à renommer** (`skills/list-dir/scripts/listdir/`) :

| Aujourd'hui | Demain | Où |
|---|---|---|
| `TEMPLATES` | `PATRONS` | `contract.py:32`, et ses importateurs |
| `_gabarits` | `_patrons` | `provenance.py:735` et ses 6 appels |
| `fusionner_gabarits` | `fusionner_patrons` | `provenance.py:527` |
| `gabarits`, `gabarits_semence` | `patrons`, `patrons_semence` | `provenance.py`, `store.py:717-738` |
| `gabarit` (variable locale) | `patron` | `store.py:431-518`, `definitions.py:108-113` |
| `template` (paramètre) | `patron` | `contract.py:source_path`, `commands/contract.py` |
| `--template` | `--patron` | `commands/derive.py:32`, `commands/contract.py:79` |

**Messages d'erreur destinés à l'utilisateur** — ils sont assertés par les tests, donc ils bougent
dans la même étape : `definitions.py:110-113`, `contract.py:79/84`, `store.py:485/490`,
`provenance.py:101-102`.

**Données sur disque** — quatre répertoires, tous porteurs de la même paire `review.{md,toml}`,
renommés par `git mv` pour que l'historique suive :

```
skills/implementation-tracker/list-dir/technical-debt/templates/      → patrons/
.claude/implementation/todo/technical-debt/.list/templates/           → patrons/
.claude/implementation/todo/technical-debt/.list/semence/templates/   → patrons/
.claude/implementation/todo/technical-debt/.list/backup/templates/    → patrons/
```

Les quatre ensemble : la semence et la copie vive sont comparées fichier par fichier par
`provenance.py`, et un côté renommé seul se lirait comme une suppression plus un ajout.

**`def = "technical-debt/review"` ne change pas** : le second segment nomme le patron `review`, pas
le répertoire. Aucun contrat sur disque n'est réécrit.

**Deux appels externes au drapeau**, corrigés ici pour que rien ne soit cassé entre deux commits —
c'est l'unique exception au hors-périmètre « skills tierces non touchées », et rien d'autre n'y
change :

- `skills/debt-review/SKILL.md:172` — `derive … --template review` → `--patron review`
- `skills/debt-review/references/gabarit-rapport.md:56` — `contract --def … --template review` →
  `--patron review`

**Tests** — les fichiers de `skills/list-dir/scripts/tests/` qui construisent des `templates/` ou
assertent les messages suivent le renommage : `jouet.py` (l'aide qui fabrique les listes d'essai),
`test_derive_merge.py` (29 occurrences), `test_entree_cli.py`, `test_provenance.py`,
`test_reseed.py`, `test_fusion.py`, `test_definitions.py`, `test_store_ecriture.py`,
`test_store_lecture.py`. La liste vient d'un grep sur `template|gabarit` : plusieurs n'y passent que
par `jouet.py` et n'auront rien à changer — c'est `pytest` qui tranche, pas cette énumération. Un
test ajusté pour accepter l'ancien message plutôt que corrigé est un signal de dérive.

**Vérification**

```bash
/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q   # 508 passed
ls .claude/implementation/todo/technical-debt/.list/patrons/                                                     # review.md review.toml
list-dir validate .claude/implementation/todo/technical-debt                                                     # conforme
list-dir contract .claude/implementation/todo/technical-debt --patron review | head -1                           # le contrat du patron
list-dir reseed .claude/implementation/todo/technical-debt --dry-run                                             # aucun conflit, aucun fichier « disparu »
grep -rni 'template' skills/list-dir/scripts skills/debt-review --include=*.py --include=*.md                    # aucune
```

---

## Étape 2 — Renommer le moule dans la prose de `list-dir`

30 emplois, dans `SKILL.md` et les cinq références. Chacun devient « patron » — c'est un changement
de **mot**, pas de sens : une phrase dont la tournure change est hors de cette étape.

Les endroits qui demandent plus qu'un remplacement :

- **`references/provenance.md:33`** — le titre `## \`def\` prend deux formes, et la seconde nomme un
  gabarit` est une **ancre**, citée par `references/operations.md:142`. Le titre et le renvoi
  changent ensemble, sinon le lien meurt.
- **`references/definitions.md:26`** — « Pourquoi une définition peut ce qu'un gabarit ne pouvait
  pas » se lit aujourd'hui comme une comparaison avec le skill `gabarit`. Écrite « … ce qu'un patron
  ne pouvait pas », elle redit ce qu'elle a toujours voulu dire.
- **les arborescences** — `SKILL.md:25`, `format.md:16/21/24`, `definitions.md:15` montrent
  `templates/` : le répertoire devient `patrons/`, et son commentaire « gabarits pour `derive` »
  devient « patrons pour `derive` ».

**Vérification**

```bash
grep -rni 'template' skills/list-dir/SKILL.md skills/list-dir/references/            # aucune
grep -rn 'gabarit' skills/list-dir/SKILL.md skills/list-dir/references/              # aucune
/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py                      # conforme — c'est lui qui contrôle les renvois
```

Le second grep rend **zéro** et non « à relire une à une » : les 30 occurrences de « gabarit » dans
la prose de `list-dir` désignent aujourd'hui toutes un moule, et le premier renvoi légitime vers le
paquet n'arrive qu'à l'étape 4, avec la section « Prérequis ». L'étape se clôt donc sur un code de
retour, pas sur un jugement.

---

## Étape 3 — Poser le socle dans `gabarit/references/format.md`

Une référence neuve, sur le modèle d'« une référence par sujet, chacune fait autorité sur le sien »
(`5a3ec97`). `semences.md` garde les semences, les racines et l'estampille ; `format.md` reçoit ce
que `gabarit` possède déjà en code et prête aujourd'hui en prose :

- **le format d'un fichier** — Markdown à front matter TOML délimité par `+++`, sections en `##`,
  dates et listes natives, erreur de syntaxe localisée à la ligne ;
- **le contrat** — `name`, `description`, `[fields.*]`, `[sections.*]`, l'ordre du TOML qui ordonne
  les sections, `description` exigée partout (clé, pas texte), l'ancien format à deux listes refusé ;
- **les six types admis** — `slug`, `text`, `date`, `enum` (avec `values`), `list`, `int` — avec la
  règle du jeton sur une valeur de `values`. C'est le seul endroit où ils sont écrits, et il est
  désormais celui qui les définit (`gabarit/scripts/gabarit/types.py:80`) ;
- **le préremplissage** — `text` / `command`, leur exclusion mutuelle, le refus sur un champ `list`,
  la conversion sur un `int`, l'échec fermé. Sans les `LISTDIR_*`, qui restent à list-dir :
  l'environnement est fourni par l'appelant ;
- **les marqueurs et les deux verdicts** — `<À REMPLIR>` / `<OPTIONNEL>`, « un marqueur dit qu'il
  faut écrire, jamais quoi écrire », le contrôle de type suspendu sous un marqueur, ce que
  `--filled` réclame et ce qu'il ignore.

`gabarit/SKILL.md` et `references/semences.md` cessent alors de renvoyer vers `list-dir`. Les quatre
emprunts, un par un :

| Où | Ce qu'il emprunte | Demain |
|---|---|---|
| `SKILL.md:20` | `../list-dir/references/format.md#le-contrat` — le renvoi le plus fort | `references/format.md#le-contrat`, interne |
| `SKILL.md:46` | « Deux verdicts, ceux de `list-dir validate` » | les verdicts sont dits ici, sans emprunt |
| `semences.md:19` | le contrat, vers `format.md` de list-dir | `../references/format.md` |
| `semences.md:43` | les quatre racines, vers `definitions.md` de list-dir | décrites dans `semences.md`, qui en est déjà l'autorité pour gabarit |

(`semences.md:32` mentionne les racines de list-dir en prose mais ne porte aucun lien.)

**Ce qui n'entre pas dans `gabarit`** : `id` égal au nom du fichier, `.list/`, `from`, `[origin]`,
`reseed`, les `LISTDIR_*`, les limites de `derive` et `migrate`, `merge`.

**Vérification**

```bash
grep -rn 'list-dir/references\|\.\./list-dir' skills/gabarit/                        # aucun renvoi de gabarit vers list-dir
for t in slug text date enum list int; do                                            # les six types, un par un
  grep -q "\`$t\`" skills/gabarit/references/format.md || echo "type absent : $t"
done
/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py                      # les renvois neufs résolvent
```

---

## Étape 4 — `list-dir` perd le socle et gagne ses « Prérequis »

`references/format.md` (235 lignes) se réduit à ce qui est propre à une liste, et renvoie vers
`gabarit/references/format.md` pour le reste :

- gardé : la structure d'un répertoire-liste, « tout `*.md` à la racine est un élément », `id`
  toujours égal au nom du fichier, `from`, `semence/` et `backup/`, les `LISTDIR_*`, les trois
  limites (`derive` ne préremplit pas les sections, un essai de migration n'exécute aucune
  `command`, rien n'est mémorisé), `merge --filled`, et « l'état d'un élément est porté par son
  répertoire » ;
- parti : le format du fichier, le contrat, les types, le préremplissage générique, les marqueurs.

`SKILL.md` gagne la section **« Prérequis »** que la dette `list-dir-depend-de-gabarit-sans-le-dire`
réclame — Python ≥ 3.12 y est déjà, `gabarit` s'y ajoute : le paquet est localisé par
`listdir/__init__.py` et l'import échoue sans lui, avec renvoi à `skills/gabarit/SKILL.md` pour ce
qu'une liste en tient.

**Les cinq références ne sont pas réorganisées** : elles perdent du texte et gagnent des renvois,
leur découpage ne bouge pas.

**Vérification**

```bash
grep -n 'Prérequis' -A6 skills/list-dir/SKILL.md                                     # la section nomme gabarit et y renvoie
/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py                      # conforme
/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q
```

---

## Étape 5 — Contrôles finaux et registre de dette

**Le contrôle des skills tierces** — `skill-convention`, `intent-brief`, `implementation-tracker`,
`debt-review` emploient « gabarit » pour le fichier posé, qui ne change pas. Vérifier qu'aucune n'en
désignait un moule ; ne rien modifier si le contrôle passe. `scripts/check_pipeline.py:617/675`
porte deux commentaires « gabarit, pas un chemin » qui parlent d'un placeholder de lien : les lire,
les laisser s'ils ne désignent ni l'un ni l'autre des deux sens.

**Deux dettes soldées**, par `debt-review` ou à la main selon l'usage du dépôt :
`gabarit-nomme-deux-choses-dans-list-dir` (« renommer l'un des deux sens ») et
`list-dir-depend-de-gabarit-sans-le-dire` (« écrire la dépendance dans SKILL.md, section
Prérequis »). `gabarit-porte-des-residus-de-liste` reste ouverte — c'est du découpage de paquet.

**Vérification**

```bash
grep -rn 'gabarit' skills/skill-convention skills/intent-brief skills/implementation-tracker skills/debt-review --include=*.md
uvx ruff check skills/list-dir skills/gabarit > /tmp/apres-ruff.txt 2>&1; diff /tmp/base-ruff.txt /tmp/apres-ruff.txt
uvx --with pytest basedpyright > /tmp/apres-pyright.txt 2>&1; diff /tmp/base-pyright.txt /tmp/apres-pyright.txt
```

Les deux `diff` se lisent contre le relevé pris à l'étape 1 : le dépôt sort déjà non nul sur `ruff
check`, et c'est l'écart qui compte, pas le code de retour.

---

## Vérification de bout en bout

```bash
# 1. le mot ne nomme plus qu'une chose
grep -rni 'template' skills/list-dir skills/debt-review --include=*.py --include=*.md   # aucune
grep -rn 'gabarit' skills/list-dir --include=*.py --include=*.md                        # paquet ou fichier posé, jamais un moule

# 2. la prose suit la dépendance
grep -rn 'list-dir/references' skills/gabarit/                                          # aucun
grep -n 'Prérequis' skills/list-dir/SKILL.md                                            # présent

# 3. rien n'a changé de comportement
/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q   # 508 passed
/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py                                                 # conforme

# 4. les listes réelles tiennent, patrons compris
list-dir validate .claude/implementation/todo/technical-debt
list-dir reseed .claude/implementation/todo/technical-debt --dry-run
T=$(mktemp -d); list-dir derive .claude/implementation/todo/technical-debt "$T/revue" --patron review \
  && list-dir validate "$T/revue"

# 5. la forme
uvx ruff check skills/list-dir skills/gabarit
uvx --with pytest basedpyright
```

## Ce que ce plan ne fait pas

- Le fichier posé depuis une semence garde son nom : skill, paquet, commande, lien de `bin/`, champ
  d'estampille `gabarit = "…"` — rien n'y change.
- Aucun changement de comportement : aucune commande ne gagne ni ne perd d'option, aucun verdict ne
  change. C'est un renommage et un déplacement de prose.
- `gabarit-porte-des-residus-de-liste` (déplacer `Item.id` vers `listdir`, purger les docstrings qui
  citent leur consommateur) reste ouverte.
- Les archives de `.claude/implementation/done/` gardent leurs `--template` : ce sont des documents
  figés qui décrivent l'état du dépôt à leur date.
- Les cinq références de `list-dir` ne sont pas réorganisées, et la road-map `rapport-audit-en-liste`
  n'est pas abordée.
