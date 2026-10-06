+++
gabarit = "suivi"
slug = "mods-a-la-racine-des-skills"
titre = "Cadrer l'utilisation des mods : lexique à la racine de son skill, mod commun, mod outillage"
branche = "mods-a-la-racine-des-skills"
base = "master"
statut = "terminé"
session = 3
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-06-mods-a-la-racine-des-skills.plan.md"
brief = ".claude/implementation/done/2026-10-06-mods-a-la-racine-des-skills.brief.md"
audit = ".claude/implementation/done/2026-10-06-mods-a-la-racine-des-skills.audit.md"
road-map = "<OPTIONNEL>"
skills = ["claude-code-mods", "skill-convention"]
"créé" = 2026-10-06
maj = 2026-10-06
+++

## Objectif et périmètre

**Symptôme** : `CLAUDE_CODE_PLUGIN_DIRS` posera probablement problème quand plus de mods
existeront ; et rien ne dit comment écrire le TypeScript d'un mod, que l'utilisateur n'écrit pas.

**But** : chaque mod vit à la racine de son skill et se charge seul, le code partagé passe par un
mod commun, et une convention dit comment écrire et documenter le TypeScript d'un mod.

**Critères de réussite** :

- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` rend `0`, et `skills/lexique/mod/` n'existe plus.
- Le journal d'un `claude -p --debug` ouvert sur ce dépôt montre `lexique`, le mod commun et
  `outillage` chargés `@skills-dir`, et un appel `$.commande.lancer` de `lexique` et d'`outillage`
  vers le mod commun.
- Pour chacun des trois mods : `claude plugin validate` et `claude plugin test` passent, `tsc` ne
  rend aucune erreur, et le formatage Biome en mode vérification ne rend rien à reformater.
  *Amendé le 2026-10-06* : pour `mod-commun`, `claude plugin test` est remplacé par une
  vérification de `$.commande.lancer` en session réelle, par un client jetable ; le banc ne peut
  pas l'exercer, et la commande sort en 1 sans `*.test.ts`.
- En session réelle : les trois agents témoins du lexique rendent ce qu'ils rendaient avant le
  Chantier, un sous-agent lancé dans ce dépôt reçoit le rappel d'outillage, et la session
  principale porte la section du lexique local.
- `grep -rn lexique-sous-agent`, hors `done/`, rapports d'audit et dettes soldées, ne rend rien.
- `agents/*.md` ne porte plus de règle d'outillage, et `check_pipeline.py` passe.
- `.claude/settings.json` n'a plus de hook `SessionStart`.
- `rules/claude-typescript-style.md` existe, `skill-convention` la cite ainsi que
  `claude-code-mods`, et `OUTILLAGE.md` dit comment lancer Biome.
- Les dettes `aucun-signal-quand-le-mod-lexique-ne-se-charge-pas`,
  `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod`,
  `tsconfig-du-mod-etend-un-fichier-genere` et `ruff-format-absent-des-agents` sont soldées.

**Hors-périmètre** :

- Les autres usages des mods proposés : garde de commit, rappels sur Edit/Write, bandeau du
  Chantier, outils natifs, Signal de dérive en direct.
- Les autres dettes du mod lexique, dont `lexique-des-sous-agents-lie-a-agent-spawn`,
  `lexique-local-absent-sous-system-prompt` et
  `conversation-reprise-sans-lexique-local-jusqua-compaction`.
- Verser le rappel d'outillage à la session principale : elle lit `OUTILLAGE.md`, référencé par
  `.claude/CLAUDE.md`.
- Un nouveau Shadow-skill.

**Signaux de dérive** :

- `CLAUDE_CODE_PLUGIN_DIRS` reste dans `settings.json` ou y revient sous une autre forme.
- Un mod porte une fonction `lancer` à lui, ou recopie du code du mod commun.
- Un mod décide (analyse, filtre, choix du texte) au lieu de lancer une commande et de transporter
  sa sortie.
- Le diff ajoute un chemin ancré sur le `HOME` (`$HOME`, `~/.claude`) dans un `.ts` ou
  `settings.json` ; les lignes `$HOME/.claude/…` que `settings.json` porte déjà n'en sont pas.
- Le diff touche un usage hors périmètre : un hook `tool.call`, un panneau, un bandeau, un outil
  enregistré.
- Le diff crée un Shadow-skill.

## Étapes

- [x] 1. Convention TypeScript et Biome — `rules/claude-typescript-style.md`, `biome.json`,
  `OUTILLAGE.md`, `.gitignore`, `shadow-skills/skill-convention/SKILL.md` — vérif:
  `npx --yes @biomejs/biome@2 format --verbose .` et `scripts/check_pipeline.py`
- [x] 2. Mod commun — `skills/mod-commun/` — vérif: `claude plugin validate skills/mod-commun`,
  `tsc`, Biome, et un client jetable en session réelle
- [x] 3. Tester un client de `$.commande` — `rules/claude-typescript-style.md`,
  `shadow-skills/claude-code-mods/SKILL.md` — vérif: `claude plugin test <client jetable>`
- [x] 4. Mod lexique à la racine de son skill — `skills/lexique/`, `settings.json` — vérif:
  `claude plugin test skills/lexique` et `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json`
- [x] 5. Module du lexique sur `$.commande` — `skills/lexique/hooks/` — vérif:
  `claude plugin test skills/lexique` et le journal `claude -p --debug`
- [x] 6. Renommage dans la documentation, témoins et session principale — `skills/lexique/`,
  `agents/lexique-test-*.md`, deux dettes — vérif: `grep -rln lexique-sous-agent …` et les témoins
- [x] 7. Contrôle 9 étendu aux scripts des skills — `scripts/check_pipeline.py`,
  `scripts/tests/test_controle_9.py` — vérif: `pytest scripts/tests/test_controle_9.py`
- [x] 8. Mod outillage — `.claude/skills/outillage/`, `.claude/settings.json`, `prose.md` — vérif:
  `claude plugin test .claude/skills/outillage` et la transcription d'un sous-agent
- [x] 9. Règles d'outillage hors des agents — `agents/implementation-auditor.md`,
  `agents/plan-reviewer.md`, `OUTILLAGE.md`, `prose.md` — vérif:
  `grep -cE 'ruff|basedpyright|pyright' agents/implementation-auditor.md agents/plan-reviewer.md`
- [x] 10. Signal quand un mod ne peut pas se charger — `scripts/sante_skills.py`,
  `scripts/tests/test_sante_skills.py` — vérif: `pytest scripts/tests/test_sante_skills.py`
- [x] 11. Shadow-skill `claude-code-mods` — `shadow-skills/claude-code-mods/SKILL.md` — vérif:
  `shadow-skill verifie`

## État courant

**Prochaine action** : Clôture, par `/implementation-tracker close` : audit final, solde des cinq
dettes, défaut du contrôle 7 au registre de dette.
**Vérification** : la vérification de bout en bout du Plan, `claude -p --debug` sur ce dépôt.
**Dernier audit** : `349bb96` — RÉSERVES — 2026-10-06
**Notes** : le mod outillage testé le 2026-10-06 attend dans le scratchpad de la session de
création (`outillage-de-cote/outillage`) ; l'Étape 8 le réécrit d'après le Plan, sans en dépendre.

## Passation

**Écrite** : session 2, après AE9.

**En cours** : rien. L'Étape 10 n'est pas commencée.

**À savoir** :

- Projet de référence pour les témoins du lexique et la section de la session principale :
  `/home/debian/projects/claude-translator`, qui a un `.claude/LEXIQUE.md`.
- Le `TY` de la recette `tsc` est désormais `skills/lexique/.claude-plugin/types/`, déplacé avec
  le mod et ignoré par git ; aucun mod `@skills-dir` n'en reçoit de neuf.
- Le processus Claude Code lancé avant l'Étape 4 garde `CLAUDE_CODE_PLUGIN_DIRS` dans son
  environnement, même après `/clear` : lancer chaque `claude -p` de preuve sous
  `env -u CLAUDE_CODE_PLUGIN_DIRS` tant qu'il n'a pas été relancé.
- Ne jamais lire le code de sortie d'une commande suivie d'un tube (`| tail`) : `$?` est celui du
  dernier maillon. C'est l'origine de R1 au premier audit.
- Preuves en session réelle : le journal de `claude -p --debug` est dans `debug/<session>.txt`, la
  dernière session par `ls -t debug/*.txt | head -1` ; la transcription d'un sous-agent est sous
  `projects/-home-debian--claude/<session>/subagents/`, la session étant le nom du journal.
- `.claude/implementation/mods-a-la-racine-des-skills.audit.md` porte les deux audits
  intermédiaires (`ff927cc`, `62f2a4a`), non commité : il ne l'est qu'à l'aplatissement. R6 reste
  ouvert par choix de l'utilisateur.
- À la Clôture, outre les cinq dettes à solder, le défaut du contrôle 7 noté au Journal va au
  registre de dette.

## Journal de décisions

- **2026-10-06** — La règle « comparer à la base par `git archive` » reste dans
  `implementation-auditor.md`, écart au Brief ratifié par l'utilisateur. *Pourquoi* : méthode
  d'audit valable dans tout projet, que le mod outillage n'apporte que dans ce dépôt. *Rejeté* :
  la retirer avec les autres règles d'outillage.
- **2026-10-06** — La dette `nom-du-mod-lexique-sous-agent-trop-etroit` est soldée en plus des
  quatre du Brief, écart ratifié par l'utilisateur. *Pourquoi* : le renommage que le Brief décide
  la solde. *Rejeté* : la laisser ouverte une fois le nom changé.
- **2026-10-06** — Le Signal « chemin ancré sur le HOME » ne vise que les lignes ajoutées par le
  diff, après deux passages NON CONFORME du Plan par `plan-reviewer`. *Pourquoi* : `settings.json`
  porte déjà trois lignes `$HOME/.claude/…`. *Rejeté* : arrêter sur l'état du fichier.
- **2026-10-06** — `biome.json` active `vcs.useIgnoreFile`, et porte `arrowParentheses:
  "asNeeded"` et `assist.enabled = false`, écarts ratifiés par l'utilisateur. *Pourquoi* : sans le
  premier, Biome parcourt `.venv/` ; les deux autres gardent l'écriture `on =>` et ne laissent à
  Biome que le format. *Rejeté* : `!biome.json` dans `files.includes`, qui fait échouer Biome ; les
  valeurs par défaut.
- **2026-10-06** — Critère 3 amendé pour `mod-commun`, écart ratifié par l'utilisateur après l'audit
  DÉFAVORABLE de `ff927cc` (R1) : `claude plugin test` y fait place à un client jetable en session
  réelle. *Pourquoi* : le banc refuse tout appel à `$` depuis un hook de test, et la commande sort
  en 1 sans `*.test.ts`. *Rejeté* : un `*.test.ts` de façade.
- **2026-10-06** — Un client de `$.commande` se teste par un `on('engine.create')` du test qui pose
  un faux `$.commande`. *Pourquoi* : seule voie qui tient en un hook et se type. *Rejeté* : un fond
  `on('commande.lancer')`, qui demande un `engine.create` à côté.
- **2026-10-06** — Un mod appelle une commande par son nom de `bin/`, résolu par le `PATH`.
  *Pourquoi* : aucun chemin ancré sur le `HOME` ; un mod jetable a lancé `['lexique', 'chemin']`.
  *Rejeté* : résoudre la racine de la configuration dans le mod.
- **2026-10-06** — `TY`, dans la recette `tsc`, est le dossier de types du mod lexique, rafraîchi
  par `claude -p --plugin-dir <mod>`. *Pourquoi* : `claude -p` ne pose pas les types d'un mod
  chargé `@skills-dir`. *Rejeté* : versionner les types.
- **2026-10-06** — Les hooks des mods portent un `.catch` qui dit `next.error.message ?? kind` et
  rend `next(e)`. *Pourquoi* : le moteur saute un hook qui lève en silence, et `validate` tient
  `agent.spawn` pour une garde. *Rejeté* : un `try` autour de chaque appel.
- **2026-10-06** — Témoins du lexique, dans `claude-translator`, relevés avant le déplacement et
  identiques après : `isole` rend trois « absent » ; `claude-md` et `injecte` rendent le local
  (premier terme Orchestrateur), le global (Gabarit) et les règles. La session principale porte
  la ligne « Lexique local de … ». *Pourquoi* : référence des preuves en session réelle.
  *Rejeté* : aucun.
- **2026-10-06** — Audit de clôture sur `349bb96` : RÉSERVES ; le Chantier se clôt avec R10, R11 et
  R12, versées au registre de dette avec R6 et le défaut du contrôle 7. *Pourquoi* : choix de
  l'utilisateur, aucun bloquant. *Rejeté* : traiter les réserves avant la Clôture.
