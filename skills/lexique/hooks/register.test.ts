import type { EngineInterface, On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

// Le contrat du mod commun n'est pas importable hors de son dossier : on le lit sur `$`.
type CommandeLancer = Parameters<EngineInterface['commande']['lancer']>[0]

const TEXTE = 'Lexique local de /projet'

// Le banc ne charge pas `mod-commun` : le test pose lui-même `$.commande`, par `engine.create`. Le
// faux `lancer` note ce qu'il reçoit et rend `rendu`.
const commande = (on: On, rendu: string | undefined) => {
  const appels: CommandeLancer[] = []
  on('engine.create', async (_$, e, next) => {
    const built = await next(e)
    return {
      ...built,
      commande: {
        lancer: async input => {
          appels.push(input)
          return rendu
        },
      },
    }
  })
  return appels
}

// Le projet de la session, lu dans l'environnement.
const projet = (on: On, valeur: string | undefined) => on('env.get', () => ({ value: valeur }))

// L'entrée d'un lancement de sous-agent. Le typeur ne sait pas construire l'entrée entière, que le
// mod ne lit qu'en partie : d'où `as never`.
const SPAWN = {
  tool_use_id: 't1',
  prompt: 'Fais ceci.',
  description: 'essai',
  subagentType: 'analyste',
  isTeammate: false,
  fork: false,
} as never

// Ce que le sous-agent reçoit : le `prompt` que le fond de `agent.spawn` voit passer.
const fond = (on: On) => {
  const vus: string[] = []
  on('agent.spawn', (_$, e) => {
    vus.push(e.prompt)
    return { model: 'm', agentId: 'a1' }
  })
  return vus
}

test('préfixe le prompt du sous-agent du texte rendu par la commande', async ($, on) => {
  const appels = commande(on, TEXTE)
  projet(on, '/projet')
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(appels).toEqual([
    {
      argv: ['lexique', 'sous-agent', 'analyste'],
      env: { CLAUDE_PROJECT_DIR: '/projet' },
      source: 'lexique',
    },
  ])
  expect(vus[0]).toContain(TEXTE)
  expect(vus[0]?.endsWith('Fais ceci.')).toBe(true)
})

test('laisse le prompt intact quand la commande ne rend rien', async ($, on) => {
  commande(on, undefined)
  projet(on, '/projet')
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(vus[0]).toBe('Fais ceci.')
})

test("prend le répertoire de la session quand l'environnement ne nomme pas le projet", async ($, on) => {
  const appels = commande(on, TEXTE)
  projet(on, undefined)
  on('session.cwd', () => ({ value: '/session' }))
  fond(on)

  await $['agent'].spawn(SPAWN)

  expect(appels[0]?.env).toEqual({ CLAUDE_PROJECT_DIR: '/session' })
})

// L'entrée d'une composition du prompt système, que le mod ne lit pas : d'où `as never`.
const COMPOSE = {
  model: 'm',
  promptModel: 'm',
  surfaces: ['terminal'],
  tools: [],
  outputStyle: null,
  traits: [],
} as never

// Ce que la session reçoit : les sections que le fond de `prompt.compose` rend, le mod ajouté.
const fondCompose = (on: On) =>
  on('prompt.compose', () => ({ sections: [{ id: 'intro', text: 'Intro.', scope: 'shared' }] }))

test('ajoute le lexique local en section de session, après celles du moteur', async ($, on) => {
  const appels = commande(on, TEXTE)
  projet(on, '/projet')
  fondCompose(on)

  const { sections } = await $['prompt'].compose(COMPOSE)

  expect(appels).toEqual([
    { argv: ['lexique', 'session'], env: { CLAUDE_PROJECT_DIR: '/projet' }, source: 'lexique' },
  ])
  expect(sections.map(s => s.id)).toEqual(['intro', 'lexique:local'])
  expect(sections[1]).toEqual({ id: 'lexique:local', text: TEXTE, scope: 'session' })
})

test("ne lance la commande qu'une fois, pour toutes les compositions", async ($, on) => {
  const appels = commande(on, TEXTE)
  projet(on, '/projet')
  fondCompose(on)

  await $['prompt'].compose(COMPOSE)
  await $['prompt'].compose(COMPOSE)

  expect(appels.length).toBe(1)
})

test('laisse les sections du moteur quand la commande ne rend rien', async ($, on) => {
  commande(on, undefined)
  projet(on, '/projet')
  fondCompose(on)

  const { sections } = await $['prompt'].compose(COMPOSE)

  expect(sections.map(s => s.id)).toEqual(['intro'])
})

// Ce que la ligne d'état reçoit. Le fond rend `void`, que le typeur ne sait pas construire en
// résultat d'événement : d'où `as never`.
const ligneEtat = (on: On) => {
  const dits: string[] = []
  on('ui.status', (_$, e) => {
    dits.push(e.text ?? '')
    return { value: undefined } as never
  })
  return dits
}

// Sans fond pour `env.get`, la lecture du projet échoue et le hook lève. Un fond qui lèverait
// lui-même serait sauté par le moteur, avec le même effet.
const MOTIF = 'no implementation for env.get'

test("laisse le sous-agent démarrer et dit l'erreur quand le projet ne se lit pas", async ($, on) => {
  const appels = commande(on, TEXTE)
  const dits = ligneEtat(on)
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(appels.length).toBe(0)
  expect(vus[0]).toBe('Fais ceci.')
  expect(dits.length).toBe(1)
  expect(dits[0]).toBe(`lexique : ${MOTIF}`)
})

test("laisse les sections du moteur et dit l'erreur quand le projet ne se lit pas", async ($, on) => {
  commande(on, TEXTE)
  const dits = ligneEtat(on)
  fondCompose(on)

  const { sections } = await $['prompt'].compose(COMPOSE)

  expect(sections.map(s => s.id)).toEqual(['intro'])
  expect(dits).toEqual([`lexique : ${MOTIF}`])
})
