# Le format d'un gabarit

Ce qu'est un gabarit, ce que son contrat déclare, et ce que `check` confronte à quoi. Tout ce qui
suit est mécaniquement vérifiable.

Ce fichier fait autorité sur le **socle** : le format, le contrat, les types, le préremplissage,
les marqueurs. Une liste `list-dir` est une liste de gabarits et le tient d'ici ; ce qu'elle y
ajoute — l'`id` égal au nom du fichier, `from`, `[origin]` — est à elle seule.

---

## Un gabarit

Un fichier Markdown à front matter TOML, délimité par `+++`.

```markdown
+++
gabarit = "suivi"
titre = "Un intitulé"
date = 2026-08-20
refs = ["R4"]
+++

## Objectif

…prose…

## Étapes

…prose…
```

- Le front matter est du **TOML** : dates et listes sont natives, les valeurs texte prennent des
  guillemets. Une erreur de syntaxe est localisée à la ligne.
- Les titres de section sont des `##`.
- `gabarit` est l'**estampille**, posée par `new` et réservée : elle nomme la semence, n'est jamais
  comptée comme un champ non déclaré, et permet à `check` de retrouver le contrat sans qu'on ait à
  le dire. [Semences](semences.md#lestampille).
- **Aucun `id` n'est imposé** : un gabarit n'est pas lié au nom de son fichier. Un suivi archivé
  sous `done/<date>-<slug>.md` reste conforme.

---

## Le contrat

Le `contract.toml` d'une semence. Il déclare ce qu'un gabarit doit contenir.

```toml
name = "revue"
description = "À quoi sert ce gabarit"

[fields.titre]
type = "text"
required = true
description = ""

[fields.date]
type = "date"
required = true
description = "date du constat, jamais modifiée"
command = "date +%F"   # la sortie de cette commande, à la place du marqueur

[fields.category]
type = "enum"
required = false
description = ""
values = ["a-traiter", "doublon", "sans-objet"]

[sections."Constat"]
required = true
description = "ce qui a été observé, factuel, sans remède"

[sections."Assumé"]
required = false
description = ""
text = "Rien d'assumé à ce jour."   # ce texte, à la place du marqueur
```

### Les six types

`slug`, `text`, `date`, `enum` (avec `values`), `list` (de chaînes), `int` (un entier ; un booléen
n'en est pas un). **La liste est fermée** : un contrat n'est pas un langage, et tout autre type est
une erreur qui nomme le type.

**L'autorité est `FieldType`, dans `scripts/gabarit/types.py`** : le code y dérive `FIELD_TYPES` de
l'alias plutôt que d'en tenir une seconde liste, et un type ajouté là est admis sans qu'aucune
énumération suive. Les six noms ci-dessus sont une transcription pour le lecteur, la seule du
dépôt : un type ajouté ou retiré se reporte ici, et nulle part ailleurs. Une transcription qu'on
oublie de suivre annonce un type qui n'existe pas, ou tait celui qui vient d'apparaître.

**Une valeur de `values` est un jeton** : ni vide, ni porteuse d'espace. Le contrat est refusé
sinon, en nommant la valeur fautive. Une valeur à blanc traverserait toute substitution de commande
en se découpant — `contract … --values category` la rend bien sur une ligne, mais un appelant qui
boucle dessus compterait deux catégories fantômes, chacune à zéro, sans qu'aucune commande
n'échoue ; une valeur vide, elle, disparaîtrait sans laisser de trace.

### Les sections

**Une section se déclare en table, une par section**, sur le modèle de `[fields.*]` : le titre est
la clé, `required` dit si elle est obligatoire (défaut `false`), `description` dit ce qu'il faut y
écrire. C'est l'ordre du TOML qui ordonne les sections dans un fichier créé — pas un tri par
`required`.

### `description` est exigée partout

Sur chaque `[fields.*]`, sur chaque `[sections.*]`, et à la racine du contrat. Elle manque : le
contrat est refusé, en nommant l'endroit.

**C'est la clé qui est exigée, pas son texte** : `description = ""` est accepté aux trois endroits.
Un champ ou une section qu'on n'a pas su décrire sur le moment reste donc déclarable — mais il
reste aussi *visible* comme non documenté, ce qui est précisément l'objet de la règle. Sans cette
exigence, une clé absente et une clé vide rendraient toutes deux `""`, et un contrat à moitié
documenté passerait sans un mot. C'est `gabarit contract <nom>` qui sert ces descriptions, celles
des champs comme celles des sections.

---

## Préremplir un champ ou une section

Deux clés facultatives, sur `[fields.*]` comme sur `[sections.*]` :

| Clé | Ce qu'elle pose à la place du marqueur |
|---|---|
| `text` | le texte, **littéral** — aucune substitution, ni `{{id}}` ni `$VAR` |
| `command` | la sortie standard d'une commande Bash, débarrassée de ses blancs de bord |

**Un champ prérempli est une valeur ordinaire** : `check --filled` ne le réclame pas. C'est tout
l'objet de ces deux clés — ce qui est mécaniquement connu n'a pas à être relu.

Le contrat est refusé si `text` et `command` sont déclarés **ensemble**, si l'un des deux est
**vide**, ou s'il porte sur un champ de type **`list`** : la valeur produite est toujours du texte.
Sur un champ de type `int`, ce texte est converti en entier à la pose — `text = "1"` pose `1` — et
refusé en le nommant s'il n'est pas un entier en base 10. Une date préremplie est posée en date
nue, comme une date saisie : deux graphies valides du même champ ne cohabitent pas selon l'origine
de la valeur.

**Échec fermé.** Une commande qui sort en code non nul interrompt l'opération, **sans qu'aucun
fichier soit écrit**, en nommant le champ ou la section et la commande incriminée. Une sortie que
le type déclaré refuse — `date` sur autre chose qu'une date ISO — est refusée de la même façon : à
la création, jamais laissée écrire un front matter que `check` recalerait ensuite.

Où tourne la commande et ce qu'elle reçoit dans son environnement :
[L'environnement du préremplissage](semences.md#lenvironnement-du-préremplissage).

---

## Les marqueurs

Un fichier créé par `new` porte **tout** le contrat : chaque champ et chaque section y figure, même
facultatif. Ce qu'on ne voit pas n'est jamais rempli.

**Un marqueur dit qu'il faut écrire, jamais quoi écrire.** Aucune `description` du contrat n'est
reportée dans le fichier : `<À REMPLIR>` sous `## Constat` ne rappelle pas que la section veut un
constat factuel sans remède. C'est `gabarit contract <nom>` qui la sert — à lire avant de remplir.

Deux constantes, définies une seule fois dans `scripts/gabarit/types.py` :

| Déclaré au contrat | Marqueur posé | `check --filled` |
|---|---|---|
| champ `required = true` | `<À REMPLIR>` | le réclame |
| champ `required = false` | `<OPTIONNEL>` | l'ignore |
| section `required = true` | `<À REMPLIR>` | la réclame |
| section `required = false` | `<OPTIONNEL>` | l'ignore |

Un champ ou une section portant `text` ou `command` y échappe : il reçoit sa valeur, pas un
marqueur, et `check --filled` ne le réclame donc jamais.

Rien d'autre ne marque un vide — ni chaîne vide, ni champ omis, ni tiret. Un champ **absent** et un
champ **à remplir** sont deux états différents.

Sur un champ portant `<À REMPLIR>`, le contrôle de type est **suspendu** : `date = "<À REMPLIR>"`
est signalé comme *à remplir*, jamais comme *type invalide* — le message doit dire quoi faire.

---

## Les deux verdicts

`check` confronte un fichier au contrat de sa semence, et rend l'un des deux :

- **sans `--filled`** — la structure seule : les champs et les sections déclarés sont présents, les
  types tiennent, et les marqueurs sont légitimes ;
- **avec `--filled`** — plus aucun `<À REMPLIR>` là où le contrat exige quelque chose. Les
  facultatifs restés `<OPTIONNEL>` ne sont jamais réclamés.

Un champ ou une section que le contrat ne déclare pas est signalé ; l'estampille `gabarit` ne l'est
jamais.
