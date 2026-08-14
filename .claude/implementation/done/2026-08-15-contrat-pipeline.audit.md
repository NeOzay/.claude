---
slug: contrat-pipeline
---

## 2026-08-14 — clôture — `a8e3111`

**Verdict** : DÉFAVORABLE

### Vérifications exécutées

- `bash scripts/check-pipeline.sh` → **code 0**, cinq contrôles au vert (28 renvois résolvent,
  8 empreintes à une occurrence, 2 fichiers listés sans bruit, 2 agents non couplés, tous les
  champs `plan`/`brief`/`audit` résolvent).
- `grep -c '^## ' skills/implementation-tracker/references/contrat.md` → **7** (étape 1, conforme).
- `bash scripts/impl-list.sh .claude/implementation/done | grep -cE '\.(brief|audit|plan)\.md'`
  → **0** (étape 2, conforme).
- `grep -c 'contrat.md#' skills/implementation-tracker/SKILL.md` → **11** (≥ 5 attendu) ;
  `grep -c "grep -vE" …/SKILL.md` → **0** (étape 3, conforme).
- `grep -c 'contrat.md#' skills/intent-brief/SKILL.md` → **4** (≥ 3 attendu, étape 4, conforme).
- `grep -rc 'contrat.md#' skills/*/references/ | grep -v ':0'` → 7 fichiers porteurs
  (`squash.md`, `contrat.md`, `gabarit-suivi.md`, `audit.md`, `dette.md`, `cloture.md`,
  `gabarit-brief.md`) — étape 5, conforme.
- `grep -n 'check-pipeline' skills/implementation-tracker/references/cloture.md` → ligne 14,
  appel conditionnel (étape 7, conforme).
- `grep -l 'contrat' agents/*.md` → **2 fichiers** (`implementation-auditor.md`,
  `step-implementer.md`) — voir R1.
- **Tests d'efficacité du garde-fou**, joués sur une copie isolée du dépôt (aucune écriture dans
  l'arbre audité, `git` neutralisé par un faux binaire), une violation injectée puis retirée à
  chaque fois :
  - ancre falsifiée (`#frontmatteur`) → **exit 1**, `✗ ancre morte : #frontmatteur` ;
  - empreinte recopiée (« le suivi fait foi » ajoutée à `intent-brief/SKILL.md`) → **exit 1**,
    `✗ 2 fichiers — la règle a été recopiée hors du contrat` ;
  - section ajoutée au contrat sans renvoi → **exit 1**, `✗ section jamais citée` ;
  - renvoi `contrat.md#…` ajouté dans `agents/step-implementer.md` → **exit 1**, `✗ … renvoie au
    contrat` ;
  - champ `plan:` d'une archive pointé dans le vide → **exit 1**, `✗ pointe dans le vide` ;
  - `contrat.md` retiré → **exit 1**, `FATAL : contrat introuvable`.

  Les cinq contrôles détectent réellement ce qu'ils annoncent : le garde-fou n'est pas un script
  qui affiche vert sans rien examiner.
- `bash scripts/impl-list.sh .claude/implementation` depuis un répertoire **sans** `scripts/`
  → `bash: scripts/impl-list.sh: Aucun fichier ou dossier de ce nom`, **code 127**, sortie vide
  (voir R2).

### Conformité à l'intention

- **Critère « `bash scripts/check-pipeline.sh` sort en code 0 »** : **atteint, vérifié** — et
  vérifié aussi dans l'autre sens (le script échoue bien quand il doit échouer).
- **Critère « chaque règle du tableau n'a qu'un seul lieu de définition, les autres portent un
  renvoi ancré »** : **atteint, vérifié**. Les huit règles du tableau du plan sont dans
  `contrat.md`, et le diff montre partout une suppression de la copie suivie d'une ligne d'appel
  porteuse (arborescence dans `SKILL.md:28`, format d'étape en Étape 2.4, autorité en Étape 4,
  branche/commits en trois points, frontmatter dans les deux gabarits). Le contrôle 2 le rejoue
  mécaniquement sur 8 empreintes.
- **Critère « aucune ancre morte »** : **atteint, vérifié** — 28 renvois, tous résolvent, chemin
  relatif inclus. Réserve de portée en R4.
- **Critère « le filtre de listing filtre réellement »** : **atteint, vérifié** sur le répertoire
  réel `done/` (11 fichiers présents, 2 suivis remontés, aucun `.brief.md` / `.audit.md` /
  `.plan.md`). Le filtre est passé sur le **nom de fichier** (`find ! -name`), donc immunisé à la
  colonne de taille ajoutée par le hook `rtk` — la cause exacte de la dette d'origine.
- **Critère « `grep -l 'contrat' agents/*.md` → aucun résultat »** : **non atteint dans sa lettre**
  (R1), atteint dans son intention.
- **Critère « les quatre entrées de dette visées sont passées dans `technical-debt-solde.md` »** :
  **non atteint au SHA audité** (R3). `todo/technical-debt.md` porte toujours ses huit entrées et
  `technical-debt-solde.md` dit « Aucune entrée soldée à ce jour ». Le suivi et le plan le
  revendiquent : le solde relève du point 2 de `cloture.md`, **postérieur à l'audit**. Le critère
  est donc structurellement invérifiable à ce stade ; il reste à la charge de l'appelant.
- **Hors-périmètre** : **respecté**. `git-smart-commit` n'est touché que dans `squash.md`, sur
   5 lignes remplacées par un renvoi « Branche et commits » — c'est la clause « touché si une règle
  du noyau l'y oblige », pas un dégraissage. Les deux agents ne sont ni dédupliqués ni rendus
  dépendants du noyau ; l'unique modification (`implementation-auditor.md`, 2 lignes) est le solde
  de dette explicitement mis dans le périmètre par le brief. `skills/emmylua-ls/` et
  `skills/nvim-mini-test/` : intacts, absents du diff. La croissance du corpus (+853/-131) est
  admise par le brief.
- **Signal de dérive « la même instruction dupliquée dans tous les skills »** : **non
  matérialisé**, et c'est le point fort du chantier. Le diff est net : chaque ajout de renvoi est
  gagé sur une suppression de copie (`SKILL.md` : +37/-70, `intent-brief/SKILL.md` : +15/-20,
  `audit.md` : +5/-9). Le contrôle 2 rend la récidive détectable.
- **Symptôme d'origine** (« une règle définie en moyenne dans 3,6 fichiers ») : **traité** pour les
  huit règles inventoriées. Deux des dérives citées au brief sont corrigées dans l'arbre (champs de
  frontmatter réécrits, divergence auteur/appelant sur la racine du dépôt alignée) ; leur inscription
  au registre des soldes reste due (R3).

### Qualité du code

- **R1** — *critère faux dans sa lettre, non dans son intention.* `grep -l 'contrat' agents/*.md`
  remonte les deux agents, parce qu'ils contiennent l'expression « **contrats** en lecture »
  (`implementation-auditor.md:10`, `step-implementer.md:11`). Ces occurrences sont **antérieures au
  chantier** (`git grep -l 'contrat' master -- agents/` renvoie les deux mêmes fichiers) : le
  critère était inatteignable tel qu'écrit dès sa rédaction. La forme qui porte l'intention réelle
  est `grep -l 'contrat\.md' agents/*.md` → vide, c'est celle qu'implémente le contrôle 4 du script.
  Aucune correction de code n'est requise ; le critère du brief est à lire comme satisfait, et
  c'est le rapport qui doit en garder la trace.

- **R2** — *`bash scripts/impl-list.sh` est appelé sans garde dans un skill global.*
  `skills/implementation-tracker/SKILL.md:42` (Étape 0) et `:75` (Cas C) appellent le script par un
  chemin **relatif au répertoire courant**. Or `implementation-tracker` est un skill global de
  `~/.claude/skills`, invoqué depuis n'importe quel dépôt, et `scripts/impl-list.sh` n'existe que
  dans ce dépôt-ci. Vérifié : depuis un répertoire dépourvu de `scripts/`, la commande sort en
  **127** avec une sortie **vide**. Le mode de défaillance est celui-là même que le chantier
  redoutait ailleurs : une liste vide se lit « aucune implémentation en cours », et l'Étape 1
  enchaîne sur « proposer directement la création » — un second chantier ouvert sur un dépôt qui en
  a déjà un.

  Ce n'est pas une exigence que j'ajoute : le journal du suivi (2026-08-14) pose explicitement la
  contrainte — « le tracker sert dans d'autres dépôts, où `scripts/check-pipeline.sh` n'existe pas
  — un appel inconditionnel ferait échouer toutes leurs clôtures » — et y répond par un appel
  conditionnel dans `cloture.md:14`. Le même raisonnement n'a pas été appliqué au second script,
  celui qui est sur le chemin d'entrée de **toutes** les invocations du tracker. Avant le chantier,
  le `ls | grep` s'exécutait partout (filtre cassé, mais liste juste) ; après, l'Étape 0 ne
  fonctionne plus que dans ce dépôt.

  Correction attendue (une ligne, même patron que `cloture.md`) : appel conditionnel avec repli
  explicite, ou résolution du script relativement au dépôt qui l'héberge. Le contrat
  (`contrat.md:175-181`) devra porter la même nuance, puisqu'il y prescrit le script sans réserve.

- **R3** — *critère 6 non établi au SHA audité.* Voir « Conformité ». Le point est légitimement
  reporté à la clôture, mais il n'est couvert **par aucun contrôle** : ni le garde-fou ni l'audit ne
  peuvent constater qu'il a bien eu lieu. C'est le seul des six critères qui reposera sur la seule
  discipline de l'appelant. À vérifier après écriture du registre, par
  `grep -c '^## ' .claude/implementation/todo/technical-debt.md` (attendu : 8 − 4 = 4) et présence
  des quatre entrées, avec leur commande et sa sortie, dans `technical-debt-solde.md`.

- **R4** — *le contrôle 1 ne regarde que `skills/`.* `check-pipeline.sh:43,62` scanne `skills` et
  rien d'autre. Un renvoi `contrat.md#…` écrit un jour dans `CLAUDE.md`, `hooks/`, `README.md` ou un
  fichier de `.claude/` échapperait donc au contrôle d'ancre morte, en silence. Aucun n'existe
  aujourd'hui (vérifié), et l'exclusion volontaire d'`agents/` justifie de ne pas scanner le dépôt
  entier — mais le motif d'exclusion devrait être `agents/`, pas « tout sauf `skills/` ».

- **R5** — *la normalisation d'ancre du script est plus étroite que celle annoncée.* Le plan
  décrit « minuscules, espaces → tirets, ponctuation retirée, accents conservés » ;
  `slugify()` (`check-pipeline.sh:33`) ne retire que les apostrophes. Un futur titre de section
  contenant une virgule, des parenthèses ou un deux-points produirait une ancre calculée fausse — et,
  comme les deux côtés de la comparaison passent par la même fonction, l'écart ne se verrait
  **pas** dans le script : il apparaîtrait seulement en suivant le lien depuis nvim. Les sept
  titres actuels sont exempts de ponctuation ; le piège est en embuscade pour la huitième règle.

- **R6** — *le contrôle 2 compte des fichiers, pas des occurrences.* `grep -rl "$motif" | wc -l`
  (`check-pipeline.sh:94`) accepte donc deux copies d'une même règle **dans un seul fichier**. Cas
  marginal, mais la décision du journal parle d'« exactement une occurrence » : le code dit
  « exactement un fichier ». Écart entre l'intention écrite et l'implémentation.

- **R7** — *portabilité de `impl-list.sh`.* `find -printf` (`impl-list.sh:31`) est une extension
  GNU : sur BSD/macOS, la commande échoue. Le point est nul dans cet environnement (Linux) et n'est
  contredit par aucune contrainte du brief ; il n'est cité que parce que R2 place ce script sur le
  chemin d'entrée de tous les dépôts.

- **R8** — *style.* Le corpus enroule sa prose autour de 100 colonnes ; trois lignes ajoutées la
  dépassent nettement sans raison structurelle : `contrat.md:7` (121), `contrat.md:15` (131),
  `dette.md:122` (140). Les lignes longues restantes du diff sont des tableaux, des URL de renvoi ou
  des lignes d'étape, où l'usage du dépôt l'admet. Détail, mais le contrat est le fichier qui sera
  le plus relu.

### Dette induite

- **R9** — *le contrat est adossé à une table d'empreintes maintenue à la main.* Le journal
  l'assume (« toute règle ajoutée au contrat doit recevoir son empreinte, sinon elle n'est pas
  protégée »), et le contrôle « section jamais citée » couvre partiellement l'oubli — il détecte une
  section sans renvoi, pas une section sans empreinte. Coût futur : une règle ajoutée au contrat
  sans sa ligne dans `fingerprints` est invisible au garde-fou, et personne ne s'en apercevra. Une
  vérification « autant d'empreintes que de sections » serait mécanique et fermerait le trou.

- **R10** — *le contrat crée un couplage `git-smart-commit` → `implementation-tracker`.*
  `squash.md` renvoie désormais vers `../../implementation-tracker/references/contrat.md`. C'est
  assumé et conforme à la décision d'emplacement, mais c'est un couplage nouveau : `git-smart-commit`
  n'est plus lisible seul si le tracker est déplacé ou renommé. Le contrôle 1 le rendra visible
  (chemin mort), ce qui est le bon niveau de garantie — noté pour mémoire, pas à corriger.

- **R11** — *auto-citation du contrat.* `contrat.md:15` contient un exemple de renvoi
  `[Contrat des sous-agents](contrat.md#contrat-des-sous-agents)`, qui compte comme une citation
  aux yeux du contrôle « section jamais citée » (`check-pipeline.sh:72`). Une section qui ne serait
  citée que par cet exemple passerait le contrôle sans être réellement appelée. Sans effet
  aujourd'hui (la section est citée par `audit.md` et `SKILL.md`).

### Bloquants

- **R2** — l'Étape 0 et le Cas C d'`implementation-tracker` sont inopérants dans tout dépôt autre
  que celui-ci, avec un mode de défaillance silencieux (liste vide lue comme « aucun chantier »).
  Régression introduite par le chantier, contraire à la contrainte que le suivi lui-même a posée
  et satisfaite pour l'autre script.

*Note de verdict* — le choix `DÉFAVORABLE` plutôt que `RÉSERVES` tient au seul R2 : les six
critères sont servis, le hors-périmètre tenu, aucun signal de dérive matérialisé, et le dispositif
est de bonne facture. Mais un orchestrateur global dont la première commande échoue partout sauf
chez lui n'est pas livrable en l'état, et le correctif est d'une ligne, sur le patron déjà écrit à
`cloture.md:14`. R3 seul n'aurait pas justifié ce verdict — il se lève par l'écriture du registre
que la clôture prévoit.

## 2026-08-14 — clôture — `801c9a8`

**Verdict** : RÉSERVES

Second audit de clôture, sur le diff complet `master...801c9a8`. Le précédent (`a8e3111`,
DÉFAVORABLE) bloquait sur `R2` ; la numérotation reprend à `R12` pour que les renvois à `R1`–`R11`
gardent leur sens.

### Vérifications exécutées

- `git status --short` → arbre propre, `git rev-parse HEAD` → `801c9a8…` : l'arbre audité est bien
  le SHA annoncé.
- `bash scripts/check-pipeline.sh` → **code 0**, **six** contrôles au vert (28 renvois résolvent,
  8 empreintes à une occurrence, 2 fichiers listés sans bruit, 2 agents non couplés, tous les champs
  `plan`/`brief`/`audit` résolvent, 21 fichiers sans appel de script relatif non gardé).
- **`R2` rejoué** — depuis `/tmp/tmp.5aFVKyqZxp`, répertoire hors du dépôt contenant un
  `.claude/implementation/` factice (un suivi + un `.brief.md`) :
  `bash "$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh" .claude/implementation`
  → sortie `contrat-pipeline.md`, **code 0**, le `.brief.md` filtré. Le mode de défaillance
  bloquant (127 + sortie vide lue comme « aucun chantier ») **ne se reproduit plus**.
- `readlink -f /home/Benoit` → `/var/home/Benoit` : `$HOME/.claude` et la racine du dépôt sont le
  même arbre, le chemin absolu résout ici.
- **Efficacité du contrôle 6**, sur une copie isolée du dépôt (`git` neutralisé par un faux binaire,
  aucune écriture dans l'arbre audité), une violation injectée puis retirée à chaque fois :
  - `bash scripts/foo.sh` nu dans `dette.md` → **exit 1**, `✗ appel relatif non gardé : …` ;
  - `bash ./scripts/foo.sh` → **passe au vert** (voir R12) ;
  - `bash skills/implementation-tracker/scripts/impl-list.sh …` (chemin relatif au dépôt) →
    **passe au vert** (voir R12) ;
  - `[ -f autre.txt ] && bash scripts/foo.sh` → **passe au vert** (voir R12) ;
  - retour à l'état d'origine → vert, la copie était bien revenue à l'identique.
- Étapes du suivi, une par une :
  - étape 1 : `grep -c '^## ' …/contrat.md` → **7** (attendu 7) ;
  - étape 2 : `bash scripts/impl-list.sh …` → **NON EXÉCUTÉE telle qu'écrite** : code **127**, le
    script n'est plus à ce chemin depuis l'étape 9 (voir R14). Rejouée au chemin réel
    (`$HOME/.claude/skills/…/impl-list.sh .claude/implementation/done | grep -cE '\.(brief|audit|plan)\.md'`)
    → **0**, conforme ;
  - étape 3 : `grep -c 'contrat.md#' …/implementation-tracker/SKILL.md` → **11** (≥ 5) ;
  - étape 4 : `grep -c 'contrat.md#' skills/intent-brief/SKILL.md` → **4** (≥ 3) ;
  - étape 5 : `grep -rc 'contrat.md#' skills/*/references/ | grep -v ':0'` → **7 fichiers** porteurs ;
  - étape 6 : `bash scripts/check-pipeline.sh; echo $?` → **0** ;
  - étape 7 : `grep -n 'check-pipeline' …/cloture.md` → ligne 14, appel **gardé** par `[ -f … ]` ;
  - étape 9 : voir « `R2` rejoué » ci-dessus → **code 0**.
- `grep -l 'contrat' agents/*.md` → **2 fichiers** (inchangé, cf. R1) ;
  `grep -l 'contrat\.md' agents/*.md` → **vide**, code 1.
- `grep -c '^## ' .claude/implementation/todo/technical-debt.md` → **8** ;
  `technical-debt-solde.md` → « *Aucune entrée soldée à ce jour.* » (voir R13).
- `git diff --numstat master...801c9a8` → `skills/emmylua-ls/` et `skills/nvim-mini-test/` absents du
  diff ; `git-smart-commit` touché sur le seul `squash.md` (+5/-3).
- `grep -rn "grep -vE" --include='*.md' skills` → **3 occurrences**, toutes illustratives (gabarit de
  dette, note de mode de défaillance) : aucun filtre de listing réécrit en ligne ne subsiste.
- `HOME=/nonexistent-home bash -c 'bash "$HOME/.claude/skills/…/impl-list.sh" .claude/implementation'`
  → **code 127**, stdout vide (voir R15).

### Conformité à l'intention

- **Critère « `bash scripts/check-pipeline.sh` sort en code 0 »** : **atteint, vérifié** — et dans
  l'autre sens pour le contrôle 6, ajouté depuis le dernier audit : il échoue bien sur la forme
  exacte de la régression qu'il vise.
- **Critère « chaque règle du tableau n'a qu'un seul lieu de définition, les autres portent un renvoi
  ancré »** : **atteint, vérifié**. Inchangé depuis `a8e3111` ; les 8 empreintes sont à une
  occurrence, les 7 sections du contrat sont toutes citées, 9 fichiers portent des renvois ancrés.
- **Critère « aucune ancre morte »** : **atteint, vérifié** — 28 renvois, tous résolvent. Réserve de
  portée : R4 (audit précédent), toujours ouverte.
- **Critère « le filtre de listing filtre réellement »** : **atteint, vérifié**, et désormais aussi
  **hors du dépôt** — c'était le manque bloquant du précédent audit.
- **Critère « `grep -l 'contrat' agents/*.md` → aucun résultat »** : **non atteint dans sa lettre,
  atteint dans son intention** — R1 de l'audit précédent, inchangé et sans correction requise : les
  deux occurrences (« contrats en lecture ») sont antérieures au chantier.
- **Critère « les quatre entrées de dette visées sont passées dans `technical-debt-solde.md` »** :
  **non atteint au SHA audité**, et il ne peut pas l'être — voir R13.
- **Hors-périmètre** : **respecté**, constat identique au précédent audit et revérifié sur le diff
  complet. Le correctif `R2` n'a touché que `SKILL.md` (2 lignes), `contrat.md` (+10/-1),
  `check-pipeline.sh` et le déplacement du script : aucun débordement.
- **Signaux de dérive** : **aucun matérialisé**. Le correctif n'a réintroduit aucune copie de règle —
  au contraire, il a supprimé le dernier point d'édition dupliquable en déplaçant le script plutôt
  qu'en posant un filtre de repli en ligne, ce que le journal du suivi motive explicitement.
- **Symptôme d'origine** (« une règle définie en moyenne dans 3,6 fichiers ») : **traité** pour les
  huit règles inventoriées, et désormais protégé par un garde-fou qui tient debout dans les deux
  sens. Le solde du registre reste dû (R13).

### Qualité du code

- **R12** — *le contrôle 6 ne reconnaît qu'une seule forme d'appel fautif.*
  `check-pipeline.sh:184` cherche la chaîne littérale `bash scripts/` et écarte toute ligne
  contenant `[ -f `. Trois variantes proches sont passées au vert dans mes injections :
  `bash ./scripts/foo.sh` ; `bash skills/implementation-tracker/scripts/impl-list.sh …` ;
  `[ -f autre.txt ] && bash scripts/foo.sh` (le garde porte sur un autre fichier).
  La deuxième est la plus gênante : maintenant que le script vit dans la skill, la régression la
  plus probable est précisément un auteur qui écrit son chemin **relatif au dépôt** au lieu de
  `$HOME/…` — et c'est le cas que le contrôle ne voit pas. Le contrôle reste utile (il attrape la
  forme exacte qui a bloqué la clôture) mais il protège moins large que son titre « Portabilité des
  appels de script » ne le laisse croire.

- **R13** — *critère 6 structurellement invérifiable à l'audit* (reprise de R3, toujours ouvert).
  `todo/technical-debt.md` porte ses **8** entrées et `technical-debt-solde.md` reste vide. Le
  solde relève du point 2 de `cloture.md`, **postérieur** au point 1 (audit) : aucun audit ne peut
  le constater, et aucun contrôle du garde-fou ne le couvre. Le critère reste entièrement à la
  charge de l'appelant. À vérifier après écriture :
  `grep -c '^## ' .claude/implementation/todo/technical-debt.md` → attendu **4**, et présence des
  quatre entrées dans `technical-debt-solde.md` avec leur commande et sa sortie réelle.

- **R14** — *la vérification de l'étape 2 du suivi ne s'exécute plus.* Elle est écrite
  `bash scripts/impl-list.sh …` alors que l'étape 9 a déplacé le script ; rejouée telle quelle, elle
  sort en **127**. L'étape 2 reste cochée à juste titre — son intention est servie, je l'ai
  revérifiée au chemin réel — mais un suivi archivé dont une commande de vérification est morte perd
  sa valeur de preuve rejouable, qui est toute la raison d'être du champ `vérif:`. Pas un défaut de
  code ; un défaut de traçabilité dans le contrat de suivi, à corriger avant archivage.

- **R15** — *le chemin absolu suppose une installation en `~/.claude`.*
  `SKILL.md:42`, `:75`, `contrat.md:178` et `check-pipeline.sh:28` codent en dur
  `$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh`. Si la skill est chargée depuis
  un autre emplacement (skill de projet dans `<dépôt>/.claude/skills/`, `CLAUDE_CONFIG_DIR`
  personnalisé, installation par plugin), l'appel retombe **exactement** dans le mode de défaillance
  de R2 : code 127, stdout vide, lu par l'Étape 1 comme « aucune implémentation en cours »
  (reproduit avec `HOME=/nonexistent-home`). Le risque est bien plus étroit qu'avant le correctif —
  il faut désormais une installation non standard, là où le défaut d'origine frappait *tout* autre
  dépôt — et aucune contrainte du brief n'exige davantage. Mais le contrat pose la règle « chemin
  absolu ancré dans la skill » (`contrat.md:183`) sans dire ce qu'on fait quand ce chemin n'existe
  pas, et le garde-fou ne le contrôle pas.

- **R16** — *le garde-fou contrôle la skill installée, pas celle de l'arbre audité.*
  `check-pipeline.sh:28` fait pointer `LISTER` vers `$HOME/.claude/…`, tandis que le script commence
  par `cd "$(git rev-parse --show-toplevel)"`. Ici les deux coïncident (le dépôt **est** `~/.claude`,
  vérifié) et le contrôle 3 teste donc bien le fichier de la branche. Sur une copie de travail du
  dépôt — un clone, un worktree, l'arbre isolé que j'ai utilisé pour mes injections — le contrôle 3
  validerait la version *installée* pendant que le contrôle 1 examine la version *locale* : vert sur
  un arbre cassé. Conséquence pratique immédiate : mes tests d'injection sur copie ne prouvent rien
  du contrôle 3, et un futur auditeur doit le savoir.

- **R17** — *style, reprise de R8, non traité.* Trois lignes de prose ajoutées dépassent nettement
  l'enroulement à 100 colonnes du corpus : `contrat.md:7` (121), `contrat.md:15` (131),
  `dette.md:122` (140). Le correctif `R2` n'en a ajouté aucune nouvelle — les lignes qu'il introduit
  dans `contrat.md:183-190` respectent la largeur.

- **R18** — *commentaire d'en-tête devenu relatif à rien.* `impl-list.sh:6` renvoie à
  `skills/implementation-tracker/references/contrat.md`, un chemin relatif à la racine du dépôt,
  alors que le fichier vit désormais dans `skills/implementation-tracker/scripts/`. Depuis
  l'emplacement du script, la cible est `../references/contrat.md`. Sans effet fonctionnel
  (commentaire), mais c'est un chemin qui ne se suit pas depuis l'éditeur — la contrainte même que
  le brief posait sur les renvois.

- Constats **R5** (normalisation d'ancre plus étroite que le plan), **R6** (le contrôle 2 compte des
  fichiers, pas des occurrences) et **R4** (le contrôle 1 ne scanne que `skills/`) de l'audit
  précédent : **inchangés**, vérifiés dans le code au SHA courant (`check-pipeline.sh:34`, `:95`,
  `:44`). Toujours des réserves, aucune n'est bloquante.

### Dette induite

- **R9** (table d'empreintes maintenue à la main), **R10** (couplage `git-smart-commit` →
  `implementation-tracker`) et **R11** (auto-citation du contrat en `contrat.md:15`, qui satisfait à
  elle seule le contrôle « section jamais citée ») de l'audit précédent : **inchangés**, toujours
  ouverts, toujours non bloquants.

- **R19** — *le chemin absolu de la skill est répété en quatre points d'édition.* `SKILL.md:42`,
  `SKILL.md:75`, `contrat.md:178`, `check-pipeline.sh:28`. Ce sont des lignes d'**appel**, pas des
  définitions de règle — la doctrine du chantier les autorise, et le contrôle 6 en surveille une
  partie. Mais un renommage de la skill ou un changement d'emplacement demande quatre éditions
  coordonnées, dont aucune n'échoue bruyamment si elle est oubliée (R15 : 127 sur stderr, stdout
  vide). Coût futur borné, noté pour mémoire.

### Bloquants

Aucun. `R2`, seul bloquant du précédent audit, est levé et vérifié hors du dépôt.

*Note de verdict* — `RÉSERVES` et non `FAVORABLE` pour deux raisons distinctes. D'abord R13 : le
sixième critère de réussite n'est pas atteint au SHA audité et ne peut pas l'être par construction —
un critère non constaté ne se déclare pas atteint, même quand la procédure prévoit qu'il le sera au
point suivant. Ensuite R12 et R15 : le garde-fou ajouté pour empêcher la récidive de `R2` couvre une
forme d'appel sur quatre, et le correctif conserve une variante étroite du mode de défaillance
d'origine. Rien de tout cela n'interdit de clore — le dispositif fonctionne, les cinq autres
critères sont servis et revérifiés, le hors-périmètre est tenu et aucun signal de dérive ne s'est
matérialisé — mais l'utilisateur doit trancher en le sachant.

## 2026-08-14 — clôture — `0c5a8fe`

**Verdict** : RÉSERVES

Troisième audit de clôture, sur le diff complet `master...0c5a8fe`. Le précédent (`801c9a8`,
RÉSERVES) laissait `R12`, `R14` et `R16` à traiter — l'étape 10 les vise. La numérotation reprend à
`R20` pour que les renvois à `R1`–`R19` gardent leur sens.

### Vérifications exécutées

- `git rev-parse HEAD` → `0c5a8fec…` : l'arbre audité est bien le SHA annoncé. `git status --short`
  → une seule modification non commitée, `.claude/implementation/contrat-pipeline.audit.md` (la
  section `801c9a8` de ce rapport, écrite après le commit — normal, pas un défaut).
- `bash scripts/check-pipeline.sh` → **code 0**, **six** contrôles au vert (28 renvois résolvent,
  8 empreintes à une occurrence, 2 fichiers listés sans bruit, 2 agents non couplés, tous les champs
  `plan`/`brief`/`audit` résolvent, 21 fichiers sans appel de script relatif non gardé).
- **`R12` rejoué — les quatre formes fautives, injectées une à une** sur une copie isolée du dépôt
  (`git` neutralisé par un faux binaire, aucune écriture dans l'arbre audité, retour à l'identique
  après chaque injection) :
  - `bash scripts/foo.sh` → **exit 1**, `✗ appel relatif non gardé : … → scripts/foo.sh` ;
  - `bash ./scripts/foo.sh` → **exit 1** (passait au vert en `801c9a8`) ;
  - `bash skills/implementation-tracker/scripts/impl-list.sh …` → **exit 1** (passait au vert) ;
  - `[ -f autre.txt ] && bash scripts/foo.sh` → **exit 1** (passait au vert) ;
  - forme légitime `bash "$HOME/.claude/skills/…/impl-list.sh" …` → **exit 0**, pas de faux positif ;
  - retour à l'état d'origine → vert. **`R12` est levé** : les quatre formes sont couvertes.
- **`R16` rejoué** — sur la même copie isolée, `impl-list.sh` **local** cassé (filtre `.brief.md`
  retiré) : le contrôle 3 sort en **exit 1**, `✗ 6 fichiers parasites remontés par le listing`, alors
  que la skill installée sous `$HOME` restait saine. Le garde-fou juge désormais l'arbre audité et
  non l'installation. **`R16` est levé.**
- **Efficacité des cinq autres contrôles revérifiée après la réécriture du contrôle 6**, même
  protocole d'injection : ancre falsifiée → `✗ ancre morte : #ancre-bidon` ; empreinte « le suivi
  fait foi » recopiée dans `intent-brief/SKILL.md` → `✗ 2 fichiers — la règle a été recopiée` ;
  `contrat.md` cité dans `agents/step-implementer.md` → `✗ … renvoie au contrat` ; champ `plan:`
  d'une archive pointé dans le vide → `✗ pointe dans le vide`. Aucune régression collatérale.
- Étapes du suivi, une par une :
  - étape 1 : `grep -c '^## ' …/contrat.md` → **7** (attendu 7) ;
  - étape 2 : `bash "$HOME/.claude/skills/…/impl-list.sh" .claude/implementation/done | grep -cE
    '\.(brief|audit|plan)\.md'` → **0** — la vérif est désormais écrite au chemin réel et
    **s'exécute** : **`R14` est levé** ;
  - étape 3 : `grep -c 'contrat.md#' …/implementation-tracker/SKILL.md` → **11** (≥ 5) ;
  - étape 4 : `grep -c 'contrat.md#' skills/intent-brief/SKILL.md` → **4** (≥ 3) ;
  - étape 5 : `grep -rc 'contrat.md#' skills/*/references/ | grep -v ':0'` → **7 fichiers** ;
  - étape 6 : `bash scripts/check-pipeline.sh; echo $?` → **0** ;
  - étape 7 : `grep -n 'check-pipeline' …/cloture.md` → ligne 14, appel **gardé** par `[ -f … ]` ;
  - étape 9 : depuis `…/scratchpad/outside`, hors du dépôt, avec un `.claude/implementation/` factice
    (un suivi, un `.brief.md`, un `.audit.md`) → sortie `foo.md`, **code 0**, parasites filtrés ;
  - étape 10 : voir « `R12` rejoué » et « `R16` rejoué » ci-dessus.
- `grep -l 'contrat' agents/*.md` → **2 fichiers** (inchangé, cf. `R1`) ;
  `grep -l 'contrat\.md' agents/*.md` → **vide**, code 1.
- `grep -c '^## ' .claude/implementation/todo/technical-debt.md` → **8** ;
  `todo/` ne contient que `README.md`, `technical-debt.md`, `technical-debt-solde.md` (voir `R13`).
- `git diff --numstat master...0c5a8fe` → `skills/emmylua-ls/` et `skills/nvim-mini-test/` absents du
  diff ; `git-smart-commit` touché sur le seul `squash.md` (+5/-3).
- `awk 'length>100'` sur `contrat.md` et `dette.md` → 5 lignes, dont 1 tableau et 1 à 101 colonnes
  (voir `R17`).
- **Tests de faux positifs sur le contrôle 6** (nouveaux, même copie isolée) :
  `bash ~/.claude/skills/…/impl-list.sh` → **exit 1** ;
  `bash "${HOME}/.claude/skills/…/impl-list.sh"` → **exit 1** ;
  `bash "$CLAUDE_DIR/scripts/impl-list.sh"` → **exit 1** ;
  `bash scripts/foo.sh   # [ -f scripts/foo.sh ]` → **exit 0** (voir `R21`).

### Conformité à l'intention

- **Critère « `bash scripts/check-pipeline.sh` sort en code 0 »** : **atteint, vérifié**, et vérifié
  dans l'autre sens pour les six contrôles — chacun échoue sur ce qu'il annonce. C'est la première
  fois que le contrôle 6 tient dans les deux sens sur ses quatre formes.
- **Critère « chaque règle du tableau n'a qu'un seul lieu de définition, les autres portent un renvoi
  ancré »** : **atteint, vérifié**. Inchangé depuis `801c9a8` : 8 empreintes à une occurrence,
  7 sections toutes citées, 28 renvois qui résolvent, 7 fichiers de `references/` porteurs.
- **Critère « aucune ancre morte »** : **atteint, vérifié**. Réserve de portée `R4` toujours ouverte
  (revérifiée : aucun renvoi ancré réel n'existe hors de `skills/`, seulement des citations en prose
  dans le brief et ce rapport).
- **Critère « le filtre de listing filtre réellement »** : **atteint, vérifié**, dans le dépôt et
  hors du dépôt.
- **Critère « `grep -l 'contrat' agents/*.md` → aucun résultat »** : **non atteint dans sa lettre,
  atteint dans son intention** — `R1`, inchangé et sans correction requise : les deux occurrences
  (« contrats en lecture ») sont antérieures au chantier.
- **Critère « les quatre entrées de dette visées sont passées dans `technical-debt-solde.md` »** :
  **non atteint au SHA audité**, et structurellement inatteignable à l'audit — `R13`, inchangé.
- **Hors-périmètre** : **respecté**, revérifié sur le diff complet. L'étape 10 n'a touché que
  `check-pipeline.sh` (+24/-6), `contrat.md` (+2/-1) et le suivi. `git-smart-commit` reste au seul
  `squash.md` ; `emmylua-ls` et `nvim-mini-test` absents du diff ; les agents non couplés au noyau.
- **Signaux de dérive** : **aucun matérialisé**. L'étape 10 n'ajoute aucune règle ni aucune copie —
  elle durcit un contrôle et précise une phrase du contrat.
- **Symptôme d'origine** : **traité** pour les huit règles inventoriées, et le garde-fou qui les
  protège est maintenant éprouvé sur les quatre formes de la régression la plus probable. Le solde du
  registre reste dû (`R13`).

### Qualité du code

- **`R12`, `R14`, `R16` : levés**, chacun rejoué ci-dessus par la commande qui l'avait établi. Le
  correctif du contrôle 6 est bien fait : il extrait le chemin appelé de la ligne (`grep -o`), écarte
  les seuls chemins absolus, et exige que le garde `[ -f … ]` porte **sur ce même chemin** — c'est
  exactement ce que le journal du suivi motive.

- **R20** — *neuf réserves des audits précédents ne sont ni traitées, ni inscrites nulle part.*
  L'« État courant » du suivi ne nomme que `R13` (structurel) et `R15` (assumé) comme partant au
  registre de dette. Restent ouvertes et silencieuses : `R4` (contrôle 1 limité à `skills/`),
  `R5` (`slugify` ne retire que les apostrophes — `check-pipeline.sh:37`), `R6` (le contrôle 2 compte
  des fichiers, pas des occurrences — `:98`), `R9` (table d'empreintes maintenue à la main),
  `R11` (auto-citation `contrat.md:15` qui satisfait à elle seule « section jamais citée »),
  `R17` (trois lignes de prose au-delà de 100 colonnes : `contrat.md:7` (121), `:15` (131),
  `dette.md:122` (140)), `R18` (`impl-list.sh:6` renvoie à un chemin relatif à la racine du dépôt
  alors que le fichier vit dans `scripts/` — la cible est `../references/contrat.md`), `R19` (chemin
  absolu de la skill répété en trois points d'édition ; `check-pipeline.sh:31` n'en fait plus partie
  depuis `R16`), `R10` (couplage assumé). Aucune n'est bloquante et aucune ne l'a jamais été — mais
  une réserve qu'on ne traite ni n'inscrit disparaît à la clôture, et c'est précisément le mécanisme
  de dérive que ce chantier combat. Décision à prendre explicitement à la clôture, réserve par
  réserve : traitée, inscrite au registre, ou écartée motivée.

- **R21** — *le contrôle 6 refuse deux écritures absolues légitimes.* `check-pipeline.sh:194-196`
  n'accepte que `/…` et la chaîne littérale `$HOME/…`. Vérifié par injection :
  `bash ~/.claude/skills/…/impl-list.sh` et `bash "${HOME}/.claude/skills/…/impl-list.sh"` sortent
  tous deux en **exit 1**, alors qu'ils sont fonctionnellement identiques à la forme prescrite par le
  contrat. Le journal du suivi pose lui-même l'enjeu — « un contrôle qui produit des faux positifs se
  fait désactiver, ce qui tue le garde-fou entier » — et c'est le sens inverse de la même exigence :
  l'auteur qui écrit `~/` verra un rouge injustifié. Deux motifs de plus dans le `case` suffiraient.
  Sans effet aujourd'hui (les trois appels du dépôt utilisent `$HOME/`).

- **R22** — *le garde du contrôle 6 se satisfait d'une mention textuelle sur la ligne.* Le test est
  `printf '%s\n' "$line" | grep -q "\[ -f \"\?$call"` (`:197`) : il cherche la chaîne n'importe où
  dans la ligne, sans exiger qu'elle précède l'appel ni qu'elle le commande. Vérifié :
  `bash scripts/foo.sh   # [ -f scripts/foo.sh ]` passe au vert alors que l'appel est nu. De plus,
  `$call` est injecté tel quel dans un motif `grep` de base : les `.` du chemin y sont des
  métacaractères. Cas de contournement improbable en pratique — il faut écrire le garde en
  commentaire — mais le contrôle valide une forme, pas une garde effective.

- **R15** — *inchangé, non traité, assumé par le suivi.* Les trois appels (`SKILL.md:42`, `:75`,
  `contrat.md:178`) codent en dur `$HOME/.claude/skills/…`. Une installation hors `~/.claude` retombe
  dans le mode de défaillance de `R2` (127, stdout vide). Le suivi l'annonce au registre de dette :
  c'est le bon traitement, il reste à l'écrire.

- **R13** — *inchangé.* `todo/technical-debt.md` porte ses **8** entrées, `technical-debt-solde.md`
  reste vide. Le solde relève du point 2 de `cloture.md`, postérieur à l'audit : aucun audit ne peut
  le constater. À vérifier après écriture : `grep -c '^## ' …/todo/technical-debt.md` → attendu **4**,
  et les quatre entrées dans `technical-debt-solde.md` avec leur commande et sa sortie réelle.

### Dette induite

- **R9**, **R10**, **R11**, **R19** de l'audit `801c9a8` : **inchangés**, toujours ouverts, toujours
  non bloquants. `R19` est allégé d'un point d'édition (`check-pipeline.sh:31` vise désormais la copie
  du dépôt), il en reste trois.

- Aucune dette **nouvelle** introduite par l'étape 10. Le contrôle 6 gagne 24 lignes de shell dont la
  logique d'extraction est un cran plus subtile que le `grep | grep -v` qu'elle remplace : c'est le
  prix payé pour couvrir les quatre formes, et le commentaire de `:184-188` l'explicite. Acceptable.

### Bloquants

Aucun.

*Note de verdict* — `RÉSERVES` et non `FAVORABLE`, pour les mêmes deux raisons de fond qu'en
`801c9a8`, plus une nouvelle. `R13` d'abord : le sixième critère de réussite n'est pas atteint au SHA
audité et ne peut pas l'être par construction ; un critère non constaté ne se déclare pas atteint.
`R20` ensuite : neuf réserves antérieures ne sont ni traitées ni inscrites, et le chantier dont le
sujet est la dérive ne devrait pas clore en laissant des constats s'évaporer. `R21` et `R22` enfin,
mineurs, sur le durcissement du contrôle 6 lui-même. Ce qui était bloquant est levé et vérifié :
`R12` sur ses quatre formes, `R14` par exécution, `R16` par injection sur copie. Le dispositif est
solide et éprouvé dans les deux sens ; l'utilisateur peut clore en sachant ce qu'il reporte.
