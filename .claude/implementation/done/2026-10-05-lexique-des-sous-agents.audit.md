---
slug: lexique-des-sous-agents
---

## 2026-10-05 — clôture — `6668faa`

**Verdict** : RÉSERVES

Lus : Brief (validé), Suivi (session 2, six Étapes cochées), Plan `.claude/plans/wiggly-growing-map.md`,
`git diff master...lexique-des-sous-agents` (18 fichiers, +902 −8). Le périmètre élargi aux mods
est daté et accepté au Suivi : il est jugé comme légitime.

### Vérifications exécutées

- `.venv/bin/python -m pytest skills/lexique/scripts/tests` → 87 passés, 0 échec (base extraite
  par `git archive master` : 69 passés ; +18, tous dans `test_sous_agent.py`)
- `uvx ruff check skills/lexique/scripts` → All checks passed
- `uvx ruff format --check skills/lexique/scripts` → 12 fichiers déjà formatés
- `uvx --with pytest basedpyright` (depuis `skills/lexique/`) → 0 erreur, 0 avertissement, 0 note
- `python3 -m json.tool settings.json` → valide (arbre de travail et `HEAD`)
- `uvx rumdl fmt --check skills/lexique` → aucun écart (2 fichiers) ; sur les trois agents de
  test → aucun écart
- Étape 4, `printf '{"agent_type":"<nom>"}' | CLAUDE_PROJECT_DIR=/home/debian/projects/claude-translator lexique sous-agent` :
  - `lexique-test-claude-md` → code 0, JSON `SubagentStart`, 13 094 caractères : le local seul
    (« Lexique local de … », premier terme `Orchestrateur`)
  - `lexique-test-isole` → code 0, sortie vide
  - `lexique-test-injecte` → code 0, JSON, 19 338 caractères : instructions, puis global
    (`Gabarit`), puis local (`Orchestrateur`), dans cet ordre
- `claude plugin validate skills/lexique/mod` (Claude Code 2.1.290) → passée avec un
  avertissement (`author` absent) ; le validateur note aussi « gating hook without .catch:
  agent.spawn » (voir R6)
- `claude plugin test skills/lexique/mod` → 3 passés, 0 échec
- Étape 6, refaite par l'auditeur : `claude -p` lancé dans `/home/debian/projects/claude-translator`
  **sans `--plugin-dir`** (le mod chargé par `CLAUDE_CODE_PLUGIN_DIRS` de `settings.json`, donc
  dans la configuration qui sera livrée), qui lance les trois agents de test :
  - `lexique-test-claude-md` → local (« Lexique local de /home/debian/projects/claude-translator »,
    `Orchestrateur`), global (« Contents of /home/debian/.claude/LEXIQUE.md », `Gabarit`), règles
    (« Contents of …/skills/lexique/instructions.md », première puce exacte)
  - `lexique-test-isole` → « absent » sur les trois lignes
  - `lexique-test-injecte` → local, global (« Lexique global (…) ») et règles (« Instructions du
    lexique (…) »), tous par le mod
- Transcription de cette session : le texte versé n'apparaît, côté session principale, que dans
  `toolUseResult.prompt` (métadonnée), pas dans le `tool_result` rendu au modèle : le contexte de
  l'Orchestrateur n'en paie pas le prix.

### Conformité à l'intention

- Critère « un sous-agent de test … montre qu'il a reçu ce lexique » : **atteint, vérifié** —
  exécution réelle ci-dessus, et le hook `SubagentStart` ayant été ôté, le mod est la seule voie
  par laquelle le local a pu arriver.
- Critère « un agent à `omitClaudeMd: true` … reste isolé » : **atteint, vérifié**.
- Critère « un agent à `omitClaudeMd: true` dont le champ dédié demande l'injection … reçoit les
  lexiques global et local et leurs instructions » : **atteint, vérifié**.
- Hors-périmètre : respecté. Ni le mod ni la CLI n'écrivent dans un fichier d'agent (le mod
  réécrit le `prompt` de l'appel, pas la définition) ; aucune règle n'est recopiée dans un agent ;
  les agents intégrés ne reçoivent rien (`Explore` → sortie vide, testé).
- Signaux de dérive :
  - « ajoute un script hors de la skill `lexique` » : non matérialisé, le mod est sous
    `skills/lexique/mod/`.
  - « retouche un agent existant de `agents/` » : non matérialisé, les trois fichiers de
    `agents/` sont neufs (`A` au `--name-status`).
  - « modifie `lexique session` ou le hook `SessionStart` » : non matérialisé sur le fond.
    - **R1** — `skills/lexique/scripts/lexique-cli.py:31`, la garde Python < 3.12 propre à
      `session`, est retouchée : `== ["session"]` devient `in (["session"], ["sous-agent"])`.
      Le comportement de `session` est inchangé, `_session` n'est pas touché, et l'entrée
      `SessionStart` de `settings.json` est intacte. L'écart est prescrit par le Plan (Q3) et
      arbitré au Journal : je le tiens pour légitime, mais le signal a été effleuré et
      l'utilisateur doit le savoir.
- Symptôme d'origine : disparu pour les agents qui ont un fichier. Un sous-agent personnalisé
  reçoit désormais le lexique local, complet, sans le plafond de 10 000 caractères.
- **R2** — `skills/lexique/mod/tsconfig.json` est toujours versionné à `HEAD`, alors que la
  « Prochaine action » du Suivi pose, avant la Clôture, une Retouche qui l'ôte et l'ignore. Il
  étend `./.claude-plugin/types/tsconfig.json`, que le moteur génère et qui s'ignore lui-même
  (`.gitignore` à `*`) : dans un clone neuf, la référence pointe dans le vide. La Retouche
  annoncée n'est pas faite.
- **R3** — L'arbre de travail porte une modification non commitée de `settings.json`
  (`"model": "opus"` → `"sonnet"`), étrangère au Chantier. Elle ne doit pas être emportée par
  l'aplatissement de Clôture.
- **R4** — `.gitignore` gagne `dev-mods/` (« dossier de rechargement à chaud de la session ») :
  lié à l'essai des mods, donc couvert par l'élargissement, mais le Journal ne le mentionne pas.
  Sans conséquence pour le résultat.

### Qualité du code

- **R5** — `skills/lexique/scripts/lexique.py:408` et `:410` — `omitClaudeMd` et `injectLexique`
  ne valent oui que sur la chaîne exacte `true` (guillemets ôtés). Le binaire, lui, lit
  `X === "true" || X === true` **après** analyse YAML : `omitClaudeMd: True` ou
  `omitClaudeMd: true  # isolé` font un agent isolé pour Claude Code, mais un agent « sans
  `omitClaudeMd` » pour `lexique sous-agent`, qui lui verse alors le lexique local. L'isolation
  est rompue en silence, sur un cas limite qu'aucun test ne couvre. Le Suivi affirme
  « `injectLexique` se lit pareil [que le binaire] » : c'est vrai pour `true` et `"true"`
  seulement.
- **R6** — `skills/lexique/mod/hooks/register.ts:19` — l'échec ouvert est voulu, mais il est
  muet sur son chemin le plus probable : CLI introuvable, Python trop ancien ou exception
  rattrapée par la CLI donnent un code ≠ 0 ou une sortie vide, et le mod rend `next(e)` sans rien
  dire ; seule une exception côté TypeScript passe par `$.ui.status`. Un mod qui cesse de verser
  le lexique ne se remarque qu'au résultat. Le validateur signale de plus l'absence de `.catch`
  sur ce hook bloquant (`agent.spawn`) : sans conséquence constatée, à trancher.
- **R7** — `skills/lexique/scripts/lexique-cli.py:16` (« c'est un hook `SubagentStart` ») et
  `:173` (aide « pour le hook SubagentStart ») décrivent un branchement qui n'existe plus : le
  hook a été ôté de `settings.json`, la commande est appelée par le mod. `SKILL.md:49` et `:74`
  ont été mis à jour, la CLI non : la documentation se contredit.

Le reste suit le style des voisins : docstring de module en régimes capitalisés, `annonce_*` à
côté d'`annonce_session`, échec ouvert calqué sur `_session`, `cast` commenté, tests
sous-processus à la manière de `test_session.py`.

### Dette induite

- **R8** — Le chemin de la configuration est ancré sur le `HOME` à deux endroits nouveaux :
  `register.ts:16` (`${home}/.claude/skills/lexique/scripts/lexique-cli.py`) et
  `CLAUDE_CODE_PLUGIN_DIRS` (`~/.claude/skills/lexique/mod`). C'est la forme de l'entrée
  `SessionStart` voisine, mais `OUTILLAGE.md` refuse cet ancrage pour les `.md` (contrôle 7) et
  le garde-fou ne lit pas le TypeScript. Coût : un déplacement de la configuration casse le mod
  sans bruit (cf. R6).
- **R9** — Les trois agents de test vivent dans `agents/`, donc au catalogue d'agents de chaque
  session, dans tous les projets. Choix de l'utilisateur, consigné au Journal : dette assumée,
  mais permanente — trois descriptions au contexte de chaque session, et un risque de
  lancement par erreur malgré leur mention « jamais pour une tâche ». À garder ou retirer
  sciemment à la Clôture.
- **R10** — Le lexique arrive par le `prompt` du sous-agent, pas par un contexte système : il
  précède la tâche dans le premier message, sous un en-tête qui le signale. Choix arbitré au
  Journal (`session.append` refusé à ce moment) et efficace (vérifié) ; il lie toutefois le
  mécanisme à l'API `agent.spawn`, encore jeune (premier mod du dépôt).

### Bloquants

Aucun.

## 2026-10-05 — clôture — `b3239f0`

**Verdict** : RÉSERVES

Deuxième audit de clôture, après la Retouche E6.2, qui traite les réserves R2, R4, R5, R6 et R7 de
l'audit du `6668faa`. Lus : Brief (validé), Suivi (session 2, six Étapes cochées), Plan
`.claude/plans/wiggly-growing-map.md`, `git diff master...lexique-des-sous-agents` (18 fichiers,
+976 −8), dont `git diff 6668faa b3239f0` (7 fichiers, +88 −14), relu ligne à ligne. Les numéros
`R<n>` de cette section sont les siens ; ceux de l'audit précédent sont cités « R<n> du `6668faa` ».

### Vérifications exécutées

- `.venv/bin/python -m pytest skills/lexique/scripts/tests` → 90 passés, 0 échec (base extraite
  par `git archive master` : 69 passés ; +21, tous dans `test_sous_agent.py`, qui compte 21 tests)
- `uvx ruff check skills/lexique/scripts` → All checks passed!
- `uvx ruff format --check skills/lexique/scripts` → 12 files already formatted
- `uvx --with pytest basedpyright` (depuis `skills/lexique/`) → 0 errors, 0 warnings, 0 notes ;
  base extraite : idem, aucune régression
- `python3 -m json.tool settings.json` → valide, sur l'arbre de travail et sur `HEAD`
- `uvx rumdl fmt --check skills/lexique` → No issues found in 2 files ; sur les trois agents de
  test → No issues found in 3 files
- Étape 4, `printf '{"agent_type":"<nom>"}' | CLAUDE_PROJECT_DIR=/home/debian/projects/claude-translator lexique sous-agent` :
  - `lexique-test-claude-md` → code 0, JSON `SubagentStart`, 13 094 caractères : le local seul
    (« Lexique local de … », premier terme `Orchestrateur`)
  - `lexique-test-isole` → code 0, sortie vide
  - `lexique-test-injecte` → code 0, JSON, 19 338 caractères : instructions, global (`Gabarit`),
    local (`Orchestrateur`), dans cet ordre
  - `Explore` → code 0, sortie vide
- `claude plugin validate skills/lexique/mod` (Claude Code 2.1.290) → passée, un avertissement
  (`author` absent), et la remarque « gating hook without .catch: agent.spawn »
- `claude plugin test skills/lexique/mod` → 4 passés, 0 échec (dont le test neuf « dit sur la
  ligne d'état que la commande échoue »)
- Étape 6, refaite : `claude -p` dans `/home/debian/projects/claude-translator`, sans
  `--plugin-dir` (le mod chargé par `CLAUDE_CODE_PLUGIN_DIRS` de `settings.json`, donc dans la
  configuration livrée), qui lance les trois agents de test :
  - `lexique-test-claude-md` → local (« Lexique local de /home/debian/projects/claude-translator »,
    `Orchestrateur`), global (`/home/debian/.claude/LEXIQUE.md`, `Gabarit`), règles (première
    puce exacte)
  - `lexique-test-isole` → « absent » sur les trois lignes
  - `lexique-test-injecte` → local, global (« Lexique global (…) »), règles (« Instructions du
    lexique (…) »), tous par le mod
- Lecture du frontmatter par Claude Code, dans le binaire 2.1.290 : `Bun.YAML.parse`, puis
  `Xe==="true"||Xe===!0` sur `omitClaudeMd` — la règle que `_valeur` dit reproduire.
- Cas limites de `entete_agent` / `annonce_sous_agent`, essayés sur des agents factices (voir R5) :
  `True`, `true # c`, `"true"`, espaces → isolé ; `"true"  # c`, `'true' # c` → **local versé**.

### Conformité à l'intention

- Critère « un sous-agent de test … montre qu'il a reçu ce lexique » : **atteint, vérifié** par
  l'exécution réelle ci-dessus ; le hook `SubagentStart` étant ôté de `settings.json`, le mod est
  la seule voie par laquelle le local a pu arriver.
- Critère « un agent à `omitClaudeMd: true` … reste isolé » : **atteint, vérifié**.
- Critère « un agent à `omitClaudeMd: true` dont le champ dédié demande l'injection … reçoit les
  lexiques global et local et leurs instructions » : **atteint, vérifié**.
- Hors-périmètre : respecté. Ni le mod ni la CLI n'écrivent dans un fichier d'agent ; aucune règle
  n'est recopiée dans un agent ; un agent intégré ne reçoit rien (`Explore` → sortie vide).
- Signaux de dérive :
  - « ajoute un script hors de la skill `lexique` » : non matérialisé (mod sous
    `skills/lexique/mod/`, élargissement daté au Suivi).
  - « retouche un agent existant de `agents/` » : non matérialisé, les trois fichiers sont neufs
    (`A` au `--name-status`).
  - « modifie `lexique session` ou le hook `SessionStart` » : non matérialisé sur le fond ;
    `_session`, `annonce_session` et l'entrée `SessionStart` de `settings.json` sont intacts.
    - **R1** — `skills/lexique/scripts/lexique-cli.py:31` — la garde Python < 3.12, propre à
      `session`, reste élargie à `sous-agent` (R1 du `6668faa`). Prescrite par le Plan (Q3),
      arbitrée au Journal : légitime, mais le signal a été effleuré.
- Symptôme d'origine : disparu pour les agents qui ont un fichier ; le local arrive complet, sans
  le plafond de 10 000 caractères.
- Réserves du `6668faa` levées : **R4** (`dev-mods/` consigné au Journal) ; **R7** pour la CLI
  (docstring et aide citent le mod) — voir R7 ci-dessous pour ce qui reste.
- **R2** — `settings.json` porte toujours, non commitée, la modification `"model": "opus"` →
  `"sonnet"` (R3 du `6668faa`), étrangère au Chantier. Elle ne doit pas partir avec
  l'aplatissement de Clôture.
- **R3** — `skills/lexique/mod/tsconfig.json` reste versionné (R2 du `6668faa`), par choix de
  l'utilisateur consigné au Journal. Le constat de fond demeure : il étend
  `./.claude-plugin/types/tsconfig.json`, que le moteur génère et qui s'ignore lui-même (`*`) ;
  dans un clone neuf, la référence pointe dans le vide jusqu'à la première génération. Dette
  assumée, pas défaut.
- **R4** — Le Suivi committé à `HEAD` a pour « Prochaine action » « commiter la Retouche E6.2 »,
  déjà faite par ce commit, et pour « Dernier audit » le `6668faa`. À remettre à jour avec le
  verdict de cet audit avant la Clôture.

### Qualité du code

- **R5** — `skills/lexique/scripts/lexique.py:366` (`_valeur`) — R5 du `6668faa` n'est levée
  qu'en partie. Une valeur entre guillemets **suivie d'un commentaire** ne passe ni par la branche
  « guillemets » (le dernier caractère est celui du commentaire) ni par la comparaison à `true`
  (le commentaire ôté, il reste `"true"` guillemets compris). Essai :
  `omitClaudeMd: "true"  # isolé` et `omitClaudeMd: 'true' # isolé` → `entete_agent` rend
  `'"true"'` et `"'true'"`, et `annonce_sous_agent` **verse le lexique local**. Claude Code, lui,
  analyse le YAML (`Bun.YAML.parse`) : il obtient la chaîne `"true"`, et isole l'agent. L'isolation
  est donc encore rompue en silence, sur une forme plus rare que celle de l'audit précédent. Même
  mécanisme sur `name: "x"  # c` : l'agent n'est pas trouvé, et un agent qui devait recevoir le
  local ne reçoit rien. `SKILL.md:112` affirme sans réserve « un commentaire de fin de ligne est
  ignoré » ; `test_entete_lit_le_yaml_comme_claude_code` couvre `'x # y'` (le `#` dans les
  guillemets), pas les guillemets suivis d'un commentaire.
- **R6** — `skills/lexique/mod/hooks/register.ts:26` — R6 du `6668faa` levée en partie : un code
  de sortie non nul se dit désormais sur la ligne d'état (essayé par `claude plugin test`). Mais
  le commentaire nomme « Python trop ancien » parmi les cas couverts, et le test neuf simule ce
  cas par un code 2 et le stderr `python trop ancien` (`register.test.ts:76`) : or la garde de
  `lexique-cli.py:31` fait sortir `sous-agent` en **0, sans un mot**, sous Python < 3.12. Ce cas
  reste muet, et le test éprouve un scénario que la CLI ne produit pas. Reste muet aussi une
  exception rattrapée par `_sous_agent` (code 0, stdout vide, message sur stderr, que le mod ne
  lit pas). La remarque `.catch` du validateur est en revanche sans objet : les types du moteur
  disent qu'un hook en échec est sauté et que la suite s'exécute, soit l'échec ouvert voulu. Par
  ailleurs, `$.ui.status` épingle la ligne « jusqu'au prochain appel » : un échec reste affiché
  toute la session, même si les lancements suivants réussissent — acceptable, mais non dit.
- **R7** — `agents/lexique-test-claude-md.md:3` (« doit recevoir le local par le hook
  SubagentStart ») et `agents/lexique-test-injecte.md:3` (« doit recevoir par le hook les règles,
  le global et le local ») décrivent un branchement qui n'existe plus — reste de R7 du `6668faa`,
  que la Retouche a corrigé dans la CLI mais pas ici. Ces descriptions entrent au catalogue
  d'agents de chaque session.

Le reste de la Retouche suit le style des voisins : `_valeur` documentée en une docstring qui dit
pourquoi, regex nommée et commentée à côté de `_CHAMP`, tests au même gabarit que leurs voisins,
docstring de module mise à jour.

### Dette induite

- **R8** — Ancrage sur le `HOME` (R8 du `6668faa`), inchangé : `register.ts:16` et
  `CLAUDE_CODE_PLUGIN_DIRS`. Un déplacement de la configuration casse le mod — bruyamment
  désormais (fichier introuvable → code 2 → ligne d'état), ce qui en réduit le coût.
- **R9** — Les trois agents de test au catalogue de chaque session (R9 du `6668faa`), inchangé.
- **R10** — Le lexique passe par le `prompt` via `agent.spawn` (R10 du `6668faa`), inchangé.
- **R11** — `entete_agent` lit le YAML par regex : dette consignée au Journal, à verser au
  Registre à la Clôture. R5 en est le premier coût concret : chaque forme YAML non prévue est un
  écart silencieux avec Claude Code, et c'est sur `omitClaudeMd` qu'il coûte le plus. R8 à R10
  sont eux aussi annoncés « à verser » ; aucun n'est encore au Registre.

### Bloquants

Aucun. Les trois critères du Brief sont atteints et vérifiés par exécution réelle ; R5 est un
défaut de correction sur une forme rare du frontmatter, qui n'invalide pas le résultat mais rompt
l'isolation en silence quand elle se présente : à corriger ou à documenter avant de clore.
