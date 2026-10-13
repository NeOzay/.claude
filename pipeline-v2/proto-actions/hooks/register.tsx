// Actions du Chantier pipeline-v2 : ce qu'un geste dans l'interface peut déclencher.
//
// Prototype jetable, sans gestion d'erreurs (Signal de dérive S3). Il répond aux éléments 2, 3 et
// 11 des constats : proposition de commit générée, ouverture du Suivi, du Brief et de l'audit,
// choix de fin d'Étape sans tour du modèle.
//
// Aucun bouton ne commit ni ne modifie le Suivi : chacun essaie une voie du moteur et l'écrit au
// journal. Les quatre choix de fin d'Étape essaient chacun une voie différente — soumettre un
// message, remplir l'invite, lancer une commande, poser une question dans le dialogue du moteur —
// pour voir laquelle se passe du modèle.

import type { EngineInterface, Register } from 'claude-code'

const IMPL = '.claude/implementation'
const SLUG = 'pipeline-v2'
const FICHIER = 'fichier'
const PROPOSITION = 'proposition'

// Le diff tronqué : assez pour un message de commit, pas de quoi remplir la fenêtre du modèle.
const DIFF_MAX = 20_000

type Ouvert = { titre: string; chemin: string; texte: string }

let ouvert: Ouvert | undefined
let proposition = ''
let choixVisibles = false

const noter = async ($: EngineInterface, texte: string) => {
  const chemin = `${$.plugin.root}/journal.log`
  const avant = await $.fs.read(chemin).catch(() => '')
  await $.fs.write(chemin, `${avant}${new Date(await $.clock.now()).toISOString()} ${texte}\n`)
}

const ouvrir = async ($: EngineInterface, titre: string, relatif: string) => {
  const racine = await $.session.root()
  const chemin = `${racine}/${relatif}`
  const texte = await $.fs.read(chemin).catch(() => '*absent*')
  ouvert = { titre, chemin, texte }
  const place = await $.ui.open({ id: FICHIER, title: titre })
  await noter($, `/${titre} ${relatif} ui.open ${JSON.stringify(place)}`)
  $.ui.invalidate('ui.render')

  return { text: `${titre} ouvert.` }
}

const dernierAudit = async ($: EngineInterface) => {
  const dossier = `${IMPL}/${SLUG}.audit`
  const fichiers = await $.fs.list(dossier).catch(() => [])
  const nom = fichiers
    .map(entree => entree.name)
    .sort()
    .at(-1)

  return nom === undefined ? `${dossier}/aucun-audit` : `${dossier}/${nom}`
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    for (const [name, description] of [
      ['suivi', 'pipeline-v2 : ouvre le Suivi'],
      ['brief', 'pipeline-v2 : ouvre le Brief'],
      ['audit', 'pipeline-v2 : ouvre le dernier audit'],
      ['fin', 'pipeline-v2 : montre les choix de fin d’Étape'],
      ['proposer', 'pipeline-v2 : propose un message de commit pour le diff'],
    ] as const) {
      await $.command.register({ name, description })
    }

    return next(e)
  })

  on('command.run', { command: 'suivi' }, $ => ouvrir($, 'suivi', `${IMPL}/${SLUG}.md`))
  on('command.run', { command: 'brief' }, $ => ouvrir($, 'brief', `${IMPL}/${SLUG}.brief.md`))
  on('command.run', { command: 'audit' }, async $ => ouvrir($, 'audit', await dernierAudit($)))

  on('command.run', { command: 'fin' }, async $ => {
    choixVisibles = true
    $.ui.invalidate('ui.render')
    await noter($, '/fin : choix montrés')

    return { text: 'Choix de fin d’Étape montrés au-dessus de l’invite.' }
  })

  on('command.run', { command: 'proposer' }, async $ => {
    const racine = await $.session.root()
    const stat = await $.process.run(['git', 'diff', 'HEAD', '--stat'], { cwd: racine })
    const diff = await $.process.run(['git', 'diff', 'HEAD'], { cwd: racine })
    const debut = await $.clock.now()
    const reponse = await $.model.complete({
      model: 'haiku',
      system:
        'Tu rédiges un message de commit Conventional Commits, en français, à partir d’un diff. Rends le message seul : un titre de 72 caractères au plus, une ligne vide, puis au plus cinq puces.',
      prompt: `${stat.stdout}\n\n${diff.stdout.slice(0, DIFF_MAX)}`,
      maxTokens: 400,
    })
    const duree = (await $.clock.now()) - debut
    proposition = reponse.isAnswered ? reponse.text.trim() : `échec : ${reponse.reason}`
    await noter(
      $,
      `/proposer : ${diff.stdout.length} caractères de diff, ${duree} ms, ${reponse.isAnswered ? `${reponse.usage.output_tokens} tokens rendus` : 'pas de réponse'}`,
    )
    const place = await $.ui.open({ id: PROPOSITION, title: 'Commit proposé' })
    await noter($, `ui.open ${JSON.stringify(place)}`)
    $.ui.invalidate('ui.render')

    return { text: 'Proposition de commit ouverte.' }
  })

  on('ui.render', { component: 'Pane', requestId: FICHIER }, async ($, e) => {
    const { Box, Markdown } = $.ui.resolve(e)

    return (
      <Box flexDirection="column">
        <Markdown text={`[Ouvrir ${ouvert?.chemin}](file://${ouvert?.chemin})`} />
        <Markdown text={ouvert?.texte ?? ''} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PROPOSITION }, async ($, e) => {
    const { Box, Button, Code } = $.ui.resolve(e)

    return (
      <Box flexDirection="column">
        <Code source={proposition} />
        <Box>
          <Button
            key="valider"
            label="Valider"
            onPress={async () => {
              await noter($, `proposition validée (surface ${e.surface}), rien n’est commité`)
              $.ui.toast('Proposition validée : journalisée, rien n’est commité.')
            }}
          />
          <Button
            key="refuser"
            label="Refuser"
            onPress={async () => {
              await noter($, `proposition refusée (surface ${e.surface})`)
              await $.ui.close({ id: PROPOSITION })
            }}
          />
        </Box>
      </Box>
    )
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || !choixVisibles) {
      return next(e)
    }
    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box flexDirection="column">
        <Text>Étape terminée — choix (test pv2-actions, rien n’est commité) :</Text>
        <Box>
          <Button
            key="passer"
            label="1. Valider et passer"
            onPress={async () => {
              await noter($, `choix passer (surface ${e.surface}) : $.prompt.submit`)
              const r = await $.prompt.submit({
                text: 'Test pv2-actions : bouton « Valider et passer » pressé. Ne fais rien ; réponds seulement « reçu ».',
              })
              await noter($, `$.prompt.submit → ${JSON.stringify(r)}`)
            }}
          />
          <Button
            key="attendre"
            label="2. Valider et attendre"
            onPress={async () => {
              await noter($, `choix attendre (surface ${e.surface}) : $.prompt.fill`)
              const r = await $.prompt.fill({ text: 'Valider et attendre' })
              await noter($, `$.prompt.fill → ${JSON.stringify(r)}`)
            }}
          />
          <Button
            key="suivi"
            label="3. Voir le Suivi"
            onPress={async () => {
              await noter($, `choix suivi (surface ${e.surface}) : $.command.run`)
              const r = await $.command.run({ command: 'suivi' })
              await noter($, `$.command.run → ${JSON.stringify(r)}`)
            }}
          />
          <Button
            key="autre"
            label="4. Autre chose"
            onPress={async () => {
              await noter($, `choix autre (surface ${e.surface}) : $.ui.ask`)
              const r = await $.ui.ask('Que faire de cette Étape ?', ['Retouche', 'Passation'])
              await noter($, `$.ui.ask → ${r}`)
              choixVisibles = false
              $.ui.invalidate('ui.render')
            }}
          />
        </Box>
      </Box>
    )
  })
}
