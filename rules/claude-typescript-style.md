---
paths:
  - "skills/*/hooks/**/*.ts"
  - "skills/*/types/**/*.ts"
  - ".claude/skills/*/hooks/**/*.ts"
  - "**/.claude/skills/*/hooks/**/*.ts"
---

# Convention de code TypeScript d'un mod

Le TypeScript de ce dépôt est celui des mods : des plugins de hooks que Claude Code charge depuis la
racine d'un skill. Chaque règle cite entre parenthèses un endroit du dépôt où elle est pratiquée ;
une règle qui n'a pas encore d'exemple est dite *prescrite*. Ce que les mods permettent et leurs
limites : le Shadow-skill `claude-code-mods` (`shadow-skill charge claude-code-mods`). Lancer
Biome, `tsc` et le banc : `OUTILLAGE.md`, à la racine du dépôt, qui en est l'autorité.

## Principe

- **Le moins de TypeScript possible.** La logique vit dans une commande du skill, en Python, qui
  rend le texte à verser ; le mod lance la commande et transporte sa sortie. Un mod qui analyse,
  filtre ou choisit le texte porte une logique que seul le banc des mods teste, et que l'utilisateur
  ne relit pas. (mod lexique, `register.ts` : `lexique session` et `lexique sous-agent <type>`)
- **Le code partagé entre mods passe par `$.commande`**, le nom que le mod `mod-commun` ajoute à
  `$`. Un mod ne porte pas sa propre fonction de lancement et ne recopie pas celle du mod commun :
  un import hors du dossier du plugin est refusé au chargement. (mod lexique, `register.ts`)
- **Aucun chemin ancré sur le `HOME`.** Une commande s'appelle par son nom de `bin/`, résolu par
  le `PATH` ; un fichier du projet se situe depuis `$.session.root()`. Un `~/.claude` écrit dans un
  mod suppose une installation que rien ne garantit. (mod lexique, `register.ts` : `lexique` par
  son nom)
- **Un rappel échoue ouvert, une garde échoue fermé.** Un hook qui verse du contexte dit toute
  erreur par `$.ui.status` et laisse passer l'événement intact : le moteur saute un hook qui lève,
  mais en silence, d'où un `.catch` sur son enregistrement qui dit l'erreur et rend `next(e)`. Un
  hook qui bloque attache un `.catch` qui bloque aussi : une garde qui laisse passer sur erreur ne
  garde rien. (`skills/mod-commun/hooks/register.ts`, `lancer` ; mod lexique, `register.ts`,
  `signaler`, pour le rappel ; la garde est *prescrite*)

## Typage

- Typage strict : `strict` et `noUncheckedIndexedAccess`, posés par le `tsconfig.json` que le
  moteur écrit. `tsc` ne rend aucune erreur. (mod lexique)
- Jamais d'`any`, explicite ou implicite, ni de `@ts-ignore` ou `@ts-expect-error`. Un événement se
  type par ce que `claude-code` exporte : `Register` pour le point d'entrée, `EngineInterface` pour
  le `$` d'un hook, `On` pour le fond d'un test. (mod lexique, `register.ts`)
- Une valeur que le typeur ne peut pas construire, dans un test, se force par `as never`, avec un
  commentaire qui dit ce qui manque. Hors des tests, aucune assertion de type. (mod lexique,
  `register.test.ts`, `SPAWN`)

## Structure

- Un mod tient dans `.claude-plugin/plugin.json`, `hooks/hooks.json` et un module
  `hooks/register.ts`, qui exporte `register`. Un module de plus ne se justifie que par un second
  sujet. (mod lexique)
- Un `register.ts` pose ses hooks à la suite, un `on(...)` par événement ; une fonction utilitaire
  ne sert qu'à éviter une répétition entre deux hooks. (mod lexique, `register.ts`)
- Une valeur calculée une fois se mémorise dans une variable du module (`local ??= await …`).
  (mod lexique, `register.ts`, `local`)
- Une constante de texte est définie une fois, en tête du module, avec son motif en commentaire.
  (mod lexique, `register.ts`, `ENTETE`)
- Messages, commentaires et noms locaux en français ; les noms que le moteur impose (`register`,
  `on`, `next`, les champs d'événement) restent les siens. (mod lexique)

## Documentation

- **Le module ouvre sur un en-tête** en commentaire : une ligne qui dit ce que le mod fait, puis
  les paragraphes-clés : d'où vient le texte, pourquoi ce hook plutôt qu'un autre, comment il
  échoue. (mod lexique, `register.ts` ; `skills/mod-commun/hooks/register.ts`)
- **Une JSDoc d'une ligne** sur chaque export et sur chaque membre d'un contrat de types
  (`types/index.d.ts`). Elle dit ce que le membre fait ; la signature dit le reste.
  (`skills/mod-commun/types/index.d.ts`)
- Un commentaire dit **pourquoi**, jamais ce que fait la ligne : la limite du moteur qui écarte la
  voie évidente, le cas d'échec qui reste muet. (mod lexique, `register.ts`, `prompt.compose`)

## Tests

- `claude plugin test <mod>` lance les `*.test.ts` posés à côté du module. Chaque test monte le
  fond de chaque événement que le mod appelle (`env.get`, `session.cwd`, l'événement lui-même), et
  affirme sur ce que l'appelant reçoit. (mod lexique, `register.test.ts`)
- Un test qui passe se lit jusqu'à la ligne « the engine reported » : un hook ignoré par le moteur
  (« hook was skipped ») n'y fait pas échouer le test. (Shadow-skill `claude-code-mods`, « Tester »)
- Le banc ne dit pas ce que reçoit une vraie session : chaque mod se vérifie aussi en session
  réelle, par la recette de `claude-code-mods`. (mod lexique)
- **Un client de `$.commande` pose lui-même le nom dans son test**, par un hook
  `on('engine.create', …)` qui rend `{ ...built, commande: { lancer } }` : le banc ne charge que le
  mod testé, donc pas `mod-commun`. Le faux `lancer` note ce qu'il reçoit et rend le texte du cas ;
  le test affirme sur l'appel et sur ce que l'événement transporte. Le type d'entrée se lit sur `$`
  (`Parameters<EngineInterface['commande']['lancer']>[0]`) : le contrat du fournisseur n'est pas
  importable hors de son dossier. (mod lexique, `register.test.ts`, `commande`)
- **Un fournisseur ne se teste pas au banc** : un hook de test n'appelle rien sur `$`. Son nom se
  vérifie en session réelle, par un client jetable. (`skills/mod-commun/SKILL.md`, « Vérifier le
  mod »)

## Configuration

- `tsconfig.json` n'est pas versionné : celui d'un mod étend le fichier que le moteur pose dans
  `.claude-plugin/types/`, lui-même ignoré, et ne vaudrait rien sur une machine où le mod ne s'est
  jamais chargé. `tsc` passe par la recette d'`OUTILLAGE.md`, avec un `tsconfig.json` temporaire
  hors du mod. (`.gitignore`)
- Le format se tient par Biome, configuré une fois à la racine du dépôt (`biome.json`) : espaces,
  indentation 2, largeur 100, guillemets simples, point-virgule et parenthèses du paramètre d'une
  flèche seulement là où ils sont requis.
  Aucune configuration dans le mod. (`biome.json`)
