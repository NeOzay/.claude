---
slug: enchainement-du-chantier
---

## 2026-10-10 — clôture — `e06e952`

**Verdict** : RÉSERVES

Diff audité : `git diff master...enchainement-du-chantier`, 18 fichiers, +620 −114, commits `AE0`
à `AE6` et la Passation `95ca718`. Brief présent et `validé` ; Suivi, Plan
(`.claude/plans/wiggly-discovering-sprout.md`) présents. Les neuf critères sont atteints et
vérifiés, aucun signal de dérive ne se matérialise dans le texte livré. Restent des constats que
l'utilisateur doit connaître avant l'aplatissement, dont une incohérence entre `etape.md` et
l'exception de C5 (R1).

### Vérifications exécutées

- E1 :
  `grep -n "Valider et faire la Passation" skills/git-smart-commit/references/confirmation.md && python3 scripts/check_pipeline.py`
  → ligne 36 trouvée ; « Pipeline conforme. », sortie 0.
- E1 (Plan) : `grep` des quatre libellés dans `etape.md` → lignes 44, 56, 57, 60, sortie 0.
- E2 :
  `awk '/Étape terminée/ { exit !(index($0,"contexte") < index($0,"propos")) }' … && python3 scripts/check_pipeline.py`
  → sortie 0 ; « Pipeline conforme. » (voir R8 sur la portée de l'`awk`).
- E2 (Plan) :
  `grep -n "Valider et lancer l'audit de Clôture" skills/implementation-tracker/SKILL.md` → ligne
  169, sortie 0.
- E3 : `grep -n "## Relecture" …/creation.md && python3 scripts/check_pipeline.py` → lignes 51 et
  64 ; « Pipeline conforme. », sortie 0. Le `grep` du Plan trouve aussi `AskUserQuestion` (57) et
  le choix 1 de `<L>E0` (141).
- E4 :
  `! grep -n "commandes de vérification à rejouer" …/SKILL.md && python3 scripts/check_pipeline.py`
  → aucune occurrence ; « Pipeline conforme. », sortie 0. `grep -n "commencer l'Étape"` → ligne 151.
- E5 :
  `grep -n "Valider le Brief et passer au Plan" skills/intent-brief/SKILL.md && gabarit check …brief.md --filled`
  → ligne 207 ; « rempli et conforme à la semence « brief » », sortie 0.
  `gabarit contract brief | grep -n "C1\|S1"` → lignes 55 et 68.
- E6 / C9 : `uvx rumdl fmt --check .` → sortie 0 sur la branche (« Found 23 issues in 11/244
  files », non réparables par `fmt`, sans effet sur le code de sortie). Base extraite par
  `git archive master` : sortie 1, « Would fix: 24/40 issues in 6 files ».
- E6, nature du changement : les six fichiers comparés à la base, blancs normalisés → identiques
  tous les six : reformatage seul.
- `list-dir validate` sur `technical-debt`, `technical-debt-solde`, `road-map-fait`, `road-map`
  → sortie 0 pour chacun, éléments conformes au contrat.
- `~/.claude/.venv/bin/python -m pytest scripts/tests/ -q` → 140 passed, sortie 0.
- `gabarit check .claude/implementation/enchainement-du-chantier.md` → conforme, sortie 0.
- S2 / S6 :
  `! git diff master --stat -- settings.json CLAUDE.md agents/implementation-auditor.md | grep .` →
  sortie 0, aucun de ces fichiers touché ; `agents/`, `cloture.md`, `audit.md` absents du diff.
- S5 : `git diff … -- skills | grep "300 000\|400 000"` → les deux seuils inchangés, seul le texte
  autour bouge.

### Conformité à l'intention

- **C1** : atteint. `creation.md` point 3 : `plan-reviewer` « une fois, avant `ExitPlanMode` »,
  verdict consigné dans `## Relecture` en tête du Plan, `AskUserQuestion`, Plan corrigé selon les
  réponses, puis `ExitPlanMode` ; l'ancien point 10 a disparu, la Passation est le choix 1 du
  point 9.
- **C2** : atteint. `etape.md` point 4, état initial, deux choix. Le libellé du choix 1 porte
  « (commit inclus) », écart au Brief tracé au journal du 2026-10-10.
- **C3** : atteint. Trois choix pour l'Étape, « les mêmes » pour la Retouche, le choix de
  Passation ajouté sur demande de l'appelant, que `execution.md` fait au-delà de 300 000 tokens ;
  le choix 1 devient « Valider et lancer l'audit de Clôture » après la dernière Étape.
- **C4** : atteint. Tableau des déclencheurs et section « Passation » d'`execution.md` : `contexte`
  avant la proposition ; aucune mesure ne reste après le commit.
- **C5** : atteint. La règle « un accord, un commit » reste ; l'exception, seule, est écrite sous
  « Ce qui compte comme accord ». Voir R1 et R3.
- **C6** : atteint. Phase 3 : message en quatre points, écarts signalés sans bloquer, « Aucune Étape
  ne commence sans la réponse de l'utilisateur ». Voir R2.
- **C7** : atteint. Semence `brief`, sections « Critères de réussite » et « Signaux de dérive ».
- **C8** : atteint. Phase 6, point 2 : message dédié, deux choix, « Seule une réponse à cette
  proposition vaut validation » ; le point 3 passe `statut` à `validé`. Voir R4.
- **C9** : atteint, exécuté ci-dessus.
- **Hors-périmètre** : respecté. Ni `settings.json`, ni le commit sans proposition, ni la forme des
  messages hors des choix, ni le fond de l'audit. `lexique-local-tronque.audit.md` n'est touché que
  par le reformatage d'E6, arbitré au Plan.
- **Signaux de dérive** : aucun matérialisé dans le texte livré. S1 : le seul commit sans
  proposition qu'autorise le diff est celui de Passation après le choix 1 de `<L>E0`. Que les
  commits de ce Chantier soient partis sur un choix de l'utilisateur ne se lit pas dans le dépôt :
  invérifiable. S3 : interdit en toutes lettres. S4 : « une fois », aucune relance écrite. S5 et
  S2 : voir les vérifications.
- **Symptôme d'origine** : traité dans le texte : chaque passage obligé se termine sur un choix qui
  enchaîne. Sa disparition réelle ne se constate qu'à l'usage, et R1 peut en coûter un tour à
  `<L>E0`.
- **Changement hors Plan** : voir R5.

### Qualité du code

- **R1** — `skills/git-smart-commit/references/etape.md` point 4 et tableau des cas,
  `confirmation.md` § « Ce qui est présenté ». L'exception de C5 n'est écrite que sous « Ce qui
  compte comme accord » et dans `execution.md`. `etape.md`, la procédure même du commit de
  Passation, dit toujours « session, Passation — des commits mécaniques : l'accord se demande sans
  le titre », et son tableau garde « la Passation acceptée ». `confirmation.md` répète, deux
  paragraphes au-dessus de l'exception, « Un commit mécanique — état initial, session, Passation —
  […] L'accord se demande quand même », sans réserve. Un agent qui suit `etape.md` redemandera
  l'accord après « Valider et faire la Passation (commit inclus) » : `<L>E0` et la Passation
  reprennent deux tours, ce que le But voulait supprimer. Le défaut est sûr, il n'ouvre pas S1,
  mais deux textes de la même procédure se contredisent.
- **R2** — `skills/implementation-tracker/SKILL.md`, Phase 3, point 4 : « la proposition de
  commencer l'Étape X ». Rien n'est dit quand aucune Étape ne reste `[ ]` : c'est l'état de ce
  Chantier à sa reprise, où la prochaine action est la Clôture, que la Phase 5 ne compte pas parmi
  ses déclencheurs. Rien non plus pour une Étape `[>]` interrompue, à reprendre plutôt qu'à
  commencer. Le point 2, « sa prochaine action », couvre en partie le premier cas, sans proposition
  à la clé.
- **R3** — `confirmation.md`, motif de l'exception : « Rien n'a encore commencé : la section
  `## Passation` ne porte rien à relire ». `creation.md` point 9 justifie la même Passation parce
  que « la session de création est celle qui en sait le plus sans l'avoir écrit ». Et la Passation
  de ce Chantier après `AE0` (`95ca718`) porte quatre points « À savoir », que l'utilisateur aurait
  eu intérêt à relire. L'exception est une décision de l'utilisateur, au Brief (« dit ») : ce
  n'est pas un défaut d'implémentation. Mais son motif écrit est contredit par le dépôt, et la
  règle laisse entrer dans l'historique un contenu qu'aucun regard n'a validé : c'est le mode de
  défaillance que `confirmation.md` décrit lui-même.
- **R4** — `skills/intent-brief/SKILL.md`, Phase 6 et 7. Lancé seul, « Valider le Brief et passer
  au Plan » ne passe pas au Plan : la Phase 7 propose `/implementation-tracker`. L'arbitrage Q4 du
  Plan a choisi ce comportement, mais le libellé promet autre chose que ce qui suit.
- **R5** — `.gitignore` : `feedback/` (« Brouillons de retours de Claude Code, locaux à la
  machine ») est ajouté dans le commit `AE0`. Ce changement n'est ni dans le Plan, ni au journal,
  et n'a pas de lien avec le Brief. Il est inoffensif, mais il sera aplati sur `master` sous le
  titre du Chantier sans que rien ne l'explique.
- **R6** — Lexique, dans la prose ajoutée : `intent-brief` Phase 6 écrit « le chemin du brief » à
  côté de « Valider le Brief », et `creation.md` « en tête du plan », « plan corrigé selon les
  réponses » pour le Plan au sens défini. `execution.md` garde « proposer le commit d'étape » dans
  une ligne réécrite. C'est cohérent avec la prose voisine, en minuscule avant ce Chantier, mais
  pas avec la règle de la majuscule. Faible.

### Dette induite

- **R7** — Les libellés des choix sont recopiés littéralement dans cinq fichiers, de deux skills :
  `etape.md` (6 occurrences), `execution.md` (6), `creation.md` (2), `confirmation.md` (1),
  `SKILL.md` du tracker (1). La correspondance entre un libellé et sa suite, au tableau « Après un
  commit d'Étape ou de Retouche », ne repose que sur l'identité des chaînes, et
  `scripts/check_pipeline.py` ne la contrôle pas. Coût futur : un renommage oublié dans un fichier
  laisse un choix sans suite ou une exception d'accord qui ne s'applique plus. Le journal du
  2026-10-10 a déjà dû propager un changement de libellé à la main, en E2 et E3.
- **R8** — La vérification d'E2, `awk … index($0,"contexte") < index($0,"propos")`, passe aussi
  quand « contexte » disparaît de la ligne : `index` rend alors 0. Elle ne garde pas l'ordre
  qu'elle prétend garder. L'ordre est vérifié ici à la lecture de la ligne 11 d'`execution.md`.
  Le coût est nul tant que la commande ne sert que pour cette Étape.

### Bloquants

Aucun. R1 est le constat à trancher en priorité avant la Clôture : sans lui, le choix 1 de `<L>E0`
ne tient pas sa promesse d'un seul tour.

## 2026-10-10 — clôture — `e80dda8`

**Verdict** : RÉSERVES

Diff audité : `git diff master...enchainement-du-chantier`, 18 fichiers, +626 −116, commits `AE0`
à `AE6`, la Passation `95ca718` et la Retouche `AE6.1` (`e80dda8`, 4 fichiers, +11 −7), qui
traite R1, R2 et R3 de l'audit `e06e952`. Brief présent et `validé` ; Suivi et Plan
(`.claude/plans/wiggly-discovering-sprout.md`) présents. Le diff entier a été rejugé, et la
Retouche lue en détail. Les neuf critères restent atteints et vérifiés, et aucun signal de dérive ne
se matérialise. R1, R2 et R3 de l'audit précédent sont levés. Ses R4 à R8 restent ouverts, sans
changement : la Retouche ne les visait pas. Ils sont repris ci-dessous sous R1, R2, R3, R5 et R6.

### Vérifications exécutées

- E1 :
  `grep -n "Valider et faire la Passation" skills/git-smart-commit/references/confirmation.md && python3 scripts/check_pipeline.py`
  → ligne 36 ; « Pipeline conforme. » (9 contrôles ✓), sortie 0.
- E2 :
  `awk '/Étape terminée/ { exit !(index($0,"contexte") < index($0,"propos")) }' … && python3 scripts/check_pipeline.py`
  → sortie 0 ; « Pipeline conforme. ». L'ordre « mesurer le contexte » puis « proposer le commit »
  est vérifié à la lecture de la ligne 11 d'`execution.md` (voir R6).
- E3 : `grep -n "## Relecture" …/creation.md && python3 scripts/check_pipeline.py` → lignes 51 et
  64 ; « Pipeline conforme. », sortie 0.
- E4 :
  `! grep -n "commandes de vérification à rejouer" …/SKILL.md && python3 scripts/check_pipeline.py`
  → aucune occurrence ; « Pipeline conforme. », sortie 0.
- E5 :
  `grep -n "Valider le Brief et passer au Plan" skills/intent-brief/SKILL.md && gabarit check …brief.md --filled`
  → ligne 207 ; « rempli et conforme à la semence « brief » », sortie 0.
- E6 / C9 : `uvx rumdl fmt --check .` → sortie 0 sur la branche (« Found 22 issues in 9/245
  files », non réparables par `fmt`). Base extraite par `git archive master` dans un répertoire
  temporaire : sortie 1.
- Vérification de l'État courant :
  `~/.claude/.venv/bin/python -m pytest scripts/tests/ -q` → 140 passed, sortie 0.
- `gabarit check .claude/implementation/enchainement-du-chantier.md` → « conforme à la semence
  « suivi » », sortie 0, champ `audit` ajouté par `AE6.1` compris.
- `list-dir validate` sur les six répertoires de `.claude/implementation/todo/` → sortie 0 pour
  chacun.
- S2 / S6 :
  `git diff master...enchainement-du-chantier --stat -- settings.json CLAUDE.md agents/ …/cloture.md …/audit.md`
  → sortie vide : aucun de ces fichiers n'est touché.
- S5 : `git diff master...enchainement-du-chantier -- skills | grep -E "^[+-].*(300 000|400 000)"`
  → les deux seuils restent inchangés, seul le texte autour bouge.
- Restes de l'ancienne formulation :
  `grep -rn "Passation acceptée\|Rien n'a encore commencé\|s'il veut la Passation" skills agents rules`
  → aucune occurrence, sortie 1.

### Conformité à l'intention

- **C1** : atteint. Inchangé depuis `e06e952` : `creation.md` point 3, `plan-reviewer` « une
  fois », `## Relecture` en tête, `AskUserQuestion`, correction, `ExitPlanMode` ; la Passation est
  le choix 1 du point 9.
- **C2** : atteint. `etape.md` lignes 44 à 46. Le libellé « (commit inclus) » s'écarte du Brief :
  c'est tracé au journal du 2026-10-10.
- **C3** : atteint. `etape.md` lignes 55 à 64 : trois choix, le cas de la dernière Étape, le choix
  de Passation sur demande de l'appelant, et les mêmes choix pour la Retouche.
- **C4** : atteint. `execution.md` ligne 11 et section « Passation » : `contexte` se mesure avant la
  proposition.
- **C5** : atteint, et désormais cohérent. L'exception est écrite une fois, sous « Ce qui compte
  comme accord ». Les deux passages qui la contredisaient la renvoient maintenant :
  `confirmation.md` ligne 19 (« hors l'exception ci-dessous ») et `etape.md` lignes 42 et 43
  (« sauf pour la Passation qui suit … déjà accordée »). Le tableau des cas dit « la Passation
  choisie ». L'ancien R1 est levé : un agent qui suit `etape.md` ne redemande plus l'accord.
- **C6** : atteint. Phase 3, point 4 : il couvre maintenant l'Étape `[>]` à reprendre et la Clôture
  quand toutes les Étapes sont `[x]`. L'ancien R2 est levé. L'accord à « lancer l'audit de
  Clôture » proposé en reprise entre dans le déclencheur de la Phase 5 « quand l'utilisateur
  déclare l'implémentation terminée ».
- **C7** : atteint. Semence `brief`, inchangée depuis `e06e952`.
- **C8** : atteint. Inchangé depuis `e06e952`. Voir R1.
- **C9** : atteint, exécuté ci-dessus.
- **Hors-périmètre** : respecté. `AE6.1` ne touche ni `settings.json`, ni la forme des messages
  hors des choix, ni le fond de l'audit.
- **Signaux de dérive** : aucun ne se matérialise dans le texte livré. S1 : le seul commit sans
  nouvelle proposition que le texte autorise reste celui de Passation après le choix 1 de `<L>E0`.
  Que les commits du Chantier, `AE6.1` compris, soient partis sur un choix de l'utilisateur ne se
  lit pas dans le dépôt : c'est invérifiable. S3 : interdit en toutes lettres (« Aucune Étape ne
  commence sans la réponse de l'utilisateur »). S4 : « une fois ». S2, S5, S6 : voir les
  vérifications.
- **Symptôme d'origine** : traité dans le texte. Chaque passage obligé se termine sur un choix qui
  enchaîne, et l'ancien R1, qui coûtait un tour à `<L>E0`, est levé. Sa disparition réelle ne se
  constate qu'à l'usage.
- **Ancien R3** (motif de l'exception) : levé. `confirmation.md` ne prétend plus que la section
  « ne porte rien à relire ». Il dit ce qu'elle transmet (« ce que la création a établi ») et ce qui
  borne le risque (« la branche ne rejoint la Base qu'aplatie, après audit »). Le motif est
  cohérent avec `creation.md` point 9. Voir R4.

### Qualité du code

- **R1** (ex-R4 de `e06e952`, ouvert) — `skills/intent-brief/SKILL.md`, Phases 6 et 7. Quand
  `intent-brief` est lancé seul, le choix « Valider le Brief et passer au Plan » ne passe pas au
  Plan : la Phase 7 propose `/implementation-tracker`. Le comportement suit l'arbitrage Q4 du Plan,
  mais le libellé promet autre chose que ce qui suit.
- **R2** (ex-R5, ouvert) — `.gitignore` : `feedback/` est ajouté dans le commit `AE0`, sans entrée
  au Plan ni au journal, et sans lien avec le Brief. Le changement est inoffensif, mais il sera
  aplati sur `master` sous le titre du Chantier sans que rien ne l'explique.
- **R3** (ex-R6, ouvert, faible) — Lexique : `intent-brief` Phase 6 écrit « le chemin du brief »,
  et `creation.md` « en tête du plan », « plan corrigé », pour les termes définis. C'est cohérent
  avec la prose voisine, mais pas avec la règle de la majuscule. La prose ajoutée par `AE6.1`
  (« le Brief et le Plan », « la Base ») respecte, elle, la règle.
- **R4** (nouveau, faible) — `AE6.1` réécrit le motif de l'exception de C5, que le Brief porte
  comme une « Décision » de l'utilisateur sous une autre justification (« rien n'a commencé, la
  section `## Passation` ne porte rien que l'utilisateur doive relire (dit) »). Le Suivi n'en garde
  aucune trace : le journal s'arrête au 2026-10-10 sur le libellé « (commit inclus) ».
  `execution.md` § Retouche le demande pourtant : « une décision prise en Retouche va au journal
  comme toute autre ». Une fois le Chantier archivé, rien ne dira pourquoi le texte livré justifie
  l'exception autrement que le Brief. Le choix de ne traiter que R1 à R3 de `e06e952` n'est pas
  noté non plus : R4 à R8 iront au registre de dette à la Clôture sans que le Suivi dise pourquoi
  ils ont été laissés.

### Dette induite

- **R5** (ex-R7, ouvert) — Les libellés des choix sont recopiés littéralement dans cinq fichiers de
  deux skills. Après `AE6.1`, « Valider et faire la Passation (commit inclus) » apparaît dans
  `etape.md` (deux fois), `confirmation.md`, `creation.md` et `execution.md`. La correspondance
  entre un libellé et sa suite ne repose que sur l'identité des chaînes, et
  `scripts/check_pipeline.py` ne la contrôle pas. `AE6.1` a ajouté une occurrence de plus
  (`etape.md` ligne 43), qui conditionne une exception d'accord : si un renommage l'oublie,
  l'exception ne s'applique plus, ou s'applique à un choix qui n'existe plus.
- **R6** (ex-R8, ouvert) — La vérification d'E2, `awk … index($0,"contexte") < index($0,"propos")`,
  passe aussi quand « contexte » disparaît de la ligne, puisque `index` rend alors 0. Le coût reste
  nul tant que la commande ne sert qu'à cette Étape.

### Bloquants

Aucun. Les critères sont atteints et le constat prioritaire de `e06e952` (son R1) est levé. Restent
des réserves à trancher avant l'aplatissement : R1 et R2 ont un effet visible, sur un libellé et
sur `master` ; R4 touche à la traçabilité ; R3, R5 et R6 sont de la dette faible.
