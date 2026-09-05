# Étendre `list-dir`

Deux façons d'ajouter du comportement sans toucher au paquet : appeler la bibliothèque depuis un
script, ou déposer une commande. Ce que font les commandes elles-mêmes est décrit dans
[Les opérations sur une liste](../references/operations.md).

---

## La bibliothèque Python

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
[`validate`](../references/operations.md#ce-que-validate-confronte-au-contrat) qui le dit.

### L'élément, immuable

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

### Le contrat

```python
contract.name, contract.description
contract.fields         # Mapping[str, Field], ordonné
contract.sections       # Mapping[str, Section], ordonné
contract.required_sections  # list[str] — les titres requis, dans l'ordre du TOML

field.type              # "slug" | "text" | "date" | "enum" | "list"
field.required          # bool
field.values            # list[str] — enum seulement
field.source            # str | None — le `from` d'un contrat dérivé

section.name            # str — le titre, tel qu'il paraît en `##`
section.required        # bool
section.description     # str — libre, éventuellement vide
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

`REQUIRES` est vérifié **avant** l'appel : une dépendance déclarée absente sort non nulle en la
nommant, plutôt que d'échouer plus loin sans motif lisible.

**Surcharge** — une commande de la liste masque la générique de même nom, à trois exceptions près :

| | |
|---|---|
| `validate` | non surchargeable — elle porte le contrat |
| `help` | non surchargeable — elle porte la découvrabilité |
| `migrate` | non surchargeable — elle réécrit des fichiers au nom du contrat |

`utils.run("move", …)` donne accès à la générique : une surcharge **décore**, elle ne réimplémente
pas.

## Ce que `help` découvre

**`help` est le seul point d'où l'interface complète se découvre** : les génériques, et celles que
la liste visée ajoute ou substitue. Sans liste en argument, seules les génériques sont visibles —
c'est exact, pas un oubli. Une commande de liste qui masque une générique porte la mention
**`(surchargée)`** : une surcharge invisible serait un piège.

Rien n'est exécuté pour afficher cette page. `DESCRIPTION` et `REQUIRES` sont lus par `ast.parse`,
jamais par import — un module déposé dans une liste ne peut donc pas s'exécuter du seul fait qu'on
demande l'aide, ni la faire échouer parce qu'il est cassé. Un module illisible est signalé
**INUTILISABLE** à sa place, et les autres restent listés. Un module qui écrit sur stderr à
l'import le prouve : mesuré, son effet ne se produit pas alors que sa description s'affiche.
