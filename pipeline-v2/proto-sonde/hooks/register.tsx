// Sonde de pipeline-v2 : montre chaque surface de Claude Code et note ce que le moteur en fait.
//
// Prototype jetable, sans gestion d'erreurs (Signal de dérive S3) : il sert à répondre à la
// question qui décide du Chantier, ce que Claude Code suivi au navigateur affiche d'un mod.
// La commande `/sonde` ouvre un panneau, pose une ligne d'état, un toast et une notification ;
// une bande au-dessus de l'invite est dessinée dès le démarrage.
//
// Le journal, `journal.log` à la racine du mod, dit ce que le moteur a fait : chaque client qui
// s'attache, chaque demande de dessin par surface, le placement du panneau, le sort de la
// notification. L'utilisateur dit ce qui s'est vu ; les deux font le constat.

import type { EngineInterface, Register } from 'claude-code'

const PANNEAU = 'sonde'

// `$.fs.write` réécrit le fichier entier : le journal se tient ici et se réécrit à chaque ligne.
const lignes: string[] = []

// Une demande de dessin revient à chaque rafraîchissement : seule une combinaison nouvelle
// de composant, surface et taille mérite une ligne.
const dessins = new Set<string>()

const noter = async ($: EngineInterface, texte: string) => {
  lignes.push(`${new Date(await $.clock.now()).toISOString()} ${texte}`)
  await $.fs.write(`${$.plugin.root}/journal.log`, `${lignes.join('\n')}\n`)
}

const noterDessin = async (
  $: EngineInterface,
  composant: string,
  surface: string,
  viewport: unknown,
) => {
  const cle = `${composant} ${surface} ${JSON.stringify(viewport ?? null)}`
  if (dessins.has(cle)) {
    return
  }
  dessins.add(cle)
  await noter($, `ui.render ${cle}`)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'sonde',
      description: 'pipeline-v2 : ouvre un panneau, pose ligne d’état, toast et notification',
    })
    await noter($, `session.start surfaces=${JSON.stringify(await $.session.surfaces())}`)

    return next(e)
  })

  on('session.attach', async ($, e, next) => {
    await noter(
      $,
      `session.attach surface=${e.surface} clientId=${e.clientId} viewport=${JSON.stringify(e.viewport ?? null)}`,
    )

    return next(e)
  })

  on('command.run', { command: 'sonde' }, async $ => {
    await noter($, `/sonde surfaces=${JSON.stringify(await $.session.surfaces())}`)
    const ouvert = await $.ui.open({ id: PANNEAU, title: 'Sonde pipeline-v2' })
    await noter($, `ui.open ${JSON.stringify(ouvert)}`)
    $.ui.status('pv2-sonde : ligne d’état')
    $.ui.toast('pv2-sonde : toast', { timeoutMs: 15000 })
    const notifie = await $.ui.notify('pv2-sonde : notification', { title: 'pipeline-v2' })
    await noter($, `ui.notify ${JSON.stringify(notifie)}`)

    return { text: 'Sonde lancée : panneau, ligne d’état, toast, notification.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANNEAU }, async ($, e) => {
    await noterDessin($, 'Pane', e.surface, e.viewport)
    const { Box, Button, Markdown } = $.ui.resolve(e)

    return (
      <Box flexDirection="column">
        <Markdown
          text={[
            `**Panneau de la sonde**, surface \`${e.surface}\`, placement \`${e.props.placement}\`.`,
            '',
            '- un lien [https](https://code.claude.com/docs)',
            `- un lien [file](file://${$.plugin.root}/../README.md)`,
          ].join('\n')}
        />
        <Button
          key="appui"
          label="Appuyer"
          onPress={async () => {
            await noter($, `ui.press panneau surface=${e.surface}`)
            $.ui.toast(`pv2-sonde : bouton du panneau pressé (${e.surface})`)
          }}
        />
      </Box>
    )
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    await noterDessin($, 'AbovePrompt', e.surface, e.viewport)
    if (e.props.hasSurvey) {
      return next(e)
    }
    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box>
        <Text>pv2-sonde : bande au-dessus de l’invite ({e.surface}) </Text>
        <Button
          key="bande"
          label="Appuyer"
          onPress={async () => {
            await noter($, `ui.press bande surface=${e.surface}`)
            $.ui.toast(`pv2-sonde : bouton de la bande pressé (${e.surface})`)
          }}
        />
      </Box>
    )
  })
}
