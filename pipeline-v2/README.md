# pipeline-v2 — exploration d'un pipeline des Chantiers porté par des mods

Ce répertoire porte l'étude d'une v2 du pipeline des Chantiers, écrite de zéro à côté de la v1 :
des prototypes de mods qui cernent ce que Claude Code modifié de l'intérieur peut afficher et
faire, les constats qu'on en tire, une conclusion — poursuivre ou annuler —, et, si l'on poursuit,
une spécification. Chantier `pipeline-v2`, Brief `.claude/implementation/pipeline-v2.brief.md`.

Rien ici n'est en service. **Aucun prototype ne se charge seul** : ni lien sous `skills/`, ni
`CLAUDE_CODE_PLUGIN_DIRS` dans `settings.json`. Un prototype se charge pour une session, par
`--plugin-dir`, et seulement pour l'observer.

**Exploration arrêtée le 2026-10-13, verdict mitigé** : [conclusion](conclusion.md). Le Suivi, le
Brief, le Plan et l'audit du Chantier sont archivés à sa Clôture sous
`.claude/implementation/done/`, préfixés de la date de Clôture (`*-pipeline-v2.*`).

| Fichier | Ce qu'il porte |
|---|---|
| `conclusion.md` | le verdict, les douze éléments, les incertitudes du Brief, quand reprendre |
| `constats.md` | ce que chaque surface a affiché, puis un constat par élément à afficher |
| `proto-<nom>/` | un prototype, mod mince et jetable : `.claude-plugin/plugin.json` de nom `pv2-<nom>`, `hooks/` |
| `api/` | l'inventaire de l'API des mods par version, et `inventaire.py` qui le dresse |
| `proto-<nom>/journal.log` | ce que le moteur a fait pendant la session témoin, écrit par le prototype ; ignoré par git |

## Une session témoin

Un prototype s'observe dans une session à part, jamais dans celle du Chantier, et **dans Desktop** :
le navigateur, par Remote Control, ne dessine aucun mod (`constats.md`, « Surfaces »).

Desktop ouvre la session par SSH sur la machine, dans `~/.claude`, branche `pipeline-v2`. Il ne
prend pas `--plugin-dir` : le prototype s'y charge par `CLAUDE_CODE_PLUGIN_DIRS`, posé **le temps
de l'observation** dans le bloc `env` de `settings.json`, puis retiré. Tant qu'elle y est, toute
session de la machine charge le prototype ; elle n'est jamais commitée, et la garde ne se lance
qu'une fois la variable retirée. Une session déjà ouverte pendant que la variable
était posée la garde dans son environnement, et tout `claude` qu'elle lance charge le prototype :
la redémarrer, ou lancer `env -u CLAUDE_CODE_PLUGIN_DIRS claude …`.

```json
"CLAUDE_CODE_PLUGIN_DIRS": "~/.claude/pipeline-v2/<proto>"
```

Ce qui s'affiche se rapporte, capture d'écran à l'appui. Au terminal,
`claude --debug --plugin-dir pipeline-v2/<proto>` sert de témoin et écrit le journal `--debug`.

Deux sources font un constat :

- **ce qui s'est vu**, que rapporte celui qui suit la session ;
- **ce que le moteur a fait**, dans `pipeline-v2/<proto>/journal.log` — clients attachés, demandes
  de dessin par surface, placement d'un panneau, sort d'une notification — et dans le journal
  `--debug`, le plus récent de `debug/`.

## Le format d'un constat

Dans `constats.md`, chaque constat se range sous `### <surface>`, dans la section de son élément ;
sa première ligne dit qui l'a vu, quand, sur quelle version :

```md
### Panneau

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.296, surface navigateur.

<ce qui s'est affiché, ou pas, et ce que dit le journal>
```

Un élément non essayé porte `### Non essayé` et sa raison. La section `## Surfaces`, en tête,
porte ceux de la sonde. Ce qui vaut au-delà du pipeline va aussi au Shadow-skill
`claude-code-mods`, chaque ligne ajoutée avec sa version entre parenthèses.

## Les contrôles

Lancés depuis la racine du dépôt.

**Garde** — v1 intacte, aucun prototype chargé seul, lexique inchangé (S1, S2, S6, C7) :

```bash
test -z "$(git diff master --name-only -- skills .claude/skills settings.json LEXIQUE.md)" \
  && ! grep -q CLAUDE_CODE_PLUGIN_DIRS settings.json && echo GARDE-OK
```

**Constats** — chaque `###` est vu ou dit non essayé, chaque section numérotée en a un (S5, C3) :

```bash
C=pipeline-v2/constats.md
test "$(grep -c '^### ' $C)" -eq "$(grep -c -e '^Vu par ' -e '^### Non essayé' $C)" \
  && awk '/^## /{if(s&&!h)m++; s=/^## [0-9]/; h=0; next} /^### /{h=1}
          END{if(s&&!h)m++; exit m>0}' $C && echo CONSTATS-OK
```

**`claude-code-mods`** — chaque ligne ajoutée porte sa version (S5, C6) :

```bash
git diff master -U0 -- shadow-skills/claude-code-mods/SKILL.md | grep '^+- ' | grep -v '2\.1\.' \
  | grep -q . && echo "CONSTAT SANS VERSION" || echo MODS-OK
```

**Manifeste** (C2) : `claude plugin validate pipeline-v2/<proto>`.

**Chargement** (C2), pour un prototype `<proto>` de nom `<name>` :

```bash
claude -p --debug --model haiku --plugin-dir pipeline-v2/<proto> "Réponds OK." < /dev/null
grep -q '<name>' "$(ls -t debug/*.txt | head -1)" && echo CHARGE-OK
```

**Typage** (C8). En 2.1.296, `claude -p` ne pose plus les types dans
`<proto>/.claude-plugin/types/` ; une session interactive `claude --plugin-dir` les y écrit. Le
`tsconfig.json` temporaire nomme donc le dossier de types, `TY` : celui d'un prototype qu'une
session témoin a chargé, `pipeline-v2/proto-sonde/.claude-plugin/types`. Il porte l'API
(`claude-code/`) et les outils (`claude-code-tools/`), dont `proto-veille` a besoin. À défaut,
`types/claude-code.d.ts` du skill `plugin-authoring` donne l'API seule.

```bash
R=$(git rev-parse --show-toplevel); T=$(mktemp -d)
TY="$R/pipeline-v2/proto-sonde/.claude-plugin/types"; M="$R/pipeline-v2/<proto>"
printf '{"compilerOptions":{"target":"es2023","lib":["es2023"],"types":[],"module":"esnext","moduleResolution":"bundler","strict":true,"noUncheckedIndexedAccess":true,"noEmit":true,"skipLibCheck":true,"jsx":"react","jsxFactory":"h","jsxFragmentFactory":"Fragment"},"include":["%s","%s/hooks","%s/types"]}' \
  "$TY" "$M" "$M" > "$T/tsconfig.json"
npx --yes -p typescript@5 tsc -p "$T/tsconfig.json" --noEmit && echo TSC-OK
```

**Format** :

```bash
npx --yes @biomejs/biome@2 format pipeline-v2 && uvx rumdl fmt --check .
```
