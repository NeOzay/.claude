# Road-map

Trois **répertoires-listes**, sous `.claude/implementation/todo/` :

| Répertoire | Ce qu'il contient |
|---|---|
| `road-map/` | les tâches qu'on veut accomplir, et qu'aucun chantier ne porte encore |
| `road-map-fait/` | celles qu'un chantier a portées, avec le chantier qui l'a fait |
| `road-map-ecarte/` | celles qu'on a cessé de vouloir, avec leur motif |

Ce sont des répertoires-listes : toutes les manipulations passent par les commandes de `list-dir`,
et par elles seules. Structure, contrat, marqueurs, comportement des commandes :
[Répertoires-listes](../../list-dir/references/format.md#structure-dun-répertoire-liste).

```bash
T=".claude/implementation/todo"
```

**Les trois listes n'existent pas d'office dans un projet neuf.** Elles s'y amorcent depuis les
définitions que ce skill embarque sous `list-dir/`, résolues par leur nom — même geste que pour les
registres de dette ([Registre de dette](dette.md#registre-de-dette-technique)), et mêmes suites :
une liste amorcée est **détachée** de sa définition, porte sa propre copie du contrat, et rien ne la
resynchronise de lui-même.

```bash
set -e
for l in road-map road-map-fait road-map-ecarte; do
  list-dir init "$T/$l" --def "$l"
  list-dir validate "$T/$l" --filled
done
list-dir defs    # ce qui est définissable, et de quelle racine ça vient
```

Le `set -e` n'est pas décoratif, et le `validate` derrière chaque `init` non plus : un amorçage se
joue **une fois par projet**, et personne ne repasse derrière. Sans eux, une définition introuvable
ou un contrat refusé laisse une liste absente ou vide au milieu des deux autres, la boucle se
termine sans un mot, et le trou se découvre au premier `move` — c'est-à-dire le jour où une entrée
doit sortir. `--filled` sur des listes neuves est trivialement vrai : c'est justement le moment de
l'écrire, tant qu'il ne coûte rien.

---

## Le rôle

Un **pense-bête**. On y note une tâche qu'on veut accomplir : la correction d'une dette devenue
gênante, une idée rencontrée pendant un chantier, un sujet qu'on ne veut pas perdre.

Une entrée sert de **point de départ à un chantier**. C'est ce qui commande son contenu : elle
référence les éléments pertinents — contexte, code, entrées de dette, chantiers archivés — pour
qu'on puisse repartir d'elle sans avoir le sujet en tête. Ce que le contrat exige exactement se lit
là où il s'applique, jamais dans une copie en prose :

```bash
list-dir contract "$T/road-map"      # le contrat EN VIGUEUR, tel qu'il s'applique
```

Ce que le contrat déclare sans pouvoir le motiver : **`À faire` reste requise jusque dans les
listes de sortie**. Sans elle, une entrée sortie ne dirait plus de quoi elle parlait, et
`road-map-fait/` deviendrait une liste de dates.

## La frontière avec le registre de dette

C'est la distinction qui décide où une chose atterrit, et les deux listes se croisent souvent.

| | `technical-debt/` | `road-map/` |
|---|---|---|
| Nature | un **constat**, vérifié dans le dépôt | une **tâche** qu'on veut accomplir |
| Qui écrit | l'orchestrateur, à la clôture | l'utilisateur, quand il le demande |
| Ce qu'elle exige | de quoi plaider un coût — [Ce qui entre](dette.md#ce-qui-entre) | de quoi rouvrir le sujet |

Une idée d'amélioration n'entre pas au registre de dette : elle vient ici. Une dette constatée
n'entre pas ici : elle va au registre. Mais **décider de payer une dette** est une tâche, et cette
tâche-là s'écrit ici, en référençant l'entrée de dette par son `id`.

> *Mode de défaillance* — les deux listes se confondent dès qu'on écrit dans la road-map un constat
> qu'on n'a pas vérifié, parce qu'il est plus facile à noter là. On se retrouve alors avec un
> registre de dette qui prétend être exhaustif et ne l'est plus, sans qu'aucune commande le dise.

## Qui écrit, et quand

**L'utilisateur, à sa demande, et personne d'autre.** Aucune étape du pipeline n'ajoute d'entrée :
ni l'orchestrateur, ni l'auditeur, ni un audit intermédiaire. C'est ce qui sépare cette liste du
registre de dette, alimenté une fois par chantier à la clôture.

> *Mode de défaillance* — une road-map qu'un agent alimente tout seul se remplit d'idées que
> personne n'a voulues, et devient le premier endroit qu'on cesse de lire. Une liste qu'on ne lit
> plus ne retient plus rien : c'est exactement ce qu'elle existait pour éviter.

## Comment on en sort

Par un `list-dir move`, jamais par un champ — l'état est porté par le répertoire, pour la raison
donnée au registre de dette ([Un état, pas un journal](dette.md#un-état-pas-un-journal)). Deux
sorties, et elles ne se déclenchent pas de la même façon :

**À la clôture d'un chantier**, quand le suivi porte un `road-map:` — c'est-à-dire quand le chantier
est parti de cette entrée. L'orchestrateur déplace vers `road-map-fait/` et écrit la section
`Fait le`. Le geste est décrit là où il s'exécute : `cloture.md`, point 2.

**À la main**, quand l'utilisateur le demande : vers `road-map-ecarte/`, avec son motif. Aucune
preuve exécutée n'y est exigée, contrairement à `technical-debt-ecarte/`. La raison tient en une
phrase : une dette est un constat, dont on peut établir par commande qu'il ne tient plus ; une tâche
à laquelle on renonce est une **décision**, et aucune commande ne l'établit. Exiger une preuve ici
n'en produirait pas — elle produirait de la preuve creuse, qui se lit comme une vérification.

Un chantier **abandonné** ne fait rien sortir : la tâche n'a pas été faite, et l'abandon est
précisément ce qui la remet en attente.

## Le champ `road-map:`

Quand un chantier part d'une entrée, le suivi porte son `id` — [Frontmatter](contrat.md#frontmatter)
en donne la forme. Deux conséquences qui ne se devinent pas :

- **C'est l'`id`, pas un chemin.** Un `id` ne se renomme jamais
  ([Un élément](../../list-dir/references/format.md#un-élément)), donc la citation reste vraie après
  le `move` vers `road-map-fait/`. Un chemin, lui, deviendrait faux au moment même de la sortie.
- **Il n'est pas réécrit à l'archivage**, contrairement à `plan`, `brief` et `audit` : il ne désigne
  pas un fichier qui bouge vers `done/`.

C'est ce champ, et lui seul, qui permet à la clôture de savoir quoi déplacer. Sans lui, l'entrée
reste dans `road-map/` — ce qui est le bon comportement par défaut, et non une panne.

## Le cas croisé

Une entrée de road-map qui référence une entrée de `technical-debt/`, quand le chantier solde la
dette : **deux listes bougent, par deux `move` indépendants**, et rien ne les couple.

```bash
list-dir move "$T/technical-debt" <id-dette> "$T/technical-debt-solde"
list-dir move "$T/road-map"       <id-tache> "$T/road-map-fait"
```

Chacun a sa propre condition : la dette sort sur la preuve exécutée de son solde
([Solder](dette.md#solder)), la tâche sort parce que le chantier l'a portée. Un chantier peut très
bien faire l'un sans l'autre — payer une dette qu'aucune entrée de road-map ne réclamait, ou
accomplir une tâche qui ne soldait aucune dette.

## Lecture

Rien ici n'est lu automatiquement par le pipeline, et aucune commande de revue ne la relit — c'est
la différence avec `technical-debt/`, que `/debt-review` confronte au dépôt entrée par entrée. Une
road-map se consulte à la main, typiquement en cherchant un sujet de chantier :

```bash
list-dir list "$T/road-map" --sort date
list-dir show "$T/road-map" <id>
```
