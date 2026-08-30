# Contrat d'un répertoire-liste

Ce que `list-dir` garantit, et ce qu'un consommateur peut supposer. Tout ce qui suit est
mécaniquement vérifiable par `validate`.

---

## Structure d'un répertoire-liste

```
ma-liste/
├── .list/
│   ├── contract.toml          contrat : champs, sections, description
│   ├── commands/              commandes propres à cette liste
│   │   └── close.py
│   └── templates/             gabarits pour `derive`
│       ├── review.toml
│       └── review.md
├── premier-element.md
└── second-element.md
```

**Tout `*.md` à la racine d'une liste est un élément, sans exception.** Tout le reste vit sous
`.list/`.

> *Mode de défaillance* — un `README.md` posé à la racine se ferait compter comme un élément, et le
> contrôle de conservation d'une agglomération rendrait un nombre faux sans broncher.

Une liste **sans aucun élément est valide** pour `init` et `validate` : une liste fraîchement créée
est légitimement vide. Elle est en revanche une **erreur** pour `merge` et `derive` — agglomérer ou
projeter zéro élément se lirait comme « rien à traiter ».

---

## Définitions de listes

`init` seul rend un squelette : un `id`, un `title`, une section. C'est assez pour commencer une
liste à la main, et pas assez pour recréer une liste dont le contrat est connu. Une **définition**
comble ce trou.

Une définition est un répertoire dont le contenu **est** le futur `.list/` :

```
list-dir/
└── recettes/            le nom de la définition
    ├── contract.toml          obligatoire — sans lui, ce n'est pas une définition
    └── templates/             facultatif, copié tel quel s'il existe
        ├── review.toml
        └── review.md
```

```bash
list-dir defs                                # ce qui est définissable, et d'où
list-dir init <cible> --def recettes   # résolu par son nom, dans les racines
list-dir init <cible> --from <chemin>        # ou pris à un chemin, tel quel
```

**Pourquoi une définition peut ce qu'un gabarit ne pouvait pas** : un gabarit vit dans le
`.list/templates/` d'une liste *existante*, et `init` s'adresse justement au cas où aucune liste
n'existe. Une définition vit hors de tout répertoire-liste — c'est exactement ce qui la rend
disponible quand il n'y a encore rien.

### Les quatre racines

Un nom est cherché dans quatre racines, du plus spécifique au plus général :

| # | Racine | Ancrage |
|---|---|---|
| 1 | `<projet>/.claude/list-dir/<nom>/` | le premier répertoire **contenant** un `.claude`, en remontant depuis le répertoire courant |
| 2 | `<projet>/.claude/skills/*/list-dir/<nom>/` | idem |
| 3 | `<config>/list-dir/<nom>/` | le premier répertoire **nommé** `.claude`, en remontant depuis le paquet |
| 4 | `<config>/skills/*/list-dir/<nom>/` | idem |

**Les deux ancrages ne cherchent pas la même chose**, et les confondre casse le cas où une
configuration porte son propre projet : un projet *contient* un `.claude`, une configuration *est*
un `.claude`. Une règle unique ferait viser le même répertoire aux deux, et l'un des deux couples
de racines serait faux.

Aucune constante de chemin, aucune variable d'environnement : les deux ancrages sont des remontées.
`defs` imprime celui qu'il a retenu — la remontée s'arrête au **premier** `.claude` trouvé, qui
n'est pas toujours celui qu'on avait en tête, et le voir vaut mieux que le deviner.

**N'avoir aucune racine est un état légitime**, pas une erreur : hors de tout `.claude`, `defs` ne
liste rien et `--def` échoue en le disant.

### Qui gagne

**La spécificité prime, et masquer est le comportement voulu** : une définition de rang 1 l'emporte
sur son homonyme de rang 4, exactement comme une commande de `.list/commands/` l'emporte sur une
générique. C'est ainsi qu'un projet reprend la main sur une définition de sa configuration. `defs`
montre la masquée plutôt que de la taire.

**L'ambiguïté ne se déclare qu'à rang égal** : deux skills qui définissent le même nom font sortir
la commande non nulle, en les nommant tous les deux.

> *Mode de défaillance* — choisir en silence ferait dépendre le contrat d'une liste de l'ordre de
> parcours d'un répertoire. Deux machines rendraient deux contrats, et rien ne dirait pourquoi.

Un répertoire sans `contract.toml` n'est pas une définition à moitié faite : ce n'en est pas une, et
`defs` ne le propose pas. L'annoncer pour échouer ensuite sur un fichier manquant serait pire que
de l'ignorer.

### La définition n'est autorité que le temps de l'`init`

C'est la règle dont tout le reste découle. Une liste amorcée porte **sa propre copie** du contrat,
et `contract_path` la lit toujours depuis `<liste>/.list/contract.toml` — jamais depuis une
définition. `list-dir contract <liste>` imprime cette copie, c'est-à-dire la règle réellement
appliquée.

**Rien ne resynchronise une liste avec sa définition.** La définition peut évoluer, `migrate` ne
la rattrapera pas : il remet les éléments au contrat *de la liste*. Il n'existe pas de re-semis, et
c'est voulu — un projet qui redéfinit sa liste au rang 1 a délibérément pris la main.

> *Mode de défaillance* — une documentation qui renverrait au **fichier** d'une définition
> décrirait autre chose que ce que l'outil applique, et d'autant plus faux que le projet a
> justement redéfini sa liste. Un renvoi vers `list-dir contract` ne peut pas mentir : il rend ce
> que la commande rendrait.

### Ce que `contract` vise, et ce que ça engage

`contract` accepte les deux cibles d'`init`, et la différence n'est pas cosmétique :

| Forme | Ce qui est imprimé | Ce que ça vaut |
|---|---|---|
| `contract <liste>` | `<liste>/.list/contract.toml` | la règle **réellement appliquée** |
| `contract --def <nom>` | `<définition>/contract.toml` | une **semence**, appliquée à rien |
| `contract --from <chemin>` | idem, sans passer par les rangs | idem |

`--template <nom>` vise le `<nom>.toml` de `templates/` au lieu du contrat, dans les trois cas.

**Une prose doit dire laquelle des deux elle décrit.** Renvoyer à une définition alors qu'une
liste existe et a divergé décrit ce qui *aurait été* semé, pas ce qui s'applique — c'est le mode de
défaillance ci-dessus, déplacé d'un cran. Le renvoi à une définition se justifie quand la liste
**n'existe pas encore** au moment de la lecture : une liste engendrée par `derive` n'a de contrat
qu'après coup, et son gabarit source est le seul fichier déjà là.

`--values <champ>` rend les valeurs déclarées d'un champ, une par ligne et **dans l'ordre du
fichier**. Il extrait : rien n'est trié, filtré ni jugé. Un champ inconnu ou sans `values` est un
échec nommé, jamais une sortie vide sous un code 0.

**Le code de retour est à l'appelant, et il n'est pas facultatif.** `for c in $(list-dir contract …
--values category)` avale l'échec : la substitution rend une chaîne vide, la boucle itère zéro fois
et le bloc réussit. Affecter, tester, puis lire ligne à ligne :

```bash
if ! VALEURS=$(list-dir contract "$L" --values category); then
  echo "ÉCHEC : contrat illisible"; false
else
  printf '%s\n' "$VALEURS" | while read -r v; do …; done
fi
```

Le `while read` plutôt qu'un `for` sur la variable : zsh ne découpe pas une variable en mots, et la
boucle y tournerait une seule fois sur la chaîne entière.

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

[fields.category]
type = "enum"
required = false
values = ["a-traiter", "doublon", "sans-objet"]

[sections]
required = ["Constat", "Pour solder"]
optional = ["Assumé"]
```

Types admis : `slug`, `text`, `date`, `enum` (avec `values`), `list` (de chaînes). Tout autre type
est une erreur nommant le type.

**Une valeur de `values` est un jeton** : ni vide, ni porteuse d'espace. Le contrat est refusé
sinon, en nommant la valeur fautive.

> *Mode de défaillance* — une valeur à blanc traverse toute substitution de commande en se
> découpant : `list-dir contract … --values <champ>` la rend sur une ligne, mais un appelant qui
> boucle dessus compte deux catégories fantômes, chacune à zéro, sans qu'aucune commande n'échoue.
> Une valeur vide, elle, disparaît sans laisser de trace.

**L'état d'un élément est porté par son répertoire, jamais par un champ.** Une liste d'éléments
soldés est une liste sœur avec son propre contrat, pas un champ `soldé = true`.

> *Mode de défaillance* — un état porté par un champ se change par une écriture ; porté par le
> répertoire, il se change par un renommage, que l'historique conserve.

---

## Les marqueurs

Un élément créé par `new`, ou une fiche créée par `derive`, porte **tout** le contrat : chaque champ
et chaque section y figure, même facultatif. Ce qu'on ne voit pas n'est jamais rempli.

Deux constantes, définies une seule fois dans `listdir/types.py` :

| Déclaré au contrat | Marqueur posé | `validate --filled` |
|---|---|---|
| champ `required = true` | `<À REMPLIR>` | le réclame |
| champ `required = false` | `<OPTIONNEL>` | l'ignore |
| section de `required` | `<À REMPLIR>` | la réclame |
| section de `optional` | `<OPTIONNEL>` | l'ignore |

Seul `id` échappe aux deux : il est renseigné à la création, puisqu'il est le nom du fichier.

Rien d'autre ne marque un vide — ni chaîne vide, ni champ omis, ni tiret. Un champ **absent** et un
champ **à remplir** sont deux états différents.

Sur un champ portant `<À REMPLIR>`, le contrôle de type est suspendu : `date = "<À REMPLIR>"` est
signalé comme *à remplir*, jamais comme *type invalide* — le message doit dire quoi faire.

**`merge` exige `--filled`** et omet de sa sortie les sections restées à `<OPTIONNEL>` : elles ont
joué leur rôle de guide et n'ont rien à dire dans un document final.

---

## L'API Python

La CLI n'est qu'une façade. Un script tiers a les mêmes moyens, sans `subprocess` ni sortie à
reparser.

```python
import shutil, sys
from pathlib import Path

# La commande est un lien de `bin/` vers `scripts/list-dir.py` : le résoudre donne le
# répertoire à insérer, sans constante et où que le dépôt soit installé.
cmd = shutil.which("list-dir")
if cmd is None:
    raise SystemExit("list-dir introuvable dans le PATH — ajouter bin/ au profil du shell")
sys.path.insert(0, str(Path(cmd).resolve().parent))
from listdir import open_list, PLACEHOLDER, OPTIONAL
```

Toute opération rend un `Result[T]` : `status` (0 = succès), `value`, `message`. `bool(result)` dit
le succès ; `result.unwrap()` rend la valeur ou lève en portant le message.

```python
lst = open_list("chemin/vers/ma-liste").unwrap()

lst.contract                        # Contract
lst.items()                         # Result[list[Item]]
lst.get("premier-element")          # Result[Item]
lst.where(category="doublon")       # Result[list[Item]] — champs déclarés seulement
lst.create(id, **champs)            # Result[Item]
lst.write(item)                     # Result[Path]
lst.validate(filled=False)          # Result[list[Violation]] — vide = conforme
lst.move(id, cible)                 # Result[Path] — git mv seul
lst.derive(dst, template)           # Result[ListStore]
lst.merge(out)                      # Result[Path]
```

`where` et `create` n'acceptent en valeur qu'un **`FieldValue`** — `str`, `bool`, `int`,
`date` ou `list[str]`, c'est-à-dire exactement ce que le sérialiseur du front matter sait
réécrire. Refuser à l'entrée ce qu'on ne saurait pas rendre à la sortie évite un élément
qu'on crée mais qu'on ne peut plus enregistrer. Les valeurs **lues** sur le disque, elles,
restent quelconques : un fichier édité à la main peut contenir n'importe quoi, et c'est
`validate` qui le dit.

**Ce que `validate` confronte au contrat**, dans l'ordre où les manquements sont rendus — un
`Violation` par manquement, chacun nommant fichier, sujet et cause :

| Sujet | Sans `--filled` | Avec `--filled` |
|---|---|---|
| champ non déclaré au contrat | manquement | idem |
| champ requis absent | manquement | idem |
| `id` ≠ nom du fichier | manquement | idem |
| valeur mal typée, hors enum, date non ISO | manquement | idem |
| champ portant un marqueur | légitime — le type n'est pas contrôlé | manquement si le champ est **requis** |
| section non déclarée au contrat | manquement | idem |
| section requise absente ou vide | manquement | idem |
| section requise au marqueur | légitime | manquement |
| champ ou section **facultatif** au marqueur | légitime | légitime — jamais réclamé |

Une liste **sans élément est conforme** : elle est légitimement vide au sortir d'`init`.

**`help` est le seul point d'où l'interface complète se découvre** : les génériques, et celles que
la liste visée ajoute ou substitue. Sans liste en argument, seules les génériques sont visibles —
c'est exact, pas un oubli. Une commande de liste qui masque une générique porte la mention
**`(surchargée)`** : une surcharge invisible serait un piège.

Rien n'est exécuté pour afficher cette page. Les descriptions sont lues par `ast.parse`, jamais par
import — un module déposé dans une liste ne peut donc pas s'exécuter du seul fait qu'on demande
l'aide, ni la faire échouer parce qu'il est cassé. Un module illisible est signalé **INUTILISABLE**
à sa place, et les autres restent listés.

> *Mode de défaillance* — un module qui écrit sur stderr à l'import prouve la règle : mesuré, son
> effet ne se produit pas alors que sa description s'affiche.

**`derive` projette, il ne copie pas.** Chaque élément source engendre une fiche de même `id`, mais
son corps vient du gabarit `<nom>.md`, jamais de la source — une fiche qui porterait la prose de
l'élément qu'elle instruit en serait un doublon éditable. Le seul emprunt est déclaratif : un champ
du contrat cible portant `from = "champ"` reçoit la valeur du champ nommé dans la source ; sans
`from`, il reçoit le marqueur de son propre statut. L'`id` est reporté d'office. `derive` ne
transforme, ne concatène et ne calcule rien.

Tout est construit **en mémoire avant la moindre écriture** : un gabarit incohérent ne laisse
aucune destination à moitié bâtie, qu'une seconde tentative refuserait comme « existe déjà ».

**`merge` recompte sur le document rendu**, pas sur la liste qui a servi à l'écrire — compter deux
fois la même variable ne prouverait rien. Le compte est fait **hors blocs de code**, par la même
règle que le découpage en sections : un `## ` collé dans une sortie de commande est du contenu.

> Un `grep -c '^## '` lancé à la main sur l'aggloméré ne donne donc **pas** le compte des éléments
> dès qu'une section porte un bloc de code — il compte aussi les `## ` qui s'y trouvent. Le compte
> qui fait foi est celui du **préambule**, écrit par `merge` après vérification.

> *Mode de défaillance* — un `title` contenant une ligne « ## … » ajouterait un faux élément au
> document. Mesuré : le recomptage le refuse, en nommant l'écart.

**`move` est un renommage pur** — `git mv`, et rien d'autre. Git ne stocke pas les renommages :
il les *déduit* de la similarité des contenus. Réécrire le fichier dans le même commit fait tomber
cette déduction sous son seuil, et l'historique montre alors une suppression suivie d'une création
— `git log --follow` s'arrête là. Ce qui accompagne un déplacement va donc dans un **second
commit**. Ce que le contrat d'arrivée exige en plus est rappelé **sur stderr** ; stdout ne porte
que le chemin d'arrivée, pour qu'un script puisse le lire sans le démêler d'un commentaire.

> *Mode de défaillance* — un commit qui mêle déplacement et réécriture perd la trace de l'élément.
> Mesuré : `git log --follow` sur le fichier d'arrivée ne remonte alors qu'au commit mêlé.

**Le format de sortie de `list`** est une ligne par élément : l'id, puis les champs nommés à
`--sort`, séparés par une espace. Il se lit dans un `while read`, se compte au `wc -l`, se coupe
au `cut`. `--where` est répétable et les critères se cumulent ; il porte sur les champs déclarés,
jamais sur le texte. Un filtre qui ne rend rien produit **zéro octet et le code 0** : c'est une
réponse, pas une erreur — contrairement à `merge`, qui perdrait un élément.

L'élément, **immuable** :

```python
item.id, item.path
item.fields             # Mapping, en lecture
item.sections           # Mapping ordonné, en lecture
item.render()           # str — le fichier tel qu'il sera écrit

item.with_fields(**kw)  # copie modifiée
item.with_sections(**kw)
```

**Pourquoi immuable** : un élément lu conserve le texte brut de son front matter, et `render()` le
reconduit tel quel — c'est ce qui garantit qu'un aller-retour lecture/écriture ne change pas un
octet. Muter les valeurs en place les ferait diverger du texte conservé, sans que rien ne le
signale. `with_fields` rend une copie dont le texte brut est marqué périmé : c'est ce marquage, et
lui seul, qui déclenche une resérialisation.

Le contrat :

```python
contract.name, contract.description
contract.fields         # Mapping[str, Field], ordonné
contract.sections       # required: list[str], optional: list[str]

field.type              # "slug" | "text" | "date" | "enum" | "list"
field.required          # bool
field.values            # list[str] — enum seulement
field.source            # str | None — le `from` d'un contrat dérivé
```

---

## Commandes : déclaration, découverte, surcharge

**La découverte se fait par le système de fichiers**, jamais par un registre à tenir à jour.

- génériques : `skills/list-dir/scripts/listdir/commands/<nom>.py`
- propres à une liste : `<liste>/.list/commands/<nom>.py`

Chaque module déclare, au niveau module :

```python
DESCRIPTION = "ce que fait la commande, affiché par help"
REQUIRES    = ["git"]        # outils externes ; absent → sortie non nulle le nommant

def register(parser): ...            # les arguments de la commande
def command(args, utils): ...        # -> Result[T]
```

`help` lit `DESCRIPTION` et `REQUIRES` **sans importer le module** (`ast.parse`) : une commande
cassée ne fait pas tomber `help`, et rien ne s'exécute pour afficher une liste.

`REQUIRES` est vérifié **avant** l'appel : une dépendance déclarée absente sort non nulle en la
nommant, plutôt que d'échouer plus loin sans motif lisible.

**Surcharge** — une commande de la liste masque la générique de même nom, à deux exceptions près :

| | |
|---|---|
| `validate` | non surchargeable — elle porte le contrat |
| `help` | non surchargeable — elle porte la découvrabilité |
| `migrate` | non surchargeable — elle réécrit des fichiers au nom du contrat |

`help` marque `(surchargée)` toute générique masquée. `utils.run("move", …)` donne accès à la
générique : une surcharge **décore**, elle ne réimplémente pas.

---

## Quand le contrat change

Un contrat n'est pas figé : un champ apparaît, une section est ajoutée, l'ordre est remanié. Tous
les éléments écrits avant deviennent invalides **d'un coup**, et les corriger à la main est
exactement ce que ce format existe pour supprimer.

`migrate` les remet en ligne :

| Écart au contrat courant | Ce que fait `migrate` |
|---|---|
| champ déclaré, absent de l'élément | posé au marqueur de son statut |
| section déclarée, absente | ajoutée au marqueur de son statut |
| `id` absent | posé au nom du fichier — jamais un marqueur |
| ordre des champs ou des sections différent | repris de l'ordre du contrat |
| champ ou section que le contrat ne déclare plus | **conservé** et signalé ; `--drop` le retire |
| valeur déjà écrite | jamais touchée |

**Elle ne juge pas.** Elle ne renomme rien et ne reporte aucune valeur : décider qu'un champ
`severite` disparu est devenu `gravite` demande un contexte qu'aucun script n'a. C'est le partage
du dispositif — la structure au script, le jugement au modèle. La conservation par défaut suit la
même règle : supprimer une donnée que personne n'a relue serait un jugement.

**Rejouable.** Une liste déjà conforme ne fait toucher aucun fichier. `--dry-run` montre le plan
sans rien écrire.

### Mode de défaillance

Un élément modifié voit son front matter **resérialisé** — `Item.realigned` abandonne `raw_front`,
et c'est ce qui permet de retirer et de réordonner, là où `with_fields` ne sait que fusionner.
D'éventuels commentaires TOML écrits à la main y disparaissent. C'est assumé : le contrat est
l'autorité sur la structure, pas la mise en page du fichier.

Une remarque seule — un champ conservé — ne déclenche **aucune** écriture. Sans cette distinction,
relancer `migrate` sur une liste conforme réécrirait chaque élément et lui coûterait son
`raw_front` pour rien.

Enfin, une migration réécrit du contenu : son commit ne doit jamais être mêlé à un `move`, sous
peine de faire lâcher la détection de renommage et de perdre la traçabilité.

---

## Listes dérivées

`derive` **projette la structure** d'une liste sur une liste neuve. Le gabarit vit dans la liste
source, sous `.list/templates/`, et va par paire :

- `<nom>.toml` → copié en `<dst>/.list/contract.toml` ; la destination devient une liste ordinaire
- `<nom>.md` → le moule du corps, une copie par élément source

| | |
|---|---|
| Crée une liste | oui : répertoire, contrat, un élément par élément source |
| Copie le contenu des éléments | **non** : même `id`, mais le corps vient du moule |
| Convertit | seulement par `from`, champ par champ, déclaré au contrat cible |
| Touche la source | non |
| Destination existante | erreur — ni fusion ni mise à jour |

**Pourquoi le contenu n'est pas recopié** : une liste dérivée qui porterait la prose de sa source en
serait un doublon éditable, et la source cesserait d'être unique. Une liste dérivée ne porte que du
contenu neuf.

Le report par `from` est le seul emprunt, et il est déclaratif :

```toml
[fields.title]
type = "text"
required = true
from = "title"        # repris de l'élément source

[fields.verdict]
type = "enum"
required = true
values = ["retenu", "écarté"]
                      # pas de `from` : posé au marqueur, c'est au modèle de trancher
```

L'`id` est reporté d'office — c'est le seul lien entre une fiche dérivée et son élément d'origine.
`derive` ne transforme, ne concatène et ne calcule rien : un champ nommé par `from` est recopié, un
champ sans `from` reçoit le marqueur de son statut.

**`derive` projette, `move` déplace.** `move` fait changer un fichier de liste — `git mv`,
l'historique suit, l'élément reste le même. `derive` crée un second fichier à côté du premier, sans
lien Git, relié seulement par l'`id`.

---

## Le rendu de `merge`

| Niveau | Contenu |
|---|---|
| `#` | préambule : nom de la liste, date, **compte des éléments face au compte du répertoire** |
| `##` | un élément — son `title`, ou son `id` à défaut |
| `###` | les sections de l'élément, décalées d'un niveau |

Le décalage n'est pas cosmétique : les sections d'un élément sont des `##` dans son fichier. Sans
lui, compter les `##` du document aggloméré compterait les sections en plus des éléments, et le
contrôle de conservation ne voudrait plus rien dire.
