# Répertoires-listes — format de données manipulable par script

## État au 2026-08-20 — plan non validé, révisé

Relu par `plan-reviewer` le 2026-08-19 : **NON CONFORME**. Présenté, décision reportée. Aucun
fichier de suivi n'existe : le chantier n'est pas ouvert, la branche `format-registres` n'est pas
créée.

**Révisions du 2026-08-20** — l'utilisateur a arrêté sept points absents du plan du 19 : structure
de fichiers d'une liste ; surcharge des commandes ; mécanisme de déclaration et de découverte ;
forme `command(args, utils) -> Result` avec typage par protocoles ; **`Result` générique et API
complète importable par les scripts** ; **revue à blanc de bout en bout** ; **paire
`<nom>.toml` / `<nom>.md` pour les listes dérivées** ; **Python ≥ 3.12 (PEP 695) exigé par le
skill**, `typing.Generic` écarté.

Le cinquième point retourne l'architecture : le cœur devient une **bibliothèque** (`listdir/`), et
la CLI n'en est qu'une façade.

| Critère du brief | Servi par |
|---|---|
| dépendance déclarée absente → échec fermé, éprouvé par injection | `REQUIRES`, étape 5 |
| le cas d'usage de référence tourne de bout en bout | étape 16 (revue à blanc) |
| `validate` passe sur les quatre listes | étapes 12, 14 et 16 |
| `git log --follow` remonte au commit de création | étape 9 et Vérification #13 |
| **archive sous `done/revues/<date>-revue.md`** | **non servi** — écart assumé, ci-dessous |

**Arbitrages du 2026-08-20, seconde passe** (après relecture `plan-reviewer`, verdict NON
CONFORME) : les commits de chantier sont **autorisés** pour éprouver la traçabilité ;
`scripts/check-pipeline.sh` **peut être modifié** — l'utilisateur prévoit par ailleurs de le migrer
en Python, ce qui lève le signal de dérive que l'étape 18 déclenchait ; `DESCRIPTION` reste dans les
modules `.py`, **pour ne pas la répliquer**.

Un point reste hors du plan : l'étape qui débranchait `jq` de `hooks/intent-brief-gate.sh`
déclenchait le signal de dérive « si le diff dépasse la réécriture de `debt-review` et des
registres ». C'est un élargissement à ratifier, pas une décision d'exécution.

**Un écart littéral avec le brief est assumé** : le brief veut que « le fichier aggloméré [soit]
archivé sous `done/revues/<date>-revue.md` ». La revue à blanc de l'étape 16 produit un rapport
factice — il reste dans le scratchpad et **rien n'est commité sous `done/revues/`**. Ce qui est
démontré, c'est la mécanique et la conservation des 17 ; le jugement, et donc l'archive réelle,
appartiennent à la première revue post-clôture.

> **Ce fichier n'est pas versionné et son nom est attribué par le harness.** Le contrat du pipeline
> documente le cas : un plan laissé sous son nom généré a déjà été écrasé par celui d'un autre
> chantier. À la reprise, le committer ou le renommer avant d'ouvrir un second plan.

---

## Contexte

Les registres vivants du pipeline (`.claude/implementation/todo/technical-debt.md` et ses deux
compagnons) sont des listes stockées dans un document unique. Toutes les opérations coûteuses le
sont pour cette raison : solder une entrée, c'est découper 30 lignes de prose d'un fichier et les
recoller dans un autre, sans qu'aucune commande ne signale une perte ; dédoublonner, c'est comparer
des intitulés caractère par caractère ; compter, c'est recompter à la main.

Le coût est mesurable dans le dépôt : `skills/debt-review/scripts/trier-revue.sh` fait 177 lignes
dont l'essentiel découpe des blocs `## ` et les recolle, et son en-tête documente un bug déjà
rencontré — des intitulés de pile qui se dupliquaient à chaque passe (7 → 13 → 19) sans qu'aucun
contrôle ne bronche. C'est un bug de manipulation de texte à la main, imposé par le format.

Le chantier remplace ce modèle par le **répertoire-liste** : un répertoire = une liste, un fichier
= un élément, un contrat embarqué qui déclare la structure, et une interface commune — bibliothèque
et CLI — portée par un skill déployable dans n'importe quel dépôt. Principe directeur, arrêté au
brief : *les scripts font la structure, le modèle fait le jugement et la correction*.

Brief : `.claude/implementation/format-registres.brief.md`.

---

## Décisions structurantes

### Structure de fichiers d'une liste

```
.claude/implementation/todo/technical-debt/
├── .list/
│   ├── contract.toml              contrat : champs, sections, description
│   ├── commands/                  commandes propres à CETTE liste
│   │   └── close.py
│   └── templates/                 gabarits pour `derive` — voir « Listes dérivées »
│       ├── review.toml
│       └── review.md
├── filtres-listing-hook-rtk.md    un élément
├── patterns-securite-debranches.md
└── …
```

Une seule règle de lecture, et elle est absolue : **tout `*.md` à la racine d'une liste est un
élément, sans exception**. Tout le reste — contrat, commandes, gabarits — vit sous `.list/`. C'est
ce qui rend le contrôle de conservation trivial et ce qui interdit à un `README.md` de se faire
compter comme un élément — le défaut qui donnait 25 au lieu de 24 dans la version précédente de ce
plan.

**Un élément = un fichier Markdown à front matter TOML**, délimité par `+++`.

```markdown
+++
id = "filtres-listing-hook-rtk"
title = "Les filtres de listing sont cassés par le hook rtk"
date = 2026-08-14
source = "audit-integre"
refs = ["R4"]
+++

## Constat
…prose inchangée…
```

TOML plutôt qu'un format `clé: valeur` maison **parce que `tomllib` est dans la stdlib** : aucune
ligne de parsing écrite à la main, dates et listes natives, erreurs localisées précisément. C'est
la même raison qui fait tout le chantier — le parsing artisanal est ce qu'on supprime. Contrepartie
assumée : les valeurs texte demandent des guillemets, `validate` le signale immédiatement.

**Mais `tomllib` ne sait que lire** — le brief le note, et la stdlib n'a pas d'écrivain TOML. Or
`render()`, `new`, le squelette d'`init` et le contrat écrit par `derive` doivent en émettre. La
justification ci-dessus vaut pour la lecture ; en écriture, la sérialisation serait artisanale,
c'est-à-dire exactement ce que le chantier supprime. Trois règles bornent le problème (arbitrées le
2026-08-20) :

1. **`render()` reconduit le bloc de front matter brut, à l'octet près**, tant que les champs n'ont
   pas été modifiés. Un `Item` conserve le texte source de son front matter à côté des valeurs
   parsées. L'aller-retour lecture→écriture est alors exact par construction — et le modèle qui
   corrige de la prose ne voit jamais son front matter réécrit sous lui.
2. **Un sérialiseur borné aux seuls types déclarables au contrat** — `slug`, `text`, `date`, `enum`,
   listes de chaînes — et à rien d'autre. Quelques dizaines de lignes, un cas par type, fini et
   testable parce que le contrat interdit tout le reste. Il sert au **préremplissage** (`new`,
   `init`, `derive`) **et à la réécriture d'un champ modifié** — c'est le seul autre cas où du TOML
   est émis, et il est borné par les mêmes types. Un type non couvert est une erreur nommant le
   type, jamais une écriture approximative. Un élément dont aucun champ n'a bougé ne passe jamais
   par lui : la règle 1 prime.
3. **`validate` relit ce qui vient d'être écrit** — la règle est déjà posée, elle referme la boucle :
   un TOML mal émis est détecté à l'écriture même, pas trois sessions plus tard.

### Le contrat

`.list/contract.toml`, dans la liste elle-même.

```toml
name = "technical-debt"
description = "Dette technique constatée et non résolue"

[fields.id]
type = "slug"          # toujours obligatoire, toujours égal au nom de fichier

[fields.title]
type = "text"
required = true

[fields.date]
type = "date"
required = true
description = "date du constat, jamais modifiée"

[fields.category]
type = "enum"
required = false
values = ["a-solder", "non-pertinent", "doublon", "pas-une-dette",
          "aggravee", "pertinent", "inverifiable"]

[sections]
required = ["Constat", "Pourquoi c'est gênant", "Pour solder"]
optional = ["Assumé"]
```

**L'état est porté par le répertoire, jamais par un champ** — décision du brief. Les trois registres
de dette deviennent trois listes sœurs avec trois contrats distincts (celui des soldés exige une
section `Soldé le`, celui des écartés une section `Écartée le`).

### Le marqueur de champ à remplir

Un élément prérempli — par `new`, par le squelette d'`init`, par `derive` — porte partout **la même
valeur**, définie une seule fois dans `listdir/types.py` et exportée par `__all__` :

```python
PLACEHOLDER = "<À REMPLIR>"     # requis — tant qu'il est là, l'élément n'est pas instruit
OPTIONAL    = "<OPTIONNEL>"     # facultatif — sa présence n'empêche rien
```

Des constantes, jamais des chaînes recopiées : c'est le principe de source unique du brief appliqué
à la lettre. Rien d'autre n'a le droit de marquer un vide — ni chaîne vide, ni champ omis, ni
tiret. Un champ absent et un champ à remplir sont deux états différents, et seul le second est
légitime dans un élément fraîchement créé.

**`new` pose tout le contrat, requis et facultatif**, parce que la seule présence d'une ligne dit
au modèle ce qu'il peut écrire : ce qu'on ne voit pas n'est jamais rempli. Mais les deux ne se
marquent pas pareil — sans quoi `--filled` réclamerait de remplir du facultatif, ce qui n'a pas de
sens.

**Une seule règle, appliquée aux champs comme aux sections** :

| Déclaré au contrat | Marqueur posé | `--filled` |
|---|---|---|
| champ `required = true` | `<À REMPLIR>` | le réclame |
| champ `required = false` | `<OPTIONNEL>` | l'ignore |
| section de `required` | `<À REMPLIR>` | la réclame |
| section de `optional` | `<OPTIONNEL>` | l'ignore |

Un champ facultatif se marque donc exactement comme une section facultative : `category`, déclaré
`required = false` dans le contrat d'exemple, reçoit `<OPTIONNEL>`. Seul `id` échappe aux deux — il
est renseigné à la création, puisqu'il est le nom du fichier.

**`merge` omet du fichier aggloméré toute section restée à `<OPTIONNEL>`.** Elle a joué son rôle —
guider — et n'a rien à dire dans la sortie ; l'y laisser produirait un rapport constellé de sections
vides.

Les deux valent pour les champs du front matter **et** pour le corps des sections, et se cherchent
en une commande (`grep -rF '<À REMPLIR>'`).

**Conséquence directe : `validate` a deux verdicts.**

| Appel | Vérifie | Le placeholder est |
|---|---|---|
| `validate <liste>` | la **structure** : champs déclarés présents, sections présentes, `id` = nom de fichier | accepté — il occupe la place |
| `validate <liste> --filled` | la structure **et** que plus aucun `<À REMPLIR>` ne subsiste — `<OPTIONNEL>` est ignoré | une violation, nommant champ et fichier |

Sans cette séparation, une liste fraîchement dérivée serait invalide par construction et `derive`
ne pourrait jamais être vérifié. Sur un champ portant le placeholder, le contrôle de **type** est
suspendu : `date = "<À REMPLIR>"` est légitimement une chaîne dans un champ typé `date`, et
`--filled` le signale comme *à remplir*, jamais comme *type invalide* — le message doit dire au
modèle quoi faire, pas le laisser croire à une erreur de format.

**`merge` exige `--filled`** avant d'agglomérer : un rapport qui contiendrait encore `<À REMPLIR>`
se lirait comme instruit alors qu'il ne l'est pas — le mode de défaillance que tout ce chantier
combat. `debt-review` le lance de même avant de rendre la main.

**Le rendu de `merge` est fixé, et il vaut pour toute liste** — pas seulement pour `debt-review` :

| Niveau | Contenu |
|---|---|
| `# ` | le préambule : nom de la liste, date, **compte des éléments face au compte du répertoire** |
| `## ` | un élément — son `title`, ou son `id` à défaut |
| `### ` | les sections de l'élément, décalées d'un niveau |

Le décalage n'est pas cosmétique : les sections d'un élément sont des `## ` dans son fichier. Sans
lui, `grep -c '^## '` compterait les sections en plus des éléments, et le contrôle de conservation
— qui est la raison d'être de `merge` — ne voudrait plus rien dire.

### Les quatre listes

| Liste | Origine | Nature |
|---|---|---|
| `todo/technical-debt/` | migration des 17 entrées actives | permanente |
| `todo/technical-debt-solde/` | migration des 7 soldées | permanente |
| `todo/technical-debt-ecarte/` | **créée vide** — rien à migrer, le `.md` n'existe pas | permanente |
| `done/revues/<date>/` | engendrée par `derive` à chaque revue | éphémère |

`technical-debt-ecarte/` n'a pas de source : le fichier annoncé par `todo/README.md` n'a jamais été
créé. Elle est donc initialisée avec son seul `.list/contract.toml`, exigeant une section
`Écartée le` — ce qui est légitime, puisqu'**une liste vide est valide pour `init` et `validate`**.
`todo/README.md`, qui la dit « créée à la première revue qui en écarte une », est réécrit en
conséquence.

### Listes dérivées : la paire `<nom>.toml` / `<nom>.md`

Une liste engendrée par `derive` a besoin de son propre contrat, sans quoi `validate` échoue dessus
par construction. Ce contrat **vient de la liste source**, sous forme d'une paire de gabarits :

```
todo/technical-debt/.list/templates/
├── review.toml     contrat de la liste engendrée : champs et sections de la fiche de revue
└── review.md       gabarit d'un élément, sections préétablies, au marqueur
```

`derive <src> <dst> --template review` écrit `review.toml` en `<dst>/.list/contract.toml`, puis crée
un élément par élément source à partir de `review.md`. Les « sections préétablies » que le brief
exige viennent donc du contrat, jamais d'une chaîne codée en dur dans `debt-review` — c'est ce qui
laisse le skill générique ignorant de la dette.

Un `--template` dont un des deux fichiers manque est une erreur nommant celui qui manque.

**Ce que `derive` fait — et ce qu'il ne fait pas.** Il **projette la structure** d'une liste sur une
liste neuve. Rien d'autre.

| | |
|---|---|
| Crée une liste | oui : répertoire, contrat copié depuis `<nom>.toml`, un élément par élément source |
| Copie les entrées | **non** : même `id`, mais le corps vient du moule `<nom>.md`, jamais de la source |
| Convertit les entrées | seulement par `from`, champ par champ, déclaré au contrat cible |
| Touche la source | non |
| Destination déjà existante | **erreur** — `derive` ne fusionne ni ne met à jour ; deux revues = deux répertoires datés |

**Pourquoi la prose n'est pas recopiée** : le brief pose le signal de dérive « si une vue dérivée
devient éditable, la source unique est perdue ». Une fiche qui porterait le *Constat* de la dette
qu'elle instruit en ferait un doublon éditable. Ici la fiche ne porte **que du contenu neuf** — le
jugement de la revue, qui n'existe nulle part ailleurs. Elle est éditable justement parce qu'elle
n'est pas une vue.

**Le report par `from`** est le seul emprunt à la source, et il est déclaratif :

```toml
# review.toml — contrat de la liste engendrée
[fields.title]
type = "text"
required = true
from = "title"        # repris de l'élément source

[fields.verdict]
type = "enum"
required = true
values = ["pertinent", "a-solder", "doublon", "non-pertinent"]
                      # pas de `from` : posé au marqueur, c'est au modèle de trancher
```

L'`id` est reporté d'office : c'est le seul lien entre une fiche et la dette qu'elle instruit.
`derive` ne transforme, ne concatène et ne calcule rien — un champ nommé par `from` est recopié, un
champ sans `from` reçoit **le marqueur de son propre statut** : `<À REMPLIR>` s'il est `required`,
`<OPTIONNEL>` sinon, exactement comme `new`. Un script qui déciderait *quoi* reporter serait un script qui
juge.

**`derive` projette, `move` déplace.** `move` fait changer un fichier de liste — `git mv`, l'histoire
suit, l'élément reste le même. `derive` crée un second fichier à côté du premier, sans lien Git,
relié seulement par l'`id`. Les deux ne se remplacent jamais l'un l'autre.

### `Result[T]`, générique

```python
@dataclass(frozen=True)
class Result[T]:
    status: int              # 0 succès · ≠ 0 échec fermé
    value: T | None = None
    message: str = ""        # écrit sur stderr quand status ≠ 0

    def __bool__(self) -> bool:
        return self.status == 0

    def unwrap(self) -> T:
        """La valeur, ou ListError(message) si status ≠ 0."""

def ok[T](value: T) -> Result[T]: ...
def fail(message: str, code: int = 1) -> Result[Never]: ...
```

Le paramètre de type porte réellement : `store.items()` rend un `Result[list[Item]]`,
`store.get(id)` un `Result[Item]`, `store.move(...)` un `Result[Path]`. Un appelant qui traite un
`Result[Path]` comme une liste est une erreur de typage, pas un `AttributeError` à l'exécution.

`unwrap()` existe pour les scripts qui veulent l'exception plutôt que le code retour ; la CLI, elle,
ne l'utilise jamais — elle traduit `status` en code de sortie et `message` en stderr.

**Python ≥ 3.12 est une exigence du skill, arbitrée.** `class Result[T]` et `def ok[T](...)` sont la
syntaxe PEP 695 ; `typing.Generic`, portable dès 3.9, a été écarté au profit de la lisibilité. Le
dépôt a 3.13 et 3.14 (mesuré au brief), mais le skill se veut déployable ailleurs : `list-dir.py`
vérifie `sys.version_info >= (3, 12)` au démarrage et **sort non nul en nommant la version
trouvée** — échec fermé, même règle que partout ailleurs. L'exigence est écrite en tête de
`SKILL.md`.

---

## L'architecture : une bibliothèque, une CLI par-dessus

C'est la décision qui commande toutes les autres. `listdir` est un **paquet Python importable** ;
`list-dir.py` est un point d'entrée mince qui parse des arguments et appelle la bibliothèque.
Un script tiers a exactement les mêmes moyens que la CLI, sans passer par `subprocess` ni reparser
une sortie texte.

```
skills/list-dir/scripts/
├── list-dir.py            point d'entrée CLI (argparse + dispatch, aucune logique métier)
└── listdir/               LA bibliothèque
    ├── __init__.py        surface publique — __all__ ; rien d'autre n'est stable
    ├── types.py           Result[T], Item, Contract, Field, Violation, protocoles
    ├── items.py           lecture / écriture du front matter TOML
    ├── contract.py        chargement et validation du contrat
    ├── store.py           ListStore — toutes les opérations sur une liste
    ├── loader.py          découverte des commandes, surcharges, REQUIRES
    ├── utils.py           implémentation de Utils, façade passée aux commandes
    └── commands/          les neuf commandes génériques
```

Le tiret de `list-dir.py` interdit l'import : le nom importable est `listdir`, sans tiret. Les deux
coexistent volontairement — l'un est une commande, l'autre un module.

**Règle de non-divergence** : aucune commande n'implémente de logique métier. Chacune se réduit à
`register()` plus un appel à une méthode de `ListStore`. C'est mécaniquement vérifiable (aucun
`tomllib`, aucun `open(` dans `commands/`) et c'est ce qui garantit qu'API et CLI ne se séparent
jamais.

### L'API publique

Ce que `from listdir import …` expose, et que `__all__` fige :

```python
lst = open_list("todo/technical-debt")         # Result[ListStore] — accepte str | Path

lst.contract                        # Contract : champs déclarés, sections, description
lst.items()                         # Result[list[Item]]
lst.get("filtres-listing-hook-rtk") # Result[Item]
lst.where(category="doublon")       # Result[list[Item]]   — champs déclarés seulement
lst.create(id, fields)              # Result[Item]         — prérempli du contrat
lst.write(item)                     # Result[Path]
lst.validate(filled=False)          # Result[list[Violation]]  — vide = conforme
                                    # filled=True : exige qu'aucun PLACEHOLDER ne subsiste
lst.move(id, target)                # Result[Path]         — git mv seul
lst.derive(dst, template)           # Result[ListStore]    — écrit <template>.toml en contrat
lst.merge(out)                      # Result[Path]         — conservation vérifiée
```

Et l'élément :

```python
item.id                 # str, toujours égal au nom de fichier
item.path               # Path
item.fields             # Mapping[str, object] — front matter typé par le contrat, en lecture
item.sections           # Mapping[str, str], ordonné — titre de section → prose, en lecture
item.render()           # str — le fichier tel qu'il sera écrit

item.with_fields(**kw)  # Item — copie modifiée ; les valeurs doivent être du type déclaré
item.with_sections(**kw)# Item — idem pour la prose
```

**`Item` est immuable**, et c'est la règle 1 de l'écriture TOML qui l'impose : un `Item` lu porte le
texte brut de son front matter, et `render()` le reconduit tel quel. Muter `fields` en place
laisserait le bloc brut et les valeurs se contredire, sans que rien ne le signale.
`with_fields` / `with_sections` rendent une **copie** dont le bloc brut est marqué périmé — c'est
exactement ce qui dit à `write` de resérialiser, et à lui seul. Un `Item` non passé par ces
méthodes s'écrit à l'octet près.

Et le contrat, dont les commandes ont besoin pour savoir quoi marquer :

```python
contract.name           # str
contract.description    # str
contract.fields         # Mapping[str, Field], ordonné
contract.sections        # required: list[str], optional: list[str]

field.type              # "slug" | "text" | "date" | "enum" | "list"
field.required          # bool
field.values            # list[str] — enum seulement
field.source            # str | None — le `from` du contrat dérivé
```

Un `Violation` nomme le fichier, le champ ou la section, et ce qui manque : c'est ce que `validate`
imprime, et ce qu'un script tiers peut trier lui-même.

**Amorçage depuis un script tiers**, stdlib seule et sans installation — la forme canonique,
documentée dans `references/contrat-liste.md` :

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/list-dir/scripts"))
from listdir import open_list, Result
```

### Typage : les protocoles

Le noyau ne connaît des commandes que ces protocoles ; il n'en importe aucune en dur.

```python
class Utils(Protocol):
    def open(self, list_dir: Path | str) -> Result[ListStore]: ...
    def git(self, *argv: str) -> Result[str]: ...
    def run(self, name: str, argv: list[str]) -> Result[object]: ...
    def ok[T](self, value: T) -> Result[T]: ...
    def fail(self, message: str, code: int = 1) -> Result[Never]: ...

class Command[T](Protocol):
    DESCRIPTION: str
    REQUIRES: list[str]
    def register(self, parser: ArgumentParser) -> None: ...
    def command(self, args: Namespace, utils: Utils) -> Result[T]: ...
```

`utils.run` permet à une commande d'en appeler une autre — c'est ce qui rend une surcharge
décorative plutôt que réimplémentée.

### Déclaration et découverte des commandes

**Découverte par le système de fichiers, jamais par un registre à maintenir** — un registre se
désynchronise, une arborescence non.

- génériques : `skills/list-dir/scripts/listdir/commands/<nom>.py`
- spécifiques à une liste : `<liste>/.list/commands/<nom>.py`

Chaque module déclare au niveau module :

```python
DESCRIPTION = "déplace un élément vers une autre liste (git mv seul)"
REQUIRES    = ["git"]

def register(parser: ArgumentParser) -> None: ...
def command(args: Namespace, utils: Utils) -> Result[Path]: ...
```

`help` lit `DESCRIPTION` et `REQUIRES` **par `ast.parse`, sans importer le module** : pas
d'exécution, pas de coût d'import, et une commande cassée ne fait pas tomber `help`. À l'exécution,
`importlib` ne charge que le module appelé.

**Pourquoi dans le module et non dans `contract.toml`** — le brief formulait l'incertitude en
demandant que le contrat « porte les descriptions que `help` affiche ». Les y mettre les
répliquerait : une commande vit dans un fichier, sa description doit vivre avec elle, sinon les deux
divergent au premier renommage. C'est le principe de source unique du brief, appliqué ici contre sa
propre formulation — arbitré le 2026-08-20.

`REQUIRES` porte la déclaration de dépendances exigée par le brief : le chargeur vérifie chaque
outil par `shutil.which` **avant** d'appeler `command`, et sort non nul en le nommant. C'est la
réponse directe au précédent de `hooks/intent-brief-gate.sh`, qui gardait sur `jq` absent et sortait
0 en silence.

### Surcharge

Résolution en deux couches, **la liste gagne sur le générique**, avec deux exceptions :

- **`validate` et `help` ne sont pas surchargeables.** L'une porte le contrat, l'autre la
  découvrabilité. Une liste qui redéfinit ce que « valide » veut dire vide le contrat de son sens.
  Tentative de surcharge → échec nommant le fichier fautif.
- **`help` affiche `(surchargée)`** sur toute commande générique masquée. Une surcharge invisible
  est un piège.

Partout ailleurs la surcharge est libre, et `utils.run("move", …)` rend le générique accessible :
`close.py` d'une liste de dette = `move` plus l'exigence de la section `Soldé le`.

### Les autres arbitrages

**`move` est un renommage pur** : `git mv` et rien d'autre, pour que la détection de renommage de
Git tienne. La preuve exécutée qui accompagne un solde s'écrit **dans un second commit**.

**`validate` repasse après toute écriture** — c'est ce qui paie la dispense d'écriture directe
accordée au modèle. Elle est lancée en fin de chaque étape, par `debt-review` avant de rendre la
main, et par `scripts/check-pipeline.sh`.

**`where` / `list --where` filtre sur les champs déclarés au contrat, et rien d'autre.** Pas de
recherche plein texte : `grep` la fait déjà mieux.

### Commits de chantier, et la preuve de traçabilité

`CLAUDE.md` interdit tout `git commit` sans accord explicite. **Cet accord est donné pour ce
chantier** (2026-08-20) : sans commits, `move` n'est pas éprouvable — `git mv` échoue sur un fichier
non suivi — et le critère du brief sur `git log --follow` est hors d'atteinte.

Deux niveaux, volontairement séparés :

- **Étape 9, dans un dépôt jetable du scratchpad** (`git init`) : c'est là que `move` est éprouvé
  pour de bon, commits compris, **sans rien écrire dans l'historique du dépôt réel**. Le critère y
  est servi tôt, quand le corriger coûte encore peu.
- **Étapes 12 à 16, dans le dépôt réel** : commits de session normaux, aplatis à la clôture par
  `git-smart-commit`. C'est ce qui rend la Vérification #13 exécutable sur de vrais éléments.

**`git status` montrant `R` ne suffit pas.** Il prouve la détection de renommage au niveau de
l'index ; le brief demande que l'**historique** se traverse. Seul `git log --follow` sur le fichier
de la liste d'arrivée l'établit, et il exige que le renommage soit commité. D'où la règle déjà
posée — `move` est un renommage pur, la preuve d'un solde va dans un **second** commit : un commit
qui mêle déplacement et réécriture fait lâcher la détection, c'est un signal de dérive du brief.

---

## Les neuf commandes génériques

Point d'entrée unique : `python3 "$HOME/.claude/skills/list-dir/scripts/list-dir.py" <cmd> …`

| Commande | Rôle | Méthode API | Surchargeable |
|---|---|---|---|
| `help [liste]` | génériques **et** commandes propres à la liste, avec leur description | — (`loader`) | non |
| `init <dir>` | crée une liste : `.list/contract.toml` squelette | `init_list` | oui |
| `new <liste> <id>` | élément portant **toutes** les sections du contrat : requises au marqueur, optionnelles à `<OPTIONNEL>` | `create` | oui |
| `list <liste> [--where champ=valeur] [--sort champs]` | une ligne par élément : `<id>` puis les champs de `--sort`, séparés par une espace | `where` | oui |
| `show <liste> <id>` | affiche un élément | `get` | oui |
| `validate <liste> [--filled]` | chaque élément contre le contrat ; `--filled` exige en plus qu'aucun `<À REMPLIR>` ne subsiste | `validate` | non |
| `move <liste> <id> <cible>` | `git mv` seul, puis rappelle ce que le contrat cible exige | `move` | oui |
| `derive <src> <dst> --template <nom>` | contrat depuis `<nom>.toml`, un élément par source depuis `<nom>.md` | `derive` | oui |
| `merge <liste> [--out <fichier>]` | agglomère, ordre déclaré, conservation vérifiée, refuse tout `<À REMPLIR>` résiduel, omet les sections restées `<OPTIONNEL>` | `merge` | oui |

**Échec fermé** : sortie ≠ 0 et message nommant la cause — contrat introuvable, champ inconnu passé
à `--where`, élément non conforme, outil de `REQUIRES` absent, gabarit incomplet, `merge` qui perd
un élément en route. Même règle que `scripts/check-pipeline.sh`.

**Une liste sans élément est valide pour `init` et `validate`** — une liste fraîchement créée est
légitimement vide. Elle est en revanche une erreur pour `merge` et `derive`, qui agglomèrent ou
projettent : agglomérer zéro élément sans broncher se lit comme « rien à traiter », exactement le
mode de défaillance que `trier-revue.sh` refuse déjà.

---

## Étapes

- [ ] 1. Squelette du skill et contrat de format — `skills/list-dir/SKILL.md`,
  `skills/list-dir/references/contrat-liste.md` : structure d'une liste, front matter TOML,
  **surface de l'API et forme d'amorçage**, protocoles, règle de surcharge, paire de gabarits,
  **exigence Python ≥ 3.12 en tête de `SKILL.md`** — vérif: `bash scripts/check-pipeline.sh` ;
  `grep -q 'Python ≥ 3.12' skills/list-dir/SKILL.md` ; `references/contrat-liste.md` porte une
  section par sujet annoncé (`grep -c '^## '` ≥ 5) et le bloc d'amorçage `sys.path.insert`
- [ ] 2. `listdir/types.py` — `Result[T]`, `ok`, `fail`, `unwrap`, `Item`, `Contract`, `Field`,
  `Violation`, **`PLACEHOLDER` et `OPTIONAL`**, protocoles `Utils` et `Command[T]` — vérif: chacune
  est définie une seule fois dans tout le paquet (`grep -rn 'À REMPLIR\|OPTIONNEL'
  skills/list-dir/scripts/` → une occurrence chacune, dans `types.py`) ; `python3 -c` construit un `Result`
  succès et un échec, `bool()` distingue les deux, `unwrap()` sur l'échec lève en portant le
  message
- [ ] 3. `listdir/items.py` et `listdir/contract.py` — lecture du front matter TOML, **conservation
  du bloc brut**, `render()`, **sérialiseur borné aux types du contrat**, chargement et validation
  du contrat — vérif: aller-retour lecture→`render()` sur un élément jetable du scratchpad rend le
  fichier octet pour octet, **y compris commentaires, ordre des clés et style de guillemets** (c'est
  la reconduction du bloc brut qui le garantit, pas une resérialisation) ; un `Item` passé par
  `with_fields` se resérialise et `tomllib` relit le résultat, **tandis qu'un `Item` simplement relu
  et réécrit ne bouge pas d'un octet** — c'est la frontière entre les règles 1 et 2 ;
  `item.fields` refuse la mutation en place ; un type hors contrat passé au
  sérialiseur → `Result` d'échec nommant le type ; un `+++` non fermé → échec nommant le fichier et
  la ligne ; un `contract.toml` au TOML invalide → échec localisé
- [ ] 4. `listdir/store.py` et `listdir/__init__.py` — `open_list`, `items`, `get`, `where`,
  `create`, `write` ; `__all__` fige la surface publique — vérif: un script du scratchpad qui
  s'amorce par la forme canonique documentée, crée une liste, y écrit deux éléments et les relit
  par `where` ; `where` sur un champ non déclaré → `Result` d'échec nommant le champ
- [ ] 5. `listdir/loader.py` et `list-dir.py` — découverte des modules dans `listdir/commands/` puis
  `<liste>/.list/commands/`, résolution des surcharges, refus sur `validate` et `help`, contrôle de
  `REQUIRES` par `shutil.which` avant appel, `register` sur argparse, traduction `Result` → code de
  sortie et stderr, garde `sys.version_info >= (3, 12)` nommant la version trouvée — vérif: sans
  argument → code 2 et usage sur stderr ; **injection** d'une
  commande jetable déclarant `REQUIRES = ["outil-absent-xyz"]` → code ≠ 0 nommant `outil-absent-xyz`,
  **sortie consignée telle quelle au journal de décisions du suivi**, d'où le rapport d'audit de
  clôture la reprend — le brief exige qu'elle y figure, et le suivi est le seul porteur qui existe
  à l'étape 5 ; injection d'un `.list/commands/validate.py` → code ≠ 0 nommant le
  fichier
- [ ] 6. `init`, `new`, `show` — `listdir/commands/{init,new,show}.py` — vérif: `init` puis `new`
  sur une liste jetable, `show` rend le fichier créé, champs et sections du contrat présents et
  présents — **aucun champ vide ni omis** : requis au `PLACEHOLDER`, facultatifs à `OPTIONAL`, et
  `id` renseigné de l'argument. Sur le contrat d'exemple — `title` et `date` requis, `category`
  facultatif, 3 sections requises, 1 optionnelle — `grep -cF '<À REMPLIR>'` → **5** et
  `grep -cF '<OPTIONNEL>'` → **2**
- [ ] 7. `ListStore.validate` et la commande `validate` — champs obligatoires, types, enums,
  sections, `id` = nom de fichier — vérif: vert sur la liste jetable, puis un champ obligatoire
  retiré → code ≠ 0 nommant le champ et le fichier ; une valeur hors enum → code ≠ 0 ; le `Result`
  rendu par l'API porte un `Violation` par manquement ; **l'élément prérempli par l'étape 6 passe
  `validate` et échoue `validate --filled`**, dont le message nomme chaque champ à remplir —
  **sans jamais réclamer la section optionnelle restée à `OPTIONAL`** ; un champ typé `date` portant
  `PLACEHOLDER` est signalé comme *à remplir*, jamais comme type invalide
- [ ] 8. `list` avec `--where` et `--sort` — `listdir/commands/list.py` — vérif: `--where` sur un
  champ déclaré filtre, `--where` sur un champ inconnu → code ≠ 0 nommant le champ
- [ ] 9. `ListStore.move` et la commande `move` — vérif: **dans un dépôt jetable du scratchpad**
  (`git init`, deux listes, éléments commités), `move` puis `git status --short` montre
  `R  <ancien> -> <nouveau>` et l'élément n'est pas modifié (`git diff --cached -M --stat` ne compte
  aucune ligne changée) ; après commit du renommage, `git log --follow --oneline` sur le fichier
  d'arrivée **remonte jusqu'au commit de création dans la liste de départ** — c'est le critère du
  brief, servi ici et rejoué sur le dépôt réel en Vérification #13
- [ ] 10. `ListStore.derive` / `ListStore.merge` et leurs commandes, paire `<nom>.toml` /
  `<nom>.md` lue dans `.list/templates/` — vérif: `derive` d'une liste jetable de 3 rend 3 éléments
  **et un `.list/contract.toml` dans la destination**, `validate` vert sur la liste engendrée et
  `validate --filled` rouge (les fiches sont préremplies) ; une fois les fiches remplies à la main,
  `merge` en rend 3 ; un élément retiré entre les deux → code ≠ 0 ; **`merge` sur une liste où
  subsiste un `<À REMPLIR>` → code ≠ 0 nommant le fichier** ; une section laissée à `<OPTIONNEL>`
  n'apparaît pas dans l'aggloméré ; l'aggloméré porte un `# ` de préambule, un `## ` par élément et
  des `### ` pour leurs sections, si bien que `grep -c '^## '` compte les éléments et rien d'autre ; `--template` dont le `.toml` manque →
  code ≠ 0 le nommant ; un champ déclarant `from` porte la valeur de la source, un champ sans `from`
  porte le marqueur ; `derive` vers une destination existante → code ≠ 0
- [ ] 11. `help`, lecture des `DESCRIPTION` et `REQUIRES` par `ast.parse` sans import — vérif:
  `help` liste les 9 commandes ; `help <liste>` y ajoute une commande spécifique posée dans
  `.list/commands/` ; une commande générique surchargée apparaît marquée `(surchargée)` ; un module
  au Python invalide n'empêche pas `help` de rendre les autres
- [ ] 12. Les trois listes permanentes : migration des 24 entrées par un script jetable
  (`scripts/migrate-dette.py`, supprimé à l'étape suivante) **écrit contre l'API** vers
  `todo/technical-debt/` et `todo/technical-debt-solde/`, plus création de
  `todo/technical-debt-ecarte/` vide (contrat exigeant `Écartée le`) — vérif: 24 éléments, chaque
  **Constat** migré retrouvé à l'identique dans le `.md` d'origine (`grep -Fq`), sortie « 24/24 » ;
  `validate` vert sur les **trois** listes, dont la vide
- [ ] 13. Retrait des anciens `.md` et du script de migration ; réécriture de
  `skills/implementation-tracker/references/dette.md` et de `.claude/implementation/todo/README.md`
  (les trois listes, `technical-debt-ecarte/` désormais existante et vide) — vérif:
  `bash scripts/check-pipeline.sh` ; **commit de session** (accord donné, voir « Commits de
  chantier ») : `git log --oneline -1` porte la migration, et `git status --short -- $T` est vide,
  sans quoi la Vérification #13 n'a rien de commité sur quoi s'exécuter
- [ ] 14. **La paire de gabarits** `todo/technical-debt/.list/templates/review.{toml,md}` : le
  `.toml` porte le contrat de la liste de revue (champs et sections de la fiche), le `.md` le
  gabarit d'un élément, sections préétablies et **portant le marqueur** — vérif: les deux fichiers existent ;
  `derive` de `todo/technical-debt/` vers le scratchpad avec `--template review` rend une liste que
  `validate` accepte et que `validate --filled` refuse, une fiche par entrée, chaque section de la
  fiche portant son marqueur selon son statut au contrat ; `grep -ril 'dette\|debt' skills/list-dir/` reste sans
  résultat
- [ ] 15. **Refonte de `debt-review`** sur `derive` → remplir → `merge` : réécriture de
  `skills/debt-review/SKILL.md` et de `references/gabarit-rapport.md`, suppression de
  `skills/debt-review/scripts/trier-revue.sh` — vérif: `git ls-files skills/debt-review` ne contient
  plus `trier-revue.sh` ; `SKILL.md` cite les trois commandes du flux (`derive`, `merge`,
  `validate`) et ne mentionne plus `trier-revue.sh` ; `gabarit-rapport.md` décrit le fichier
  aggloméré rendu par `merge`, préambule compris
- [ ] 16. **Revue à blanc de bout en bout**, sur les 17 entrées réelles, `derive` **vers le
  scratchpad** (`$SCRATCHPAD/revue-a-blanc/`, jamais sous `done/revues/`). Un script de recette
  jetable remplit chaque fiche d'un contenu fixe — il **ne juge rien** : pas de choix
  de catégorie, une valeur constante — **et surtout pas `PLACEHOLDER`**, sinon rempli et non rempli
  ne se distinguent plus. Sinon le signal de dérive « si un script se met à juger » se déclenche. —
  vérif: `derive` rend 17 fiches et un contrat dans la destination, `validate` vert et
  `validate --filled` rouge avant remplissage, les deux verts après ; `merge` rend un rapport à
  17 blocs, préambule « 17 — 17 », et **aucun `<À REMPLIR>` n'y subsiste** ; une fiche retirée avant
  `merge` → code ≠ 0 ; `git status --short` ne montre **rien** sous `done/revues/`
- [ ] 17. `skills/implementation-tracker/references/cloture.md` et
  `skills/implementation-tracker/references/contrat.md` : arborescence, écriture au registre,
  section *Dépendances* — vérif: `bash scripts/check-pipeline.sh`
- [ ] 18. Garde-fou : contrôle 6 de `scripts/check-pipeline.sh` étendu aux appels `python3`
  (modification du script **ratifiée le 2026-08-20** ; le contrôle ne reconnaît aujourd'hui que
  `bash …*.sh`, donc un appel `python3` relatif non gardé passerait) — vérif:
  `bash scripts/check-pipeline.sh` vert, puis injection d'un appel `python3` relatif non gardé dans
  un `.md` de `skills/` → contrôle 6 rouge, injection retirée
- [ ] 19. Passe de vérification d'ensemble — vérif: section *Vérification* ci-dessous, intégralement

---

## Ce qui n'est pas fait

Repris du brief : la vue Neovim de la liste (sujet à part), `road-map.md` (inexistante), et les
autres fichiers du pipeline — briefs, suivis, rapports d'audit — qui restent des documents.

**L'archive réelle d'une revue.** L'étape 16 démontre le flux et la conservation sur les 17 entrées,
mais avec un contenu factice : le rapport reste au scratchpad et rien n'est commité sous
`done/revues/`. Le brief demande le fichier aggloméré « archivé sous `done/revues/<date>-revue.md` » ;
cela suppose d'instruire réellement 17 dettes, donc du jugement, donc une session de `/debt-review`
— un chantier de contenu, pas d'outillage. Écart assumé, reporté à la première revue post-clôture.

**La migration de `scripts/check-pipeline.sh` en Python** — annoncée par l'utilisateur le
2026-08-20, elle est un chantier à part. L'étape 18 se borne à étendre le contrôle 6 aux appels
`python3` dans le script bash existant ; réécrire les six contrôles est hors de ce périmètre.

`hooks/intent-brief-gate.sh` n'est pas touché : le brief ne le cite que comme précédent, et le
signal de dérive « si le diff dépasse la réécriture de `debt-review` et des registres » se
déclenchait.

## Vérification

```bash
S="$HOME/.claude/skills/list-dir/scripts"
L="$S/list-dir.py"
T=.claude/implementation/todo

# 1. Le garde-fou du pipeline
bash scripts/check-pipeline.sh                                   # → Pipeline conforme.

# 2. Les trois listes permanentes valident, la vide comprise,
#    sans garde qui transforme une absence en succès
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  test -f "$T/$l/.list/contract.toml" || echo "ÉCHEC : contrat absent — $l"
  python3 "$L" validate "$T/$l" || echo "ÉCHEC : $l"
done

# 3. Aucun marqueur résiduel : la migration a rempli, pas prérempli
# Les gabarits de .list/ portent légitimement le marqueur : seuls les éléments sont balayés.
find "$T" -mindepth 2 -maxdepth 2 -name '*.md' -not -path '*/.list/*' -exec grep -lF '<À REMPLIR>' {} + \
  && { echo "ÉCHEC : élément non rempli ci-dessus"; false; }

# Les trois listes, la vide comprise — elle est trivialement verte, et c'est justement
# une exclusion silencieuse de moins.
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  python3 "$L" validate "$T/$l" --filled || echo "ÉCHEC : reste à remplir — $l"
done

# 4. Conservation : les 24 éléments migrés, aucun perdu — plus ce que le chantier a
#    lui-même versé au registre depuis (1 au 2026-08-23).
find "$T" -mindepth 2 -maxdepth 2 -name '*.md' -not -path '*/.list/*' | wc -l   # → 25

# 5. Le skill générique ne connaît aucun consommateur
grep -ril 'dette\|debt' skills/list-dir/ ; echo "attendu : aucune sortie"

# 6. Stdlib seule — échec fermé, pas un simple affichage.
#    Les imports relatifs (from .types import …) sont internes au paquet : hors filtre par
#    construction, et c'est le second grep qui établit qu'aucune autre forme n'échappe.
grep -rhE '^[[:space:]]*(import|from) ' "$S" \
  | grep -vE '^[[:space:]]*(import|from) (\.|[a-zA-Z_])' \
  && { echo "ÉCHEC : forme d'import non couverte par le contrôle"; false; }

grep -rhoE '^[[:space:]]*(import|from) [a-zA-Z_][a-zA-Z0-9_]*' "$S" \
  | awk '{print $2}' | sort -u \
  | grep -vxE '__future__|argparse|ast|collections|dataclasses|datetime|importlib|os|pathlib|re|shutil|subprocess|sys|tomllib|types|typing|listdir' \
  && { echo "ÉCHEC : import hors stdlib ci-dessus"; false; }

# 7. L'API est utilisable telle que documentée, et rend des Result typés
python3 - <<'PY'
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/list-dir/scripts"))
from listdir import open_list
r = open_list(".claude/implementation/todo/technical-debt")
assert r, r.message
print(f"{len(r.unwrap().items().unwrap())} éléments")   # → 17
print(open_list("/inexistant").message)                 # → message nommant le répertoire
PY

# 8. La CLI ne double pas la bibliothèque : aucune logique métier dans les commandes.
#    `\bopen(` seul attrape `utils.open(` — la façade que les commandes DOIVENT appeler.
#    Ce qu'on cherche est l'ouverture de FICHIER : `open(` en début d'expression, jamais
#    précédé d'un point.
grep -rnE '(tomllib|(^|[^.[:alnum:]_])open\()' "$S/listdir/commands/" ; echo "attendu : aucune sortie"

# 9. Chaque marqueur n'a qu'une DÉFINITION, une fois tout le paquet écrit.
#    Le motif porte sur l'affectation de la constante, pas sur le texte : un marqueur
#    cité dans une docstring ou un commentaire est de la prose, pas une seconde source
#    de vérité. Compter les occurrences brutes rendait ce contrôle rouge sur du code
#    parfaitement conforme.
for m in 'À REMPLIR' 'OPTIONNEL'; do
  test "$(grep -rE "^[A-Z_]+ *(: *[A-Za-z]+ *)?= *\"<$m>\"" "$S" | wc -l)" -eq 1 \
    || { echo "ÉCHEC : <$m> défini ailleurs qu'une fois — une seule définition attendue"; false; }
done

# 10. Découverte complète : help rend les 10 génériques.
#     Neuf au plan d'origine, dix depuis l'élargissement de périmètre du 2026-08-22
#     qui a ajouté `migrate`.
python3 "$L" help | grep -c '^  [a-z]'                           # → 10

# 11. Dépendance déclarée absente → échec fermé nommant l'outil
d="$T/technical-debt/.list/commands"; mkdir -p "$d"
printf 'DESCRIPTION = "sonde"\nREQUIRES = ["outil-absent-xyz"]\n\ndef register(p): pass\n\ndef command(a, u): return u.ok(None)\n' > "$d/probe.py"
python3 "$L" probe "$T/technical-debt"; echo "code=$?"           # → ≠ 0, nomme outil-absent-xyz
rm -f "$d/probe.py"

# 12. Le flux de revue tourne de bout en bout, hors du dépôt
W=$(mktemp -d)
python3 "$L" derive "$T/technical-debt" "$W/revue" --template review
test -f "$W/revue/.list/contract.toml" || echo "ÉCHEC : derive n'a pas posé de contrat"
python3 "$L" validate "$W/revue"                                 # → vert : la structure y est
python3 "$L" validate "$W/revue" --filled; echo "code=$?"        # → ≠ 0 : tout est au marqueur
ls "$W/revue"/*.md | wc -l                                       # → 17

# Remplissage mécanique, contre l'API : une valeur constante par type déclaré,
# jamais le marqueur. Aucun jugement — c'est le script de recette de l'étape 16.
python3 - "$W/revue" <<'PY2'
import sys, os, datetime
sys.path.insert(0, os.path.expanduser("~/.claude/skills/list-dir/scripts"))
from listdir import open_list, PLACEHOLDER
lst = open_list(sys.argv[1]).unwrap()
for item in lst.items().unwrap():
    # Une valeur du type déclaré, constante, jamais un marqueur — et jamais un choix.
    # Le branchement est explicite : un dict littéral évaluerait `f.values[0]`
    # pour TOUT champ, et lèverait IndexError sur le premier non-enum rencontré.
    def constante(f):
        if f.type == "date":
            return datetime.date(2026, 1, 1)
        if f.type == "enum":
            return f.values[0]
        return "recette"

    champs = {n: constante(f) for n, f in lst.contract.fields.items()
              if item.fields.get(n) == PLACEHOLDER}
    prose = {k: "recette" for k, v in item.sections.items() if v.strip() == PLACEHOLDER}
    lst.write(item.with_fields(**champs).with_sections(**prose)).unwrap()
PY2

python3 "$L" validate "$W/revue" --filled                        # → vert : plus rien à remplir
python3 "$L" merge "$W/revue" --out "$W/revue.md"
# Le compte qui fait foi est celui du préambule : `merge` compte hors blocs de code,
# un grep à la main compterait les « ## » d'une sortie de commande collée.
sed -n 3p "$W/revue.md"                                          # → « 17 élément(s) … 17 fichier(s) »
grep -cF '<À REMPLIR>' "$W/revue.md"                             # → 0
# Une fiche retirée : `merge` NE LE VOIT PAS, et c'est structurel — il compare les blocs
# rendus aux fichiers présents, deux comptes qu'une suppression réduit ensemble. Seule la
# liste SOURCE est une référence extérieure. (R1 de l'audit du 2026-08-23.)
rm -f "$(ls "$W"/revue/*.md | head -1)"
python3 "$L" merge "$W/revue" --out "$W/ko.md"; echo "code=$?"   # → 0 : le trou connu
test "$(python3 "$L" list "$W/revue" | wc -l)" \
   -eq "$(python3 "$L" list "$T/technical-debt" | wc -l)" \
  || echo "conservation rompue : détectée contre le registre"
rm -rf "$W"
git status --short -- .claude/implementation/done                # → vide : rien n'a fui dans le dépôt

# 13. Traçabilité d'un déplacement, éprouvée sur un élément commité par l'étape 13.
#     Deux commits sont créés ici — ils sont aplatis à la clôture par git-smart-commit.
id=$(python3 "$L" list "$T/technical-debt" --sort date | head -1 | cut -d' ' -f1)

python3 "$L" move "$T/technical-debt" "$id" "$T/technical-debt-solde"
git status --short          # → R  …/technical-debt/$id.md -> …/technical-debt-solde/$id.md
git commit -qm "test(move): aller — $id" -- "$T/technical-debt" "$T/technical-debt-solde"

# Le critère du brief : l'historique se traverse, le renommage n'est pas une création
git log --follow --oneline -- "$T/technical-debt-solde/$id.md" | tail -1   # → le commit de l'étape 13
git log --follow --oneline -- "$T/technical-debt-solde/$id.md" | wc -l     # → ≥ 2

python3 "$L" move "$T/technical-debt-solde" "$id" "$T/technical-debt"
git commit -qm "test(move): retour — $id" -- "$T/technical-debt" "$T/technical-debt-solde"
git status --short -- "$T/technical-debt" "$T/technical-debt-solde"   # → vide : rien ne reste
git diff --stat HEAD~2 -- "$T"                                        # → vide : l'aller-retour est neutre
```
