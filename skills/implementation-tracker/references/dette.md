# Registre de dette technique

Fichiers : `.claude/implementation/todo/technical-debt.md`, et `technical-debt-solde.md` pour ce qui
a été soldé.

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

## Lecture

Le pipeline n'ouvre jamais le registre de lui-même : ni `intent-brief` au cadrage, ni le tracker à
l'Étape 0. Il l'alimente, l'utilisateur le consulte — typiquement quand il cherche un sujet de
chantier.
