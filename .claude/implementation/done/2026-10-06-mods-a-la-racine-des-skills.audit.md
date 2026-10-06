---
slug: mods-a-la-racine-des-skills
---

## 2026-10-06 — intermédiaire — `ff927cc`

**Verdict** : DÉFAVORABLE

Périmètre jugé : Étapes 1 à 6, cochées `[x]` (`bb03756` à `ff927cc`). Les Étapes 7 à 11, encore
`[ ]`, ne sont pas reprochées. Diff lu : `git diff master...mods-a-la-racine-des-skills`. Brief,
Suivi et Plan (`.claude/plans/compressed-tinkering-hanrahan.md`) lus.

Le verdict tient à un seul point, **R1** : la commande de vérification de l'Étape 2 sort en échec,
alors que le critère du Suivi exige qu'elle passe, et le Shadow-skill `claude-code-mods` affirme le
contraire de ce qu'elle rend. Le reste des Étapes 1 à 6 est conforme et vérifié. Le point se lève
vite, mais il demande une décision de l'utilisateur, d'où le verdict le plus sévère.

### Vérifications exécutées

Toutes depuis `/home/debian/.claude`, sauf mention contraire. Claude Code 2.1.291.

- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` → `0`
- `test ! -e skills/lexique/mod` → vrai (absent)
- `grep -cE 'HOME|\.claude/skills' skills/lexique/hooks/register.ts` → `0`. Aucun `HOME` ni
  `~/.claude` dans `skills/*/hooks/*.ts` ni `skills/*/types/*.ts`.
- `/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. »,
  9 contrôles verts, code 0
- `python3 scripts/sante_skills.py` → code 0, aucune sortie
- `npx --yes @biomejs/biome@2 format --verbose .` → 7 fichiers traités (`biome.json`, les deux
  `hooks.json`, les quatre `.ts`/`.d.ts` des mods), aucun hors de `files.includes` à part
  `biome.json`, « No fixes applied », code 0
- `claude plugin validate skills/mod-commun` → « Validation passed with warnings », code 0. Seul
  avertissement : `author` absent. `types ./types/index.d.ts declares on $: $.commande`.
- `claude plugin test skills/mod-commun` → **« no *.test.ts or *.test.tsx under …/skills/mod-commun »,
  code 1** (relancé sans tube : code 1 confirmé). Voir R1.
- `claude plugin validate skills/lexique` → « Validation passed with warnings », code 0.
  Avertissements : `author` absent, et `gating hook without .catch: agent.spawn` (voir R3).
- `claude plugin test skills/lexique` → 6 pass, 0 fail, code 0
- Recette `tsc` d'`OUTILLAGE.md`, `TY` = `skills/lexique/.claude-plugin/types` :
  - `M` = `skills/mod-commun` → code 0, aucune erreur ;
  - `M` = `skills/lexique` → code 0, aucune erreur. `--listFiles` confirme que `register.ts`,
    `register.test.ts` et `skills/mod-commun/types/index.d.ts` sont lus, et `--showConfig` que
    `strict` et `noUncheckedIndexedAccess` sont actifs.
- `/home/debian/.claude/.venv/bin/python -m pytest -q skills/lexique/scripts/tests` → 90 passés
- `uvx ruff check skills/lexique/scripts` → « All checks passed! »
- `uvx ruff format --check skills/lexique/scripts` → « 12 files already formatted »
- `uvx --with pytest basedpyright`, depuis `skills/lexique` → 0 errors, 0 warnings, 0 notes
- `uvx rumdl fmt --check` sur `OUTILLAGE.md`, `rules/claude-typescript-style.md`, les `SKILL.md`
  de `skill-convention`, `claude-code-mods`, `lexique` et `mod-commun` → « No issues found in 6
  files »
- Le `grep -rln lexique-sous-agent …` de l'Étape 6 → exactement les cinq fichiers attendus par le
  Plan : brief, Suivi, et les dettes `nom-du-mod-lexique-sous-agent-trop-etroit`,
  `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod`,
  `aucun-signal-quand-le-mod-lexique-ne-se-charge-pas`.
- `env -u CLAUDE_CODE_PLUGIN_DIRS claude -p --debug --model haiku …` sur ce dépôt (journal
  `debug/af4d0d88-….txt`) :
  - `hooks module lexique@skills-dir loaded … events: prompt.compose,agent.spawn` ;
  - `hooks module mod-commun@skills-dir loaded … events: engine.create` ;
  - `engine.create: $.commande (mod-commun: lancer)` (premier journal, `d57e2be5-….txt`) ;
  - `$.commande.lancer (lexique -> mod-commun) answered in 157.0ms` ;
  - aucune ligne `ERROR` de module.

  Le modèle répond `lexique=oui, mod-commun=non` à la question de la liste des skills.
- Dans `/home/debian/projects/claude-translator` :
  - `lexique session | head -1` et la session principale (`claude -p --model haiku`, question de la
    ligne « Lexique local de ») rendent la même ligne, « Lexique local de
    /home/debian/projects/claude-translator (/home/debian/projects/claude-translator/.claude/LEXIQUE.md) : » ;
  - `lexique-test-isole` → trois « absent » ;
  - `lexique-test-claude-md` et `lexique-test-injecte` → local annoncé par « Lexique local de
    /home/debian/projects/claude-translator (…) », premier terme Orchestrateur ; global, premier
    terme Gabarit ; règles, première puce « Un terme s'écrit avec une majuscule initiale ».

  C'est le relevé de référence consigné au Journal du 2026-10-06.
- Essais au banc, dans le scratchpad, sur une copie du module lexique, supprimée ensuite :
  - sans `$.commande` posé, `agent.spawn` et `prompt.compose` laissent l'événement intact, sans
    erreur ni ligne d'état ;
  - avec un `env.get` qui lève, de même.
- Recette `claude -p` de l'Étape 8, journal `outillage`, transcription d'un sous-agent : NON
  EXÉCUTÉE, Étape 8 non commencée.

### Conformité à l'intention

Critères de réussite du Suivi, identiques à ceux du Brief :

1. « `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` rend `0`, et `skills/lexique/mod/` n'existe
   plus » : **atteint, vérifié**.
2. « Le journal montre `lexique`, le mod commun et `outillage` chargés `@skills-dir`, et un appel
   `$.commande.lancer` de `lexique` et d'`outillage` » : **atteint pour `lexique` et `mod-commun`**,
   vérifié au journal. La partie `outillage` relève de l'Étape 8, pas encore faite.
3. « Pour chacun des trois mods : `validate` et `test` passent, `tsc` sans erreur, Biome rien à
   reformater » :
   - `lexique` : **atteint**, les quatre vérifiés ;
   - `mod-commun` : `validate`, `tsc` et Biome atteints, mais **`claude plugin test` non atteint
     tel qu'écrit, code 1** (R1) ;
   - `outillage` : Étape 8.
4. « En session réelle » :
   - les trois témoins rendent ce qu'ils rendaient avant : **atteint**, vérifié ;
   - la session principale porte la section du lexique local : **atteint**, vérifié ;
   - un sous-agent reçoit le rappel d'outillage : Étape 8.
5. « `grep -rn lexique-sous-agent` … ne rend rien » : en bonne voie. Il ne reste que les fichiers
   que le Plan attend jusqu'à la Clôture, et le critère se constate après elle.
6. « `agents/*.md` ne porte plus de règle d'outillage, et `check_pipeline.py` passe » :
   `check_pipeline.py` passe aujourd'hui ; le retrait des règles est l'Étape 9.
7. « `.claude/settings.json` n'a plus de hook `SessionStart` » : pas encore. Le hook
   `$HOME/.claude/hooks/outillage-rappel.sh` y est toujours, attendu jusqu'à l'Étape 8.
8. « `rules/claude-typescript-style.md` existe, `skill-convention` la cite ainsi que
   `claude-code-mods`, et `OUTILLAGE.md` dit comment lancer Biome » : **atteint, vérifié**. Ligne
   « Code TypeScript d'un mod » de la table de `skill-convention` ; section « Le TypeScript des
   mods » d'`OUTILLAGE.md`.
9. Les quatre dettes soldées : à la Clôture. La matière est en place pour deux d'entre elles :
   - `tsconfig-du-mod-etend-un-fichier-genere` : `.gitignore`, et `skills/lexique/mod/tsconfig.json`
     supprimé ;
   - `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod` : `lexique` est appelé par son
     nom, sans `HOME`.

**Hors-périmètre** : respecté :

- aucun hook `tool.call`, panneau, bandeau ni outil enregistré ;
- aucun Shadow-skill créé, `shadow-skills/` n'a que des modifications ;
- les dettes hors périmètre ne sont touchées que pour le renommage, constat intact ;
- le rappel d'outillage de la session principale n'est pas touché.

**Signaux de dérive** : aucun matérialisé :

- `CLAUDE_CODE_PLUGIN_DIRS` est absent de `settings.json` ;
- `lexique` n'a plus de `lancer` à lui : le seul `lancer` hors de `mod-commun` est le faux du test,
  que la convention prescrit ;
- le mod lexique ne fait que transporter : `if (!local) return composition`, aucun filtre ;
- aucun chemin `HOME` ajouté dans un `.ts` ni dans `settings.json`, qui a perdu une ligne
  `~/.claude` et n'en a gagné aucune ;
- aucun usage hors périmètre, aucun Shadow-skill neuf.

**Symptôme d'origine** : à moitié résorbé à ce stade, ce qu'on attend d'un audit intermédiaire.
`CLAUDE_CODE_PLUGIN_DIRS` a disparu, `lexique` et `mod-commun` se chargent seuls, et la convention
TypeScript existe. Le troisième mod reste à poser.

- **R1** — **`claude plugin test skills/mod-commun` sort en 1, et `claude-code-mods` dit qu'il sort
  en 0.**
  - **Trois sources disent autre chose que la commande.** La vérification de l'Étape 2 du Suivi
    est `claude plugin test skills/mod-commun`, et le critère 3 exige qu'elle passe pour chacun des
    trois mods. Le Journal ratifie que `mod-commun` n'a pas de test au banc, repli prévu au Plan,
    mais aucun critère n'en a été amendé. Or `shadow-skills/claude-code-mods/SKILL.md`, section
    « Tester », écrit : « et `claude plugin test` sur un mod sans `*.test.ts` sort en 0. »
  - **Constaté ici** : code 1, message « no *.test.ts or *.test.tsx under
    /home/debian/.claude/skills/mod-commun ».
  - **Conséquences** :
    - le critère 3 ne pourra pas être déclaré atteint à la Clôture tel qu'il est écrit ;
    - le Shadow-skill, autorité des mods, porte un fait faux, qu'un auditeur ou un agent suivant
      prendra pour une permission de compter ce test comme passant.
  - **Pour lever le point** :
    - une décision datée et ratifiée au Journal, qui restreint le critère 3 pour `mod-commun`
      (`test` remplacé par la vérification en session réelle, déjà pratiquée) ;
    - la phrase de `claude-code-mods` corrigée ;
    - la vérification de l'Étape 2 alignée.

  Ce choix revient à l'utilisateur, l'auditeur ne le tranche pas.

### Qualité du code

- **R2** — `skills/lexique/hooks/register.ts:18-19,33,47` — **une erreur avant `lancer` reste
  muette.** `projet($)` est évalué hors de `lancer`, donc hors de son `try`. Dans l'ancien module,
  la lecture de `CLAUDE_PROJECT_DIR` et de `cwd` était dans le `try` de `lancer`. Une exception de
  `$.env.get` ou de `$.session.cwd` n'est plus dite par `$.ui.status`. Au banc, le moteur l'absorbe
  et laisse l'événement intact, sans aucune ligne d'état. Cela contredit la convention que le
  Chantier vient d'écrire (`rules/claude-typescript-style.md`, « Un rappel échoue ouvert… attrape
  toute erreur, la dit par `$.ui.status` »), et l'en-tête du module (« ÉCHEC OUVERT : une commande
  qui échoue se dit sur la ligne d'état »). Même silence si `$.commande` manque, c'est-à-dire si
  `mod-commun` ne se charge pas : c'est le terrain de la dette
  `aucun-signal-quand-le-mod-lexique-ne-se-charge-pas` et de l'Étape 10, qui ne verra qu'un
  `dependencies` mal nommé, pas un module qui échoue au chargement. Probabilité faible, et le
  résultat reste fermé sur « rien versé » : réserve, pas bloquant.
- **R3** — `claude plugin validate skills/lexique` avertit `gating hook without .catch:
  agent.spawn`. `claude-code-mods` consigne l'avertissement comme attendu. L'ancien mod, lu sur
  `master`, n'avait pas de `.catch` non plus : l'avertissement n'est pas une régression propre
  (validate non relancé sur `master`). Mais la convention neuve dit d'un hook qui verse du contexte qu'il attrape toute erreur.
  À trancher avec R2 : soit un `try` qui couvre tout le hook, soit une phrase de la convention qui
  dit que l'absorption par le moteur suffit, ce que les deux essais au banc semblent établir.
- **R4** — `skills/mod-commun/hooks/register.ts:27-28` — le commentaire « Sous Python < 3.12, une
  commande du dépôt sort en 0 sans rien rendre » vient de l'ancien `lancer` du lexique, où il
  visait `lexique-cli.py`. Dans le module commun, générique, il parle d'un cas propre à une
  commande cliente. Il est aussi posé au-dessus du test `exitCode !== 0`, alors qu'il justifie le
  `|| undefined` deux lignes plus bas. Défaut de style mineur.
- **R5** — `biome.json` ajoute `arrowParentheses: "asNeeded"` et `assist.enabled: false`, que le
  Brief n'énumère pas (« guillemets simples, sans point-virgule, 2 espaces, largeur 100 »).
  `vcs.useIgnoreFile` est justifié au Journal, ces deux-là non. La convention les reprend (« et
  parenthèses du paramètre d'une flèche seulement là où ils sont requis »). C'est sans gravité,
  mais c'est un choix de format non ratifié : une ligne de Journal suffit.

Respect du style par ailleurs :

- les en-têtes de module, les JSDoc d'une ligne et les noms en français suivent la règle neuve ;
- Biome ne trouve rien à reformater ;
- les docstrings Python modifiées restent sous `ruff format`.

### Dette induite

- **R6** — **le lexique dépend désormais du `PATH` de la session.** Il lançait
  `python3 <chemin absolu>/lexique-cli.py`, il lance `lexique`, résolu par le `PATH` de la session.
  Une session ouverte hors d'un shell dont le `PATH` porte `bin/` n'a plus de lexique, par exemple
  depuis un lanceur graphique ou un IDE. L'échec est dit sur la ligne d'état, par `mod-commun`.
  C'est la décision du Journal, conforme à `OUTILLAGE.md` (« Ces commandes sont des liens de
  `bin/`, résolus par le `PATH` »), et le prix assumé du solde de la dette `HOME`. Ce coût n'est
  écrit qu'au Shadow-skill, entre parenthèses, et pas dans `skills/lexique/SKILL.md`, « Charger le
  mod ».
- **R7** — **environnement, non imputable au diff.** La session qui a lancé l'audit porte encore
  `CLAUDE_CODE_PLUGIN_DIRS=~/.claude/skills/lexique/mod` dans son environnement, hérité de
  `settings.json` à son ouverture. Tout `claude -p` lancé depuis elle journalise « Plugin path does
  not exist: …/skills/lexique/mod (ENOENT), skipping », et répète « Plugin loading errors ».
  Inoffensif, mais les preuves de journal de l'Étape 8 et de la Clôture sont à prendre sous
  `env -u CLAUDE_CODE_PLUGIN_DIRS` ou dans une session neuve. Sinon elles portent ces lignes, et un
  contrôle « sans ligne d'erreur de module » devient ambigu.

Aucune duplication introduite : le `lancer` du lexique a été retiré au profit de `mod-commun`, sans
copie.

### Bloquants

- **R1** — la vérification de l'Étape 2, `claude plugin test skills/mod-commun`, sort en 1. Le
  critère 3 du Suivi exige qu'elle passe, et `claude-code-mods` affirme qu'elle sort en 0.

## 2026-10-06 — intermédiaire — `62f2a4a`

**Verdict** : RÉSERVES

Périmètre jugé : les Étapes 1 à 6, cochées `[x]`, et la Retouche E6.1 (`62f2a4a`), qui répond à
l'audit précédent. Les Étapes 7 à 11 sont encore `[ ]` et ne sont pas reprochées. J'ai lu le
Brief, le Suivi, le Plan, `git diff master...mods-a-la-racine-des-skills` et
`git diff ff927cc 62f2a4a`.

La numérotation reprend à **R8** pour ne pas heurter les R1 à R7 de l'audit `ff927cc`, que le
Journal cite déjà.

Le bloquant précédent (R1) est levé. Les autres réserves, de R2 à R5, sont traitées. Il reste
pourtant un défaut dans la correction de R2 : le `.catch` dit qu'une erreur est survenue, mais pas
laquelle (**R9**). Aucun critère n'est en échec, aucune commande de vérification ne sort en erreur,
aucun Signal de dérive ne s'est matérialisé. D'où RÉSERVES, et non DÉFAVORABLE.

### Vérifications exécutées

Toutes les commandes sont lancées depuis `/home/debian/.claude`, sauf mention contraire, sous
Claude Code 2.1.291.

- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` → `0`.
- `test -e skills/lexique/mod` → absent.
- `grep -rnE 'HOME|~/\.claude' skills/*/hooks/*.ts skills/*/types/*.ts` → aucune ligne (code 1).
  Dans `settings.json`, le diff ne fait que retirer la ligne `CLAUDE_CODE_PLUGIN_DIRS`.
- `/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. »,
  9 contrôles verts, code 0.
- `python3 scripts/sante_skills.py` → code 0, aucune sortie.
- `npx --yes @biomejs/biome@2 format --verbose .` → 7 fichiers traités, « No fixes applied »,
  code 0.
- `claude plugin validate skills/mod-commun` → « Validation passed with warnings », code 0. Seul
  avertissement : `author` absent.
- `claude plugin test skills/mod-commun` → « no *.test.ts or *.test.tsx under … », code 1. C'est
  désormais ce que disent le critère 3 amendé, `claude-code-mods` et `skills/mod-commun/SKILL.md`.
- `claude plugin validate skills/lexique` → « Validation passed with warnings », code 0.
  - Seul avertissement : `author` absent.
  - `gating hook with .catch: agent.spawn` : l'avertissement R3 a disparu.
  - Appels relevés : `$.ui.status (via signaler)`.
- `claude plugin test skills/lexique` → 8 pass, 0 fail, code 0. La sortie complète, 14 lignes, ne
  porte aucun « hook was skipped » ni « the engine reported ».
- Essai de mutation dans le scratchpad, sur une copie du mod, supprimée ensuite : les deux `.catch`
  retirés, les deux tests neufs échouent (« Expected: 1, Received: 0 »). Ils observent donc bien le
  `.catch`.
- Sonde dans le scratchpad, sur une copie du test : la ligne d'état reçue vaut
  **`"lexique : [object Object]"`**. Le moteur rapporte « lexique's agent.spawn hook was skipped:
  lexique: no implementation for env.get ». Voir R9.
- Recette `tsc` d'`OUTILLAGE.md`, avec `TY` = `skills/lexique/.claude-plugin/types` :
  - `M` = `skills/mod-commun` → code 0 ;
  - `M` = `skills/lexique` → code 0.
- `/home/debian/.claude/.venv/bin/python -m pytest -q skills/lexique/scripts/tests` → 90 passés.
- `uvx ruff check skills/lexique/scripts` → « All checks passed! ».
- `uvx ruff format --check skills/lexique/scripts` → « 12 files already formatted ».
- `uvx --with pytest basedpyright`, depuis `skills/lexique` → 0 errors, 0 warnings, 0 notes.
- `uvx rumdl fmt --check` fichier par fichier → « No issues found » sur `OUTILLAGE.md`,
  `rules/claude-typescript-style.md` et les `SKILL.md` de `skill-convention`, `claude-code-mods`,
  `lexique` et `mod-commun`.
  - Le Suivi rend 2 issues : MD041, et MD013 à la ligne 125, un chemin de scratchpad insécable de
    la Passation de session 1.
  - Ce n'est pas du code livré : rien à signaler.
- `env -u CLAUDE_CODE_PLUGIN_DIRS claude -p --debug --model haiku` sur ce dépôt, journal
  `debug/1f10cfaa-….txt` :
  - `hooks module lexique@skills-dir loaded … events: prompt.compose,agent.spawn` ;
  - `hooks module mod-commun@skills-dir loaded … events: engine.create` ;
  - `engine.create: $.commande (mod-commun: lancer)` ;
  - `$.commande.lancer (lexique -> mod-commun) answered in 196.5ms` ;
  - aucun hook sauté ;
  - une seule ligne `ERROR`, « NON-FATAL: Lock acquisition failed », étrangère aux mods.
- Dans `/home/debian/projects/claude-translator`, après E6.1, toujours sous
  `env -u CLAUDE_CODE_PLUGIN_DIRS` :
  - `lexique session | head -1` rend la ligne « Lexique local de
    /home/debian/projects/claude-translator (/home/debian/projects/claude-translator/.claude/LEXIQUE.md) : ».
    La session principale (`claude -p --model haiku`) la recopie mot pour mot quand on lui demande
    la ligne « Lexique local de ». Avec la question littérale du Plan, « la première ligne du
    lexique local », elle rend `# Lexique local` : c'est l'ambiguïté que le Journal consigne déjà.
  - `lexique-test-isole` → trois « absent ».
  - `lexique-test-claude-md` et `lexique-test-injecte` rendent le relevé de référence :
    - local : « Lexique local de /home/debian/projects/claude-translator », premier terme
      Orchestrateur ;
    - global : premier terme Gabarit ;
    - règles : première puce « Un terme s'écrit avec une majuscule initiale ».
- NON EXÉCUTÉES, Étapes 7 à 11 non commencées :
  - la partie `outillage` des critères 2, 3 et 4 ;
  - `.claude/settings.json` sans `SessionStart` ;
  - le retrait des règles d'outillage des agents.

### Conformité à l'intention

Les critères de réussite sont ceux du Suivi. Seul le critère 3 diffère du Brief, amendé le
2026-10-06.

1. `CLAUDE_CODE_PLUGIN_DIRS` à `0` et `skills/lexique/mod/` absent : **atteint, vérifié**.
2. Journal `@skills-dir` et appel `$.commande.lancer` : **atteint pour `lexique` et `mod-commun`**,
   revérifié après E6.1. La partie `outillage` relève de l'Étape 8.
3. `validate`, `test`, `tsc` et Biome pour chaque mod :
   - `lexique` : **atteint**, les quatre vérifiés ;
   - `mod-commun`, critère amendé : `validate`, `tsc` et Biome sont **atteints**. La vérification
     de `lancer` en session réelle est consignée au Journal pour l'Étape 2, et le journal ci-dessus
     montre `lancer` servir `lexique` ;
   - `outillage` : Étape 8.
4. En session réelle :
   - les trois témoins sont inchangés : **atteint**, revérifié ;
   - la session principale porte la section : **atteint**, revérifié ;
   - le rappel d'outillage d'un sous-agent relève de l'Étape 8.
5. `grep -rn lexique-sous-agent` : inchangé depuis l'audit précédent. Le critère se constate après
   la Clôture.
6. `agents/*.md` sans règle d'outillage : Étape 9. `check_pipeline.py` passe aujourd'hui.
7. `.claude/settings.json` sans `SessionStart` : Étape 8.
8. La convention, sa citation et Biome dans `OUTILLAGE.md` : **atteint**. E6.1 n'a touché qu'à
   la règle d'échec ouvert.
9. Les dettes soldées : à la Clôture.

**Hors-périmètre** : respecté. E6.1 n'ajoute aucun hook `tool.call`, panneau, bandeau, outil
enregistré ni Shadow-skill. `signaler` n'est qu'un affichage de ligne d'état, au sein des deux
hooks existants.

**Signaux de dérive** : aucun ne s'est matérialisé.

- Aucun `lancer` propre au lexique : `signaler` ne lance rien.
- Aucun chemin `HOME`.
- Le mod continue de transporter sans filtrer.

**Symptôme d'origine** : même état qu'au précédent audit, attendu à mi-Chantier. Le troisième mod
reste à poser.

**Suite donnée à l'audit `ff927cc`** :

- **R1** : levé. Le critère 3 est amendé et daté dans le Suivi, qui fait foi. La vérification de
  l'Étape 2 est alignée. `claude-code-mods` et `skills/mod-commun/SKILL.md` disent « sort en
  **1** », conforme à la sortie constatée.
- **R2 et R3** : traités sur le fond, puisque l'erreur du hook est désormais rattrapée et
  `validate` n'avertit plus. Le message dit reste vide de sens : voir R9.
- **R4** : traité. Le commentaire est générique et posé au-dessus du `|| undefined` qu'il
  justifie.
- **R5** : consigné au Journal (`arrowParentheses`, `assist.enabled`).
- **R6** (dépendance au `PATH` de la session) : aucune suite au Journal.
  - `skills/lexique/SKILL.md` dit, ligne 56, que `lexique` est « résolu par le `PATH` ».
  - « Charger le mod » ne dit toujours pas qu'une session sans `bin/` au `PATH` n'a pas de
    lexique.
  - Réserve maintenue.
- **R7** (environnement) : toujours vrai. La session qui a lancé cet audit porte encore
  `CLAUDE_CODE_PLUGIN_DIRS`, d'où le `env -u` de chaque `claude -p` ci-dessus.

- **R8** — **L'amendement d'un critère du Brief ne se dit pas ratifié.** L'audit précédent
  laissait expressément à l'utilisateur le choix de lever R1.
  - Deux entrées du Journal portent la mention « ratifié par l'utilisateur » : la règle
    `git archive` et la dette `nom-du-mod-…`.
  - L'entrée « Critère 3 amendé pour `mod-commun` » ne la porte pas. L'entrée R5 ne la porte pas
    non plus.
  - Le Suivi fait foi et l'amendement y est daté : il est légitime en forme. Mais je ne peux pas
    établir que l'utilisateur l'a tranché. Si ce n'est pas le cas, R1 n'est levé que sur le papier.
    Invérifiable : réserve.

### Qualité du code

- **R9** — `skills/lexique/hooks/register.ts:24-25, 47, 61` — **la ligne d'état affiche
  `lexique : [object Object]`.** Le défaut :
  - Le `.catch` passe `next.error` à `signaler`.
  - Or `next.error` est un `HookFailure`, `{ kind, message?, budget }` d'après les types du moteur
    (`index.d.ts`, « Why a hook failed, as its `.catch` handler reads it on `next.error`: plain
    frozen data »). Ce n'est pas une `Error`.
  - `String()` en fait `[object Object]`, et `slice(0, 60)` ne change rien.
  - Le paramètre `erreur: unknown` de `signaler` laisse passer l'objet sans que `tsc` ne dise
    rien.

  Ce que dit la sonde : la ligne d'état reçoit exactement `"lexique : [object Object]"`, alors que
  le moteur connaît le motif (« no implementation for env.get »). L'utilisateur apprend que le
  lexique a échoué, pas pourquoi.

  Ce qui est contredit :
  - le Journal (« un `.catch` qui dit l'erreur ») ;
  - la convention neuve (« dit toute erreur par `$.ui.status` ») ;
  - le paragraphe ajouté à `claude-code-mods` (« il dit l'erreur »).

  Les deux tests neufs ne le voient pas. L'un affirme `startsWith('lexique')`, l'autre seulement
  `dits.length`.

  Côté sécurité, le résultat reste ouvert : l'événement passe intact. C'est une réserve à lever
  avant la Clôture, pas un bloquant. Il faut corriger le texte affiché et un test qui affirme le
  message.
- Le reste d'E6.1 suit le style des fichiers voisins :
  - en-tête de module complété ;
  - commentaire du « pourquoi » au-dessus de `signaler` ;
  - aides de test nommées en français (`ligneEtat`, `projetEnPanne`) ;
  - `as never` commenté, comme `SPAWN`.

### Dette induite

Rien de neuf dans E6.1. Le `.catch` est dupliqué sur les deux hooks, mais il est factorisé par
`signaler`, comme la convention le prévoit (« une fonction utilitaire ne sert qu'à éviter une
répétition entre deux hooks »). R6 reste ouverte, voir plus haut.

### Bloquants

Aucun.

## 2026-10-06 — clôture — `349bb96`

**Verdict** : RÉSERVES

Périmètre jugé : le Chantier entier, Étapes 1 à 11 toutes cochées `[x]`, de `d7ba6c4` à `349bb96`.
J'ai lu le Brief, le Suivi, le Plan (`.claude/plans/compressed-tinkering-hanrahan.md`),
`git diff master...mods-a-la-racine-des-skills` en entier, et `git diff 62f2a4a 349bb96` en détail.
La numérotation reprend à **R10**, après les R1 à R9 des deux audits intermédiaires.

Tous les critères vérifiables à ce stade sont atteints. Toutes les commandes de vérification passent
ou rendent ce que le Suivi attend. Aucun Signal de dérive ne s'est matérialisé, et le
Hors-périmètre est respecté. Deux critères ne se constatent qu'après le point 2 de la Clôture : le
solde des dettes et le `grep` de `lexique-sous-agent`. Leur matière est en place. Restent trois
réserves que l'utilisateur doit connaître : un cas d'entrée qui fait planter le contrôle de santé
(R10), une perte de portée du rappel d'outillage (R11), et la forme inversée d'un solde (R12).
D'où RÉSERVES.

### Vérifications exécutées

Toutes les commandes sont lancées depuis `/home/debian/.claude`, sauf mention contraire, sous
Claude Code 2.1.291. L'environnement de cet audit ne porte plus `CLAUDE_CODE_PLUGIN_DIRS`
(`env | grep` vide) : aucun `env -u` n'a été nécessaire.

- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` → `0`. `skills/lexique/mod` est absent.
- `.claude/settings.json` est absent du disque et de l'arbre de la branche. Sur `master`, il ne
  portait que le hook `SessionStart`. `.claude/settings.local.json`, non suivi, n'a pas de hook.
- `grep -cE 'ruff|basedpyright|pyright' agents/*.md` → `0` pour chacun des cinq agents.
  `grep -c 'git archive' agents/implementation-auditor.md` → `1`. `grep -nE
  'uvx|rumdl|\.venv|pytest|biome|npx|tsc'` sur `agents/*.md` ne rend rien.
- `/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. »,
  9 contrôles verts, code 0. Contrôle 9 : « 6 mention(s) de « pyright », toutes des
  interdictions ».
- `python3 scripts/sante_skills.py` → code 0, aucune sortie.
- `npx --yes @biomejs/biome@2 format --verbose .` → 10 fichiers traités : `biome.json` et le
  TypeScript et les `hooks.json` des trois mods. « No fixes applied », code 0.
- `claude plugin validate` → « Validation passed with warnings », code 0, pour chacun des trois
  mods. Seul avertissement : `author` absent.
  - `skills/mod-commun` : `types ./types/index.d.ts declares on $: $.commande`.
  - `skills/lexique` : `gating hook with .catch: agent.spawn`.
  - `.claude/skills/outillage` : `gating hook with .catch: agent.spawn` ; appels
    `$.commande.lancer, $.session.root, $.ui.status`.
- `claude plugin test`, sortie redirigée dans un fichier et code lu sans tube :
  - `skills/lexique` → 8 pass, 0 fail, code 0 ;
  - `.claude/skills/outillage` → 3 pass, 0 fail, code 0 ;
  - `skills/mod-commun` → « `no *.test.ts or *.test.tsx under …` », code 1. C'est ce que dit le
    critère 3 amendé.
- Recette `tsc` d'`OUTILLAGE.md`, `TY` = `skills/lexique/.claude-plugin/types` → code 0, aucune
  erreur, pour `skills/mod-commun`, `skills/lexique` et `.claude/skills/outillage`. `--listFiles`
  confirme que les `register.ts` et `register.test.ts` de chaque mod sont lus. `--showConfig`
  confirme que `strict` et `noUncheckedIndexedAccess` sont actifs.
- `/home/debian/.claude/.venv/bin/python -m pytest -q scripts/tests skills/lexique/scripts/tests`
  → 230 passés.
- `uvx ruff check scripts skills/lexique/scripts` → « All checks passed! ».
- `uvx ruff format --check scripts skills/lexique/scripts` → « 26 files already formatted ».
- `uvx --with pytest basedpyright` sur `scripts/sante_skills.py`, `scripts/check_pipeline.py`,
  `scripts/tests/test_sante_skills.py` et `scripts/tests/test_controle_9.py` → 12 erreurs
  `reportPrivateUsage`, toutes sur `_dependances`, aux lignes 145 à 246 de
  `test_sante_skills.py`. Les mêmes 12 apparaissent sur l'arbre de `master` extrait par
  `git archive` : elles préexistent, et les lignes ajoutées par le Chantier n'en portent aucune.
- `uvx rumdl fmt --check`, fichier par fichier → « No issues found » pour les 11 Markdown touchés
  hors Chantier : `OUTILLAGE.md`, la règle TypeScript, les deux fichiers de `skill-convention`,
  `claude-code-mods`, les `SKILL.md` de `lexique` et `mod-commun`, et quatre agents.
- `shadow-skill verifie` → code 0, aucune sortie.
- `grep -rln lexique-sous-agent …`, avec les exclusions de l'Étape 6 → exactement cinq fichiers :
  le brief, le Suivi et les trois dettes que la Clôture solde (`nom-du-mod-…`,
  `chemins-de-la-configuration-…`, `aucun-signal-…`).
- Session réelle sur ce dépôt : `claude -p --debug --model haiku`, avec un lancement de
  `lexique-test-isole`. Journal `debug/f070f2ee-801b-4077-b292-6ac880d212b8.txt` :
  - `hooks module order: dependencies register lexique@skills-dir, outillage@skills-dir,
    mod-commun@skills-dir` ;
  - les trois modules sont `loaded`, et `plugin.register` les dit `admitted` ;
  - `engine.create: $.commande (mod-commun: lancer); $ built for lexique,outillage,mod-commun,…` ;
  - `$.commande.lancer (lexique -> mod-commun) answered in 176.0ms` ;
  - `$.process.run (mod-commun): /home/debian/.claude/.claude/skills/outillage/scripts/rappel.sh
    … exited 0 in 18ms, 805 + 0 chars` ;
  - `$.commande.lancer (outillage -> mod-commun) answered in 20.9ms` ;
  - `agent.spawn lexique-test-isole: prompt rewritten by a hook` ;
  - une seule ligne `ERROR`, « NON-FATAL: Lock acquisition failed », étrangère aux mods. Aucun
    hook sauté.
- Transcription du sous-agent,
  `projects/-home-debian--claude/f070f2ee-…/subagents/agent-acd0ea04bce624ddc.jsonl`. Son premier
  message s'ouvre sur « Outillage de ce dépôt (/home/debian/.claude/OUTILLAGE.md) : ». Il porte
  les cinq puces, dont « `uvx ruff format <chemins>` » et la ligne Biome, puis `---`, puis
  « Fais ton constat. ». Le témoin rend trois « absent ».
- Dans `/home/debian/projects/claude-translator`, qui porte un `.claude/LEXIQUE.md` :
  - `lexique session | head -1` → « Lexique local de /home/debian/projects/claude-translator
    (/home/debian/projects/claude-translator/.claude/LEXIQUE.md) : » ;
  - la session principale, à qui l'on demande la ligne du prompt système qui commence par
    « Lexique local de », la recopie à l'identique ;
  - `lexique-test-isole` → trois « absent ». Sa transcription commence par « Fais ton
    constat. » : ni lexique, ni rappel d'outillage hors de ce dépôt ;
  - `lexique-test-claude-md` et `lexique-test-injecte` → local, premier terme Orchestrateur ;
    global, premier terme Gabarit ; règles, première puce « Un terme s'écrit avec une majuscule
    initiale ». Les deux nomment l'en-tête du local « # Lexique local », et non « Lexique local
    de … » comme au relevé de référence. Leurs transcriptions portent pourtant la ligne « Lexique
    local de /home/debian/projects/claude-translator (…) : » sous l'en-tête du mod. Le contenu
    reçu est le même, seule la formulation du modèle varie.
- Sondes dans le scratchpad, supprimées ensuite :
  - copie de HEAD par `git archive`, sur laquelle j'ai retiré le `name` de `mod-commun` et
    supprimé le module d'`outillage`. `python3 scripts/sante_skills.py` → code 1. Il nomme quatre
    défauts : module absent, `name` absent, et la dépendance `'mod-commun'` d'`outillage` et de
    `lexique` ;
  - copie du mod outillage, dont un test ne pose pas `$.commande` : la ligne d'état reçoit
    « outillage : undefined is not an object (evaluating '$.commande.lancer') », et le prompt passe
    intact. Un `mod-commun` qui ne se charge pas est désormais dit ;
  - `mods_en_defaut` sur un mod jouet dont `dependencies` porte un objet → `TypeError: unhashable
    type: 'dict'`. Voir R10 ;
  - session ouverte dans `skills/lexique/` : le journal `debug/01e83421-….txt` ne charge que
    `lexique` et `mod-commun`. `outillage` n'y apparaît pas. Voir R11 ;
  - projet git jetable dont `.claude/settings.json` porte un `SessionStart` qui écrit un marqueur :
    la session ouverte à sa racine le reçoit (« Oui. »), mais pas celle ouverte dans un
    sous-dossier (« Non. »).

### Conformité à l'intention

Les critères sont ceux du Suivi : le critère 3 y est amendé, l'amendement daté et ratifié.

1. `CLAUDE_CODE_PLUGIN_DIRS` à `0` et `skills/lexique/mod/` absent : **atteint, vérifié**.
2. Le journal montre `lexique`, `mod-commun` et `outillage` chargés `@skills-dir`, et un appel
   `$.commande.lancer` de `lexique` comme d'`outillage` : **atteint, vérifié**.
3. `validate`, `test`, `tsc` et Biome pour les trois mods : **atteint, vérifié**.
   - `lexique` et `outillage` passent les quatre commandes.
   - `mod-commun`, critère amendé, passe `validate`, `tsc` et Biome. `lancer` est vérifié en session
     réelle : le journal ci-dessus le montre servir deux clients, et `process.run` lui est
     attribué.
4. En session réelle : **atteint, vérifié**.
   - Les trois témoins rendent le relevé de référence. Pour deux d'entre eux, la formulation de
     l'en-tête varie, mais le contenu reçu est identique.
   - La session principale porte la ligne du lexique local.
   - Un sous-agent lancé sur ce dépôt reçoit le rappel, ligne `ruff format` comprise.
5. `grep -rn lexique-sous-agent` vide hors `done/`, audits et dettes soldées : **atteint pour tout
   ce que le Chantier pouvait toucher avant la Clôture**. Il reste le brief, le Suivi et trois
   dettes, que le point 2 de la Clôture déplace vers `technical-debt-solde/` et que l'archivage
   déplace vers `done/`. Le critère se constate après eux, comme le prévoit le Plan.
6. `agents/*.md` sans règle d'outillage, `check_pipeline.py` passe : **atteint, vérifié**. La règle
   `git archive` reste dans l'auditeur, écart ratifié au Journal.
7. `.claude/settings.json` sans hook `SessionStart` : **atteint**. Le fichier est supprimé, ce que
   le Plan prévoit quand il ne reste rien.
8. La règle TypeScript existe, `skill-convention` la cite avec `claude-code-mods` (ligne « Code
   TypeScript d'un mod »), et `OUTILLAGE.md` dit comment lancer Biome : **atteint, vérifié**.
9. Les quatre dettes du Brief, et la cinquième ratifiée, sont soldées : **à faire au point 2 de la
   Clôture**, qui suit cet audit. La matière de chacune est en place :
   - `aucun-signal-quand-le-mod-lexique-ne-se-charge-pas` : `sante_skills.py` contrôle les mods à
     la racine d'un skill et signale la variable si elle revient. La sonde l'établit en conditions
     réelles. La variable n'existe plus : la voie du « Pour solder » est donc transposée. La limite,
     un module qui échoue au chargement, est écrite dans la docstring et dans `claude-code-mods`.
     Elle est à reprendre dans la preuve du solde, comme le prévoit le Plan.
   - `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod` : aucun `HOME` dans un `.ts`, et
     la variable a quitté `settings.json`.
   - `tsconfig-du-mod-etend-un-fichier-genere` : `.gitignore` couvre `skills/*/tsconfig.json`, et
     `git ls-files | grep tsconfig` ne rend plus que le fichier de la dette.
   - `ruff-format-absent-des-agents` : soldée à l'inverse de son « Pour solder ». Voir R12.
   - `nom-du-mod-lexique-sous-agent-trop-etroit` : le plugin s'appelle `lexique`, la section
     `lexique:local`, et les dix fichiers cités sont renommés.

**Hors-périmètre** : respecté.

- Les lignes `+` du diff dans `*.ts` ne portent ni hook `tool.call`, ni panneau, ni bandeau, ni
  outil enregistré.
- `git diff --name-status master...HEAD -- shadow-skills/` ne rend que trois `M` : aucun
  Shadow-skill créé.
- Les dettes hors périmètre n'ont changé que de nom.
- `outillage` ne pose qu'`agent.spawn` : la session principale ne reçoit pas le rappel.

**Signaux de dérive** : aucun ne s'est matérialisé.

- `CLAUDE_CODE_PLUGIN_DIRS` est absent de `settings.json`. `sante_skills.py` le signalerait s'il y
  revenait.
- `lexique` et `outillage` n'appellent que `$.commande.lancer`. Les seuls `lancer` hors de
  `mod-commun` sont les faux des tests, que la convention prescrit.
- Les deux clients transportent seulement : ils préfixent le prompt si le texte est non vide, et
  le laissent intact sinon.
- Les lignes `+` du diff dans `*.ts`, `*.json` et `*.sh` ne portent ni `HOME`, ni `~/.claude`, ni
  `/home/debian`.
- Aucun usage hors périmètre, aucun Shadow-skill neuf.

**Symptôme d'origine** : disparu.

- `CLAUDE_CODE_PLUGIN_DIRS` n'existe plus. Les trois mods se chargent seuls depuis la racine de
  leur skill, et un quatrième n'ajouterait aucun réglage.
- Le code partagé passe par `$.commande`.
- `rules/claude-typescript-style.md` dit comment écrire, documenter, typer, formater et tester le
  TypeScript d'un mod.

**Suite donnée à l'audit `62f2a4a`** :

- **R8** : levé. Les entrées du Journal « Critère 3 amendé » et « `biome.json` porte
  `arrowParentheses` » disent désormais « écart ratifié par l'utilisateur ».
- **R9** : levé (E6.2). `signaler` lit `HookFailure.message ?? kind`. Les deux tests affirment le
  texte exact, « lexique : no implementation for env.get ». `outillage` suit le même motif, et
  son test affirme « outillage : no implementation for session.root ».
- **R6** (le lexique dépend du `PATH` de la session) : toujours ouvert, par choix de l'utilisateur
  consigné à la Passation. « Charger le mod », dans `skills/lexique/SKILL.md`, ne le dit toujours
  pas.
- **R7** (environnement hérité) : levé. La session de cet audit ne porte plus la variable.

### Qualité du code

- **R10** — `scripts/sante_skills.py`, `mods_en_defaut`, dernière boucle (`if dep not in noms`) :
  **une dépendance écrite en objet fait planter tout le contrôle de santé.**
  - `noms` est un `set`, et `_liste` laisse passer chaque élément de `dependencies` tel quel. Un
    élément non hachable, comme `{"name": "mod-commun"}` ou une liste, lève `TypeError: unhashable
    type: 'dict'`. Établi par la sonde ci-dessus.
  - `main()` n'attrape rien. Le hook `SessionStart` sort sur une trace Python, dont l'hôte n'affiche
    que la première ligne, « Traceback (most recent call last): ». Toutes les autres anomalies de
    la session sont perdues : `bin/`, venv, `PATH`.
  - C'est le chemin d'échec que la docstring du script veut fermer : « crie fort et une seule
    fois ». Le reste de la fonction est pourtant défensif : objet JSON vérifié, `name` vérifié
    comme chaîne.
  - Aucun mod du dépôt n'écrit cette forme, et je n'ai pas pu établir si Claude Code l'accepte.
    D'où une réserve, et non un bloquant. Il suffirait de comparer `str(dep)`, ou de signaler un
    élément qui n'est pas une chaîne, sans lever.
- Le reste du code neuf suit le style des fichiers voisins.
  - `outillage/hooks/register.ts` reprend l'en-tête en trois paragraphes du lexique, la JSDoc
    d'une ligne et le `.catch` qui dit `message ?? kind`. Faute d'un second hook, l'appel est en
    ligne plutôt que dans un `signaler`, ce qui est conforme à la règle « une fonction utilitaire ne
    sert qu'à éviter une répétition entre deux hooks ».
  - Son test reprend les aides du lexique (`commande`, `fond`, `ligneEtat`, `SPAWN` en `as
    never` commenté).
  - `rappel.sh` a un en-tête réécrit et exact : appelant, portée, racine quatre niveaux au-dessus,
    ligne Biome.
  - `check_pipeline.py` porte un commentaire du pourquoi, et `test_controle_9.py` teste les trois
    emplacements, plus un `.sh` hors emplacement ignoré.
  - Les tests de `sante_skills.py` couvrent une anomalie par cas, l'absence d'anomalie et le
    branchement dans `anomalies()`.

### Dette induite

- **R11** — **un sous-agent lancé depuis un sous-dossier du dépôt ne reçoit plus aucune règle
  d'outillage.**
  - Un mod de `.claude/skills/` ne se charge que si la session s'ouvre à la racine du dépôt. Ouverte
    dans `skills/lexique/`, la session liste bien `project=[/home/debian/.claude/.claude/skills]`
    pour les skills, mais ne charge pas `outillage`. Le journal `debug/01e83421-….txt` ne le nomme
    nulle part.
  - Avant le Chantier, `implementation-auditor` et `plan-reviewer` portaient `ruff`,
    `basedpyright` et l'interdit de `pyright` en dur, où que la session s'ouvre. Ils n'en reçoivent
    plus rien dans ce cas.
  - La session principale n'a rien perdu : la sonde montre qu'un `SessionStart` de
    `.claude/settings.json` ne s'exécutait pas non plus depuis un sous-dossier. Et
    `.claude/CLAUDE.md`, qui renvoie à `OUTILLAGE.md`, se charge en remontant.
  - Le Brief décide de retirer ces règles des agents : le principe est ratifié, mais cette borne ne
    l'est pas. Ni `OUTILLAGE.md` (« dans une session ouverte sur ce dépôt »), ni `claude-code-mods`,
    ni l'en-tête de `rappel.sh` ne disent qu'un sous-dossier n'en est pas une.
  - Coût futur : le mode de défaillance du 2026-09-09, trois audits sous `pyright`, redevient
    possible pour qui ouvre une session dans un skill. Le fait constaté a sa place dans
    `claude-code-mods`, et le cas au registre de dette si l'utilisateur ne le tranche pas.
- **R12** — **`ruff-format-absent-des-agents` se solde par l'inverse de son « Pour solder », et le
  rappel ne porte pas tout ce que la dette demandait.**
  - La dette voulait que l'auditeur lance `ruff format --check` et compte un fichier hors format
    comme un écart, et que `plan-reviewer` l'exige d'une vérification d'Étape sur du Python.
  - Le rappel versé aux deux agents dit `uvx ruff format <chemins>` « avant de commiter du
    Python ». C'est une consigne d'auteur, pas de juge, et elle ne vaut que dans une session ouverte
    à la racine (R11).
  - Le Brief décide ce solde, et le Plan en fixe la preuve : la ligne du rappel et la
    transcription. Le solde est donc légitime. Mais la section `## Soldé le` devrait dire ce qui
    n'est pas repris, plutôt que présenter la dette comme payée en entier. Il revient à
    l'utilisateur de juger si ce reste mérite une entrée.

Rien d'autre :

- aucune duplication, `lancer` n'existe qu'une fois ;
- aucune abstraction gratuite : `mod-commun` a deux clients ;
- aucun contournement laissé en place. `biome.json` et la recette `tsc` sont décrits une fois,
  dans `OUTILLAGE.md`, et cités ailleurs.

Le défaut du contrôle 7 noté au Journal reste à verser au registre, comme le prévoit la Passation.

### Bloquants

Aucun.
