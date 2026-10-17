# Le format d'un gabarit

Ce qu'est un gabarit, ce que son contrat déclare, et ce que `check` confronte à quoi. Tout ce qui
suit est mécaniquement vérifiable.

Ce fichier fait autorité sur le **socle** : le format, le contrat, les types, les sections
structurées, le préremplissage, les marqueurs. Une liste `list-dir` est une liste de gabarits et le
tient d'ici ; ce qu'elle y ajoute — l'`id` égal au nom du fichier, `from`, `[origin]` — est à elle
seule.

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

### Les sept types

`slug`, `text`, `date`, `enum` (avec `values`), `list` (de chaînes), `int` (un entier ; un booléen
n'en est pas un), `bool` (`true` ou `false`, sans guillemets ; l'entier `0` ou `1` n'en est pas un).
**La liste est fermée** : un contrat n'est pas un langage, et tout autre type est
une erreur qui nomme le type.

**L'autorité est `FieldType`, dans `scripts/gabarit/types.py`** : le code y dérive `FIELD_TYPES` de
l'alias plutôt que d'en tenir une seconde liste, et un type ajouté là est admis sans qu'aucune
énumération suive. Une capture de motif n'en prend que cinq :
[Une section à motif](#une-section-à-motif). Les sept noms ci-dessus sont une transcription pour le
lecteur, la seule du dépôt : un type ajouté ou retiré se reporte ici, et nulle part ailleurs. Une
transcription qu'on oublie de suivre annonce un type qui n'existe pas, ou tait celui qui vient
d'apparaître.

**Une valeur de `values` est un jeton** : ni vide, ni porteuse d'espace. Le contrat est refusé
sinon, en nommant la valeur fautive. Une valeur à blanc traverserait toute substitution de commande
en se découpant — `contract … --values category` la rend bien sur une ligne, mais un appelant qui
boucle dessus compterait deux catégories fantômes, chacune à zéro, sans qu'aucune commande
n'échoue ; une valeur vide, elle, disparaîtrait sans laisser de trace.

### Les sections

**Une section se déclare en table, une par section**, sur le modèle de `[fields.*]` : le titre est
la clé, `required` dit si elle est obligatoire (défaut `false`), `description` dit ce qu'il faut y
écrire. C'est l'ordre du TOML qui ordonne les sections dans un fichier créé — pas un tri par
`required`. `type` déclare la structure de son contenu :
[Les sections structurées](#les-sections-structurées).

### `deprecated` retire un champ ou une section sans le supprimer

`deprecated = "<consigne>"` marque un champ ou une section qu'on ne pose plus, et dit à qui le porte
encore ce qu'il en fait. La consigne est une chaîne non vide.

- Un fichier neuf ne le porte pas : ni `new`, ni `derive`, ni `migrate` ne le posent, et `migrate`
  ne le retire pas d'un fichier qui le porte (`--drop` non plus : il est déclaré).
- `check` ne le réclame jamais, ne le signale jamais comme non déclaré, et contrôle encore le type
  d'un champ déprécié qu'un fichier porte.
- Tant qu'un fichier le porte, `check` avertit sur stderr, avec la consigne, sans changer son code
  de retour : `<fichier>: champ « source » — déprécié : <consigne>`. Une absence ne dit rien.

Le contrat est refusé si `deprecated` est vide, ou s'il est déclaré avec `required = true`, `text`
ou `command` : ce qu'on ne pose plus ne se préremplit pas et ne se réclame pas. Le message nomme la
contradiction ; le contrat n'est pas corrigé en silence.

### `description` est exigée partout

Sur chaque `[fields.*]`, sur chaque `[sections.*]` et chacun de ses labels, et à la racine du
contrat. Elle manque : le contrat est refusé, en nommant l'endroit. Une capture de motif en est
dispensée : sans description, elle prend celle de sa section ou de son label, qui la dit déjà —
[Une section à motif](#une-section-à-motif).

**C'est la clé qui est exigée, pas son texte** : `description = ""` est accepté partout où elle est
exigée. Un champ ou une section qu'on n'a pas su décrire sur le moment reste donc déclarable — mais
il reste aussi *visible* comme non documenté, ce qui est précisément l'objet de la règle. Sans cette
exigence, une clé absente et une clé vide rendraient toutes deux `""`, et un contrat à moitié
documenté passerait sans un mot. C'est `gabarit contract <nom>` qui sert ces descriptions, celles
des champs comme celles des sections.

---

## Les sections structurées

Une section sans `type` est de la prose libre : `check` n'en juge que la présence. `type = "motif"`
ou `type = "label"` déclare sa structure, et `check` en juge chaque puce ou chaque label. Une
structure décrite seulement dans la `description` ne se vérifie pas : une ligne mal formée passe
`check`, et n'échoue que chez le consommateur qui la lit — ou jamais, s'il l'ignore.

### Une section à motif

```toml
[sections."Étapes"]
required = true
description = "les étapes, dans l'ordre"
type = "motif"
motif = "[{etat: enum}] {n: int}. {intitule} — vérif: {verif}"

[sections."Étapes".captures.etat]
description = "x fait, > en cours, ! bloqué, une espace : à faire"
values = ["x", ">", "!", " "]

[sections."Étapes".captures.n]
description = "le numéro de l'étape"
min = 1
sequence = true

[sections."Étapes".captures.verif]
description = "la commande qui la vérifie"
required = false
```

```markdown
## Étapes

- [x] 1. Déclarer le motif — vérif: `pytest; echo $?` ;;
- [ ] 2. Une étape dont l'intitulé
  court sur deux lignes — vérif: ;;
```

**Le motif est un gabarit de ligne, pas une regex** : des littéraux, et des captures `{nom}` ou
`{nom: type}`, de type `text` quand il est omis. Une regex écrite à la main ferait du contrat un
langage, avec une seconde syntaxe. Le contrat est refusé, en nommant section et capture, sur une
accolade non appariée, un nom qui n'est pas un identifiant, deux captures de même nom, ou deux
captures sans littéral entre elles : rien ne dirait où finit la première.

**Une capture prend l'un de cinq types** : `slug`, `text`, `date`, `enum`, `int`. `bool` et `list`
sont refusés ; `list` exigerait un séparateur à déclarer. Une capture se précise par
`[sections.X.captures.<nom>]`, qui doit nommer une capture du motif. Sans table, comme `intitule`
ci-dessus, elle est requise, sans contrainte, et prend la description de sa section ou de son
label : une capture simple n'alourdit pas le contrat. Une `enum` déclare toujours sa table, pour ses
`values`.

| Clé | Ce qu'elle dit |
|---|---|
| `description` | ce qu'il faut écrire ; absente ou blanche, celle de la section ou du label |
| `required` | vrai par défaut ; faux, la capture peut rester vide |
| `values` | les valeurs d'une `enum`, obligatoires ; l'espace y est admise, la vide non |
| `min`, `max` | les bornes d'un `int` |
| `sequence` | sur un `int` : la puce *i*, comptée depuis 0, vaut `min + i`, ou `1 + i` sans `min` |

Le type d'une capture ne se déclare que dans le motif : `type`, `text`, `command` ou toute autre clé
refuse le contrat, comme `values` hors d'une `enum` et `min`, `max` ou `sequence` hors d'un `int`.
**L'espace n'est admise que dans les `values` d'une capture**, pour que `[ ]` puisse valoir `" "` ;
celles d'un champ restent des jetons.

**Une puce va de `debut` à `fin`**, « - » et « ;; » par défaut, que la section déclare autrement par
`debut` et `fin` — deux jetons, ni vides ni blancs, hors la `fin` de ligne ci-dessous. Elle s'ouvre
sur une ligne qui commence, blancs ignorés, par `debut` suivi d'un blanc, et peut courir sur
plusieurs lignes. Elle se clôt sur une ligne terminée par `fin` et suivie d'une ligne vide, d'une
autre puce ou de la fin de la section ; suivie d'une ligne de texte, la puce continue, et ce
`fin`-là est intérieur. Un « ; » ne ferme rien : il paraît dans les commandes de vérification.

**`fin = "\n"` finit la puce à la ligne**, comme dans une liste Markdown : sa suite s'écrit en
retrait, la forme que `rumdl` donne à une puce qu'il réenroule. Une ligne vide, une autre puce ou
un texte à la marge la closent, et aucune `fin` ne peut manquer ; une puce en retrait est
imbriquée. Le marqueur d'une telle section ne porte pas de `fin`.

`check` nomme section, puce et capture —
`section « Étapes », puce 2, capture « n » — 3 rompt la séquence — 2 attendu à cette puce` — pour :

- une puce dont la `fin` manque avant la suivante, ce qui couvre une puce imbriquée, ou une dernière
  puce sans `fin` ; avec `fin = "\n"`, une puce en retrait, imbriquée ;
- un texte hors puce : une section à motif ne porte que des puces ;
- une puce que le motif ne couvre pas ;
- une capture que `check_value` refuse — le type d'une capture se juge à l'endroit où se juge celui
  d'un champ —, hors de `min`-`max`, ou qui rompt sa `sequence`.

Une puce fautive n'est pas jugée plus loin, mais elle compte dans la `sequence` : elle ne décale pas
les suivantes.

**Les blancs se réduisent à une espace**, dans la puce comme dans le motif, et chaque capture est
rognée — une `enum` se compare d'abord brute, ce qui laisse `[ ]` valoir `" "`. L'espace qui borde
une capture facultative est facultative elle aussi : `— vérif: {verif}` laissé vide finit sur
« vérif: ».

### Une section à labels

```toml
[sections."État courant"]
required = true
description = "où en est le chantier"
type = "label"
forme = "bold"

[sections."État courant".labels."Prochaine action"]
required = true
description = "la prochaine chose à faire"
order = 1

[sections."État courant".labels."Vérification"]
description = "la commande qui vérifie l'ensemble"
order = 2
```

```markdown
## État courant

**Prochaine action** : Étape 3.

**Vérification** :
`pytest`
```

**Un label se déclare comme une section** — `description`, `required`, `text`, `command`,
`deprecated`, et `type` : un label peut porter un motif. Il y gagne `order`, un entier : les labels
qui en portent se suivent dans cet ordre, ceux qui n'en portent pas prennent n'importe quelle place.
Le contrat déclare ses labels dans leur ordre, et refuse un `order` qui ne croît pas : le squelette
posé dans l'ordre de déclaration passe ainsi `check`.

**`forme` dit comment s'écrivent tous les labels de la table** — jamais deux formes à un même
niveau :

- `bold` : `**Nom** :` ou `**Nom**:` en début de ligne, le corps sur la même ligne ou les suivantes.
  Un label `bold` ne porte pas de labels.
- `title` : un titre d'un rang de plus que la table — `###` sous la section, `####` sous un label
  `title`, jusqu'au rang 6. Un label `title` peut déclarer `type = "label"` et ses propres labels.

Un label court jusqu'au label suivant de même niveau, ou jusqu'à la fin de son parent. Une étiquette
dans un bloc de code n'en est pas une. La prose avant le premier label n'est admise que si la table
déclare `prefix`, dont la valeur dit ce que cette prose contient. Elle prend le `required` de sa
table : une table requise la réclame, et la dit manquante sans elle ; une table facultative ne la
réclame jamais.

Le contrat est refusé, en nommant le chemin jusqu'au label, sur une `forme` absente ou inconnue,
une table sans label, des labels sous un `bold`, un rang au-delà de 6, un `order` qui n'est pas un
entier ou ne croît pas. `forme`, `labels` et `prefix` sont refusés hors d'une table
`type = "label"` : un label qui déclarerait sa forme sans porter de labels en imposerait une seconde
à ses voisins. `order` hors d'un label, et `motif`, `debut`, `fin` ou `captures` hors d'une section
à motif, refusent aussi le contrat.

`check` nomme, en `bold` comme en `title` et à chaque niveau :

- un label `required` absent, vide, ou resté à son marqueur avec `--filled` ;
- un label qui suit une ligne non vide : deux labels se séparent d'une ligne vide ;
- un `order` violé, un label en double ;
- la prose avant le premier label, sans `prefix` ; avec, sa prose absente ou restée à son marqueur
  avec `--filled`, quand la table est requise ;
- les fautes du motif d'un label.

**Une table facultative laissée au squelette n'est pas jugée** : tant que sa prose et chacun de
ses labels sont à leur marqueur, `--filled` n'y réclame rien, pas même un label requis. Un label
prérempli par `text` ou `command` ne l'entame pas ; une prose écrite, un label rempli ou vidé, une
étiquette non déclarée, si. Sans cette règle, un fichier qu'on vient de poser échouerait à
`--filled`, et l'on n'en sortirait qu'en supprimant la section. Entamée, la table réclame ses
labels requis ; une table requise les réclame dès le squelette.

Une étiquette que le contrat ne déclare pas n'est pas une faute, mais le signe d'un contrat
incomplet : `check` la note sur stderr, comme un label `deprecated` encore présent, sans changer son
code de retour.

### La pose et la lecture

`new` pose une section à motif au marqueur qui porte son motif et ses bornes —
`<À REMPLIR motif: - [{etat: enum}] {n: int}. {intitule};;>` —, `fin` collée au motif : un motif
qui veut une espace avant elle la porte à sa fin, `"{intitule} "`. Il pose une section à labels en
squelette : le marqueur de son `prefix`, du statut de la table, puis ses labels non dépréciés, dans
l'ordre de déclaration, séparés d'une ligne vide, chacun à son `text`, à sa `command` ou à son
marqueur. Sous un label `bold`, un motif se pose à la ligne, son marqueur comme ses puces : une
puce s'ouvre en début de ligne. Un `text` ou une `command` sur la section l'emporte sur le
squelette. Le marqueur d'un motif se reconnaît blancs réduits : rumdl peut le réenrouler sur deux
lignes.

`section_values(contrat, item, titre)`, du module `structure`, rend ce que porte une section. Pour
un motif, une liste d'une entrée par puce : les captures par nom, un `int` converti, `None` pour une
facultative vide. Pour des labels, un dict d'un label par clé : le corps rogné, la liste d'un label
à motif, le dict d'un label à labels. Une section au marqueur rend une liste ou un dict vides ; un
label en prose resté au marqueur, absent ou non déclaré n'a pas de clé. Une section mal formée,
sans `type`, absente ou non déclarée rend un échec qui nomme chaque faute : un consommateur ne lit
jamais ce que `check` refuserait.

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
refusé en le nommant s'il n'est pas un entier en base 10. Sur un champ `bool`, `text = "false"`
pose le booléen `false`, pas la chaîne ; seuls `true` et `false` sont admis, tout autre texte est
refusé en le nommant. Une date préremplie est posée en date
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

Deux constantes, définies une seule fois dans `scripts/gabarit/types.py`, et la fonction `marker`
qui en tire la forme typée :

| Déclaré au contrat | Marqueur posé | `check --filled` |
|---|---|---|
| champ `required = true` | `<À REMPLIR>`, ou `<À REMPLIR int>` | le réclame |
| champ `required = false` | `<OPTIONNEL>`, ou `<OPTIONNEL date>` | l'ignore |
| section `required = true` | `<À REMPLIR>` | la réclame |
| section `required = false` | `<OPTIONNEL>` | l'ignore |
| section à motif | `<À REMPLIR motif: - …;;>`, ou `<OPTIONNEL motif: - …;;>` ; sans `fin` si elle vaut `"\n"` | selon `required` |
| section à labels | son squelette : le `prefix` au marqueur de sa table, chaque label au sien | chaque label requis resté au marqueur, le `prefix` d'une table requise — rien d'une table facultative laissée au squelette |

**Le marqueur d'un champ `int`, `date`, `bool` ou `list` dit son type** : `<OPTIONNEL date>`.
`text`, `enum`, `slug` et les sections en prose portent le marqueur générique. Le marqueur d'une
section à motif porte son motif ; le générique y reste accepté :
[La pose et la lecture](#la-pose-et-la-lecture).

**La règle des guillemets** : seuls les champs `slug`, `text` et `enum` gardent leurs guillemets.
Un champ `int`, `date`, `bool` ou `list` s'écrit sans guillemets, et le marqueur qui le tient se
remplace guillemets compris — `reviewed = "<OPTIONNEL date>"` devient `reviewed = 2026-10-07`, pas
`reviewed = "2026-10-07"`. Le marqueur typé le rappelle, là où le marqueur générique laissait
écrire une chaîne. `gabarit contract` rappelle la règle sur stderr.

**Le marqueur d'un autre type est un manquement** : `<OPTIONNEL int>` sur un champ `date` ne dit
pas quoi écrire. Le marqueur générique sur un champ typé reste accepté ; `check` avertit sur
stderr, sans changer son code de retour, et nomme la forme typée qui le remplace. Sur une liste,
`list-dir migrate` fait la conversion.

Un champ ou une section portant `text` ou `command` y échappe : il reçoit sa valeur, pas un
marqueur, et `check --filled` ne le réclame donc jamais.

Rien d'autre ne marque un vide — ni chaîne vide, ni champ omis, ni tiret. Un champ **absent** et un
champ **à remplir** sont deux états différents.

Sur un champ portant un marqueur de son type, ou le marqueur générique, le contrôle de type est
**suspendu** : `date = "<À REMPLIR date>"` est signalé comme *à remplir*, jamais comme *type
invalide* — le message doit dire quoi faire.

---

## Les deux verdicts

`check` confronte un fichier au contrat de sa semence, et rend l'un des deux :

- **sans `--filled`** — la structure seule : les champs et les sections déclarés sont présents, les
  types tiennent, chaque section structurée suit son motif ou ses labels, et les marqueurs sont
  légitimes ;
- **avec `--filled`** — plus aucun `<À REMPLIR>`, typé ou non, là où le contrat exige quelque
  chose. Les facultatifs restés `<OPTIONNEL>` ne sont jamais réclamés.

Un champ ou une section que le contrat ne déclare pas est signalé ; l'estampille `gabarit` ne l'est
jamais.

**Les avertissements ne sont pas des manquements.** Un ancien marqueur générique sur un champ typé,
un champ, une section ou un label `deprecated` encore portés, et une étiquette de label que le
contrat ne déclare pas sortent sur stderr, avec la consigne s'il y en a une ; le code de retour ne
change pas.
