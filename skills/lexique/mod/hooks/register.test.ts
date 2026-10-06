import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

const TEXTE = 'Lexique local de /p'
const SORTIE = `${TEXTE}\n`

const execution = (stdout: string, exitCode = 0) => ({
  value: { exitCode, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false },
})

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
  const vus: { prompt: string }[] = []
  on('agent.spawn', (_$, e) => {
    vus.push({ prompt: e.prompt })
    return { model: 'm', agentId: 'a1' }
  })
  return vus
}

test('préfixe le prompt du sous-agent du texte rendu par la commande', async ($, on) => {
  const appels: { argv: readonly string[]; projet?: string }[] = []
  on('env.get', (_$, e) => ({ value: e.name === 'HOME' ? '/h' : '/projet' }))
  on('process.run', (_$, e) => {
    appels.push({ argv: e.argv, projet: e.init?.env?.CLAUDE_PROJECT_DIR })
    return execution(SORTIE)
  })
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(appels.length).toBe(1)
  expect(appels[0]?.argv).toEqual([
    'python3',
    '/h/.claude/skills/lexique/scripts/lexique-cli.py',
    'sous-agent',
    'analyste',
  ])
  expect(appels[0]?.projet).toBe('/projet')
  expect(vus[0]?.prompt).toContain(TEXTE)
  expect(vus[0]?.prompt.endsWith('Fais ceci.')).toBe(true)
})

test('laisse le prompt intact quand la commande ne rend rien', async ($, on) => {
  on('env.get', () => ({ value: '/h' }))
  on('process.run', () => execution(''))
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(vus[0]?.prompt).toBe('Fais ceci.')
})

test('dit sur la ligne d\'état que la commande échoue', async ($, on) => {
  const dits: string[] = []
  on('env.get', () => ({ value: '/h' }))
  on('process.run', () => ({
    value: { exitCode: 2, stdout: '', stderr: 'cli introuvable', isStdoutTruncated: false, isStderrTruncated: false },
  }))
  on('ui.status', (_$, e) => {
    dits.push(e.text ?? '')
    return { value: undefined } as never
  })
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(vus[0]?.prompt).toBe('Fais ceci.')
  expect(dits.length).toBe(1)
  expect(dits[0]).toContain('cli introuvable')
})

const COMPOSE = {
  model: 'm',
  promptModel: 'm',
  surfaces: ['terminal'],
  tools: [],
  outputStyle: null,
  traits: [],
} as never

// Ce que la session reçoit : les sections que le fond de `prompt.compose` rend, le mod ajouté.
const fondCompose = (on: On) => on('prompt.compose', () => ({ sections: [{ id: 'intro', text: 'Intro.', scope: 'shared' }] }))

test('ajoute le lexique local en section de session, après celles du moteur', async ($, on) => {
  const appels: { argv: readonly string[]; projet?: string }[] = []
  on('env.get', (_$, e) => ({ value: e.name === 'HOME' ? '/h' : '/projet' }))
  on('process.run', (_$, e) => {
    appels.push({ argv: e.argv, projet: e.init?.env?.CLAUDE_PROJECT_DIR })
    return execution(`${TEXTE}\n`)
  })
  fondCompose(on)

  const { sections } = await $['prompt'].compose(COMPOSE)

  expect(appels[0]?.argv).toEqual(['python3', '/h/.claude/skills/lexique/scripts/lexique-cli.py', 'session'])
  expect(appels[0]?.projet).toBe('/projet')
  expect(sections.map(s => s.id)).toEqual(['intro', 'lexique-sous-agent:local'])
  expect(sections[1]).toEqual({ id: 'lexique-sous-agent:local', text: TEXTE, scope: 'session' })
})

test('ne lance la commande qu\'une fois, pour toutes les compositions', async ($, on) => {
  let lancements = 0
  on('env.get', () => ({ value: '/h' }))
  on('process.run', () => {
    lancements++
    return execution(`${TEXTE}\n`)
  })
  fondCompose(on)

  await $['prompt'].compose(COMPOSE)
  await $['prompt'].compose(COMPOSE)

  expect(lancements).toBe(1)
})

test('laisse les sections du moteur quand la commande ne rend rien', async ($, on) => {
  on('env.get', () => ({ value: '/h' }))
  on('process.run', () => execution(''))
  fondCompose(on)

  const { sections } = await $['prompt'].compose(COMPOSE)

  expect(sections.map(s => s.id)).toEqual(['intro'])
})

test('laisse les sections du moteur quand la commande échoue', async ($, on) => {
  on('env.get', () => ({ value: '/h' }))
  on('process.run', () => execution('', 2))
  on('ui.status', () => ({ value: undefined }) as never)
  fondCompose(on)

  const { sections } = await $['prompt'].compose(COMPOSE)

  expect(sections.map(s => s.id)).toEqual(['intro'])
})
