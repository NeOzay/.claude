+++
gabarit = "brief"
slug = "mods-a-la-racine-des-skills"
titre = "Cadrer l'utilisation des mods : lexique à la racine de son skill, mod commun, mod outillage"
statut = "validé"
"créé" = 2026-10-06
+++

## Intention

**Symptôme** : `CLAUDE_CODE_PLUGIN_DIRS` posera probablement problème quand plus de mods
existeront ; et rien ne dit comment écrire le TypeScript d'un mod, que l'utilisateur n'écrit pas.
**But** : chaque mod vit à la racine de son skill et se charge seul, le code partagé passe par un
mod commun, et une convention dit comment écrire et documenter le TypeScript d'un mod.

## Critères de réussite

- `grep -c CLAUDE_CODE_PLUGIN_DIRS settings.json` rend `0`, et `skills/lexique/mod/` n'existe plus.
- Le journal d'un `claude -p --debug` ouvert sur ce dépôt montre `lexique`, le mod commun et
  `outillage` chargés `@skills-dir`, et un appel `$.commande.lancer` de `lexique` et d'`outillage`
  vers le mod commun.
- Pour chacun des trois mods : `claude plugin validate` et `claude plugin test` passent, `tsc` ne
  rend aucune erreur, et le formatage Biome en mode vérification ne rend rien à reformater.
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

## Hors-périmètre

- Les autres usages des mods proposés : garde de commit, rappels sur Edit/Write, bandeau du
  Chantier, outils natifs, Signal de dérive en direct.
- Les autres dettes du mod lexique, dont `lexique-des-sous-agents-lie-a-agent-spawn`,
  `lexique-local-absent-sous-system-prompt` et
  `conversation-reprise-sans-lexique-local-jusqua-compaction`.
- Verser le rappel d'outillage à la session principale : elle lit `OUTILLAGE.md`, référencé par
  `.claude/CLAUDE.md`.
- Un nouveau Shadow-skill.

## Signaux de dérive

- `CLAUDE_CODE_PLUGIN_DIRS` reste dans `settings.json` ou y revient sous une autre forme (dit).
- Un mod porte une fonction `lancer` à lui, ou recopie du code du mod commun (dit).
- Un mod décide (analyse, filtre, choix du texte) au lieu de lancer une commande et de transporter
  sa sortie (dépôt: `shadow-skills/claude-code-mods/SKILL.md`, « Une commande qui fournit le
  texte »).
- Un `.ts` ou `settings.json` porte un chemin ancré sur le `HOME` (`$HOME`, `~/.claude`) (dépôt:
  `.claude/implementation/todo/technical-debt/chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod.md`).
- Le diff touche un usage hors périmètre : un hook `tool.call`, un panneau, un bandeau, un outil
  enregistré (dit).
- Le diff crée un Shadow-skill (dit).

## Contraintes connues de l'utilisateur

- **Décision** : le mod lexique quitte `skills/lexique/mod/` pour la racine de `skills/lexique/`
  (dit).
- **Décision** : le mod `lexique-sous-agent` est renommé `lexique` (dit).
- **Décision** : un mod commun, à la racine d'un skill global, porte le code partagé entre mods ;
  le mod outillage vit dans `.claude/skills/outillage/` (dit).
- **Décision** : le hook `SessionStart` de `.claude/settings.json` est retiré ; la session
  principale trouve l'outillage par `.claude/CLAUDE.md`, qui renvoie à `OUTILLAGE.md`, et seuls
  les sous-agents reçoivent le rappel par le mod (dit).
- **Décision** : les règles d'outillage recopiées en dur dans `agents/*.md` sont supprimées (dit).
- **Décision** : la règle d'usage des mods est citée dans `skill-convention`, et son autorité est le
  Shadow-skill existant `claude-code-mods` ; aucun nouveau Shadow-skill (dit).
- **Décision** : une convention TypeScript, pour le code et la documentation, entre au Chantier,
  dans `rules/claude-typescript-style.md` citée par `skill-convention`, avec les propositions
  acceptées telles quelles : le moins de TypeScript possible (la logique dans une commande du
  skill), typage strict sans `any` ni `@ts-ignore`, code partagé par `$.commande`, aucun chemin
  ancré sur le `HOME`, échec ouvert d'un rappel et `.catch` d'une garde, en-tête de module, JSDoc
  d'une ligne sur l'exporté et le contrat, tests `claude plugin test` puis vérification en session
  réelle (dit).
- **Décision** : le TypeScript se formate par Biome, `npx --yes @biomejs/biome format`, configuré
  à la racine du dépôt (guillemets simples, sans point-virgule, 2 espaces, largeur 100), inscrit à
  `OUTILLAGE.md` (dit).
- **Décision** : le Chantier solde quatre dettes :
  `aucun-signal-quand-le-mod-lexique-ne-se-charge-pas`,
  `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod`,
  `tsconfig-du-mod-etend-un-fichier-genere`, `ruff-format-absent-des-agents` (dit).
- **Existant** : un import hors du dossier du plugin est refusé ; un nom ajouté à `$` par
  `engine.create` se partage entre mods, avec ou sans `dependencies` (dépôt: `9060903`).
- **Existant** : `check_pipeline.py`, contrôle 4, tient la duplication des règles dans
  `agents/*.md` pour voulue (dépôt: `scripts/check_pipeline.py`, `check_agents`) ; la convention
  « Un sous-agent recopie ses règles » la pose
  (dépôt: `shadow-skills/skill-convention/references/prose.md`).
- **Existant** : les agents sont globaux, et leurs règles d'outillage ne valent que pour ce dépôt
  (« Les linters de ce dépôt ») (dépôt: `agents/implementation-auditor.md:78`).
- **Existant** : le mod outillage, testé au banc et en session réelle, attend dans le scratchpad de
  la session du 2026-10-06 (`outillage-de-cote/outillage`) ; il lance `hooks/outillage-rappel.sh`,
  dont l'en-tête le dit branché sur `SessionStart` (dépôt: `hooks/outillage-rappel.sh`).

## Incertitudes à lever en plan

- Où vit `hooks/outillage-rappel.sh` une fois le hook `SessionStart` retiré : à sa place, ou dans
  `.claude/skills/outillage/` ? Son en-tête est à réécrire dans les deux cas.
- Le nom du skill du mod commun (`mod-commun` proposé) et celui de son nom sur `$` (`commande`
  proposé).
- Le mod lexique appelle-t-il `lexique` par son nom de `bin/` : le `PATH` du processus d'un mod
  contient-il `bin/` ? À vérifier avant de choisir.
- Le scratchpad est propre à la session : si le Chantier s'exécute dans une autre session, le mod
  outillage mis de côté y est introuvable, et il se réécrit depuis ce qui est consigné.
