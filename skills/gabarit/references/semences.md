# Semences

Ce qu'est une semence, où `gabarit` la cherche, ce que l'estampille engage, et ce que reçoit une
commande de préremplissage.

---

## Forme d'une semence

Un répertoire portant un `contract.toml`, et rien d'autre n'est exigé :

```
gabarit/
└── suivi/               le nom de la semence
    └── contract.toml    obligatoire — sans lui, ce n'est pas une semence
```

Ce que le contrat déclare — `name`, `description`, `[fields.*]`, `[sections.*]`, les six types,
`text`/`command` : [Le contrat](format.md#le-contrat). Une liste `list-dir` en porte un de même
forme, avec deux différences :

- **aucun `id` n'est imposé** : un gabarit n'est pas lié au nom de son fichier. Un suivi archivé
  sous `done/<date>-<slug>.md` ne porte plus le nom de son slug, et reste conforme ;
- **le champ `gabarit` est réservé** à l'estampille. Une semence qui le déclare est refusée à la
  lecture.

`from`, `[origin]` et `patrons/` n'ont de sens que pour une liste : une semence de gabarit les
ignore.

## Où elle est cherchée

**Quatre rangs**, du plus spécifique au plus général. Le répertoire qui les porte dit qui sait les
lire : `gabarit/` ici, `list-dir/` pour les définitions de liste — le mécanisme est le même, les
espaces de noms ne se mélangent pas.

| # | Racine |
|---|---|
| 1 | `<projet>/.claude/gabarit/<nom>/` |
| 2 | `<projet>/.claude/skills/*/gabarit/<nom>/` |
| 3 | `<config>/gabarit/<nom>/` |
| 4 | `<config>/skills/*/gabarit/<nom>/` |

**Découverte par le système de fichiers**, jamais par un registre à tenir à jour : un registre se
désynchronise, une arborescence non. Un répertoire sans `contract.toml` n'est pas une semence à
moitié faite — ce n'en est pas une, et elle n'est pas proposée.

**Les deux ancrages sortent de la même remontée, mais ne cherchent pas la même chose** : un
*projet* est un répertoire qui **contient** un `.claude` ; une *configuration* est un répertoire
qui **est** un `.claude`. Sur un dépôt dont la configuration est `~/.claude` et qui porte son
propre `~/.claude/.claude`, une règle unique ferait répondre la même chose aux deux questions, et
l'un des deux rangs viserait le mauvais répertoire. Les racines atteintes deux fois sont
dédupliquées sur leur chemin résolu, l'exemplaire du rang le plus fort étant conservé.

**La spécificité prime, et masquer n'est pas un conflit** : le rang 1 masque le rang 4, et c'est un
succès. Une **ambiguïté ne se déclare qu'à rang égal** — deux skills qui définissent le même nom —,
et la commande échoue en nommant les deux chemins ; choisir en silence ferait dépendre le résultat
de l'ordre de parcours d'un répertoire. Un nom que personne ne porte échoue en listant les noms
connus, plutôt qu'un « introuvable » sec qui obligerait à aller lire l'arborescence.

`gabarit defs` imprime les ancrages retenus, le rang et l'origine de chaque semence, et ce qui en
masque quoi.

`--from <chemin>` prend une semence à un chemin, sans passer par les rangs.

## L'estampille

`new` écrit `gabarit = "<nom>"` en tête du front matter, avant les champs du contrat.

| Semence désignée par | Nom estampillé |
|---|---|
| `new <nom>` | ce nom |
| `new --from <chemin>` | le nom du **répertoire** de la semence — celui sous lequel elle se résoudra une fois rangée, et non le `name` de son contrat |

`check <fichier>` résout l'estampille dans les racines. Trois cas s'écartent :

- **pas d'estampille** : échec nommé, sauf semence imposée par `--def` ou `--from`. Vérifier contre
  une semence devinée pourrait déclarer conforme un fichier à un contrat qui n'est pas le sien ;
- **estampille mal formée** (pas un slug) : échec nommé ;
- **semence imposée qui contredit l'estampille** : acceptée, puisque demandée, mais dite sur stderr.

## L'environnement du préremplissage

Une `command` tourne dans le répertoire du fichier — ou son premier ancêtre qui existe — et reçoit,
en plus de l'environnement du processus :

| Variable | Valeur |
|---|---|
| `GABARIT_FICHIER` | le chemin du fichier posé |
| `GABARIT_NAME` | le nom du champ, ou le titre de la section |
| `GABARIT_SEMENCE` | le nom de la semence — celui de l'estampille |
| `GABARIT_ROOT` | la racine du dépôt git — **absente de l'environnement** hors dépôt |

Un élément de liste reçoit les `LISTDIR_*` à la place : c'est l'appelant qui fournit
l'environnement, le calcul du préremplissage n'en connaît aucun.
