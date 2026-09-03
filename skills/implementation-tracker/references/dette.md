# Registre de dette technique

Trois **répertoires-listes**, sous `.claude/implementation/todo/` :

| Répertoire | Ce qu'il contient |
|---|---|
| `technical-debt/` | la dette constatée et non résolue |
| `technical-debt-solde/` | ce qui a été payé, avec la preuve qui l'établit |
| `technical-debt-ecarte/` | ce qui est sorti du registre **sans** avoir été payé, avec son motif |

Ce sont des répertoires-listes : toutes les manipulations passent par les commandes de `list-dir`,
et par elles seules. Structure, contrat, marqueurs, comportement des commandes :
[Répertoires-listes](../../list-dir/references/contrat-liste.md#structure-dun-répertoire-liste).

```bash
T=".claude/implementation/todo"
```

Ce que le pipeline exige de son environnement pour que ces commandes tournent — et ce qu'il advient
quand un outil déclaré manque : [Dépendances](contrat.md#dépendances).

**Les trois registres n'existent pas d'office dans un projet neuf.** Ils s'y amorcent depuis les
définitions que ce skill embarque sous `list-dir/`, résolues par leur nom :

```bash
T=".claude/implementation/todo"
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  list-dir init "$T/$l" --def "$l" || echo "ÉCHEC init : $l"
  list-dir validate "$T/$l"        || echo "ÉCHEC validate : $l"
done
list-dir defs    # ce qui est définissable, et de quelle racine ça vient
```

Une fois amorcés, ils sont **détachés** de ces définitions : chaque registre porte sa propre copie
du contrat, seule appliquée, et rien ne le resynchronise. Un projet qui redéfinit un registre chez
lui a délibérément pris la main —
[Définitions de listes](../../list-dir/references/contrat-liste.md#définitions-de-listes).

Le pipeline produisait déjà des constats de dette — l'auditeur en fait un axe de jugement — mais
n'avait nulle part où les déposer : ils vivaient dans `<slug>.audit.md`, archivé en `done/` à la
clôture. Le registre est cet endroit.

---

## Un état, pas un journal

C'est la distinction dont tout le reste découle.

Le rapport d'audit **s'appende** : une section par audit, du plus ancien au plus récent
(`audit.md`, « Gabarit du rapport »). La répétition y est le format — elle date les constats et
montre ce qui avait déjà été signalé.

Le registre, lui, dit ce qui reste vrai **aujourd'hui**. Un constat qui y figure deux fois est un
doublon, et une entrée qu'un correctif a soldée n'a plus rien à y faire. D'où les deux règles qui
tiennent tout le dispositif :

- **Une seule écriture par chantier, à la clôture** (voir `cloture.md`). Pas au retour d'un audit
  intermédiaire : le même constat ressortirait à l'audit de clôture, qui rejuge le diff entier.
- **L'orchestrateur écrit, jamais l'auditeur.** L'auditeur tourne en contexte isolé, sans mémoire
  du passage précédent : il ne peut ni dédupliquer, ni retirer ce qui a été soldé entre-temps. Son
  contrat n'ouvre qu'un seul fichier en écriture, et ce n'est pas celui-ci.

Contrepartie assumée : c'est l'auteur du travail qui reporte ses propres dettes. Ce qui la rend
tenable est que chaque constat du rapport porte son `R<n>` — la complétude se vérifie après coup en
confrontant le rapport au registre.

**L'état est porté par le répertoire, jamais par un champ.** Une entrée soldée n'est pas une entrée
marquée soldée : c'est une entrée qui a changé de liste. Un champ `statut` autoriserait une entrée
payée à traîner dans le registre actif, ce que la ligne précédente interdit.

---

## Ce qui entre

Tout problème **non résolu** au moment de clore :

- les constats de la section « Dette induite » du rapport d'audit ;
- les réserves que l'utilisateur a choisi de clore avec plutôt que de traiter ;
- le hors-périmètre assumé au brief, quand c'est un problème qu'on a vu et laissé ;
- une étape retirée en cours de route, ou un contournement laissé en place.

**Ce qui n'entre pas :**

- les idées d'amélioration — le registre ne liste que du constaté, vérifié dans le dépôt. Elles
  iront dans une liste `road-map/`, à côté ;
- ce qui a été corrigé pendant le chantier : le rapport en garde la trace, pas le registre ;
- les préférences de style qu'aucun critère ne porte.

Le filtre à l'entrée est volontairement large : mieux vaut une entrée que l'utilisateur supprimera
qu'un problème qui disparaît avec la conversation. L'élagage est son geste, pas le nôtre.

---

## Ce qu'une entrée porte

**Le contrat de la liste fait foi.** Champs, sections requises et facultatives, valeurs admises
d'un `category` : il les déclare tous, et il se lit sans l'ouvrir.

```bash
list-dir contract "$T/technical-debt"       # le contrat EN VIGUEUR, tel qu'il s'applique
list-dir show "$T/technical-debt" <id>      # une entrée, telle qu'elle est écrite
list-dir validate "$T/technical-debt"       # toutes, confrontées au contrat
```

**Lire le contrat, jamais une copie de sa structure.** Ce fichier portait ici un tableau des champs
et une énumération des sections, recopiés à la main. Ils ont été retirés : deux écritures d'une même
chose finissent toujours par diverger, et c'est la copie en prose qu'on croit, parce qu'elle se lit
plus vite que le fichier qu'elle décrit.

Ce que ce fichier ne redit pas non plus, c'est le **contenu** attendu : les `description` du
contrat disent ce qu'il faut écrire dans chaque champ et chaque section — ce qu'une entrée sortie
du registre n'a plus à plaider, ou qu'une entrée sans `Pour solder` est un regret. Cela se lit là,
pas ici.

Ce que le contrat déclare sans pouvoir le motiver, en revanche, reste ici : **`Constat` est requis
jusque dans les listes de sortie** — sans lui, une entrée soldée ne dirait plus de quoi elle
parlait, et le registre des payées deviendrait une liste de dates.

> *Mode de défaillance* — un projet peut redéfinir sa liste (rang 1 des définitions, cf.
> [Définitions de listes](../../list-dir/references/contrat-liste.md#définitions-de-listes)). La
> prose décrirait alors le contrat *d'origine* pendant que l'outil en applique un autre, sans
> qu'aucune commande échoue. `list-dir contract` ne peut pas mentir : il imprime ce qui s'applique.

Ce qui suit n'est **pas** dans le contrat, et c'est pourquoi c'est écrit ici : les règles de tenue
que la structure ne sait pas porter.

**L'`id` ne se renomme pas.** Il est la seule identité d'un élément de liste
([Un élément](../../list-dir/references/contrat-liste.md#un-élément)) ; ce qui en découle ici,
c'est que par lui une entrée se cite, et sur lui que le point 3 d'*Alimenter* dédoublonne. Le
renommer ferait revenir le même constat comme s'il était neuf.

**Désigner sans numéro de ligne.** La description de `Constat` l'interdit ; ce que le contrat ne
peut pas dire, c'est quoi écrire à la place. Une entrée cite un fichier, une section, une phrase :
`` `cloture.md`, « toutes les étapes sont cochées » ``. La citation reste vraie tant que la règle
existe, et devient introuvable exactement quand elle disparaît — ce qui est précisément
l'information cherchée.

> *Mode de défaillance* — un numéro de ligne périmé ne casse rien de visible : il fait classer
> `non-pertinent` une dette vivante dont la relecture n'a pas retrouvé la cible. C'est la sortie de
> registre la plus facile à obtenir sur une preuve fausse.

---

## La dernière vérification, entrée par entrée

L'ancien registre portait **une** ligne « Dernière vérification » en tête de fichier. Elle a
disparu avec le fichier unique, et ce qui la remplace dit davantage : le champ `reviewed` de
**chaque** entrée, avec le `category` qui l'accompagne.

```bash
list-dir list "$T/technical-debt" --sort reviewed          # les moins récemment relues d'abord
list-dir list "$T/technical-debt" --where category=aggravee
```

Un registre dont on soupçonne qu'il est périmé ne se lit plus — c'est ce que l'ancienne ligne
protégeait. Une entrée dont `reviewed` est resté à `<OPTIONNEL>` n'a **jamais** été confrontée au
dépôt depuis son écriture, et le tri le montre sans qu'on ait à le croire sur parole.

---

## Alimenter — à la clôture

1. Relire le rapport d'audit **en entier**, toutes sections d'audit confondues, et parcourir ses
   `R<n>` un par un : traité pendant le chantier, ou survivant ? Seuls les survivants deviennent
   des entrées.

   **Le dernier audit ne suffit pas.** Rien n'oblige un auditeur à reprendre les réserves des
   passages précédents : il peut ne consigner que ses constats neufs, et une réserve non traitée
   de la première section disparaîtrait alors sans une seule erreur. Le rapport est un journal —
   c'est le fichier entier qui fait foi, pas sa dernière page.
2. Y ajouter ce que le rapport ne pouvait pas connaître — les arbitrages rendus après lui
   (« clore avec ces réserves »), le hors-périmètre assumé, ce qui a été laissé en route.
3. **Lire le registre avant d'écrire.** Un constat déjà présent ne se duplique pas : le compléter,
   en gardant sa date d'origine. C'est le seul contrôle qui empêche le registre de gonfler.

   ```bash
   list-dir list "$T/technical-debt" --sort date
   ```
4. Créer une entrée par survivant, et **remplir le fichier créé** :

   ```bash
   list-dir new "$T/technical-debt" <id>
   ```
5. **Vérifier avant de clore**, et pas seulement la structure :

   ```bash
   list-dir validate "$T/technical-debt" --filled
   ```

**Le contrat a changé depuis la dernière écriture** et les entrées existantes ne lui correspondent
plus : `list-dir migrate` les remet en ligne. Ce qu'il fait, ce qu'il ne fait pas, et pourquoi le
renommage d'un champ reste à la main :
[Quand le contrat change](../../list-dir/references/contrat-liste.md#quand-le-contrat-change).

---

## Solder

Une entrée soldée **change de liste**. Elle n'est ni barrée, ni marquée : elle sort du registre
actif, qui reste ainsi la liste de ce qui reste à faire.

```bash
list-dir move "$T/technical-debt" <id> "$T/technical-debt-solde"
```

Le déplacement préserve l'historique de l'entrée, jusqu'à son commit de création dans la liste de
départ — à une condition, qui tient à ce qu'est `move`
([L'API Python](../../list-dir/references/contrat-liste.md#lapi-python)) : **déplacer et commiter
d'abord, écrire la preuve ensuite, dans un second commit.** Mêlés, l'historique de l'entrée
s'arrête au jour du solde.

L'entrée déplacée reçoit alors sa section `## Soldé le` :

```markdown
## Soldé le

**2026-09-02, chantier `listing-fix`** — les listings filtrent désormais sur le nom du fichier.
Établi par : `ls .claude/implementation/*.md | grep -vE 'brief|audit'` → 2 lignes, aucun
`.brief.md` ni `.audit.md` remonté.
```

**Sans commande exécutée et sa sortie réelle, l'entrée reste dans le registre.** C'est le même
principe que le point d'intégrité de l'auditeur : celui qui vient de faire le travail est le plus
mal placé pour affirmer qu'il l'a fait. Un solde s'établit, il ne se déclare pas.

Une entrée qu'un chantier a **aggravée** plutôt que soldée ne bouge pas de liste : son `## Constat`
est mis à jour, daté de la mise à jour et non de l'origine, et `category` passe à `aggravee`.

---

## Écarter

Une entrée peut cesser d'avoir sa place au registre sans qu'un correctif y soit pour quelque chose :
ce qu'elle cite n'existe plus, une autre entrée dit déjà la même chose, ou le constat n'était pas
une dette.

```bash
list-dir move "$T/technical-debt" <id> "$T/technical-debt-ecarte"
```

Elle reçoit sa section `## Écartée le`, motif compris :

```markdown
## Écartée le

**2026-09-02 — non pertinent** — le hook `rtk` ne réécrit plus les `ls`, la colonne de taille a
disparu.
Établi par : `git log -1 --format=%H -- hooks/rtk.sh` → aucun commit, le hook a été supprimé.
```

Motifs admis, et rien d'autre : **non pertinent**, **doublon**, **pas une dette**. Pour un doublon,
la ligne `Établi par` cite l'**`id` de l'entrée conservée** au lieu d'une commande — c'est la seule
dispense, et l'entrée conservée est la plus ancienne des deux.

**Écarter exige la même preuve que solder** : une commande lancée et sa sortie réelle. Sans elle,
l'entrée reste au registre. Le registre des écartés n'est pas une corbeille — c'est là qu'on
retrouve, deux ans plus tard, pourquoi un problème a arrêté d'en être un.

---

## Corriger une entrée

Une entrée peut être **vraie et mal écrite** : un chiffre sous-mesuré dès l'origine, un **Pour
solder** qui échouerait à son premier lancement, un **Assumé** devenu faux, un repère périmé. Ce
n'est ni un solde, ni une mise à l'écart, ni une aggravation — le problème n'a pas bougé, c'est sa
description qui est fautive. Elle se corrige **sur place**, dans son fichier, sans changer de liste.

Ce qui se corrige : les sections **Constat**, **Pourquoi c'est gênant**, **Assumé**, **Pour
solder**.

Ce qui ne bouge pas : le champ **`date`** — il dit depuis quand le problème est connu, pas depuis
quand il est bien décrit — et l'**`id`**, qui ne se renomme pas ([Ce qu'une entrée
porte](#ce-quune-entrée-porte)). Le `title` porte
lui-même le chiffre faux → il reste tel quel, et le **Constat** énonce l'écart.

**La correction exige la même preuve que le solde** : la commande qui établit le bon chiffre, citée
dans l'entrée. Sans elle, on remplace une erreur par une autre — et celle-là aura l'air vérifiée.

Après correction, relire ce qui vient d'être écrit :

```bash
list-dir validate "$T/technical-debt" --filled
```

## Marqueur d'une entrée relue

Une entrée peut être **relue et laissée en place**, avec une information sur cette relecture. Elle
porte alors deux champs, et pas une ligne de prose : `category` reçoit le verdict, `reviewed` la
date de la revue qui l'a rendu.

```toml
reviewed = 2026-08-16
category = "inverifiable"
```

**Le `title` et l'`id`, eux, ne bougent jamais** — pas de suffixe, pas de mention ajoutée. Marquer
une entrée relue ne la réécrit pas : le verdict vit dans les champs de revue, jamais dans son
identité ([Ce qu'une entrée porte](#ce-quune-entrée-porte)).

Les catégories qui marquent, et ce que chaque marqueur engage :
[Catégories](../../debt-review/references/categories.md). Le contrat de la liste les énumère, et
refuse toute autre valeur.

---

## Lecture

Le pipeline n'ouvre jamais le registre de lui-même : ni `intent-brief` au cadrage, ni le tracker à
l'Étape 0. Il l'alimente, l'utilisateur le consulte — typiquement quand il cherche un sujet de
chantier.

```bash
list-dir list "$T/technical-debt" --sort date       # tout, du plus ancien au plus récent
list-dir show "$T/technical-debt" <id>              # une entrée
```

**Une exception, et elle est manuelle** : le skill `debt-review` ouvre le registre pour le relire
entrée par entrée, le confronter au dépôt et le faire arbitrer. Il ne s'invoque jamais de lui-même,
et il ne corrige aucun code — il instruit un verdict, l'utilisateur tranche, puis les entrées sont
déplacées, les champs de revue écrits.
