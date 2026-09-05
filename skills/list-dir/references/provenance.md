# Provenance et péremption

Une liste semée porte une copie du contrat, et cette copie est la seule règle appliquée
([La définition n'est autorité que le temps de l'`init`](../references/definitions.md#la-définition-nest-autorité-que-le-temps-de-linit)).
Une skill qui écrit dans cette liste suppose pourtant qu'elle vaut sa semence — et le jour où la
définition évolue, rien ne le disait. La table `[origin]` comble ce trou sans rendre à la définition
la moindre autorité.

```toml
[origin]
def = "technical-debt"   # le nom de la définition, ou false : cette liste n'a pas de semence
version = 3              # entier >= 1, obligatoire dès que `def` est un nom
frozen = false           # facultatif — cette liste a délibérément pris la main
```

**`init` n'écrit jamais cette table, il la reçoit.** Elle vit dans le contrat de la définition, et
la copie l'emporte avec le reste : c'est ce qui garde une liste octet pour octet égale à sa
semence, et ce qui fait qu'`init --from <chemin>` estampille exactement comme `init --def <nom>`.
Une estampille que `init` écrirait d'après ce qu'on lui a tapé nommerait la définition **visée**,
pas celle qui a réellement semé — et c'est la même raison qui fait refuser en code 2 un
`--def <nom>` posé sur une semence déclarant un autre nom.

**`def` nomme, il ne localise pas.** Un chemin dépend de la machine ; deux machines rendraient deux
contrats, ce que la résolution par rangs existe pour éviter. `reseed` rerésout ce nom le jour venu,
et `reseed --from <chemin>` reste la porte de sortie quand la définition n'est installée nulle part.

**Une liste sans semence le déclare** : `def = false`, ce que le squelette d'`init` porte d'emblée.
Une liste née à la main n'a rien à rattraper, et l'absence de réponse se distingue de la réponse
« aucune ».

---

## `def` prend deux formes, et la seconde nomme un gabarit

Une liste engendrée par `derive` n'est pas semée par une définition : sa semence est le **gabarit**
`<nom>.toml` d'une définition. `def` le dit sous la forme `mère/dérivée` :

```toml
[origin]
def = "technical-debt/review"   # le gabarit « review » de la définition « technical-debt »
version = 1                     # celle du GABARIT, sans rapport avec celle de sa définition
frozen = true                   # la norme d'une liste jetable — voir plus bas
```

| Forme | Ce qu'elle nomme | Ce qu'on peut en faire |
|---|---|---|
| `technical-debt` | une définition, cherchée dans les quatre rangs | `init --def`, `reseed --def`, `contract --def` |
| `technical-debt/review` | le gabarit `review` de cette définition | **rien** : elle se lit, elle ne se résout pas |

**Le nom composite DIT, il ne résout pas.** `--def technical-debt/review` est refusé en le disant :
un gabarit ne s'amorce ni ne se rattrape, il projette une liste qui existe déjà. Ce qu'il donne au
lecteur, c'est de quoi retrouver la semence sans la chercher —
`list-dir contract --def technical-debt --template review` l'imprime, et les deux moitiés du nom
sont exactement les deux arguments à taper.

Sans cette forme, la seule façon de faire taire l'avertissement d'adoption sur une liste dérivée
serait `def = false`, c'est-à-dire lui faire déclarer qu'elle n'a pas de semence. Elle en a une ;
ce serait un mensonge, et il effacerait la seule trace du gabarit qui l'a produite.

**Deux segments, pas trois**, chacun non vide et différent de `.` et `..` — les gabarits vivent à
plat dans `templates/`. La forme est vérifiée à la lecture du contrat, sans rien ouvrir : une
estampille se relit sur une machine où la définition n'est pas installée, et une forme qu'on ne
jugerait qu'à l'ouverture ne s'y jugerait jamais. Un `def = "technical-debt/revue"` fautif
échouerait sinon en silence — le gel tait la péremption, et `reseed` n'est jamais appelé sur une
liste jetable.

**`frozen = true` est la norme d'une liste dérivée**, et c'est le gabarit qui le déclare, comme il
déclare le reste de l'estampille. Une liste de revue est dérivée, instruite, agglomérée puis
archivée : il n'y a rien à y rattraper, et une liste qu'on ne rattrapera jamais n'a pas à s'entendre
rappeler qu'elle pourrait l'être. Sur une dérivée qu'on aurait dégelée à la main, `validate` dit que
la péremption d'un gabarit **n'est pas suivie** — plutôt que de le chercher dans les rangs, où il
n'a jamais été.

## Ce que `validate` avertit

Les avertissements sortent sur **stderr**, sur un succès comme sur un échec, et ne changent jamais
le code de retour. Une liste dont la semence a évolué n'a aucun élément fautif : ses éléments
suivent le contrat qu'elle porte, et c'est celui-là que les commandes appliquent.

| État | Ce qui est dit |
|---|---|
| pas de table `[origin]` | aucune provenance déclarée, et le geste d'adoption |
| `def = false` | rien |
| `frozen = true` | rien |
| `def` nomme un gabarit (`mère/dérivée`) | la péremption d'un gabarit n'est pas suivie, et le `contract --def … --template …` qui imprime la semence |
| définition introuvable dans les quatre rangs | péremption invérifiable, avec le nom cherché |
| semence sans `[origin]`, ou illisible | dit avec le fichier fautif |
| version de la semence plus haute | « contrat périmé — semé en v2, en v5 », et `reseed` |
| version de la semence plus basse | état anormal, dit tel quel |
| contrat ou gabarit modifié depuis le semis | fichier par fichier |

La dernière ligne se lit dans `.list/semence/` et **ne résout aucune définition** : elle vaut encore
là où le skill qui porte la définition n'est pas installé. Sans ce répertoire — liste adoptée, ou
semée avant lui — on se tait sur ce point, jamais sur la péremption.

## `reseed` : rattraper sur ordre

```bash
list-dir reseed <liste>                    # la semence que la liste déclare
list-dir reseed <liste> --def <nom>        # ... ou celle-là, résolue dans les rangs
list-dir reseed <liste> --from <chemin>    # ... ou celle-là, telle quelle
list-dir reseed <liste> --dry-run          # ce qui serait fait, sans rien écrire
list-dir reseed <liste> --force            # passe outre un gel, et RIEN D'AUTRE
```

La fusion se fait **à trois points** — la semence gardée, le contrat local, la semence courante — et
la règle est *qui a bougé*, jamais une préséance :

| Situation | Issue |
|---|---|
| le local n'a pas bougé | la semence gagne |
| la semence n'a pas bougé | le local reste, sans un mot |
| les deux ont bougé sur la même clé | **conflit** — rien n'est écrit, les clés sont nommées |
| la semence a retiré une clé | **gardée**, comme `migrate` |
| le local a retiré une clé | **laissée supprimée** — une absence gagne comme une valeur |

Sans la semence gardée, il n'y a pas de troisième point : une clé qui diffère ne dit plus lequel des
deux côtés a bougé, et la moindre reformulation de description dans la définition se lirait comme
un conflit.

**Seul ce que le re-semis fait est rapporté.** Une clé gardée, une clé laissée supprimée : ce sont
des états, identiques au prochain appel, et `validate` les dit une fois — le contrat diffère de sa
semence — au lieu que `reseed` les rejoue indéfiniment sous le nom de « changement ». Un `reseed` qui
n'a rien à changer n'écrit rien non plus — **pas même la sauvegarde**, sans quoi un second appel
remplacerait `.list/backup/` par une copie de l'état courant en répondant « déjà à jour ».

L'avertissement « modifié localement » se juge sur le **contenu** du contrat, jamais sur ses
octets : un contrat réémis perd ses commentaires, et le comparer au texte ferait avertir pour
toujours une liste que personne n'a touchée. La décision de réécrire suit la même règle — un
commentaire ajouté sur place ne fait pas réécrire le contrat, donc ne se perd pas.

La granularité est la **clé TOML** (`fields.category.values`), pas le bloc `[fields.x]` : un conflit
sur une description n'emporte pas le type du champ avec lui. Les gabarits, eux, se comparent par
**fichier entier** — une prose libre n'a pas de clés à confronter.

**Ce qui ne s'écrit pas se refuse.** Un contrat qu'on ne peut pas réémettre — une valeur d'un type
hors contrat, un caractère de contrôle dans un titre de section — fait sortir `reseed` non nul en
nommant la clé fautive, avant toute écriture. Le sérialiseur est le même que celui des éléments, et
sa règle ne change pas parce qu'on écrit un contrat : ce qui ne se relit pas ne s'écrit pas.

**Un conflit ne se force pas.** `--force` dégèle une liste `frozen`, et c'est tout : trancher entre
deux versions d'une même clé appartient à qui a écrit l'une des deux. Sur un conflit, rien n'est
écrit — pas même la sauvegarde.

Quand rien n'a divergé, la semence est **recopiée verbatim**, commentaires compris : ils portent
souvent le pourquoi d'un champ. Le contrat n'est réémis qu'en cas de divergence réelle, et le
rapport dit alors que les commentaires de la version précédente sont dans `.list/backup/`.

`.list/backup/` est une marche arrière **locale** : un dépôt qui versionne ses listes gagne à
l'ignorer (`**/.list/backup/`), sans quoi chaque re-semis y ajoute un contrat périmé en double.
`.list/semence/`, lui, se versionne — c'est le point de référence, et il doit suivre le clone.

L'ordre d'écriture est **sauvegarde, contrat, semence rafraîchie**, et il n'est pas indifférent : la
sauvegarde d'abord parce qu'elle est la seule marche arrière, la semence en dernier parce que c'est
elle qui rend le geste idempotent.

`reseed` **ne touche pas aux éléments**. Un contrat rattrapé rend les éléments écrits avant lui non
conformes : `migrate` les remet en ligne, et c'est un second geste.

## Adopter une liste antérieure

Une liste écrite avant ce dispositif n'a pas d'`[origin]`, et `validate` le lui dit. `reseed --def
<nom>` l'adopte : les apports de la semence sont injectés, l'estampille est posée à la version
courante, et `.list/semence/` est créé. Sans point de référence, toute clé écrite des deux côtés à
deux valeurs différentes est un conflit — l'attribution est impossible, et la refuser vaut mieux
que la deviner.
