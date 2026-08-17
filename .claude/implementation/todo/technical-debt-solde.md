# Dette soldée

Ce qu'un chantier a réglé, retiré de [technical-debt.md](technical-debt.md) et déposé ici. Une
entrée soldée n'est pas barrée dans le registre : elle en sort, pour qu'il ne gonfle pas.

Chaque entrée garde son texte d'origine — constat, raison, ce qu'il fallait faire — et reçoit en fin
la date du solde, le chantier qui l'a rendu, et **la commande exécutée qui l'établit avec sa sortie
réelle**. Sans cette sortie, l'entrée serait restée dans le registre : un solde s'établit, il ne se
déclare pas.

Ordre du plus ancien au plus récent, comme le registre.

Gabarit et procédure : `skills/implementation-tracker/references/dette.md`, section « Solder ».

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

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — le filtre vit désormais dans
`skills/implementation-tracker/scripts/impl-list.sh`, un script que le hook `rtk` ne réécrit pas, et
que l'Étape 0 comme le Cas C appellent au lieu de recopier une commande.
Établi par : `bash "$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh" .claude/implementation/done | grep -cE '\.(brief|audit|plan)\.md$'` → `0`,
sur un répertoire contenant pourtant 2 `.brief.md`, 2 `.audit.md` et 2 `.plan.md`.

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

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — la règle est définie une seule fois,
dans `contrat.md`, section « Contrat des sous-agents » : « l'appelant peut la donner, sinon l'agent
la calcule ». `audit.md` renvoie à cette section au lieu d'énumérer une liste divergente, et l'agent
porte la même formulation.
Établi par : `grep -n -A1 "peut te la" agents/implementation-auditor.md` → l. 26-27, « **L'appelant
peut te la donner ; sinon, calcule-la** » ; et `grep -n "Contrat des sous-agents" …/references/audit.md`
→ l. 42, renvoi ancré au lieu de la liste.

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

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — les six champs ont été réécrits vers
leurs cibles `done/`, et la boucle d'archivage de `cloture.md` les réécrit désormais à chaque
clôture. Le contrôle 5 du garde-fou vérifie qu'ils résolvent.
Établi par : `bash scripts/check-pipeline.sh` → contrôle 5 « ✓ tous les champs plan/brief/audit
résolvent », code 0.

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

**Soldé le 2026-08-15 par le chantier `contrat-pipeline`** — l'archive mal nommée a été renommée
d'après son slug, et les deux champs `plan:` pointent chacun vers leur propre plan. La règle de
nommage est au contrat, section « Arborescence et nommage ».
Établi par : `ls .claude/implementation/done/ | grep plan` → `2026-08-14-audit-integre.plan.md` et
`2026-08-14-dette-technique.plan.md` ; `grep -h '^plan:' .claude/implementation/done/*.md` → deux
chemins distincts, chacun vers le plan de son chantier.

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

*Identifié par `audit-integre`, R7 du rapport d'audit.*

**Soldé le 2026-08-16 par le chantier `revue-plan-deleguee`** — l'option « regard extérieur » a été
retenue : l'Étape 7 d'`intent-brief` est supprimée, et la confrontation est rendue par le sous-agent
`plan-reviewer` (contexte isolé, lecture seule), appelé par le tracker **avant** que le plan ne soit
présenté à l'utilisateur. L'option « rapport versionné » a été écartée : un plan pas encore accepté
peut changer plusieurs fois, un historique de verdicts sur des versions mortes n'aiderait personne.
Établi par : `grep -c 'Confrontation plan' skills/intent-brief/SKILL.md` → `0` et ses étapes
s'arrêtent à `## Étape 6 — Passage au suivi` ; `grep -n 'plan-reviewer'
skills/implementation-tracker/SKILL.md` → `126:` l'appel avant `ExitPlanMode` ; `agents/plan-reviewer.md`
existe, `tools: Read, Grep, Glob, Bash` sans droit d'écriture.

---

## 2026-08-16 — Le contrôle 1 du garde-fou de pipeline n'a jamais rien testé

**Constat** — `scripts/check-pipeline.sh:47` et `:65` comptaient les renvois vers le contrat avec la
classe `[a-zà-ÿ0-9-]`. Le range `à-ÿ` est une collation invalide : `/usr/bin/grep` échouait sur
`Invalid collation character`, `total` valait `0`, et le script concluait « aucun renvoi trouvé — le
contrat n'est cité nulle part », en sortant systématiquement en code 1.

**Pourquoi c'était gênant** — le contrôle 1 détecte les ancres mortes vers `contrat.md`, soit la
dérive que la centralisation des règles existe pour empêcher. Il ne produisait pas un faux positif :
il rapportait une anomalie constante, indistinguable d'une vraie, et faisait échouer chaque clôture.
Un contrôle qui crie toujours ne se lit plus.

*Identifié par `revue-plan-deleguee`, constaté au point 1 de sa clôture. Anomalie préexistante,
reproduite à l'identique sur `master`.*

**Soldé le 2026-08-16 par le chantier `revue-plan-deleguee`** — range remplacé par `[^)]` aux deux
endroits. Le correctif évident `[a-z0-9-]` a été **écarté** : il tronquait les ancres accentuées du
contrat (`#format-détape-et-délégabilité`, `#autorité-et-divergence`), transformant un contrôle mort
en faux « ancre morte ». `[^)]` ne dépend d'aucune collation et capture l'ancre entière.
Établi par : `bash scripts/check-pipeline.sh` → « 1. Renvois vers le contrat ✓ 29 renvois, tous
résolvent », « Pipeline conforme. », `EXIT=0` ; les six contrôles passent.

---

## 2026-08-17 — Les correctifs R11 et R13 de `revue-dette` n'ont jamais été audités

**Constat** — le chantier s'est clos sur le verdict `RÉSERVES` de `69fd11c`. L'étape 12, qui ouvre
dans le skill le chemin d'écriture d'une règle issue d'un arbitrage et borne la validation de date
de `trier-revue.sh`, a été écrite **après** cet audit et n'a été jugée par personne.

**Assumé** : décision explicite de l'utilisateur — deux audits successifs, aucun bloquant, et R11
comme R13 sont des corrections dont la vérification est mécanique et a été exécutée.

**Pourquoi c'est gênant** — R11 touche la procédure d'arbitrage, c'est-à-dire l'endroit exact où le
skill décide ce qu'il a le droit d'écrire hors du registre. Un défaut y est silencieux par
construction : il ne se manifeste qu'à la revue suivante, devant un arbitrage qu'elle refusera ou
qu'elle écrira au mauvais endroit. C'est le troisième chantier de ce dépôt à se clore ainsi.

**Pour solder** — auditer le diff de l'étape 12, ou constater à la deuxième revue réelle qu'un
arbitrage produisant une règle suit bien le chemin écrit à l'Étape 3, et que l'Étape 5 ne le signale
plus comme une violation.

**Soldé le 2026-08-17 par un troisième audit, demandé avant l'aplatissement** — le *Pour solder*
disait « auditer le diff de l'étape 12 ». C'est fait : `implementation-auditor` a jugé le delta
`69fd11c..be0eadf` et rendu `RÉSERVES`, aucun bloquant, les quatre vérifications de l'étape 12
reproduites par ses propres commandes.
Établi par : `grep -n '^## 2026-08-17' .claude/implementation/revue-dette.audit.md` → trois
sections, la dernière `## 2026-08-17 — clôture (2ᵉ passe) — be0eadf`, qui juge précisément le diff
de l'étape 12.

*Identifié par `revue-dette`, décision de clôture ; soldé le jour même, R18 du troisième audit.*
