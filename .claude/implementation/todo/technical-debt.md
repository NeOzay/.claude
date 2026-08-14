# Dette technique

Ce document recense ce qui a été **délibérément laissé de côté**, avec la raison et ce qu'il
faudrait faire pour solder. Il ne liste que de la dette constatée et vérifiée dans le dépôt — pas
des idées d'amélioration.

Chaque entrée indique le chantier qui l'a identifiée. Entrées ordonnées de la plus ancienne à la
plus récente. Une entrée soldée est retirée d'ici et déplacée dans
[technical-debt-solde.md](technical-debt-solde.md), pas barrée.

Procédure, gabarit et règle de solde : `skills/implementation-tracker/references/dette.md`.

> Dernière vérification : 2026-08-14 (chantier `dette-technique`)

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

*Identifié par `audit-integre`, R8 du rapport d'audit.*

---

## 2026-08-14 — Les filtres de listing sont cassés par le hook `rtk`

**Constat** — `ls .claude/implementation/*.md | grep -vE '\.(brief|audit)\.md$'` n'exclut plus rien.
Le hook `rtk` réécrit `ls` en ajoutant une colonne de taille en fin de ligne
(`…brief.md  6.2K`), donc l'ancre `$` ne matche jamais. Vérifié le 2026-08-14 : la commande de
l'Étape 0 du tracker remonte `dette-technique.brief.md` à côté de `dette-technique.md`.

**Pourquoi c'est gênant** — les `*.brief.md` et `*.audit.md` apparaissent dans la liste des
implémentations en cours, que l'Étape 0 de `implementation-tracker` existe précisément pour tenir
propre. Le filtre est écrit à trois endroits (`SKILL.md` Étape 0 et Cas C, et la commande du Cas C).

**Pour solder** — filtrer sur le nom de fichier plutôt que sur la fin de ligne : `find
.claude/implementation -maxdepth 1 -name '*.md' ! -name '*.brief.md' ! -name '*.audit.md'`, ou un
`grep -vE '\.(brief|audit)\.md( |$)'`.

*Identifié par `audit-integre`, journal du suivi.*

---

## 2026-08-14 — Le contrat de l'auditeur et celui de l'appelant divergent sur la racine du dépôt

**Constat** — `skills/implementation-tracker/references/audit.md:43-45` range la racine du dépôt
parmi ce que l'appelant **transmet** à l'agent ; `agents/implementation-auditor.md:21-23` énumère ce
que l'appelant fournit sans la mentionner, l'agent la calculant lui-même juste après
(`git rev-parse --show-toplevel`). Les deux documents décrivent une entrée différente.

**Assumé** : sans mode de défaillance connu — l'agent est autonome, et une entrée surnuméraire ne le
gêne pas.

**Pourquoi c'est gênant** — c'est exactement le type d'écart inter-fichiers qui avait produit R3 du
même rapport, lequel avait, lui, un mode de défaillance réel (rapport écrit à côté).

**Pour solder** — une phrase dans `implementation-auditor.md` : « l'appelant peut te la donner ;
sinon, calcule-la ».

*Identifié par `audit-integre`, R6 du rapport d'audit.*

---

## 2026-08-14 — Les champs `plan:` / `brief:` / `audit:` pointent à faux après archivage

**Constat** — la clôture déplace suivi, brief, rapport et plan vers `done/` avec un préfixe de date
(`cloture.md`, point 4), mais ne réécrit pas les chemins du frontmatter. Vérifié sur
`done/2026-08-14-audit-integre.md` : `brief:` pointe vers `.claude/implementation/audit-integre.brief.md`
et `audit:` vers `…/audit-integre.audit.md`, deux chemins qui n'existent plus.

**Aggravant, constaté le 2026-08-14** — le même fichier porte `plan:
.claude/plans/linked-toasting-graham.md`, nom que le harness a depuis réattribué au plan d'un
**autre** chantier. Ce champ ne pointe donc plus vers rien : il pointe vers le mauvais contenu, ce
qu'aucune vérification d'existence ne détecte.

**Assumé** : dette préexistante, non aggravée par le chantier qui l'a relevée.

**Pourquoi c'est gênant** — ces champs existent pour qu'une reprise à froid retrouve l'intention et
le contenu des étapes. Un chemin mort les prive de leur seul usage ; un chemin qui résout vers le
plan d'un autre chantier est pire, parce qu'il a l'air de fonctionner.

**Pour solder** — réécrire les trois champs pendant la boucle d'archivage de `cloture.md`, avec les
chemins `done/` définitifs.

*Identifié par `audit-integre`, corollaire de R1 ; aggravation constatée par `dette-technique`.*

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

## 2026-08-14 — Les plans archivés portent un nom réattribuable, sans garde-fou à l'écrasement

**Constat** — la boucle d'archivage de `cloture.md` renommait le plan `<AAAA-MM-DD>-<son nom
généré>`. Or le harness réattribue ces noms (`linked-toasting-graham.md`) d'un chantier à l'autre.
À la clôture de `dette-technique`, le plan d'`audit-integre` a été **écrasé** : `git mv` refuse
d'écraser, mais le repli `mv` de la boucle, lui, écrase sans un mot. Détecté à la relecture de
`ls done/`, restauré depuis `HEAD`.

**Traité** — le plan est désormais archivé `<AAAA-MM-DD>-<slug>.plan.md`, et chaque déplacement est
précédé d'un `[ -e "$t" ]` qui refuse au lieu d'écraser (`cloture.md`, point 4).

**Ce qui reste en dette** — les archives déjà écrites gardent l'ancienne convention :
`done/2026-08-14-linked-toasting-graham.md` est le plan d'`audit-integre`, mais rien dans son nom
ne le dit. Et le champ `plan:` de `done/2026-08-14-audit-integre.md` continue de pointer vers
`.claude/plans/linked-toasting-graham.md`, chemin qui a depuis désigné deux chantiers différents.

**Pour solder** — renommer l'archive existante en `2026-08-14-audit-integre.plan.md` et réécrire le
champ `plan:` correspondant, en même temps que l'entrée sur les champs obsolètes ci-dessus.

*Identifié par `dette-technique`, incident constaté pendant sa propre clôture.*
