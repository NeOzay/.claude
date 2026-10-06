+++
gabarit = "shadow-skill"
name = "claude-code-mods"
description = "Ce qu'on a établi en écrivant des mods de Claude Code (plugins de hooks en TypeScript) : ce qui marche, les limites constatées, comment les tester. Tiré du mod `lexique-sous-agent`, version 2.1.289 à 2.1.291."
when-to-load = "À charger avant d'écrire, de déboguer ou de tester un mod, un hook `prompt.compose`, `prompt.context`, `agent.spawn` ou `session.start`, ou avant de verser du contexte à une session ou à un sous-agent."
tags = ["mods", "tests"]
+++

# claude-code-mods — ce que les mods permettent et leurs limites

## Instructions

Constats tirés de la pratique, un par ligne de vérification : chacun a été établi en exécutant,
pas en lisant les types. Ce qui n'a pas été essayé est dit comme tel, en fin de fichier. Les
versions de Claude Code sont celles de la session ; un constat peut changer avec elles.

### Entretenir ce fichier

Ce fichier n'est pas figé : il se tient à jour à chaque découverte sur les mods, par celui qui
travaille sur un mod, dans la session même.

- **Ce qui s'y ajoute** : un comportement établi en exécutant (ce qui marche, une limite, une
  recette de test), rangé sous la section qui lui correspond. Une découverte qui n'a que la lecture
  des types pour preuve va sous « Non essayé ».
- **Ce qui s'y corrige** : un constat que Claude Code a rendu faux (nouvelle version, comportement
  qui change) se remplace, avec la version qui l'a montré. Un constat démenti ne reste pas à côté
  de son remplaçant.
- **Ce qui en sort** : un constat devenu sans objet, ou un « Non essayé » qu'on a essayé : il passe
  dans la section de son résultat.
- **Quand** : au moment où la découverte est faite, avant de poursuivre le travail sur le mod ;
  pas à la clôture, où elle s'oublie. Aucun commit sans l'accord de l'utilisateur, ici comme
  ailleurs.

### Charger et vérifier un mod

- Un mod posé à la racine d'un dossier de skill, `.claude/skills/<nom>/` du projet ou
  `~/.claude/skills/<nom>/`, se charge seul, `claude -p` compris, sans `SKILL.md` ni réglage : le
  journal de `--debug` le nomme `<nom>@skills-dir`. Celui du projet ne se charge que dans une
  session ouverte sur ce projet.
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
- `claude --debug` écrit dans `debug/<session>.txt` l'ordre de chargement des modules, l'échec d'un
  module avec sa raison, et chaque appel d'un mod (`$.process.run (<mod>)`). C'est la preuve
  qu'un mod est chargé.
- `claude -p` ne pose pas les types dans le dossier du mod. Pour vérifier un mod qui n'en a pas
  encore, un `tsconfig.json` hors du mod étend celui d'un autre mod, avec son `typeRoots` en chemin
  absolu, et nomme les `hooks/` du mod à vérifier dans son `include`.
- Le `$` d'un hook se type par `EngineInterface`, exporté par `claude-code` : c'est le `$` de tout
  événement sauf `engine.create`.

### Ce qui marche

- **`agent.spawn`** : réécrire `e.prompt` préfixe ce que le sous-agent reçoit. Le hook peut lancer
  une commande (`$.process.run`) et lire l'environnement (`$.env.get`) avant d'appeler `next`.
- **`prompt.compose`** : ajouter à `composition.sections` une section
  `{ id, text, scope: 'session' }` verse du texte au prompt système de la
  **session principale seulement**. Elle survit à `/clear`, à `/compact` et à `--continue`, sans se
  dupliquer. Elle n'a pas de plafond de taille (13 000 caractères versés entiers). Un sous-agent ne
  la reçoit pas. L'`id` d'un plugin s'écrit `<plugin>:<nom>`.
- **Mémoriser entre deux appels** : une variable du module tient jusqu'au rechargement du mod,
  donc un calcul coûteux se mémorise (`local ??= await ...`). `prompt.compose` n'est pas rappelé à
  chaque requête (une fois observé pour quatre requêtes) : ne pas compter sur lui pour recalculer.
  `??=` relance le calcul tant qu'il rend une valeur vide.
- **Partager du code entre mods** : un plugin ajoute un nom à `$` dans `engine.create`
  (`const built = await next(e)`, puis `return { ...built, commande: { lancer } }`) ; la méthode
  appelle le moteur par `built` (`built.process.run`). Tout autre mod l'appelle par
  `$.commande.lancer(...)`, avec ou sans `dependencies` dans son `plugin.json` : le contrat de types
  (`"types"` du fournisseur) ne sert qu'à typer l'appel. Le journal attribue l'appel au fournisseur
  (`$.process.run (essai-commun)`). Établi par un essai jetable, fournisseur dans
  `~/.claude/skills/`, client dans `.claude/skills/`.
- **Une commande qui fournit le texte** : le mod ne décide de rien, il lance une commande
  (`lexique session`, `lexique sous-agent <type>`) et verse sa sortie en texte brut. Un JSON de
  format de hook n'apporte rien au mod et alourdit la commande.
- **Échec ouvert** : un `try/catch` autour de la commande, qui dit l'erreur par `$.ui.status` et
  rend le contexte inchangé, évite qu'un rappel bloque une session.

### Limites constatées

- **Un import ne sort pas du dossier du plugin** : `import '../../autre/lib.ts'` est refusé par
  `claude plugin validate` et au chargement (« outside the plugin's folder »), et un lien
  symbolique posé dans le dossier aussi (« resolves outside the plugin's folder ») : le module
  entier ne se charge pas. Du code partagé passe par un nom ajouté à `$`.
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
- **`$.session.append` avant `next` dans `agent.spawn`, ou à `SubagentStart`** : il n'y a pas encore
  d'`agentId` à nommer, la boucle du sous-agent n'existe pas (« no running loop »). Appelé **après**
  `next(e)`, avec l'`agentId` rendu, il est accepté, en avant-plan comme en arrière-plan : la ligne
  arrive dans la conversation du sous-agent avant sa première requête.
- **Verser du contexte à un sous-agent** : deux voies, le `prompt` réécrit avant `next` (celle du
  mod `lexique-sous-agent`) ou `$.session.append` après `next`. Ni l'une ni l'autre n'est essayée
  sur un sous-agent `fork`, refusé dans cette configuration.

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

### Autres modes, essayés au troisième audit

- Autre style de sortie et `--append-system-prompt` : la section de `prompt.compose` est présente,
  une seule fois.
- `--system-prompt` : la section disparaît, et la session n'a plus de lexique local.
- `--bare` : le moteur refuse de charger le mod, même avec `--plugin-dir` ; les hooks de
  `settings.json` sont aussi sautés. Session non ouverte faute de clé d'API.
- Une conversation reprise réutilise le prompt système qu'elle a enregistré, jusqu'à sa prochaine
  compaction : une conversation commencée sans la section n'en reçoit pas à la reprise.

### Non essayé

La session interactive, la compaction automatique, le rechargement à chaud d'un mod en cours de
session et un coéquipier d'équipe d'agents.

D'après la référence de `plugin-authoring` (2.1.291), non vérifié :

- `CLAUDE_CODE_PLUGIN_DIRS` n'est jamais lu dans les réglages d'un projet ;
- un module importe un autre fichier de son plugin par un `import` statique ; un `import()`
  empêche le chargement ;
- `dependencies` pose le contrat du fournisseur dans `.claude-plugin/types/<plugin>/` du client,
  pour `tsc` : non observé, `claude -p` ne posant pas les types ;
- l'ordre d'appel de deux mods qui ajoutent chacun un nom, ou d'un client qui l'appelle depuis
  `engine.create`.
