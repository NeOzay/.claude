# Le format d'une liste

Ce qu'est un répertoire-liste, et ce qu'une liste ajoute à un gabarit. Tout ce qui suit est
mécaniquement vérifiable par `validate`.

**Une liste est une liste de gabarits.** Le format d'un fichier, le contrat, les six types admis,
le préremplissage et les marqueurs sont déclarés par `gabarit`, dont ce paquet dépend :
[Le format d'un gabarit](../../gabarit/references/format.md). Ce fichier-ci ne porte que ce qu'une
liste y ajoute — l'`id` égal au nom du fichier, `.list/`, `from`, `[origin]`.

---

## Structure d'un répertoire-liste

```
ma-liste/
├── .list/
│   ├── contract.toml          contrat : champs, sections, description
│   ├── commands/              commandes propres à cette liste
│   │   └── close.py
│   ├── patrons/               patrons pour `derive`
│   │   ├── review.toml
│   │   └── review.md
│   ├── semence/               la semence intacte, au dernier semis
│   │   ├── contract.toml
│   │   └── patrons/
│   └── backup/                ce que le dernier `reseed` a remplacé
│       ├── contract.toml
│       └── patrons/
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

Un gabarit, plus une règle d'identité :
[Un gabarit](../../gabarit/references/format.md#un-gabarit) donne le format du fichier — Markdown à
front matter TOML délimité par `+++`, sections en `##`, dates et listes natives.

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

- `id` est **toujours** égal au nom de fichier, sans l'extension. C'est la seule identité, et c'est
  ce qu'une liste ajoute à un gabarit, qui n'en impose aucune.
- Un élément ne porte pas d'estampille `gabarit` : c'est le contrat de sa liste qui fait foi, et
  `[origin]` dit d'où ce contrat vient.

---

## Le contrat

`.list/contract.toml`, dans la liste elle-même. Il déclare ce qu'un élément doit contenir, et a la
forme de celui d'une semence de gabarit — `name`, `description`, `[fields.*]`, `[sections.*]`, les
six types, `text`/`command`, `description` exigée partout :
[Le contrat](../../gabarit/references/format.md#le-contrat).

Quatre ajouts lui sont propres.

**`[fields.id]` est toujours déclaré, toujours obligatoire**, et sa valeur est le nom du fichier.

**`from` projette un champ** d'une liste source sur une liste dérivée. Un gabarit seul n'a pas de
source, et n'a donc pas de `from` : [Listes dérivées](../references/operations.md#listes-dérivées).

**`[origin]` dit d'où la liste vient** — sa semence, sa version, un gel éventuel. Le contrat d'une
définition la porte, et la copie l'emporte avec le reste :
[Provenance et péremption](../references/provenance.md#provenance-et-péremption).

**L'ancien format à deux listes est refusé** — un unique `[sections]` portant deux listes de noms,
`required` et `optional` —, avec un message nommant la liste à migrer. La réécriture est manuelle :
aucune commande ne la fait, et la semence de la liste est l'endroit où corriger. Tolérer les deux
formes en lecture, ce serait les laisser diverger : la documentation d'une section n'existerait que
dans l'une des deux écritures, et rien ne dirait laquelle fait foi.

**L'état d'un élément est porté par son répertoire, jamais par un champ.** Une liste d'éléments
soldés est une liste sœur avec son propre contrat, pas un champ `soldé = true` — un état porté par
un champ se change par une écriture, porté par le répertoire il se change par un renommage, que
l'historique conserve.

**Avant de remplir un élément, lire `list-dir contract <liste>`** — le contrat réellement appliqué,
pas la définition qui l'a semé.

### Préremplir un champ ou une section

Les deux clés `text` et `command`, leur exclusion mutuelle, leurs refus et l'échec fermé sont ceux
d'un gabarit :
[Préremplir un champ ou une section](../../gabarit/references/format.md#préremplir-un-champ-ou-une-section).
Elles s'appliquent **partout où un champ ou une section est posé pour la première fois** : `new`,
`migrate` sur un champ ou une section absents, `derive` sur un champ sans `from`. Une valeur déjà
écrite n'est jamais recalculée, et `merge` fait sortir une valeur préremplie comme une autre.

La commande tourne **dans le répertoire de la liste** — ou, si celui-ci n'existe pas encore, dans
son premier ancêtre qui existe. Le cas se produit en `derive`, qui construit toutes ses fiches en
mémoire avant de créer quoi que ce soit : `LISTDIR_LIST` y nomme bien la liste engendrée, mais le
répertoire courant de la commande est ailleurs. Une commande qui lit le disque relativement à son
cwd — `ls | wc -l` — n'y rendra donc pas la même chose qu'à `new`. `LISTDIR_ROOT` est résolue
depuis ce même répertoire.

L'environnement porte, à la place des `GABARIT_*` :

| Variable | Valeur |
|---|---|
| `LISTDIR_ID` | l'identifiant de l'élément — le nom de son fichier, sans extension |
| `LISTDIR_NAME` | le nom du champ, ou le titre de la section |
| `LISTDIR_LIST` | le chemin du répertoire-liste |
| `LISTDIR_CONTRACT` | le `name` du contrat |
| `LISTDIR_ROOT` | la racine du dépôt git — **absente de l'environnement** hors dépôt |

Trois limites propres à une liste :

- **`derive` ne préremplit pas les sections d'une fiche** : elles viennent du patron `.md`, pas du
  contrat. Seuls les champs sans `from` y passent par `text`/`command`.
- **un essai de migration n'exécute aucune `command`**, ce qui a une contrepartie :
  [Quand le contrat change](../references/operations.md#quand-le-contrat-change).
- **rien n'est mémorisé** : `migrate` rejouée sur un élément dont le champ est déjà écrit ne
  relance pas la commande. C'est la pose initiale qu'on préremplit, pas la valeur qu'on maintient.

---

## Les marqueurs

Les deux marqueurs, ce qu'ils disent, et ce que `--filled` réclame ou ignore sont ceux d'un
gabarit : [Les marqueurs](../../gabarit/references/format.md#les-marqueurs). Un élément créé par
`new`, ou une fiche créée par `derive`, porte **tout** le contrat — chaque champ et chaque section,
même facultatif. Ce qu'on ne voit pas n'est jamais rempli.

**Seul `id` échappe aux deux** : il est renseigné à la création, puisqu'il est le nom du fichier.

C'est `list-dir contract <liste>` qui sert les descriptions du contrat — un marqueur dit qu'il faut
écrire, jamais quoi écrire.

**`merge` exige `--filled`** et omet de sa sortie les sections restées à `<OPTIONNEL>` : elles ont
joué leur rôle de guide et n'ont rien à dire dans un document final.
