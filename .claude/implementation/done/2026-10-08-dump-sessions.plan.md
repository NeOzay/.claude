# Plan — dump-sessions

Brief : `.claude/implementation/dump-sessions.brief.md` (validé le 2026-10-08).
Shadow-skills : `skill-convention`.

## Contexte

L'utilisateur veut repérer les lourdeurs des discussions (« des textes à rallonge qui ne
m'apprennent pas grand-chose ») pour améliorer le pipeline des Chantiers. Ce Chantier ne fait que
**l'extraction** : une commande `/session-dump`, réservée à l'utilisateur, écrit un dump Markdown
par discussion d'un espace de travail, dans `<projet>/.claude/session-dump/<id>/`. Chaque dump a
un frontmatter TOML de statistiques et un corps qui ne garde que la discussion. L'analyse se fait
ailleurs (Hors-périmètre).

Rappels du brief qui bornent le plan :

- **Critères** : un dump par session principale, nommé `<date>-<nom>.md` ; frontmatter lisible par
  `tomllib` avec tokens (total et par type), coût, durée, tours ; corps sans résultat d'outil ni
  thinking, un appel d'outil par ligne ; skill à `disable-model-invocation: true` ; tests verts.
- **Hors-périmètre** : l'analyse, toute autre métrique, les résultats d'outils et le thinking.
- **Signal de dérive** : le diff interprète, classe ou analyse le contenu des sessions.

## Modèle

**Sonnet** : du code Python vérifiable par tests, 4 Étapes, et le Plan tranche toutes les
incertitudes du brief (ci-dessous).

## Incertitudes du brief, tranchées

| Incertitude | Décision | Source |
|---|---|---|
| `session-dump/` versionné ou ignoré | Ignoré ; la commande ne touche à aucun `.gitignore`. Ce dépôt ajoute `.claude/session-dump/` au sien, comme `projects/` ; le SKILL.md le rappelle pour les autres projets. | utilisateur, en plan |
| Portée de l'écrasement | Tout le répertoire `<id>/` : construit à côté, puis substitué à l'ancien. | utilisateur, en plan |
| Sessions sans `cost-state` (4/210) | Tokens recalculés depuis les transcriptions (principale + sous-agents) ; `cout_usd` et `[duree]` omis ; `mesure = "transcriptions"`. | plan |
| « nombre de tours » | Les messages saisis par l'utilisateur (prompts et commandes `/`), hors messages méta et résultats d'outils. | plan |

## Faits vérifiés qui fixent la conception

- **`<id>` = chemin absolu du projet, tout caractère non alphanumérique remplacé par `-`** :
  vérifié sur les 12 répertoires de `projects/` contre le `cwd` de leurs sessions.
- **Un message `assistant` est éclaté en plusieurs lignes JSONL de même `message.id`** (579 lignes
  pour 313 messages dans `06b2291d…`) : sommer l'`usage` ligne à ligne compterait double. Dédoublonner
  par `message.id`.
- **`cost-state` est cumulatif, la dernière ligne fait foi** (deux lignes identiques au coût près
  dans `06b2291d…`). Son `modelUsage` dépasse la somme principale + sous-agents (appels annexes :
  titres, classifieur) : c'est lui qui est cohérent avec `totalCostUSD`, donc **les tokens viennent
  de `modelUsage` quand `cost-state` existe**.
- **Titres** : `custom-title` (`customTitle`, donné par l'utilisateur) et `ai-title` (`aiTitle`),
  tous deux « last-wins » d'après le binaire 2.1.294. Ordre : dernier `custom-title`, sinon dernier
  `ai-title`, sinon l'UUID.
- `projects/` est déjà dans le `.gitignore` de ce dépôt.

## Conception

Nouveau skill global `skills/session-dump/`, sur le modèle de `skills/implementation-tracker/`
(`ruff.toml`, `pyrightconfig.json`, `scripts/tests/conftest.py` recopiés) :

```
skills/session-dump/
├── SKILL.md                        disable-model-invocation: true, argument-hint "[chemin du projet]"
├── ruff.toml, pyrightconfig.json
└── scripts/
    ├── session-dump-cli.py         garde de version, parse argv, appelle la bibliothèque, code de sortie
    ├── session_dump.py             lecture, statistiques, rendu — sans I/O hors des fonctions nommées
    └── tests/conftest.py, test_lecture.py, test_rendu.py, test_cli.py
bin/session-dump -> ../skills/session-dump/scripts/session-dump-cli.py
```

Seule la bibliothèque standard est utilisée (le TOML s'écrit à la main : scalaires et tables plates).
Le script n'a pas besoin du venv.

**Lecture** (`session_dump.py`) : une session = `projects/<id>/<uuid>.jsonl` (+ `<uuid>/subagents/*.jsonl`
pour le repli). Une ligne illisible est comptée et signalée sur stderr, jamais fatale. Le répertoire
des projets vient de `$CLAUDE_CONFIG_DIR`, à défaut `~/.claude`.

**Frontmatter** (champs plats, ordre fixe) :

```toml
session = "<uuid>"
titre = "<titre retenu>"
cree = 2026-10-08T09:12:44Z     # premier horodatage de la session
branches = ["master", "dump-sessions"]   # valeurs de gitBranch, dans l'ordre d'apparition
tours = 12
mesure = "cost-state"           # ou "transcriptions"
cout_usd = 38.24                # omis si mesure = "transcriptions"

[tokens]
total = 45372384
entree = 128766
sortie = 239447
cache_lu = 43941711
cache_cree = 1062460

[duree]                         # omise si mesure = "transcriptions"
totale_s = 93160
api_s = 2999
```

Les tokens de `modelUsage` sont additionnés sur tous les modèles. `thinkingTokens` n'a pas de
ligne : il est déjà compté dans `outputTokens`, donc dans `sortie` (280 061 en sortie dans les
transcriptions de `06b2291d…` contre 291 953 dans `modelUsage`). `total` est la somme des quatre
types.

`session`, `titre`, `cree` et `branches` identifient la session ; ce ne sont pas des métriques.
`branches` relie un dump à son Chantier sans rien interpréter.

**Corps** : la discussion, dans l'ordre, sous des titres `## Utilisateur` / `## Assistant` :

- le texte de l'utilisateur, débarrassé de ses blocs `<system-reminder>` ; une commande `/` rendue
  par `/<nom> <arguments>` ;
- le texte de l'assistant ;
- un appel d'outil par ligne, `` - `<Outil>` <cible> ``. La cible est `file_path` (Read, Edit,
  Write), `description` (Bash), `skill` (Skill), `subagent_type` et `description` (Agent), les
  `header` des questions (AskUserQuestion) ; à défaut, le nom seul ;
- exclus : résultats d'outils, thinking, messages méta (`isMeta`), attachments.

Conséquence à connaître : la réponse à un `AskUserQuestion` est un résultat d'outil, donc absente du
corps. Si l'utilisateur la veut, c'est une Retouche du format, que le brief prévoit.

**Nom** : `<date de cree, en UTC>-<titre en kebab-case>.md`, accents conservés, `/` et blancs remplacés
par `-`. En cas de collision, suffixe des 8 premiers caractères de l'UUID. Une session sans aucun tour
n'est pas une discussion : elle n'est pas dumpée, et le compte des sessions écartées s'affiche.

**CLI** : `session-dump [chemin]`. Le chemin, `.` par défaut, est résolu en absolu, puis traduit en
`<id>`. Chemin inexistant → sortie 2. Aucun `projects/<id>/` → sortie 1, avec le chemin attendu.
Écriture dans un répertoire temporaire voisin, puis substitution de `<projet>/.claude/session-dump/<id>/`
— un échec laisse l'ancien dump intact. La sortie nomme le répertoire et le nombre de dumps écrits.

## Étapes

1. **Lecture et statistiques** : `session_dump.py` (lecture JSONL tolérante, dédoublonnage par
   `message.id`, `cost-state` dernier, repli sur les transcriptions, titre, tours, branches), squelette
   du skill (`ruff.toml`, `pyrightconfig.json`, `conftest.py`), `test_lecture.py` sur des JSONL
   synthétiques — vérif : `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`
2. **Rendu** : frontmatter TOML et corps, nom de fichier et collisions, `test_rendu.py` (chaque
   frontmatter relu par `tomllib`, aucun `tool_result` ni `thinking` dans le corps, une ligne par
   appel, blocs `<system-reminder>` retirés) — vérif : même commande pytest
3. **Commande** : `session-dump-cli.py`, résolution chemin → `<id>`, écriture avec substitution du
   répertoire, sessions sans tour écartées, lien `bin/session-dump`, `test_cli.py` (écrasement d'un
   fichier périmé, chemin inexistant, `<id>` inconnu, échec d'écriture sans perte) — vérif : pytest,
   puis `command -v session-dump`
4. **Skill et branchement** : `SKILL.md` (`disable-model-invocation: true`, appel de la commande,
   rappel du `.gitignore`), entrée `.claude/session-dump/` au `.gitignore` du dépôt, essai réel —
   vérif : `session-dump && session-dump ~/projects/mdview`, puis le contrôle des vrais dumps
   ci-dessous (Vérification de bout en bout), puis `rm -r ~/projects/mdview/.claude/session-dump`
   — le `.gitignore` de ce dépôt-là ne l'ignore pas

Chaque Étape passe aussi `uvx ruff check skills/session-dump`, `uvx ruff format --check
skills/session-dump` et `uvx --with pytest basedpyright -p skills/session-dump`
(`OUTILLAGE.md`).

## Vérification de bout en bout

```bash
~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/
uvx ruff check skills/session-dump && uvx ruff format --check skills/session-dump
uvx --with pytest basedpyright -p skills/session-dump
session-dump && ls .claude/session-dump/-home-debian--claude/ | head
session-dump ~/projects/mdview && ls ~/projects/mdview/.claude/session-dump/-home-debian-projects-mdview/
git status --short .claude/session-dump ; echo "attendu : aucune sortie (ignoré)"
python3 - .claude/session-dump/-home-debian--claude/*.md <<'PY'
import sys, tomllib
for p in sys.argv[1:]:
    t = open(p, encoding="utf-8").read()
    _, fm, corps = t.split("+++\n", 2)
    d = tomllib.loads(fm)
    assert {"total", "entree", "sortie", "cache_lu", "cache_cree"} <= d["tokens"].keys(), p
    assert isinstance(d["tours"], int) and d["tours"] > 0, p
    if d["mesure"] == "cost-state":
        assert "cout_usd" in d and {"totale_s", "api_s"} <= d["duree"].keys(), p
    assert '"tool_result"' not in corps and '"thinking"' not in corps, p
print("ok", len(sys.argv) - 1)
PY
rm -r ~/projects/mdview/.claude/session-dump
```

Puis `/session-dump` invoqué dans une session : le modèle ne doit pas pouvoir l'appeler de lui-même
(`disable-model-invocation: true`), l'utilisateur oui.

## Relecture par plan-reviewer — RÉSERVES

**À arbitrer (Q1)** : les sessions sans aucun tour sont écartées (une sur 73 dans ce dépôt), alors
que le critère dit « un dump par session principale ». L'exclusion est absente du brief.

Corrigé sans arbitrage, défauts de rédaction : contrôle réel des dumps écrit en entier et étendu à
`cout_usd`, `[duree]` et au corps (Q2) ; `thinkingTokens` compté dans `sortie` et modèles additionnés,
dits (Q3) ; date du nom en UTC, comme `cree` (Q4) ; dump d'essai de `mdview` retiré après contrôle
(Q5) ; `total` de l'exemple rectifié (Q6).
