---
slug: dette-technique
---

## 2026-08-14 — clôture — `bc67bb9`

**Verdict** : RÉSERVES

### Vérifications exécutées

Commandes des étapes du suivi :

- `test -f skills/implementation-tracker/references/dette.md` → OK (étape 1)
- `test -f .claude/implementation/todo/README.md` → OK (étape 2)
- `grep -c '^## 2026-' .claude/implementation/todo/technical-debt.md` → `6` (étape 3, attendu 6)
- `grep -n 'todo/' skills/implementation-tracker/SKILL.md` → 2 occurrences (l. 37, 42) (étape 4)
- `grep -n 'dette.md' skills/implementation-tracker/references/cloture.md` → 2 occurrences
  (l. 28 point 2, l. 106 abandon) (étape 5)
- `grep -n 'registre' skills/implementation-tracker/references/audit.md` → 3 occurrences
  (l. 71, 73, 74) (étape 6)

Critères de réussite du brief :

- `grep -c 'audit\.md' agents/implementation-auditor.md` → `4` ; même commande sur `master`
  (`git show master:agents/implementation-auditor.md | grep -c 'audit\.md'`) → `4`. **Inchangé.**
- `grep -c 'todo/' agents/implementation-auditor.md` → `0`
- `git diff --stat master...dette-technique -- agents/implementation-auditor.md` → sortie vide
- `grep -c '^## [0-9]\+\.' .claude/implementation/todo/technical-debt.md` → `0` (aucune
  numérotation, conforme à la décision)
- `grep '^## ' … | cut -d' ' -f2 | sort -c` → OK (ordre chronologique croissant)
- `grep -n '^### ' skills/implementation-tracker/references/cloture.md` → `1. Audit`,
  `2. Alimenter le registre de dette`, `3. Finaliser le fichier de suivi`,
  `4. Aplatir la branche d'implémentation`, `5. Résumé` — l'alimentation est bien après l'audit et
  avant l'archivage, la renumérotation est complète et sans doublon.
- `git check-ignore -v .claude/implementation/todo/technical-debt.md` → aucune règle : le registre
  est bien versionnable.
- `grep -rn 'todo/' skills/ agents/ --include=*.md` → seulement `dette.md`, `cloture.md:27`,
  `SKILL.md:37,42`. Aucune occurrence dans `skills/intent-brief/` : pas de lecture au cadrage.
- `git diff --shortstat master...dette-technique` → 9 fichiers, 697 insertions, 4 suppressions.

### Conformité à l'intention

- **Critère 1** — « `todo/technical-debt.md` existe et porte les six dettes d'`audit-integre`,
  datées, ordonnées de la plus ancienne à la plus récente, avec leur chantier d'origine » :
  **atteint, vérifié**. Six entrées `## 2026-08-14 — …`, chacune close par
  `*Identifié par `audit-integre`, …*`. Les six correspondent aux constats réellement survivants du
  rapport archivé `done/2026-08-14-audit-integre.audit.md` : R6, R7, R8 (les seuls non levés),
  le hors-périmètre assumé au brief, le constat de journal sur les filtres `rtk`, et le corollaire
  de R1 sur les chemins de frontmatter. R1 à R5 sont bien levés dans ce rapport (l. 215-232) et
  n'ont, à juste titre, pas été versés. Les références de ligne citées dans les entrées ont été
  recoupées et sont exactes (`intent-brief/SKILL.md` Étape 7, `cloture.md:10`, `audit.md:43-45`
  contre `implementation-auditor.md:21-23`).
- **Critère 2** — « étape d'alimentation située après l'audit et avant l'archivage » :
  **atteint, vérifié** (point 2 de `cloture.md`, entre le point 1 « Audit » et le point 4
  « Aplatir »). La justification de la position est écrite sur place, pas seulement dans le plan.
- **Critère 3** — « l'auditeur n'a toujours qu'un seul fichier en écriture, aucune mention de
  `todo/` » : **atteint, vérifié**. `agents/implementation-auditor.md` n'apparaît pas dans le diff
  du chantier ; le compte de `audit\.md` est identique à celui de `master`.
- **Critère 4** — « l'abandon propose l'alimentation au lieu de l'imposer » : **atteint, vérifié**.
  `cloture.md`, section Abandon, point 4 : « **Proposer** … Proposer, jamais imposer », avec le
  contre-exemple du chantier abandonné sans dette.
- **Hors-périmètre** : respecté. Aucune lecture automatique — `dette.md` section « Lecture » et
  `SKILL.md:43` le disent explicitement, et `skills/intent-brief/` est intact. Aucun `road-map.md`
  créé ; il n'est qu'annoncé comme extension possible (README, `dette.md`).
- **Signaux de dérive** : aucun matérialisé. Le doublon est fermé à trois endroits cohérents
  (`dette.md` « Un état, pas un journal » + point 3 de « Alimenter », `cloture.md` point 2,
  `audit.md` l. 71-74) ; l'auditeur ne gagne aucun droit d'écriture.
- **Symptôme d'origine** — « les dettes finissent dans un fichier archivé que personne ne relit » :
  **disparu pour les six dettes connues**, qui existent désormais hors de `done/`. Le mécanisme qui
  empêche la récidive (point 2 de `cloture.md`) est en place mais n'a encore jamais été exécuté :
  ce chantier en est le premier passage réel, et il n'est pas encore clos. Voir R1.

### Qualité du contenu produit

- **R1 — le registre écrit au point 2 n'est jamais explicitement mis en index, et le point 2 promet
  pourtant qu'il « entre dans l'aplatissement ».** `cloture.md:31-33` justifie sa position par
  « avant l'archivage, pour que l'écriture entre dans l'aplatissement de la branche », mais le
  point 3 qui suit ne commite que le fichier de suivi (« **Sur la branche `<slug>`** : `statut:
  terminé` … Le committer »), et le point 4 ne stage que les fichiers déplacés vers `done/`.
  `technical-debt.md` est, au premier usage, un fichier **non suivi** : rien dans la procédure ne
  garantit qu'il soit ajouté avant le commit unique. Chemin d'échec silencieux — le registre reste
  dans l'arbre de travail, l'aplatissement passe, et l'écriture est perdue sans message d'erreur.
  Une phrase au point 2 (« l'ajouter à l'index ») ou une mention au point 3 suffirait.
- **R2 — le bloc de citation « Dernière vérification » du modèle imposé est absent.** Le brief
  range parmi les *contraintes connues de l'utilisateur* un « bloc de citation en tête portant
  `Dernière vérification : <date> (chantier <slug>)` » (brief, section « Modèle imposé »), présent
  dans `docs/TECHNICAL_DEBT.md` d'`ebook-translator` (l. 11, vérifié). Les *Décisions* du brief
  n'écartent que **l'historique des soldes** de cette tête de fichier, déplacé vers
  `technical-debt-solde.md` — pas la ligne de dernière vérification, qui a une fonction distincte :
  dire quand le registre a été confronté au dépôt pour la dernière fois. Elle ne figure ni dans
  `todo/technical-debt.md`, ni dans le gabarit de `dette.md`. En l'état, rien ne permet de savoir
  si le registre est à jour ou périmé. Ce n'est pas un critère de réussite, et le plan avait déjà
  omis la contrainte : c'est précisément le type d'écart que l'Étape 7 d'`intent-brief` devait
  attraper — laquelle est, ironie utile, l'entrée n° 2 du registre.
- **R3 — `technical-debt-solde.md` est annoncé dans deux documents mais n'existe pas.**
  `SKILL.md:39` le liste dans l'arborescence et le README `todo/` lui consacre une puce. Les deux
  précisent « créé au premier solde », donc l'écart est documenté et l'écart au brief est
  journalisé au suivi (« écart au brief signalé à l'utilisateur, laissé tel quel »). Constat porté
  ici pour mémoire : un lecteur qui suit l'arborescence de `SKILL.md` cherchera un fichier absent.
  Arbitrage déjà rendu, aucune action attendue.
- Style : conforme aux fichiers voisins (`audit.md`, `cloture.md`) — même densité, mêmes renvois
  inter-fichiers par chemin relatif à `skills/implementation-tracker/`, même usage du gras pour la
  règle et de l'italique pour l'attribution. Le README `todo/` reprend la forme de `done/`. Rien à
  signaler.

### Dette induite

- **R4 — la justification « l'orchestrateur écrit, jamais l'auditeur » est écrite trois fois.**
  `dette.md:24-28`, `cloture.md:35-36`, `audit.md:71-74`. Les trois formulations sont aujourd'hui
  cohérentes, mais une révision de la règle devra les toucher toutes trois, et c'est exactement le
  motif de l'entrée n° 5 déjà présente au registre (divergence inter-fichiers sans mode de
  défaillance). Coût futur modéré ; le choix se défend, chaque fichier devant rester lisible seul.
- Aucune abstraction créée sans nécessité, aucun couplage nouveau : `dette.md` porte le procédural,
  `SKILL.md` et `cloture.md` n'y renvoient que par une ligne, ce que le plan annonçait.

### Bloquants

Aucun. Les quatre critères de réussite sont atteints et vérifiés par exécution ; R1 à R4 sont des
réserves à trancher par l'utilisateur avant la clôture, pas des empêchements.

---

## 2026-08-14 — clôture (ré-audit complet) — `f3f7728`

**Verdict** : RÉSERVES

Ré-audit complet du diff `master...dette-technique` après le correctif de l'étape 7 (R1, R2).
Le rapport précédent (`bc67bb9`) reste au-dessus : il porte R1 à R4, dont la numérotation est
reprise ici sans réattribution. Les constats nouveaux commencent à R5.

### Vérifications exécutées

Commandes des étapes du suivi :

- `test -f skills/implementation-tracker/references/dette.md` → OK (étape 1)
- `test -f .claude/implementation/todo/README.md` → OK (étape 2)
- `grep -c '^## 2026-' .claude/implementation/todo/technical-debt.md` → `6` (étape 3, attendu 6)
- `grep -n 'todo/' skills/implementation-tracker/SKILL.md` → l. 37, 42 (étape 4)
- `grep -n 'dette.md' skills/implementation-tracker/references/cloture.md` → l. 28, 122 (étape 5)
- `grep -n 'registre' skills/implementation-tracker/references/audit.md` → l. 71, 73, 74 (étape 6)
- `grep -n 'index' skills/implementation-tracker/references/cloture.md` → l. 42, 56, 75 (étape 7)
- `grep -c 'Dernière vérification' references/dette.md todo/technical-debt.md` → `1` et `1`
  (étape 7)

Critères de réussite du brief :

- `grep -c 'audit\.md' agents/implementation-auditor.md` → `4` ; `git show
  master:agents/implementation-auditor.md | grep -c 'audit\.md'` → `4`. **Inchangé.**
- `grep -c 'todo/' agents/implementation-auditor.md` → `0`
- `git diff --stat master...dette-technique -- agents/implementation-auditor.md` → sortie vide
- `grep -n '^### ' skills/implementation-tracker/references/cloture.md` → `1. Audit`,
  `2. Alimenter le registre de dette`, `3. Finaliser le fichier de suivi`, `4. Aplatir la branche`,
  `5. Résumé` — renumérotation complète, sans doublon ni saut
- `grep '^## ' todo/technical-debt.md | cut -d' ' -f2 | sort -c` → OK (ordre croissant)
- `grep -c '^## [0-9]\+\.' todo/technical-debt.md` → `0` (aucune numérotation)
- `grep -rn 'todo/' skills/ agents/ --include=*.md | grep -v implementation-tracker` → sortie vide :
  aucune lecture de `todo/` par `intent-brief` ni ailleurs
- `test -e .claude/implementation/todo/technical-debt-solde.md` → **ABSENT** (attendu, cf. R3)
- `git status --short` → arbre propre

### Conformité à l'intention

- **Critère 1** — registre existant, six dettes datées, ordonnées, avec chantier d'origine :
  **atteint, vérifié**. Six entrées `## 2026-08-14 — …`, chacune close par `*Identifié par
  `audit-integre`, …*`, chacune portant **Constat** / **Pourquoi c'est gênant** / **Pour solder**
  conformément au gabarit de `dette.md:101` (« une entrée sans *Pour solder* est un regret »).
  Inchangé depuis `bc67bb9`, hors ajout de la ligne de tête.
- **Critère 2** — alimentation après l'audit et avant l'archivage : **atteint, vérifié**
  (point 2, entre le point 1 « Audit » et le point 4 « Aplatir »).
- **Critère 3** — l'auditeur inchangé, sans mention de `todo/` : **atteint, vérifié**. Le fichier
  n'apparaît pas dans le diff du chantier.
- **Critère 4** — l'abandon propose au lieu d'imposer : **atteint, vérifié** (`cloture.md:121-124`).
  Voir toutefois R5 sur ce que devient cette proposition une fois acceptée.
- **Hors-périmètre** : respecté. Aucune lecture automatique (`dette.md` section « Lecture »,
  `SKILL.md:43`, et `grep` sur `skills/` sans résultat hors du tracker). Aucun `road-map.md` créé,
  seulement annoncé comme extension (README `todo/`, `dette.md`).
- **Signaux de dérive** : aucun matérialisé. Le doublon est fermé en quatre endroits cohérents
  (`dette.md` « Un état, pas un journal » et point 3 d'« Alimenter », `cloture.md:32-34`,
  `audit.md:71-74`). L'auditeur ne gagne aucun droit d'écriture.
- **Symptôme d'origine** : **disparu** pour les six dettes connues, qui existent désormais hors de
  `done/`, versionnées et versionnables (aucune règle `.gitignore`). Le mécanisme de non-récidive
  (`cloture.md` point 2) est en place ; il n'aura été réellement exécuté qu'à la clôture de ce
  chantier même.

### Traitement des réserves précédentes

- **R1 (mise à l'index)** — **levé, vérifié**. `cloture.md:42-51` ajoute `git add
  .claude/implementation/todo/` au point 2, avec la raison du chemin d'échec silencieux écrite sur
  place, et le point 3 reprend le répertoire dans son `git add`. La double mise à l'index est
  redondante mais volontairement défensive : le point 2 protège l'écriture si le point 3 est
  reformulé un jour. Sans coût.
- **R2 (« Dernière vérification »)** — **levé, vérifié**. `todo/technical-debt.md:13` porte la
  ligne, `dette.md` lui consacre une section « Tête du registre » qui distingue explicitement
  *vérifié* de *modifié*, et le point 5 d'« Alimenter » impose de l'actualiser avec `date +%F`
  « jamais devinée », y compris quand le chantier n'a rien versé. Le traitement va au-delà du
  constat : il ferme aussi le cas du registre relu sans modification.
- **R3 (`technical-debt-solde.md` annoncé, absent)** — **subsiste, arbitré**. Le suivi le journalise
  comme écart signalé et laissé tel quel. Un point supplémentaire non relevé au premier passage :
  `todo/technical-debt.md:9` en fait un **lien markdown** `[technical-debt-solde.md](…)`, qui ne
  résout vers rien tant qu'aucun solde n'a eu lieu. Aucune action attendue, arbitrage déjà rendu.
- **R4 (justification écrite en trois endroits)** — **subsiste, dette assumée**. Le correctif de
  l'étape 7 n'en a pas ajouté de quatrième. Coût futur inchangé.

### Qualité du contenu produit

- **R5 — la proposition d'alimentation à l'abandon n'a aucun chemin d'écriture défini, et le seul
  qu'on puisse déduire perd le fichier.** `cloture.md:121-124` (point 4 de l'Abandon) propose de
  verser au registre ce que l'abandon laisse ouvert, mais rien n'indique où ni comment cette
  écriture est committée. Le point 3 qui précède a déjà fait son commit direct sur `base:` (cas
  « tout jeter ») ; dans le cas « garder la branche », on reste sur `<slug>`, et le point 5 interdit
  explicitement de jamais l'aplatir dans `base:` — une entrée écrite là n'atteindra donc jamais
  `base:`. C'est exactement le mode de défaillance que R1 a fait corriger sur le chemin de clôture,
  laissé ouvert sur le chemin d'abandon, alors que le même correctif — une ligne `git add` + commit,
  et la précision qu'on écrit sur `base:` — s'y appliquerait à l'identique. Le critère 4 du brief est
  atteint (l'alimentation est bien proposée et non imposée) ; c'est sa mise en œuvre qui est
  incomplète. Réserve, pas bloquant : l'abandon reste rare et l'orchestrateur est présent pour
  rattraper, mais le brief ne demandait pas une proposition qui se perd.
- **R6 — l'ordre du point 4 de l'Abandon place la proposition après la suppression de la branche.**
  Toujours `cloture.md:117-124` : le point 3 peut exécuter `git branch -D <slug>`, et c'est
  seulement au point 4 qu'on propose de verser au registre. Or ce qu'il y a à verser — « le problème
  qui restait à traiter » — se lit dans le suivi et, le cas échéant, dans le rapport d'audit, que le
  point 3 vient d'archiver et dont la branche vient d'être détruite. Rien n'est irrécupérable
  (l'archivage en `done/` conserve suivi et rapport), mais l'ordre demande de décider après avoir
  rangé plutôt qu'avant, à l'inverse de la position soigneusement justifiée du point 2 de la clôture
  (« après l'audit, avant l'archivage »). Asymétrie de raisonnement entre les deux procédures du
  même fichier.
- **R7 — `todo/README.md` n'apparaît pas dans l'arborescence de `SKILL.md`.** `SKILL.md:36-39`
  liste `todo/` avec ses deux registres mais pas son README, alors que c'est le seul fichier des
  trois qui existe réellement à l'instant. Symétrique de `done/`, qui n'a pas de README — la
  convention est donc nouvelle et non documentée à l'endroit où un lecteur cherche l'arborescence.
  Constat mineur, sans mode de défaillance.
- **Style** : conforme au voisinage. `dette.md` reprend la structure de `audit.md` et de
  `cloture.md` (séparateurs `---`, gras pour la règle, italique pour l'attribution, renvois par
  chemin relatif à `skills/implementation-tracker/`). `todo/README.md` suit la forme de
  `archive/README.md`, comme le plan l'annonçait. La section « Tête du registre » ajoutée à l'étape 7
  respecte la densité des sections voisines. Rien à signaler.

### Dette induite

- R4 (ci-dessus) reste la seule dette induite par ce chantier : la règle « l'orchestrateur écrit,
  jamais l'auditeur » vit en trois formulations qu'une révision devra toucher ensemble. C'est le
  motif de l'entrée n° 5 du registre lui-même.
- R5 et R6 ne sont pas de la dette induite mais de la couverture incomplète : ils portent sur du
  contenu que ce chantier vient d'écrire.
- Aucune abstraction créée sans nécessité, aucun couplage nouveau : `dette.md` porte tout le
  procédural, `SKILL.md` et `cloture.md` n'y renvoient que par une ligne.

### Bloquants

Aucun. Les quatre critères de réussite sont atteints et vérifiés par exécution ; R1 et R2 sont
levés. R3 à R7 sont des réserves à trancher par l'utilisateur avant de clore — R5 étant celle qui
mérite un arbitrage explicite, les autres pouvant partir au registre à la clôture.

---

## 2026-08-14 — clôture (ré-audit complet) — `343f180`

**Verdict** : RÉSERVES

Troisième passage sur `master...dette-technique`, après le correctif de l'étape 8 (R3 à R7). Les
deux rapports précédents restent au-dessus : ils portent R1 à R7, dont la numérotation est reprise
ici sans réattribution. Les constats nouveaux commencent à **R8**.

### Vérifications exécutées

Commandes des étapes du suivi, rejouées :

- étape 1 — `test -f skills/implementation-tracker/references/dette.md` → **OK**
- étape 2 — `test -f .claude/implementation/todo/README.md` → **OK**
- étape 3 — `grep -c '^## 2026-' .claude/implementation/todo/technical-debt.md` → `6` (attendu 6)
- étape 4 — `grep -n 'todo/' skills/implementation-tracker/SKILL.md` → l. 37, 43
- étape 5 — `grep -n 'dette.md' skills/implementation-tracker/references/cloture.md` → l. 28, 36, 118
- étape 6 — `grep -n 'registre' skills/implementation-tracker/references/audit.md` → l. 71, 72
- étape 7 — `grep -n 'index' …/cloture.md` → l. 42, 56, 75, 129 ;
  `grep -c 'Dernière vérification' …/dette.md …/technical-debt.md` → `1` et `1`
- étape 8 — `test -e .claude/implementation/todo/technical-debt-solde.md` → **EXISTS** ;
  `grep -n 'git add .claude/implementation/todo' …/cloture.md` → l. 45, 133 ;
  `grep -n 'README.md' skills/implementation-tracker/SKILL.md` → l. 38

Critères de réussite du brief :

- `grep -c 'audit\.md' agents/implementation-auditor.md` → `4` ;
  `git show master:agents/implementation-auditor.md | grep -c 'audit\.md'` → `4`. **Inchangé.**
- `grep -c 'todo/' agents/implementation-auditor.md` → `0`
- `git diff --stat master...dette-technique -- agents/implementation-auditor.md` → sortie vide
- `grep -n '^### ' …/cloture.md` → `1. Audit`, `2. Alimenter le registre de dette`,
  `3. Finaliser le fichier de suivi`, `4. Aplatir la branche d'implémentation`, `5. Résumé` —
  renumérotation complète, sans doublon ni saut ; l'alimentation est bien **après** l'audit et
  **avant** l'aplatissement/archivage
- `grep '^## ' …/technical-debt.md | cut -d' ' -f2 | sort -c` → **OK** (ordre chronologique croissant)
- `grep -c '^## [0-9]\+\.' …/technical-debt.md` → `0` (aucune numérotation)
- `grep -rn 'todo/' skills/ agents/ --include=*.md | grep -v implementation-tracker` → sortie vide :
  aucune lecture de `todo/` par `intent-brief` ni ailleurs
- `git status --short` → arbre propre ; `git rev-parse dette-technique HEAD` → `343f180…` (le SHA
  annoncé est bien celui audité)

Recoupement des références citées par le registre (aucune écriture de mémoire) :

- `sed -n '43,45p' …/audit.md` et `sed -n '21,23p' agents/implementation-auditor.md` → l'asymétrie
  sur la racine du dépôt (entrée n° 5) est **toujours réelle**
- `sed -n '193p;205p' skills/intent-brief/SKILL.md` → « Étape 7 — Confrontation plan ↔ brief » et
  « Sortie en trois lignes, pas un rapport » : entrée n° 2 exacte
- `sed -n '10p' …/cloture.md` → « Vérifier d'abord que toutes les étapes sont cochées » : entrée
  n° 3 exacte **après** la renumérotation du chantier
- `ls .claude/implementation/*.md | grep -vE '\.(brief|audit)\.md$'` → remonte `.brief.md` et
  `.audit.md` : le bug `rtk` de l'entrée n° 4 est **reproduit en direct**

### Conformité à l'intention

- **Critère 1** — registre existant, six dettes datées, ordonnées, avec chantier d'origine :
  **atteint, vérifié**. Six entrées `## 2026-08-14 — …`, chacune close par
  `*Identifié par `audit-integre`, …*`, chacune portant **Constat** / **Pourquoi c'est gênant** /
  **Pour solder**. Les quatre références de dépôt vérifiables ont été recoupées ci-dessus et tiennent
  toutes, y compris après la renumérotation de `cloture.md` faite par ce chantier même.
- **Critère 2** — alimentation après l'audit, avant l'archivage : **atteint, vérifié** (point 2,
  entre le point 1 « Audit » et le point 4 « Aplatir »), avec la justification écrite sur place.
- **Critère 3** — l'auditeur inchangé, sans mention de `todo/` : **atteint, vérifié**. Le fichier
  n'apparaît pas dans le diff du chantier et son compte de `audit\.md` est identique à `master`.
- **Critère 4** — l'abandon propose au lieu d'imposer : **atteint, vérifié** (`cloture.md:117-120`,
  « Proposer, jamais imposer », avec le contre-exemple du chantier sans dette). Voir R9 sur la
  complétude du chemin d'écriture une fois la proposition acceptée.
- **Hors-périmètre** : **respecté**. Aucune lecture automatique (`dette.md` section « Lecture »,
  `SKILL.md:44`, `README.md:18`, et `grep -rn 'todo/'` hors tracker sans résultat). Aucun
  `road-map.md` créé — seulement annoncé comme extension possible.
- **Signaux de dérive** : **aucun matérialisé**. Le doublon est fermé en trois points cohérents
  (`dette.md` « Un état, pas un journal », `cloture.md:32-34`, `audit.md:71-74`) ; l'auditeur ne
  gagne aucun droit d'écriture. Voir toutefois R8, qui ouvre le risque inverse — non pas écrire deux
  fois, mais n'écrire pas du tout.
- **Symptôme d'origine** : **disparu** pour les six dettes connues, désormais hors de `done/`,
  versionnées et versionnables. Le mécanisme de non-récidive (`cloture.md` point 2) est en place ;
  il ne sera réellement exercé qu'à la clôture de ce chantier même.

### Traitement des réserves précédentes

- **R3 (`technical-debt-solde.md` annoncé, absent)** — **levé, vérifié**. Le fichier existe
  (17 lignes), porte son préambule, la règle « une entrée soldée sort, elle n'est pas barrée », le
  renvoi à `dette.md` section « Solder » et un marqueur `*Aucune entrée soldée à ce jour.*`. Le lien
  markdown de `technical-debt.md:9` résout désormais. Les trois mentions « créé au premier solde »
  ont été retirées de façon cohérente (`grep -rn 'premier solde' skills/ todo/` → vide) : l'écart au
  brief signalé à l'utilisateur est refermé, pas seulement documenté.
- **R4 (justification écrite en trois endroits)** — **levé pour l'essentiel**. Le raisonnement
  complet ne vit plus qu'une fois, dans `dette.md` « Un état, pas un journal » ; `cloture.md:36` et
  `audit.md:74` n'en portent plus qu'un renvoi nommé. Reste une redite de la règle elle-même (pas de
  son pourquoi) entre `cloture.md:32-34` et `audit.md:71-73`, ce qui est le minimum pour que chaque
  fichier reste lisible seul. Coût futur ramené de trois formulations à une.
- **R5 (chemin d'écriture de l'abandon)** — **levé partiellement**. Le point 4 pose désormais
  « Une fois sur `base:` », le `git add .claude/implementation/todo/` et la raison du chemin d'échec.
  Le cas « garder la branche » reste ouvert : voir **R9**.
- **R6 (ordre du point 4 de l'Abandon)** — **levé, vérifié**. La proposition est remontée au point 3,
  la décision du sort du travail descendue au point 4, avec la règle « on décide **ici**, on écrit au
  point 4 » et sa raison. L'asymétrie de raisonnement avec le point 2 de la clôture est résorbée.
- **R7 (`todo/README.md` absent de l'arborescence)** — **levé, vérifié**. `SKILL.md:38` le liste,
  avec un commentaire de rôle. Les trois fichiers annoncés existent tous les trois.
- **R1** et **R2** restent levés (revérifiés : `git add` au point 2 et au point 3 ; ligne
  `> Dernière vérification : 2026-08-14 (chantier `dette-technique`)` à `technical-debt.md:13`, et
  section « Tête du registre » de `dette.md`).

### Qualité du contenu produit

- **R8 — la procédure d'alimentation ne lit que le *dernier* rapport d'audit, alors que rien
  n'oblige ce dernier à reprendre les constats survivants des sections antérieures.** `dette.md:108`
  (« Alimenter », point 1) dit : « Relire le **dernier** rapport d'audit et parcourir ses `R<n>` un
  par un ». Or le gabarit de `audit.md:85-131` n'impose **aucune** section « Traitement des réserves
  précédentes » : il exige une section par audit, les axes conformité / qualité / dette induite, et
  la numérotation continue — rien de plus. Un auditeur qui juge un correctif et ne relève que des
  constats neufs produit une dernière section où R1 à R4 n'apparaissent pas, alors qu'ils peuvent
  très bien survivre. L'orchestrateur qui applique `dette.md` à la lettre les perd alors sans une
  seule erreur. Ce chantier n'a pas été mordu parce que ses deux derniers rapports ont, par choix de
  l'auditeur et non par obligation, repris les réserves antérieures. Le brief, lui, écrit la
  contrepartie au singulier et sans restriction : « la complétude est vérifiable après coup par
  confrontation **rapport** ↔ `todo/` » — c'est le fichier entier, pas sa dernière section.
  **Pour lever** : écrire « le rapport d'audit **entier**, ses sections du plus ancien au plus
  récent » au point 1, ou rendre obligatoire dans le gabarit la reprise du sort de chaque `R<n>`
  antérieur. C'est le mode de défaillance silencieux que ce chantier existe pour supprimer, laissé
  ouvert d'un cran en amont.
- **R9 — le chemin d'écriture de l'abandon n'est fermé que sur une de ses deux branches.**
  `cloture.md:129-134` dit « **Une fois sur `base:`**, écrire l'entrée décidée au point 3, la mettre
  à l'index et la joindre au commit direct de l'archivage ». Seule la puce « *tout jeter* » du même
  point pose ce passage sur `base:` et ce commit direct (`archiver … en `base:` (commit direct)`).
  La puce « *garder la branche* » dit « ne rien supprimer, archiver seulement le suivi » sans dire ni
  où l'on est, ni qu'il y a un commit — et le point 2 vient précisément de committer sur `<slug>`.
  Un lecteur qui suit ce cas n'a donc aucun commit auquel « joindre » l'entrée, et le repli naturel
  (écrire sur `<slug>`) est exactement celui que le paragraphe suivant interdit. Le correctif de R5
  s'applique à la lettre au premier cas et se lit à contresens du second. Portée limitée — l'abandon
  est rare et l'orchestrateur est présent — mais c'est le même type d'échec silencieux que R1.
- **R10 — la note du suivi sur `technical-debt-solde.md` est périmée depuis l'étape 8.**
  `.claude/implementation/dette-technique.md`, `## État courant` : « **Notes** : le fichier
  `todo/technical-debt-solde.md` n'est créé qu'au premier solde — écart au brief signalé à
  l'utilisateur, laissé tel quel ». Le fichier existe depuis `343f180`, et l'écart est refermé
  (cf. R3). Le suivi part en `done/` à la clôture : c'est la version archivée qui portera cette
  contre-vérité, alors qu'aucun autre document ne la contredit explicitement. Constat de tenue de
  document, sans effet sur le code produit — mais le suivi est justement ce qu'on relit à froid.
- **R11 — deux scories de mise en forme laissées par l'édition de l'étape 8.** `dette.md:126-128`
  garde un repli de ligne cassé après suppression de « , créé au premier solde » (77 puis 20
  colonnes, là où le fichier remplit ~100) ; `audit.md:73` passe à 103 colonnes après réécriture,
  seul dépassement introduit par ce chantier dans un fichier qui tient les 100 ailleurs (les
  dépassements de `SKILL.md` sont tous préexistants, vérifié). Purement cosmétique, aucun effet de
  rendu.
- **Style** : conforme au voisinage pour le reste. `dette.md` reprend la structure de `audit.md` et
  `cloture.md` (séparateurs `---`, gras pour la règle, italique pour l'attribution, renvois par
  chemin relatif à `skills/implementation-tracker/`) ; `todo/README.md` et
  `todo/technical-debt-solde.md` suivent la forme des README voisins ; le registre respecte le
  modèle imposé par le brief, aux deux écarts décidés près (pas de numérotation, historique des
  soldes déporté). Rien d'autre à signaler.

### Dette induite

- La redite résiduelle de la règle « l'orchestrateur écrit, jamais l'auditeur » entre
  `cloture.md:32-34` et `audit.md:71-73` (reliquat de R4) : deux formulations à réviser ensemble,
  contre trois avant l'étape 8. C'est le motif de l'entrée n° 5 du registre lui-même ; le coût est
  assumé et réduit.
- Aucune abstraction créée sans nécessité, aucun couplage nouveau : `dette.md` porte tout le
  procédural, `SKILL.md`, `cloture.md` et `audit.md` n'y renvoient que par une ligne. La double mise
  à l'index (points 2 et 3 de la clôture) est redondante mais défensive, sans coût.
- R8, R9, R10 et R11 ne sont pas de la dette induite mais de la couverture incomplète ou de la tenue
  de document : ils portent sur du contenu que ce chantier vient d'écrire.

### Bloquants

Aucun. Les quatre critères de réussite sont atteints et vérifiés par exécution, le hors-périmètre est
respecté, aucun signal de dérive ne s'est matérialisé, et R3 à R7 sont traités (R5 partiellement).
R8 à R11 sont des réserves à trancher par l'utilisateur avant de clore — **R8 étant celle qui mérite
un arbitrage explicite**, puisqu'elle peut faire perdre silencieusement des entrées au registre que
ce chantier crée ; R9 vient ensuite ; R10 et R11 peuvent partir au registre ou être corrigées en une
ligne chacune.
