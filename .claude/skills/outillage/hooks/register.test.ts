import type { EngineInterface, On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

// Le contrat du mod commun n'est pas importable hors de son dossier : on le lit sur `$`.
type CommandeLancer = Parameters<EngineInterface['commande']['lancer']>[0]

const RAPPEL = 'Outillage de ce dépôt (/depot/OUTILLAGE.md) :'

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

// La racine de la session.
const racine = (on: On) => on('session.root', () => ({ value: '/depot' }))

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

test('préfixe le prompt du sous-agent du rappel, lancé depuis la racine', async ($, on) => {
  const appels = commande(on, RAPPEL)
  racine(on)
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(appels).toEqual([
    {
      argv: ['/depot/.claude/skills/outillage/scripts/rappel.sh'],
      cwd: '/depot',
      source: 'outillage',
    },
  ])
  expect(vus[0]).toBe(`${RAPPEL}\n\n---\n\nFais ceci.`)
})

test('laisse le prompt intact quand le rappel ne rend rien', async ($, on) => {
  commande(on, undefined)
  racine(on)
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(vus[0]).toBe('Fais ceci.')
})

// Sans fond pour `session.root`, la lecture de la racine échoue et le hook lève.
test("laisse le sous-agent démarrer et dit l'erreur quand la racine ne se lit pas", async ($, on) => {
  const appels = commande(on, RAPPEL)
  const dits = ligneEtat(on)
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(appels.length).toBe(0)
  expect(vus[0]).toBe('Fais ceci.')
  expect(dits).toEqual(['outillage : no implementation for session.root'])
})
