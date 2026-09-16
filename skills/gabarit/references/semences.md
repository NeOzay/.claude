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

Le contrat a la forme de celui d'une liste — `name`, `description`, `[fields.*]`,
`[sections.*]`, `text`/`command` : [Le contrat](../../list-dir/references/format.md#le-contrat).
Deux différences :

- **aucun `id` n'est imposé** : un gabarit n'est pas lié au nom de son fichier. Un suivi archivé
  sous `done/<date>-<slug>.md` ne porte plus le nom de son slug, et reste conforme ;
- **le champ `gabarit` est réservé** à l'estampille. Une semence qui le déclare est refusée à la
  lecture.

`from`, `[origin]` et `templates/` n'ont de sens que pour une liste : une semence de gabarit les
ignore.

## Où elle est cherchée

Les quatre racines de list-dir, sous un répertoire `gabarit/` au lieu de `list-dir/` — le
mécanisme est partagé, les espaces de noms ne se mélangent pas :

| # | Racine |
|---|---|
| 1 | `<projet>/.claude/gabarit/<nom>/` |
| 2 | `<projet>/.claude/skills/*/gabarit/<nom>/` |
| 3 | `<config>/gabarit/<nom>/` |
| 4 | `<config>/skills/*/gabarit/<nom>/` |

Ancrages, précédence et ambiguïté sont ceux des définitions de liste :
[Les quatre racines](../../list-dir/references/definitions.md#les-quatre-racines). `gabarit defs`
imprime les ancrages retenus, le rang et l'origine de chaque semence, et ce qui en masque quoi.

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
