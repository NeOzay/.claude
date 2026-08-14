# Noyau de contrat du pipeline, et garde-fou qui le vérifie

Brief : `.claude/implementation/contrat-pipeline.brief.md` (validé 2026-08-14)

## Contexte

Le pipeline `intent-brief → plan → implementation-tracker → step-implementer → git-smart-commit`
est fait de skills **textuellement autonomes** : une seule référence croisée existe dans tout le
corpus (`agents/implementation-auditor.md:95`). Conséquence mesurée le 2026-08-14 : une règle
partagée est définie en moyenne dans **3,6 fichiers**, et deux dérives en sont déjà sorties, toutes
deux inscrites au registre de dette — contrats divergents sur la racine du dépôt, et champs
`plan:` / `brief:` / `audit:` morts après archivage.

Le chantier ne vise pas la taille du corpus (le contrat va la faire croître, c'est admis). Il vise
le **nombre de points d'édition par règle** : le ramener à un, et empêcher les copies restantes de
diverger en silence.

Deux faits établis au cadrage orientent tout le reste :

- **Le hook `rtk` ne réécrit que les appels Bash du modèle, pas les commandes internes à un
  script** (`hooks/intent-brief-gate.sh:31` exécute un `find` que le modèle ne peut pas lancer en
  ligne). Ce qui passe dans un script échappe entièrement au problème.
- Un **appel** de script est un appel ; une commande recopiée dans deux étapes est une définition
  dupliquée. D'où le choix d'extraire la commande de listing plutôt que de la réécrire correctement
  à deux endroits.

## Approche

**Un noyau** — `skills/implementation-tracker/references/contrat.md`, sept sections ancrées. Le
tracker est l'orchestrateur et porte déjà l'arborescence ; la référence croisée depuis une autre
skill est déjà pratiquée dans le dépôt.

**Des renvois navigables** — `[Autorité](contrat.md#autorité)`, suivables depuis nvim et
vérifiables : une ancre morte devient une erreur détectable.

**Deux scripts** dans un `scripts/` nouveau :
`impl-list.sh` (commande de listing canonique) et `check-pipeline.sh` (garde-fou).

**Discipline non négociable** (signal d'arrêt du brief) : le noyau porte ce qui est **défini**
plusieurs fois, jamais ce qui est **appliqué** plusieurs fois. Une règle déplacée laisse une ligne
d'appel portant sa conséquence, jamais un vide. Si le diff fait apparaître la même instruction
recopiée dans tous les skills, on s'arrête et on en reparle.

### Contenu du noyau

| Section (ancre) | Ce qu'elle définit | Sites de définition actuels |
|---|---|---|
| `#arborescence-et-nommage` | `.claude/implementation/`, `done/`, `todo/`, slug kebab-case figé, appariement par slug | tracker `SKILL.md:174` + `intent-brief/SKILL.md:131` + les 2 gabarits |
| `#frontmatter` | champs des 3 fichiers, valeurs, défauts — dont `execution:` absent = `direct` | `intent-brief/SKILL.md:170` + `gabarit-brief.md:25,91` + tracker `SKILL.md:178` + `gabarit-suivi.md:26` |
| `#autorité-et-divergence` | brief figé, suivi fait foi, où s'écrit un élargissement | tracker `SKILL.md:247` + `intent-brief/SKILL.md:232` |
| `#format-détape-et-délégabilité` | `- [état] N. Intitulé — <fichier> — vérif: <cmd>`, une étape = un tour, vérif obligatoire | tracker `SKILL.md` Étape 2.4 + `gabarit-suivi.md:14` |
| `#contrat-des-sous-agents` | entrée en chemins absolus, racine par `rev-parse --show-toplevel`, git en lecture seule, blocs de sortie | `references/audit.md:43-49` (côté skill uniquement) |
| `#branche-et-commits` | branche `<slug>`, `base:`, `session: N`, format du message, stager les chemins jamais `-A` | tracker `SKILL.md:215,313,319` + `cloture.md` + `squash.md` |
| `#dates-et-listing` | `date +%F` jamais devinée ; le listing des suivis actifs passe par `scripts/impl-list.sh` | 4 fichiers pour la date, `SKILL.md:54` et `:88` pour le listing |

Chaque règle du noyau garde **son mode de défaillance en une ligne**. Sans le pourquoi, le contrat
devient un schéma, et un schéma se survole — c'est ce qui distingue ce fichier d'une doc morte.

### Contrôles de `check-pipeline.sh`

Cinq contrôles, tous à faux positifs nuls par construction (le brief avertit qu'un contrôle bruyant
sera désactivé au premier chantier, et que le garde-fou mourra là) :

1. **Ancres mortes** — chaque `](…contrat.md#ancre)` du dépôt résout vers un titre existant, par
   normalisation déterministe du titre (minuscules, espaces → tirets, ponctuation retirée, accents
   conservés).
2. **Formulations canoniques hors du noyau** — table explicite `motif → fichier autorisé`. Une
   *allowlist*, pas une heuristique : chaque ligne est un choix délibéré. `agents/` est exclu du
   scan, sa redondance étant voulue.
3. **Filtre de listing** — `scripts/impl-list.sh` exécuté sur `done/` ne remonte aucun `.brief.md`,
   `.audit.md` ni `.plan.md`. Test fonctionnel sur données réelles.
4. **Indépendance des agents** — `grep -l 'contrat\.md' agents/*.md` vide.
5. **Chemins de frontmatter résolvables** — dans chaque suivi de `done/`, les champs `plan:`,
   `brief:`, `audit:` pointent vers un fichier existant.

Sort en code ≠ 0 sur violation (contrairement au gate d'`intent-brief`, pédagogique et à échec
ouvert : celui-ci est un outil de vérification, il doit échouer fermé). Style repris de
`hooks/intent-brief-gate.sh` : en-tête `PORTÉE`, politique d'échec documentée, justification en
commentaire.

## Étapes

- [ ] 1. Écrire le noyau, sept sections ancrées, sans toucher aux appelants — `skills/implementation-tracker/references/contrat.md` — vérif: `grep -c '^## ' skills/implementation-tracker/references/contrat.md` → 7
- [ ] 2. Commande de listing canonique — `scripts/impl-list.sh` — vérif: `bash scripts/impl-list.sh .claude/implementation/done | grep -cE '\.(brief|audit|plan)\.md'` → 0
- [ ] 3. Brancher le tracker : Étape 0 et Cas C appellent le script, les règles définies au noyau deviennent des renvois ancrés — `skills/implementation-tracker/SKILL.md` — vérif: `grep -c 'contrat.md#' skills/implementation-tracker/SKILL.md` ≥ 5 et `grep -c "grep -vE" skills/implementation-tracker/SKILL.md` → 0
- [ ] 4. Brancher `intent-brief` : slug, `execution:`, date, section « Articulation » réduite à un renvoi — `skills/intent-brief/SKILL.md` — vérif: `grep -c 'contrat.md#' skills/intent-brief/SKILL.md` ≥ 3
- [ ] 5. Brancher les gabarits et les références — `gabarit-suivi.md`, `gabarit-brief.md`, `audit.md`, `cloture.md`, `dette.md`, `squash.md` — vérif: `grep -rc 'contrat.md#' skills/*/references/ | grep -v ':0'`
- [ ] 6. Écrire le garde-fou et ses cinq contrôles — `scripts/check-pipeline.sh` — vérif: `bash scripts/check-pipeline.sh; echo $?`
- [ ] 7. Appeler le garde-fou depuis la procédure de clôture, à côté de l'audit — `skills/implementation-tracker/references/cloture.md` — vérif: `grep -n 'check-pipeline' skills/implementation-tracker/references/cloture.md`
- [ ] 8. Solder les dettes que le garde-fou révèle : réécriture des champs `plan:`/`brief:`/`audit:` dans `done/`, renommage de l'archive `2026-08-14-linked-toasting-graham.md`, phrase sur la racine du dépôt dans l'agent — `done/*.md`, `cloture.md`, `agents/implementation-auditor.md` — vérif: `bash scripts/check-pipeline.sh` → code 0

L'étape 8 est **la seule à toucher `agents/`**, et c'est une exception assumée : le hors-périmètre
du brief interdit de dédupliquer les agents ou de les rendre dépendants du noyau, pas d'y ajouter
la phrase qui solde une dette explicitement mise dans le périmètre (« l'appelant peut te la donner ;
sinon, calcule-la »). À redire à la confrontation plan ↔ brief.

**Le solde du registre n'est pas une étape.** Le déplacement des quatre entrées vers
`todo/technical-debt-solde.md`, avec la commande exécutée qui l'établit, relève de la procédure de
clôture existante (`cloture.md`, point 2) — une seule écriture par chantier.

## Vérification

**D'ensemble** : `bash scripts/check-pipeline.sh` → code 0, aucun rouge.

**Points d'édition** — pour chaque règle du tableau ci-dessus, `grep -rn` de sa formulation
canonique sur `skills/` ne doit remonter que `contrat.md` ; partout ailleurs, un renvoi ancré.
C'est le contrôle 2 du garde-fou, donc automatiquement rejoué.

**Navigation** — ouvrir `skills/implementation-tracker/SKILL.md` dans nvim et suivre un renvoi
`contrat.md#…` : il doit atterrir sur la bonne section. C'est le seul critère que le script ne
couvre pas, et la raison d'être de la forme retenue.

**Non-régression du pipeline** : la clôture de ce chantier est elle-même le premier essai réel du
dispositif — elle exécutera le garde-fou et soldera les quatre entrées.
