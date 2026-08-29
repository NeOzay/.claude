---
name: list-dir
description: >
  Manipule des répertoires-listes : un répertoire = une liste, un fichier = un élément, un contrat
  embarqué qui déclare la structure. Fournit dix commandes génériques (init, new, list, show,
  validate, migrate, move, derive, merge, help) et une bibliothèque Python importable. Se déclenche
  dès qu'il s'agit de créer, valider, migrer, filtrer, déplacer, dériver ou agglomérer les éléments
  d'une liste stockée en fichiers. Ne juge aucun contenu.
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

## Les dix commandes

```bash
list-dir help [<liste>]                      # les commandes disponibles, avec leur description
list-dir init <répertoire>                   # crée une liste et son contrat squelette
list-dir new <liste> <id>                    # crée un élément prérempli du contrat
list-dir list <liste> [--where c=v] [--sort c]
list-dir show <liste> <id>
list-dir validate <liste> [--filled]         # structure ; --filled exige que tout soit rempli
list-dir migrate <liste> [--drop] [--dry-run] # remet les éléments au contrat courant
list-dir move <liste> <id> <liste-cible>     # git mv seul — l'historique suit
list-dir derive <src> <dst> --template <nom> # projette une liste sur une liste neuve
list-dir merge <liste> [--out <fichier>]     # agglomère, conservation vérifiée
```

`list-dir` est un lien de `bin/` vers `scripts/list-dir.py`, résolu par le `PATH`. Sa présence
est vérifiée au démarrage de chaque session par `scripts/sante_skills.py` — inutile de la
retester dans un bloc.

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
