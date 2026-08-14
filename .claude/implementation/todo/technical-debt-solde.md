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
