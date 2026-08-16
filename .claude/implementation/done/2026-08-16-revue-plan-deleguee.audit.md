---
slug: revue-plan-deleguee
---

## 2026-08-16 — clôture — `1adfb84`

**Verdict** : RÉSERVES

### Vérifications exécutées

Étapes du suivi :

- `grep -c '^## ' agents/plan-reviewer.md` → `5` (attendu 5) — les cinq H2 sont bien `Entrée`,
  `Ce que tu juges`, `Interdits`, `Verdict`, `Rapport de sortie`
- `grep -c 'plan-reviewer' skills/implementation-tracker/references/contrat.md` → `2` (attendu ≥ 1)
- `grep -c 'Étapes 6 et 7' skills/implementation-tracker/SKILL.md` → `0` (attendu 0)
- `grep -c 'EnterPlanMode\|ExitPlanMode\|Confrontation plan' skills/intent-brief/SKILL.md` → `0`
  (attendu 0)

Vérifications complémentaires du plan (`.claude/plans/eager-wibbling-moon.md`) :

- `grep -c '^\(name\|description\|model\|tools\):' agents/plan-reviewer.md` → `4` (attendu 4)
- `grep -c 'Termine par ce bloc, et rien d.autre après' agents/plan-reviewer.md` → `1` (attendu 1)
- `grep -c 'SANS OBJET' agents/plan-reviewer.md` → `3` (attendu ≥ 2)
- `grep -c 'Write\|Edit' agents/plan-reviewer.md` → `0` (attendu 0)
- `grep -c 'plan-reviewer' skills/implementation-tracker/SKILL.md` → `1` (attendu ≥ 1)
- `grep -rn "Étape [678] d.\`\?intent-brief" skills/ agents/` → aucun résultat : aucun renvoi ne
  pointe vers une étape supprimée
- `grep -rn -i "confront" skills/ agents/ commands/` → seules occurrences restantes : la phrase
  neuve du tracker (l.123), un usage sans rapport (l.278) et deux dans `cloture.md` / `dette.md`,
  hors sujet. Aucune mécanique de confrontation résiduelle.
- `grep -n '^## ' skills/intent-brief/SKILL.md` → numérotation continue `Étape 0` … `Étape 6`,
  sans trou
- `grep -n 'deux agents\|les deux' .../contrat.md` → aucun résultat : le compte à deux a été purgé
  partout, pas seulement aux deux emplacements cités par le plan
- `git diff --stat master...revue-plan-deleguee` → 7 fichiers (voir R1)
- `git status --short` → `M settings.json` seul, non commité (hors chantier, exclu par
  l'utilisateur)

Aucune commande `NON EXÉCUTÉE`.

### Conformité à l'intention

- Critère « une seule voie mène au plan : `intent-brief` → `implementation-tracker` → plan » :
  **atteint, vérifié**. `intent-brief` n'a plus ni `EnterPlanMode` ni `ExitPlanMode` (grep = 0) ;
  son `## Étape 6 — Passage au suivi` est l'unique sortie et renvoie à `/implementation-tracker`.
  Le tracker pose explicitement « C'est ici que le plan se construit, et nulle part ailleurs »
  (`SKILL.md:122`). La clause d'exception a disparu (grep `Étapes 6 et 7` = 0).
- Critère « la comparaison brief ↔ plan est exécutée par un sous-agent » : **atteint, vérifié**.
  `agents/plan-reviewer.md` existe, est appelé au point 3 de l'Étape 2 du tracker.
- Critère « le sous-agent juge aussi la qualité du plan » : **atteint**. `### 2. Qualité du plan`
  couvre atomicité, fichiers nommés, commande de vérification, ordre des dépendances, et exige la
  vérification réelle des citations dans le dépôt.
- Critère « pas de brief → qualité du plan seulement » : **atteint**. Section `### Cas sans brief`
  de l'agent (interdiction explicite de reconstituer l'intention depuis le plan) + « **Pas de
  brief** → le lui dire explicitement » dans le tracker (`SKILL.md:132`).
- Critère « la revue a lieu avant la présentation ; verdict et plan dans le même `ExitPlanMode` » :
  **atteint**. `SKILL.md:126` (« **avant `ExitPlanMode`** ») et `SKILL.md:136-137`
  (« `ExitPlanMode` présente donc **le plan et le verdict ensemble** »), avec tableau de conduite
  par verdict.
- Hors-périmètre : **respecté sur les fichiers de production**. Les quatre fichiers annoncés sont
  touchés, et eux seuls ; `gabarit-brief.md`, `gabarit-suivi.md`, `audit.md`, `dette.md`,
  `cloture.md`, `implementation-auditor.md`, `step-implementer.md` sont intacts. Voir R1 pour la
  nuance sur le décompte du diff.
- Signaux de dérive : **aucun matérialisé**.
  - n°1 (mécanique de plan résiduelle dans `intent-brief`) : non déclenché. Les occurrences de
    « plan » subsistantes sont des *références* — titre de section du gabarit
    (`## Incertitudes à lever en plan`, l.59/67/76), arbitrage `execution:` (l.177), garde-fou
    « s'il déborde, c'est un plan déguisé » (l.184) — exactement les rescapés que le plan avait
    listés d'avance comme à ne pas supprimer.
  - n°2 (agent qui propose des alternatives de conception) : non déclenché. Interdit nommé
    (`plan-reviewer.md:99-101`) et cadrage « contrôle de contrat, pas critique d'architecture ».
  - n°3 (règle dupliquée dans un `SKILL.md` au lieu de `contrat.md`) : non déclenché. Aucune règle
    nouvelle dans `contrat.md` (le diff s'y limite au compte des agents, 6 lignes), et le tracker
    renvoie par ancre à `#contrat-des-sous-agents`. Le tableau `VERDICT` dupliqué dans le tracker
    suit le précédent déjà en place pour le tableau `RÉSULTAT` de `step-implementer`
    (`SKILL.md:282`), et `contrat.md:18-22` exclut explicitement les agents du dispositif de
    centralisation.
- Symptôme d'origine : **disparu**. La double compétence plan/confrontation n'existe plus ; la
  condition que le modèle devait détecter lui-même (`SKILL.md:126-127` de `master`) est supprimée,
  remplacée par un chemin unique inconditionnel.
- Incertitudes du brief : les deux sont tranchées. « Le plan mode autorise-t-il un sous-agent ? » →
  oui, constaté par appel réel (documenté au plan, § *Incertitude levée en cours de
  planification*). « Brief orphelin » → tranchée par la réécriture de l'Étape 6 en sortie unique
  vers `/implementation-tracker`, et par le renvoi de « Quand ne pas cadrer » vers le tracker, qui
  sait ouvrir un chantier sans brief (`SKILL.md:112-115`).

### Qualité du code

- **R1** — Le diff de branche compte **7 fichiers**, pas 4 : les quatre fichiers de production plus
  `.claude/implementation/revue-plan-deleguee.brief.md`,
  `.claude/implementation/revue-plan-deleguee.md` et `.claude/plans/eager-wibbling-moon.md`. Ces
  trois-là sont les artefacts de traçabilité du chantier lui-même, dont le versionnement est
  imposé par le tracker (« Le plan doit être versionné », `SKILL.md:156`) — ce n'est pas une
  violation du hors-périmètre. Le constat est posé parce que la commande de vérification inscrite
  dans le suivi, `git diff --stat master` « doit rester à quatre fichiers exactement », **ne passe
  pas telle qu'elle est écrite** : elle renvoie 7. La vérification est mal formulée, pas le
  résultat. Coût : à la relecture, cette ligne du suivi fait croire à un dépassement de périmètre
  qui n'existe pas.

- **R2** — `skills/implementation-tracker/SKILL.md:147-149` introduit une exception que le brief ne
  prévoit pas : « Seuls les défauts de rédaction relevés en `QUALITÉ` — une citation fausse, une
  commande de vérification inopérante — se corrigent sans arbitrage, et se disent quand même. » La
  décision du brief est absolue : « **Retour** : rien n'est corrigé d'office » (dit). L'assouplissement
  est raisonnable et borné, et la phrase préserve l'obligation de le dire — mais il n'apparaît
  **ni au journal de décisions du suivi, ni au plan**. Le dispositif d'`Autorité et divergence`
  exige qu'un écart daté à une décision `(dit)` s'inscrive dans le suivi ; les deux entrées
  présentes couvrent le revirement sur la transmission du plan et la non-persistance du rapport,
  pas celui-ci. Coût : une décision utilisateur amendée sans trace, invisible à la relecture du
  seul journal.

- **R3** — `agents/plan-reviewer.md:132-133` — dans le bloc de sortie, les lignes `CRITÈRES` et
  `HORS-PÉRIMÈTRE` portent la mention inline « — "SANS OBJET" sans brief », mais `DÉRIVE` et
  `INCERTITUDES` ne portent que « — sinon "aucun" » / « "aucune" ». La prose du § *Cas sans brief*
  (l.90-93) impose bien `SANS OBJET` aux quatre, conformément au brief, mais un agent qui recopie
  le bloc en fin de tour — c'est précisément l'usage du bloc — a sous les yeux une consigne qui
  l'oriente vers « aucun ». Coût : un rapport sans brief où deux lignes sur quatre disent « aucun »
  au lieu de « SANS OBJET », c'est-à-dire une absence de dérive affirmée alors qu'aucun signal
  n'existait pour la mesurer.

- **R4** — Le fonctionnement de tout le point 3 du tracker repose sur une prémisse d'environnement
  affirmée et non documentée : « Le harness assigne un fichier de plan dès l'entrée en plan mode et
  en autorise l'écriture ». Elle est corroborée par ce chantier même (le plan existe bien dans
  `.claude/plans/` et le suivi atteste d'une revue avant présentation), mais **l'audit ne peut pas
  la revérifier a posteriori** : le fichier committé ne prouve pas l'instant de son écriture.
  Constat rapporté comme invérifiable, non comme faux. Coût : si ce comportement du harness change,
  le point 3 devient inexécutable et aucun repli n'est écrit — le brief en avait envisagé un
  (revue après `ExitPlanMode`), que le plan a explicitement abandonné.

### Dette induite

Rien à signaler. Aucune duplication introduite : la règle des chemins absolus reste dans
`contrat.md` avec renvoi ancré depuis le tracker, et le bloc de sortie vit chez l'agent
conformément à `contrat.md:18-22`. Aucune abstraction créée, aucun contournement laissé en place.
Le solde net est une suppression : 57 lignes retirées pour 208 ajoutées, dont 141 de fichier neuf —
`intent-brief` perd 41 lignes pour 28.

### Bloquants

Aucun. R2 et R3 sont des corrections d'une ligne ; R1 porte sur la formulation d'une vérification
du suivi ; R4 est un risque à connaître, pas un défaut.
