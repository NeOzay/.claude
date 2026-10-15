+++
gabarit = "shadow-skill"
name = "claude-code-mods"
description = "Ce qu'on a établi en écrivant des mods de Claude Code (plugins de hooks en TypeScript) : ce qui marche, les limites constatées, comment les tester. Tiré des mods `lexique`, `mod-commun` et `outillage`, version 2.1.289 à 2.1.291."
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

- **La racine d'un skill est la voie de ce dépôt.** Un mod posé à la racine d'un dossier de skill,
  `.claude/skills/<nom>/` du projet ou `~/.claude/skills/<nom>/`, se charge seul, `claude -p`
  compris, sans `SKILL.md` ni réglage : le journal de `--debug` le nomme `<nom>@skills-dir`. Celui
  du projet ne se charge que dans une session ouverte sur ce projet. Pratiqué par `lexique` et
  `mod-commun` sous `skills/`, `outillage` sous `.claude/skills/` (2.1.291).
- Un `SKILL.md` posé à côté du mod, avec `disable-model-invocation: true` et
  `user-invocable: false`, n'empêche pas le mod de se charger, et le skill n'entre pas dans la
  liste du modèle (2.1.291, `skills/mod-commun/`). À côté d'un skill ordinaire, le mod se charge
  aussi (`skills/lexique/`).
- `CLAUDE_CODE_PLUGIN_DIRS`, dans le bloc `env` de `settings.json`, n'est plus que la voie d'un mod
  hors d'un skill : il nomme le dossier du mod, et chaque session le charge, `claude -p` compris.
  Ce dépôt n'en a plus, et `scripts/sante_skills.py` signale la variable si elle y revient.
- `claude --plugin-dir <dossier>` charge un mod pour une session. Un mod du même nom chargé
  `@skills-dir` s'efface devant lui (« the name … is already taken by a session-only plugin ») :
  c'est la copie de `--plugin-dir` qui agit (2.1.291).
- Un mod tient en trois fichiers : `.claude-plugin/plugin.json`, `hooks/hooks.json`
  (`{ "modules": ["./register.ts"] }`) et le module, résolu depuis `hooks/`.
- **Un mod qui ne se charge pas ne dit rien** : la session tourne sans lui. Au démarrage,
  `scripts/sante_skills.py` contrôle chaque mod à la racine d'un skill du dépôt : `plugin.json`
  lisible avec un `name`, modules de `hooks.json` présents, `dependencies` qui nomment un mod
  présent. Un module présent qui échoue au chargement lui échappe : seul le journal le montre.
- `claude plugin validate <mod>` lit le manifeste et le module ; `claude plugin test <mod>` lance
  les `*.test.ts`. Un avertissement « no author information » est sans effet.
- `claude --debug` écrit dans `debug/<session>.txt` l'ordre de chargement des modules, l'échec d'un
  module avec sa raison, et chaque appel d'un mod (`$.process.run (<mod>)`). C'est la preuve
  qu'un mod est chargé.
- **Les types** : le moteur écrit dans `<mod>/.claude-plugin/types/` ceux de `claude-code`, un
  `tsconfig.json` que celui du mod étend, et le contrat de chaque `dependencies`
  (`types/mod-commun/index.d.ts`). `claude -p` ne les pose plus, même pour un mod chargé par
  `--plugin-dir` : le journal n'écrit aucun `type root of <mod>`, et le dossier reste absent
  (2.1.296, `pipeline-v2/proto-sonde`). Une session interactive `claude --plugin-dir <mod>` les pose
  (2.1.296 : `type root of <mod> at … wrote …`). À défaut, le skill `plugin-authoring`, chargé,
  donne le chemin de `types/claude-code.d.ts`, que le `tsconfig.json` temporaire nomme dans son
  `include` (2.1.296, recette dans `pipeline-v2/README.md`).
- **`tsc`**, absent du `PATH`, passe par `npx`. Aucun `tsconfig.json` n'est versionné : ils
  étendent des types que le moteur pose et que git ignore. Un `tsconfig.json` temporaire, hors du
  mod, étend celui d'un mod qui a déjà ses types, avec son `typeRoots` en chemin absolu, et nomme
  les `hooks/` du mod à vérifier dans son `include` ; chaque chemin part de
  `git rev-parse --show-toplevel`, aucun du `HOME`. La recette est dans `OUTILLAGE.md`, « Le
  TypeScript des mods ».
- Le `$` d'un hook se type par `EngineInterface`, exporté par `claude-code` : c'est le `$` de tout
  événement sauf `engine.create`.

### Ce qui marche

- **`agent.spawn`** : réécrire `e.prompt` préfixe ce que le sous-agent reçoit. Le hook peut lancer
  une commande (`$.process.run`) et lire l'environnement (`$.env.get`) avant d'appeler `next`.
- **`prompt.compose`** : ajouter à `composition.sections` une section
  `{ id, text, scope: 'session' }` verse du texte au prompt système de la
  **session principale seulement**. Elle survit à `/clear` et à `/compact` sans se dupliquer. Elle
  n'a pas de plafond de taille (13 000 caractères versés entiers). Un sous-agent ne la reçoit pas.
  L'`id` d'un plugin s'écrit `<plugin>:<nom>`. Une conversation reprise ne la recompose pas : elle
  garde celle de son début, ou son absence, jusqu'à sa compaction (« Autres modes, essayés au
  troisième audit »).
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
  `~/.claude/skills/`, client dans `.claude/skills/`. Dans ce dépôt, ce nom est `$.commande` du mod
  commun, son contrat et son appel : [mod-commun](../../skills/mod-commun/SKILL.md).
  - La méthode s'écrit **dans** le hook `engine.create`, où elle appelle `built.process.run` tel
    quel : `claude plugin validate` refuse que la valeur de `next(e)` passe en argument à une
    fonction (« the value of next(e) at engine.create is passed as an argument »), et le module ne
    se charge pas (2.1.291).
  - Le moteur lit dans le module les appels à `$` qu'il écrit (`validate` les liste :
    « calls: … »), et refuse tout autre appel (« its hooks module does not call it »).
- **Une commande de `bin/` s'appelle par son nom** : `$.process.run(['lexique', 'chemin'])` la
  trouve, le processus lancé par un mod héritant du `PATH` de la session (2.1.291, session lancée
  d'un shell dont le `PATH` porte `bin/`).
- **Une commande qui fournit le texte** : le mod ne décide de rien, il lance une commande
  (`lexique session`, `lexique sous-agent <type>`) et verse sa sortie en texte brut. Un JSON de
  format de hook n'apporte rien au mod et alourdit la commande.
- **Échec ouvert** : un `try/catch` autour de la commande, qui dit l'erreur par `$.ui.status` et
  rend le contexte inchangé, évite qu'un rappel bloque une session.
- **Un hook qui lève est sauté** : le moteur fait passer l'événement aux hooks inférieurs, sans
  rien afficher. `on(...).catch(($, e, next) => { …; return next(e) })` reprend la main à la place
  du hook : il dit l'erreur, et `next(e)` laisse passer l'événement (rejoue le dernier `next` si le
  hook l'avait appelé). `next.error` n'est pas l'erreur levée mais un constat du moteur,
  `{ kind, message?, budget }` : le motif se lit dans `message` (`String(next.error)` rend
  `[object Object]`). Établi au banc : sans fond pour `env.get`, le sous-agent passe intact et la
  ligne d'état dit « no implementation for env.get », seulement avec le `.catch`. Un fond du test
  qui lève est lui-même sauté, avec le même effet (2.1.291, mod lexique).
- `claude plugin validate` tient un hook `agent.spawn` pour une garde, et avertit sans échouer
  quand il n'attache pas de `.catch` (« gating hook without .catch: agent.spawn »), même s'il
  attrape ses erreurs lui-même ; un `.catch` attaché lève l'avertissement (2.1.291).

### Limites constatées

- **Le contrat d'un `$.state`** (2.1.296) : `claude plugin validate` ne lit une clé que déclarée
  en objet littéral sous le nom du mod, `interface PluginState { '<mod>': { <clé>: … } }` ; un
  alias (`'<mod>': Jetable`) laisse chaque clé « not declared ». Le contrat exporte au moins un
  type, et rien d'autre : un `export {}` est refusé (`pipeline-v2/proto-etat`).
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
  mod `lexique`) ou `$.session.append` après `next`. Ni l'une ni l'autre n'est essayée
  sur un sous-agent `fork`, refusé dans cette configuration.

### Où un mod dessine

Établi par la sonde de `pipeline-v2` (`pipeline-v2/constats.md`, section « Surfaces »), d'après
ce que l'utilisateur a vu et ce que la sonde a noté du moteur.

- **Le navigateur ne dessine rien** (2.1.296) : une session suivie sur claude.ai/code par Remote
  Control ne montre ni panneau, ni bande, ni ligne d'état, ni toast. Le client web ne se déclare pas
  surface (aucun `session.attach`) ; une commande `/` tapée au navigateur arrive à la session et
  s'exécute, mais le panneau qu'elle ouvre se place au terminal de la machine.
- **Desktop attaché par Remote Control à une session CLI** (2.1.296) ne dessine rien non plus : même
  comportement que le navigateur.
- **Desktop qui lance la session** (2.1.295), ici par SSH sur la machine, est une surface
  `desktop` : un `session.attach` (`clientId` `desktop-2`) ; panneau, bande, `Markdown` et ses liens
  `https:` et `file:`, toast et `Button` s'affichent, et un appui arrive au mod.
- **Desktop en SSH tourne sa propre CLI**, 2.1.295, posée sous `~/.claude/remote/`, avec son état
  d'exécution et les plugins qu'il synchronise. Le mod s'y est chargé par
  `CLAUDE_CODE_PLUGIN_DIRS` du `settings.json` de l'utilisateur ; la même variable dans
  `.claude/settings.local.json` du projet ne l'a pas chargé, et aucune voie de passer
  `--plugin-dir` n'a été trouvée (2.1.295).
- **La ligne d'état sous Desktop** (2.1.295) : `$.ui.status` s'affiche préfixé du nom du mod
  (`pv2-sonde pv2-sonde : ligne d'état`), sur une ligne étroite partagée avec d'autres éléments
  de l'interface : le texte n'a pas à répéter le nom du mod.
- **`$.ui.notify` sans canal** : `no-channel` au terminal (2.1.296), `no-surface` sous Desktop en
  SSH (2.1.295).

### Mémoire, contexte et rechargement

Établi par `pipeline-v2/proto-etat`, d'après son journal et ce que l'utilisateur a vu.

- **`$.store` survit à tout** (2.1.296 et 2.1.295) : d'une session à l'autre, et du terminal à
  Desktop en SSH sur la même machine, qui partagent le même magasin.
- **`$.state` survit au rechargement à chaud** (2.1.296), pas à une nouvelle session ; sous
  Desktop, `/clear` relance `session.start` et `$.state` repart vide (2.1.295).
- **`claude --plugin-dir <mod>` interactif** (2.1.296) recharge le mod à chaque modification de
  ses fichiers : « reloaded », puis `session.start: raised for <mod> (loaded later)`.
- **Un processus lancé par un mod n'a pas `CLAUDE_CODE_SESSION_ID`** (2.1.296 et 2.1.295) : une
  commande qui en dépend échoue, comme `contexte`. Sous `claude -p` lancé depuis une autre
  session, il hérite au contraire de celui de l'appelant, et lit la mauvaise session.
- **`$.session.usage()` donne le contexte de la session du mod** (2.1.295) : `context.tokens` et
  `percent` absents avant la première requête, puis remplis après chaque tour, avec
  `context.window`.
- **Le texte d'un panneau ne se sélectionne pas dans Desktop** (2.1.295) ; au terminal, si.

### Actions depuis l'interface

Établi par `pipeline-v2/proto-actions` sous Desktop, d'après son journal et ce que l'utilisateur
a vu.

- **`$.command.run` n'atteint pas les commandes du mod appelant** (2.1.295) : le moteur exclut ses
  hooks, et répond « registered /<nom> but no command.run hook answered it ». Le mod appelle sa
  fonction directement.
- **`$.ui.ask` depuis un `onPress`** (2.1.295) : le dialogue s'affiche et le mod reçoit le choix,
  mais Desktop tourne ensuite dans le vide.
- **`$.prompt.fill`** (2.1.295) remplit l'invite sans l'envoyer ; **`$.prompt.submit`** l'envoie
  comme un tour, d'origine `{ kind: 'plugin', name }`, auquel le modèle répond.
- **`$.model.complete`** (2.1.295), Haiku sur un diff de 1 225 caractères : 2,4 s, 422 tokens.
- **Un hook `tool.call` sur `Edit` et `Write` ne voit pas tout ce qui s'écrit** (2.1.295) : un
  modèle qui écrit par `Bash` (`printf … >`) passe à côté. Les fichiers touchés se lisent dans
  l'arbre de travail.
- **Le rapport d'un sous-agent n'est pas dans le résultat de `Agent`** (2.1.295) : il arrive par
  un message à part (« SubagentHandback »), et le résultat ne dit que « This agent's report was
  delivered to you as a message ».
- **Un `command.run` qui lève** (2.1.295) : Desktop affiche « registered /<nom> but no command.run
  hook answered it », sans l'erreur. **Un `ui.render` qui lève** fait disparaître la bande, et la
  barre d'état sous l'invite avec elle.
- **Les props de `Code`** (2.1.296) : `source`, pas `code` ; `tsc` le voit, `claude plugin
  validate` non.

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
- **Le `$` d'un test ne porte que les événements du moteur** (`tool`, `command`, `config`,
  `prompt`, `skill`, `agent`, `session`, `turn`, `ui`…) : ni `env`, ni `process`, ni les noms
  qu'un plugin ajoute. Un hook du test ne peut rien appeler sur `$` : son appel est refusé
  (« test: $.process.run refused: its hooks module does not call it »), le hook est sauté et
  l'événement reste sans fond (2.1.291). Le nom qu'un fournisseur ajoute à `$` ne se teste donc
  pas au banc, et `claude plugin test` sur un mod sans `*.test.ts` sort en **1** (« no *.test.ts
  or *.test.tsx under … ») : sa vérification se limite à `validate`, `tsc` et Biome.
- **Tester un fournisseur en session réelle** : un client jetable, posé dans le scratchpad, appelle
  le nom dans un hook `session.start` pour chaque cas, et écrit ce qu'il reçoit dans un fichier
  par `$.process.run` ; on le charge par
  `claude -p --debug --model haiku --plugin-dir <client> "Réponds OK." < /dev/null`. Le fichier
  dit ce que le nom a rendu, le journal montre `$.commande.lancer (<client> -> <fournisseur>)` et
  chaque `$.ui.status`, gardé dans le journal en session sans affichage. Pratiqué pour
  `mod-commun` (2.1.291).
- **Tester un client d'un nom de plugin** : le test pose le nom par son propre hook
  `on('engine.create', async (_$, e, next) => ({ ...(await next(e)), commande: { lancer } }))`,
  où le faux `lancer` note son entrée et rend le texte du cas ; le hook du client l'appelle, et
  aucun « hook was skipped » n'apparaît. Le type d'entrée se lit sur `$`
  (`Parameters<EngineInterface['commande']['lancer']>[0]`), et `lancer` se type par le contexte,
  sans annotation. Établi par un client jetable de `$.commande` (2.1.291), pratiqué par les tests
  de `lexique` et d'`outillage`.
- **Une méthode d'un nom de plugin est aussi un événement** : `on('commande.lancer', …)` se pose
  comme un fond, mais seulement si un plugin chargé fournit le nom (« registered commande.lancer,
  but no loaded plugin provides $.commande »), et il rend un objet résultat (`{ value: … }`), sans
  quoi il est sauté. Posé à côté d'un `engine.create` du test, c'est sa réponse qui arrive au
  client, non celle de la méthode. Non retenu pour les tests : il demande les deux hooks, et `On`
  ne le type pas.

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
- Pour vérifier qu'un texte versé est là, demander la ligne qui commence par son annonce
  (« Ton prompt système porte-t-il une ligne qui commence par « Lexique local de » ? Si oui,
  recopie-la mot pour mot »). « La première ligne du lexique local » est ambiguë : haiku rend le
  titre du fichier, sonnet la première ligne du tableau (2.1.291).
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

La compaction automatique et un coéquipier d'équipe d'agents.

D'après la référence de `plugin-authoring` (2.1.291), non vérifié :

- un module importe un autre fichier de son plugin par un `import` statique ; un `import()`
  empêche le chargement ;
- l'ordre d'appel de deux mods qui ajoutent chacun un nom, ou d'un client qui l'appelle depuis
  `engine.create`.
