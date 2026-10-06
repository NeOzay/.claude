+++
gabarit = "shadow-skill"
name = "claude-code-mods"
description = "Ce qu'on a établi en écrivant des mods de Claude Code (plugins de hooks en TypeScript) : ce qui marche, les limites constatées, comment les tester. Tiré du mod `lexique-sous-agent`, version 2.1.289 à 2.1.291."
when-to-load = "À charger avant d'écrire, de déboguer ou de tester un mod, un hook `prompt.compose`, `prompt.context`, `agent.spawn` ou `session.start`, ou avant de verser du contexte à une session ou à un sous-agent."
tags = ["mods", "tests"]
+++

## Instructions

Constats tirés de la pratique, un par ligne de vérification : chacun a été établi en exécutant,
pas en lisant les types. Ce qui n'a pas été essayé est dit comme tel, en fin de fichier. Les
versions de Claude Code sont celles de la session ; un constat peut changer avec elles.

### Charger et vérifier un mod

- `CLAUDE_CODE_PLUGIN_DIRS`, dans le bloc `env` de `settings.json`, nomme le dossier du mod : chaque
  session le charge, `claude -p` compris. `claude --plugin-dir <dossier>` le charge pour une
  session.
- Un mod tient en trois fichiers : `.claude-plugin/plugin.json`, `hooks/hooks.json`
  (`{ "modules": ["./register.ts"] }`) et le module. Les types sont écrits par le moteur dans
  `<mod>/.claude-plugin/types/` au premier chargement.
- `claude plugin validate <mod>` lit le manifeste et le module ; `claude plugin test <mod>` lance
  les `*.test.ts`. Un avertissement « no author information » est sans effet.
- `tsc` n'est pas installé : `npx --yes -p typescript@5 tsc -p tsconfig.json --noEmit` depuis le
  dossier du mod, qui étend le `tsconfig.json` posé par le moteur.
- Le `$` d'un hook se type par `Parameters<Hook<'agent.spawn'>>[0]` : le moteur n'exporte pas de
  type nommé pour lui.

### Ce qui marche

- **`agent.spawn`** : réécrire `e.prompt` préfixe ce que le sous-agent reçoit. Le hook peut lancer
  une commande (`$.process.run`) et lire l'environnement (`$.env.get`) avant d'appeler `next`.
- **`prompt.compose`** : ajouter à `composition.sections` une section
  `{ id, text, scope: 'session' }` verse du texte au prompt système de la
  **session principale seulement**. Elle survit à `/clear`, à `/compact` et à `--continue`, sans se
  dupliquer. Elle n'a pas de plafond de taille (13 000 caractères versés entiers). Un sous-agent ne
  la reçoit pas. L'`id` d'un plugin s'écrit `<plugin>:<nom>`.
- **Mémoriser entre deux appels** : une variable du module tient jusqu'au rechargement du mod ;
  `prompt.compose` se déclenche à chaque requête, donc un calcul coûteux se mémorise
  (`local ??= await ...`).
- **Une commande qui fournit le texte** : le mod ne décide de rien, il lance une commande
  (`lexique session`, `lexique sous-agent <type>`) et verse sa sortie en texte brut. Un JSON de
  format de hook n'apporte rien au mod et alourdit la commande.
- **Échec ouvert** : un `try/catch` autour de la commande, qui dit l'erreur par `$.ui.status` et
  rend le contexte inchangé, évite qu'un rappel bloque une session.

### Limites constatées

- **Plafond des hooks de `settings.json`** : un `additionalContext` de plus de 10 000 caractères
  (`SessionStart`, `SubagentStart`) est remplacé par un aperçu de 2 Ko ; le reste va dans un
  fichier. Constaté dans le binaire 2.1.289 (`HXo = 1e4`), non configurable. C'est la raison d'être
  du mod.
- **`prompt.context` arrive aux sous-agents** : le bloc ajouté est servi à tous, y compris à ceux
  dont `omitClaudeMd: true` veut l'isolation (`omitClaudeMd` ne retire que le bloc `claudeMd`). Un
  sous-agent non isolé le reçoit en double si son contexte le porte déjà. L'entrée du hook ne
  porte ni `agentId` ni rien qui dise quelle boucle appelle ; compter les `agent.spawn` en cours
  autour de `next` ne suffit pas, `prompt.context` ne se déclenche pas pendant le lancement.
- **`$.session.append` à `session.start`** : il ajoute une ligne à la conversation principale
  seulement, mais `session.start` se déclenche **une fois par processus**. Après `/clear` la
  nouvelle session n'a pas la ligne ; après `/compact` le résumé ne la garde pas et rien ne la
  rajoute ; chaque `--resume` ou `--continue` en ajoute une copie. Un hook `SessionStart` de
  `settings.json` se redéclenche, lui, avec `source=clear` et `source=compact`.
- **`$.session.append` à `agent.spawn` ou `SubagentStart`** : refusé, « no running loop » ; la
  boucle du sous-agent n'existe pas encore.
- **`agent.spawn` ne voit que son `prompt`** : c'est la seule voie pour verser du contexte à un
  sous-agent, et elle ne dit rien d'un sous-agent `fork`.

### Tester

- Chaque test charge le module à neuf : une variable de module ne fuit pas d'un test à l'autre.
- Les `on(...)` d'un test sont le fond du moteur : un événement que le mod appelle doit avoir son
  fond (`env.get`, `process.run`, `ui.status`, l'événement lui-même), sinon l'appel échoue.
- **Le banc n'implémente pas `session.append`** : un `on('session.append', ...)` n'est jamais
  appelé, et le hook qui l'utilise est ignoré par le moteur (« hook was skipped »)
  **sans que le test échoue**. Lire la ligne « the engine reported » des tests qui passent ; une
  exception d'un hook s'y trouve. Éviter les voies que le banc ne voit pas : un test vert qui
  n'observe rien est faux.
- `prompt.compose` se teste à plein : fond `on('prompt.compose', () => ({ sections: [...] }))`,
  appel `$['prompt'].compose(<entrée>)`, assertion sur les sections rendues.
- Un événement s'appelle par `$['agent'].spawn(...)`, `$['prompt'].compose(...)`.

### Vérifier en session réelle

Les tests du banc ne disent pas ce que reçoit une vraie session. Recette, dans le projet où le mod
doit agir :

```bash
claude -p --model haiku "<consigne>" < /dev/null          # < /dev/null : sans lui, 3 s d'attente
printf '%s\n' '{"type":"user","message":{"role":"user","content":"/clear"}}' \
  '{"type":"user","message":{"role":"user","content":"<question>"}}' \
  | claude -p --model sonnet --input-format stream-json --output-format stream-json --verbose
```

- Un agent témoin sans outil (`tools: Read`) qui rapporte ce que son contexte contient dit ce qu'un
  sous-agent a reçu : `lexique-test-isole`, `lexique-test-claude-md`, `lexique-test-injecte`.
- Pour compter, lire la transcription de la session plutôt que la réponse du modèle, qui se
  trompe sur un décompte ou prend le dernier terme du lexique global pour celui du local.
- `/clear` et `/compact` s'envoient en entrée `stream-json`, un message par ligne.
- Un hook `SessionStart` passé par `--settings` sert de témoin : il montre ce que la base verse
  dans les mêmes cas.

### Non essayé

La session interactive, la compaction automatique, le rechargement à chaud d'un mod en cours de
session, un sous-agent `fork`, et ce que devient une section de `prompt.compose` avec un autre
style de sortie ou `--bare`.
