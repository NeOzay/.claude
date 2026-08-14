---
slug: audit-integre
---

## 2026-08-14 — clôture — `fe80476`

**Verdict** : RÉSERVES

> Note de portée : ce chantier construit le dispositif d'audit, et c'est ce dispositif qui rend le
> présent avis. L'indépendance de jugement est réelle (contexte isolé, aucun droit d'écriture sur le
> code), mais l'auditeur ne peut pas juger avec recul le prompt qui le constitue. C'est une limite
> structurelle du « rodage sur soi-même » voulu par l'étape 7, pas un défaut du travail.

### Vérifications exécutées

Toutes les commandes de vérification des étapes 1 à 6 du suivi, plus les contrôles de bout en bout
du plan (`linked-toasting-graham.md`, section « Vérification ») :

- `ls skills/ | grep -c git-pre-commit-audit` → `0` — conforme (attendu 0)
- `ls archive/git-pre-commit-audit/SKILL.md` → présent (5.2K) — contenu préservé, conforme
- `head -6 agents/implementation-auditor.md` → frontmatter complet, `model: opus`,
  `tools: Read, Grep, Glob, Bash, Write` — pas d'`Edit`, conforme à l'étape 2
- `grep -c "400\|DÉFAVORABLE\|étapes restantes" skills/implementation-tracker/references/audit.md`
  → `5` (attendu > 0)
- `grep -n "audit\.md\|\.audit\.md" skills/implementation-tracker/SKILL.md` → 6 occurrences
  (lignes 32, 36, 50, 78, 234, 338) — bloc « Emplacement », deux exclusions de listing, ligne du
  tableau des déclencheurs, Étape 5
- `grep -c "audit" skills/implementation-tracker/references/cloture.md` → `6`
- `grep -n "audit:" skills/implementation-tracker/references/gabarit-suivi.md` → ligne 29,
  `audit: .claude/implementation/auth-refactor.audit.md`
- `grep -rn "git-pre-commit-audit"` sur tout le dépôt hors `archive/` → seulement les trois
  documents de ce chantier (brief, suivi, plan). Aucune référence croisée résiduelle : la
  prédiction du plan est confirmée.
- `ls commands/` → vide ; `ls agents/` → `implementation-auditor.md`, `step-implementer.md`
- `git diff --shortstat master...audit-integre` → `19 files changed, 576 insertions(+), 23
  deletions(-)`
- NON EXÉCUTÉE : « ouvrir une session neuve et constater que `git-pre-commit-audit` n'apparaît plus
  dans les skills disponibles » — hors de portée d'un sous-agent, qui ne peut pas ouvrir de session.
  Le contrôle statique équivalent (skill hors de `skills/`, aucun fichier de commande, aucune
  référence résiduelle) est, lui, exécuté et concluant.

### Conformité à l'intention

Les cinq critères de réussite du brief, un par un :

1. **« `git-pre-commit-audit` n'est plus appelable, ni par le modèle ni par l'utilisateur »** —
   atteint, vérifié. `git mv` vers `archive/`, historique préservé (le `--stat` montre bien un
   renommage à 0 ligne changée), aucun `commands/` ne l'expose, aucune référence croisée.
2. **« un audit tourne systématiquement avant toute clôture »** — atteint sur le plan documentaire.
   `cloture.md` en fait le **point 1** de la procédure, avant le contrôle des étapes, et `SKILL.md`
   Étape 5 le répète. Réserve de nature : c'est une discipline écrite, pas un verrou mécanique —
   arbitrage assumé et journalisé (hook `PreToolUse` explicitement rejeté).
3. **« l'audit est exécuté par un sous-agent, pas par la session de cadrage »** — atteint, et
   démontré : le présent rapport en est la sortie.
4. **« le fichier de suivi porte le commit audité (SHA) et le verdict »** — atteint au niveau du
   gabarit (`gabarit-suivi.md` : champ `audit:`, ligne `**Dernier audit** : <sha> — <VERDICT> —
   <date>`, note de remplissage). Voir toutefois la réserve R1 : le champ `audit:` n'est réclamé
   par aucune procédure de retour.
5. **« une clôture sans avis favorable ne va pas au bout »** — atteint sur le plan documentaire.
   `cloture.md` : « **Sans avis favorable, la clôture s'arrête ici.** », avec les trois suites
   (`FAVORABLE` / `RÉSERVES` / `DÉFAVORABLE`) et l'interdiction explicite de requalifier une réserve
   en détail. Même nature de réserve qu'au critère 2.

**Hors-périmètre** — respecté. Aucune reprise des fonctionnalités de `git-pre-commit-audit` : le
diff ne contient pas un pattern de sécurité, pas un grep de secret. `archive/README.md` renvoie
explicitement la reprise à un chantier dédié, ce qui documente la frontière au lieu de la franchir.

**Signaux de dérive** :

- *« si l'auditeur se met à corriger le code au lieu de le juger »* — non matérialisé, et
  doublement gardé : `Edit` retiré des `tools`, et deux interdits explicites (« Ne corrige rien.
  Pas même un défaut évident », « Un seul fichier en écriture »).
- *« si le dispositif rallonge la clôture au point qu'on l'esquive »* — non matérialisé de façon
  observable. Le coût est d'un appel de sous-agent, sans recopie du diff ni des critères par
  l'appelant ; le détail reste hors du contexte de session. Non mesurable à ce stade.
- *« si le skill d'audit déborde d'une page »* — **non tranchable seul**, voir R2. C'est la réserve
  principale de cet audit.

**Symptôme d'origine** — traité. Le point de contrôle de clôture n'est plus rendu par la session qui
a produit le travail, et il laisse désormais une trace versionnée (ce fichier), archivée en `done/`
avec le suivi, le brief et le plan.

### Qualité du code

Le chantier produit du markdown de prompt ; les critères applicables sont la précision du contrat,
la cohérence inter-fichiers et le style des voisins.

- **Style** — `implementation-auditor.md` est un miroir fidèle de `step-implementer.md` : même
  frontmatter, mêmes sections (`## Entrée`, `## Interdits`, `## Rapport de sortie`), même registre
  (impératif, deuxième personne, une justification par règle). Rien à redire.
- **R3 — chemins relatifs non résolus (cas limite réel, rencontré pendant cet audit).**
  `step-implementer.md:19-21` prend soin de dire que les chemins lus *à l'intérieur* des fichiers
  sont relatifs à la racine du dépôt, obtenue par `git rev-parse --show-toplevel`.
  `implementation-auditor.md` n'a pas l'équivalent, alors qu'il doit résoudre deux chemins relatifs :
  le champ `plan:` du suivi, et surtout son propre fichier de sortie
  `.claude/implementation/<slug>.audit.md`. Ici la racine (`~/.claude`, dont le suivi vit en
  `~/.claude/.claude/`) a été fournie hors contrat par l'appelant — `audit.md` ne la liste pas parmi
  les entrées à transmettre, et dit même « et **rien d'autre** ». Sur un dépôt où le cwd n'est pas
  la racine, l'agent écrirait son rapport à côté.
- **R4 — `..` contre `...` sur le seuil des 400 lignes.** `audit.md:20` mesure avec
  `git diff --shortstat <base>..<slug>` (deux points), tandis que l'agent lit le diff avec
  `<base>...<slug>` (trois points, choix justifié dans son prompt). Les deux formes divergent dès
  que `base:` avance pendant le chantier : le déclencheur d'audit intermédiaire compterait alors des
  lignes que l'audit ne regardera pas. Ici, identiques (`master` n'a pas bougé), donc invisible.
- **R5 — coquille.** `audit.md:30` : « Un refus ne se **represente** pas à chaque étape suivante »
  — accent manquant (« représente »), et la phrase se lit d'abord comme « ne se re-présente pas »,
  qui est le sens voulu. Dans un fichier de prompt, l'ambiguïté a un coût.
- **Cas limite bien traité, à signaler positivement** : `NON EXÉCUTÉE : <raison>` couvre le cas de
  la commande non rejouable sans jamais la supposer passante — c'est la faille naturelle de ce genre
  de dispositif, elle est fermée. De même, l'obligation d'écrire « rien à signaler » plutôt que
  d'omettre une section (`audit.md:120-121`) ferme le chemin d'échec silencieux du rapport partiel.

### Dette induite

- **R1 — champ `audit:` orphelin.** `gabarit-suivi.md:29` introduit
  `audit: .claude/implementation/<slug>.audit.md` dans le frontmatter, mais aucune procédure ne
  demande jamais de l'écrire : `audit.md`, section « Au retour », ne réclame que
  `**Dernier audit**` et `maj:` ; `cloture.md` ne le mentionne pas
  (`grep -n "audit:"` sur ces deux fichiers → aucun résultat). Le champ restera vide en pratique.
  Coût futur : un champ de gabarit que personne ne remplit finit par être recopié vide, puis par
  discréditer les champs voisins. Soit on l'inscrit dans « Au retour », soit on le retire.
  Corollaire : après l'archivage en `done/` (`cloture.md`, point 3), la valeur de `audit:` pointerait
  vers un chemin qui n'existe plus — même travers que les champs `brief:` et `plan:`, donc dette
  préexistante et non aggravée.
- **Duplication assumée, non problématique** : la grille des trois verdicts figure à la fois dans
  `implementation-auditor.md` (côté agent, pour décider) et dans `audit.md` (côté appelant, pour
  réagir). Les deux vues sont différentes et complémentaires ; la garder à un seul endroit
  obligerait l'un des deux à lire le fichier de l'autre. Pas une dette.
- **Aucune abstraction créée sans nécessité** : la décision « agent + référence, pas de sixième
  skill » évite un routage dupliqué. Elle est journalisée avec sa contre-option.
- **Observation, non reprochée** : ce chantier fait 599 lignes changées, au-delà du seuil de 400
  qu'il institue lui-même, sans audit intermédiaire. Le seuil n'existait pas pendant les étapes 1
  à 6, et le déclencheur est une *proposition*, jamais une obligation.

### Réserve principale — le signal « une page »

Le brief pose : *« si le skill d'audit déborde d'une page, c'est raté »*. Le plan n'a pas arrêté ce
que vaut « une page » — contrairement au seuil des 400 lignes, dont le brief demandait explicitement
qu'il soit chiffré et qui l'a été.

Constat factuel (`wc -l`) : `agents/implementation-auditor.md` → 119 lignes,
`skills/implementation-tracker/references/audit.md` → 121 lignes, soit 240 lignes pour le
dispositif. Voisinage immédiat : `step-implementer.md` → 94 lignes, `cloture.md` → 85 lignes.

Chacun des deux fichiers est donc ~30 % au-dessus du plus long de ses voisins, et le total est de
l'ordre de 2,5 pages écran. On peut soutenir que le signal ne vise pas le cumul de deux artefacts
distincts (un prompt d'agent, une procédure d'appelant), dont aucun n'est « le skill d'audit » à lui
seul. On peut aussi soutenir l'inverse.

Cet auditeur ne peut pas trancher sans l'utilisateur, et ne le fait donc pas : le constat est posé,
l'arbitrage lui revient. C'est ce qui empêche le verdict d'être `FAVORABLE` — un signal de dérive
possiblement matérialisé ne se requalifie pas en détail de mise en page, c'est précisément le
comportement que `cloture.md` interdit.

### Bloquants

Aucun. Aucun critère de réussite n'est manqué, le hors-périmètre est intact, aucune commande de
vérification n'échoue. Les cinq réserves R1 à R5 sont toutes traitables sans revenir sur une
décision de cadrage, et R2 relève d'un arbitrage utilisateur, pas d'une correction.

---

## 2026-08-14 — clôture — `4c5bd98`

**Verdict** : FAVORABLE

> Deuxième audit du chantier. Il porte sur **le diff complet** `master...audit-integre`
> (20 fichiers, 763 insertions, 23 suppressions), pas seulement sur le correctif de l'étape 8.
> Numérotation continuée à partir de `R5` : les constats de l'audit du `fe80476` gardent leurs
> numéros, les nouveaux commencent à `R6`.
>
> Même note de portée qu'au premier audit : le dispositif jugé est celui qui rend l'avis.
> L'indépendance est réelle (contexte isolé, aucun droit d'écriture hors ce fichier), mais
> l'auditeur ne prend pas de recul sur le prompt qui le constitue.

### Vérifications exécutées

Les huit commandes de vérification des étapes du suivi, plus les contrôles de bout en bout du plan
et un contrôle de non-régression sur le correctif :

- `git rev-parse HEAD` → `4c5bd98d51ea25fee88fd43a40798e344339c6f0` — conforme au SHA transmis
- `git log --oneline master..audit-integre` → 2 commits (`fe80476` étapes 1 à 6, `4c5bd98` étape 8)
- `git status --short` → vide — arbre de travail propre, rien d'oublié hors commit
- Étape 1 — `ls skills/ | grep -c git-pre-commit-audit` → `0` (attendu 0) ;
  `ls skills/` → `emmylua-ls/ git-smart-commit/ implementation-tracker/ intent-brief/ nvim-mini-test/`
- Étape 1 (plan) — `ls -l archive/git-pre-commit-audit/SKILL.md` → présent, 5.2K, contenu préservé
- Étape 2 — `head -6 agents/implementation-auditor.md` → `model: opus`,
  `tools: Read, Grep, Glob, Bash, Write` — pas d'`Edit`, conforme
- Étape 3 — `grep -c "400\|DÉFAVORABLE\|étapes restantes" .../references/audit.md` → `5` (> 0)
- Étape 4 — `grep -n "audit\.md\|\.audit\.md" .../SKILL.md` → 6 occurrences (l. 32, 36, 50, 78,
  234, 338), couvrant bloc « Emplacement », les deux exclusions de listing, le déclencheur des
  400 lignes, l'Étape 5
- Étape 5 — `grep -n "audit" .../references/cloture.md` → 6 occurrences (l. 11, 13, 45, 54, 62, 82)
- Étape 6 — `grep -n "audit:" .../references/gabarit-suivi.md` → l. 29,
  `audit: .claude/implementation/auth-refactor.audit.md   # créé au premier audit`
- Étape 7 — le rapport du `fe80476` existe dans ce fichier et porte des sorties de commande réelles
- Étape 8 — vérif « nouvel audit complet FAVORABLE » : c'est le présent rapport ; voir verdict
- `grep -rn "git-pre-commit-audit"` sur le dépôt hors `archive/` → aucun fichier suivi par git en
  dehors des trois documents de ce chantier (brief, suivi, plan). Les seules autres occurrences
  sont dans `backups/`, `projects/`, `file-history/`, `history.jsonl` — journaux de sessions,
  non versionnés, hors périmètre
- `wc -l` → `implementation-auditor.md` 128, `audit.md` 132, `step-implementer.md` 93,
  `cloture.md` 85, `gabarit-suivi.md` 82
- `git diff --shortstat master...audit-integre` → `20 files changed, 763 insertions(+), 23 deletions(-)`
- NON EXÉCUTÉE : « ouvrir une session neuve et constater que `git-pre-commit-audit` n'apparaît plus
  dans les skills disponibles » — un sous-agent ne peut pas ouvrir de session. L'équivalent
  statique (skill hors de `skills/`, `ls commands/` vide, aucune référence versionnée résiduelle)
  est exécuté et concluant.

### Traitement des réserves du premier audit

Les cinq réserves prises en charge par l'étape 8, contrôlées une par une dans le diff
`fe80476..4c5bd98` :

- **R1 (champ `audit:` orphelin)** — **levée.** `audit.md:65` inscrit désormais
  « frontmatter → `audit: .claude/implementation/<slug>.audit.md`, au premier audit du chantier »
  dans la section « Au retour ». Le champ a une procédure qui le réclame, et le suivi de ce
  chantier le porte effectivement (`audit-integre.md:13`).
- **R2 (signal « une page »)** — **arbitrée par l'utilisateur**, journalisée au suivi le
  2026-08-14 : le signal se compte **par fichier**, pas sur le cumul du dispositif ; jugé non
  déclenché. Le suivi fait foi. Constat factuel post-correctif, pour mémoire : les deux fichiers
  ont grossi de +9 et +11 lignes (128 et 132), l'écart au plus long voisin passe de ~30 % à ~40 %.
  L'auditeur ne rouvre pas un arbitrage rendu ; il en donne les valeurs à jour.
- **R3 (racine du dépôt hors contrat)** — **levée**, des deux côtés : `implementation-auditor.md:25-28`
  ajoute la résolution par `git rev-parse --show-toplevel`, et `audit.md:43-45` ajoute la racine à
  la liste de ce que l'appelant transmet. Le correctif a été éprouvé en conditions réelles pendant
  cet audit — la racine était bien transmise, et le rapport atterrit au bon endroit. Voir R6 pour
  une asymétrie résiduelle sans conséquence.
- **R4 (`..` contre `...`)** — **levée.** `audit.md:20` mesure désormais avec
  `git diff --shortstat <base>...<slug>`, aligné sur le diff que l'agent lit, et la raison est
  écrite juste en dessous (l. 23-24) plutôt que laissée à deviner.
- **R5 (coquille « represente »)** — **levée**, et mieux que corrigée : la phrase est réécrite en
  « Un refus ne se re-propose pas à chaque étape suivante : n'y revenir qu'une fois, si le diff a
  de nouveau doublé ». L'ambiguïté de lecture disparaît avec l'accent.
- **Constats non numérotés (motif de l'étape 8)** — **levé.** La règle de numérotation est posée
  côté agent (`implementation-auditor.md:97-99`) et côté gabarit (`audit.md:130-132`), et le
  gabarit d'exemple porte maintenant `**R1**` et `**R2**` sur ses constats. Le défaut visé était
  réel : dans le rapport du `fe80476`, `R2` est cité deux fois mais n'est posé sur aucun constat —
  il désigne la section « Réserve principale — le signal "une page" », que rien ne rattache au
  numéro.

### Conformité à l'intention

Les cinq critères de réussite du brief, un par un :

1. **« `git-pre-commit-audit` n'est plus appelable, ni par le modèle ni par l'utilisateur »** —
   **atteint, vérifié.** `git mv` vers `archive/` (le `--stat` montre bien dix renommages à zéro
   ligne changée : l'historique et le contenu sont intacts), `skills/` ne le contient plus,
   `commands/` est vide, aucune référence versionnée résiduelle.
2. **« un audit tourne systématiquement avant toute clôture »** — **atteint.** `cloture.md` en fait
   le **point 1**, avant même le contrôle des étapes, et `SKILL.md:338` le répète. C'est une
   discipline écrite et non un verrou mécanique : arbitrage assumé et journalisé (hook `PreToolUse`
   explicitement rejeté), régime commun à tous les autres contrôles du tracker.
3. **« l'audit est exécuté par un sous-agent, pas par la session de cadrage »** — **atteint et
   démontré deux fois** : ce rapport et le précédent sont les sorties de deux exécutions réelles de
   l'agent, dont une sur un correctif produit après ses propres remarques. La boucle complète
   audit → réserves → correctif → nouvel audit a tourné de bout en bout.
4. **« le fichier de suivi porte le commit audité (SHA) et le verdict »** — **atteint, et constaté
   en pratique** : `audit-integre.md:59` porte `**Dernier audit** : fe80476 — RÉSERVES — 2026-08-14
   (rapport : audit-integre.audit.md)`, et le frontmatter porte `audit:`. Le gabarit
   (`gabarit-suivi.md:29, 55, 78-79`) et la procédure de retour (`audit.md:62-66`) sont cohérents
   depuis la levée de R1.
5. **« une clôture sans avis favorable ne va pas au bout »** — **atteint.** `cloture.md:21-23` :
   « **Sans avis favorable, la clôture s'arrête ici.** », avec les trois suites et l'interdiction
   explicite de requalifier une réserve en détail pour pouvoir continuer. `audit.md:71-81` porte la
   même table côté appelant, plus l'obligation de **relancer un audit complet** après traitement —
   règle appliquée à la lettre par le présent audit.

**Hors-périmètre** — **respecté.** Le diff complet ne contient pas un pattern de sécurité, pas un
grep de secret, aucune reprise fonctionnelle de `git-pre-commit-audit`. `archive/README.md` renvoie
explicitement cette reprise à un chantier dédié : la frontière est documentée au lieu d'être
franchie. Le mot « remplacement » y désigne le remplacement du *point de contrôle*, pas celui des
patterns — la phrase suivante lève l'ambiguïté.

**Signaux de dérive** :

- *« si l'auditeur se met à corriger le code au lieu de le juger »* — **non matérialisé**, et
  triplement gardé : `Edit` absent des `tools`, interdit explicite « Ne corrige rien. Pas même un
  défaut évident », et « Un seul fichier en écriture ». Éprouvé : les cinq réserves du premier
  audit ont été corrigées par la session de chantier, pas par l'auditeur.
- *« si le skill d'audit déborde d'une page »* — **non déclenché**, sur arbitrage utilisateur du
  2026-08-14 journalisé au suivi (mesure par fichier). Valeurs à jour données en R2 ci-dessus.
- *« si le dispositif rallonge la clôture au point qu'on l'esquive »* — **non matérialisé de façon
  observable.** Coût constaté sur ce chantier : un appel de sous-agent par audit, l'appelant ne
  recopiant ni le diff ni les critères, et le détail restant hors du contexte de session. Le seul
  allongement réel a été le tour de correctif — c'est l'effet recherché, pas la dérive visée.

**Symptôme d'origine** — **traité sur son périmètre.** Le contrôle de clôture n'est plus rendu par
la session qui a produit le travail ; il laisse une trace versionnée, archivée en `done/` avec le
suivi, le brief et le plan ; et le bloc `VÉRIFICATION` auto-déclaré par `step-implementer` cesse
d'être cru sur parole, puisque l'auditeur rejoue les commandes des étapes. Voir R7 pour la part du
symptôme qui subsiste, hors des critères.

### Qualité du code

Le chantier produit du markdown de prompt : les critères applicables sont la précision du contrat,
la cohérence inter-fichiers et le style des voisins.

- **Style** — `implementation-auditor.md` reste un miroir fidèle de `step-implementer.md` (même
  frontmatter, mêmes sections `## Entrée` / `## Interdits` / `## Rapport de sortie`, même registre
  impératif, une justification par règle). Les ajouts de l'étape 8 respectent cette densité : deux
  paragraphes courts, chacun terminé par la conséquence concrète du non-respect (« ton rapport
  atterrit à côté », « rend le rapport illisible »). Idiome des fichiers voisins tenu.
- **R6 — asymétrie résiduelle du contrat sur la racine du dépôt (mineur, sans mode de défaillance).**
  `audit.md:43-45` range la racine parmi ce que l'appelant **transmet** ; `implementation-auditor.md:21-23`
  énumère ce que l'appelant fournit et ne la mentionne pas, l'agent la calculant lui-même juste
  après. Les deux documents décrivent donc une entrée légèrement différente. Sans conséquence
  pratique — l'agent est autonome, et une entrée surnuméraire ne le gêne pas — mais c'est
  exactement le genre d'écart inter-fichiers qui avait produit R3. Une phrase du type « l'appelant
  peut te la donner ; sinon, calcule-la » suffirait à refermer.
- **Cas limites bien traités, à signaler positivement** : `NON EXÉCUTÉE : <raison>` ferme le chemin
  d'échec silencieux de la commande non rejouable ; l'obligation d'écrire « rien à signaler »
  plutôt que d'omettre une section (`audit.md:127-128`) ferme celui du rapport partiel ; le
  contrôle préalable de l'appelant (`audit.md:58-60`) ferme celui du verdict rendu sans exécution ;
  et l'obligation d'appender en relisant le fichier existant (`implementation-auditor.md:90-92`)
  ferme celui de l'écrasement de l'historique d'audit — appliquée ici, le rapport du `fe80476` est
  intact au-dessus de cette section.
- **Repli `mv` + `git add`** dans la boucle d'archivage (`cloture.md:54-58`) : le `[ -e "$f" ]
  || continue` couvre correctement l'absence de rapport d'audit (chantier abandonné avant audit), et
  le `2>/dev/null ||` couvre le fichier non suivi par git. Cas limites du script pensés.

### Dette induite

- **R7 — une part du symptôme d'origine reste hors dispositif (observation, hors critères).** Le
  brief nomme trois points de contrôle auto-jugés ; deux sont traités (clôture, et le bloc
  `VÉRIFICATION` de `step-implementer` désormais rejoué), le troisième ne l'est pas : la
  confrontation plan ↔ brief d'`intent-brief` (`skills/intent-brief/SKILL.md:193-205`) reste rendue
  par la session qui vient de produire le plan, et sa sortie « en trois lignes, pas un rapport » ne
  laisse toujours aucune trace versionnée. Aucun critère de réussite ne la couvre et le « But » du
  brief scope explicitement la clôture : ce n'est **pas** un manquement, et le signaler comme tel
  serait inventer un critère. C'est un candidat de chantier suivant, au même titre que la reprise
  des patterns de sécurité.
- **R8 — circularité de l'étape 8 avec le point 1 de `cloture.md` (procédure, ce chantier
  seulement).** `cloture.md:10-11` demande que **toutes** les étapes soient cochées avant
  d'auditer ; or la vérification de l'étape 8 est « nouvel audit complet FAVORABLE », qui ne peut
  être satisfaite qu'après. L'étape est donc `[>]` au moment où cet audit tourne. L'ordre correct
  est celui suivi ici (auditer, puis cocher), mais l'appelant doit y penser : une étape dont la
  vérification est l'audit lui-même ne peut pas précéder l'audit. Coût futur : chaque étape
  corrective née d'un audit rejouera cette gêne. Formuler ces étapes avec une vérification portant
  sur le correctif (« R3 traité : `grep -n "rev-parse" agents/implementation-auditor.md` ») plutôt
  que sur le verdict à venir l'éviterait.
- **Champ `audit:` obsolète après archivage** — dette **préexistante et non aggravée** : après le
  déplacement en `done/` (`cloture.md`, point 3), `audit:` pointera vers un chemin disparu, comme
  `brief:` et `plan:` avant lui. Rappelé pour mémoire, déjà noté en corollaire de R1.
- **Duplication assumée, non problématique** : la grille des trois verdicts figure côté agent (pour
  décider) et côté appelant (pour réagir). Les deux vues sont complémentaires et l'unification
  obligerait l'un à charger le fichier de l'autre. Pas une dette.
- **Aucune abstraction créée sans nécessité** : « agent + référence, pas de sixième skill » évite un
  routage dupliqué ; la décision est journalisée avec sa contre-option.
- **Observation, non reprochée** : le chantier totalise 763 lignes changées, au-delà du seuil de 400
  qu'il institue, sans audit intermédiaire. Le seuil n'existait pas pendant les étapes 1 à 6, et le
  déclencheur est une proposition, jamais une obligation.

### Bloquants

Aucun.

### Pourquoi FAVORABLE et non RÉSERVES

Les cinq critères de réussite sont atteints et vérifiés par commandes rejouées, le hors-périmètre
est intact, aucun signal de dérive n'est matérialisé — celui qui appelait un arbitrage a été tranché
par l'utilisateur et journalisé — et les cinq réserves du premier audit sont levées, non
contournées. R6 est une asymétrie de rédaction sans mode de défaillance, R7 une piste de chantier
suivant explicitement hors des critères validés, R8 une gêne de procédure interne au tracker.
Aucun des trois ne change ce que l'utilisateur déciderait de faire de ce chantier : ils sont
consignés pour la suite, pas soumis à arbitrage avant clôture.
