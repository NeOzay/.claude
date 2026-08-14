# Dette technique

Ce document recense ce qui a été **délibérément laissé de côté**, avec la raison et ce qu'il
faudrait faire pour solder. Il ne liste que de la dette constatée et vérifiée dans le dépôt — pas
des idées d'amélioration.

Chaque entrée indique le chantier qui l'a identifiée. Entrées ordonnées de la plus ancienne à la
plus récente. Une entrée soldée est retirée d'ici et déplacée dans
[technical-debt-solde.md](technical-debt-solde.md), pas barrée.

Procédure, gabarit et règle de solde : `skills/implementation-tracker/references/dette.md`.

> Dernière vérification : 2026-08-15 (chantier `contrat-pipeline`)

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

## 2026-08-14 — La confrontation plan ↔ brief reste auto-jugée et sans trace

**Constat** — `skills/intent-brief/SKILL.md:193` (Étape 7) fait confronter le plan au brief par la
session qui vient de produire ce plan, et sa sortie tient « en trois lignes, pas un rapport »
(`:205`). Aucune trace versionnée n'en subsiste.

**Assumé** : le brief du chantier `audit-integre` nommait trois points de contrôle auto-jugés ; deux
ont été traités (la clôture, et le bloc `VÉRIFICATION` de `step-implementer` désormais rejoué). Le
« But » du brief bornait explicitement le chantier à la clôture — celui-ci n'était couvert par aucun
critère de réussite.

**Pourquoi c'est gênant** — c'est le tiers restant du symptôme d'origine : un point de contrôle
rendu par l'auteur du travail, sans trace. Le dispositif d'audit démontre qu'un juge indépendant y
change le résultat.

**Pour solder** — porter le même principe sur la confrontation : soit un rapport versionné, soit un
regard extérieur. À cadrer, l'Étape 7 étant beaucoup plus légère qu'un audit de clôture.

*Identifié par `audit-integre`, R7 du rapport d'audit.*

---

## 2026-08-14 — Une étape corrective née d'un audit ne peut pas être cochée avant l'audit

**Constat** — `references/cloture.md:10` demande que **toutes** les étapes soient cochées avant
d'auditer. Or une étape née d'un audit précédent a pour vérification « nouvel audit complet
FAVORABLE », qui ne peut être satisfaite qu'après. L'étape est donc `[>]` au moment où l'audit
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

**Constat** — le chantier `dette-technique` s'est clos sur le verdict `RÉSERVES` de `343f180`. Ses
quatre derniers correctifs (R8 lecture du rapport entier, R9 chemin d'écriture de l'abandon dans le
cas *garder la branche*, R10 note périmée, R11 mise en forme) ont été écrits **après** cet audit et
n'ont été jugés par personne. `references/audit.md:80` demandait un audit complet ; il n'a pas eu
lieu.

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

- **contrôle 1 limité à `skills/`** (`:44`, `:63`) : un renvoi `contrat.md#…` écrit dans `CLAUDE.md`,
  `hooks/` ou `.claude/` échapperait au contrôle d'ancre morte. Le motif d'exclusion devrait viser
  `agents/`, pas « tout sauf `skills/` ».
- **`slugify()` plus étroite que la règle** (`:34`) : elle ne retire que les apostrophes. Un futur
  titre de section contenant une virgule ou des parenthèses produirait une ancre fausse — invisible
  au script, les deux côtés de la comparaison passant par la même fonction.
- **contrôle 2 comptant des fichiers, pas des occurrences** (`:95`) : deux copies d'une même règle
  dans un seul fichier passent, alors que la règle écrite dit « exactement une occurrence ».
- **auto-citation du contrat** (`contrat.md:15`) : l'exemple de renvoi qu'il contient satisfait à
  lui seul le contrôle « section jamais citée ».
- **garde textuel du contrôle 6** (`:197`) : `bash scripts/foo.sh   # [ -f scripts/foo.sh ]` passe
  au vert, le test cherchant la chaîne n'importe où dans la ligne sans exiger qu'elle commande
  l'appel ; et `$call` est injecté tel quel dans un motif `grep`, où les `.` du chemin sont des
  métacaractères.

**Assumé** : aucune de ces situations n'existe dans le dépôt aujourd'hui, toutes vérifiées.

**Pourquoi c'est gênant** — le garde-fou est ce qui doit empêcher la dérive de revenir. Un contrôle
qui ne couvre qu'une écriture du défaut donne surtout de la confiance : `R12` l'a démontré, trois
formes fautives sur quatre passaient au vert un tour après l'écriture du contrôle.

**Pour solder** — reprendre les cinq points ; les quatre premiers sont des corrections d'une à trois
lignes, le cinquième demande d'exiger que le garde précède l'appel.

*Identifié par `contrat-pipeline`, R4, R5, R6, R11 et R22 du rapport d'audit.*

---

## 2026-08-14 — Le chemin de la skill est codé en dur et répété en trois points d'édition

**Constat** — `SKILL.md:42`, `SKILL.md:75` et `contrat.md:178` écrivent
`$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh`. Une installation hors
`~/.claude`, ou un renommage de la skill, retombe dans le mode de défaillance de `R2` : code 127,
`stdout` vide, que l'Étape 1 du tracker lit comme « aucune implémentation en cours ».

**Assumé** : arbitré à la clôture — le cas suppose un environnement où `HOME` est cassé ou une
installation non standard.

**Pourquoi c'est gênant** — c'est exactement le défaut qui a bloqué la clôture de ce chantier, sous
une forme plus étroite. Aucune des trois éditions n'échoue bruyamment si elle est oubliée.

**Pour solder** — soit un contrôle du garde-fou vérifiant que les trois chemins désignent un fichier
existant, soit une résolution du chemin de la skill au lieu d'une constante.

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

**Pour solder** — un contrôle « autant d'empreintes que de sections `##` dans le contrat », qui
échoue sur l'écart.

*Identifié par `contrat-pipeline`, R9 du rapport d'audit.*

---

## 2026-08-14 — `impl-list.sh` dépend d'une extension GNU de `find`

**Constat** — `impl-list.sh:31` utilise `find -printf`, absent des `find` BSD. Sur macOS, le script
échoue — et il est désormais sur le chemin d'entrée de toute invocation du tracker, dans n'importe
quel dépôt.

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

- `impl-list.sh:6` renvoie à `skills/implementation-tracker/references/contrat.md`, chemin relatif à
  la racine du dépôt, alors que le fichier vit dans `skills/implementation-tracker/scripts/` —
  depuis là, la cible est `../references/contrat.md` ;
- `agents/implementation-auditor.md:95` renvoie en prose à `skills/implementation-tracker/references/audit.md`,
  section « Gabarit du rapport » — seule référence non ancrée subsistante.

**Assumé** : la seconde découle du hors-périmètre — les agents ne sont pas rendus dépendants du
noyau. L'incertitude a été ouverte au cadrage et jamais tranchée.

**Pourquoi c'est gênant** — la navigabilité des renvois était une contrainte explicite du brief. Ces
deux-là sont exactement ce que le contrôle 1 ne regarde pas : il ne vérifie que les liens vers
`contrat.md`.

**Pour solder** — corriger le chemin d'`impl-list.sh:6` ; pour l'agent, trancher entre ancrer le
renvoi (au prix d'une exception au hors-périmètre) et l'assumer définitivement.

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

**Constat** — `contrat.md:7` (121 colonnes), `contrat.md:15` (131) et `dette.md:122` (140) dépassent
nettement l'enroulement que le reste du corpus respecte, sans raison structurelle.

**Pourquoi c'est gênant** — le respect du style des fichiers voisins est un axe de jugement de
l'auditeur, et le contrat est le fichier destiné à être le plus relu du pipeline.

**Pour solder** — ré-enrouler les trois lignes.

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

*Identifié par `contrat-pipeline`, R1 du rapport d'audit.*

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
