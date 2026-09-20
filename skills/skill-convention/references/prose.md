# La prose d'une skill et des fichiers qu'elle produit

Une section par convention : la règle, ce qu'elle évite, et au moins un endroit du dépôt où on
la voit à l'œuvre. Une règle qui a son autorité ailleurs n'est pas
réécrite ici : la section y mène.

Les trois premières sections portent le principe directeur du `SKILL.md` — réduire le
non-déterminisme du modèle.

---

## Un document structuré se pose depuis un gabarit

Un fichier qu'on écrira plusieurs fois — un suivi, un brief, un rapport — a un contrat, et
[gabarit](../../gabarit/SKILL.md) le pose depuis ce contrat : la commande construit la structure,
le modèle remplit le contenu, la commande revérifie. Un modèle qui construit aussi la structure
produit deux fichiers différents pour le même besoin, et l'écart ne se voit qu'à la lecture.

Un gabarit se nomme par sa semence, jamais par un chemin ; la semence est le seul endroit où la
structure est écrite.

**Pratiqué dans** : [gabarit](../../gabarit/SKILL.md) et ses semences `brief` et `suivi`
([`gabarit/suivi/contract.toml`](../../gabarit/gabarit/suivi/contract.toml)), posées et vérifiées
par [intent-brief](../../intent-brief/SKILL.md) et
[implementation-tracker](../../implementation-tracker/SKILL.md) ;
[debt-review](../../debt-review/references/gabarit-rapport.md) pour son rapport de revue.

## Une mémoire se tient en registre

Ce qui doit être relu, filtré, compté ou déplacé au fil du temps est une liste de fichiers tenue
par [list-dir](../../list-dir/SKILL.md) : un répertoire est une liste, un fichier un élément, un
contrat embarqué déclare la structure et `list-dir validate` la vérifie. Une mémoire en prose
libre ne se filtre pas, ne se compte pas, et se relit en entier à chaque consultation.

Un état se change en déplaçant l'élément d'une liste à l'autre, jamais en éditant un champ à la
main.

**Pratiqué dans** : le [registre de dette](../../implementation-tracker/references/dette.md) et
la [road-map](../../implementation-tracker/references/road-map.md), sous
`.claude/implementation/todo/` ; [debt-review](../../debt-review/SKILL.md), qui dérive sa liste de
revue du registre.

## Le frontmatter porte les données mutables

Ce qui change au fil d'un chantier — statut, session, branche, chemins, dates — vit dans le
frontmatter, pas dans la prose. Il se lit et s'écrit sans relire le texte, et sans risquer de le
réécrire ; une commande peut le lire. Une donnée mutable noyée dans un paragraphe oblige à
reformuler la phrase pour la mettre à jour, et deux phrases finissent par se contredire.

Champs, valeurs et défauts des fichiers du pipeline :
[Frontmatter](../../implementation-tracker/references/contrat.md#frontmatter).

**Pratiqué dans** : les fichiers de suivi de `.claude/implementation/` ; le frontmatter `name` /
`description` de toute skill, seule chose que le modèle voit avant de la déclencher.

---

## Le SKILL.md oriente, les références détaillent

Le `SKILL.md` dit ce que fait la skill, quand, et où lire la suite. Le détail d'une procédure,
d'un format ou d'une règle vit dans `references/`, un fichier par sujet. Un `SKILL.md` qui porte
tout se charge en entier à chaque déclenchement, et le lecteur y cherche la seule procédure dont il
a besoin au milieu de celles dont il n'a pas besoin.

**Pratiqué dans** : [git-smart-commit](../../git-smart-commit/SKILL.md), qui tient en une table
d'orientation ; [list-dir](../../list-dir/SKILL.md) et ses cinq références.

## Lire une référence au moment d'en avoir besoin

Le `SKILL.md` dit **quand** lire chaque référence, et le dit comme une consigne : « lire celui du
type demandé, et lui seul », « à lire au moment de créer le fichier, pas avant ». Une référence
lue d'avance occupe le contexte pendant toute la procédure, et une référence dont le moment n'est
pas dit est lue d'avance par prudence.

**Pratiqué dans** : [git-smart-commit](../../git-smart-commit/SKILL.md) ;
[implementation-tracker](../../implementation-tracker/SKILL.md), dont l'Étape 5 ne fait lire
`references/cloture.md` qu'à la clôture.

## Une règle, un seul endroit

Une règle est écrite dans un fichier d'autorité ; ailleurs, un renvoi. La ligne de partage : le
fichier d'autorité porte la règle et son motif, la skill qui l'applique garde sa consigne
opératoire — ce qu'il faut faire à cet endroit-là —, et une prose qui porte du jugement n'est
jamais remplacée par un lien. Une même règle écrite en plusieurs endroits finit par donner des
réponses contradictoires, et aucun lecteur ne sait laquelle fait foi.

[`check_pipeline.py`](../../../scripts/check_pipeline.py) vérifie cette unicité pour les règles du
contrat du pipeline ; les autres ne sont vérifiées par rien.

**Pratiqué dans** : [le contrat du pipeline](../../implementation-tracker/references/contrat.md),
auquel les autres skills du pipeline renvoient ;
[git-smart-commit](../../git-smart-commit/SKILL.md), section « Ce qui vaut pour tous les types ».

## Un renvoi est un lien relatif, ancre comprise

Une skill en cite une autre par un lien Markdown relatif — `../<skill>/references/<fichier>.md`,
suivi de l'ancre de la section visée. Le lien relatif résout où que le dépôt soit installé ;
l'ancre dépose le lecteur sur la règle au lieu du haut d'un fichier de plusieurs centaines de
lignes. Un intitulé de section renommé casse les ancres qui le visent : `check_pipeline.py` les
contrôle, et c'est ce contrôle qu'il faut relancer après un renommage.

Ancrer un chemin sur le `HOME` est refusé, pour la raison que donne
[l'outillage du dépôt](../../../OUTILLAGE.md).

**Pratiqué dans** : [intent-brief](../../intent-brief/SKILL.md), dont chaque renvoi au contrat
porte son ancre ; [debt-review](../../debt-review/SKILL.md).

## Un exécutable s'appelle par son nom

Règle et motif : [l'outillage du dépôt](../../../OUTILLAGE.md), qui en est l'autorité. En
écrivant une skill, cela veut dire : une commande citée dans un bloc de code l'est par le nom de
son lien dans `bin/`, jamais par son chemin. Une commande propre à un projet suit
[les commandes locales](commandes-locales.md).

**Pratiqué dans** : [gabarit](../../gabarit/SKILL.md) (« `gabarit` est un lien de `bin/` ») ;
[list-dir](../../list-dir/SKILL.md).

## La description dit quoi, quand, et ce que la skill ne fait pas

Le champ `description` du frontmatter est tout ce que le modèle voit avant de déclencher la
skill. Il dit ce qu'elle fait, puis quand elle se déclenche (« Se déclenche dès que… »), puis sa
limite, en une phrase négative (« Ne juge aucun contenu. »). Sans la limite, la skill se déclenche
sur des demandes voisines qu'elle ne sait pas traiter.

Une skill qui ne doit jamais partir d'elle-même porte `disable-model-invocation: true` **et** le
dit dans sa description (« Skill exclusivement manuelle »), avec son `argument-hint`.

**Pratiqué dans** : [gabarit](../../gabarit/SKILL.md), [list-dir](../../list-dir/SKILL.md) ;
[debt-review](../../debt-review/SKILL.md) et
[implementation-tracker](../../implementation-tracker/SKILL.md) pour les skills manuelles.

## Les scripts font la structure, le modèle fait le jugement

Tout ce qui est mécanique — créer, compter, déplacer, valider, agglomérer — est une commande. Le
modèle remplit, juge et corrige le contenu, directement dans le fichier ; la commande repasse
après. Une opération mécanique confiée au modèle se fait à la main, et une perte n'y est signalée
par rien.

La skill énonce ce partage en toutes lettres, et sa description dit ce que la commande ne fait
pas.

**Pratiqué dans** : [list-dir](../../list-dir/SKILL.md) et [gabarit](../../gabarit/SKILL.md),
« Partage des rôles » ; [debt-review](../../debt-review/SKILL.md).

## Les codes de sortie sont dits

Une commande documente ses codes : **0** succès, la valeur seule sur stdout ; **1** refus ou
échec, message sur stderr ; **2** erreur d'appel. Un avertissement sort sur stderr sans changer le
code. Un appelant qui ne connaît pas les codes lit la sortie, et une sortie vide sous un code 0 se
lit comme un succès.

**Pratiqué dans** : [gabarit](../../gabarit/SKILL.md) ;
[list-dir](../../list-dir/references/definitions.md).

## Chaque règle porte son motif, dans la prose

Une règle s'écrit avec ce qu'elle évite : le mode de défaillance, c'est-à-dire ce qui arrive,
concrètement, quand on ne la suit pas. Il s'écrit **dans le corps du texte**, à la suite de la
règle ou dans l'exemple qui l'illustre, et non dans un bloc cité à part. Une règle sans motif se
contourne dès qu'elle gêne, parce que rien ne dit ce qu'on risque.

Les blocs cités `> *Mode de défaillance* —` qui subsistent dans le dépôt sont des écarts à cette
convention.

**Pratiqué dans** : [list-dir](../../list-dir/references/format.md) et ses autres références,
réécrites sous cette forme.

## Un outil de vérification échoue fermé, un rappel échoue ouvert

Un script qui vérifie sort en échec dès qu'un contrôle échoue — **et dès qu'un contrôle n'a rien
examiné** : un garde-fou silencieusement vide passe pour un garde-fou qui a tout vu. Un script qui
rappelle ou informe, un hook `SessionStart` par exemple, sort en 0 quoi qu'il arrive : il n'a
jamais de raison d'empêcher le démarrage d'une session. L'en-tête du script dit lequel des deux
il est.

**Pratiqué dans** : [`check_pipeline.py`](../../../scripts/check_pipeline.py) (fermé) ;
[`outillage-rappel.sh`](../../../hooks/outillage-rappel.sh) (ouvert).

## Une date se lit, elle ne s'écrit pas de mémoire

Règle et motif : [Dates et listing](../../implementation-tracker/references/contrat.md#dates-et-listing).

**Pratiqué dans** : [intent-brief](../../intent-brief/SKILL.md), Étape 0.

## Un sous-agent recopie ses règles

Exception à « une règle, un seul endroit » : un agent de `agents/` se charge dans sa propre
fenêtre, sans suivre les renvois, et sans recevoir les hooks de la session. Les règles qui le
concernent y sont donc écrites en dur. C'est la seule recopie admise, et elle est bornée aux
règles dont l'agent a besoin.

**Pratiqué dans** : [`step-implementer.md`](../../../agents/step-implementer.md) ; l'exception est
déclarée en tête de [`check_pipeline.py`](../../../scripts/check_pipeline.py).

## Une phrase déclare, elle ne raconte pas

Une skill s'écrit au présent, en phrases déclaratives : elle dit ce qu'elle fait, ce qu'on fait,
et pourquoi. Elle ne raconte ni son origine, ni le constat qui l'a fait naître, ni ce qui se
faisait avant elle : ce récit va dans le message de commit. Chaque phrase porte une règle, un
motif ou une consigne ; une phrase qui n'en porte aucune est retirée, formule frappante comprise.
Une phrase de récit se charge à chaque déclenchement sans rien apprendre au modèle, et un
« jusqu'ici » lui laisse croire que deux régimes coexistent.

Ce paragraphe raconte :

```
Les conventions de ce dépôt se lisaient jusqu'ici dans les skills elles-mêmes : chacune en
pratique une partie, aucune ne les énonce. Ce skill les énonce, et **chacune cite un endroit du
dépôt où elle est pratiquée** — une convention qu'on ne retrouve nulle part est un vœu, pas une
convention.
```

Il déclare :

```
Ce skill énonce les conventions du dépôt. Chacune cite un endroit du dépôt où elle est pratiquée.
```

**Pratiqué dans** : ce fichier ; [skill-convention](../SKILL.md), « Ce skill décrit, il ne
corrige pas ».

## La prose est en français

Français correct, accents compris ; identifiants, commandes et termes techniques restent dans
leur forme d'origine. Les noms de fichiers, de sections et de slugs sont en français sans
accents quand ils servent d'identifiants.

**Pratiqué dans** : [implementation-tracker](../../implementation-tracker/SKILL.md),
[list-dir](../../list-dir/SKILL.md) ; slugs de `.claude/implementation/todo/technical-debt/`.
