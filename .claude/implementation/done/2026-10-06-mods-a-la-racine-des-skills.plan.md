# Plan — mods-a-la-racine-des-skills

Brief : `.claude/implementation/mods-a-la-racine-des-skills.brief.md` (validé).

## Contexte

Le mod lexique se charge par `CLAUDE_CODE_PLUGIN_DIRS`, qui nomme son dossier dans `settings.json`.
Chaque nouveau mod y ajouterait un chemin. Or un mod posé à la racine d'un dossier de skill se
charge seul (constaté en 2.1.291, `9060903`). Le Chantier :

- remonte le mod lexique à la racine de son skill et retire la variable ;
- crée un mod commun qui porte le code partagé entre mods ;
- réécrit le mod outillage pour s'en servir ;
- écrit la convention TypeScript, que l'utilisateur, qui n'écrit pas de TypeScript, ne peut pas
  écrire lui-même.

Rappel du Brief :

- **Critères** :
  - plus de `CLAUDE_CODE_PLUGIN_DIRS` ni de `skills/lexique/mod/` ;
  - les trois mods chargés `@skills-dir` et appelant `$.commande.lancer` ;
  - validate, test, `tsc` et Biome propres ;
  - témoins du lexique inchangés, et section du lexique local dans la session principale ;
  - un sous-agent reçoit le rappel d'outillage ;
  - plus de `lexique-sous-agent` ;
  - plus de règle d'outillage dans `agents/*.md` ;
  - plus de `SessionStart` dans `.claude/settings.json` ;
  - convention citée ;
  - quatre dettes soldées.
- **Hors-périmètre** : les autres usages des mods (garde de commit, rappels sur Edit, bandeau,
  outils natifs, Signal de dérive en direct) ; les autres dettes du mod lexique ; le rappel
  d'outillage à la session principale ; un nouveau Shadow-skill.
- **Signaux de dérive** :
  - `CLAUDE_CODE_PLUGIN_DIRS` qui reste ou revient ;
  - un mod avec son propre `lancer` ;
  - un mod qui décide au lieu de transporter ;
  - un chemin ancré sur le `HOME` dans un `.ts` ou `settings.json` — **ajouté par le diff** : les
    lignes `$HOME/.claude/…` que `settings.json` porte déjà (hooks, `statusLine`) n'en sont pas ;
  - un hook `tool.call`, un panneau, un bandeau ou un outil enregistré ;
  - un nouveau Shadow-skill.

## Écarts au Brief, ratifiés

Le Brief reste figé ; ces deux décisions de l'utilisateur, prises après sa validation, s'écrivent
dans le Suivi (`## Décisions`) à sa création.

- **`git archive` reste dans l'auditeur.** La règle de comparaison à la base reste dans
  `implementation-auditor.md` : c'est une méthode d'audit valable dans tout projet, que le mod
  outillage n'apporte qu'ici. Seules les règles propres à ce dépôt partent : `ruff`,
  `basedpyright`, `pyright` (dit, 2026-10-06).
- **Une cinquième dette est soldée.** `nom-du-mod-lexique-sous-agent-trop-etroit` est soldée par le
  renommage que le Brief décide (dit, 2026-10-06).

## Incertitudes levées

- **Emplacement du rappel** : `hooks/outillage-rappel.sh` devient
  `.claude/skills/outillage/scripts/rappel.sh`. Son seul appelant est le mod, et il voyage avec
  lui (dit, 2026-10-06).
- **Noms** : skill et plugin `mod-commun`, nom `$.commande` sur `$` (dit, 2026-10-06).
- **`PATH` d'un mod** : non tranché par lecture. L'Étape 4 le vérifie en session réelle avant tout
  autre changement du mod lexique (voir « Appel d'une commande par son nom »).
- **Mod outillage mis de côté** : il est réécrit à l'Étape 8 d'après ce Plan. La copie du
  scratchpad (`outillage-de-cote/outillage`) sert de référence si elle existe encore, sans en
  dépendre.

## Conception

### Mod commun (`skills/mod-commun/`)

- **`.claude-plugin/plugin.json`** : `name = "mod-commun"`, `"types": "./types/index.d.ts"`.
- **`types/index.d.ts`**, le contrat : `CommandeLancer = { argv; cwd?; env?; source }`, et
  `Commande = { lancer: (input: CommandeLancer) => Promise<string | undefined> }`, déclaré sur
  `EngineInterface`, avec une JSDoc d'une ligne par membre.
- **`hooks/register.ts`** : un hook `engine.create` qui ajoute `commande: { lancer }`. `lancer`
  reprend le comportement de la fonction `lancer` actuelle du mod lexique
  (`skills/lexique/mod/hooks/register.ts`) :
  - il lance `argv` par `built.process.run` ;
  - il rend le stdout débarrassé de ses blancs, ou `undefined` si la sortie est vide ;
  - un code non nul ou une exception s'affiche par `built.ui.status(`${source} : …`)`, et `lancer`
    rend alors `undefined`, sans jamais bloquer.
- **`SKILL.md`** : frontmatter `disable-model-invocation: true` et `user-invocable: false`, car le
  skill ne sert qu'aux mods. Il dit ce que `$.commande` fait et comment un mod l'appelle, et renvoie
  à `claude-code-mods` pour la mécanique.

### Tester un mod qui appelle `$.commande`

Le banc ne charge que le plugin testé, donc pas `mod-commun`. L'Étape 3 établit, avec un test
jetable, laquelle de ces voies simule `$.commande`, dans cet ordre :

1. un fond `on('commande.lancer', …)` dans le test ;
2. un hook `on('engine.create', …)` du test qui ajoute un faux `commande` ;
3. aucune. Les tests du client ne portent alors que sur ce qu'il fait sans `$.commande`, et son
   appel se vérifie en session réelle seule.

La voie retenue va dans la convention et dans `claude-code-mods`, et les Étapes 5 et 8 la suivent.

### Appel d'une commande par son nom

Le mod lexique appelle `lexique session` et `lexique sous-agent <type>` par le nom du lien de
`bin/`. C'est ce qui solde `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod`.

Cela suppose que le `PATH` du processus que lance un mod contient `bin/`, ce que l'Étape 4 vérifie
en premier. **Si le nom n'est pas trouvé, arrêter et revenir à l'utilisateur** : toute autre
résolution de la racine de la configuration est une décision qu'il n'a pas prise.

### `tsconfig.json` des mods

Il n'est plus versionné : `.gitignore` ignore `tsconfig.json` à la racine d'un skill qui porte un
mod. Cela solde `tsconfig-du-mod-etend-un-fichier-genere`, par la voie que la dette propose en
premier. `tsc` passe par la recette de `claude-code-mods`, avec un `tsconfig.json` temporaire hors
du mod :

```bash
R=$(git rev-parse --show-toplevel); T=$(mktemp -d)
TY="$R/<dossier .claude-plugin/types d'un mod déjà chargé>"   # chemins absolus : le
M="$R/<mod>"                                                  # tsconfig vit dans $T
printf '{"extends":"%s/tsconfig.json","compilerOptions":{"typeRoots":["%s"]},"include":["%s/hooks","%s/skills/mod-commun/types"]}' \
  "$TY" "$TY" "$M" "$R" > "$T/tsconfig.json"
npx --yes -p typescript@5 tsc -p "$T/tsconfig.json" --noEmit
```

Les types posés sous `skills/lexique/mod/.claude-plugin/types/` sont ignorés par git : ils sont
déplacés avec leur dossier par `mv`, non par `git mv`. Ils servent de `TY` pendant tout le Chantier.

### Biome

`biome.json` à la racine du dépôt contient :

- `files.includes` limité au TypeScript des mods : `skills/*/hooks/**`, `skills/*/types/**`,
  `.claude/skills/*/hooks/**`. Sans cette limite, Biome formaterait aussi le JSON du dépôt,
  `settings.json` compris ;
- les réglages du formateur : espaces, indentation 2, largeur 100, guillemets simples,
  `semicolons: "asNeeded"` ;
- `linter.enabled = false`, puisque le Brief ne retient que le formatage.

Il se lance par `npx --yes @biomejs/biome@2 format --write <chemins>`, et sans `--write` pour
vérifier.

## Modèle

**Opus** :

- de la prose pour moitié : convention, `SKILL.md`, `OUTILLAGE.md`, Shadow-skill, agents ;
- une incertitude du Brief que seule l'exécution tranche, le `PATH` d'un mod ;
- deux comportements non établis, le banc face à `$.commande` et un `SKILL.md` à côté d'un mod ;
- onze Étapes.

## Étapes

### 1. Convention TypeScript et Biome

`rules/claude-typescript-style.md` (neuf), `biome.json` (neuf), `OUTILLAGE.md`, `.gitignore`,
`shadow-skills/skill-convention/SKILL.md`.

- **La règle.** `rules/claude-typescript-style.md`, sur le modèle de
  `rules/claude-python-style.md`. Son `paths:` couvre `skills/*/hooks/**/*.ts`,
  `skills/*/types/**/*.ts`, `.claude/skills/*/hooks/**/*.ts` et `**/.claude/skills/*/hooks/**/*.ts`.
  - Ses sections reprennent les propositions acceptées au Brief : principe (le moins de TypeScript
    possible), typage, structure, documentation, tests, configuration (`tsconfig.json` non
    versionné, Biome).
  - La section Tests laisse la voie de simulation de `$.commande` à l'Étape 3.
  - Chaque règle cite l'endroit où elle est pratiquée ; une règle sans exemple encore est marquée
    « prescrite », comme dans la règle Python.
- **Biome.** Poser `biome.json` selon « Biome ».
- **`OUTILLAGE.md`.** Ajouter une ligne Biome au tableau des dépendances, et une section « Le
  TypeScript des mods » : Biome, la recette `tsc`, `claude plugin validate` et `claude plugin test`.
- **`.gitignore`.** Ajouter `skills/*/tsconfig.json` et `.claude/skills/*/tsconfig.json`.
- **`skill-convention`.** Ajouter une ligne « Code TypeScript d'un mod » à la table, qui cite la
  règle et `claude-code-mods`.

vérif :

- `npx --yes @biomejs/biome@2 format --verbose .` → aucune erreur de configuration, et aucun
  fichier traité hors de `files.includes` (aucun `.json` ni `settings.json`). À cette Étape, aucun
  mod n'est encore sous `skills/*/hooks/`, donc aucun fichier n'est traité. Le formatage réel se
  constate à l'Étape 2, sur le premier mod ;
- `/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py` ;
- `uvx rumdl fmt --check OUTILLAGE.md rules/claude-typescript-style.md shadow-skills/skill-convention/SKILL.md`.

### 2. Mod commun

`skills/mod-commun/{.claude-plugin/plugin.json,types/index.d.ts,hooks/hooks.json,hooks/register.ts,hooks/register.test.ts,SKILL.md}`
(neufs), `shadow-skills/claude-code-mods/SKILL.md`.

Selon « Mod commun ». Tests, en appelant `$['commande'].lancer(...)` sur un fond `process.run` :

- un stdout non vide → le texte, sans ses blancs ;
- un stdout vide → `undefined`, aucun `ui.status` ;
- un code non nul → `undefined`, un seul `ui.status`, qui commence par `source` ;
- `cwd` et `env` arrivent à `process.run`.

Si le banc n'exécute pas le `engine.create` du mod testé, le dire dans `claude-code-mods` et
tester `lancer` par la session réelle seule.

vérif :

- `claude plugin validate skills/mod-commun` et `claude plugin test skills/mod-commun` ;
- `npx --yes @biomejs/biome@2 format skills/mod-commun` → rien à reformater, puis la recette `tsc`
  avec `M` = `skills/mod-commun` ;
- `claude -p --debug --model haiku "Réponds OK." < /dev/null` : le journal montre
  `mod-commun@skills-dir` chargé et `engine.create: $.commande (mod-commun: lancer)`.

### 3. Tester un client de `$.commande`

`rules/claude-typescript-style.md`, `shadow-skills/claude-code-mods/SKILL.md`.

Établir « Tester un mod qui appelle `$.commande` ». Un client jetable, posé dans le scratchpad avec
son test, appelle `$.commande.lancer` et essaie les voies 1 puis 2 par `claude plugin test`. La
voie retenue, ou l'absence de voie (3), s'écrit dans la section Tests de la convention et dans
`claude-code-mods`. Le client jetable est supprimé.

vérif : la sortie de `claude plugin test <client jetable>`, citée dans le Journal du Suivi, montre
le test passant par la voie retenue, sans ligne « hook was skipped » dans « the engine reported » ;
`uvx rumdl fmt --check rules/claude-typescript-style.md shadow-skills/claude-code-mods/SKILL.md`.

### 4. Mod lexique à la racine de son skill

`skills/lexique/mod/` → `skills/lexique/{.claude-plugin,hooks}`,
`skills/lexique/.claude-plugin/plugin.json`, `settings.json`.

0. **Relever les témoins.** Avant tout changement, lancer les trois agents témoins du lexique dans
   un projet qui a un `.claude/LEXIQUE.md`, selon la recette de `claude-code-mods`, et citer leur
   sortie dans le Journal du Suivi : c'est la référence de « ce qu'ils rendaient avant ».
1. **Vérifier le `PATH`.** Avant de toucher au mod, une session
   `claude -p --debug --plugin-dir <mod jetable>` sur ce dépôt. Le mod jetable, posé dans le
   scratchpad, lance `["lexique", "chemin"]` par `$.process.run` à `session.start` et écrit le
   résultat dans un fichier. Rendu non nul ou introuvable → arrêt, voir « Appel d'une commande par
   son nom ».
2. **Déplacer.** `mv` du dossier `.claude-plugin`, types ignorés compris, et de `hooks/` vers
   `skills/lexique/`, puis `git rm --cached` de l'ancien emplacement et `git add` du nouveau.
   Supprimer `skills/lexique/mod/` et son `tsconfig.json`.
3. **Renommer le plugin** `lexique` dans `plugin.json`.
4. **`settings.json`** : retirer `CLAUDE_CODE_PLUGIN_DIRS` du bloc `env`.

Le module garde ici son code : sa réécriture est l'Étape 5.

vérif :

- `claude plugin validate skills/lexique` et `claude plugin test skills/lexique` ;
- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` → `0`, et `test ! -e skills/lexique/mod` ;
- `claude -p --debug --model haiku "Réponds OK." < /dev/null` : le journal montre
  `lexique@skills-dir` chargé ;
- `claude -p --model haiku "Le skill lexique est-il dans ta liste de skills ? Oui ou non." < /dev/null`
  → oui.

### 5. Module du lexique sur `$.commande`

`skills/lexique/hooks/register.ts`, `skills/lexique/hooks/register.test.ts`,
`skills/lexique/.claude-plugin/plugin.json`.

- **Le `lancer` local fait place à `$.commande.lancer`**, avec :
  - `argv: ['lexique', 'session']` et `['lexique', 'sous-agent', type]` ;
  - `env: { CLAUDE_PROJECT_DIR: projet }` ;
  - `source: 'lexique'`.
- **`plugin.json`** déclare `"dependencies": ["mod-commun"]`.
- **Renommer** l'`id` de la section en `lexique:local`.
- **L'en-tête du module** suit la convention.
- **Les tests** suivent la voie établie à l'Étape 3.
- **Formater** par Biome.

vérif :

- `claude plugin validate skills/lexique` et `claude plugin test skills/lexique` ;
- `npx --yes @biomejs/biome@2 format skills/lexique` et la recette `tsc` sur
  `skills/lexique/hooks` ;
- `grep -cE 'HOME|\.claude/skills' skills/lexique/hooks/register.ts` → `0` ;
- `claude -p --debug --model haiku "Réponds OK." < /dev/null` : le journal montre
  `$.commande.lancer (lexique -> mod-commun)`.

### 6. Renommage dans la documentation, témoins et session principale

`skills/lexique/SKILL.md`, `skills/lexique/scripts/lexique-cli.py`,
`skills/lexique/scripts/lexique.py`, `agents/lexique-test-claude-md.md`,
`agents/lexique-test-injecte.md`, `shadow-skills/claude-code-mods/SKILL.md`,
`.claude/implementation/todo/technical-debt/hook-sante-chemin-home.md`,
`.claude/implementation/todo/technical-debt/lexique-local-absent-sous-system-prompt.md`.

- **`SKILL.md` du lexique.** Les liens `mod/hooks/register.ts` deviennent `hooks/register.ts`. Le
  paragraphe « Charger le mod » dit que le mod est à la racine du skill et se charge seul, et qu'il
  appelle `lexique` par `$.commande`.
- **Le nom `lexique-sous-agent` → `lexique`** partout :
  - docstrings et aides de `lexique-cli.py` et de `lexique.py` ;
  - descriptions des deux agents témoins ;
  - mentions du Shadow-skill ;
  - les deux dettes ouvertes qui le citent, où seul le nom change, sans toucher au constat.

vérif :

- `grep -rln lexique-sous-agent . --exclude-dir={done,technical-debt-solde,projects,debug,file-history,jobs,backups,dev-mods,.rumdl_cache,.git,__pycache__,plans} --exclude='*.audit.md' --exclude=history.jsonl | grep -v '/.claude-plugin/types/'`
  → seulement les fichiers du Chantier (son brief et son Suivi) et les trois dettes qu'il solde à la
  Clôture (`nom-du-mod-…`, `chemins-de-la-configuration-…`, `aucun-signal-…`). Le même `grep` se
  relance après la Clôture : il ne rend plus rien (voir « Vérification de bout en bout ») ;
- `/home/debian/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests` ;
- `uvx ruff check skills/lexique/scripts` et `uvx ruff format --check skills/lexique/scripts` ;
- `scripts/check_pipeline.py` ;
- en session réelle, selon la recette de `claude-code-mods`, dans un projet qui a un
  `.claude/LEXIQUE.md` :
  - les trois agents témoins rendent ce que le relevé de l'Étape 4 (point 0) consigne au Journal ;
  - la session principale porte la section :
    `claude -p --model haiku "Recopie mot pour mot la première ligne du lexique local de ce projet que porte ton prompt système." < /dev/null`
    rend la première ligne de `lexique session`, lancé dans le même projet.

### 7. Contrôle 9 étendu aux scripts des skills

`scripts/check_pipeline.py`, `scripts/tests/test_controle_9.py` (neuf).

Le contrôle 9 (« pyright n'est cité que pour être écarté ») lit aussi `skills/*/scripts/*.sh` et
`.claude/skills/*/scripts/*.sh`, où le rappel va vivre. Tests sur une arborescence-jouet : un
`.sh` sous `.claude/skills/x/scripts/` qui cite `pyright` sans l'écarter fait échouer le
contrôle, et un qui l'écarte le laisse passer.

vérif :

- `/home/debian/.claude/.venv/bin/python -m pytest scripts/tests/test_controle_9.py` ;
- `uvx ruff check scripts`, `uvx ruff format --check scripts`, et `uvx --with pytest basedpyright`
  depuis la racine → aucune erreur sur les fichiers que l'Étape touche (des erreurs préexistent
  ailleurs : dette `basedpyright-treize-erreurs-non-tenues`) ;
- `scripts/check_pipeline.py`.

### 8. Mod outillage

`hooks/outillage-rappel.sh` → `.claude/skills/outillage/scripts/rappel.sh` ;
`.claude/skills/outillage/{.claude-plugin/plugin.json,hooks/hooks.json,hooks/register.ts,hooks/register.test.ts}`
(neufs) ; `.claude/settings.json` ; `shadow-skills/skill-convention/references/prose.md`.

- **Déplacer le rappel.** `git mv` du script, puis réécrire son en-tête :
  - il est appelé par le mod outillage au lancement d'un sous-agent, non plus par `SessionStart` ;
  - la racine du dépôt se calcule quatre niveaux au-dessus du script ;
  - la ligne de formatage cite Biome pour le TypeScript.
- **Le mod.** Un hook `agent.spawn` appelle `$.commande.lancer` avec :
  - `argv: [`${racine}/.claude/skills/outillage/scripts/rappel.sh`]`, où `racine` vient de
    `$.session.root()` ;
  - `cwd: racine` et `source: 'outillage'`.

  Il préfixe le prompt du texte rendu suivi de `---`, et le laisse intact sinon. `plugin.json`
  déclare `dependencies: ["mod-commun"]`. Les tests suivent la voie établie à l'Étape 3.
- **`.claude/settings.json`.** Retirer le hook `SessionStart`. S'il ne reste rien, supprimer le
  fichier.
- **`prose.md`.** Le lien « Pratiqué dans » du rappel qui échoue ouvert pointe vers le nouveau
  chemin.

vérif :

- `claude plugin validate .claude/skills/outillage`, `claude plugin test .claude/skills/outillage`,
  `npx --yes @biomejs/biome@2 format .claude/skills/outillage` → rien à reformater, et la recette
  `tsc` avec `M` = `.claude/skills/outillage` ;
- `scripts/check_pipeline.py`, contrôle 9 compris, qui lit désormais le rappel ;
- en session réelle (`claude -p --debug`), le sous-agent `lexique-test-isole` reçoit le rappel en
  tête de son prompt, ligne `ruff format` comprise. La preuve se lit dans la transcription du
  sous-agent, sous `projects/-home-debian--claude/<session>/subagents/`. Le journal montre
  `$.commande.lancer (outillage -> mod-commun)`.

### 9. Règles d'outillage hors des agents

`agents/implementation-auditor.md`, `agents/plan-reviewer.md`, `OUTILLAGE.md`,
`shadow-skills/skill-convention/references/prose.md`.

- **`implementation-auditor.md`.** Retirer les paragraphes « Les linters de ce dépôt… » et
  « N'appelle jamais `pyright`… », avec leur bloc de commandes. Garder « Comparer à la base… »
  (écart ratifié).
- **`plan-reviewer.md`.** Retirer la puce `pyright`.
- **`OUTILLAGE.md`.** Le paragraphe « Les sous-agents portent ces règles en dur » dit désormais
  que, dans ce dépôt, le mod outillage verse le rappel à chaque sous-agent. Seule la comparaison
  à la base reste recopiée dans l'auditeur, valable dans tout projet.
- **`prose.md`.** La section « Un sous-agent recopie ses règles » borne la recopie aux règles du
  contrat du pipeline et aux méthodes d'audit valables partout. L'outillage d'un dépôt arrive par
  un mod.

vérif :

- `grep -cE 'ruff|basedpyright|pyright' agents/implementation-auditor.md agents/plan-reviewer.md`
  → `0` pour chacun ;
- `grep -c 'git archive' agents/implementation-auditor.md` → `1` ;
- `scripts/check_pipeline.py` passe, contrôles 4 et 9 compris.

### 10. Signal quand un mod ne peut pas se charger

`scripts/sante_skills.py`, `scripts/tests/test_sante_skills.py`.

`anomalies()` contrôle chaque mod à la racine d'un skill, sous `skills/*/` et sous le
`.claude/skills/*/` du dépôt :

- `.claude-plugin/plugin.json` est un JSON lisible qui porte `name` ;
- `hooks/hooks.json` existe, et chaque module qu'il nomme existe ;
- chaque `dependencies` nomme un mod présent.

Le script signale aussi un `CLAUDE_CODE_PLUGIN_DIRS` resté dans `settings.json`. Tests sur une
arborescence-jouet : un par anomalie, et un pour l'absence d'anomalie. Ce que ce contrôle ne voit
pas, un module qui échoue au chargement, se dit dans le solde de la dette.

vérif :

- `/home/debian/.claude/.venv/bin/python -m pytest scripts/tests/test_sante_skills.py` ;
- `uvx ruff check scripts`, `uvx ruff format --check scripts`, et `uvx --with pytest basedpyright`
  depuis la racine → aucune erreur sur les fichiers que l'Étape touche (des erreurs préexistent
  ailleurs : dette `basedpyright-treize-erreurs-non-tenues`) ;
- `python3 scripts/sante_skills.py` → code 0, aucune sortie.

### 11. Shadow-skill `claude-code-mods`

`shadow-skills/claude-code-mods/SKILL.md`.

Consolider ce que les Étapes 2 à 10 y ont consigné au fil de l'eau :

- « Charger et vérifier un mod » : la racine d'un skill devient la voie de ce dépôt.
  `CLAUDE_CODE_PLUGIN_DIRS` n'est plus que la voie d'un mod hors d'un skill ;
- la recette `tsc` sans `tsconfig.json` versionné, écrite avec `git rev-parse --show-toplevel` et
  sans chemin ancré sur le `HOME` ;
- `$.commande` du mod commun, renvoyé à `skills/mod-commun/SKILL.md` ;
- la voie de test d'un client de `$.commande` ;
- un `SKILL.md` à côté d'un mod.

Faire passer de « Non essayé » à leur section ce que le Chantier a établi.

vérif :

- `shadow-skill verifie` ;
- `uvx rumdl fmt --check shadow-skills/claude-code-mods/SKILL.md` ;
- `grep -c lexique-sous-agent shadow-skills/claude-code-mods/SKILL.md` → `0` ;
- `scripts/check_pipeline.py`, contrôle 7 compris.

## Clôture

Les dettes se soldent à la Clôture, par `list-dir move` vers `technical-debt-solde/` puis un second
commit qui écrit leur preuve (`skills/implementation-tracker/references/dette.md#solder`) :

- `aucun-signal-quand-le-mod-lexique-ne-se-charge-pas` — Étape 10 ;
- `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod` — Étapes 4 et 5 ;
- `tsconfig-du-mod-etend-un-fichier-genere` — Étapes 1 et 4 ;
- `ruff-format-absent-des-agents` — Étapes 8 et 9. Son « Pour solder » attendait `ruff format`
  recopié dans les agents ; le Chantier le solde à l'inverse. La preuve est donc :
  - `grep -c 'ruff format' .claude/skills/outillage/scripts/rappel.sh` → au moins `1` ;
  - la transcription d'un sous-agent qui reçoit cette ligne ;
- `nom-du-mod-lexique-sous-agent-trop-etroit` — Étapes 4 à 6 (écart ratifié).

## Vérification de bout en bout

- `claude -p --debug --model haiku "Réponds OK." < /dev/null` sur ce dépôt. Le journal montre
  `lexique@skills-dir`, `mod-commun@skills-dir` et `outillage@skills-dir` chargés, sans ligne
  `ERROR` de module.
- Dans un projet qui a un `.claude/LEXIQUE.md` :
  - les trois témoins du lexique rendent ce que consigne le relevé de l'Étape 4 ;
  - la session principale porte la première ligne de `lexique session`.
- Un sous-agent lancé sur ce dépôt reçoit le rappel d'outillage.
- `scripts/check_pipeline.py`, `python3 scripts/sante_skills.py`, et pytest sur `scripts/tests` et
  `skills/lexique/scripts/tests`.
- Après l'archivage et le solde des dettes, le `grep` de l'Étape 6 ne rend plus rien : c'est là que
  le critère « plus de `lexique-sous-agent` » se constate.
