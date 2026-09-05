# Le format d'une liste

Ce qu'est un répertoire-liste, ce qu'est un élément, et ce que le contrat déclare. Tout ce qui
suit est mécaniquement vérifiable par `validate`.

---

## Structure d'un répertoire-liste

```
ma-liste/
├── .list/
│   ├── contract.toml          contrat : champs, sections, description
│   ├── commands/              commandes propres à cette liste
│   │   └── close.py
│   ├── templates/             gabarits pour `derive`
│   │   ├── review.toml
│   │   └── review.md
│   ├── semence/               la semence intacte, au dernier semis
│   │   ├── contract.toml
│   │   └── templates/
│   └── backup/                ce que le dernier `reseed` a remplacé
│       ├── contract.toml
│       └── templates/
├── premier-element.md
└── second-element.md
```

**Tout `*.md` à la racine d'une liste est un élément, sans exception.** Tout le reste vit sous
`.list/`. La règle n'admet pas de fichier de service à la racine : un `README.md` posé là se ferait
compter comme un élément, et le contrôle de conservation d'une agglomération rendrait un nombre
faux sans broncher.

`semence/` et `backup/` n'existent que sur une liste semée depuis une définition, et n'ont de sens
que pour `reseed` : [Provenance et péremption](../references/provenance.md#provenance-et-péremption).

Une liste **sans aucun élément est valide** pour `init` et `validate` : une liste fraîchement créée
est légitimement vide. Elle est en revanche une **erreur** pour `merge` et `derive` — agglomérer ou
projeter zéro élément se lirait comme « rien à traiter ».

---

## Un élément

Un fichier Markdown à front matter TOML, délimité par `+++`.

```markdown
+++
id = "premier-element"
title = "Un intitulé"
date = 2026-08-20
refs = ["R4"]
+++

## Constat

…prose…

## Pour solder

…prose…
```

- `id` est **toujours** égal au nom de fichier, sans l'extension. C'est la seule identité.
- Le front matter est du TOML : dates et listes sont natives, les valeurs texte prennent des
  guillemets. Une erreur de syntaxe est localisée à la ligne.
- Les titres de section sont des `##`.

---

## Le contrat

`.list/contract.toml`, dans la liste elle-même. Il déclare ce qu'un élément doit contenir.

```toml
name = "ma-liste"
description = "À quoi sert cette liste"

[fields.id]
type = "slug"          # toujours obligatoire, toujours égal au nom de fichier

[fields.title]
type = "text"
required = true

[fields.date]
type = "date"
required = true
description = "date du constat, jamais modifiée"
command = "date +%F"   # la sortie de cette commande, à la place du marqueur

[fields.category]
type = "enum"
required = false
values = ["a-traiter", "doublon", "sans-objet"]

[sections."Constat"]
required = true
description = "ce qui a été observé, factuel, sans remède"

[sections."Pour solder"]
required = true
description = "ce qu'il faut faire pour que la dette disparaisse"

[sections."Assumé"]
required = false
description = ""
text = "Rien d'assumé à ce jour."   # ce texte, à la place du marqueur
```

Types admis : `slug`, `text`, `date`, `enum` (avec `values`), `list` (de chaînes). Tout autre type
est une erreur nommant le type.

**Une valeur de `values` est un jeton** : ni vide, ni porteuse d'espace. Le contrat est refusé
sinon, en nommant la valeur fautive. Une valeur à blanc traverserait toute substitution de commande
en se découpant — `contract … --values category` la rend bien sur une ligne, mais un appelant qui
boucle dessus compterait deux catégories fantômes, chacune à zéro, sans qu'aucune commande
n'échoue ; une valeur vide, elle, disparaîtrait sans laisser de trace.

**Une section se déclare en table, une par section**, sur le modèle de `[fields.*]` : le titre est
la clé, `required` dit si elle est obligatoire (défaut `false`), `description` dit ce qu'il faut y
écrire. C'est l'ordre du TOML qui ordonne les sections dans un élément créé — pas un tri par
`required`.

**`description` n'est pas exigée des deux côtés**, et c'est une asymétrie, non une règle :

| Où | `description` | Absente |
|---|---|---|
| `[sections.*]` | **obligatoire** | le contrat est refusé, en nommant la section |
| `[fields.*]` | facultative | vaut `""` |
| racine du contrat | facultative | vaut `""` |

Sur une section, **sa valeur reste libre** : `description = ""` est accepté. Une section non
documentée reste donc visible comme telle, sans qu'on soit forcé d'en rédiger le texte au moment où
on la déclare. C'est `list-dir contract <liste>` qui la sert, à côté de celle des champs — laquelle
peut être vide sans que rien ne l'ait réclamée.

> L'asymétrie n'est pas voulue : la raison qui fait exiger une description de section vaut telle
> quelle pour un champ. La résorber est une dette ouverte
> (`description-obligatoire-sur-les-sections-seulement`), et le sens de la symétrie — exiger
> partout, ou nulle part — reste à trancher.

**L'ancien format à deux listes** — un unique `[sections]` portant deux listes de noms, `required`
et `optional` — est refusé, avec un message nommant la liste à migrer. La réécriture est manuelle :
aucune commande ne la fait, et la semence de la liste est l'endroit où corriger. Tolérer les deux
formes en lecture, ce serait les laisser diverger : la documentation d'une section n'existerait que
dans l'une des deux écritures, et rien ne dirait laquelle fait foi.

**L'état d'un élément est porté par son répertoire, jamais par un champ.** Une liste d'éléments
soldés est une liste sœur avec son propre contrat, pas un champ `soldé = true` — un état porté par
un champ se change par une écriture, porté par le répertoire il se change par un renommage, que
l'historique conserve.

### Préremplir un champ ou une section

Deux clés facultatives, sur `[fields.*]` comme sur `[sections.*]` :

| Clé | Ce qu'elle pose à la place du marqueur |
|---|---|
| `text` | le texte, **littéral** — aucune substitution, ni `{{id}}` ni `$VAR` |
| `command` | la sortie standard d'une commande Bash, débarrassée de ses blancs de bord |

Elles s'appliquent **partout où un champ ou une section est posé pour la première fois** : `new`,
`migrate` sur un champ ou une section absents, `derive` sur un champ sans `from`. Une valeur déjà
écrite n'est jamais recalculée.

**Un champ prérempli est une valeur ordinaire** : `validate --filled` ne le réclame pas, et `merge`
la fait sortir. C'est tout l'objet de ces deux clés — ce qui est mécaniquement connu n'a pas à être
relu.

La commande tourne **dans le répertoire de la liste** — ou, si celui-ci n'existe pas encore, dans
son premier ancêtre qui existe. Le cas se produit en `derive`, qui construit toutes ses fiches en
mémoire avant de créer quoi que ce soit : `LISTDIR_LIST` y nomme bien la liste engendrée, mais le
répertoire courant de la commande est ailleurs. Une commande qui lit le disque relativement à son
cwd — `ls | wc -l` — n'y rendra donc pas la même chose qu'à `new`. `LISTDIR_ROOT` est résolue
depuis ce même répertoire.

L'environnement porte :

| Variable | Valeur |
|---|---|
| `LISTDIR_ID` | l'identifiant de l'élément — le nom de son fichier, sans extension |
| `LISTDIR_NAME` | le nom du champ, ou le titre de la section |
| `LISTDIR_LIST` | le chemin du répertoire-liste |
| `LISTDIR_CONTRACT` | le `name` du contrat |
| `LISTDIR_ROOT` | la racine du dépôt git — **absente de l'environnement** hors dépôt |

Le contrat est refusé si `text` et `command` sont déclarés ensemble, si l'un des deux est vide, ou
s'il porte sur un champ de type `list` : la valeur produite est toujours du texte.

**Échec fermé.** Une commande qui sort en code non nul interrompt l'opération, sans qu'aucun fichier
soit écrit, en nommant le champ ou la section et la commande incriminée. Une sortie que le type
déclaré refuse — `date` sur autre chose qu'une date ISO — est refusée de la même façon : à la
création, jamais laissée écrire un front matter que `validate` recalera ensuite.

Trois limites à connaître :

- **`derive` ne préremplit pas les sections d'une fiche** : elles viennent du gabarit `.md`, pas du
  contrat. Seuls les champs sans `from` y passent par `text`/`command`.
- **un essai de migration n'exécute aucune `command`**, ce qui a une contrepartie :
  [Quand le contrat change](../references/operations.md#quand-le-contrat-change).
- **rien n'est mémorisé** : `migrate` rejouée sur un élément dont le champ est déjà écrit ne
  relance pas la commande. C'est la pose initiale qu'on préremplit, pas la valeur qu'on maintient.

---

## Les marqueurs

Un élément créé par `new`, ou une fiche créée par `derive`, porte **tout** le contrat : chaque champ
et chaque section y figure, même facultatif. Ce qu'on ne voit pas n'est jamais rempli.

**Un marqueur dit qu'il faut écrire, jamais quoi écrire.** Aucune `description` du contrat n'est
reportée dans l'élément : `<À REMPLIR>` sous `## Constat` ne rappelle pas que la section veut un
constat factuel sans remède. C'est `list-dir contract <liste>` qui la sert — le contrat réellement
appliqué, à lire avant de remplir.

Deux constantes, définies une seule fois dans `listdir/types.py` :

| Déclaré au contrat | Marqueur posé | `validate --filled` |
|---|---|---|
| champ `required = true` | `<À REMPLIR>` | le réclame |
| champ `required = false` | `<OPTIONNEL>` | l'ignore |
| section `required = true` | `<À REMPLIR>` | la réclame |
| section `required = false` | `<OPTIONNEL>` | l'ignore |

Seul `id` échappe aux deux : il est renseigné à la création, puisqu'il est le nom du fichier. Un
champ ou une section portant `text` ou `command` y échappe aussi — il reçoit sa valeur, pas un
marqueur, et `validate --filled` ne le réclame donc jamais (voir « Préremplir un champ ou une
section »).

Rien d'autre ne marque un vide — ni chaîne vide, ni champ omis, ni tiret. Un champ **absent** et un
champ **à remplir** sont deux états différents.

Sur un champ portant `<À REMPLIR>`, le contrôle de type est suspendu : `date = "<À REMPLIR>"` est
signalé comme *à remplir*, jamais comme *type invalide* — le message doit dire quoi faire.

**`merge` exige `--filled`** et omet de sa sortie les sections restées à `<OPTIONNEL>` : elles ont
joué leur rôle de guide et n'ont rien à dire dans un document final.
