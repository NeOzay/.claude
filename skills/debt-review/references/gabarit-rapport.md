# La fiche de revue et le rapport aggloméré

Deux objets, et un seul est écrit à la main.

| | Qui l'écrit | Où |
|---|---|---|
| **la fiche** — un verdict sur une entrée | le modèle, dans un fichier créé par `derive` | `done/revues/<AAAA-MM-DD>/<id>.md` |
| **le rapport** — l'aggloméré de toutes les fiches | `merge`, jamais à la main | `done/revues/<AAAA-MM-DD>-revue.md` |

Le modèle **instruit**, la commande **agglomère**. Rien de ce qui suit n'est un format à respecter
en écrivant du texte : la structure vient du contrat
`.claude/implementation/todo/technical-debt/.list/templates/review.toml`, lu par `derive`, et
`validate` la fait respecter.

---

## La fiche

`derive` la crée déjà remplie de sa structure : `id`, `title` et `date` reportés de l'entrée, tout
le reste au marqueur. Il ne reste qu'à écrire.

```markdown
+++
id = "cache-sessions-sans-ttl"
title = "Le cache de sessions n'expire jamais"
date = 2025-03-04
reviewed = "<À REMPLIR>"
category = "<À REMPLIR>"
+++

## Vérifié par

<À REMPLIR>

## Verdict

<À REMPLIR>

## Action

<À REMPLIR>

## Arbitrage

<OPTIONNEL>
```

**Les deux champs à écrire :**

- `category` — une des valeurs **déclarées par le contrat**, en ASCII kebab-case. Le contrat refuse
  toute valeur hors de la liste, donc une faute de frappe échoue à `validate` au lieu de se ranger
  dans une pile fantôme. Les lire — la liste de revue n'existant pas encore, le renvoi vise le
  gabarit source :

  ```bash
  list-dir contract --def technical-debt --template review --values category
  ```

  Ce que chacune veut dire et la preuve qu'elle exige : `categories.md`. Ce fichier-ci ne les
  recopie pas — une énumération de plus à tenir à jour se désynchroniserait sans qu'aucune commande
  ne le dise.
- `reviewed` — la date de **cette** revue, jamais celle du constat. `date` porte déjà celle-là, et
  elle est reportée sans être touchée : c'est elle qui ordonne l'intérieur d'une pile.

**Ce qui n'est jamais écrit dans une fiche** : la prose de l'entrée. La fiche ne porte que du
jugement, qui n'existe nulle part ailleurs — c'est ce qui la rend légitimement éditable sans faire
double emploi avec le registre. `show` va lire l'entrée quand il faut la relire.

**Les quatre sections** — trois requises, `Arbitrage` facultative. Ce que chacune attend est dit
au contrat de la liste de revue, que `list-dir contract <revue>` imprime ; la semence de fiche
([`templates/review.md`](../../implementation-tracker/list-dir/technical-debt/templates/review.md))
n'ajoute que les cas qui n'y tiennent pas. Ce fichier-ci ne recopie ni l'un ni l'autre — même
raison que pour les catégories.

Deux points tiennent au rapport, et non à la fiche :

- coller une sortie de commande sous **Vérifié par** est sûr : un `## ` qui s'y trouverait n'ouvre
  pas de section, le découpage comme le recomptage ignorent ce qui est entre fences ;
- **Arbitrage** laissée au marqueur est **omise** du rapport, au lieu d'y figurer vide.

> *Mode de défaillance* — le corps d'une section vaut « à remplir » **exactement** tant qu'il est le
> marqueur seul. Y ajouter une consigne, un rappel ou un « TODO » suffit à faire passer la fiche
> pour instruite auprès de `validate --filled`, et le rapport partira à l'arbitrage avec un verdict
> qui n'existe pas.

## Le rapport

Rendu par `merge`, et par rien d'autre :

```bash
list-dir merge .claude/implementation/done/revues/<AAAA-MM-DD> \
        --out .claude/implementation/done/revues/<AAAA-MM-DD>-revue.md
```

Sa forme est fixée par la commande et vaut pour toute liste :

| Niveau | Contenu |
|---|---|
| `# ` | le préambule : nom de la liste, date, **compte des blocs face au compte du répertoire** |
| `## ` | une fiche — son `title` |
| `### ` | les sections de la fiche, décalées d'un niveau |

```markdown
# revue

2026-09-02 — 17 élément(s) aggloméré(s), 17 fichier(s) dans le répertoire.

## Le cache de sessions n'expire jamais

### Vérifié par

`grep -n 'ttl' orders/cache.py` → `ttl=1800` passé au constructeur depuis le commit `4f1c9ab`.

### Verdict

La dette a été payée : les entrées de cache expirent, le problème décrit ne se reproduit plus.

### Action

Déplacer vers `technical-debt-solde` avec la commande ci-dessus.
```

Le décalage d'un niveau n'est pas cosmétique : les sections d'une fiche sont des `## ` dans son
fichier. Sans lui, le recomptage verrait les sections en plus des blocs, et le compte du préambule
ne voudrait plus rien dire.

> **Ne pas recompter à la main.** `merge` compte hors blocs de code ; un `grep -c '^## '` lancé sur
> l'aggloméré compte en plus les `## ` que porte une sortie de commande collée — c'est-à-dire
> exactement le contenu que ce skill demande d'écrire. Le compte qui fait foi est celui du
> préambule.

**Le préambule dit ce que `merge` a pu vérifier, et rien de plus** : les blocs rendus face aux
fichiers **présents dans la liste de revue**.

La complétude se contrôle donc **contre le registre**, avant d'agglomérer
([Étape 3](../SKILL.md#étape-3--agglomérer-et-restituer), qui porte le mode de défaillance mesuré).
C'est le seul contrôle de la revue qui ne tienne pas dans une commande : la liste générique ne
connaît pas le registre dont elle dérive, et c'est précisément ce qui la garde générique.

**Le rapport ne s'édite pas.** Une correction se fait dans la fiche, et `merge` se relance — c'est
la même règle que partout : une vue dérivée qui devient éditable fait perdre la source unique.

## Ce que le rapport n'est pas

Ce n'est **pas** un journal : un rapport par revue, un répertoire par revue, archivés tels quels et
jamais appendus. Le journal des soldes est la liste `technical-debt-solde`, celui des sorties sèches
`technical-debt-ecarte`.

Ce n'est **pas** une décision : le rapport est présenté, l'utilisateur tranche, l'écriture suit. Un
rapport archivé sans arbitrage écrit à côté est un rapport qui n'a servi à rien.
