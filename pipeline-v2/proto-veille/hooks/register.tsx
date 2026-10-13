// Veille du Chantier pipeline-v2 : ce que des hooks voient pendant que le modèle travaille.
//
// Prototype jetable, sans gestion d'erreurs (Signal de dérive S3). Il répond aux éléments 5, 7 et
// 12 des constats : fichiers touchés face aux fichiers de l'Étape en cours, état et verdict des
// sous-agents, Signaux de dérive vérifiables par commande.
//
// Les fichiers prévus sont ceux de la ligne de l'Étape `[>]` du Suivi, entre accents graves, avant
// « vérif ». Les Signaux se relancent après chaque `Edit` ou `Write`, chacun par sa commande du
// Brief ; un toast dit celui qui tombe. Un sous-agent se suit par l'appel de l'outil `Agent` :
// lancé avant `next`, terminé quand `next` rend, son verdict lu dans sa réponse.
//
// `/lever` fait lever la bande, `/lever-commande` fait lever la commande elle-même : ce que le
// moteur montre d'un hook qui échoue est la matière de la politique d'échec.

import type { EngineInterface, Register } from 'claude-code'

const SUIVI = '.claude/implementation/pipeline-v2.md'

// Les Signaux de dérive du Brief qu'une commande vérifie : elle sort 0 quand le Signal tombe.
const SIGNAUX = {
  S1: 'test -n "$(git diff master --stat -- skills/implementation-tracker skills/intent-brief skills/git-smart-commit)"',
  S2: 'test -n "$(git diff master --name-only -- skills .claude/skills settings.json)" || grep -q CLAUDE_CODE_PLUGIN_DIRS settings.json',
  S6: 'test -n "$(git diff master -- LEXIQUE.md)"',
} as const

type Agent = { id: string; type: string; etat: string; verdict: string }

let prevus: string[] = []
let etape = ''
const horsPrevus = new Set<string>()
let tombes: string[] = []
const agents: Agent[] = []
let leve = false

const noter = async ($: EngineInterface, texte: string) => {
  const chemin = `${$.plugin.root}/journal.log`
  const avant = await $.fs.read(chemin).catch(() => '')
  await $.fs.write(chemin, `${avant}${new Date(await $.clock.now()).toISOString()} ${texte}\n`)
}

const lirePrevus = async ($: EngineInterface) => {
  const suivi = await $.fs.read(`${await $.session.root()}/${SUIVI}`)
  const ligne = suivi.match(/^- \[>\] (\d+)\. ([\s\S]*?)— vérif/m)
  etape = ligne?.[1] ?? '?'
  prevus = [...(ligne?.[2] ?? '').matchAll(/`([^`]+)`/g)].map(m => m[1] ?? '')
}

const verifier = async ($: EngineInterface) => {
  const racine = await $.session.root()
  const avant = tombes
  tombes = []
  for (const [nom, commande] of Object.entries(SIGNAUX)) {
    const r = await $.process.run(['bash', '-c', commande], { cwd: racine })
    if (r.exitCode === 0) {
      tombes.push(nom)
    }
  }
  const nouveaux = tombes.filter(nom => !avant.includes(nom))
  if (nouveaux.length > 0) {
    $.ui.toast(`Signal de dérive : ${nouveaux.join(', ')}`, { timeoutMs: 15000 })
  }
  await noter($, `signaux tombés : ${tombes.join(', ') || 'aucun'}`)
  $.ui.invalidate('ui.render')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'lever', description: 'pv2-veille : fait lever la bande' })
    await $.command.register({
      name: 'lever-commande',
      description: 'pv2-veille : fait lever cette commande',
    })
    await lirePrevus($)
    await noter($, `session.start : Étape ${etape}, prévus ${JSON.stringify(prevus)}`)
    await verifier($)

    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (e.tool !== 'Edit' && e.tool !== 'Write') {
      return ran
    }
    const racine = await $.session.root()
    const relatif = e.file_path.startsWith(`${racine}/`)
      ? e.file_path.slice(racine.length + 1)
      : e.file_path
    const estPrevu = prevus.some(prevu => relatif === prevu || relatif.startsWith(prevu))
    if (!estPrevu) {
      horsPrevus.add(relatif)
    }
    await noter($, `${e.tool} ${relatif} : ${estPrevu ? 'prévu' : 'hors prévus'}`)
    await verifier($)

    return ran
  })

  on('tool.call', { tool: 'Agent' }, async ($, e, next) => {
    const agent: Agent = {
      id: e.tool_use_id,
      type: e.subagent_type ?? 'general-purpose',
      etat: 'en cours',
      verdict: '',
    }
    agents.push(agent)
    await noter($, `Agent lancé : ${agent.type} (${e.description})`)
    $.ui.invalidate('ui.render')
    const ran = await next(e)
    const texte = ran.text ?? JSON.stringify(ran.result ?? '')
    agent.etat = ran.deny !== undefined ? 'refusé' : ran.isError === true ? 'en erreur' : 'terminé'
    agent.verdict = texte.match(/VERDICT\s*:\s*([A-ZÉ ]+)/)?.[1]?.trim() ?? ''
    await noter(
      $,
      `Agent ${agent.etat} : ${agent.type}, verdict « ${agent.verdict || 'aucun'} », ${texte.length} caractères`,
    )
    $.ui.invalidate('ui.render')

    return ran
  })

  on('command.run', { command: 'lever' }, async () => {
    leve = true

    return { text: 'La bande va lever à son prochain dessin.' }
  })

  on('command.run', { command: 'lever-commande' }, async () => {
    throw new Error('pv2-veille : erreur voulue dans command.run')
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (leve) {
      throw new Error('pv2-veille : erreur voulue dans ui.render')
    }
    if (e.props.hasSurvey) {
      return next(e)
    }
    const { Box, Text } = $.ui.resolve(e)
    const dernier = agents.at(-1)

    return (
      <Box flexDirection="column">
        <Text>
          Étape {etape} · prévus : {prevus.join(', ') || 'aucun'}
          {horsPrevus.size > 0 ? ` · hors prévus : ${[...horsPrevus].join(', ')}` : ''}
        </Text>
        <Text>Signaux : {tombes.length === 0 ? 'aucun tombé' : `tombés ${tombes.join(', ')}`}</Text>
        {dernier && (
          <Text>
            Agents : {agents.filter(agent => agent.etat === 'en cours').length} en cours · dernier{' '}
            {dernier.type} {dernier.etat}
            {dernier.verdict ? ` — ${dernier.verdict}` : ''}
          </Text>
        )}
      </Box>
    )
  })
}
