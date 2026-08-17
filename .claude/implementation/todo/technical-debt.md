# Dette technique

Ce document recense ce qui a été **délibérément laissé de côté**, avec la raison et ce qu'il
faudrait faire pour solder. Il ne liste que de la dette constatée et vérifiée dans le dépôt — pas
des idées d'amélioration.

Chaque entrée indique le chantier qui l'a identifiée. Entrées ordonnées de la plus ancienne à la
plus récente. Une entrée soldée est retirée d'ici et déplacée dans
[technical-debt-solde.md](technical-debt-solde.md), pas barrée.

Procédure, gabarit et règle de solde : `skills/implementation-tracker/references/dette.md`.

> Dernière vérification : 2026-08-17 (chantier `revue-dette`)

---

## 2026-08-14 — Les patterns de sécurité de `git-pre-commit-audit` ne sont plus branchés

**Constat** — le skill a été débranché vers `archive/git-pre-commit-audit/` et n'est donc chargé ni
par le modèle ni par l'utilisateur. Ses neuf annexes sont intactes : `security-patterns.md` et huit
grilles par langage (`lang-js-ts`, `lang-python`, `lang-php`, `lang-go`, `lang-java-kotlin`,
`lang-sql`, `lang-infra`, `lang-lua-neovim`).

**Assumé** : le débranchement était le but du chantier — le skill ne lisait ni le brief ni les
critères de réussite, d'où son remplacement par `agents/implementation-auditor.md`. La reprise des
patterns était hors-périmètre, écrite au brief.

**Pourquoi c'est gênant** — l'auditeur juge la conformité à l'intention et la qualité du code, mais
ne fait aucune détection de secrets ni de patterns de sécurité par langage. Cette capacité existe,
vérifiée, et n'est plus appelée par rien.

**Pour solder** — reprendre les grilles dans un chantier dédié, soit comme axe supplémentaire de
l'auditeur, soit comme skill séparé de pré-commit.

*Identifié par `audit-integre`, hors-périmètre assumé au brief.*

---

## 2026-08-14 — Une étape corrective née d'un audit ne peut pas être cochée avant l'audit

**Constat** — `references/cloture.md` demande, sous « Vérifier ensuite que toutes les étapes sont
cochées », que **toutes** les étapes le soient avant d'auditer. Or une étape née d'un audit
précédent a pour vérification « nouvel audit complet FAVORABLE », qui ne peut être satisfaite
qu'après. L'étape est donc `[>]` au moment où l'audit
tourne — c'est ce qui s'est passé pour l'étape 8 d'`audit-integre`.

**Pourquoi c'est gênant** — l'ordre correct (auditer, puis cocher) fonctionne, mais l'appelant doit
y penser à chaque fois. Chaque étape corrective née d'un audit rejouera la même gêne, et la règle
écrite dit littéralement le contraire de ce qu'il faut faire.

**Pour solder** — formuler ces étapes avec une vérification portant sur le **correctif** plutôt que
sur le verdict à venir (`grep -n "rev-parse" agents/implementation-auditor.md`), et le dire dans
`cloture.md`.

**Élargi le 2026-08-14 par `contrat-pipeline`** — le même ordonnancement rend **structurellement
invérifiable** tout critère de réussite portant sur le registre de dette. Le solde s'écrit au point 2
de `cloture.md`, donc après l'audit : aucun audit ne pourra jamais constater que les entrées sont
passées dans `technical-debt-solde.md`. Les trois audits du chantier ont chacun signalé ce critère
comme non atteint, sans qu'aucune correction soit possible.

**Pour solder, complété** — les critères de réussite portant sur un geste postérieur à l'audit
doivent être écrits comme tels au brief, ou déplacés vers une vérification post-clôture. La
formulation actuelle oblige tout auditeur à rendre `RÉSERVES` sur un point que le dispositif interdit
d'atteindre au moment où il juge.

*Identifié par `audit-integre`, R8 du rapport d'audit ; élargi par `contrat-pipeline`, R3 puis R13.*

---

## 2026-08-14 — Les correctifs de l'étape 9 de `dette-technique` n'ont jamais été audités

(invérifiable en revue) 2026-08-17

**Constat** — le chantier `dette-technique` s'est clos sur le verdict `RÉSERVES` de `343f180`. Ses
quatre derniers correctifs (R8 lecture du rapport entier, R9 chemin d'écriture de l'abandon dans le
cas *garder la branche*, R10 note périmée, R11 mise en forme) ont été écrits **après** cet audit et
n'ont été jugés par personne. `references/audit.md` demandait de « relancer un audit complet » ; il
n'a pas eu lieu.

**Assumé** : décision explicite de l'utilisateur — trois audits successifs, tous `RÉSERVES`, aucun
bloquant, des constats de plus en plus fins. Le coût d'une quatrième passe a été jugé supérieur au
risque.

**Pourquoi c'est gênant** — R8 et R9 touchent deux chemins d'échec silencieux de la procédure de
clôture et d'abandon. Ce sont précisément les endroits où un défaut ne se manifeste par aucune
erreur, et ils n'ont jamais été relus par un tiers. Le premier usage réel du dispositif sera aussi
son premier test.

**Pour solder** — auditer le diff `master…dette-technique` de l'étape 9, ou constater au premier
emploi réel que la clôture et l'abandon versent bien au registre ce qu'ils annoncent.

*Identifié par `dette-technique`, R8 à R11 du rapport d'audit.*

---

## 2026-08-14 — Le garde-fou de pipeline a cinq angles morts connus

**Constat** — `scripts/check-pipeline.sh` passe au vert sur cinq situations qu'il devrait signaler,
toutes vérifiées par injection à l'audit :

- **contrôle 1 limité à `skills/`** (ses `grep -r … --include='*.md' skills`) : un renvoi
  `contrat.md#…` écrit dans `CLAUDE.md`, `hooks/` ou `.claude/` échapperait au contrôle d'ancre
  morte. Le motif d'exclusion devrait viser `agents/`, pas « tout sauf `skills/` ».
- **`slugify()` plus étroite que la règle** (`sed "s/['’]//g; s/ /-/g"`) : elle ne retire que les
  apostrophes. Un futur titre de section contenant une virgule ou des parenthèses produirait une
  ancre fausse — invisible au script, les deux côtés de la comparaison passant par la même fonction.
- **contrôle 2 comptant des fichiers, pas des occurrences** (`grep -rl "$motif" … | wc -l`) : deux
  copies d'une même règle dans un seul fichier passent, alors que la règle écrite dit « exactement
  une occurrence ».
- **auto-citation du contrat** : l'exemple de renvoi que `contrat.md` contient sous « Une règle
  déplacée ici laisse … une ligne d'appel portant sa conséquence » satisfait à lui seul le contrôle
  « section jamais citée ».
- **garde textuel du contrôle 6** (`grep -q "\[ -f \"\?$call"`) : `bash scripts/foo.sh   # [ -f
  scripts/foo.sh ]` passe au vert, le test cherchant la chaîne n'importe où dans la ligne sans
  exiger qu'elle commande l'appel ; et `$call` est injecté tel quel dans un motif `grep`, où les
  `.` du chemin sont des métacaractères.

**Assumé** : aucune de ces situations n'existe **dans `skills/`**, toutes vérifiées.

**Corrigé le 2026-08-17 par `revue-dette`** — l'**Assumé** disait « aucune de ces situations
n'existe dans le dépôt aujourd'hui », ce qui était faux avant même ce chantier : le premier angle
mort est réalisé hors de `skills/`, où le contrôle ne regarde pas.
Établi par : `grep -rl 'contrat.md#autorité)' --include='*.md' .claude` → 2 fichiers de `done/`,
alors que la section réelle est « Autorité et divergence », d'ancre `#autorité-et-divergence`
(`grep -c '^## Autorité et divergence' contrat.md` → 1). Renvoi mort, hors de la portée du contrôle
1. `#ancre` est dans le même cas. Ces deux-là sont en prose d'exemple, ce qui atténue sans annuler.

**Pourquoi c'est gênant** — le garde-fou est ce qui doit empêcher la dérive de revenir. Un contrôle
qui ne couvre qu'une écriture du défaut donne surtout de la confiance : `R12` l'a démontré, trois
formes fautives sur quatre passaient au vert un tour après l'écriture du contrôle.

**Pour solder** — reprendre les cinq points ; les quatre premiers sont des corrections d'une à trois
lignes, le cinquième demande d'exiger que le garde précède l'appel.

*Identifié par `contrat-pipeline`, R4, R5, R6, R11 et R22 du rapport d'audit.*

---

## 2026-08-14 — Le chemin de la skill est codé en dur et répété en trois points d'édition

(aggravée) 2026-08-17

**Constat, mis à jour le 2026-08-17** — **cinq** points d'édition, et non plus trois : deux dans
`implementation-tracker/SKILL.md`, un dans `contrat.md`, deux dans `debt-review/SKILL.md` — tous
écrivant en dur `$HOME/.claude/skills/…`. Une installation hors `~/.claude`, ou un renommage de la
skill, retombe dans le mode de défaillance de `R2` : code 127, `stdout` vide, que l'Étape 1 du
tracker lit comme « aucune implémentation en cours ».
Établi par : `git grep -c '\$HOME/\.claude/skills' master -- skills` → 3, `… HEAD -- skills` → 5.

**À noter** — le contrôle 6 du garde-fou **impose** la forme `$HOME/…` pour tout appel de script
depuis un `.md` de `skills/`. Cette extension était structurellement forcée : elle ne se solde pas
sans traiter le problème générique.

**Assumé** : arbitré à la clôture — le cas suppose un environnement où `HOME` est cassé ou une
installation non standard.

**Pourquoi c'est gênant** — c'est exactement le défaut qui a bloqué la clôture de ce chantier, sous
une forme plus étroite. Aucune des cinq éditions n'échoue bruyamment si elle est oubliée.

**Pour solder** — soit un contrôle du garde-fou vérifiant que chacun de ces chemins désigne un
fichier existant, soit une résolution du chemin de la skill au lieu d'une constante. La seconde est
la seule qui empêche le compte de croître : le contrôle 6 impose la forme, donc chaque skill neuve
ajoute ses points d'édition.

*Identifié par `contrat-pipeline`, R15 et R19 du rapport d'audit.*

---

## 2026-08-14 — La table d'empreintes du garde-fou est maintenue à la main

**Constat** — le contrôle 2 de `check-pipeline.sh` repose sur une liste `fingerprints` de huit
motifs, une par section du contrat. Rien ne vérifie qu'elle reste complète : une huitième règle
ajoutée au contrat sans son empreinte n'est protégée par rien, et le contrôle « section jamais
citée » ne détecte que l'absence de renvoi, pas l'absence d'empreinte.

**Pourquoi c'est gênant** — le journal du chantier pose la règle (« toute règle ajoutée au contrat
doit recevoir son empreinte »), mais une règle qui repose sur la mémoire de son auteur est
précisément ce que ce chantier existe pour supprimer.

**Pour solder** — un contrôle qui rattache **chaque empreinte à la section qu'elle protège**, et qui
échoue sur une section sans empreinte. Une règle par section n'est pas la réalité du fichier :
plusieurs sections en portent deux.

**Corrigé le 2026-08-17 par `revue-dette`** — le **Pour solder** disait « autant d'empreintes que de
sections `##` dans le contrat ». Ce contrôle aurait échoué à son premier lancement, sur un dépôt
sain, et le correctif consistait alors à **retirer** une empreinte légitime.
Établi par : `sed -n '/^fingerprints=(/,/^)/p' scripts/check-pipeline.sh | grep -c "^  '"` → 8, et
`grep -c '^## ' skills/implementation-tracker/references/contrat.md` → 7.

*Identifié par `contrat-pipeline`, R9 du rapport d'audit.*

---

## 2026-08-14 — `impl-list.sh` dépend d'une extension GNU de `find`

**Constat** — `impl-list.sh` utilise `find … -printf '%f\n'`, absent des `find` BSD. Sur macOS, le
script échoue — et il est désormais sur le chemin d'entrée de toute invocation du tracker, dans
n'importe quel dépôt.

**Assumé** : l'environnement est Linux, aucune contrainte du brief ne portait sur la portabilité
système.

**Pourquoi c'est gênant** — le déplacement du script dans la skill l'a rendu global ; sa surface
d'exécution n'est plus celle d'un utilitaire local à un dépôt.

**Pour solder** — remplacer `-printf '%f\n'` par un `-exec basename {} \;` ou un post-traitement.

*Identifié par `contrat-pipeline`, R7 du rapport d'audit.*

---

## 2026-08-14 — Deux renvois du dépôt ne se suivent pas depuis l'éditeur

**Constat** — le chantier a rendu navigables les 28 renvois vers le contrat, mais deux références
restent en dehors :

- l'en-tête d'`impl-list.sh` renvoie à `skills/implementation-tracker/references/contrat.md`, chemin
  relatif à la racine du dépôt, alors que le fichier vit dans
  `skills/implementation-tracker/scripts/` — depuis là, la cible est `../references/contrat.md` ;
- `agents/implementation-auditor.md` renvoie en prose à
  `skills/implementation-tracker/references/audit.md`, section « Gabarit du rapport » — seule
  référence non ancrée subsistante.

**Assumé** : la seconde découle du hors-périmètre — les agents ne sont pas rendus dépendants du
noyau. L'incertitude a été ouverte au cadrage et jamais tranchée.

**Pourquoi c'est gênant** — la navigabilité des renvois était une contrainte explicite du brief. Ces
deux-là sont exactement ce que le contrôle 1 ne regarde pas : il ne vérifie que les liens vers
`contrat.md`.

**Pour solder** — corriger le chemin dans l'en-tête d'`impl-list.sh` ; pour l'agent, trancher entre
ancrer le renvoi (au prix d'une exception au hors-périmètre) et l'assumer définitivement.

*Identifié par `contrat-pipeline`, R18 du rapport d'audit et incertitude ouverte au cadrage.*

---

## 2026-08-14 — La clause « arbre propre » du tracker ne couvre pas le plan

**Constat** — l'Étape 2 d'`implementation-tracker` refuse de créer un chantier si l'arbre n'est pas
propre, avec une exception explicite pour les `*.brief.md` produits par `intent-brief`. Or le flux
normal produit **aussi** un plan non suivi dans `.claude/plans/`, que la clause ne mentionne pas.

**Constaté** à l'ouverture de ce chantier même : `git status` remontait le brief *et* `.claude/plans/`,
et il a fallu décider hors procédure que le second relevait de la même logique que le premier.

**Pourquoi c'est gênant** — la règle écrite dit d'arrêter là où le flux normal du pipeline exige de
continuer. Chaque ouverture de chantier rejouera l'arbitrage, et un modèle qui suit la lettre
refusera de démarrer.

**Pour solder** — étendre l'exception au plan dans l'Étape 2 du tracker.

*Identifié par `contrat-pipeline`, journal du suivi.*

---

## 2026-08-14 — Trois lignes du corpus dépassent l'enroulement à 100 colonnes

**Constat, corrigé le 2026-08-17** — **133 lignes** du corpus versionné dépassaient déjà 100
caractères à l'écriture de cette entrée, et non trois. Les trois lignes qu'elle nomme sont les plus
longues du seul répertoire `skills/implementation-tracker/references/` — 121, 131 et 140 caractères
— mais quatorze lignes de ce répertoire dépassent 100, dont une à 188 et une à 193. **L'intitulé est
donc faux** ; il est conservé tel quel parce qu'il sert de clé de référence.

**Corrigé le 2026-08-17 par `revue-dette`** — le Constat annonçait « trois lignes […] que le
reste du corpus respecte », description sous-mesurée **d'un facteur 44** dès son écriture. Ce
n'est pas une aggravation : rien ne s'est étendu, la mesure d'origine était fausse.
Établi par : comptage **en caractères** sur `git ls-files -- skills scripts hooks` filtré
`.md`/`.sh`, via `python3` (`len(l.rstrip('\n')) > 100`) → **133 sur `master`**. En octets,
`awk length` en rendrait une centaine de plus, sur du texte accentué.

**Pourquoi c'est gênant** — le respect du style des fichiers voisins est un axe de jugement de
l'auditeur, et le contrat est le fichier destiné à être le plus relu du pipeline. Mais à 133 lignes,
ce n'est plus une anomalie ponctuelle : c'est l'absence de convention outillée.

**Pour solder** — ré-enrouler les trois lignes nommées, qui est le geste d'origine ; puis décider
séparément si le reste du corpus relève d'une convention à écrire — et à faire tenir par le
garde-fou — ou d'un état accepté. Sans cette seconde décision, l'entrée reviendra.

*Identifié par `contrat-pipeline`, R8 puis R17 du rapport d'audit.*

---

## 2026-08-14 — Un critère de réussite du brief `contrat-pipeline` était faux dans sa lettre

**Constat** — le brief exigeait `grep -l 'contrat' agents/*.md` → aucun résultat. Les deux agents
contiennent « contrats en lecture », formulation antérieure au chantier : le critère ne pouvait pas
être atteint tel qu'écrit. Le contrôle 4 du garde-fou cherche `contrat\.md`, ce qui est l'intention
réelle, et passe.

**Assumé** : constaté au premier audit, jugé non bloquant, jamais corrigé — le brief est figé après
validation.

**Pourquoi c'est gênant** — un critère de réussite invérifiable dans sa lettre affaiblit le
dispositif qui le porte : l'auditeur doit choisir entre la lettre et l'intention, ce qu'on lui
interdit par ailleurs (« n'invente pas de critère »).

**Pour solder** — rien sur ce chantier-ci ; y penser au cadrage suivant, en écrivant les critères
sous la forme exacte de la commande qui les établit.

**Élargi le 2026-08-17 par `revue-dette`** — deuxième occurrence, sous une autre forme : le
critère 4 de ce brief (« `git status --short` après une passe ne montre que des chemins sous
`.claude/implementation/` ») porte sur l'état de l'arbre **pendant** une passe. À la clôture l'arbre
est commité et propre, et le skill n'est pas relançable (`disable-model-invocation`) : l'auditeur
n'a pu établir que ce qui ne le contredit pas, et a dû s'en remettre à la déclaration du suivi pour
l'attribution des fichiers modifiés. Un critère vérifiable aurait exigé que la sortie de l'Étape 5
soit **recopiée dans le rapport archivé** — la seule pièce qui survit à la passe.

**Pour solder, complété** — un critère de réussite doit nommer la pièce **persistante** qui
l'établit, pas un état transitoire de l'arbre de travail. C'est la généralisation des deux cas.

*Identifié par `contrat-pipeline`, R1 du rapport d'audit ; élargi par `revue-dette`, R14.*

---

## 2026-08-14 — `git-smart-commit` n'est plus lisible sans `implementation-tracker`

**Constat** — `squash.md` renvoie désormais à
`../../implementation-tracker/references/contrat.md`. Un déplacement ou un renommage du tracker
casse cette référence.

**Assumé** : conséquence directe de la décision d'emplacement du noyau, prise au cadrage. Le
contrôle 1 du garde-fou rend la casse visible (chemin mort), ce qui est le bon niveau de garantie.

**Pourquoi c'est gênant** — `git-smart-commit` est la seule skill du pipeline qui serve largement
hors de lui ; elle porte maintenant une dépendance vers une skill de chantier.

**Pour solder** — rien tant que le tracker ne bouge pas. Si le noyau devait migrer vers un
emplacement neutre, c'est ce renvoi qui le motiverait.

*Identifié par `contrat-pipeline`, R10 du rapport d'audit.*

---

## 2026-08-14 — Le correctif `R21` de `contrat-pipeline` n'a jamais été audité

(invérifiable en revue) 2026-08-17

**Constat** — le chantier s'est clos sur le verdict `RÉSERVES` de `0c5a8fe`. L'étape 11, qui élargit
le `case` du contrôle 6 aux écritures `~/` et `${HOME}/`, a été écrite **après** cet audit et n'a
été jugée par personne. `references/audit.md` demandait un audit complet ; il n'a pas eu lieu.

**Assumé** : décision explicite de l'utilisateur — trois audits successifs, un défavorable levé puis
deux fois `RÉSERVES` avec des constats de plus en plus fins, aucun bloquant. Le coût d'un quatrième
passage a été jugé supérieur au risque.

**Pourquoi c'est gênant** — le correctif touche la logique de décision du seul contrôle qui protège
contre le défaut ayant bloqué ce chantier. Il a été testé par injection sur neuf cas, mais par son
auteur.

**Pour solder** — auditer le diff de l'étape 11, ou constater au premier usage réel que le contrôle
6 ne produit ni faux positif ni faux négatif.

*Identifié par `contrat-pipeline`, décision de clôture.*

---

## 2026-08-16 — Le point 3 du tracker repose sur une prémisse de harness sans repli écrit

**Constat** — le point 3 de l'Étape 2 de `skills/implementation-tracker/SKILL.md` (« Faire relire le
plan avant de le présenter ») fait appeler `plan-reviewer` avant `ExitPlanMode`, en s'appuyant
sur le fait que « le harness assigne un fichier de plan dès l'entrée en plan mode et en autorise
l'écriture ». C'est vrai aujourd'hui, vérifié pendant ce
chantier, mais aucun repli n'est écrit si le harness change.

**Assumé** : la prémisse a été constatée empiriquement, et le brief l'avait justement notée comme
incertitude à lever.

**Pourquoi c'est gênant** — sans fichier de plan à lire, l'appel n'a plus d'entrée et le point 3
devient inexécutable, sans que rien n'indique quoi faire à la place.

**Pour solder** — écrire le repli en une phrase : relancer `plan-reviewer` après `ExitPlanMode` sur
le fichier de plan persisté, au prix d'un aller-retour si le verdict est défavorable.

*Identifié par `revue-plan-deleguee`, R4 du rapport d'audit.*

---

## 2026-08-17 — La moitié « sortie du registre » de `debt-review` n'a jamais été exercée

**Constat** — la première passe réelle du skill n'a produit aucune des quatre catégories qui font
sortir une entrée : ni `a-solder`, ni `non-pertinent`, ni `doublon`, ni `pas-une-dette`. Le fichier
`technical-debt-ecarte.md` n'existe donc pas, son préambule n'a jamais été rédigé, le champ
`**Écartée le <date> — <motif>**` jamais écrit, et le déplacement vers `technical-debt-solde.md`
jamais effectué par ce skill.
Établi par : `ls .claude/implementation/todo/` → `README.md`, `technical-debt.md`,
`technical-debt-solde.md` — trois fichiers, pas quatre.

**Assumé** : la revue du 2026-08-17 n'avait rien à écarter — les 14 entrées tiennent toutes. On ne
fabrique pas une sortie de registre pour éprouver un chemin de code.

**Pourquoi c'est gênant** — quatre catégories sur sept sont validées par le seul tri de l'exemple
fictif. Le premier écartement réel sera aussi le premier test de ce chemin, et il s'exécutera sur
une entrée qu'on **retire** d'un fichier : le mode de défaillance y est la perte, pas l'erreur
visible.

**Pour solder** — constater au premier écartement réel que l'entrée atterrit bien dans
`technical-debt-ecarte.md` avec son motif et sa preuve, et que le contrôle de conservation reste
juste. C'est le même mode de solde que pour les deux entrées d'audit jamais mené : un usage réel,
pas une relecture.

*Identifié par `revue-dette`, R12 du rapport d'audit de clôture.*

---

## 2026-08-17 — Quatre trous de procédure de `debt-review` sont connus et non traités

**Constat** — l'audit de clôture les a relevés, la première passe réelle les a tous rencontrés, et
aucun n'a été corrigé :

- **la somme « avant » du contrôle de conservation n'est mesurée nulle part** : l'Étape 0 ne compte
  pas les registres et le préambule ne porte que le compte de `technical-debt.md`. Le point de
  comparaison a dû être reconstitué de la conversation ;
- **rien ne dit quoi faire d'un marqueur déjà présent** quand une entrée est reclassée `aggravee` ou
  `inverifiable` à une revue ultérieure : remplacer la ligne, ou en ajouter une seconde. Trois
  entrées en portent un depuis cette revue ;
- **la ligne de tête n'a pas de forme pour une revue sans chantier** : `dette.md`, § *Tête du
  registre*, impose `(chantier <slug>)`, et une revue n'a pas de slug. Cette passe s'en est tirée
  parce qu'elle **était** un chantier ;
- **une clause résiduelle du gabarit** dit de recopier l'intitulé « marqueur de catégorie exclu s'il
  y en a déjà un », alors que le marqueur vit sous le titre depuis l'amendement du 2026-08-16 et
  qu'aucun intitulé ne peut en porter.

**Assumé** : arbitrés à la clôture. Aucun n'est bloquant, aucun n'a faussé la passe du 2026-08-17.

**Pourquoi c'est gênant** — les trois premiers se paieront à la **deuxième** revue, pas dans un an :
c'est elle qui rencontrera les marqueurs déjà posés et qui n'aura pas de chantier pour donner un
slug à sa ligne de tête. Un dispositif conçu pour être rejoué périodiquement a ses défauts au
deuxième tour, pas au premier.

**Pour solder** — les quatre sont des corrections d'une à trois lignes. Le premier demande le bloc
de comptage à l'Étape 0 avec report du TOTAL au préambule.

*Identifié par `revue-dette`, R5 à R8 des rapports d'audit.*

---

## 2026-08-17 — Une revue peut amender les règles du pipeline sans brief, plan ni audit

**Constat** — l'Étape 3 de `debt-review` fait écrire, **pendant la passe**, la règle qu'un arbitrage
produit, directement dans `dette.md`, `categories.md` ou `SKILL.md`. C'est l'inverse de ce que le
skill impose pour un correctif de code, qui doit passer par `/implementation-tracker` : un
amendement de règle entre au dépôt sans cadrage, sans plan relu, sans audit, et sans borne écrite
sur son ampleur. Rien ne distingue la phrase d'une revue d'une réécriture de section.
Établi par : la première passe réelle a produit deux règles de cette façon — l'interdiction des
numéros de ligne et la section *Corriger une entrée* — soit `git diff --stat 643581d 69fd11c --
skills` → 3 fichiers, 45 insertions.

**Assumé** : choix arbitré et daté au journal du chantier. L'alternative — ouvrir un chantier pour
chaque règle — était pire : les corrections d'entrées auraient été écrites sans la règle qui les
autorise, ou reportées jusqu'à ce que personne ne les fasse.

**Pourquoi c'est gênant** — c'est la seule porte du dépôt par laquelle une règle du pipeline entre
sans le dispositif qui existe pour ça. Elle est étroite et surveillée par un humain qui arbitre,
mais elle n'a pas de plafond : la même phrase autorise « ajouter une ligne à un gabarit » et
« réécrire la tenue des registres ».

**Pour solder** — écrire la borne dans `SKILL.md` : ce qu'un arbitrage de revue peut amender seul
(une règle qui tient en un paragraphe, dans une section existante) et ce qui bascule en chantier
`/implementation-tracker` (section neuve, changement de gabarit, tout ce qui touche un script).

*Identifié par `revue-dette`, R19 du troisième rapport d'audit.*
