# `description` obligatoire sur les champs comme sur les sections

## Contexte

Un contrat de `list-dir` déclare ses champs et ses sections sur le même modèle — `[fields.<nom>]`
et `[sections."<titre>"]`, mêmes clés `required` et `description`. La lecture, elle, ne les traite
pas pareil :

- `contract.py:475` refuse un contrat dont une section n'a pas `description`, en la nommant ;
- `contract.py:422` lit la description d'un champ par `_texte()` (l. 161), qui rend `""` quand la
  clé est absente — aucun test de présence ;
- `contract.py:378` fait de même pour la `description` à la racine du contrat.

Conséquence : un auteur que l'outil force à documenter ses sections laisse ses champs muets sans
jamais s'en apercevoir. `validate` reste vert, et `list-dir contract` sert une description vide
sans distinguer « pas de texte » de « pas documenté ». Le mode de défaillance est silencieux et
durable.

L'asymétrie n'est pas voulue — dette `description-obligatoire-sur-les-sections-seulement`,
ouverte par le chantier `decoupe-contrat-liste` et déjà documentée comme telle en
`format.md:125-141`. **Arbitrage de l'utilisateur : exiger partout** — champs, sections et racine.

Ce qui est exigé est la **présence de la clé**, jamais son contenu : `description = ""` reste
accepté, exactement comme aujourd'hui sur une section (`format.md:133`). C'est ce qui rend un
contrat à moitié documenté visible à la déclaration, sans forcer à rédiger sur-le-champ.

### Ce que coûte le changement, mesuré

| Où | Déclarations sans `description` |
|---|---|
| `contract.toml` du dépôt (12 fichiers) | 1 seul champ, `id`, dans les 3 listes de dette × copie/semence/backup |
| gabarits `templates/review.toml` (4 fichiers) | `[fields.id]` |
| fixtures des tests | ~50 sur 93 déclarations `[fields.*]` / `[sections.*]` |
| squelette écrit par `init_list` (`store.py:810-820`) | `[fields.id]`, `[fields.title]` |
| exemples TOML de la doc | `format.md:79,82,92` · `operations.md:114,119` |

Le coût est donc **dans les fixtures et les exemples**, pas dans les données. Deux points durs, de
même nature : le squelette de `init_list` et le gabarit de `derive` sont des **contrats produits
par l'outil**. Sans correction, `list-dir init` et `list-dir derive … --template review`
produiraient un contrat que `validate` refuse aussitôt.

Le chiffre des fixtures est un ordre de grandeur — le comptage varie de 48 à 63 selon la façon de
borner un bloc TOML inline. À recompter à l'exécution, pas à lire comme une liste close.

**Baseline** : 440 tests passent, les 3 registres de dette sont conformes.

## Étapes

Les étapes 1 et 2 amènent le dépôt à l'état que l'étape 3 rendra obligatoire, en gardant tout vert
à chaque instant : **compléter avant d'exiger**. Aucune modification de `contract.py` avant
l'étape 3.

### 1. Compléter les contrats produits par l'outil, les données et la doc

- **Squelette de `init_list`** (`skills/list-dir/scripts/listdir/store.py:810-820`) : ajouter
  `description = ""` sous `[fields.id]` et `[fields.title]`, sur le modèle du
  `[sections."Constat"]` qui en porte déjà une. Deux tests le lisent —
  `test_entree_cli.py:321` et `test_provenance.py:200` — les ajuster si besoin.
- **Gabarit de `derive`** : `[fields.id]` dans les 4 `templates/review.toml` — la définition
  `skills/implementation-tracker/list-dir/technical-debt/templates/review.toml`, la copie de
  travail `.claude/implementation/todo/technical-debt/.list/templates/review.toml` et sa
  `semence/`. Tous les autres champs et sections de ce gabarit en ont déjà une.
- **Définitions et listes vivantes** : `[fields.id]` dans les 3 contrats de définition
  `skills/implementation-tracker/list-dir/{technical-debt,technical-debt-solde,technical-debt-ecarte}/contract.toml`,
  et dans les copies de travail et semences correspondantes
  `.claude/implementation/todo/<liste>/.list/contract.toml` et `.list/semence/contract.toml`.
  Définition, copie et semence doivent recevoir **les mêmes octets** : `validate` compare la copie
  de travail à `.list/semence/` (`provenance.py:145,194`) et signalerait « modifié depuis le
  semis » si l'une bougeait seule ; la définition suit pour que le prochain semis parte du même
  texte.
- **`.list/backup/` n'est pas touché.** C'est « ce que le dernier `reseed` a remplacé »
  (`format.md:22`), jamais relu — `provenance.py` ne fait qu'y écrire. Le corriger le ferait
  mentir.
- **Exemples TOML de la doc** : `format.md:79,82,92` et `operations.md:114,119`. Correction
  d'exemple, pas réécriture de prose — sans elle, la référence qui énonce la règle montrerait
  des contrats refusés.

Vérification :

```bash
uv run --with pytest pytest skills/list-dir/scripts/tests -q          # 440 passed
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  list-dir validate .claude/implementation/todo/$l; done              # 47 / 18 / 2 conformes
git diff --stat -- '**/.list/backup/'                                 # vide
```

### 2. Compléter les fixtures de tests

Les déclarations sans `description` de `skills/list-dir/scripts/tests/` — `jouet.py` et les
contrats TOML inline des `test_*.py`. Ajouter `description = ""` : **une clé, rien d'autre**.
Ajouter de même la `description` racine aux contrats inline qui n'en ont pas (motif fréquent :
`name = "n"\n\n[…]`).

Recompter le périmètre au début de l'étape plutôt que de se fier au chiffre du contexte.

Vérification :

```bash
uv run --with pytest pytest skills/list-dir/scripts/tests -q
```

### 3. Exiger `description` dans `contract.py`

Trois contrôles, tous sur le modèle exact de celui des sections (`contract.py:475-476`) : tester
la **présence de la clé** avant de lire sa valeur par `_texte()`.

- **champ** — dans la boucle `for name, value in declared.unwrap().items()`, avant la ligne 422 :
  `if "description" not in body: return fail(f"{path}: champ « {name} » — « description » manquante")`
- **racine** — à la place de la ligne 378, sur `raw`. Le message doit dire que c'est la clé qui
  manque, pas du texte : la valeur reste libre. Le contrôle de `name` (l. 372-376) reste **avant**,
  pour que `test_contract.py:226` continue d'échouer sur « une liste se nomme ».
- **section** — inchangé, il sert de modèle.

Tests à ajouter dans `skills/list-dir/scripts/tests/test_contract.py`, en miroir de
`test_section_sans_description_est_refusee` (l. 208) et
`test_section_description_vide_est_acceptee` (l. 214) :

- un champ sans `description` est refusé, le message nomme le champ ;
- `description = ""` sur un champ reste accepté ;
- un contrat sans `description` racine est refusé ;
- `description = ""` à la racine reste accepté.

Vérification :

```bash
uv run --with pytest pytest skills/list-dir/scripts/tests -q
list-dir validate .claude/implementation/todo/technical-debt
```

### 4. Écrire la règle dans `format.md`

`skills/list-dir/references/format.md:125-141` : remplacer le tableau de l'asymétrie **et** le
bloc cité qui renvoie à la dette par l'énoncé de la règle unique — `description` est exigée sur
un champ, sur une section et à la racine ; sa valeur reste libre, `description = ""` est accepté ;
un contrat sans elle est refusé en nommant l'endroit.

Le paragraphe voisin (l. 120-123, « une section se déclare en table, sur le modèle de
`[fields.*]` ») devient exact sans retouche : c'est le bénéfice recherché.

**Aucune autre prose n'est modifiée** — ni `contrat.md`, ni `dette.md`, ni `debt-review/`.

Vérification :

```bash
grep -n "description-obligatoire-sur-les-sections-seulement" skills/list-dir/references/format.md  # vide
grep -n "asymétrie" skills/list-dir/references/format.md                                           # vide
uv run scripts/check_pipeline.py
```

### 5. Solder la dette

Procédure de `skills/implementation-tracker/references/dette.md`, section « Solder ». Elle exige
**deux commits séparés** — le déplacement d'abord, la preuve ensuite — sans quoi l'historique de
l'entrée s'arrête au jour du solde. Rappel : **aucun commit sans accord explicite de
l'utilisateur** (`CLAUDE.md`) ; l'étape prépare les deux, elle ne les déclenche pas seule.

```bash
T=.claude/implementation/todo
list-dir move "$T/technical-debt" description-obligatoire-sur-les-sections-seulement "$T/technical-debt-solde"
```

Puis la section `## Soldé le` de l'entrée déplacée : date, nom du chantier, et **la sortie réelle**
de la commande qui l'établit — celle-ci, dont la sortie est à recopier telle quelle dans la fiche :

```bash
d=$(mktemp -d) && mkdir -p "$d/.list" \
  && printf 'name = "x"\ndescription = ""\n\n[fields.id]\ntype = "slug"\n' > "$d/.list/contract.toml" \
  && list-dir validate "$d"
```

Vérification de l'étape :

```bash
list-dir validate "$T/technical-debt-solde"                                    # 19 conformes
ls "$T/technical-debt/description-obligatoire-sur-les-sections-seulement.md"   # absent
grep -n "Soldé le" "$T/technical-debt-solde/description-obligatoire-sur-les-sections-seulement.md"
```

## Décisions prises dans ce plan

- **Ce qui est exigé est la clé, pas le texte.** `description = ""` reste accepté partout. Toute
  autre lecture rendrait invalides des contrats du dépôt et forcerait à rédiger au moment le moins
  propice.
- **Compléter avant d'exiger** (étapes 1-2 puis 3). L'ordre inverse laisserait la suite de tests
  rouge entre les étapes, et aucune ne serait vérifiable seule.
- **`.list/backup/` est laissé intact**, à la différence de `.list/semence/` : l'un est un
  instantané du passé que rien ne relit, l'autre le point de référence vivant de `reseed`.
- **`[origin].version` des définitions n'est pas incrémenté** (aujourd'hui `version = 2`). Copies
  et semences reçoivent les mêmes octets, aucune règle documentée n'impose l'incrément.
  Conséquence assumée : une liste semée ailleurs depuis ces définitions ne verra pas ce
  changement comme un contrat périmé.

## Vérification de bout en bout

```bash
uv run --with pytest pytest skills/list-dir/scripts/tests -q
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  list-dir validate .claude/implementation/todo/$l; done
uv run scripts/check_pipeline.py

# la règle mord réellement, sur un cas neuf
d=$(mktemp -d) && mkdir -p "$d/.list" \
  && printf 'name = "x"\ndescription = ""\n\n[fields.id]\ntype = "slug"\n' > "$d/.list/contract.toml" \
  && list-dir validate "$d"   # doit refuser en nommant le champ « id »

# les deux contrats produits par l'outil restent immédiatement valides
e=$(mktemp -d)/l && list-dir init "$e" && list-dir validate "$e"
f=$(mktemp -d)/revue \
  && list-dir derive .claude/implementation/todo/technical-debt "$f" --template review \
  && list-dir validate "$f"
```
