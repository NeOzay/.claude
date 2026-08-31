---
name: list-dir
description: >
  Manipule des répertoires-listes : un répertoire = une liste, un fichier = un élément, un contrat
  embarqué qui déclare la structure. Fournit douze commandes génériques (init, new, list, show,
  validate, migrate, move, derive, merge, defs, contract, help), des définitions de listes
  réutilisables pour amorcer une liste dans un projet neuf, et une bibliothèque Python importable.
  Se déclenche dès qu'il s'agit de créer, amorcer, valider, migrer, filtrer, déplacer, dériver ou
  agglomérer les éléments d'une liste stockée en fichiers. Ne juge aucun contenu.
---

# list-dir — répertoires-listes

Une liste tenue dans un document unique coûte cher à toute opération mécanique : en retirer un
élément, c'est découper de la prose et la recoller ailleurs sans qu'aucune commande ne signale une
perte ; en compter, c'est recompter à la main.

Un **répertoire-liste** renverse ça :

```
ma-liste/
├── .list/
│   ├── contract.toml     ce que doit contenir un élément
│   ├── commands/         commandes propres à cette liste
│   └── templates/        gabarits pour `derive`
├── premier-element.md
└── second-element.md
```

**Tout `*.md` à la racine est un élément, sans exception.** Tout le reste vit sous `.list/`. C'est
cette règle qui rend le comptage et la conservation triviaux.

**Partage des rôles** : les scripts font la structure — créer, chercher, déplacer, valider,
agglomérer. Le jugement et la correction de contenu restent au modèle, qui écrit directement dans
un fichier quand il corrige une section. `validate` repasse après.

## Prérequis

**Python ≥ 3.12**, stdlib seule — aucune dépendance à installer. Les commandes le vérifient au
démarrage et sortent en code non nul si la version est inférieure.

## Les douze commandes

```bash
list-dir help [<liste>]                      # les commandes disponibles, avec leur description
list-dir defs                                # les définitions disponibles, et d'où elles viennent
list-dir init <répertoire>                   # crée une liste et son contrat squelette
list-dir init <répertoire> --def <nom>       # ... ou celui d'une définition, résolue par son nom
list-dir init <répertoire> --from <chemin>   # ... ou d'un répertoire de définition, tel quel
list-dir new <liste> <id>                    # crée un élément prérempli du contrat
list-dir list <liste> [--where c=v] [--sort c]
list-dir show <liste> <id>
list-dir contract <liste>                    # le contrat EN VIGUEUR de cette liste
list-dir contract --def <nom>                # ... ou celui d'une définition, résolue par son nom
list-dir contract --from <chemin>            # ... ou d'un répertoire de définition, tel quel
list-dir contract <cible> --template <nom>   # ... le gabarit <nom>.toml plutôt que le contrat
list-dir contract <cible> --values <champ>   # les valeurs déclarées d'un champ, une par ligne
list-dir validate <liste> [--filled]         # structure ; --filled exige que tout soit rempli
list-dir migrate <liste> [--drop] [--dry-run] # remet les éléments au contrat courant
list-dir move <liste> <id> <liste-cible>     # git mv seul — l'historique suit
list-dir derive <src> <dst> --template <nom> # projette une liste sur une liste neuve
list-dir merge <liste> [--out <fichier>]     # agglomère, conservation vérifiée
```

`list-dir` est un lien de `bin/` vers `scripts/list-dir.py`, résolu par le `PATH`. Sa présence
est vérifiée au démarrage de chaque session par `scripts/sante_skills.py` — inutile de la
retester dans un bloc.

**Amorcer une liste quand aucune n'existe.** `init` seul rend un squelette minimal, à compléter à
la main. Une **définition** — un `contract.toml` et ses gabarits, rangés sous `list-dir/<nom>/` —
donne à la place un contrat complet, et `init --def <nom>` la trouve sans qu'on ait à dire où elle
est. Quatre racines sont fouillées, du projet vers la configuration ; la plus spécifique gagne, et
deux racines de même rang qui portent le même nom font échouer la commande en les nommant.
`defs` montre ce qui est définissable, d'où ça vient, et ce qui en masque quoi.

**La définition fait autorité le temps de l'`init`, et pas au-delà.** La liste créée porte dès lors
sa propre copie du contrat, et c'est elle seule que les commandes appliquent — `contract <liste>`
l'imprime. Rien ne les resynchronise ensuite : une liste qu'un projet a délibérément redéfinie ne se
fait pas rattraper par la définition qui l'a semée. `contract --def`/`--from` imprime la semence,
justement parce qu'une liste engendrée par `derive` n'a de contrat qu'après coup — une prose écrite
d'avance n'a que le gabarit source à quoi renvoyer. Forme d'une définition, les quatre racines, la
règle de précédence, ce que chaque cible engage : `references/contrat-liste.md`.

**Ce qui est mécaniquement connu se prérenseigne.** Un champ ou une section du contrat peut porter
`text = "…"` (texte littéral) ou `command = "…"` (sortie d'une commande Bash, lancée depuis le
répertoire de la liste, ou son premier ancêtre existant quand `derive` ne l'a pas encore créé) : la
valeur est posée à la place du marqueur, à la création comme en migration. Un champ prérempli est
une valeur ordinaire — `validate --filled` ne le réclame pas. Une commande qui échoue interrompt
l'opération sans rien écrire, en la nommant, et `migrate --dry-run` n'en exécute aucune — au prix
de ne pas pouvoir annoncer celle qui échouera.

**Le contrat change, la liste suit.** Ajouter un champ ou une section au contrat invalide d'un
coup tous les éléments écrits avant : `migrate` les remet en ligne — ce qui manque est posé au
marqueur, l'ordre est repris du contrat, aucune valeur déjà écrite n'est touchée. Elle ne renomme
et ne reporte rien : un champ que le contrat ne déclare plus est conservé et signalé, `--drop` le
retire sur ordre. Le renommage reste au modèle, qui seul sait que `severite` est devenu `gravite`.

**Échec fermé** : sortie non nulle et message nommant la cause — contrat introuvable, champ inconnu,
élément non conforme, outil déclaré manquant, agglomération qui perd un élément. Jamais de succès
silencieux sur une liste vide là où c'en est un.

## La bibliothèque

Les commandes ne sont qu'une façade : tout passe par un paquet Python importable, qui donne à un
script tiers exactement les mêmes moyens.

```python
import shutil, sys
from pathlib import Path

# La commande est un lien de `bin/` vers `scripts/list-dir.py` : le résoudre donne le
# répertoire à insérer, sans constante et où que le dépôt soit installé.
cmd = shutil.which("list-dir")
if cmd is None:
    raise SystemExit("list-dir introuvable dans le PATH — ajouter bin/ au profil du shell")
sys.path.insert(0, str(Path(cmd).resolve().parent))
from listdir import open_list

lst = open_list("chemin/vers/ma-liste").unwrap()
for item in lst.items().unwrap():
    print(item.id, item.fields["title"])
```

## Pour aller plus loin

Structure d'une liste, format du contrat, marqueurs de champ à remplir, surface complète de l'API,
déclaration et surcharge des commandes, listes dérivées :
`references/contrat-liste.md`.
