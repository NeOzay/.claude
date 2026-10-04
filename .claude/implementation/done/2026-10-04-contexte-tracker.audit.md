---
slug: contexte-tracker
---

## 2026-10-04 — clôture — `38d27af`

**Verdict** : RÉSERVES

Brief présent et lu. Le Suivi l'élargit en trois points datés du 2026-10-04 (Q1, Q3, Q7) : c'est
le Suivi qui fait foi, et le critère `rumdl` est jugé sous sa forme `uvx rumdl fmt --check`.

### Vérifications exécutées

- `.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests` → 35 passés, 0 échec
- `.venv/bin/python -m pytest skills/implementation-tracker scripts/tests` → 155 passés, 0 échec
- `uvx ruff check skills/implementation-tracker statusline-command.py` → `All checks passed!`
  (sur la Base, `statusline-command.py` seul : `Found 3 errors.`, corrigées comme Q1 le prévoyait)
- `uvx ruff format --check skills/implementation-tracker statusline-command.py` → `7 files already
  formatted`
- `uvx --with pytest basedpyright skills/implementation-tracker` → `0 errors, 0 warnings, 0 notes`
- `uvx --with pytest basedpyright statusline-command.py` → `0 errors` (`Found 1 source file` :
  le fichier est bien analysé, bien qu'il soit hors de l'`include`)
- `uvx ruff check .` sur tout le dépôt → 2 erreurs (Base extraite par `git archive` : 5) ; aucune
  régression
- `contexte` → `169072` ; ORACLE du Plan → `169072` ; écart 0 (< 5 000). Lancée depuis un
  sous-agent, `CLAUDE_CODE_SESSION_ID` y vaut l'identifiant de la session parente : la mesure est
  celle de la session principale, ce que la procédure attend.
- `gabarit new suivi <scratchpad>/s.md` → pose `## Passation` / `<OPTIONNEL>` entre `État courant`
  et `Journal de décisions`
- `gabarit check --filled .claude/implementation/done/2026-10-04-shadow-skill.md` → « rempli et
  conforme ». Quatre archives plus anciennes de `done/` échouent sur `champ « skills » — manquant`,
  sans rapport avec la Passation (section facultative, `required` absent = `false`).
- `gabarit check --filled .claude/implementation/contexte-tracker.md` → conforme
- `git diff --no-index --word-diff` de `master:SKILL.md` l. 97–232 et 259–359 contre
  `references/creation.md` et `references/execution.md` **à `0d0b385` (E4)** → seuls changent le
  niveau des titres et les liens relatifs (le renommage « Phase » vient à E5). À `HEAD`, s'y
  ajoutent les titres « Phase » (E5) et les ajouts d'E6, rien d'autre.
- `grep -rn "Étape [0-6]" skills/implementation-tracker/SKILL.md` → vide ;
  `grep -rn "Étape [0-6]" skills/implementation-tracker` → vide
- `grep -rln "Étape 2" .claude/implementation/todo/technical-debt` → vide
- `git grep "Étape [0-6]"` sur `skills shadow-skills agents OUTILLAGE.md scripts` → ne restent que
  les titres propres à `intent-brief`, à `debt-review` et à la semence `brief` (hors périmètre,
  journalisé)
- `grep -rn "/clear" skills/implementation-tracker` → deux lignes : `creation.md:139` (après
  `<L>E0`) et `execution.md:99` (au-delà de 300 000 au commit d'Étape)
- `list-dir validate .claude/implementation/todo/technical-debt` → 80 éléments conformes
- `.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. », sortie 0 ; 58 renvois
  entre skills résolvent
- `uvx rumdl fmt --check` sur les fichiers du Plan → sortie 0
- `uvx rumdl check` (forme d'origine du Brief) → sortie 1 : `contrat.md:214` MD028 et
  `list-dir/technical-debt/patrons/review.md:1` MD041 ; **mêmes deux constats sur la Base**

### Conformité à l'intention

- Critère « `SKILL.md` ne porte plus création ni exécution, renvoie vers deux références, garde
  vérifications, routage et reprise » : atteint. Phases 0, 1, 3 en place ; Phases 2 et 4 réduites
  à une consigne de lecture de `references/creation.md` / `references/execution.md`.
- Critère « déplacement à l'identique » : atteint, vérifié par word-diff à E4.
- Critère « aucun `Étape [0-6]` dans `SKILL.md`, aucun renvoi aux anciens titres » : atteint pour
  les titres. Un renvoi garde un chemin périmé (R6).
- Critère « `/clear` proposé après `<L>E0`, et à un commit d'Étape seulement au-delà de 300k » :
  atteint pour les deux seuls points qui proposent `/clear`. Une phrase déplacée telle quelle
  qualifie pourtant le retour de chaque Étape déléguée de « coupure naturelle entre deux
  sessions » (R1).
- Critère « la semence déclare `## Passation`, la procédure la réécrit avant le commit qui précède
  une coupure, la reprise la restitue » : atteint (`contract.toml`, `creation.md` point 9,
  `execution.md` l. 99, `SKILL.md` Phase 3).
- Critère « l'agent lit la taille de son contexte par une commande, qui concorde avec le dernier
  `usage` » : atteint, écart 0 mesuré.
- Critère « linters et formateur passent sur les fichiers touchés » : atteint sous la forme du
  Suivi (`rumdl fmt --check`). La forme `rumdl check` du Brief échoue sur `contrat.md`, un fichier
  touché, mais sur un constat antérieur au Chantier et identique sur la Base.
- Hors-périmètre : respecté. La reprise lit toujours le Suivi en entier ; aucun hook ajouté ;
  `intent-brief` ne change que sur ses deux renvois (l. 228, 235) ; `agents/` intact.
- Signaux de dérive : aucun matérialisé.
  - Déplacement : pur, vérifié.
  - `statusline-command.py` : il ne fait que lire `session_id` et `current_usage` puis appeler
    `contexte ecrire`. S'y ajoutent les trois corrections `ruff` acceptées (Q1).
  - Coupure ailleurs : aucune autre proposition de `/clear`. Voir R1, jugé en réserve et non en
    dérive : la phrase ne propose pas de coupure, et la règle explicite de `execution.md` (« 300 000
    tokens ou moins : Rien ») la contredit.
- Symptôme d'origine (Chantiers au-delà de 400k) : invérifiable en l'état. Il ne se constatera que
  sur les Chantiers à venir. Le mécanisme est en place et sa mesure fonctionne sur une session
  réelle.

### Qualité du code

- **R1** — `skills/implementation-tracker/references/execution.md:75-77` — « Rendre la main après
  chaque étape déléguée […] c'est […] la coupure naturelle entre deux sessions ». En
  `execution = "délégué"`, toute Étape substantielle est déléguée : la phrase revient à suggérer
  une coupure à chaque Étape, ce que le Brief a « rejeté d'emblée », alors que la règle nouvelle
  (l. 89–107) n'en propose qu'au-delà de 300 000. La phrase a été déplacée à l'identique, comme le
  critère l'exigeait. Mais E6, qui réécrivait déjà ce fichier, ne l'a pas réconciliée avec la
  règle nouvelle. Un agent peut lire deux consignes contraires.
- **R2** — `SKILL.md` Phase 3 et semence `suivi` — la Passation n'est jamais vidée. Seule une
  coupure proposée par la procédure la réécrit. Cas limite : une session s'arrête autrement (Clôture
  de l'utilisateur, fin sous le seuil, sortie sans commit d'Étape). La reprise suivante restitue
  alors la Passation d'une session antérieure comme si elle était la dernière. Par ailleurs, un
  Suivi posé avant ce Chantier n'a pas la section, et la consigne d'`execution.md:99` (« Réécrire
  la section ») ne dit pas de l'ajouter.
- **R3** — `SKILL.md` Phase 3 — la reprise ne renvoie pas à la Phase 4. Avant le Chantier, la
  règle du commit d'Étape était dans le `SKILL.md` toujours chargé. Désormais, la mesure du
  contexte, cœur du mécanisme, n'a lieu que si l'agent lit `execution.md` « au début de
  l'exécution ». Un agent qui enchaîne après la reprise sans lire la référence saute la mesure, et
  rien ne le signale. Risque faible : la consigne figure dans le `SKILL.md` chargé.
- **R4** — `skills/implementation-tracker/scripts/contexte.py` — chemins d'échec hors du contrat
  de sa docstring (« message sur stderr ») :
  - dans `ecrire`, une `OSError` de `mkdir`, `mkstemp` ou `os.replace` sort en trace Python, et
    laisse le fichier `.<session>.*` temporaire derrière elle ;
  - dans `lire`, un fichier non UTF-8 lève `UnicodeDecodeError`, qui n'est pas une `OSError`.

  La sortie reste non nulle : l'échec reste fermé. Seul le message promis manque.
- **R5** — `statusline-command.py:84-88` — la somme des trois champs est calculée hors du `try`.
  Un `current_usage` aux valeurs `null` ou non entières lève `TypeError` et éteint toute la
  statusline, contre la docstring (« EN SILENCE QUOI QU'IL ARRIVE »). La probabilité est faible et
  le code voisin a la même exposition, mais la promesse écrite n'est pas tenue.
- **R6** — `OUTILLAGE.md:14` — « cinq commandes » alors que `bin/` expose sept liens
  (`commit-chantier` et `lexique` absents de la table). L'inexactitude existait déjà sur la Base
  (« quatre » pour six). Le Chantier a réécrit la phrase sans la rendre vraie. Même nature :
  `point-3-premisse-harness-sans-repli.md` cite toujours `skills/implementation-tracker/SKILL.md`
  pour un contenu passé dans `references/creation.md` (noté au journal pour la Clôture). Et
  `lettre-attribuee-sans-reservation.md` dit « Phase 2, point 8 » pour le commit de l'état
  initial, qui est le point 9 (erreur héritée de la Base).

### Dette induite

- **R7** — `contexte.py`, repli `~/.cache/claude-contexte/` — un fichier par session, jamais
  supprimé quand `XDG_RUNTIME_DIR` est absent. `XDG_RUNTIME_DIR` est un tmpfs vidé à la
  déconnexion, mais le repli s'accumule sans borne. Coût faible : quelques octets par session.
- **R8** — À reporter au registre à la Clôture, comme le journal le prévoit :
  - la part statusline de `statusline-hors-des-linters` est soldée, ce que la fiche ne dit pas
    encore ;
  - `intent-brief` et `debt-review` titrent leurs phases « Étape N », en collision avec le
    Lexique ;
  - le chemin périmé de `point-3-premisse-harness-sans-repli` (R6).

### Bloquants

Aucun. R1 et R2 sont à arbitrer par l'utilisateur avant l'aplatissement : ils touchent
directement le mécanisme de coupure que le Chantier introduit.

## 2026-10-04 — clôture — `b323e5a`

**Verdict** : RÉSERVES

Brief présent et lu ; Suivi, Plan et diff `master...contexte-tracker` lus (8 commits, `c13ccab` à
`b323e5a`). Le Suivi élargit le Brief en trois points datés (Q1, Q3, Q7) : il fait foi, et le
critère `rumdl` est jugé sous la forme `uvx rumdl fmt --check`. Cet audit couvre le diff entier ;
E7 (`b323e5a`), qui traite R1 à R6 de l'audit précédent, y est lu en détail. La numérotation des
constats reprend à R9 pour ne pas croiser les R1 à R8 que cite le commit d'E7.

### Vérifications exécutées

- `.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. », sortie 0 (58 renvois entre
  skills résolvent, 33 chemins de skill cités existent)
- `.venv/bin/python -m pytest skills/implementation-tracker scripts/tests` → 158 passés, 0 échec
- `uvx ruff check skills/implementation-tracker statusline-command.py` → `All checks passed!`
- `uvx ruff format --check skills/implementation-tracker statusline-command.py` → `7 files already
  formatted`
- `uvx --with pytest basedpyright skills/implementation-tracker statusline-command.py` → `0 errors,
  0 warnings, 0 notes`. `statusline-command.py` est bien analysé malgré l'`include` : une copie
  piégée (`y: int = "b"`) rend `1 error`
- `uvx --with pytest basedpyright` sur tout le dépôt, comparé à la Base extraite par `git archive` :
  fichiers versionnés 133 → 81 erreurs, aucune hausse par fichier. Le total brut (6580) vient de
  `skills/synced/`, ignoré par git et étranger au Chantier
- `uvx ruff check .` → 2 erreurs ; Base extraite → 5 : aucune régression
- `uvx rumdl fmt --check` sur la liste du Plan → sortie 0 ; sur les trois fiches de dette touchées
  → `No issues found`, sortie 0
- `uvx rumdl check` (forme d'origine du Brief) → sortie 1 : `contrat.md:214` MD028 et
  `list-dir/technical-debt/patrons/review.md:1` MD041, **identiques sur la Base extraite**
- `contexte` → `193394`. La commande `ORACLE` du Plan, telle qu'écrite → **échec**
  `KeyError: 'message'` (R12). Même calcul, en écartant la ligne fautive → `193394` : écart 0
  (< 5 000)
- Statusline alimentée à la main (`XDG_RUNTIME_DIR` dans le scratchpad) : `current_usage` à
  `input_tokens: null` → sortie 0, rien écrit ; `current_usage` chaîne → sortie 0, rien écrit ;
  valeurs entières → `213` écrit et relu par `contexte` ; `current_usage: null` → sortie 0
- `contexte ecrire abc 12` avec un fichier à la place du répertoire → `contexte : écriture
  impossible dans … : File exists`, sortie 1, aucun temporaire laissé ; `contexte ecrire ../x 1`
  → sortie 2 ; `contexte foo` → usage, sortie 2 ; session sans mesure → message, sortie 1
- `git diff --no-index --word-diff` de `master:SKILL.md` l. 97–232 et 259–359 contre
  `references/creation.md` et `references/execution.md` à `0d0b385` (E4) → seuls changent le
  niveau des titres et les liens relatifs. À `HEAD` s'y ajoutent les titres « Phase » (E5), les
  ajouts d'E6 et la reformulation de R1 (E7), rien d'autre. Le reste de `master:SKILL.md`, comparé
  à `HEAD:SKILL.md` → renommages « Phase » et ajouts prévus (Phases 2 et 4 en renvoi, Passation
  en Phase 3)
- `grep -rn "Étape [0-6]" skills/implementation-tracker/SKILL.md` → vide ;
  `grep -rn "Étape [0-6]" skills/implementation-tracker` → vide
- `grep -rn "Étape [0-6]" skills shadow-skills OUTILLAGE.md agents scripts | grep -i "tracker\|suivi"`
  → seul `intent-brief/SKILL.md:206` (« Étape 6 — Passage au suivi »), titre propre à
  `intent-brief`, toléré au journal
- `git grep` des ancres `#étape-…` → seules des archives de `done/` en citent, vers `debt-review`
- `grep -rln "Étape 2" .claude/implementation/todo/technical-debt` → vide
- `grep -rn "/clear" skills/implementation-tracker` → deux lignes : `creation.md:139` (après
  `<L>E0`) et `execution.md:99` (au-delà de 300 000 au commit d'Étape)
- `gabarit new suivi <scratchpad>/s.md` → `## Passation` / `<OPTIONNEL>`, entre `État courant` et
  `Journal de décisions`
- `gabarit check --filled .claude/implementation/done/2026-10-04-shadow-skill.md` → « rempli et
  conforme » ; `gabarit check --filled .claude/implementation/contexte-tracker.md` → conforme
- `list-dir validate .claude/implementation/todo/technical-debt` → 80 éléments conformes
- `ls bin/` → 7 liens, autant que de lignes de commande dans la table d'`OUTILLAGE.md`
- `~/.config/nvim/lua/chantier.lua` : ne lit que le frontmatter du Suivi, et la section ajoutée
  ne le touche pas

### Réserves de l'audit `38d27af`

- R1 : levée — `execution.md:75-77` dit désormais que rendre la main n'est pas couper la session.
- R2 : levée sur ses deux cas. La reprise remet la Passation au marqueur, et `execution.md:99` dit
  d'ajouter la section à un Suivi plus ancien. Un chemin reste ouvert (R9), et la remise en crée un
  autre (R10).
- R3 : levée — `SKILL.md:132` renvoie à la Phase 4, et `SKILL.md:138` en fixe le moment.
- R4 : levée — écriture impossible et fichier non UTF-8 rendent un message et une sortie 1 ;
  testés et exécutés.
- R5 : levée — le calcul est dans le `try`, et `null` comme chaîne laissent la statusline en vie.
  Exécuté.
- R6 : levée — `OUTILLAGE.md` dit « sept », pour 7 liens dans `bin/`. Les deux fiches sont
  corrigées : `creation.md` pour le chemin, le point 9 pour le commit de l'état initial.
- R7 : ouverte, inchangée (repli `~/.cache/claude-contexte/` sans purge).
- R8 : à reporter au registre à la Clôture, comme le journal le prévoit. Son troisième point, le
  chemin périmé, est soldé par E7. Restent la part statusline de `statusline-hors-des-linters` et
  les titres « Étape N » d'`intent-brief` et de `debt-review`.

### Conformité à l'intention

- Critère « `SKILL.md` ne porte plus création ni exécution, renvoie vers deux références, garde
  vérifications, routage et reprise » : atteint. Les Phases 0, 1, 3, 5 et 6 sont en place ; les
  Phases 2 et 4 se réduisent à une consigne de lecture.
- Critère « déplacement à l'identique » : atteint, vérifié par word-diff à E4. Les changements
  ultérieurs du texte déplacé sont des ajouts d'E6 et la seule reformulation de R1, décidée par
  l'utilisateur et journalisée.
- Critère « aucun `Étape [0-6]` dans `SKILL.md`, aucun renvoi aux anciens titres » : atteint.
- Critère « `/clear` proposé après `<L>E0`, et à un commit d'Étape seulement au-delà de 300k » :
  atteint ; aucune autre consigne ne suggère plus de coupure.
- Critère « la semence déclare `## Passation`, la procédure la réécrit avant le commit qui précède
  une coupure, la reprise la restitue » : atteint (`contract.toml`, `creation.md` point 9,
  `execution.md:99`, `SKILL.md` Phase 3).
- Critère « l'agent lit la taille de son contexte par une commande, qui concorde avec le dernier
  `usage` » : atteint, écart 0 mesuré sur la session courante.
- Critère « linters et formateur passent sur les fichiers touchés » : atteint sous la forme du
  Suivi. La forme `rumdl check` du Brief échoue sur deux constats antérieurs au Chantier,
  identiques sur la Base.
- Hors-périmètre : respecté. La reprise lit toujours le Suivi en entier. Aucun hook n'est ajouté.
  `intent-brief` ne change que sur ses deux renvois, et `agents/` est intact.
- Signaux de dérive : aucun matérialisé.
  - Déplacement : pur à E4. E7 n'a réécrit qu'une phrase, sur décision journalisée.
  - `statusline-command.py` : lit `session_id` et `current_usage`, appelle `contexte ecrire`, et
    s'éteint en silence en cas d'échec. S'y ajoutent les trois corrections `ruff` acceptées (Q1).
  - Coupure ailleurs : non, seuls deux points proposent `/clear`.
- Symptôme d'origine (Chantiers au-delà de 400k) : invérifiable en l'état. Il se constatera sur les
  Chantiers à venir. Le mécanisme est en place, et sa mesure est juste sur une session réelle.

### Qualité du code

- **R9** — Cycle de vie de la Passation, chemin resté ouvert. La section est écrite pour une
  coupure qui n'a pas lieu dans deux cas : l'utilisateur enchaîne après `<L>E0` au lieu de
  `/clear` (`creation.md:142` le permet), ou il refuse la coupure proposée au-delà du seuil. Elle
  reste alors remplie et committée pendant toute la suite de la session. Si cette session s'arrête
  ensuite sans nouvelle coupure, la reprise suivante restitue comme actuelle une Passation écrite
  plusieurs Étapes plus tôt. C'est le défaut que R2 visait, sur un chemin plus étroit : rien ne dit
  de remettre la section au marqueur quand la coupure proposée n'est pas prise.
- **R10** — `SKILL.md:128` — La remise au marqueur à la reprise efface le bloc `**À savoir** :`.
  Ce bloc contient par construction ce que la session a appris et qu'aucun autre fichier ne dit.
  Si la session reprise s'arrête sans coupure, ce savoir disparaît du Suivi et ne survit que dans
  l'historique git. Le journal (R2) justifie la remise par la fraîcheur. Il ne dit pas où doit
  migrer un acquis qui vaut au-delà d'une session, par exemple vers `Notes` de `## État courant`.
  Choix assumé, mais sa contrepartie n'est pas écrite.
- **R11** — « Passation » porte une majuscule sans être un terme défini : `SKILL.md:128`
  (« La Passation restituée »), `creation.md:142` (« sa Passation »), `execution.md:105` (« à la
  Passation »). Aucun lexique ne le définit : le global ne le porte pas, et `.claude/LEXIQUE.md`
  n'existe pas. Or la règle du Lexique réserve la majuscule initiale au sens défini. Le lecteur
  croit alors à un terme défini qu'il ne trouve nulle part. Deux sorties sont possibles :
  l'utilisateur ajoute le terme au Lexique, ou les trois emplois passent à la minuscule ou à
  « la section `## Passation` ». Cet arbitrage revient à l'utilisateur.
- **R12** — Commande `ORACLE` du Plan (`.claude/plans/sleepy-coalescing-marshmallow.md`) : elle
  filtre les lignes du transcript sur la sous-chaîne `"usage"`, puis lit `["message"]`. Une ligne
  `type: attachment` qui contient ce mot la fait échouer (`KeyError: 'message'`, constaté sur ce
  transcript). La vérification de l'Étape 2 n'est donc pas rejouable telle quelle. Le livrable
  n'est pas touché : `contexte` concorde avec l'oracle corrigé. Mais ce Plan archivé portera une
  commande de contrôle cassée.

### Dette induite

- **R13** — `skills/implementation-tracker/scripts/contexte.py` mêle point d'entrée et logique, et
  E7 y ajoute un flux par exception (`except OSError` dans `main`, l. 96–100). C'est contraire à
  `rules/claude-python-style.md`, section « Structure » : point d'entrée sans logique, `Result[T]`
  entre couches. Le fichier suit en revanche son voisin `impl_list.py`, de même forme. Coût faible
  tant que le script garde deux usages. Il croîtra si un troisième s'y greffe.
- R7 et le reste de R8 : voir plus haut, à porter au registre à la Clôture.

### Bloquants

Aucun. Tous les critères de réussite sont atteints et vérifiés par exécution, le Hors-périmètre est
respecté et aucun Signal de dérive n'est matérialisé. Le verdict reste RÉSERVES pour trois raisons.
Le symptôme d'origine n'est vérifiable que sur les Chantiers à venir. R9 et R10 touchent le cycle
de vie de la Passation, cœur du mécanisme introduit. R11 demande un arbitrage de l'utilisateur sur
le Lexique.

## 2026-10-04 — clôture — `cd7f05b`

**Verdict** : RÉSERVES

Brief présent et lu ; Suivi, Plan et diff `master...contexte-tracker` lus (10 commits, `c13ccab` à
`cd7f05b`). Le Suivi élargit le Brief en quatre points datés (Q1, Q3, Q7, puis la Passation et son
commit dédié au second audit) : il fait foi, et le critère `rumdl` est jugé sous la forme
`uvx rumdl fmt --check`. Cet audit couvre le diff entier. E8 (`14b54ae`) et E9 (`cd7f05b`), qui
traitent R9 à R12, y sont lus en détail. Aucun fichier Python n'a changé depuis `b323e5a`. La
numérotation reprend à R14 pour ne pas croiser les R1 à R13 déjà posés.

### Vérifications exécutées

- `.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. », sortie 0 (59 renvois entre
  skills résolvent, 34 chemins de skill cités existent)
- `.venv/bin/python -m pytest skills/implementation-tracker scripts/tests` → 158 passés, 0 échec
- `uvx ruff check skills/implementation-tracker statusline-command.py` → `All checks passed!`
- `uvx ruff format --check skills/implementation-tracker statusline-command.py` → `7 files already
  formatted`
- `uvx --with pytest basedpyright skills/implementation-tracker statusline-command.py` → `0 errors,
  0 warnings, 0 notes`
- `uvx ruff check .` → 2 erreurs ; Base extraite par `git archive` → 5 : aucune régression
- `uvx rumdl fmt --check` sur la liste du Plan, plus `LEXIQUE.md`,
  `skills/git-smart-commit/references/etape.md`, le Plan, le Suivi et les trois fiches de dette
  touchées → sortie 0 partout
- `uvx rumdl check` (forme d'origine du Brief) sur `skills/implementation-tracker` →
  `contrat.md:214` MD028 et `patrons/review.md:1` MD041, **identiques sur la Base extraite**. Sur
  les documents du Chantier, seulement MD041 (front matter en tête) et MD013 (commandes de
  vérification d'une ligne)
- `contexte` → `222333` ; `ORACLE` du Plan, telle qu'écrite à E9 → `222333`, sortie 0 : écart 0
  (< 5 000), et la commande se rejoue
- `gabarit new suivi <scratchpad>/s.md` → `## Passation` / `<OPTIONNEL>`
- `gabarit check --filled .claude/implementation/done/2026-10-04-shadow-skill.md` → « rempli et
  conforme » ; `gabarit check --filled .claude/implementation/contexte-tracker.md` → conforme
- `git diff --no-index --word-diff` de `master:SKILL.md` l. 97–232 et 259–359 contre
  `references/creation.md` et `references/execution.md` à `HEAD` → titres « Phase » et leur niveau,
  liens relatifs, reformulation de R1 (E7), section `## Passation` et point 10 de la création
  (E6, réécrits à E8). Aucune autre règle touchée
- `grep -rn "Étape [0-6]" skills/implementation-tracker/SKILL.md` → vide ;
  `grep -rn "Étape [0-6]" skills/implementation-tracker` → vide
- `grep -rn "Étape [0-6]" skills shadow-skills OUTILLAGE.md agents scripts | grep -i "tracker\|suivi"`
  → seul `intent-brief/SKILL.md:206`, toléré au journal
- `grep -rln "Étape 2" .claude/implementation/todo/technical-debt` → vide
- `grep -rn "/clear" skills/implementation-tracker` → une ligne, `execution.md:119`, dans la
  procédure de Passation que la création appelle (journalisé)
- `list-dir validate .claude/implementation/todo/technical-debt` → 80 éléments conformes
- `lexique liste` → `Passation` présent, lien `execution.md#passation` ; l'ancre existe
  (`## Passation`)
- `git grep "les-trois-cas"` → aucun renvoi à l'ancien titre d'`etape.md`

### Réserves des audits antérieurs

- R9 : levée — la section ne s'écrit qu'après l'accord (`execution.md:112-119`), et la Passation a
  son commit propre. Un chemin plus étroit subsiste (R16).
- R10 : levée — plus de remise au marqueur. Une section ancienne reste dans le Suivi et la reprise
  la dit périmée (`SKILL.md:114-117`) : « À savoir » survit.
- R11 : levée — `Passation` est un terme du Lexique global, employé partout dans son sens défini.
  La trace de l'accord manque (R15).
- R12 : levée — l'`ORACLE` se rejoue, exécuté ci-dessus.
- R7, R13 et le reste de R8 (part statusline de `statusline-hors-des-linters` ; titres « Étape N »
  d'`intent-brief` et de `debt-review`) : ouverts, à porter au registre à la Clôture.

### Conformité à l'intention

- Critère « `SKILL.md` ne porte plus création ni exécution, renvoie vers deux références, garde
  vérifications, routage et reprise » : atteint. Les Phases 2 et 4 se réduisent à une consigne de
  lecture.
- Critère « déplacement à l'identique » : atteint. Le word-diff ne montre que titres et renvois
  sur le texte déplacé. S'y ajoutent les ajouts prévus et la reformulation de R1, journalisée.
- Critère « aucun `Étape [0-6]` dans `SKILL.md`, aucun renvoi aux anciens titres » : atteint.
- Critère « `/clear` après `<L>E0`, et au commit d'Étape seulement au-delà de 300k » :
  atteint. `creation.md:135` propose toujours la Passation après `<L>E0`. `execution.md:101-105`
  ne la propose au commit d'Étape qu'au-delà de 300 000 tokens. Aucune autre consigne ne
  suggère de coupure.
- Critère « la semence déclare `## Passation`, la procédure la réécrit avant le commit qui précède
  une coupure, la reprise la restitue » : atteint. Semence exécutée ; réécriture puis commit dédié
  avant `/clear` (`execution.md:114-119`) ; restitution si à jour (`SKILL.md:111-117`).
- Critère « l'agent lit la taille de son contexte par une commande, qui concorde avec le dernier
  `usage` » : atteint, écart 0 mesuré.
- Critère « linters et formateur passent sur les fichiers touchés » : atteint sous la forme du
  Suivi. Les constats de `rumdl check` sur le skill sont antérieurs au Chantier.
- Hors-périmètre : respecté. Le Suivi est toujours lu en entier, et aucun hook n'est ajouté.
  `intent-brief` ne change que sur ses deux renvois, et `agents/` est intact. `git-smart-commit` et
  `LEXIQUE.md` sont touchés au titre de l'élargissement daté et de l'Étape 8.
- Signaux de dérive : aucun matérialisé. Le déplacement est pur ; `statusline-command.py`
  n'a pas changé depuis l'audit précédent ; la Passation n'est proposée qu'aux deux moments
  convenus.
- Symptôme d'origine (Chantiers au-delà de 400k) : invérifiable en l'état. Il se constatera sur
  les Chantiers à venir. Le mécanisme est en place, et sa mesure est juste sur une session réelle.

### Qualité du code

- **R14** — `skills/git-smart-commit/SKILL.md:21` — la ligne de routage du type 2 énumère encore
  « état initial, session ou étape terminée », alors qu'`etape.md` porte désormais « Les quatre
  cas ». Le routage aboutit quand même au type 2 (« Un commit sur la branche d'un chantier »).
  Mais l'énumération est devenue fausse par omission, dans le fichier que l'agent lit en premier.
- **R15** — `LEXIQUE.md:27` — le terme `Passation` entre au Lexique global. La règle du Lexique
  exige l'accord explicite de l'utilisateur pour toute entrée. Le Suivi ne la trace pas :
  l'élargissement daté ne nomme que `git-smart-commit`, et aucune ligne du journal ne parle du
  terme. Seule la liste de fichiers de l'Étape 8 cite `LEXIQUE.md`. L'accord est donc invérifiable
  sur pièces : à confirmer par l'utilisateur, et à journaliser si c'est le cas.
- **R16** — `execution.md:112-119` avec `SKILL.md:114-117` — un dernier chemin rend une Passation
  périmée « à jour ». L'utilisateur accepte la Passation : section écrite et committée. Puis il
  décline le `/clear` du point 3 et continue dans la même session. La procédure le permet : elle
  propose `/clear` sans l'imposer. Si cette session s'arrête ensuite sans nouvelle Passation, la
  reprise trouve `**Écrite** : session N` et un frontmatter toujours à `N`. Elle restitue alors
  comme actuelle une section écrite plusieurs Étapes plus tôt, où « En cours » peut dire « rien ».
  Le bloc `**Écrite** :` porte bien `après <L>E<n>`, mais la règle de fraîcheur ne le compare pas au
  dernier tag d'Étape. Chemin étroit : accepter la Passation, c'est en général vouloir couper.

### Dette induite

Rien de nouveau. R7, R13 et le reste de R8 sont à porter au registre à la Clôture (voir plus haut).

### Bloquants

Aucun. Tous les critères de réussite sont atteints et vérifiés par exécution, le Hors-périmètre
est respecté, et aucun Signal de dérive n'est matérialisé. Le verdict reste RÉSERVES pour trois
raisons :

- le symptôme d'origine n'est vérifiable que sur les Chantiers à venir ;
- R15 demande une confirmation de l'utilisateur sur le Lexique global ;
- R14 et R16 sont des écarts mineurs du mécanisme introduit, à corriger ou à assumer avant
  l'aplatissement.

## 2026-10-04 — clôture — `50071c4`

**Verdict** : RÉSERVES

Brief présent et lu ; Suivi, Plan et diff `master...contexte-tracker` lus (11 commits, `c13ccab` à
`50071c4`). Le Suivi élargit le Brief en quatre points datés : il fait foi, et le critère `rumdl`
est jugé sous la forme `uvx rumdl fmt --check`. Cet audit couvre le diff entier. E10 (`50071c4`),
qui traite R14 et R16 et trace R15 au journal, y est lu en détail. Aucun fichier Python n'a changé
depuis `cd7f05b` (`git diff --stat cd7f05b HEAD -- '*.py' bin` vide). La numérotation reprend à
R17.

### Vérifications exécutées

- `.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. », sortie 0 (59 renvois entre
  skills résolvent, 34 chemins de skill cités existent)
- `.venv/bin/python -m pytest skills/implementation-tracker scripts/tests` → 158 passés, 0 échec
- `uvx ruff check skills/implementation-tracker statusline-command.py` → `All checks passed!`
- `uvx ruff format --check skills/implementation-tracker statusline-command.py` → `7 files already
  formatted`
- `uvx --with pytest basedpyright skills/implementation-tracker statusline-command.py` → `0 errors,
  0 warnings, 0 notes`
- `uvx ruff check .` → `Found 2 errors.` ; Base extraite par `git archive master` → `Found 5
  errors.` : aucune régression
- `uvx rumdl fmt --check` sur la liste du Plan, plus `LEXIQUE.md`, les deux fichiers de
  `git-smart-commit`, le Suivi, le Plan et les trois fiches de dette touchées → sortie 0. Les
  7 constats non corrigeables qu'il affiche sont ceux de `rumdl check` : MD041 et MD013 sur Suivi
  et Plan (front matter, commandes de vérification d'une ligne), `contrat.md:214` MD028 et
  `patrons/review.md:1` MD041, ces deux derniers identiques sur la Base
- `contexte` → `234066` ; `ORACLE` du Plan → `234066`, sortie 0 : écart 0 (< 5 000)
- `gabarit new suivi <scratchpad>/s.md` → `## Passation` / `<OPTIONNEL>`
- `gabarit check --filled .claude/implementation/done/2026-10-04-shadow-skill.md` → « rempli et
  conforme » ; `gabarit check --filled .claude/implementation/contexte-tracker.md` → « rempli et
  conforme »
- `git diff --no-index --word-diff` de `master:SKILL.md` l. 97–232 et 259–359 contre
  `references/creation.md` et `references/execution.md` → titres « Phase » et leur niveau, liens
  relatifs, reformulation de R1 (E7), point 10 de la création et section `## Passation` (E6, E8).
  Aucune autre règle touchée
- `grep -rn "Étape [0-6]" skills/implementation-tracker/SKILL.md` → vide ;
  `grep -rn "Étape [0-6]" skills/implementation-tracker` → vide
- `grep -rn "Étape [0-6]" skills shadow-skills OUTILLAGE.md agents scripts | grep -i "tracker\|suivi"`
  → seul `intent-brief/SKILL.md:206`, toléré au journal
- `grep -rln "Étape 2" .claude/implementation/todo/technical-debt` → vide
- `grep -rn "/clear" skills/implementation-tracker` → une ligne, `execution.md:119`, procédure de
  Passation que la création appelle (journalisé)
- `list-dir validate .claude/implementation/todo/technical-debt` → 80 éléments conformes
- `lexique liste` → `Passation`, lien `execution.md#passation`
- `git diff --stat master...contexte-tracker -- agents hooks settings.json` → vide
- `git status --short` → `?? .claude/implementation/contexte-tracker.audit.md` ;
  `git check-ignore` sur ce fichier → sortie 1, non ignoré (voir R17)

### Réserves des audits antérieurs

- R14 : levée — `git-smart-commit/SKILL.md:21` énumère « état initial, session, étape terminée ou
  Passation », comme les quatre cas d'`etape.md`.
- R15 : levée — le journal du Suivi trace l'accord, citation de l'utilisateur à l'appui.
- R16 : levée sur le chemin visé. Une session qui continue après sa Passation committe ou modifie
  l'arbre : la Passation n'est alors plus le dernier commit, ou l'arbre n'est plus propre, et la
  reprise la dit périmée (`SKILL.md:114-123`). Le correctif ouvre un faux négatif (R17).
- R7, R13 et le reste de R8 (part statusline de `statusline-hors-des-linters` ; titres « Étape N »
  d'`intent-brief` et de `debt-review`) : ouverts, à porter au registre à la Clôture.

### Conformité à l'intention

- Critère « `SKILL.md` ne porte plus création ni exécution, renvoie vers deux références, garde
  vérifications, routage et reprise » : atteint. Les Phases 2 et 4 se réduisent à une consigne de
  lecture.
- Critère « déplacement à l'identique » : atteint, word-diff exécuté ci-dessus.
- Critère « aucun `Étape [0-6]` dans `SKILL.md`, aucun renvoi aux anciens titres » : atteint.
- Critère « `/clear` après `<L>E0`, et au commit d'Étape seulement au-delà de 300k » : atteint
  (`creation.md` point 10, `execution.md:91-105`). Aucune autre consigne ne suggère de coupure.
- Critère « la semence déclare `## Passation`, la procédure la réécrit avant le commit qui précède
  une coupure, la reprise la restitue » : atteint sur le chemin nominal. La restitution manque à
  tort dans un Chantier qui a reçu un audit intermédiaire (R17).
- Critère « l'agent lit la taille de son contexte par une commande, qui concorde avec le dernier
  `usage` » : atteint, écart 0 mesuré.
- Critère « linters et formateur passent sur les fichiers touchés » : atteint sous la forme du
  Suivi.
- Hors-périmètre : respecté. Le Suivi est lu en entier, aucun hook n'est ajouté, `intent-brief`
  ne change que sur ses deux renvois, `agents/` est intact.
- Signaux de dérive : aucun matérialisé. Le déplacement est pur, `statusline-command.py` ne fait que
  mesurer et transmettre (plus les corrections `ruff` acceptées, Q1), et la Passation n'est proposée
  qu'aux deux moments convenus.
- Symptôme d'origine (Chantiers au-delà de 400k) : invérifiable en l'état. Il se constatera sur les
  Chantiers à venir. Le mécanisme est en place, et sa mesure est juste sur une session réelle.

### Qualité du code

- **R17** — `SKILL.md:114-115` — la condition « arbre propre » du correctif de R16 rend périmée une
  Passation fraîche dès qu'un audit a eu lieu. Le fichier `<slug>.audit.md` n'est committé qu'à
  l'aplatissement (`cloture.md`), et `audit.md` ne prévoit aucun commit au retour d'un audit
  intermédiaire. Le commit de Passation ne stage que le Suivi (`etape.md`, procédure point 2). Le
  rapport reste donc non suivi, et `git status --short` n'est jamais vide. Ce Chantier en est la
  preuve : après quatre audits, `git status --short` rend
  `?? .claude/implementation/contexte-tracker.audit.md`. L'audit intermédiaire est proposé au-delà
  de 400 lignes de diff, c'est-à-dire sur les gros Chantiers que vise le Brief. Toute Passation
  qui le suit sera dite périmée à la reprise, et « En cours » comme « À savoir » ne seront pas
  restitués comme actuels. `execution.md:107-108` (« après un commit d'Étape, l'arbre est
  propre ») repose sur la même prémisse. L'échec est fermé : la section reste dans le Suivi, lu en
  entier, et la reprise l'annonce avec son bloc `**Écrite** :`. Rien n'est perdu, mais le
  mécanisme se dégrade sur son cas d'usage principal.
- **R18** — `skills/gabarit/gabarit/suivi/contract.toml`, section `Passation` — la règle de
  fraîcheur y est définie sans la condition d'arbre propre (« à jour tant que son commit de
  Passation reste le dernier de la branche »), alors que `SKILL.md:114-115` exige les deux. Une même
  règle a donc deux définitions qui divergent. Un correctif de R17 devra les accorder, ou n'en
  garder qu'une et renvoyer à l'autre.

### Dette induite

Rien de nouveau. R7, R13 et le reste de R8 sont à porter au registre à la Clôture.

### Bloquants

Aucun. Tous les critères de réussite sont atteints et vérifiés par exécution, le Hors-périmètre
est respecté, et aucun Signal de dérive n'est matérialisé.

J'ai hésité avec DÉFAVORABLE à cause de R17, qui touche le critère « la reprise la restitue ». Je
le retiens en réserve pour trois raisons : le chemin nominal fonctionne, l'échec est fermé (la
Passation est annoncée périmée, jamais restituée à tort comme actuelle), et l'information reste
dans le Suivi lu en entier. Le verdict reste RÉSERVES pour deux raisons :

- le symptôme d'origine n'est vérifiable que sur les Chantiers à venir ;
- R17 et R18 sont à corriger ou à assumer avant l'aplatissement. R17 dégrade la Passation sur les
  Chantiers que le Brief vise.
