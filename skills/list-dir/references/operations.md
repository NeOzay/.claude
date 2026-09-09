# Les opérations sur une liste

Ce que fait chaque commande qui lit ou modifie des éléments : `validate`, `migrate`, `move`,
`list`, `derive`, `merge`. Le format qu'elles appliquent est décrit dans
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
| champ portant un marqueur | légitime — le type n'est pas contrôlé | manquement si le champ est **requis** |
| section non déclarée au contrat | manquement | idem |
| section requise absente ou vide | manquement | idem |
| section requise au marqueur | légitime | manquement |
| champ ou section **facultatif** au marqueur | légitime | légitime — jamais réclamé |

Une liste **sans élément est conforme** : elle est légitimement vide au sortir d'`init`.

`validate` avertit par ailleurs sur stderr quand la semence d'une liste a évolué, sans jamais
changer son code de retour — [Ce que `validate` avertit](../references/provenance.md#ce-que-validate-avertit).

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
| ordre des champs ou des sections différent | repris de l'ordre du contrat |
| champ ou section que le contrat ne déclare plus | **conservé** et signalé ; `--drop` le retire |
| valeur déjà écrite | jamais touchée |

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
raison dite juste en dessous.

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

## Listes dérivées

`derive` **projette la structure** d'une liste sur une liste neuve. Le gabarit vit dans la liste
source, sous `.list/templates/`, et va par paire :

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
champ sans `from` reçoit le marqueur de son statut, et les sections viennent du gabarit `.md`, pas
du contrat.

Tout est construit **en mémoire avant la moindre écriture** : un gabarit incohérent ne laisse
aucune destination à moitié bâtie, qu'une seconde tentative refuserait comme « existe déjà ».

**La dérivée reçoit son estampille du gabarit**, comme toute liste reçoit la sienne de sa semence :
`derive` recopie le `<nom>.toml` verbatim, et n'écrit pas une ligne de `[origin]`. Un gabarit qui
porte la table sème donc une liste qui sait d'où elle vient, sous la forme `mère/dérivée`
([`def` prend deux formes](../references/provenance.md#def-prend-deux-formes-et-la-seconde-nomme-un-gabarit)) ;
un gabarit muet sème une liste muette, à qui `validate` réclamera une adoption.

**`derive` n'écrit pas de `.list/semence/`.** Une liste dérivée est gelée par convention, et une
liste gelée n'a rien à rattraper : le point de référence d'un `reseed` qui n'aura jamais lieu ne
serait qu'une copie de plus à tenir à jour. C'est aussi pourquoi la version d'un gabarit ne se
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
