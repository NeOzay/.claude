# Déléguer la revue de plan à un sous-agent

Brief : `.claude/implementation/revue-plan-deleguee.brief.md` (statut `validé`)

## Contexte

`intent-brief` et `implementation-tracker` savent tous deux faire le plan et la confrontation
plan ↔ brief. Le tracker duplique le flux d'`intent-brief` et résout le conflit par une clause
d'exception (`skills/implementation-tracker/SKILL.md:126-127`) : « Le chantier arrive
d'`intent-brief` → ses Étapes 6 et 7 ont déjà fait le plan et la confrontation. Ne pas les
refaire ». Deux chemins pour le même travail, arbitrés par une condition que le modèle doit
détecter lui-même.

Par ailleurs, la confrontation est aujourd'hui faite par le modèle qui vient d'écrire le plan :
il juge sa propre conformité au brief. C'est exactement l'auto-évaluation que
`implementation-auditor` existe pour éviter en aval du chantier.

Résultat visé : une seule voie vers le plan — `intent-brief` s'arrête au brief validé et renvoie
au tracker ; le tracker construit le plan, puis délègue à un nouvel agent `plan-reviewer` la
confrontation au brief **et** le contrôle de qualité du plan, avant de présenter le plan à
l'utilisateur.

## Incertitude levée en cours de planification

**Le plan mode autorise l'appel d'un sous-agent** — vérifié par un appel réel depuis ce plan mode.
L'architecture retenue (revue *avant* `ExitPlanMode`) est réalisable. Le repli envisagé au brief
(revue après `ExitPlanMode`, sur le fichier de plan persisté) est abandonné.

## Décision structurante : le plan est lu, jamais recopié

Le brief redoutait de devoir transmettre le plan en clair dans le prompt, faute de fichier à lire
avant `ExitPlanMode`. **Cette crainte est infondée** : le harness assigne le fichier de plan dès
l'entrée en plan mode et autorise son écriture — c'est le seul fichier éditable dans ce mode.
Constaté sur ce chantier même, où le plan a été écrit dans
`.claude/plans/eager-wibbling-moon.md` avant toute présentation.

`plan-reviewer` reçoit donc **trois chemins absolus** — racine, brief, plan — et lit tout
lui-même. Le contrat des sous-agents s'applique intégralement, sans exception : l'agent se fait sa
propre lecture du plan *et* de l'intention. C'est l'indépendance complète, pas la moitié.

> Effet de bord sur le périmètre : `contrat.md` reste touché, mais pour une raison bien plus
> légère que prévu — le fichier compte les agents (« Vaut pour `step-implementer` et
> `implementation-auditor` », « Les deux agents sont hors de ce dispositif »), et ce compte passe
> à trois. Aucune règle nouvelle n'y est ajoutée.

**À ratifier explicitement.** Ce revirement contredit deux décisions marquées `(dit)` dans un brief
au `statut: validé`, donc figé : « le plan est transmis en clair et intégral » et « le contrat
reçoit une exception nommée ». Le brief fait autorité sur l'intention tant qu'il n'est pas amendé —
ce n'est pas au plan de le révoquer. Le brief n'est pas modifié pour autant : conformément à
[Autorité et divergence](skills/implementation-tracker/references/contrat.md#autorité-et-divergence),
la ratification s'inscrit **dans le fichier de suivi**, datée, avec une entrée au journal de
décisions à sa création.

## Fichiers touchés — quatre, pas un de plus

| Fichier | Nature |
|---|---|
| `agents/plan-reviewer.md` | création |
| `skills/implementation-tracker/references/contrat.md` | le compte des agents passe à trois |
| `skills/implementation-tracker/SKILL.md` | Étape 2, points 2-3 |
| `skills/intent-brief/SKILL.md` | coupe des Étapes 6-7, réécriture de la sortie |

Hors-périmètre, rappelé du brief : `gabarit-brief.md`, `gabarit-suivi.md`, `audit.md`, `dette.md`,
`cloture.md`, `agents/implementation-auditor.md`, `agents/step-implementer.md`.

Le **bloc de sortie de `plan-reviewer` ne va pas dans `contrat.md`** : `contrat.md:18-22` pose que
les agents sont volontairement hors du dispositif de centralisation — leurs blocs sont dupliqués
chez eux parce qu'un agent en isolation qui ne suivrait pas un renvoi perdrait son garde-fou. Le
bloc vit dans l'agent ; le tracker en duplique le tableau des verdicts, exactement comme il
duplique déjà celui de `step-implementer`.

---

## Étapes

### 1. Créer `agents/plan-reviewer.md`

Fichier neuf, calqué sur les conventions relevées chez les deux agents existants : frontmatter à
quatre champs (`name`, `description`, `model`, `tools`), H1 nom de rôle, préambule non titré posant
périmètre / valeur / isolation, puis `## Entrée` en premier et `## Rapport de sortie` en dernier.
Tutoiement, impératif, chaque règle suivie de sa justification.

- `model: opus` — c'est un jugement, comme `implementation-auditor`.
- `tools: Read, Grep, Glob, Bash` — **aucun droit d'écriture** : le rapport ne se persiste nulle
  part. Un plan pas encore accepté peut changer plusieurs fois ; un historique de verdicts sur des
  versions mortes n'a pas de valeur, et le brief est déjà le registre.

**`## Entrée`** — l'appelant fournit **trois chemins absolus** : la racine du dépôt, le fichier de
plan, et le brief (ou la mention explicite qu'il n'y en a pas). L'agent lit le brief, puis le plan,
puis le code que le plan invoque. Reprendre la formule récurrente des deux agents sur les chemins
absolus et sur `git rev-parse --show-toplevel`, ainsi que la règle d'arbitrage des sources.

**`## Ce que tu juges`** — deux H3 :

- `### 1. Conformité au brief` — critères de réussite servis, hors-périmètre intact, signaux de
  dérive non déclenchés, incertitudes tranchées ou toujours ouvertes.
- `### 2. Qualité du plan` — **contrôle de contrat, pas critique d'architecture** : une étape tient
  en un tour d'exécution, nomme ses fichiers, porte une commande de vérification ; l'ordre des
  dépendances tient ; les fichiers et commandes cités existent réellement (vérification dans le
  code, pas sur parole).

**`## Interdits`** — sur le patron des deux agents, chaque interdit redirigeant vers le canal
légitime :

- **Ne réécris pas le plan.** Tu constates, l'appelant et l'utilisateur tranchent.
- **Ne propose pas d'alternative de conception.** Le plan sort d'`ExitPlanMode`, son fond relève de
  l'utilisateur. Une préférence non formulée par le brief va en `QUALITÉ`, au plus.
- **N'invente pas de critère** — même formule que `implementation-auditor`.
- **Aucune commande git autre que de lecture** — même liste blanche / liste noire que les deux
  autres agents.
- **N'écris dans aucun fichier.**

**`## Verdict`** — tableau à deux colonnes, sur le modèle de `implementation-auditor` :

| Verdict | Quand |
|---|---|
| `CONFORME` | Tous les critères servis, hors-périmètre intact, aucun signal déclenché, chaque incertitude traitée, plan exécutable en l'état. |
| `RÉSERVES` | Rien n'empêche d'avancer, mais il reste des constats que l'utilisateur doit connaître avant de valider. |
| `NON CONFORME` | Un critère non servi, le hors-périmètre entamé, un signal de dérive déclenché, ou une étape inexécutable (sans vérification, ou visant des fichiers inexistants). |

Reprendre la règle du doute : prendre le verdict le plus sévère et expliquer pourquoi.

**`## Rapport de sortie`** — introduit par la phrase exacte des deux autres agents,
`Termine par ce bloc, et rien d'autre après :`

```
VERDICT : CONFORME | RÉSERVES | NON CONFORME
CRITÈRES : <critère → étape(s) qui le sert, une par ligne — "SANS OBJET" sans brief>
HORS-PÉRIMÈTRE : <RESPECTÉ, ou l'étape en cause et ce qu'elle entame — "SANS OBJET" sans brief>
DÉRIVE : <signal déclenché et étape en cause, un par ligne — sinon "aucun">
INCERTITUDES : <incertitude → étape qui la tranche, ou "toujours ouverte" — sinon "aucune">
QUALITÉ : <Q1, Q2, … un constat par ligne — sinon "rien à signaler">
```

**Cas sans brief** : les quatre lignes centrales passent en `SANS OBJET` et le verdict ne porte que
sur `QUALITÉ`. Le dire explicitement dans l'agent — c'est le cas prévu par le tracker quand le
cadrage a été jugé inutile.

Numéroter les constats `Q1`, `Q2`, … dès leur première apparition, sur le modèle des `R<n>` de
`implementation-auditor`.

**vérif** — chaque commande porte sa valeur attendue :

```bash
grep -c '^## ' agents/plan-reviewer.md                    # attendu : 5
grep -c '^\(name\|description\|model\|tools\):' agents/plan-reviewer.md  # attendu : 4
grep -c 'Termine par ce bloc, et rien d.autre après' agents/plan-reviewer.md  # attendu : 1
grep -c 'SANS OBJET' agents/plan-reviewer.md              # attendu : ≥ 2
grep -c 'Write\|Edit' agents/plan-reviewer.md             # attendu : 0 dans le frontmatter
```

Les cinq `## ` attendus : `Entrée`, `Ce que tu juges`, `Interdits`, `Verdict`, `Rapport de sortie`.

### 2. Porter le compte des agents à trois dans `contrat.md`

Deux phrases seulement, devenues fausses avec un troisième agent :

- préambule (`contrat.md:18`) — « **Les deux agents sont hors de ce dispositif.** » et
  l'énumération `step-implementer` / `implementation-auditor` qui suit ;
- `## Contrat des sous-agents` (`contrat.md:122`) — « Vaut pour `step-implementer` et
  `implementation-auditor`. »

**Aucune règle nouvelle**, aucune exception : `plan-reviewer` reçoit des chemins absolus et ne
recopie rien, comme les deux autres. C'est le contrat existant qui s'étend, pas qui plie.

**vérif** : `grep -n 'plan-reviewer' skills/implementation-tracker/references/contrat.md`

### 3. Réécrire l'Étape 2 du tracker, points 2 et 3

Le point 2 (entrée en plan mode) devient la seule voie et ne change qu'à la marge. Le point 3 est
réécrit dans ce nouvel ordre :

1. plan construit et **écrit dans son fichier** — le harness l'assigne dès l'entrée en plan mode ;
2. **avant `ExitPlanMode`**, appel à `plan-reviewer` — transmettre les trois chemins absolus
   (racine, plan, brief ou la mention qu'il n'y en a pas) et **rien d'autre**, avec renvoi ancré
   vers [Contrat des sous-agents](skills/implementation-tracker/references/contrat.md#contrat-des-sous-agents) ;
3. `ExitPlanMode` présente **le plan et le verdict ensemble** ; rien n'est corrigé d'office, tout
   écart se règle avec l'utilisateur ;
4. reprise inchangée du chemin du plan dans la sortie d'`ExitPlanMode`, du `git check-ignore` et du
   versionnement.

**Supprimer la clause d'exception** « Le chantier arrive d'`intent-brief` → ses Étapes 6 et 7 ont
déjà fait le plan et la confrontation » : elle n'a plus d'objet, et la laisser ferait sauter la
revue dans le cas nominal.

Ajouter un tableau de conduite au retour, sur le modèle du tableau `RÉSULTAT` de l'Étape 4 :
`CONFORME` → poursuivre ; `RÉSERVES` → présenter les constats avec le plan ; `NON CONFORME` →
présenter le verdict avec le plan et laisser l'utilisateur trancher entre corriger le plan et
élargir le brief.

**vérif** — deux commandes distinctes, aux attentes opposées, jamais fusionnées :

```bash
grep -c 'Étapes 6 et 7' skills/implementation-tracker/SKILL.md   # attendu : 0
grep -c 'plan-reviewer'  skills/implementation-tracker/SKILL.md  # attendu : ≥ 1
```

### 4. Couper les Étapes 6 et 7 d'`intent-brief` et réécrire sa sortie

- **Supprimer `## Étape 6 — Passage au plan`** et **`## Étape 7 — Confrontation plan ↔ brief`**.
- **`## Étape 8 — Passage au suivi` devient `## Étape 6`**, formulation sobre retenue par
  l'utilisateur :

  > Brief validé dans `.claude/implementation/<slug>.brief.md`.
  >
  > Ouvre le suivi avec `/implementation-tracker` pour figer les étapes et démarrer — il reprendra
  > ce brief.

- **Préambule (`SKILL.md:19`)** : « Ce skill couvre les deux bouts : il cadre avant, et il confronte
  après (Étape 7) » ne tient plus. Le skill cadre ; la confrontation appartient au tracker.
- **`description` du frontmatter** : retirer « Confronte ensuite le plan produit au brief. »
- **« Quand ne pas cadrer »** : « passer directement au plan » et « enchaîner » renvoient à un plan
  que ce skill ne fait plus — rediriger vers le tracker.
- **`## Articulation avec implementation-tracker`** : ajuster la répartition des rôles.

**Ce qui reste, et qui n'est pas une mécanique de plan** — à ne pas supprimer par excès de zèle :
le titre de section `## Incertitudes à lever en plan` (l.58) et son rappel (l.75) nomment une
section du gabarit de brief, lequel est hors-périmètre ; l'Étape 5 point 1 (l.177-178) invoque
« une incertitude reportée » pour trancher `execution:`. Ce sont des **références** au plan, pas des
étapes qui en font un. Elles subsistent telles quelles.

Attention au signal de dérive n°1 : après cette étape, plus aucune mécanique de plan ni de
confrontation ne doit subsister — c'est-à-dire aucune étape qui entre en plan mode, en sort, ou
confronte le plan au brief.

**vérif** : `grep -c 'EnterPlanMode\|ExitPlanMode\|Confrontation plan' skills/intent-brief/SKILL.md`
doit renvoyer `0` (même motif que le contrôle d'ensemble n°1)

---

## Vérification d'ensemble

Pas de suite de tests ici — le dépôt est de la configuration en markdown. Les contrôles sont
structurels :

```bash
# 1. Aucune mécanique de plan résiduelle dans intent-brief (signal de dérive n°1)
grep -n 'EnterPlanMode\|ExitPlanMode\|Confrontation plan' skills/intent-brief/SKILL.md

# 2. La clause d'exception a disparu du tracker, l'agent y est appelé
grep -n 'Étapes\s*6 et 7' skills/implementation-tracker/SKILL.md
grep -n 'plan-reviewer' skills/implementation-tracker/SKILL.md

# 3. Aucune règle nouvelle dans contrat.md : le diff doit se limiter au compte des agents
#    (dérive n°3 — un ajout de règle ici signalerait une exception qu'on a décidé de ne pas créer)
git diff master -- skills/implementation-tracker/references/contrat.md

# 4. Le périmètre a tenu : exactement quatre fichiers
git diff --stat master
```

Contrôle final à la lecture : la numérotation des étapes d'`intent-brief` est continue de 0 à 6, et
aucun renvoi interne (« Étape 7 d'`intent-brief` », etc.) ne pointe vers une étape supprimée —
`grep -rn "Étape [678] d'\`\?intent-brief" skills/`.

## Ce que ce plan ne fait pas

- Il ne touche pas aux gabarits ni aux deux agents existants.
- Il ne réaligne pas les renvois du pipeline au-delà des quatre fichiers.
- Il ne persiste aucun rapport de revue de plan.
