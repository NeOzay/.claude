# Plan — lexique-des-sous-agents

Brief : `.claude/implementation/lexique-des-sous-agents.brief.md` (validé). Entrée de road-map :
`lexique-des-sous-agents`.

## Contexte

Un sous-agent ne reçoit pas le hook `SessionStart`, donc jamais le lexique local d'un projet. Un
agent sans `omitClaudeMd` reçoit déjà `CLAUDE.md`, donc le lexique global et ses instructions ; un
agent à `omitClaudeMd: true` ne reçoit rien. Le Chantier ajoute un hook `SubagentStart` qui
complète ce que chaque agent personnalisé reçoit, selon son fichier, sans jamais écrire dedans.

Rappel du Brief :

- **Critères** : trois agents de test, lancés dans `/home/debian/projects/claude-translator`
  (qui a un `.claude/LEXIQUE.md`) — sans `omitClaudeMd` → reçoit le lexique local ;
  `omitClaudeMd: true` → ne reçoit aucun lexique ; `omitClaudeMd: true` + champ dédié → reçoit
  les lexiques global et local et leurs instructions.
- **Hors-périmètre** : le hook et ses scripts n'écrivent pas dans les fichiers d'agent ; aucune
  règle n'y est recopiée. Les agents intégrés (`Explore`, `Plan`, general-purpose) sont ignorés.
- **Signaux de dérive** : modifier `lexique session` ou le hook `SessionStart` ; ajouter un script
  hors de la skill `lexique` ; retoucher un agent existant de `agents/`.

## Incertitudes levées

- **Sortie de `SubagentStart`** : du JSON, pas un stdout brut. Le binaire 2.1.289 décrit
  « Exit code 0 - JSON additionalContext shown to subagent » et lit
  `hookSpecificOutput.additionalContext` au `case "SubagentStart"`. Entrée : le JSON commun
  (`session_id`, `cwd`…) plus `agent_id` et `agent_type` ; le matcher porte sur `agent_type`.
  Sortie attendue :
  `{"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": "<texte>"}}`.
- **Champ dédié** : `injectLexique: true` (dit). Il se lit comme le binaire lit `omitClaudeMd` :
  `true` ou `"true"` vaut oui, toute autre valeur non.
- **Dépôt de test** : `/home/debian/projects/claude-translator` (dit). Il porte aussi un agent de
  projet, `.claude/agents/analyste.md`, sans `omitClaudeMd`.
- **Agents de test** : versionnés dans `agents/` (dit).

## Conception

Tout vit dans la skill `lexique` : une fonction de bibliothèque, une sous-commande, une entrée de
`settings.json`. `annonce_session` est **réutilisée telle quelle**, pas modifiée.

### Règle d'injection (`lexique.py`)

1. **Trouver le fichier de l'agent** d'après `agent_type` : le premier `*.md` dont le
   frontmatter porte `name: <agent_type>`, cherché d'abord dans `<projet>/.claude/agents/`, puis
   dans `<racine_globale()>/agents/` — un agent de projet masque un agent utilisateur du même
   nom. Recherche récursive (`rglob`).
2. **Aucun fichier** (agent intégré, agent de plugin `x:y`) → chaîne vide.
3. **`omitClaudeMd` absent ou faux** → `annonce_session(global, local, projet)` : le lexique
   local et ses alertes, ou rien sans lexique local. Le global et les instructions arrivent
   déjà par `CLAUDE.md`.
4. **`omitClaudeMd: true` sans `injectLexique: true`** → chaîne vide : l'isolation.
5. **`omitClaudeMd: true` et `injectLexique: true`** → trois blocs, dans cet ordre :
   `<racine>/skills/lexique/instructions.md`, le lexique global (`<racine>/LEXIQUE.md`), puis
   `annonce_session(...)`. Chaque bloc s'ouvre sur une ligne qui nomme son fichier, comme
   l'en-tête « Lexique local de … » d'`annonce_session`. Un fichier illisible se dit dans son
   bloc, sans faire tomber les autres.

Le frontmatter d'un agent est du YAML ; la bibliothèque reste en stdlib seule (docstring de
`lexique.py`). Lecture minimale : les lignes `cle: valeur` en colonne 0 entre les deux premiers
`---`, guillemets ôtés. Elle ne sert qu'à `name`, `omitClaudeMd` et `injectLexique`, tous
scalaires.

Fonctions ajoutées, `annonce_*` à côté d'`annonce_session` :
`entete_agent(fichier) -> dict[str, str]`,
`fichier_agent(agent_type, projet, racine) -> Path | None`,
`annonce_sous_agent(agent_type, projet, racine) -> str`. `racine` est la racine de la
configuration globale ; la CLI passe `racine_globale()`, les tests un répertoire factice. Tout
s'en déduit : `<racine>/agents/`, `<racine>/LEXIQUE.md` (= `chemin_global()` quand
`racine = racine_globale()`), `<racine>/skills/lexique/instructions.md` ; le local est
`chemin_local(projet)`.

### Sous-commande `lexique sous-agent` (`lexique-cli.py`)

- Lit le JSON du hook sur stdin, en prend `agent_type`.
- Projet : `$CLAUDE_PROJECT_DIR` tel quel, sinon le répertoire courant — même règle que
  `session`, pour la même raison (monodépôt).
- Texte non vide → imprime le JSON `hookSpecificOutput` ci-dessus ; texte vide → rien.
- **Échoue ouvert**, comme `session` : sortie 0 quoi qu'il arrive, stdin illisible compris ; une
  exception va sur stderr. Un rappel n'empêche pas un sous-agent de démarrer. Le garde Python
  < 3.12 en tête du fichier sort aussi en 0 pour `sous-agent`.
- La docstring du module passe de « sept commandes » à huit, régime `sous-agent` décrit.

### Branchement (`settings.json`)

Une entrée `SubagentStart` sans matcher, qui lance
`python3 $HOME/.claude/skills/lexique/scripts/lexique-cli.py sous-agent` — même forme que
l'entrée `SessionStart` du lexique. Sans matcher : c'est le fichier de l'agent qui décide, pas
`settings.json`.

## Modèle

**Sonnet** : du code Python vérifié par des tests, un seul module et sa CLI, cinq Étapes, et
toutes les incertitudes du Brief tranchées ci-dessus.

## Étapes

### 1. Résolution de l'agent et règle d'injection

`skills/lexique/scripts/lexique.py`, `skills/lexique/scripts/tests/test_sous_agent.py` (neuf).

Ajouter `entete_agent`, `fichier_agent`, `annonce_sous_agent` selon « Règle d'injection ».
Tests, avec `tmp_path` comme projet et un répertoire factice passé en `racine` :

- agent introuvable → `""` ;
- agent sans `omitClaudeMd`, projet avec lexique local → le texte d'`annonce_session` ;
  sans lexique local → `""` ;
- `omitClaudeMd: true` seul → `""` ; `omitClaudeMd: "true"` lu comme vrai ;
- `omitClaudeMd: true` + `injectLexique: true` → instructions, global et local, dans l'ordre ;
  `injectLexique: false` → `""` ;
- agent de projet et agent utilisateur du même nom → celui du projet ;
- agent rangé dans un sous-répertoire de `agents/` → trouvé.

vérif : `/home/debian/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests` puis
`uvx ruff check skills/lexique/scripts`, `uvx ruff format --check skills/lexique/scripts` et
`uvx --with pytest basedpyright` (depuis `skills/lexique/`).

### 2. Sous-commande `lexique sous-agent`

`skills/lexique/scripts/lexique-cli.py`, `skills/lexique/scripts/tests/test_sous_agent.py`.

Selon « Sous-commande ». Tests en sous-processus, à la manière de `_session` dans
`test_session.py` (`CLAUDE_PROJECT_DIR` posé, stdin fourni) :

- agent qui reçoit du texte → code 0, stdout JSON parsable, `hookEventName` = `SubagentStart`,
  `additionalContext` non vide ;
- agent qui ne reçoit rien → code 0, stdout vide ;
- stdin qui n'est pas du JSON → code 0, stdout vide, message sur stderr.

vérif : mêmes commandes pytest, ruff check, ruff format --check et basedpyright qu'à l'Étape 1.

### 3. Branchement et documentation

`settings.json`, `skills/lexique/SKILL.md`, `skills/lexique/instructions.md`.

- `settings.json` : l'entrée `SubagentStart` de « Branchement ».
- `SKILL.md` : `sous-agent` dans le bloc de la commande et dans la liste des régimes d'échec ;
  la règle d'injection en quelques lignes, avec le champ `injectLexique` ; la description du
  frontmatter cite `sous-agent` parmi les sous-commandes. La section « Amorcer » dit que le
  lexique local va aussi aux sous-agents.
- `instructions.md` : la puce du lexique local dit qu'il est versé au démarrage de la session
  **et d'un sous-agent** — une proposition, pas plus : ce fichier se charge à chaque session.

vérif : `python3 -m json.tool settings.json >/dev/null && uvx rumdl fmt --check skills/lexique`.

### 4. Agents de test

`agents/lexique-test-claude-md.md`, `agents/lexique-test-isole.md`,
`agents/lexique-test-injecte.md` (neufs).

Trois agents témoins, sans outil, au prompt identique : rapporter, sans rien lire, ce que leur
contexte contient — un bloc « Lexique local de … » et son premier terme, le lexique global et
son premier terme, les règles du lexique et leur première règle —, ou dire « absent » pour
chacun. Frontmatter :

| Agent | `omitClaudeMd` | `injectLexique` | Attendu dans claude-translator |
|---|---|---|---|
| `lexique-test-claude-md` | — | — | local (par le hook), global et règles (par `CLAUDE.md`) |
| `lexique-test-isole` | `true` | — | rien |
| `lexique-test-injecte` | `true` | `true` | local, global et règles (par le hook) |

« Sans outil » se règle par le champ `tools` : vérifier à l'écriture la forme que le binaire
accepte pour une liste vide ; à défaut, `tools: Read` et la consigne de ne rien lire.

vérif, pour chacun des trois noms :
`echo '{"agent_type":"<nom>"}' | CLAUDE_PROJECT_DIR=/home/debian/projects/claude-translator lexique sous-agent`
— JSON avec le local seul ; rien ; JSON avec instructions, global et local.

### 5. Vérification réelle

Aucun fichier.

La session du Chantier ne peut pas l'ouvrir : l'Étape passe la main à l'utilisateur. Dans une
session neuve ouverte sur `/home/debian/projects/claude-translator` (pour charger le hook et les
agents), l'utilisateur lance les trois agents de test et compare leurs rapports au tableau de
l'Étape 4.

vérif : les trois rapports, recopiés au journal du Suivi.
