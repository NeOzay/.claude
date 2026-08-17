# Registre de dette technique

Fichiers : `.claude/implementation/todo/technical-debt.md`, `technical-debt-solde.md` pour ce qui
a été soldé, et `technical-debt-ecarte.md` pour ce qui est sorti du registre sans avoir été payé.

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

---

## Ce qui entre

Tout problème **non résolu** au moment de clore :

- les constats de la section « Dette induite » du rapport d'audit ;
- les réserves que l'utilisateur a choisi de clore avec plutôt que de traiter ;
- le hors-périmètre assumé au brief, quand c'est un problème qu'on a vu et laissé ;
- une étape retirée en cours de route, ou un contournement laissé en place.

**Ce qui n'entre pas :**

- les idées d'amélioration — le registre ne liste que du constaté, vérifié dans le dépôt. Elles
  iront dans `road-map.md`, à côté ;
- ce qui a été corrigé pendant le chantier : le rapport en garde la trace, pas le registre ;
- les préférences de style qu'aucun critère ne porte.

Le filtre à l'entrée est volontairement large : mieux vaut une entrée que l'utilisateur supprimera
qu'un problème qui disparaît avec la conversation. L'élagage est son geste, pas le nôtre.

---

## Tête du registre

Sous le préambule, une ligne — et une seule :

```markdown
> Dernière vérification : 2026-08-14 (chantier `dette-technique`)
```

Elle dit **quand le registre a été confronté au dépôt pour la dernière fois**, pas quand il a été
modifié. Sans elle, rien ne distingue un registre à jour d'un registre périmé dont les entrées ont
été soldées ailleurs sans que personne ne l'ouvre — et un registre qu'on soupçonne périmé ne se lit
plus.

Elle s'actualise à chaque alimentation, et à chaque fois qu'on relit le registre entrée par entrée
pour vérifier qu'il tient encore. L'historique des soldes, lui, ne vit pas ici : il est dans
`technical-debt-solde.md`.

## Gabarit d'entrée

Entrées **horodatées, sans numéro** — un numéro obligerait à réindexer à chaque retrait. Ordre du
plus ancien au plus récent, donc **ajout en fin de fichier**. Une entrée se référence par son
intitulé.

```markdown
## 2026-08-14 — Les filtres de listing sont cassés par le hook rtk

**Constat** — `ls .claude/implementation/*.md | grep -vE '\.(brief|audit)\.md$'` n'exclut plus
rien : le hook `rtk` ajoute une colonne de taille en fin de ligne, l'ancre `$` ne matche jamais.

**Pourquoi c'est gênant** — les `*.brief.md` et `*.audit.md` remontent dans la liste des
implémentations en cours, que l'Étape 0 du tracker existe précisément pour tenir propre.

**Pour solder** — filtrer sur le nom de fichier plutôt que sur la fin de ligne.

*Identifié par `audit-integre`, R4 du rapport d'audit.*
```

Champ facultatif, quand c'en était un :

```markdown
**Assumé** : le hors-périmètre était écrit au brief — ce chantier ne devait pas toucher aux
patterns de sécurité.
```

Une entrée sans **Pour solder** est un regret, pas une dette : dire ce qu'il faudrait faire, même
grossièrement, ou ne pas l'écrire.

**Désigner sans numéro de ligne.** Une entrée cite un fichier, une section, une phrase — jamais
`fichier.md:42`. Le repère se périme au premier commit qui insère une ligne au-dessus, sans qu'une
commande échoue et sans que rien ne le signale. Écrire plutôt `` `cloture.md`, « toutes les étapes
sont cochées » `` : la citation reste vraie tant que la règle existe, et devient introuvable
exactement quand elle disparaît — ce qui est précisément l'information cherchée.

> *Mode de défaillance* — un numéro de ligne périmé ne casse rien de visible : il fait classer
> `non-pertinent` une dette vivante dont la relecture n'a pas retrouvé la cible. C'est la sortie de
> registre la plus facile à obtenir sur une preuve fausse.

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
4. Appender les nouvelles entrées en fin de fichier, dans l'ordre où elles ont été constatées.
5. **Actualiser la ligne de dernière vérification** avec la date du jour
   ([Dates et listing](contrat.md#dates-et-listing)) et le slug du chantier — y compris quand le chantier n'a rien eu à verser : le registre
   a quand même été relu, et c'est cette information-là qu'elle porte.

Le fichier n'existe pas encore → le créer avec son préambule, qui dit ce qu'il recense et ce qu'il
exclut.

---

## Solder

Une entrée soldée est **retirée du registre**, pas barrée — et déplacée en fin de
`technical-debt-solde.md`. Le registre reste ainsi la liste de ce qui reste à faire, sans gonfler.

L'entrée déplacée est complétée par :

```markdown
**Soldé le 2026-09-02 par le chantier `listing-fix`** — les listings filtrent désormais sur le nom
du fichier.
Établi par : `ls .claude/implementation/*.md | grep -vE 'brief|audit'` → 2 lignes, aucun
`.brief.md` ni `.audit.md` remonté.
```

**Sans commande exécutée et sa sortie réelle, l'entrée reste dans le registre.** C'est le même
principe que le point d'intégrité de l'auditeur : celui qui vient de faire le travail est le plus
mal placé pour affirmer qu'il l'a fait. Un solde s'établit, il ne se déclare pas.

Une entrée qu'un chantier a **aggravée** plutôt que soldée reste où elle est, et son **Constat** est
mis à jour — daté de la mise à jour, pas de l'origine.

---

## Écarter

Une entrée peut cesser d'avoir sa place au registre sans qu'un correctif y soit pour quelque chose :
ce qu'elle cite n'existe plus, une autre entrée dit déjà la même chose, ou le constat n'était pas
une dette. Elle est alors **écartée** : retirée du registre et déplacée en fin de
`technical-debt-ecarte.md`, complétée par son motif.

```markdown
**Écartée le 2026-09-02 — non pertinent** — le hook `rtk` ne réécrit plus les `ls`, la colonne de
taille a disparu.
Établi par : `git log -1 --format=%H -- hooks/rtk.sh` → aucun commit, le hook a été supprimé.
```

Motifs admis, et rien d'autre : **non pertinent**, **doublon**, **pas une dette**. Pour un doublon,
la ligne `Établi par` cite l'**intitulé de l'entrée conservée** au lieu d'une commande — c'est la
seule dispense, et l'entrée conservée est la plus ancienne des deux.

**Écarter exige la même preuve que solder** : une commande lancée et sa sortie réelle. Sans elle,
l'entrée reste au registre. Le registre des écartés n'est pas une corbeille — c'est là qu'on
retrouve, deux ans plus tard, pourquoi un problème a arrêté d'en être un.

Le fichier n'existe pas encore → le créer avec son préambule, qui dit ce qu'il recense et pourquoi
il n'est pas le registre des soldes.

---

## Corriger une entrée

Une entrée peut être **vraie et mal écrite** : un chiffre sous-mesuré dès l'origine, un **Pour
solder** qui échouerait à son premier lancement, un **Assumé** devenu faux, un repère périmé. Ce
n'est ni un solde, ni une mise à l'écart, ni une aggravation — le problème n'a pas bougé, c'est sa
description qui est fautive. Elle se corrige **sur place**, sans changer de destination.

Ce qui se corrige : le **Constat**, le **Pourquoi c'est gênant**, l'**Assumé**, le **Pour solder**.

Ce qui ne bouge pas : la **date** du titre — elle dit depuis quand le problème est connu, pas depuis
quand il est bien décrit — et l'**intitulé**, clé de référence et de dédoublonnage (« Marqueur d'une
entrée relue »). L'intitulé porte lui-même le chiffre faux → il reste tel quel, et le **Constat**
énonce l'écart. Le réécrire ferait revenir l'entrée comme neuve au point 3 d'*Alimenter*, ce qui
coûte plus cher que l'imprécision d'un titre.

**La correction exige la même preuve que le solde** : la commande qui établit le bon chiffre, citée
dans l'entrée. Sans elle, on remplace une erreur par une autre — et celle-là aura l'air vérifiée.

## Marqueur d'une entrée relue

Une entrée peut être **relue et laissée en place**, avec une information sur cette relecture. Elle
porte alors, sur une ligne seule **sous son titre**, la mention `(catégorie) date` :

```markdown
## 2026-08-14 — Les correctifs de l'étape 9 n'ont jamais été audités

(invérifiable en revue) 2026-08-16
```

**L'intitulé, lui, ne bouge jamais** — pas de suffixe, pas de mention ajoutée. C'est par lui qu'une
entrée se référence (« Gabarit d'entrée ») et sur lui que le point 3 d'*Alimenter* dédoublonne
avant d'écrire : le modifier ferait revenir le même constat comme s'il était neuf, et le registre
porterait deux fois la même dette.

Les catégories qui marquent, et ce que chaque marqueur engage :
`../../debt-review/references/categories.md`.

---

## Lecture

Le pipeline n'ouvre jamais le registre de lui-même : ni `intent-brief` au cadrage, ni le tracker à
l'Étape 0. Il l'alimente, l'utilisateur le consulte — typiquement quand il cherche un sujet de
chantier.

**Une exception, et elle est manuelle** : le skill `debt-review` ouvre le registre pour le relire
entrée par entrée, le confronter au dépôt et le faire arbitrer. Il ne s'invoque jamais de lui-même,
et il ne corrige aucun code — il instruit un verdict, l'utilisateur tranche, puis les registres et
la ligne de dernière vérification sont écrits.
