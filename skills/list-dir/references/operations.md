# Les opérations sur une liste

Ce que fait chaque commande qui lit ou modifie des éléments : `validate`, `migrate`, `fill`,
`toggle`, `move`, `list`, `derive`, `merge`. Le format qu'elles appliquent est décrit dans
[Le format d'une liste](../references/format.md) ; la surface Python qui les expose, dans
[Étendre `list-dir`](../references/extension.md).

---

## Ce que `validate` confronte au contrat

Un `Violation` par manquement, chacun nommant fichier, sujet et cause, dans cet ordre :

| Sujet | Sans `--filled` | Avec `--filled` |
|---|---|---|
| champ non déclaré au contrat | manquement | idem |
| champ requis absent | manquement | idem |
| `id` ≠ nom du fichier | manquement | idem |
| valeur mal typée, hors enum, date non ISO | manquement | idem |
| champ portant un marqueur de son type, ou le marqueur générique | légitime — le type n'est pas contrôlé | manquement si le champ est **requis** |
| champ portant le marqueur **d'un autre type** (`<OPTIONNEL int>` sur un `date`) | manquement | idem |
| section non déclarée au contrat | manquement | idem |
| section requise absente ou vide | manquement | idem |
| section requise au marqueur | légitime | manquement |
| champ ou section **facultatif** au marqueur | légitime | légitime — jamais réclamé |

Une liste **sans élément est conforme** : elle est légitimement vide au sortir d'`init`.

`validate` avertit par ailleurs sur stderr, sans jamais changer son code de retour :

- quand la semence d'une liste a évolué —
  [Ce que `validate` avertit](../references/provenance.md#ce-que-validate-avertit) ;
- pour chaque élément qui porte un marqueur générique sur un champ `int`, `date`, `bool` ou
  `list` : la note nomme la forme typée, et `migrate` la pose ;
- pour chaque élément qui porte un champ ou une section `deprecated`, avec la consigne du contrat.

Un champ ou une section `deprecated` n'est jamais réclamé, jamais signalé comme non déclaré, et son
type reste contrôlé quand un élément le porte.

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
| marqueur générique sur un champ `int`, `date`, `bool` ou `list` | converti en sa forme typée, **à statut égal** : `<À REMPLIR>` devient `<À REMPLIR date>` |
| champ ou section `deprecated`, absent | **non ajouté** |
| champ ou section `deprecated`, présent | gardé en place ; `--drop` ne le retire pas |
| ordre des champs ou des sections différent | repris de l'ordre du contrat |
| champ ou section que le contrat ne déclare plus | **conservé** et signalé ; `--drop` le retire |
| valeur déjà écrite | jamais touchée — un marqueur n'est pas une valeur écrite |

**Elle ne juge pas.** Elle ne renomme rien et ne reporte aucune valeur : décider qu'un champ
`severite` disparu est devenu `gravite` demande un contexte qu'aucun script n'a. C'est le partage
du dispositif — la structure au script, le jugement au modèle. La conservation par défaut suit la
même règle : supprimer une donnée que personne n'a relue serait un jugement.

**Rejouable.** Une liste déjà conforme ne fait toucher aucun fichier. `--dry-run` montre le plan
sans rien écrire — et n'exécute **aucune** `command` de contrat : il la nomme (« ajouté, sortie de
« date +%F » ») au lieu de citer sa valeur, parce qu'un mode d'essai qui exécute le shell d'un
contrat ne promet plus rien. Contrepartie assumée : une `command` qui échouerait passe l'essai sans
être signalée — on ne peut pas le savoir sans la jouer. Un `text`, littéral, est en revanche
confronté à son type dès le dry-run, qui refuse donc exactement ce que la migration refusera
([Préremplir un champ ou une section](../references/format.md#préremplir-un-champ-ou-une-section)).

Un élément modifié voit son front matter **reprojeté**, jamais reformaté : seuls les champs dont la
valeur change sont réécrits, et `Item.realigned` retire et réordonne SUR le document d'origine, là
où `with_fields` ne sait que fusionner. Tableaux mis en forme sur plusieurs lignes, guillemets et
commentaires survivent donc à une migration qui ne portait pas sur eux — un champ retiré emportant
seulement le commentaire qui le précédait, sa légende.

Une remarque seule — un champ conservé — ne déclenche pour autant **aucune** écriture. Le rendu
serait aujourd'hui identique à l'octet, mais réécrire un fichier que rien n'oblige à changer lui
donne une date de modification neuve, et fait apparaître dans `git status` des éléments qu'aucune
migration n'a touchés.

Enfin, une migration réécrit du contenu : son commit ne doit jamais être mêlé à un `move`, pour la
raison dite plus bas.

## Remplir ce que `migrate` laisse au Marqueur

`migrate` pose un champ neuf au Marqueur dans chaque élément, et ne le remplit jamais. Quand la
valeur est connue — la même pour tous, ou choisie élément par élément —, `fill` l'écrit :

```bash
list-dir fill <liste> <champ> <valeur> (--id <id>… | --all) [--override] [--dry-run]
```

| Cas | Ce que fait `fill` |
|---|---|
| champ au Marqueur, requis ou facultatif, générique ou typé | la valeur est posée |
| champ déjà rempli, ou absent de l'élément, avec `--all` | élément **sauté** |
| champ déjà rempli, ou absent, avec `--id` | **échec** nommant l'élément, rien n'est écrit |
| `--id` qui ne nomme aucun élément | échec, rien n'est écrit |
| ni `--id` ni `--all`, ou les deux | erreur d'appel, code 2 |
| valeur que le type refuse : hors `values`, date non ISO, `bool` autre que `true`/`false` | échec, rien n'est écrit |
| valeur qui est elle-même un Marqueur | échec : un Marqueur ne remplit rien |
| champ non déclaré, ou `deprecated` | échec |
| champ déjà rempli, avec `--id --override` | la valeur est **réécrite** ; identique, aucun fichier touché |
| `--override` avec `--all`, ou sans `--id` | erreur d'appel, code 2, rien n'est écrit |
| `--override` sur un champ `list`, sur `id`, ou absent de l'élément | échec, rien n'est écrit |

**La valeur est convertie comme un `text` de contrat** : `false` s'écrit en booléen, `3` en entier,
`2026-10-07` en date nue — par la même conversion, qui accepte et refuse les mêmes formes
([Préremplir un champ ou une section](../references/format.md#préremplir-un-champ-ou-une-section)).
Un champ `list` ne se remplit pas ainsi.

**Toute la liste se demande, par `--all`** : un `--id` oublié ne doit pas poser sur chaque élément
une valeur pensée pour un seul. `--id` se répète pour en désigner plusieurs.

**Avec `--id`, l'appelant a désigné l'élément** : le sauter en silence lui ferait croire la valeur
posée. Tout est vérifié avant la moindre écriture, et le front matter est reprojeté comme par
`migrate` : le diff ne montre que la ligne du champ.

**Rejouable.** Rien à remplir ne fait toucher aucun fichier ; une écriture interrompue se reprend en
relançant le même appel, qui saute ce qu'il a déjà posé. `--dry-run` montre ce qui serait rempli.

`fill` ne juge pas plus que `migrate` : la valeur vient de l'appelant. Il évite seulement d'éditer
à la main chaque fichier, et donne à un agent un moyen d'écrire qui ne touche que le champ visé.

**`--override` réécrit une valeur écrite, et se demande.** Il lève le seul refus de `--id` devant
un champ rempli : le contrôle de type, la reprojection du front matter et la vérification de tout
avant la première écriture restent ceux de `fill`. Il exige `--id` : réécrire toute une liste ne se
fait pas par omission. Une valeur identique à celle qui est écrite ne touche aucun fichier, et la
commande le dit. `id` vaut le nom du fichier, un champ `list` n'a pas de valeur que `<valeur>` dise,
et un champ absent se pose par `migrate` : `--override` les refuse. `agents/migrateur-de-liste.md`
n'emploie pas `--override` : il ne remplit que des Marqueurs.

## Basculer un booléen

Un `pin` ou un `archive` se bascule sans que l'appelant lise la valeur pour dire la contraire :

```bash
list-dir toggle <liste> <champ> --id <id>… [--dry-run]
```

`toggle` est `fill --override` pour un `bool` : il inverse la valeur écrite, et la passe par le
même contrôle de type et le même chemin d'écriture. Le diff ne montre que la ligne du champ.

| Cas | Ce que fait `toggle` |
|---|---|
| `bool` écrit, `true` ou `false` | la valeur est inversée |
| `bool` resté au Marqueur, ou absent de l'élément | échec nommant l'élément, rien n'est écrit |
| champ d'un autre type, non déclaré ou `deprecated` | échec, rien n'est écrit |
| `--id` qui ne nomme aucun élément | échec, rien n'est écrit |
| `--all`, ou pas de `--id` | erreur d'appel, code 2 : inverser toute une liste n'a pas de sens |

`--id` se répète. Tout est vérifié avant la moindre écriture, et `--dry-run` montre ce qui serait
basculé.

## Déplacer un élément

**`move` est un renommage pur** — `git mv`, et rien d'autre. Git ne stocke pas les renommages :
il les *déduit* de la similarité des contenus. Réécrire le fichier dans le même commit fait tomber
cette déduction sous son seuil, et l'historique montre alors une suppression suivie d'une création
— `git log --follow` s'arrête là, et ne remonte qu'au commit mêlé. Ce qui accompagne un déplacement
va donc dans un **second commit**.

Ce que le contrat d'arrivée exige en plus est rappelé **sur stderr** ; stdout ne porte que le
chemin d'arrivée, pour qu'un script puisse le lire sans le démêler d'un commentaire.

## Lister et filtrer

**Le format de sortie de `list`** est une ligne par élément : l'id, puis les champs nommés à
`--sort`, séparés par une espace. Il se lit dans un `while read`, se compte au `wc -l`, se coupe
au `cut`. `--where` est répétable et les critères se cumulent ; il porte sur les champs déclarés,
jamais sur le texte. Un filtre qui ne rend rien produit **zéro octet et le code 0** : c'est une
réponse, pas une erreur — contrairement à `merge`, qui perdrait un élément.

**`--sort a,-b` ordonne selon le type déclaré**, un `-` en tête de champ inversant son sens. Le `-`
se colle à l'option, `--sort=-b` : `argparse` prend `--sort -b` pour une option. Un `int` se trie en
nombre (9 avant 10), un `enum` dans l'ordre de ses `values`, un `bool` faux avant vrai, une `date`
et un texte en chaîne. Trois groupes se rangent dans cet ordre : les valeurs conformes au type, puis
les valeurs non conformes (en texte), puis les champs absents ou restés au marqueur — ces deux
derniers groupes en fin quel que soit le sens, et sans jamais faire lever le tri. `--where` compare
un `bool` à `true` ou `false`, et `list` les écrit de même.

## Listes dérivées

`derive` **projette la structure** d'une liste sur une liste neuve. Le patron vit dans la liste
source, sous `.list/patrons/`, et va par paire :

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
description = ""
from = "title"        # repris de l'élément source

[fields.verdict]
type = "enum"
required = true
description = ""
values = ["retenu", "écarté"]
                      # pas de `from` : posé au marqueur, c'est au modèle de trancher
```

L'`id` est reporté d'office — c'est le seul lien entre une fiche dérivée et son élément d'origine.
`derive` ne transforme, ne concatène et ne calcule rien : un champ nommé par `from` est recopié, un
champ sans `from` reçoit le marqueur de son statut, et les sections viennent du patron `.md`, pas
du contrat.

Tout est construit **en mémoire avant la moindre écriture** : un patron incohérent ne laisse
aucune destination à moitié bâtie, qu'une seconde tentative refuserait comme « existe déjà ».

**La dérivée reçoit son estampille du patron**, comme toute liste reçoit la sienne de sa semence :
`derive` recopie le `<nom>.toml` verbatim, et n'écrit pas une ligne de `[origin]`. Un patron qui
porte la table sème donc une liste qui sait d'où elle vient, sous la forme `mère/dérivée`
([`def` prend deux formes](../references/provenance.md#def-prend-deux-formes-et-la-seconde-nomme-un-patron)) ;
un patron muet sème une liste muette, à qui `validate` réclamera une adoption.

**`derive` n'écrit pas de `.list/semence/`.** Une liste dérivée est gelée par convention, et une
liste gelée n'a rien à rattraper : le point de référence d'un `reseed` qui n'aura jamais lieu ne
serait qu'une copie de plus à tenir à jour. C'est aussi pourquoi la version d'un patron ne se
compare à rien — ce que `validate` dit plutôt que de le taire.

**`derive` projette, `move` déplace.** `move` fait changer un fichier de liste — `git mv`,
l'historique suit, l'élément reste le même. `derive` crée un second fichier à côté du premier, sans
lien Git, relié seulement par l'`id`.

## Agglomérer

| Niveau | Contenu |
|---|---|
| `#` | préambule : nom de la liste, date, **compte des éléments face au compte du répertoire** |
| `##` | un élément — son `title`, ou son `id` à défaut |
| `###` | les sections de l'élément, décalées d'un niveau |

Le décalage n'est pas cosmétique : les sections d'un élément sont des `##` dans son fichier. Sans
lui, compter les `##` du document aggloméré compterait les sections en plus des éléments, et le
contrôle de conservation ne voudrait plus rien dire.

**`merge` recompte sur le document rendu**, pas sur la liste qui a servi à l'écrire — compter deux
fois la même variable ne prouverait rien. Un `title` contenant une ligne « ## … » ajouterait sinon
un faux élément au document : le recomptage le refuse, en nommant l'écart. Le compte est fait
**hors blocs de code**, par la même règle que le découpage en sections : un `## ` collé dans une
sortie de commande est du contenu.

> Un `grep -c '^## '` lancé à la main sur l'aggloméré ne donne donc **pas** le compte des éléments
> dès qu'une section porte un bloc de code — il compte aussi les `## ` qui s'y trouvent. Le compte
> qui fait foi est celui du **préambule**, écrit par `merge` après vérification.

`merge` exige `--filled` et omet les sections restées au marqueur facultatif —
[Les marqueurs](../references/format.md#les-marqueurs).
