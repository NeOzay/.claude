---
slug: recopies-hors-contrat
---

## 2026-09-02 — clôture — `a9189db`

**Verdict** : RÉSERVES

### Vérifications exécutées

Toutes lancées depuis la racine du dépôt, sur la branche `recopies-hors-contrat` à `a9189db`,
arbre propre.

- `python3 scripts/check_pipeline.py` → **8 contrôles verts**, « Pipeline conforme », code 0.
  Contrôle 2 : les 9 empreintes de `contrat.md` restent à une occurrence. Contrôle 8 : 23 renvois
  entre skills, tous résolvent (16 avant le chantier, d'après le plan).
- Ét. 1 — `grep -rn "intitulé de l'entrée conservée" skills/ .claude/implementation/todo/` →
  **aucune sortie** (attendu : aucune).
- Ét. 1 — `diff skills/implementation-tracker/list-dir/technical-debt/templates/review.md
  .claude/implementation/todo/technical-debt/.list/templates/review.md` → **identiques**.
- Ét. 2 — `grep -rn --include='*.md' "ne change jamais" skills/` → **0** (attendu 0).
- Ét. 3 — `grep -rn --include='*.md' "détection de renommage\|renommage pur" skills/` → **1**,
  `contrat-liste.md:445` (attendu 1).
- Ét. 4 — `grep -rn --include='*.md' "avale" skills/` → **1**, `contrat-liste.md:142` (attendu 1).
- Ét. 5 — `grep -c "^- \*\*Vérifié par\*\*\|^- \*\*Verdict\*\*"
  skills/debt-review/references/gabarit-rapport.md` → **0** (attendu 0).
- Ét. 6 — `grep -rn --include='*.md' "16 — 16" skills/` → **1**, `debt-review/SKILL.md:265`
  (attendu 1).
- Ét. 7 — `grep -rn --include='*.md' "atomique" skills/` → **1**, `contrat.md:140` (attendu 1) ;
  `grep -rn --include='*.md' "travail partiel" skills/` → **2**, `contrat.md:167` et `:186`
  (attendu 2).
- Ét. 8 — `list-dir list .claude/implementation/todo/technical-debt | wc -l` → **39** (38 avant,
  39 attendus) ; `list-dir validate … --filled` → « 39 élément(s) remplis et conformes au
  contrat », code 0.
- Contrôle d'ancres hors garde-fou — `ancres_markdown()` de `check_pipeline.py` appliqué à
  `dette.md` : `ce-quune-entrée-porte` **existe** ; `## L'API Python` présent dans
  `contrat-liste.md` (l. 351) → `#lapi-python` résout.

Aucune commande du suivi ou du brief n'est restée non exécutée.

### Conformité à l'intention

- **Critère « la contradiction `doublon` est tranchée en faveur de l'`id` »** : **atteint,
  vérifié**. `categories.md:17` et `templates/review.md:16` disent désormais l'`id`. La
  contre-vérification `grep "intitulé de l'entrée conservée"` ne rend plus rien, et
  `categories.md` ne se contredit plus à cinquante lignes d'écart (l. 17 et l. 71 concordent).
- **Critère « chacune des six recopies est résorbée »** : **atteint**, les six lignes du tableau,
  plus les trois écritures admises par arbitrage (`contrat-liste.md:572`, deux redites internes de
  `dette.md`). Chaque résorption laisse une prescription en place et déplace le seul motif — la
  « ligne de partage » du journal est tenue partout où j'ai relu le diff.
- **Critère « chaque autorité désignée est vérifiable par lecture »** : **atteint, avec la réserve
  R2**. `contrat-liste.md#un-élément`, `#lapi-python`, `#ce-que-contract-vise…`, `dette.md#solder`,
  `templates/review.md`, `debt-review/SKILL.md` Étape 3, `contrat.md#format-détape-et-délégabilité`
  et `#contrat-des-sous-agents` portent chacune la règle, et je n'ai pas retrouvé de
  re-développement concurrent — sauf pour le comptage `merge` (R2) et sauf pour la règle de preuve
  du `doublon`, qui n'a pas d'autorité désignée (R1).
- **Critère « `check_pipeline.py` reste vert »** : **atteint, vérifié** (8/8).
- **Renoncement au mécanisme** : le brief l'autorise « auquel cas le renoncement s'écrit et se
  motive ». L'entrée `regles-hors-contrat-sans-empreinte` existe, décrit le trou, les deux formes
  étudiées et la raison du report, et le registre valide. Exigence tenue.
- **Hors-périmètre** : respecté. `contrat.md` n'est pas touché, les trois `agents/*.md` non plus
  (contrôle 4 vert), aucun `contract.toml` ni aucune fiche dérivée n'est modifié, aucun
  `description = ""` n'est comblé, aucun `.py` n'entre au diff. La seule copie touchée —
  `.list/templates/review.md` — est explicitement autorisée par le brief (« la semence et sa copie
  se corrigent à la main une dernière fois, `diff` à l'appui »), et le `diff` est vide.
- **Signaux de dérive** : **aucun matérialisé.** *Arrêt sec 1* — j'ai relu les cinq blocs supprimés
  un par un ; aucun ne portait de jugement propre. Le `if … ; false` de `debt-review/SKILL.md` est
  conservé, le blockquote sur `validate --filled` de `gabarit-rapport.md` aussi, la table
  `RÉSULTAT` → action de `tracker/SKILL.md` aussi, et le « 16 — 16 » retiré du gabarit se retrouve
  intact et enrichi dans son autorité (`SKILL.md:264-266`). *Arrêt sec 2* — aucune ligne de
  mécanisme n'est écrite : `check_pipeline.py` n'apparaît pas au diff. *Arrêts pour arbitrage* —
  les trois élargissements sont datés et motivés dans `## Élargissements de périmètre`, et le plan
  les porte en « à ratifier ».
- **Symptôme d'origine** : **la contradiction a disparu** ; la multiplicité qui l'a produite n'est
  résorbée qu'en partie (R1).

### Qualité du code

- **R1** — `skills/debt-review/references/categories.md:17` et `:70`,
  `skills/implementation-tracker/list-dir/technical-debt/templates/review.md:14` et `:16`,
  `skills/implementation-tracker/references/dette.md:251-253` : la règle « la preuve d'un `doublon`
  est l'`id` de l'entrée conservée » reste **écrite quatre fois**, sans autorité désignée. Les
  quatre écritures concordent aujourd'hui — c'est exactement l'état d'avant la divergence. Le brief
  ne l'inscrit pas au tableau des six recopies, donc aucun critère n'est en défaut ; mais son
  « But » dit « puis résorber les recopies qui l'ont produite », et celles-ci sont précisément
  celles-là. La cinquième écriture (`gabarit-rapport.md`) a bien disparu, ce qui fait passer de 5 à
  4. Constat à porter à l'utilisateur, pas à corriger d'office.
- **R2** — `skills/debt-review/references/gabarit-rapport.md:132-134` redéveloppe le raisonnement
  du comptage : « les deux comptes divergent si un `title` ouvre un faux bloc — jamais si une fiche
  a disparu, puisqu'elle manque des deux côtés », qui est la substance de
  `debt-review/SKILL.md:259-262`, l'autorité désignée à l'étape 6. Seul l'exemple chiffré
  « 16 — 16 » a migré. Le plan l'assume (« garde sa phrase descriptive »), et la ligne de partage
  se défend — le gabarit décrit ce que *le rapport* dit, le SKILL prescrit *le geste*. Mais la
  vérification de l'étape 6 (`grep "16 — 16"`) est plus étroite que le critère « aucune autre ne la
  redéfinit » : elle passe au vert sans l'établir.
- **R3** — trois renvois introduits par le chantier échappent au garde-fou qui devait les rendre
  vérifiables. `RENVOI_INTER_SKILL` (`check_pipeline.py:638`) n'accepte que les cibles commençant
  par `../` : les deux `[Ce qu'une entrée porte](#ce-quune-entrée-porte)` de `dette.md:273` et
  `:298`, et le `[L'API Python](#lapi-python)` de `contrat-liste.md:572` ne sont **jamais
  contrôlés**. Ils résolvent aujourd'hui (vérifié à la main, ci-dessus), mais le journal en fait un
  choix de conception (« un renvoi par redite vers un autre skill aurait fait trois liens
  sortants ») : ce choix échange une vérification automatique contre une lisibilité, sans que le
  suivi le dise. Même remarque pour `cloture.md:71` `([Solder](dette.md#solder))`, forme
  pré-existante non touchée.
- **R4** — `skills/implementation-tracker/SKILL.md:174-175` : « le renvoi **ci-dessus** dit
  pourquoi ». C'est un repère positionnel, dans un dépôt dont `dette.md` « Désigner sans numéro de
  ligne » condamne exactement cette forme (« le repère se périme au premier commit qui insère une
  ligne au-dessus »). Une insertion entre les points 4 et le renvoi le rend faux en silence, et
  aucun contrôle ne l'attrape. Le reste du fichier nomme systématiquement sa cible
  (`[Format d'étape et délégabilité](…)`) : c'est aussi un écart de style local.
- **R5** — chaîne de renvois à deux sauts pour le motif du commit mixte :
  `debt-review/SKILL.md:374` → `dette.md#solder`, qui renvoie lui-même à
  `contrat-liste.md#lapi-python`. Un lecteur de `debt-review` doit suivre deux liens pour obtenir
  le *pourquoi*. Conséquence directe de l'élargissement daté du 2026-09-02 (l'autorité bascule de
  `dette.md` vers `contrat-liste.md`) ; le renvoi de `debt-review` n'a pas été repointé sur la
  nouvelle autorité.
- **R6** — `gabarit-rapport.md:69-71` renvoie à `templates/review.md` **sans ancre**, et vers le
  préambule d'un fichier-semence. Le contrôle 8 ne vérifie alors que l'existence du fichier : une
  réécriture du préambule laisse le renvoi vert et vide de contenu. C'est aussi le seul renvoi du
  chantier qui pointe vers une zone que `derive` ignore (« tout ce qui précède le premier `##` »),
  donc invisible dans toute fiche produite — voulu d'après le brief, mais fragile.

Rien d'autre à signaler sur ce point : le style des fichiers voisins (blockquotes
*Mode de défaillance*, gras d'attaque, renvois en lien nommé) est respecté partout ailleurs, et
aucune section n'a été supprimée sans que sa substance se retrouve dans l'autorité citée.

### Dette induite

- **R7** — `skills/implementation-tracker/SKILL.md:292` et
  `skills/implementation-tracker/references/contrat.md:163-164` portent désormais la même phrase à
  quelques mots près (« L'appelant reste responsable au retour : relire le fichier de suivi avant
  d'y écrire »). Le chantier a retiré le motif du SKILL, pas la prescription — conforme à sa propre
  ligne de partage, donc pas un défaut ; mais c'est une recopie verbatim de plus qu'aucune empreinte
  ne couvre, c'est-à-dire l'illustration exacte de la dette ouverte à l'étape 8. À verser au
  contexte de `regles-hors-contrat-sans-empreinte` plutôt qu'à corriger.
- **R8** — les étapes 4 à 7 sont soldées dans un commit unique (`398bafa`), là où
  `contrat.md` « Branche et commits » impose qu'« une étape qui passe en `[x]` reçoit un commit
  dédié ». L'aplatissement de clôture rend le point sans conséquence sur `master`, mais tant que la
  branche vit, aucun `git show` n'isole l'étape 5 ou 6. Aucun critère de réussite n'est en cause.

### Bloquants

Aucun. Les quatre critères de réussite sont atteints et vérifiés par commande, le hors-périmètre est
intact, aucun signal de dérive n'est matérialisé. Le verdict est `RÉSERVES` et non `FAVORABLE` parce
que R1 laisse le symptôme d'origine — une règle écrite plusieurs fois — vivant à quatre exemplaires
sur la règle même qui a déclenché le chantier, et que R2 signale un critère (« aucune autre ne la
redéfinit ») dont la commande de vérification n'établit qu'une partie. Les deux se lèvent par une
décision de l'utilisateur, pas par du code.
