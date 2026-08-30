# Amorcer les répertoires-listes dans un projet neuf

## Context

`debt-review` et `implementation-tracker` s'appuient sur trois répertoires-listes
(`technical-debt`, `-solde`, `-ecarte`) qui n'existent que dans ce dépôt-ci. Dans un projet neuf,
l'Étape 0 de `debt-review` rend trois `ÉCHEC` et **aucune étape ne dit quoi faire ensuite** : les
contrats ne sont écrits nulle part ailleurs que dans l'arbre de données, et `list-dir init` ne
produit qu'un squelette générique (`id`, `title`, une section).

Le manque est déjà nommé dans le code, sans solution — `store.py`, docstring de `init_list` :
« Il ne peut pas venir d'un gabarit : un gabarit vit dans `.list/templates/` d'une liste existante,
et `init` s'adresse précisément au cas où aucune liste n'existe encore. »

Ce chantier crée le chaînon manquant : une **définition de liste** est un répertoire rangé selon
une convention connue de `list-dir`, qui sait la trouver par son nom et en amorcer une liste
conforme. Brief : `.claude/implementation/semences-de-listes.brief.md`.

**Ce qui ne change pas** : une fois amorcée, une liste est détachée de sa définition. Toute
commande travaillant sur une liste lit `<liste>/.list/contract.toml`, jamais une définition
(`contract.py`, `contract_path`). C'est la doctrine existante — `dette.md` : « Le contrat de la
liste fait foi » — et le chantier la renforce au lieu de l'entamer.

---

## Les quatre rangs

Une définition est un répertoire dont le contenu **est** le futur `.list/` : un `contract.toml`,
et un `templates/` facultatif.

| # | Racine | Découverte |
|---|---|---|
| 1 | `<projet>/.claude/list-dir/<nom>/` | remontée depuis `cwd` jusqu'au premier `.claude/` |
| 2 | `<projet>/.claude/skills/*/list-dir/<nom>/` | idem |
| 3 | `<config>/list-dir/<nom>/` | remontée depuis le paquet jusqu'au premier répertoire `.claude` |
| 4 | `<config>/skills/*/list-dir/<nom>/` | idem |

La spécificité prime : le rang 1 masque le rang 4, comme une commande de `.list/commands/` masque
une générique (`loader.py`, `overrides`). L'ambiguïté ne se déclare **qu'à rang égal** — deux
skills du rang 4 portant le même nom sortent non nul en les nommant tous les deux.

Aucune constante de chemin, aucune variable d'environnement, aucune dépendance externe : les deux
racines se trouvent par une remontée, l'une depuis `cwd`, l'autre depuis `__file__` — mais **deux
règles distinctes** : « contient un `.claude` » pour le projet, « est un `.claude` » pour la config.
`Path(__file__)` est le motif déjà employé par `loader.py:36` (`GENERIC_DIR`).

> **Divergence assumée avec le brief** — celui-ci fixait les rangs 3/4 par
> `Path(which("list-dir")).resolve().parents[3]`. Deux raisons de ne pas le suivre : `which` rend
> `None` quand le paquet est appelé par son chemin plutôt que par le lien de `bin/`, ce qui ferait
> disparaître les rangs 3/4 **en silence** ; et un index fixe (`parents[3]`) suppose une
> installation en `~/.claude/skills/list-dir/`, alors que le skill est explicitement conçu pour
> être « déployable ailleurs » (`contrat.md`). La remontée jusqu'à un `.claude` n'a aucune de ces
> deux faiblesses. **À ratifier** — voir « Points laissés ouverts ».

**Déduplication sur chemin résolu** : ce dépôt *est* `~/.claude` **et** contient `~/.claude/.claude/`.
Les rangs 1 et 3 y sont vivants et distincts, mais une même racine atteinte par deux calculs ne
doit pas se dénoncer comme ambiguë.

**Aucune racine trouvée est un état légitime**, pas une erreur : hors de tout `.claude`, `defs` ne
liste rien et `--def` échoue en le disant.

---

## Étapes

Sauf mention contraire, les commandes de vérification se lancent depuis `skills/list-dir/`.

### 1. `listdir/definitions.py` — découvrir et résoudre

Module neuf, sans I/O au-delà de `is_dir()` / `iterdir()`, sur le modèle de `loader.py` (découverte
par le système de fichiers, jamais par un registre).

- `Root` — dataclass figée : `path`, `rank`, `origin` (`"projet"` / `"projet:<skill>"` /
  `"config"` / `"config:<skill>"`), pour que `defs` dise **d'où** vient une définition.
- `project_root(start)` / `config_root(start)` — **deux remontées, pas une** : un projet est un
  répertoire qui *contient* un `.claude`, la configuration *est* un `.claude`. Les confondre casse
  le cas imbriqué de ce dépôt (`~/.claude` porte `~/.claude/.claude`), où la règle unique ferait
  viser le mauvais répertoire à l'un des deux ancrages. Corrigé à l'implémentation de l'étape 1.
- `roots(cwd: Path | None = None, package: Path | None = None) -> list[Root]` — les quatre rangs,
  dédupliqués sur `Path.resolve()`, ordre de spécificité. Les deux paramètres sont explicites :
  c'est ce qui rend la fonction testable sur `tmp_path` sans toucher au vrai dépôt.
- `definitions(roots) -> dict[str, list[Root]]` — tout ce qui est définissable, par nom.
- `resolve(name, roots) -> Result[Path]` — le rang le plus spécifique gagne ; **ambiguïté à rang
  égal → `fail` nommant les deux chemins** ; introuvable → `fail` listant les noms connus, sur le
  modèle du message de commande inconnue de `list-dir.py`.

```bash
cd skills/list-dir && uvx pytest scripts/tests/test_definitions.py -q
```

### 2. `init_list` accepte une définition

`store.py` — signature étendue :
`init_list(list_dir, name="", description="", definition: Path | None = None)`.

- `definition is None` → le squelette actuel, **inchangé** (c'est un critère de réussite).
- Sinon : lire `<definition>/contract.toml`, le valider **en mémoire** par `parse_contract` avant
  tout `mkdir` — le motif de `derive` (« TOUT EST CONSTRUIT EN MÉMOIRE D'ABORD »), pour la même
  raison : une destination à moitié bâtie que la tentative suivante refuserait comme « existe déjà ».
- Copier `contract.toml`, puis `templates/` s'il existe.
- La garde `contrat déjà présent` reste en tête, avant tout le reste.
- **Réécrire la docstring** : elle affirme aujourd'hui l'impossibilité que ce chantier lève. Dire
  le nouveau partage — le squelette en dur reste le défaut ; une définition vit hors de l'arbre
  de données, ce qui est exactement ce qui la rend utilisable quand aucune liste n'existe.

```bash
cd skills/list-dir && uvx pytest scripts/tests/test_store_ecriture.py -q
```

### 3. `init --def` / `--from`

`commands/init.py` — deux options mutuellement exclusives
(`parser.add_mutually_exclusive_group()`) : `--def <nom>` résolu par les rangs, `--from <chemin>`
pris tel quel. Le module reste une façade — `register()` + un appel de bibliothèque, aucune
logique (règle en tête de chaque module de commande).

```bash
cd skills/list-dir && uvx pytest scripts/tests/test_entree_cli.py::test_init_def_inconnu \
  scripts/tests/test_entree_cli.py::test_init_def_et_from_exclusifs -q
```

### 4. `commands/defs.py` — découvrir les définitions

Neuve : les définitions disponibles, leur rang et leur origine, **et la racine de projet retenue**
— sans elle, `--def` n'est découvrable nulle part, et le choix du premier `.claude/` trouvé reste
invisible (voir Q3 aux points ouverts).

```bash
cd skills/list-dir && uvx pytest scripts/tests/test_entree_cli.py::test_defs_liste_et_origine -q
```

### 5. `commands/contract.py` — imprimer le contrat en vigueur

Neuve. `list-dir contract <liste>` imprime `<liste>/.list/contract.toml` **tel qu'il est sur le
disque**, sur le modèle de `show.py`. C'est le moyen dont `dette.md` a besoin à l'étape 8 : sans
elle, la doc devrait renvoyer à un chemin de fichier, et un projet ayant redéfini sa liste lirait
une doc décrivant autre chose que ce que l'outil applique.

```bash
cd skills/list-dir && uvx pytest scripts/tests/test_entree_cli.py::test_contract_imprime_le_contrat -q
```

### 6. Documenter la convention dans `list-dir`

Trois points d'édition dans `SKILL.md`, pas un seul :

- le **frontmatter**, ligne 5 : « Fournit dix commandes génériques (init, new, list, show,
  validate, migrate, move, derive, merge, help) » — devient douze, `defs` et `contract` ajoutées ;
- le **bloc de code** des commandes, lignes 44-53 : deux lignes de plus, et `init` gagne ses options ;
- une section courte sur les définitions, renvoyant à la référence.

`references/contrat-liste.md` — une section « Définitions de listes » après « Structure d'un
répertoire-liste » : la forme d'une définition, les quatre rangs, la règle de spécificité,
l'ambiguïté à rang égal, et **la doctrine** — la définition fait autorité le temps de l'`init`
et pas au-delà ; aucun re-semis, `migrate` remet au contrat *de la liste*.

`list-dir` décrit ici une **forme**, jamais un consommateur :

```bash
test -z "$(grep -ril 'dette\|debt' skills/list-dir/)" || echo "ÉCHEC : list-dir cite un consommateur"
grep -c 'list-dir defs\|list-dir contract' skills/list-dir/SKILL.md   # attendu : >= 2
grep -c 'douze commandes' skills/list-dir/SKILL.md                    # attendu : 1
```

### 7. Les trois semences sous `implementation-tracker`

Copier depuis l'arbre de données, **sans modifier un seul contrat** (hors-périmètre explicite) :

```
skills/implementation-tracker/list-dir/
├── technical-debt/{contract.toml,templates/review.{toml,md}}
├── technical-debt-solde/contract.toml
└── technical-debt-ecarte/contract.toml
```

Vérification — **les trois registres**, dans un répertoire temporaire hors du dépôt, et le
`derive` que seul `technical-debt` porte :

```bash
D=$(mktemp -d)
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  list-dir init "$D/$l" --def "$l" || echo "ÉCHEC init : $l"
  list-dir validate "$D/$l"        || echo "ÉCHEC validate : $l"
done
list-dir derive "$D/technical-debt" "$D/revue" --template review || echo "ÉCHEC derive"
diff <(cat .claude/implementation/todo/technical-debt/.list/contract.toml) \
     <(cat skills/implementation-tracker/list-dir/technical-debt/contract.toml) \
  || echo "ÉCHEC : la semence diverge de l'existant"
rm -rf "$D"
```

### 8. `dette.md` — renvoyer au contrat en vigueur

Remplacer les tableaux de champs et de sections, qui recopient le contrat, par un renvoi à
`list-dir contract "$T/technical-debt"`.

**Ce qui reste**, parce qu'il dit un *pourquoi* absent du contrat : l'`id` clé de référence et de
dédoublonnage, « désigner sans numéro de ligne » et son mode de défaillance, « une entrée sans
Pour solder est un regret », la règle des listes soldée/écartée.

Ajouter la procédure d'amorçage — les trois `list-dir init --def`, puis `validate`.

```bash
grep -c 'list-dir contract' skills/implementation-tracker/references/dette.md  # attendu : >= 1
grep -c '| `title` | requis |' skills/implementation-tracker/references/dette.md  # attendu : 0
grep -c 'init .*--def' skills/implementation-tracker/references/dette.md       # attendu : >= 1
```

### 9. `debt-review` — router l'échec de l'Étape 0

Le bloc actuel (lignes 71-73) constate `ÉCHEC : $l` sans issue. Y ajouter le renvoi vers
l'amorçage de `dette.md`, en une ligne, sans recopier la procédure — `dette.md` en est l'autorité
(règle de `debt-review` sur les renvois plutôt que les recopies).

```bash
# Par motif, jamais par numéro de ligne : le renvoi se déplace au premier bloc réécrit.
awk '/## Étape 0/,/## Étape 1/' skills/debt-review/SKILL.md | grep -c 'dette.md'   # attendu : >= 1
```

### 10. Contrôle final

```bash
cd skills/list-dir
uvx pytest scripts/tests/ -q
uvx ruff check .
uvx --with pytest basedpyright
test -z "$(grep -ril 'dette\|debt' .)" || echo "ÉCHEC : list-dir cite un consommateur"
```

`uvx ruff check .` et `uvx --with pytest basedpyright` sont les formes exactes déclarées par
`contrat.md`, section Dépendances — `--with pytest` est nécessaire, sans quoi `typeCheckingMode:
all` noie les vraies erreurs sous 52 imports `pytest` non résolus.

---

## Tests

Fichier neuf `scripts/tests/test_definitions.py` — ne pas le nommer `test_amorcage.py`, ce nom est
déjà pris par les tests du harnais lui-même. Comme toute la suite, il monte ses racines sur
`tmp_path` : **aucun test ne lit le vrai dépôt** (`conftest.py`, et le test qui le vérifie).

Cas à couvrir :

- une définition trouvée au rang 4 (skill de la config) ;
- le rang 1 masque le rang 4 pour le même nom — et c'est un succès, pas un conflit ;
- deux skills du même rang, même nom → échec nommant les deux chemins ;
- deux racines identiques atteintes par deux calculs → **une** racine après déduplication (le cas
  `~/.claude` imbriqué) ;
- `claude_root` : trouvé en remontant depuis un sous-répertoire, `None` hors de tout `.claude` ;
- aucune racine → `defs` ne liste rien, `--def` échoue en le disant ;
- nom inconnu → échec listant les noms connus ;
- une définition sans `templates/` s'amorce (le `templates/` est facultatif) ;
- un `contract.toml` invalide est refusé **sans rien créer** — la cible n'existe pas après l'échec.

Ajouts aux fichiers existants : `test_store_ecriture.py` (le squelette reste inchangé sans
définition ; une définition copie contrat et gabarits), `test_entree_cli.py` — fonctions nommées,
citées une à une par les étapes 3, 4 et 5 plutôt que sélectionnées par sous-chaîne.

---

## Vérification de bout en bout

Dans un projet neuf, hors de ce dépôt :

```bash
mkdir -p "$TMP/projet/.claude" && cd "$TMP/projet"
list-dir defs                                    # les trois définitions, origine « config:implementation-tracker »
list-dir init .claude/implementation/todo/technical-debt --def technical-debt
list-dir validate .claude/implementation/todo/technical-debt   # sortie 0
list-dir contract .claude/implementation/todo/technical-debt   # le contrat en vigueur
list-dir new .claude/implementation/todo/technical-debt essai  # une entrée au marqueur
list-dir derive .claude/implementation/todo/technical-debt "$TMP/revue" --template review
```

Puis la précédence : poser une définition `technical-debt` dans `$TMP/projet/.claude/list-dir/`,
vérifier que `list-dir defs` la montre au rang 1 et que `--def technical-debt` prend celle-là.

---

## Points laissés ouverts

La relecture par `plan-reviewer` a rendu **RÉSERVES**, neuf constats. Six étaient des défauts de
rédaction — citation fausse, commande de vérification inopérante, `cwd` implicite — et sont
corrigés ci-dessus. Les trois autres appelaient un arbitrage, tranché :

- **Q1 — ancrage des rangs 3/4 : divergence avec le brief ratifiée.** La remontée jusqu'à un
  `.claude` remplace le `which("list-dir")` du brief. Motif : `which` rend `None` quand le paquet
  est appelé par son chemin, ce qui ferait disparaître les rangs 3/4 en silence, et l'index fixe
  `parents[3]` suppose une installation en `~/.claude/skills/list-dir/` alors que le skill est
  conçu pour être déployable ailleurs.
- **Q2 — `gabarit-rapport.md` : hors-périmètre assumé.** Ses sept catégories renvoient à
  `categories.md` et décrivent ce que chaque section *attend* — du jugement, pas une recopie de
  structure comme les tableaux de `dette.md`. À porter au registre de dette à la clôture.
- **Q3 — le premier `.claude/` trouvé n'est pas toujours le bon.** Non tranché, mais rendu
  **visible** : `defs` imprime la racine de projet retenue (étape 4). Border davantage — marqueur
  explicite, remontée jusqu'à la racine git — reste possible et n'est pas fait.

---

## Hors-périmètre

- **Les contrats eux-mêmes ne changent pas** : les semences sont la copie de l'existant, et
  l'étape 7 le vérifie par `diff`.
- **Aucune commande existante** autre que `init` n'est modifiée. `defs` et `contract` sont neuves —
  exception ouverte au brief pour `contract`, dont l'étape 8 a besoin.
- **Les plugins** (`~/.claude/plugins/cache/…/skills/`) ne forment pas un cinquième rang : aucun
  plugin installé ne porte de skill, et un rang qu'on ne peut pas tester s'écrit à l'aveugle.
- **`debt-review/references/gabarit-rapport.md`** n'est pas touché (Q2) : ses sept catégories sont
  un renvoi à `categories.md`, pas une recopie de structure de contrat. Constat à porter au
  registre de dette à la clôture.
- **Pas de re-semis** : aucune commande ne remet une liste existante en phase avec sa définition.
  C'est voulu — un projet qui redéfinit au rang 1 a délibérément pris la main.

## Signaux de dérive

- `list-dir` connaît le mot « dette » → le test des étapes 6 et 10 le dit.
- Un **registre** de définitions au lieu d'une découverte par arborescence — « un registre se
  désynchronise, une arborescence non » (`loader.py`).
- L'amorçage compose des contrats (héritage, surcharge, fusion) : il copie, il ne compose pas.
- L'amorçage crée des entrées : une liste neuve est vide.
- Une documentation qui décrit un contrat que l'outil n'applique pas.
