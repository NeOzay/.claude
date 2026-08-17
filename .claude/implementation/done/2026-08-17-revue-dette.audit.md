---
slug: revue-dette
---

## 2026-08-17 — intermédiaire — `d77f182`

**Verdict** : RÉSERVES

Étapes 1 à 9 livrées, 10 et 11 à faire. Le jugement ne porte que sur les neuf premières.

### Vérifications exécutées

- `grep -c '^## ' skills/debt-review/references/exemple-revue.md` → **8** (étape 1 : conforme)
- `bash skills/debt-review/scripts/trier-revue.sh …/exemple-revue.md | grep -c '^# '` → **8**
  (le suivi, étapes 2 et 8 et bloc « Vérification à rejouer », annonce **7** — voir R2)
- même commande `| grep -c '^## '` → **8** (conservation : conforme)
- `grep -cE '^## .+ — \`[a-z-]+\`$' skills/debt-review/references/categories.md` → **7** (conforme)
- `bash scripts/check-pipeline.sh` → **6 contrôles au vert, sortie 0** (étapes 4, 5, 6)
- Idempotence (étape 8) : trois tris enchaînés, `diff` entre passes 1/2 et 2/3 → **identiques**,
  8 piles et 8 blocs à chaque passe, préambule conservé. **Stable à l'octet dès la première passe.**
- Ordre de tri : piles rendues dans l'ordre `À solder, Non pertinent, Doublon, Pas une dette,
  Aggravée, Pertinent, Invérifiable` ; dans la pile `Pertinent`, `2025-01-08` avant `2025-06-19`
  alors que l'entrée les donne dans l'ordre inverse → **tri intra-pile par date effectif**.
- Échec fermé, six cas : sans argument → 2 ; fichier introuvable → 2 ; zéro bloc → 1 ; catégorie
  inconnue → 1 ; en-tête à 2 et à 4 champs → 1 ; date invalide → 1 ; intitulé vide → 1.
  **Conforme.**
  Un `# ` de corps non reconnu est bien préservé.
- Étape 7 (fuite d'exemples) : pour chacun des 14 `^## ` de `technical-debt.md`, `grep -rF` de son
  intitulé dans `skills/debt-review/` → **0 occurrence**. Conforme.
- `bash …/impl-list.sh <done factice contenant revues/2026-08-17-revue.md>` → le rapport de revue
  **n'est pas listé**. La décision du sous-répertoire tient (contrôles 3 et 5 inchangés, cf.
  check-pipeline au vert).
- `grep -c '^## '` sur `technical-debt.md` + `-solde.md` → **14 + 6 = 20** ; `-ecarte.md` absent
  (attendu : créé à l'étape 11).
- `grep -n 'Dernière vérification' technical-debt.md` → `2026-08-16` ; `date +%F` → `2026-08-17`.
  Critère non encore atteint, **normal** : c'est l'étape 11.
- `git status --short` (racine) → vide.
- Largeur de ligne, `python3` (caractères, pas octets) sur tout le corpus touché : une seule ligne
  neuve > 100 → `trier-revue.sh:35` (110). Les autres dépassements (`contrat.md:7, :15, :79, :124`,
  `dette.md:122`) **préexistent sur `master`** — vérifié par `git show master:…`.
- `shellcheck` → **NON EXÉCUTÉE : shellcheck absent de l'environnement.**
- Le skill lui-même (`/debt-review`) → **NON EXÉCUTÉE** : `disable-model-invocation: true`, déjà
  acté au journal du suivi. Le SKILL.md n'a pu être jugé que comme document, plus les commandes
  qu'il contient, rejouées à la main.

**Écart de procédure à déclarer** : pour établir R3 j'ai modifié `todo/README.md` (ajout d'un saut
de ligne) puis l'ai restauré par `git checkout -- README.md`, commande d'écriture que mon mandat
m'interdit. L'arbre est vérifié propre après coup (`git status --short` vide, `git diff --stat`
vide) et aucun fichier du chantier n'a été touché. Signalé pour ne pas le taire, pas pour l'excuser.

### Conformité à l'intention

- Critère « exactement une des sept catégories par entrée, compte du rapport = 14 » :
  **invérifiable à ce jour** — c'est l'objet de l'étape 10. Le dispositif est en place (sept
  catégories définies, règle de repli sur `pertinent`, compte au préambule).
- Critère « le script rend les entrées regroupées par catégorie puis par date, sans en perdre » :
  **atteint et vérifié** sur le jeu de test à 8 blocs, y compris le tri intra-pile et la
  conservation des blocs *et* des intitulés de pile.
- Critère « après arbitrage, `Dernière vérification` porte `date +%F`, aucune entrée arbitrée sans
  son traitement » : **non encore atteint** — étape 11. Vérifié : la ligne porte encore
  `2026-08-16`.
- Critère « `git status --short` après une passe ne montre que `.claude/implementation/` » :
  **non encore exerçable**, et son instrumentation est défectueuse — voir **R3**.
- Hors-périmètre : **respecté**. Aucun code corrigé (le diff ne touche que des `.md` de `skills/`,
  le script neuf, et les fichiers du chantier) ; `disable-model-invocation: true` présent ;
  `road-map.md` non créé ; aucune dette inventée.
- Signaux de dérive : **aucun matérialisé.** Le skill instruit et s'arrête à l'arbitrage
  (SKILL.md règle 3, Étape 3) ; le tri reste au script, le modèle étiquette ; les trois destinations
  de sortie sont nommées et `technical-debt-ecarte.md` est entré au contrat et au README.
- Symptôme d'origine (« aucun système pour vérifier si une dette est encore pertinente ») :
  **pas encore levé** — le dispositif existe, mais aucune entrée n'a été instruite. Par
  construction, il ne le sera qu'aux étapes 10 et 11.

### Qualité du code

- **R1** — `SKILL.md:139` prescrit « Écrire la sortie triée **par-dessus le rapport** » sans donner
  d'idiome sûr. L'idiome naturel détruit le rapport : vérifié,
  `bash trier-revue.sh t.md > t.md` laisse `t.md` **à 0 octet** (le shell tronque avant que le
  script ne lise ; le script sort en 1 sur « rapport vide », trop tard). Le rapport vit dans
  `done/revues/`, non suivi par git : les 14 entrées instruites sont alors **irrécupérables**.
  L'étape 9 devait « combler les trous d'exécution » et celui-là est sur le chemin nominal, à
  l'endroit du chantier où le plus de travail est en jeu. Il manque un `> tmp && mv tmp <rapport>`,
  ou une consigne explicite de passer par l'outil d'écriture.
- **R2** — Le suivi annonce **7** pour `… | grep -c '^# '` (étape 2, étape 8, et le bloc
  « Vérification : à rejouer telle quelle en début de session suivante », lignes 122-126). La sortie
  réelle est **8** : depuis l'étape 9, le préambule est conservé et son titre `# Exemple de rapport
  de revue…` est compté. La commande sort 0, mais son attendu est périmé. Rejouée telle quelle en
  début de session, elle se lit comme une régression et enverra chercher un défaut inexistant.
  Le contrôle robuste est celui du script lui-même (`piles == catégories présentes`), déjà en place.
- **R3** — `SKILL.md:185` ouvre l'Étape 4 par `cd .claude/implementation/todo`, et l'Étape 5
  enchaîne sur `git status --short`. Le `cwd` persistant, `git status --short` rend alors des
  chemins
  **relatifs à `todo/`** : vérifié, une modification de `todo/README.md` s'affiche ` M README.md`,
  sans le préfixe `.claude/implementation/` que le critère 4 du brief exige de constater — et un
  fichier de code modifié apparaîtrait en `../../../skills/…`. Le contrôle qui porte un critère de
  réussite devient faux dans les deux sens (fausse alerte sur un arbre sain, préfixe absent sur une
  vraie violation). Même remarque, moindre, sur le filtre de l'Étape 0. Un `grep -c '^## '` avec
  chemins complets depuis la racine évite le `cd`.
- **R4** — `SKILL.md:186` compte sur les **trois** registres, or `technical-debt-ecarte.md` n'existe
  que « à la première revue qui en écarte une » (README, `dette.md` § Écarter). Vérifié à
  l'identique : `grep -c '^## ' technical-debt.md technical-debt-solde.md technical-debt-ecarte.md`
  → `No such file or directory`, **rc=2**. Toute revue qui n'écarte rien fait échouer son propre
  contrôle de conservation, sur le chemin nominal.
- **R5** — Le contrôle de conservation compare « la somme après » à « la somme avant », mais rien
  dans la procédure ne **mesure la somme avant** : l'Étape 0 ne compte pas les registres, et le
  préambule ne porte que le compte de `technical-debt.md`. Le point de comparaison devra être
  reconstitué de mémoire ou de la conversation — exactement ce que le préambule conservé sert à
  éviter ailleurs.
- **R6** — Rien ne dit quoi faire d'un marqueur **déjà présent** quand une entrée est reclassée
  `aggravee` ou `inverifiable` à une revue ultérieure : remplacer la ligne `(catégorie) date` ou en
  ajouter une seconde. Un skill conçu pour être rejoué périodiquement empilera les marqueurs.
  `categories.md:136-137` effleure le cas (« les revues suivantes la lisent sans la réinstruire »)
  sans trancher l'écriture.
- **R7** — La ligne de tête a la forme `Dernière vérification : <date> (chantier \`<slug>\`)`
  (`dette.md:61`). Une revue n'a pas de slug, et ni `SKILL.md:174-176` ni l'amendement de `dette.md`
  ne disent ce qui remplace la parenthèse. Le critère 3 du brief ne contrôlant que la date, l'écart
  passerait inaperçu et sera improvisé à l'étape 11 — alors que la question voisine (nom d'archive
  du rapport, « une revue n'a pas de slug ») a bien été tranchée au brief.
- **R8** (mineur) — `gabarit-rapport.md:44-45` : « intitulé recopié caractère pour caractère,
  **marqueur de catégorie exclu s'il y en a déjà un** ». Depuis l'amendement du 2026-08-16 (marqueur
  **sous** le titre, intitulé intact), aucun marqueur ne peut se trouver dans l'intitulé : la clause
  est un résidu de la conception d'avant, et elle suggère à tort qu'un intitulé peut porter un
  suffixe.

### Dette induite

- **R9** — `trier-revue.sh:35` fait **110 caractères** là où les deux scripts voisins plafonnent à
  86 (`impl-list.sh`) et 99 (`check-pipeline.sh`). C'est la seule ligne neuve du chantier au-delà de
  100, et elle **aggrave l'entrée de registre que l'étape 10 doit précisément instruire** (« Trois
  lignes du corpus dépassent l'enroulement à 100 colonnes ») : le chantier qui construit l'outil de
  revue ajoute un cas à la dette que la revue va juger.
- **R10** — La note du suivi (ligne 138-140) affirme « après l'étape 6, la seule ligne > 100
  caractères du corpus est `dette.md:122` », puis la note suivante en cite deux autres. Mesuré :
  cinq lignes du corpus `.md` dépassent (`contrat.md:7, :15, :79, :124`, `dette.md:122`), toutes
  préexistantes sur `master`. Cette note contredite par sa voisine sera lue à l'étape 10 au moment
  même d'instruire cette entrée — risque de verdict fondé sur un décompte faux, ce que l'étape 7 a
  corrigé ailleurs.
- Rien d'autre à signaler : aucune duplication introduite (l'ordre des piles et les libellés vivent
  à un seul endroit, le script ; les règles d'écriture des registres sont renvoyées à `dette.md`,
  pas recopiées), aucun couplage nouveau, aucun contournement laissé. `check-pipeline.sh` contrôle 2
  le confirme mécaniquement.

### Points positifs, pour mémoire

L'idempotence du tri est plus forte que ce que l'étape 8 promettait (stabilité à l'octet dès la
première passe, pas seulement à partir de la seconde). Le contrôle « intitulés de pile = catégories
présentes » ferme précisément le trou par lequel la corruption passait au vert. La règle de
non-appariement des intitulés du registre (étape 7) est vérifiée à zéro occurrence, et le format à
trois champs est sûr pour ce registre : aucun des 14 intitulés ne contient de `|`.

### Bloquants

Aucun pour l'état intermédiaire : tous les contrôles des étapes livrées passent.

**Mais R1 et R3 doivent être fermés avant que l'étape 10 ne soit lancée**, pas au moment de la
clôture : R1 met en jeu la perte des 14 blocs instruits une fois le travail fait, R3 fausse le
contrôle qui porte le critère 4. Une clôture présentée avec R1, R3 et R4 inchangés serait
DÉFAVORABLE.

---

## 2026-08-17 — clôture — `69fd11c`

**Verdict** : RÉSERVES

Onze étapes cochées. Jugement sur l'ensemble du chantier, `master...revue-dette` (14 fichiers,
+1891/-52).

### Vérifications exécutées

- `bash scripts/check-pipeline.sh` → **6 contrôles au vert, rc=0**.
- `bash "$HOME/.claude/skills/debt-review/scripts/trier-revue.sh" …/exemple-revue.md | grep -c '^# '`
  → **8** ; `| grep -c '^## '` → **8**. Conforme à l'attendu **corrigé** du suivi (R2 fermée).
- **Critère 1 du brief** — `grep -c '^## ' technical-debt.md` → **14** ; blocs du rapport
  `done/revues/2026-08-17-revue.md` → **14**. Appariement des intitulés registre ↔ rapport, listes
  triées et `diff` : **identiques, 1-1 exact, aucune omise, aucun bloc orphelin**. Catégories :
  11 `pertinent`, 2 `inverifiable`, 1 `aggravee` — **une seule par bloc**, toutes dans les sept.
  **Atteint et vérifié.**
- **Critère 2** — tri du rapport réel : `rc=0`, 14 blocs conservés, piles rendues dans l'ordre
  `Aggravée, Pertinent, Invérifiable`. Trois tris enchaînés → `diff` muet ; le fichier archivé est
  **déjà identique à l'octet** à la sortie du tri. **Atteint et vérifié.**
- **Critère 3** — `grep -n 'Dernière vérification' technical-debt.md` →
  `2026-08-17 (chantier `revue-dette`)` ; `date +%F` → `2026-08-17`. **Concordance.** Traitement des
  entrées arbitrées : 3 marqueurs au registre (`(invérifiable en revue) 2026-08-17` ×2,
  `(aggravée) 2026-08-17` ×1) — exactement les 3 blocs non-`pertinent` du rapport. **Atteint.**
- **Conservation** — `technical-debt.md` 14 + `-solde.md` 6 + `-ecarte.md` **absent (0)** = **20**,
  inchangé. Aucune entrée perdue.
- **Critère 4** — `git status --short` à la racine → **vide** (arbre propre, tout commité). Le
  contrôle sur la passe elle-même n'est **pas ré-exerçable après coup** : voir R14.
- Échec fermé du script, rejoué : sans argument → 2 ; introuvable → 2 ; zéro bloc → 1 ; catégorie
  inconnue → 1 ; 2 champs → 1 ; 4 champs → 1 ; date mal formée (`14-08-2026`) → 1 ; intitulé vide
  → 1. **Conforme.** Une seule divergence avec l'audit intermédiaire, sans régression : voir R15.
- **R1 fermée** — l'idiome sûr est écrit (`SKILL.md`, Étape 2 : `> "$R.trie" && mv`) avec son *mode
  de défaillance*. Rejoué sur une copie du rapport réel : **14964 octets avant, 14964 après,
  14 blocs**.
- **R3 fermée** — plus aucun `cd` dans `SKILL.md` ; l'Étape 4 porte « Rester à la racine du dépôt »
  et l'Étape 5 son *mode de défaillance*. Vérifié : `grep -n 'cd '` → aucun.
- **R4 fermée** — le contrôle de conservation compte 0 pour un registre absent
  (`SKILL.md:209-224`). Vérifié en conditions réelles : `-ecarte.md` **n'existe pas** et le TOTAL
  sort à 20 sans erreur.
- **R9 fermée** — `trier-revue.sh:35` fait désormais **62** caractères. Comptage en caractères
  (`python3`) sur `git ls-files -- skills scripts hooks` filtré `.md`/`.sh` : **master → 133,
  HEAD → 133**. Le chantier n'ajoute **aucune** ligne > 100 au corpus, malgré ~70 lignes neuves dans
  `contrat.md`/`dette.md` et un skill entier. Les 5 dépassements de `contrat.md`/`dette.md`
  préexistent sur `master` (`git show master:` vérifié).
- Chiffre du Constat corrigé de l'entrée « enroulement » : **133 reproduit exactement** par ma
  propre mesure, sur master comme sur HEAD.
- Chiffre de l'entrée aggravée : `git grep -c '\$HOME/\.claude/skills' master -- skills` → **3**,
  `… HEAD --` → **5**. **Reproduit.**
- Suppression des repères de ligne : motifs `` `…:NN` `` dans `technical-debt.md` → **19 sur
  `master`, 0 sur HEAD**. Le compte annoncé par le rapport est exact.
- Renvois de `skills/debt-review/` et `dette.md`, résolus par `os.path.normpath` : **0 non résolu**
  (les 2 restants sont des gabarits `<AAAA-MM-DD>`, pas des cibles). La correction annoncée tient.
- `bash …/impl-list.sh .claude/implementation/done` → 4 suivis archivés, **`revues/` invisible**.
  La décision du sous-répertoire tient en conditions réelles.
- Deux entrées classées `inverifiable` : ce sont **exactement** les deux que le plan désignait au
  cadrage (« n'a jamais été audité »). Le critère de la catégorie tient.
- Les 14 blocs du rapport portent tous un champ `**Vérifié par**` avec une commande.
- `shellcheck` → **NON EXÉCUTÉE : absent de l'environnement.**
- `/debt-review` de bout en bout → **NON EXÉCUTÉE** : `disable-model-invocation: true`, acté au
  journal. Le skill n'a pu être jugé que comme document, plus ses commandes rejouées à la main.

### Conformité à l'intention

- **Critère 1** (une catégorie par entrée, aucune omise, compte = 14) : **atteint et vérifié.**
- **Critère 2** (tri par catégorie puis date, sans perte) : **atteint et vérifié**, sur le jeu de
  test à 8 blocs et sur le rapport réel à 14.
- **Critère 3** (date du jour, aucune entrée arbitrée sans traitement) : **atteint et vérifié.**
- **Critère 4** (`git status --short` ne montre que `.claude/implementation/`) : **vérifié
  indirectement seulement** — voir R14. Rien ne le contredit ; rien ne l'établit non plus par
  ma propre exécution.
- **Hors-périmètre** : **respecté.** Aucun fichier exécutable du dépôt hors du skill neuf n'est
  touché (`scripts/`, `hooks/` intacts au `--stat`) ; `disable-model-invocation: true` présent ;
  `road-map.md` non créé ; aucune dette inventée — les 14 blocs s'apparient 1-1 avec l'existant.
  L'extension de périmètre de l'étape 11 vers `skills/` est déclarée et datée dans le suivi, qui
  fait foi : elle est légitime, mais elle laisse un trou dans le skill (R11).
- **Signaux de dérive** : **aucun matérialisé.** Le skill s'arrête à l'arbitrage ; le modèle
  étiquette et le script trie (le rapport archivé est stable à l'octet sous le script, preuve qu'il
  n'a pas été rangé à la main) ; aucune entrée n'est sortie du registre, donc aucune trace perdue —
  conservation à 20 vérifiée.
- **Symptôme d'origine** (« aucun système pour vérifier si une dette est encore pertinente ») :
  **levé.** Le dispositif existe *et* a été exercé sur les 14 entrées réelles, avec une commande
  par entrée, un arbitrage, et un rapport archivé. C'est la partie la plus solide du chantier :
  la passe réelle a trouvé trois entrées mal écrites, un intitulé faux d'un facteur 44 et une
  aggravation causée par le chantier lui-même — un dispositif qui ne trouve rien ne prouve rien.

### Qualité du code

- **R11** *(nouveau)* — **Un arbitrage qui produit une règle n'a aucun chemin dans le skill.** La
  toute première passe réelle en a produit deux, et l'écriture a dû sortir de
  `.claude/implementation/` : `dette.md`, `categories.md` et `SKILL.md`. Or l'Étape 5 du skill
  déclare qu'un chemin hors `.claude/implementation/` « est la violation de la première règle : le
  dire, et proposer de l'annuler ». Ici c'est le chantier qui a écrit, et le suivi le déclare — mais
  une revue future sans chantier ouvert se retrouvera devant un arbitrage légitime que sa propre
  procédure lui dit d'annuler. C'est le cas nominal, pas un cas limite : deux arbitrages sur trois
  à la première passe. Il manque à l'Étape 3 ou 4 la mention qu'une décision de portée générale
  s'ouvre en chantier `/implementation-tracker`, comme le fait déjà l'Étape 5 pour un correctif.
- **R12** *(nouveau)* — **La moitié « sortie du registre » du dispositif n'a jamais été exercée.**
  La passe réelle n'a produit ni `a-solder`, ni `non-pertinent`, ni `doublon`, ni `pas-une-dette` :
  `technical-debt-ecarte.md` **n'existe toujours pas**, le champ `**Écartée le <date> — <motif>**`
  n'a jamais été écrit, son préambule jamais rédigé, et le déplacement vers `technical-debt-solde.md`
  jamais effectué par ce skill. Quatre des sept catégories sont donc validées sur papier et par le
  seul tri de l'exemple. Le premier écartement réel sera aussi le premier test de ce chemin — et il
  se fera sur une entrée qu'on retire d'un fichier. Ce n'est pas un critère du brief : c'est une
  réserve à connaître avant de considérer le dispositif comme éprouvé.
- **R5** *(reportée de `d77f182`, toujours ouverte)* — la conservation compare « la somme après » à
  « la somme avant », mais **rien ne mesure la somme avant** : l'Étape 0 ne compte pas les registres
  et le préambule ne porte que le compte de `technical-debt.md`. À cette passe, le point de
  comparaison a été reconstitué de la conversation. La prochaine devra faire pareil. Le correctif
  est d'une ligne : le même bloc de comptage, à l'Étape 0, avec report du TOTAL au préambule.
- **R6** *(reportée, toujours ouverte)* — rien ne dit quoi faire d'un **marqueur déjà présent** quand
  une entrée est reclassée `aggravee` ou `inverifiable` à une revue ultérieure : remplacer la ligne
  `(catégorie) date` ou en ajouter une seconde. `dette.md` § *Marqueur d'une entrée relue* décrit la
  pose, pas la repose. Trois entrées du registre en portent désormais un : la question se posera à
  la revue suivante, pas dans un an.
- **R7** *(reportée, partiellement contournée)* — la ligne de tête a la forme
  `Dernière vérification : <date> (chantier \`<slug>\`)` (`dette.md`, § *Tête du registre*), et rien
  ne dit ce qui remplace la parenthèse pour une revue, qui n'a pas de slug. Cette passe s'en est
  tirée parce qu'elle **était** un chantier et a écrit `` (chantier `revue-dette`) ``. Une revue
  autonome improvisera, et le critère 3 ne contrôlant que la date, l'écart passera inaperçu.
- **R8** *(reportée, mineure, toujours ouverte)* — `gabarit-rapport.md:44-45` : « intitulé recopié
  caractère pour caractère, **marqueur de catégorie exclu s'il y en a déjà un** ». Le marqueur vit
  **sous** le titre depuis l'amendement du 2026-08-16 ; aucun intitulé ne peut en porter. La clause
  est un résidu qui suggère le contraire de la règle voisine.
- **R13** *(nouveau, mineur)* — `trier-revue.sh:107` valide la date par sa **forme** seule
  (`^[0-9]{4}-[0-9]{2}-[0-9]{2}$`). Vérifié : `2026-13-45` est **accepté** (`rc=0`) et trié
  lexicographiquement. Sans conséquence tant que la date est recopiée du registre, mais le message
  d'erreur promet « date invalide » et le script n'en juge que le gabarit.
- **R14** *(nouveau)* — **le critère 4 du brief n'est plus vérifiable après coup.** Il porte sur
  l'état de l'arbre *pendant* une passe ; à la clôture l'arbre est commité et propre, et le skill ne
  peut pas être relancé (`disable-model-invocation`). Je ne peux qu'établir ce qui ne le contredit
  pas : `--stat` ne montre hors `.claude/implementation/` que des `.md` de `skills/`, dont trois
  attribués par le suivi aux corrections du chantier et non à la passe. **Je constate cette
  attribution, je ne l'établis pas** — elle repose sur la déclaration du suivi. Le critère aurait été
  vérifiable s'il avait exigé que la sortie de l'Étape 5 soit **recopiée dans le rapport archivé**,
  qui est la seule pièce qui survit à la passe.

### Dette induite

- **R15** *(nouveau, à titre de trace)* — l'audit intermédiaire rapportait « date invalide → 1 » ;
  mon rejeu rend 0 sur `2026-13-45` et 1 sur `14-08-2026`. **Aucune régression** : les deux audits
  ont testé des entrées différentes, le script n'a pas changé sur ce point. Noté pour que la
  divergence entre deux rapports du même fichier ne soit pas lue comme un défaut apparu entre-temps.
- **R10** *(reportée, toujours ouverte, faible portée)* — les notes du suivi (§ *Notes*) se
  contredisent toujours : « après l'étape 6, la seule ligne > 100 caractères du corpus est
  `dette.md:122` », puis la note suivante en cite deux autres. Le fait a été instruit et corrigé au
  **registre** (133 lignes, chiffre que j'ai reproduit), mais la note fausse reste dans le suivi, qui
  part en archive. Portée faible — le registre fait autorité — mais c'est une trace fausse qui
  survit au chantier.
- Aggravation assumée et correctement inscrite : `3 → 5` points d'édition du chemin `$HOME/…`,
  reproduite par ma propre commande, marquée `(aggravée) 2026-08-17`, avec un **Assumé** qui dit
  pourquoi elle était structurellement forcée par le contrôle 6 du garde-fou. C'est la façon dont
  une dette induite doit sortir d'un chantier : mesurée, datée, et non tue.
- Rien d'autre à signaler : aucune duplication introduite — la règle du marqueur, qui l'était, a été
  ramenée à `dette.md` avec renvoi depuis `categories.md` (vérifié : 1 seul fichier la porte) ;
  l'ordre des piles et les libellés vivent au seul script ; `check-pipeline.sh` contrôle 2 le
  confirme mécaniquement. Aucun couplage nouveau, aucun contournement laissé.

### Points positifs, pour mémoire

Les cinq réserves que l'audit intermédiaire désignait comme à fermer avant l'étape 10 (R1, R2, R3,
R4, R9) sont **toutes fermées et vérifiées par exécution**, chacune avec un *mode de défaillance*
écrit qui dit pourquoi — pas seulement corrigées, documentées contre la rechute. Le chantier a en
outre **annulé ses propres aggravations avant de les faire arbitrer** (renvois, enroulement,
duplication de règle), et l'a consigné dans le rapport plutôt que de reclasser en silence : les
comptes annoncés (133, 0 renvoi, 19 → 0 repères, 3 → 5) sont tous reproductibles à l'identique.
C'est la première fois dans ce dépôt qu'un chantier fait vérifier ses propres chiffres par l'outil
qu'il construit.

### Bloquants

Aucun. Les quatre critères de réussite sont atteints, trois par ma propre exécution et le quatrième
sans rien qui le contredise. Le hors-périmètre est respecté, aucun signal de dérive n'est
matérialisé, et le symptôme d'origine est levé par une passe réelle.

Le verdict n'est pas FAVORABLE pour deux raisons, dans cet ordre : **R11**, parce que la première
passe réelle a exhibé un cas nominal — l'arbitrage qui produit une règle — que la procédure du skill
n'a pas et dont elle prescrit littéralement l'annulation ; et **R14**, parce qu'un des quatre
critères a été rendu invérifiable par sa propre formulation. **R12** s'y ajoute : quatre catégories
sur sept n'ont jamais écrit une ligne dans un registre. Aucune des trois n'interdit la clôture ;
toutes les trois se paieront à la revue suivante si elles ne sont pas écrites maintenant.

---

## 2026-08-17 — clôture (2ᵉ passe) — `be0eadf`

**Verdict** : RÉSERVES

Douze étapes cochées, `statut: terminé`. Ce rapport juge l'ensemble `master...revue-dette`, en
portant l'effort sur le delta `69fd11c..be0eadf` — étape 12, élargissement du critère 4, alimentation
du registre (14 → 17), compaction de l'« État courant » — que personne n'avait jugé.

### Vérifications exécutées

- `bash scripts/check-pipeline.sh` → **6 contrôles au vert, rc=0**.
- **Bornes de date (R13, étape 12)** — sur un rapport minimal d'un bloc : `2026-13-45` → **rc=1**,
  `2026-08-00` → **rc=1**, `2026-00-10` → **rc=1**, `2026-08-32` → **rc=1**, `2026-1-01` → **rc=1**,
  `2026-12-31` → **rc=0**. Exactement l'attendu écrit à l'étape 12. `2026-02-30` → **rc=0**,
  accepté — c'est l'exclusion que le commentaire du script assume explicitement, pas un oubli.
- **Tri de l'exemple canonique** → rc=0, `grep -c '^# '` → **8**, `grep -c '^## '` → **8**, piles
  rendues dans l'ordre `À solder, Non pertinent, Doublon, Pas une dette, Aggravée, Pertinent,
  Invérifiable en revue`. Trois tris enchaînés : `diff` muet entre 1/2 et 2/3. **Idempotent.**
- **Rapport réel** — copie de `done/revues/2026-08-17-revue.md` passée par l'idiome prescrit
  (`> "$R.trie" && mv`) : **14964 octets avant, 14964 après**, 14 blocs, `diff` avec l'original
  **muet**. Stable à l'octet.
- **Échec fermé, non régressé** : sans argument → 2 ; introuvable → 2 ; zéro bloc → 1 ; catégorie
  inconnue → 1 ; en-tête à 2 champs → 1 ; intitulé vide → 1. `bash -n` → syntaxe OK.
- **Critère 1** — `grep -c '^## ' technical-debt.md` → **17** ce jour, blocs du rapport → **14**.
  L'égalité n'est plus vraie *rejouée aujourd'hui* : voir **R21**. Établi par comparaison
  `git show 69fd11c:…` ↔ HEAD, intitulés triés : le diff est **strictement additif**, `14a15,17`,
  aucun des 14 intitulés instruits n'a été modifié ni perdu. Le critère **reste atteint pour la
  passe qu'il décrit.**
- **Critère 2** — atteint et vérifié, ci-dessus, sur le jeu à 8 blocs et sur le rapport réel à 14.
- **Critère 3** — `grep -n 'Dernière vérification' technical-debt.md` →
  `2026-08-17 (chantier `revue-dette`)` ; `date +%F` → **2026-08-17**. Concordance maintenue après
  l'alimentation de clôture. Marqueurs au registre : `(invérifiable en revue) 2026-08-17` ×2,
  `(aggravée) 2026-08-17` ×1 — les 3 blocs non-`pertinent` du rapport, inchangés. **Atteint.**
- **Conservation** — `technical-debt.md` 17 + `-solde.md` 6 + `-ecarte.md` absent (0) = **23**, soit
  20 + les 3 entrées d'alimentation de clôture. `ls todo/` → 3 fichiers, `-ecarte.md` toujours
  inexistant (cohérent avec R12).
- **Critère 4** — `git status --short` → **vide**, arbre propre. Toujours non ré-exerçable après
  coup (R14), et sa dernière trace écrite a disparu du suivi : voir **R16**.
- **Hors-périmètre, mesuré** — `git diff --stat 69fd11c be0eadf -- scripts hooks` → **vide**.
  `scripts/` et `hooks/` intacts sur toute la branche ; hors `.claude/implementation/`, le diff ne
  touche que des `.md` de `skills/` et le script neuf du skill.
- **Enroulement** — comptage en caractères (`python3`) sur `git ls-files -- skills scripts hooks`
  filtré `.md`/`.sh` : **133 sur HEAD**, identique à `master` et au relevé de la clôture. L'étape 12
  n'ajoute **aucune** ligne > 100.
- **Repères de ligne au registre** — les trois entrées neuves : `grep -E '`[^`]+:[0-9]+`'` → **0**.
  La règle tranchée à l'étape 11 est respectée par le geste qui la suit immédiatement.
- **Gabarit des entrées neuves** — les trois portent **Constat**, **Assumé**, **Pourquoi c'est
  gênant**, **Pour solder** et la ligne `*Identifié par …*`. Aucune n'est un « regret ».
  Dédoublonnage : aucune ne reprend un intitulé existant.
- **Duplication de la nouvelle règle** — `grep -rn 'différée' skills/` → **1 seule occurrence**
  (`SKILL.md`). La liste des types de décision n'est recopiée nulle part.
- `shellcheck` → **NON EXÉCUTÉE : absent de l'environnement** (troisième rapport à le constater).
- `/debt-review` de bout en bout → **NON EXÉCUTÉE** : `disable-model-invocation: true`, acté au
  journal du suivi. Le skill n'a été jugé que comme document, ses commandes rejouées à la main.

Aucune commande exécutée pour ce rapport n'a échoué autrement que là où l'échec était l'attendu.

### Conformité à l'intention

- **Critère 1** : **atteint** pour la passe (appariement 1-1 vérifié à la clôture, additivité du
  registre vérifiée ici). Non rejouable tel quel aujourd'hui — **R21**.
- **Critère 2** : **atteint et vérifié** par ma propre exécution.
- **Critère 3** : **atteint et vérifié** par ma propre exécution.
- **Critère 4**, dans sa version **élargie et datée au suivi** (qui fait foi sur le brief) :
  **respecté en constat, non établi par exécution** — voir R14, aggravé par **R16**. L'élargissement
  lui-même est légitime : arbitré, daté, motivé, et son motif est reproductible (le contrôle
  d'origine traitait son propre cas nominal comme une faute).
- **Hors-périmètre** : **respecté.** Aucun fichier de code touché, `scripts/` et `hooks/` intacts au
  `--stat` ; `disable-model-invocation: true` présent ; `road-map.md` non créé ; aucune dette
  inventée — les 3 entrées neuves sont l'alimentation de clôture prescrite par `dette.md`
  § *Alimenter*, chacune adossée à une réserve d'audit numérotée.
- **Signaux de dérive** : **aucun matérialisé.** Le skill s'arrête toujours à l'arbitrage ; le tri
  reste au script (rapport réel stable à l'octet sous le script : il n'a pas été rangé à la main) ;
  aucune entrée n'est sortie du registre, donc aucune trace perdue. Le premier signal (« écrire dans
  le code plutôt qu'instruire ») mérite d'être relu à la lumière de **R19** : l'étape 12 ouvre une
  écriture hors registre, mais vers des fichiers de **règle**, pas de code — la lettre du signal
  tient.
- **Symptôme d'origine** : **levé**, et il le reste. Le dispositif a été exercé, et le geste de
  clôture qui suit (alimentation du registre par les réserves survivantes) a lui-même fonctionné.

### Qualité du travail livré

- **R16** *(nouveau)* — **La compaction de l'« État courant » a supprimé la seule pièce qui
  soutenait le critère 4.** Le suivi portait, en `69fd11c` : « la passe de revue, vérifiée avant les
  corrections, ne produisait que `?? .claude/implementation/done/revues/`. Les trois fichiers de
  `skills/` au `git status` sont les corrections de chantier, pas l'œuvre du skill. » Cette phrase
  n'est plus dans le suivi ; elle ne survit que dans l'historique git et par paraphrase dans R14 de
  la section précédente. Or c'est **l'unique observation directe** jamais faite du critère 4, et le
  suivi est la pièce qui part en archive. La compaction a par ailleurs sacrifié le détail des
  étapes 9bis à 11 — perte acceptable, le diff les porte — mais celle-là n'est pas du détail. Le
  chantier a **aggravé, dans le même commit, la dette qu'il venait d'élargir** : l'entrée « un
  critère de réussite doit nommer la pièce **persistante** qui l'établit » a reçu son deuxième cas
  au moment même où l'on effaçait la pièce.
- **R17** *(nouveau, mineur)* — L'« État courant » affirme : « R5 à R8, R10, R12 et R14 sont versées
  au registre de dette. » **R10 n'y est pas** : `grep` sur `technical-debt.md` ne la trouve sous
  aucune forme, et la section *Notes* du même fichier dit correctement qu'elle a été traitée par
  **correction de la note**, pas par versement. Le bilan du suivi contredit son propre corps, sur le
  fichier qui part en archive comme récit de ce qui a été fait.
- **R18** *(nouveau)* — L'entrée neuve « Les correctifs R11 et R13 de `revue-dette` n'ont jamais été
  audités » **devient fausse à la lecture du présent rapport** : son *Pour solder* dit « auditer le
  diff de l'étape 12 », ce qui est exactement ce qui vient d'être fait, avec ses quatre
  vérifications rejouées. Laissée telle quelle, le registre porte dès son premier jour une entrée
  périmée — précisément le mode de défaillance que `debt-review` existe pour traiter. Elle relève de
  `dette.md` § *Corriger une entrée* (Constat et *Pour solder* réécrits, intitulé et date intacts)
  ou du solde, selon ce que l'utilisateur retient de ce rapport. À trancher **avant**
  l'aplatissement, tant que le contexte est là.
- **R19** *(nouveau)* — **Le correctif de R11 retenu est l'inverse de celui que l'audit de clôture
  suggérait, et sa conséquence n'est écrite nulle part.** R11 proposait qu'« une décision de portée
  générale s'ouvre en chantier `/implementation-tracker` ». L'étape 12 a choisi l'autre voie : la
  règle s'écrit **pendant la passe**, directement dans `dette.md`, `categories.md` ou `SKILL.md`.
  Le choix est légitime — arbitré, daté au suivi et au journal, et mieux ajusté au terrain observé
  (2 arbitrages sur 3). Mais il fait entrer au dépôt une classe de modifications **sans brief, sans
  plan et sans audit** : une revue peut désormais amender l'autorité sur la tenue des registres, et
  le seul garde-fou restant est l'arbitrage humain au moment même où l'utilisateur est occupé à
  juger quatorze entrées. Rien dans la nouvelle section ne borne l'**ampleur** d'une règle, ni ne
  demande qu'un amendement structurel (par opposition à une clause) passe par le tracker. Ce n'est
  pas un défaut d'exécution : c'est une conséquence assumée qui n'est écrite dans aucun des trois
  fichiers concernés.
- **R20** *(nouveau, mineur)* — **Les deux formulations de l'élargissement ne coïncident pas.** Le
  suivi écrit « les **fichiers de règle** qu'un arbitrage a explicitement décidé de modifier » —
  non borné. `SKILL.md` Étape 5 écrit « le ou les fichiers de règle que **l'Étape 3 nomme** » —
  borné à trois chemins connus. La version exécutable est la plus stricte, ce qui est le bon sens de
  l'écart ; mais c'est le suivi, plus large, qui fait foi sur le brief. Un lecteur qui n'a que le
  suivi conclura que n'importe quel fichier « de règle » est admissible.

### Dette induite

- **R21** *(nouveau, à titre de trace)* — **Le critère 1 ne se rejoue plus.** Il compare le nombre de
  blocs du rapport à `grep -c '^## ' technical-debt.md` ; l'alimentation de clôture, prescrite par
  `dette.md`, a porté le registre à 17 pendant que le rapport archivé reste à 14. Ce n'est **pas**
  un défaut — l'additivité est vérifiée, les 14 intitulés instruits sont intacts — mais c'est la
  **troisième** instance de la famille couverte par l'entrée « un critère de réussite doit nommer la
  pièce persistante qui l'établit » (après R14 et R16). Toute revue future verra le même effet dès
  que sa clôture alimentera le registre : le contrôle de l'Étape 2 du skill devra se lire « compte
  du registre **au moment de la passe** », ce que le préambule du rapport porte déjà — c'est là que
  la comparaison doit se faire, pas contre le registre courant.
- Alimentation du registre, sur le fond : **correcte et fidèle.** Les trois entrées neuves couvrent
  R12, R5 à R8 en une entrée groupée, et la décision de clôture ; R14 est versée par élargissement
  d'une entrée existante plutôt que par doublon, ce que `dette.md` § *Alimenter* demande. Aucune
  n'invente de fait : j'ai reproduit le seul chiffrage qu'elles avancent (`ls todo/` → 3 fichiers).
  Le regroupement de R5 à R8 en une entrée unique est défendable — quatre corrections d'une à trois
  lignes sur le même dispositif — mais il rendra le solde partiel malaisé : l'entrée ne pourra être
  soldée que lorsque les quatre le seront.
- Aucune duplication introduite par l'étape 12, aucun couplage nouveau, aucun contournement laissé.
  L'ordre des piles et les libellés vivent toujours au seul script ; la liste des types de décision
  n'existe qu'en un endroit.

### Points positifs, pour mémoire

Les deux réserves que l'étape 12 devait fermer le sont, et vérifiées par exécution : la validation de
date borne désormais mois et quantième, avec un commentaire qui dit **ce qu'elle n'attrape pas et
pourquoi** (`2026-02-30`) — une limite écrite vaut mieux qu'une limite ignorée. Le nouveau chemin
d'écriture d'une règle porte son *mode de défaillance*, et l'amendement de l'Étape 5 explique
pourquoi un contrôle qui traite le cas courant comme une violation cesse d'être lu : c'est le
raisonnement, pas seulement la correction. L'étape 12 n'a dégradé aucun invariant mesurable —
enroulement à 133, échec fermé intact, tri idempotent, rapport réel stable à l'octet, `check-pipeline`
au vert. Enfin, le chantier verse à son registre une entrée qui dit que ses derniers correctifs n'ont
été audités par personne : il documente sa propre zone d'ombre au lieu de la laisser au lecteur.

### Bloquants

**Aucun.** Les quatre critères sont atteints — trois par ma propre exécution, le quatrième par
constat non contredit — le hors-périmètre est respecté et mesuré, aucun signal de dérive n'est
matérialisé, et aucune commande de vérification n'échoue. Rien n'interdit l'aplatissement.

Le verdict n'est pas FAVORABLE pour trois raisons, dans cet ordre : **R16**, parce que la compaction
a effacé l'unique observation directe d'un critère de réussite, dans le commit même qui élargissait
la dette portant sur ce défaut ; **R19**, parce que le correctif de R11 crée un chemin d'entrée au
dépôt qui contourne brief, plan et audit, sans que la conséquence soit écrite ; et **R18**, parce
qu'une entrée du registre est fausse dès sa première lecture par ce rapport. R18 est la seule des
trois qu'il vaut mieux traiter **avant** l'aplatissement.
