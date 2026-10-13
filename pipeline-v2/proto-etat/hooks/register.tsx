// État du Chantier pipeline-v2, lu dans son Suivi et montré dans l'interface.
//
// Prototype jetable, sans gestion d'erreurs (Signal de dérive S3). Il répond aux éléments 1, 4, 6,
// 8, 9 et 10 des constats : Étapes, contexte et seuil de Passation, Passation en attente,
// blocages, incertitudes du Plan, dette notée. Le Suivi reste la source : le mod le relit au
// démarrage, à `/etat` et à chaque fin de tour, et garde ce qu'il en tire dans une variable du
// module, qu'un rechargement remet à zéro.
//
// `$.state` et `$.store` ne reçoivent qu'une valeur jetable, un compteur et son horodatage
// (décision Q7 du Plan) : `journal.log` note ce qui en survit à `/clear` et au redémarrage.

import type { EngineInterface, Register } from 'claude-code'

const SUIVI = '.claude/implementation/pipeline-v2.md'
const SLUG = 'pipeline-v2'
const PANNEAU = 'etat'

// Le seuil de Passation de la v1 (references/execution.md) : au-delà, la Passation se propose.
const SEUIL = 300_000

const COMPTEUR = { plugin: 'pv2-etat', key: 'compteur' } as const
const HORODATAGE = { plugin: 'pv2-etat', key: 'horodatage' } as const

type Etape = { marque: string; numero: string; titre: string }

type Etat = {
  etapes: Etape[]
  statut: string
  session: string
  passation: string | undefined
  incertitudes: string[]
  dette: string
  contexte: string
}

let etat: Etat | undefined

// `$.fs.write` réécrit le fichier entier : relire avant d'ajouter, pour que le journal garde
// d'une session à l'autre ce que `$.state` et `$.store` y ont laissé.
const noter = async ($: EngineInterface, texte: string) => {
  const chemin = `${$.plugin.root}/journal.log`
  const avant = await $.fs.read(chemin).catch(() => '')
  await $.fs.write(chemin, `${avant}${new Date(await $.clock.now()).toISOString()} ${texte}\n`)
}

const champ = (texte: string, nom: string) =>
  texte.match(new RegExp(`^"?${nom}"? = "?([^"\\n]*)"?$`, 'm'))?.[1] ?? ''

const section = (texte: string, titre: string) =>
  texte
    .split(/^## /m)
    .find(bloc => bloc.startsWith(titre))
    ?.slice(titre.length)
    .trim() ?? ''

const lire = async ($: EngineInterface): Promise<Etat> => {
  const racine = await $.session.root()
  const suivi = await $.fs.read(`${racine}/${SUIVI}`)
  const plan = await $.fs.read(`${racine}/${champ(suivi, 'plan')}`)
  const dernier = await $.process.run(['git', 'log', '-1', '--format=%s'], { cwd: racine })
  const contexte = await $.process.run(['contexte'], { cwd: racine }).catch(() => undefined)
  const usage = await $.session.usage()
  const moteur = `${usage.context.tokens ?? '?'} / ${usage.context.window} (${usage.context.percent ?? '?'} %)`

  return {
    etapes: [...section(suivi, 'Étapes').matchAll(/^- \[(.)\] (\d+)\. (.+?) —/gm)].map(m => ({
      marque: m[1] ?? '',
      numero: m[2] ?? '',
      titre: m[3] ?? '',
    })),
    statut: champ(suivi, 'statut'),
    session: champ(suivi, 'session'),
    passation: dernier.stdout.startsWith(`${SLUG}: passation`) ? dernier.stdout.trim() : undefined,
    incertitudes: (plan.match(/^INCERTITUDES :\n([\s\S]*?)\n[A-ZÀ-Ü]+ :/m)?.[1] ?? '')
      .split('\n')
      .filter(Boolean),
    dette: section(suivi, 'Dettes écartées'),
    contexte: `commande contexte : ${contexte?.exitCode === 0 ? contexte.stdout.trim() : `indisponible (${contexte?.stderr.trim() ?? 'introuvable'})`} · moteur : ${moteur}`,
  }
}

const rafraichir = async ($: EngineInterface) => {
  etat = await lire($)
  const tokens = Number(etat.contexte.match(/contexte : (\d+)/)?.[1] ?? Number.NaN)
  $.ui.status(
    Number.isNaN(tokens)
      ? `contexte ? / seuil ${SEUIL}`
      : `contexte ${tokens} / seuil ${SEUIL}${tokens > SEUIL ? ' : Passation' : ''}`,
  )
  $.ui.invalidate('ui.render')
}

const compter = async ($: EngineInterface, quand: string) => {
  const avantEtat = await $.state.get(COMPTEUR)
  const avantHeure = await $.state.get(HORODATAGE)
  const avantStore = await $.store.get('compteur')
  const heure = new Date(await $.clock.now()).toISOString()
  await $.state.set(COMPTEUR, (avantEtat.value ?? 0) + 1)
  await $.state.set(HORODATAGE, heure)
  await $.store.set('compteur', Number(avantStore ?? 0) + 1)
  await $.store.set('horodatage', heure)
  await noter(
    $,
    `${quand} : $.state trouvé ${avantEtat.value ?? 'rien'} (${avantHeure.value ?? 'rien'}), $.store trouvé ${String(avantStore ?? 'rien')}`,
  )
}

const marque = (m: string) => ({ x: 'fait', '>': 'en cours', '!': 'bloqué' })[m] ?? 'à venir'

export const register: Register = on => {
  on('session.attach', async ($, e, next) => {
    await noter($, `session.attach surface=${e.surface}`)

    return next(e)
  })

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'etat', description: 'pipeline-v2 : état du Chantier' })
    await compter($, 'session.start')
    await rafraichir($)
    if (etat?.passation !== undefined) {
      $.ui.toast(`Passation à lire : ${etat.passation}`, { timeoutMs: 15000 })
    }

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await rafraichir($)
    await noter($, `turn.complete ${etat?.contexte}`)

    return next(e)
  })

  on('command.run', { command: 'etat' }, async $ => {
    await compter($, '/etat')
    await rafraichir($)
    const ouvert = await $.ui.open({ id: PANNEAU, title: 'Chantier pipeline-v2' })
    await noter($, `ui.open ${JSON.stringify(ouvert)}`)

    return { text: 'État du Chantier ouvert.' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || etat === undefined) {
      return next(e)
    }
    const { Box, Text } = $.ui.resolve(e)
    const faites = etat.etapes.filter(etape => etape.marque === 'x').length
    const courante = etat.etapes.find(etape => etape.marque === '>' || etape.marque === '!')

    return (
      <Box flexDirection="column">
        <Text>
          {SLUG} · {faites}/{etat.etapes.length} Étapes · {etat.statut}
          {courante ? ` · Étape ${courante.numero} ${marque(courante.marque)}` : ''}
        </Text>
        {etat.passation !== undefined && <Text>Passation à lire : {etat.passation}</Text>}
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANNEAU }, async ($, e) => {
    const { Markdown } = $.ui.resolve(e)
    const compteur = await $.state.get(COMPTEUR)
    const horodatage = await $.state.get(HORODATAGE)
    const blocages = etat?.etapes.filter(etape => etape.marque === '!') ?? []

    return (
      <Markdown
        text={[
          `## Étapes — statut \`${etat?.statut}\`, session ${etat?.session}`,
          ...(etat?.etapes ?? []).map(
            etape => `- **${etape.numero}.** ${etape.titre} — *${marque(etape.marque)}*`,
          ),
          '',
          `## Contexte`,
          `${etat?.contexte} · seuil ${SEUIL}`,
          '',
          `## Passation`,
          etat?.passation ?? 'aucune en attente',
          '',
          `## Blocages`,
          blocages.length === 0
            ? 'aucun'
            : blocages.map(etape => `- ${etape.numero}. ${etape.titre}`).join('\n'),
          '',
          `## Incertitudes du Plan`,
          ...(etat?.incertitudes ?? []).map(ligne => `- ${ligne}`),
          '',
          `## Dette notée`,
          etat?.dette || 'aucune',
          '',
          `## Valeur jetable`,
          `$.state : ${compteur.value ?? 'rien'} (${horodatage.value ?? 'rien'})`,
        ].join('\n')}
      />
    )
  })
}
