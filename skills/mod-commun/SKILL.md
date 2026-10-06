---
name: mod-commun
description: >
  Porte le mod commun, qui ajoute `$.commande` au moteur de Claude Code : le lancement d'une
  commande, partagé entre les mods, qui rend sa sortie et dit un échec sur la ligne d'état. Skill
  exclusivement interne : il ne sert qu'aux mods, ni au modèle ni à l'utilisateur. N'écrit aucun
  texte à verser : il transporte la sortie de la commande que le mod client lui donne.
disable-model-invocation: true
user-invocable: false
---

# mod-commun — le code que les mods partagent

Ce skill ne porte qu'un mod. Le mod se charge seul, depuis la racine du skill : aucun réglage ne le
nomme. Ce que les mods permettent, leurs limites et leurs tests : le Shadow-skill
`claude-code-mods` (`shadow-skill charge claude-code-mods`). Leur code :
`rules/claude-typescript-style.md`.

**Pourquoi un mod commun** : un mod n'importe rien hors de son dossier, le chargement le refuse. Le
seul code qu'un mod appelle chez un autre est un nom que ce dernier ajoute à `$` : le mod commun
ajoute `$.commande`, et chaque mod qui lance une commande passe par lui plutôt que d'écrire sa
propre fonction de lancement.

## `$.commande.lancer`

```ts
const texte = await $.commande.lancer({
  argv: ['lexique', 'session'],             // sans shell ; le premier se résout par le PATH
  env: { CLAUDE_PROJECT_DIR: projet },      // facultatif, posé sur l'environnement de la session
  cwd: racine,                              // facultatif ; absent, celui de la session
  source: 'lexique',                        // le mod appelant, en tête d'un échec affiché
})
```

`lancer` rend la sortie de la commande sans ses blancs de tête et de fin. Il rend `undefined`
quand la sortie est vide, et quand la commande sort non nul ou ne se lance pas : il dit alors
l'échec sur la ligne d'état, `<source> : …`. Il ne lève jamais. Le contrat de types est
[`types/index.d.ts`](types/index.d.ts), et le code [`hooks/register.ts`](hooks/register.ts).

**Échec ouvert** : un client qui reçoit `undefined` laisse l'événement intact. Un rappel qui ne se
calcule pas n'empêche ni une session ni un sous-agent de démarrer.

## Appeler `$.commande` depuis un mod

- Le module du client appelle `$.commande.lancer(...)` dans un de ses hooks. Le moteur n'accepte
  un appel à `$` que si le module l'écrit : il le lit dans le code avant de le charger.
- Le `plugin.json` du client déclare `"dependencies": ["mod-commun"]`. L'appel aboutit sans
  cette ligne, mais elle dit de quoi le client dépend.
- Le journal d'un `claude -p --debug` montre chaque appel : `$.commande.lancer (<client> ->
  mod-commun)`, puis `$.process.run (mod-commun)`, attribué au mod commun et non au client.

## Vérifier le mod

Le banc des mods ne l'exerce pas : un hook de test n'appelle rien sur `$`, et le `$` d'un test ne
porte pas les noms qu'un plugin ajoute. Le mod n'a donc pas de `*.test.ts`, et
`claude plugin test` sort en 1 faute de test : au banc, il se vérifie par `claude plugin validate`,
`tsc` et Biome. `lancer` se vérifie en session réelle, par un client
jetable chargé par `claude -p --debug --plugin-dir <client>` : la recette est dans
`claude-code-mods`, « Tester ».
