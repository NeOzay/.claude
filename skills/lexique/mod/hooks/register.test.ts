import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

const TEXTE = 'Lexique local de /p'
const SORTIE = JSON.stringify({
  hookSpecificOutput: { hookEventName: 'SubagentStart', additionalContext: TEXTE },
})

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
  const appels: { argv: readonly string[]; stdin?: string; projet?: string }[] = []
  on('env.get', (_$, e) => ({ value: e.name === 'HOME' ? '/h' : '/projet' }))
  on('process.run', (_$, e) => {
    appels.push({ argv: e.argv, stdin: e.init?.stdin, projet: e.init?.env?.CLAUDE_PROJECT_DIR })
    return execution(SORTIE)
  })
  const vus = fond(on)

  await $['agent'].spawn(SPAWN)

  expect(appels.length).toBe(1)
  expect(appels[0]?.argv).toEqual(['python3', '/h/.claude/skills/lexique/scripts/lexique-cli.py', 'sous-agent'])
  expect(appels[0]?.stdin).toBe(JSON.stringify({ agent_type: 'analyste' }))
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

test('échoue ouvert quand la sortie est illisible', async ($, on) => {
  on('env.get', () => ({ value: '/h' }))
  on('process.run', () => execution('pas du json'))
  on('ui.status', () => ({ value: undefined }) as never)
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
