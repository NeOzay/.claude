---
slug: check-pipeline-python
---

## 2026-08-24 — clôture — `1552f29`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → **rc 0**, « Pipeline conforme. », 7 contrôles verts
  (30 renvois, 9 empreintes, 6 fichiers listés, 3 agents, 6 archives, 27 fichiers, 12 chemins)
- `uvx pytest scripts/tests -q` → **65 passed**, 0 échec, 0.26 s
- `uvx basedpyright` (commande du plan, de l'étape 12 du suivi et de `contrat.md` § Dépendances)
  → **52 errors** — voir R1
- `uvx --with pytest basedpyright` (commande amendée au journal du 2026-08-24) → **0 error,
  0 warning, 0 note**
- `uvx ruff check scripts skills/implementation-tracker` → « All checks passed! »
- `uvx ruff check .` (commande documentée à `contrat.md` § Dépendances) → **3 erreurs**, toutes
  dans `statusline-command.py`, préexistantes à la branche — voir R8
- `python3 skills/list-dir/scripts/list-dir.py validate .claude/implementation/todo/technical-debt`
  → « 20 élément(s) conformes au contrat », rc 0
- `… validate .claude/implementation/todo/technical-debt-solde` → « 11 élément(s) conformes », rc 0
- **Parité `impl-list.sh` → `impl_list.py`** (le `.sh` restauré depuis `master` dans un scratch) sur
  `.claude/implementation`, `todo/`, `done/` et un répertoire absent → stdout, stderr et rc
  **identiques** dans les quatre cas
- **Garde-fou du garde-fou** — injections manuelles sur une copie hors dépôt de l'arbre réel, chaque
  contrôle appelé directement : ancre morte dans `CLAUDE.md` → rouge ; ancre morte dans
  `skills/list-dir/SKILL.md` → rouge ; « le suivi fait foi » recopié → rouge « 2 occurrences » ;
  `bash scripts/list-dir.py  # [ -f scripts/list-dir.py ]` → rouge ; `python3 scripts/x.py` →
  rouge ; `$HOME/.claude/skills/list-dir/scripts/nexistepas.py` → rouge. Arbre non modifié → 7 verts.
- `git ls-tree -r HEAD | grep pycache` → vide ; `git status --porcelain -uall` → propre
- `grep -rn 'check-pipeline\.sh|impl-list\.sh' --include='*.md'` → plus aucune mention hors
  archives, registre de dette, brief, suivi et plan du chantier

### Conformité à l'intention

- Critère « `python3 scripts/check-pipeline.py` → code 0, tous contrôles verts » : **atteint,
  vérifié**. Le fichier s'appelle `check_pipeline.py` : écart à la lettre du brief, tranché et
  consigné au journal du 2026-08-23 (les unitaires importent les fonctions de contrôle). Écart
  légitime.
- Critère « suite rejouable : unitaires par contrôle **et** injection bout-en-bout d'un défaut par
  contrôle » : **atteint, vérifié**. Les sept contrôles ont chacun leur fichier d'unitaires
  (`test_controles_4_5.py` en couvre deux), et `test_bout_en_bout.py` paramètre sept injections plus
  un arbre sain, en passant par `main()` — donc en prouvant aussi que chaque contrôle est branché.
- Critère « `basedpyright` en mode `all` → 0 erreur, nouveau code couvert par `pyrightconfig.json` » :
  **atteint sous condition, vérifié**. `pyrightconfig.json` inclut bien `scripts` et
  `typeCheckingMode: "all"`. 0 erreur **uniquement** avec `--with pytest` — voir R1.
- Critère « les cinq dettes retenues sont soldées ou explicitement assumées » : **atteint, vérifié**.
  Quatre entrées déplacées en `technical-debt-solde/` avec une section « Soldé le » datée, détaillée
  point par point et adossée à une preuve exécutable nommée ; `chemin-skill-code-en-dur` amendée et
  **laissée ouverte**, avec la distinction symptôme/cause explicitée et le constat « le contrôle 7
  n'empêche pas le compte de croître ». Traitement au-dessus du minimum demandé.
- Hors-périmètre : **respecté**. Aucun fichier de `skills/list-dir/` ni de `hooks/` dans le diff ;
  aucun test ne touche `listdir` ; `contrat.md` n'est modifié que d'une ligne d'appel.
- Signaux de dérive : **aucun matérialisé**. Le diff sur `contrat.md`, `cloture.md` et `SKILL.md` se
  réduit à 4 lignes, toutes `bash …*.sh` → `python3 …*.py`. Deux scripts plats, aucun paquet, aucun
  `Result[T]`. Les changements de comportement des contrôles (portée du 1, occurrences du 2, garde
  du 6, contrôle 7 neuf) sont chacun adossés à une dette retenue ou à un arbitrage du brief —
  vérifié un par un contre le `.sh` de `master` ; les contrôles 4 et 5 sont sémantiquement
  identiques à l'original. Aucune dette hors des cinq retenues n'a été touchée
  (`git diff --name-status` sur les registres : exactement 4 renommages + 1 modification).
- Symptôme d'origine : **disparu**. Le garde-fou est en Python, sous `pyrightconfig.json`, et il a
  désormais une suite de tests là où sa fidélité ne reposait que sur des injections manuelles
  recopiées en prose.

### Qualité du code

- **R1** — `uvx basedpyright`, la commande écrite dans le plan, dans la vérification de l'étape 12
  du suivi **et** dans `contrat.md` § Dépendances, rend **52 erreurs** sur cet arbre : les huit
  fichiers de `scripts/tests/` remontent `reportMissingImports` sur `pytest` et la cascade
  `reportUnknownMemberType` / `reportUntypedFunctionDecorator` qui en découle. Seul
  `uvx --with pytest basedpyright` rend 0. Le journal du 2026-08-24 constate le problème et renvoie
  la correction de `contrat.md` à « une entrée de dette à verser à la clôture » — **cette entrée
  n'existe pas dans le diff**. En l'état, la seule commande documentée pour un tiers échoue, et la
  documentation de la dépendance est fausse depuis ce chantier sans que rien ne le porte. Le critère
  du brief reste atteint (la commande amendée rend 0), mais l'écart doit être tranché avant
  archivage : soit l'entrée de dette est créée, soit `contrat.md` est corrigé dans un chantier suivant.
- **R2** — `scripts/check_pipeline.py:47`, `ZONES_EXCLUES` — le contrôle 1 parcourt l'**arbre de
  travail**, pas l'index git. Les répertoires ignorés qui ne figurent pas dans la liste sont donc
  inspectés : `cache/`, `backups/`, `file-history/`, `sessions/`, `ide/`, `projects/`… `cache/changelog.md`
  est déjà scanné aujourd'hui (constaté ; sans conséquence, il ne porte aucun renvoi). Un artefact
  local futur portant un lien `](…contrat.md#…)` rendrait le garde-fou rouge sans qu'aucune
  correction ne soit possible dans le dépôt, et la cause serait invisible pour qui lit le message.
  Le risque naît de l'extension de portée voulue par la dette : il n'existait pas quand le contrôle
  se limitait à `skills/`. Filtrer sur `git ls-files` — ou exclure tout ce qui est ignoré — lèverait
  la réserve.
- **R3** — même endroit — `.claude/implementation/` est exclu parce qu'il porte « des archives figées
  et un registre de dette qui décrivent des renvois morts », mais `.claude/plans/` **ne l'est pas**,
  alors que les plans archivés sont exactement des documents datés qu'on ne réécrit pas. L'asymétrie
  n'est justifiée nulle part — ni dans le code, ni au journal. Sans effet aujourd'hui (un seul plan
  présent, vert), elle deviendra une friction dès qu'un plan citera une section du contrat qui bouge.
- **R4** — `scripts/check_pipeline.py:392`, `garde_commande()` — `ligne.find("#")` prend le **premier**
  `#` de la ligne quel qu'en soit le contexte, alors que le seul cas visé est celui d'un commentaire
  shell. Une ligne dont le garde est précédé d'un `#` non-commentaire (ancre markdown, fragment
  d'URL, chaîne) verrait son garde invalidé et produirait un faux rouge. Le cas est étroit et n'est
  pas testé, là où le cas symétrique (`test_garde_en_commentaire_apres_lappel`) l'est.
- **R5** — même endroit, `ZONES_EXCLUES` — l'exclusion est un préfixe **depuis la racine** : un
  `node_modules/` imbriqué (`skills/x/node_modules/`) n'est pas exclu, alors que l'entrée existe
  précisément pour cela. Accessoirement, `node_modules` ne figure pas dans la liste consignée au
  journal du 2026-08-23 (« `agents/`, `.git/`, `plugins/` et `.claude/implementation/` ») : le code
  exclut une zone de plus que ce que le suivi déclare.
- **R6** — `impl_list.py:41` — `sorted()` trie par point de code, là où le `find … | sort` du `.sh`
  triait selon la locale. La parité a été vérifiée exécutablement sur les quatre répertoires du
  dépôt (sorties identiques), et les noms de chantier étant des slugs minuscules l'écart est
  aujourd'hui sans effet. Il est signalé parce que la dette soldée revendique une équivalence de
  sortie, et que cette équivalence n'est pas universelle.

### Dette induite

- **R7** — `scripts/check_pipeline.py:271` — `charger_suivis()` est appelée une fois par le contrôle 3
  et une fois par le contrôle 5, sans mémoïsation : `impl_list.py` est donc exécuté deux fois, en
  deux instances de module distinctes. Le coût est négligeable et l'isolation est plutôt un
  avantage ; c'est noté pour mémoire, pas comme un défaut à corriger.
- **R8** — hors périmètre du chantier mais constaté à l'exécution : `uvx ruff check .`, la commande
  documentée à `contrat.md` § Dépendances, rend 3 erreurs dans `statusline-command.py`, fichier de
  la racine préexistant à la branche et non couvert par `pyrightconfig.json` (dont l'`include` vaut
  `skills` + `scripts`). Rien n'est imputable à ce chantier ; le constat est posé parce qu'il touche
  la même documentation de dépendance que R1 et pourrait être traité avec elle.

### Bloquants

Aucun. Les quatre critères de réussite sont atteints et vérifiés par exécution ; R1 est une réserve
de documentation, pas un critère manqué.
