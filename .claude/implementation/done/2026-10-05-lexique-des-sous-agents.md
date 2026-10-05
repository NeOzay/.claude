+++
gabarit = "suivi"
slug = "lexique-des-sous-agents"
titre = "Donner les lexiques et leurs règles aux sous-agents"
branche = "lexique-des-sous-agents"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "sonnet"
plan = ".claude/implementation/done/2026-10-05-lexique-des-sous-agents.plan.md"
brief = ".claude/implementation/done/2026-10-05-lexique-des-sous-agents.brief.md"
audit = ".claude/implementation/done/2026-10-05-lexique-des-sous-agents.audit.md"
road-map = "lexique-des-sous-agents"
skills = ["skill-convention"]
"créé" = 2026-10-05
maj = 2026-10-05
+++

## Objectif et périmètre

**Symptôme** : un sous-agent peut employer un terme hors de sa définition sans le savoir ; c'est
« plus une question d'uniformisation, destinée au Subagent utilisé dans les Chantiers ».

**But** : tout sous-agent personnalisé qui reçoit `CLAUDE.md` reçoit aussi le lexique local ; et
un sous-agent qui porte `omitClaudeMd: true`, quand les lexiques lui sont pertinents, peut
recevoir les lexiques et leurs instructions.

**Critères de réussite** :

- Un sous-agent de test, lancé dans un dépôt existant qui a un lexique local
  (`.claude/LEXIQUE.md`), montre qu'il a reçu ce lexique.
- Un agent de test à `omitClaudeMd: true`, lancé dans le même dépôt, montre qu'il reste isolé :
  aucun lexique ne lui parvient.
- Un agent de test à `omitClaudeMd: true` dont le champ dédié demande l'injection, lancé dans le
  même dépôt, montre qu'il a reçu les lexiques global et local et leurs instructions.

**Hors-périmètre** :

- Écrire dans les fichiers des sous-agents : ni le hook ni ses scripts n'y touchent, et les règles
  n'y sont pas recopiées ; la demande d'injection y est posée à la main par l'auteur de l'agent.
- Les agents intégrés, sans fichier : `Explore`, `Plan`, general-purpose.

**Élargissement du 2026-10-05** (accepté par l'utilisateur, Journal) : le hook `SubagentStart` de
`settings.json` ne livre pas plus de 10 000 caractères ; le Chantier ajoute un **mod** (plugin de
function hooks de Claude Code) qui verse le lexique à un sous-agent sans ce plafond, et qui sert
aussi à éprouver cette nouveauté. Le mod réutilise `lexique sous-agent` : il ne porte aucune règle.
Les Signaux de dérive « script hors de la skill `lexique` » ne vaut plus pour ce mod, rangé dans
`skills/lexique/`.

**Signaux de dérive** :

- Le diff modifie la sous-commande `lexique session` ou le hook `SessionStart`.
- Le diff ajoute un script hors de la skill `lexique`.
- Le diff retouche un agent existant de `agents/`.

## Étapes

- [x] 1. Résolution de l'agent et règle d'injection — `skills/lexique/scripts/lexique.py`,
      `skills/lexique/scripts/tests/test_sous_agent.py` — vérif:
      `.venv/bin/python -m pytest skills/lexique/scripts/tests && uvx ruff check skills/lexique/scripts && uvx ruff format --check skills/lexique/scripts && (cd skills/lexique && uvx --with pytest basedpyright)`
- [x] 2. Sous-commande `lexique sous-agent` — `skills/lexique/scripts/lexique-cli.py`,
  `skills/lexique/scripts/tests/test_sous_agent.py` — vérif: même commande qu'à l'Étape 1
- [x] 3. Branchement et documentation — `settings.json`, `skills/lexique/SKILL.md`,
  `skills/lexique/instructions.md` — vérif:
  `python3 -m json.tool settings.json >/dev/null && uvx rumdl fmt --check skills/lexique`
- [x] 4. Agents de test — `agents/lexique-test-claude-md.md`, `agents/lexique-test-isole.md`,
      `agents/lexique-test-injecte.md` — vérif:
      `echo '{"agent_type":"<nom>"}' | CLAUDE_PROJECT_DIR=/home/debian/projects/claude-translator lexique sous-agent`,
      pour chacun des trois noms
- [x] 5. Mod `lexique-sous-agent` — `skills/lexique/mod/` — vérif:
  `claude plugin validate skills/lexique/mod && claude plugin test skills/lexique/mod`
- [x] 6. Vérification réelle, par l'utilisateur, dans une session neuve sur
  `/home/debian/projects/claude-translator` lancée par
  `claude --plugin-dir ~/.claude/skills/lexique/mod` — aucun fichier — vérif: les trois
  rapports d'agent, recopiés au Journal

## État courant

**Prochaine action** : Clôture en cours — dette versée, road-map sortie ; reste
`commit-chantier cloture` (message, dry-run, accord). **Vérification** :
`.venv/bin/python -m pytest skills/lexique/scripts/tests` **Dernier audit** : b3239f0 — RÉSERVES —
2026-10-05 **Notes** : format de `SubagentStart` vérifié dans le binaire 2.1.289 — sortie JSON
`hookSpecificOutput.additionalContext`, entrée `agent_type`.

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien.

**À savoir** :

- Format du hook, lu dans le binaire 2.1.289 : entrée JSON avec `agent_type` ; sortie
  `{"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": "…"}}`, code 0 ;
  le binaire tient `omitClaudeMd` pour vrai sur `true` ou `"true"`, et `injectLexique` se lit
  pareil.
- `annonce_session` se réutilise sans retouche : le Signal de dérive porte sur `lexique session`.
- Dans ce dépôt, le local est le global (`_est_le_global`) : un essai du hook ici ne verse aucun
  lexique local. Tester avec `CLAUDE_PROJECT_DIR=/home/debian/projects/claude-translator`, dont le
  lexique commence par `Orchestrateur` et qui porte un agent de projet, `analyste`, sans
  `omitClaudeMd`.
- Le frontmatter des agents est du YAML ; `lexique.py` reste en stdlib seule : lecture `cle: valeur`
  en colonne 0, rien de plus.

## Journal de décisions

- **2026-10-05** — Champ `injectLexique: true`, lu comme `omitClaudeMd`. Agents de test versionnés
  dans `agents/`, à `tools: Read` et consigne de ne rien lire. *Pourquoi* : choix de l'utilisateur ;
  le binaire ne dit pas ce qu'un `tools:` vide donne. *Rejeté* : `lexiques: true` ; agents
  temporaires ; `tools:` vide.
- **2026-10-05** — La garde Python < 3.12 de `lexique-cli.py` passe de `== ["session"]` à
  `in (["session"], ["sous-agent"])` : Signal de dérive « modifie `lexique session` » effleuré,
  comportement de `session` inchangé. *Pourquoi* : le plan le prescrit (Q3). *Rejeté* : garde
  dédiée.
- **2026-10-05** — Étape 5 (première vérification réelle) : `injecte` non conforme. *Cause* : Claude
  Code remplace tout `additionalContext` de plus de 10 000 caractères (`HXo = 1e4`, binaire 2.1.289,
  non configurable) par un aperçu de 2 Ko. Instructions 2 004 + global 4 105 + local de
  claude-translator 12 973 = 19 082 ; le local seul dépasse le seuil, donc `session` le subit déjà.
- **2026-10-05** — Périmètre élargi aux mods : `skills/lexique/mod/` (plugin `lexique-sous-agent`),
  chargé par `CLAUDE_CODE_PLUGIN_DIRS` dans le `env` de `settings.json`. Hook `SubagentStart` ôté de
  `settings.json`. *Pourquoi* : choix de l'utilisateur ; éprouve aussi les mods. *Rejeté* : hooks
  scindés en blocs, format compact, borner le critère ; mod à la racine de `skills/lexique/` (un
  plugin de dossier de skill se charge seul au démarrage, essai `claude -p`, mais fusionnerait mod
  et skill).
- **2026-10-05** — Le mod passe par `agent.spawn` et réécrit le `prompt` du sous-agent. *Pourquoi* :
  à `classic.SubagentStart`, `$.session.append` est refusé (« no running loop »). *Rejeté* :
  `session.append` ; retard avec relance (course avec la première requête). Le harnais
  `claude plugin test` ne rend pas d'implémentation de `session.append`.
- **2026-10-05** — Étape 6 (session neuve sur claude-translator, mod chargé) : `claude-md` — règles
  et global par CLAUDE.md, local complet par le mod ; `isole` — rien ; `injecte` — règles, global et
  local par le mod, sans troncature. Les trois critères du Brief sont vérifiés.
- **2026-10-05** — Audits de clôture : 6668faa (RÉSERVES), traité par E6.1 et E6.2 (R2 :
  `tsconfig.json` du mod conservé versionné, choix de l'utilisateur ; R4 : `dev-mods/` au
  `.gitignore` ; R5 : lecture YAML de `omitClaudeMd` ; R6 : le mod dit l'échec de la commande ; R7 :
  documentation de la CLI) ; b3239f0 (RÉSERVES), R6 et R7 corrigés par E6.3.
  *Clos sans troisième audit*, choix de l'utilisateur, avec R5 (valeur entre guillemets suivie d'un
  commentaire, mal lue par la regex de `_valeur`) et la dette R8–R11.
- **2026-10-05** — Dette versée au registre à la Clôture : lecteur YAML du frontmatter d'agent (R5),
  chemins ancrés sur le HOME dans le mod (R8), agents de test au catalogue (R9), dépendance à
  `agent.spawn` (R10), `tsconfig.json` du mod (R3), lexique local tronqué par `SessionStart`.
