import type { Register } from 'claude-code'

// Le texte vient de `lexique sous-agent` : le mod ne porte aucune règle d'injection, il transporte.
// Il passe par le `prompt` du sous-agent : un hook `SubagentStart` de settings.json plafonne son
// `additionalContext` à 10 000 caractères, et `$.session.append` est refusé à ce moment (« no
// running loop »), la boucle du sous-agent n'existant pas encore.
const ENTETE = 'Lexique versé au démarrage de ce sous-agent par le mod lexique-sous-agent :'

export const register: Register = on => {
  on('agent.spawn', async ($, e, next) => {
    // Échec ouvert, comme `lexique sous-agent` : un rappel n'empêche pas un sous-agent de démarrer.
    try {
      const home = await $.env.get('HOME')
      const projet = (await $.env.get('CLAUDE_PROJECT_DIR')) ?? (await $.session.cwd())
      const ran = await $.process.run(
        ['python3', `${home}/.claude/skills/lexique/scripts/lexique-cli.py`, 'sous-agent'],
        { stdin: JSON.stringify({ agent_type: e.subagentType }), env: { CLAUDE_PROJECT_DIR: projet } },
      )
      if (ran.exitCode === 0 && ran.stdout.trim() !== '') {
        const sortie = JSON.parse(ran.stdout) as {
          hookSpecificOutput?: { additionalContext?: string }
        }
        const texte = sortie.hookSpecificOutput?.additionalContext
        if (texte) return next({ ...e, prompt: `${ENTETE}\n\n${texte}\n\n---\n\n${e.prompt}` })
      } else if (ran.exitCode !== 0) {
        // Une commande qui échoue (CLI introuvable, erreur d'appel) : à dire. Sous Python < 3.12 la CLI
        // sort en 0 sans rien rendre, pour `sous-agent` : ce cas-là reste muet.
        $.ui.status(`lexique-sous-agent : la commande rend ${ran.exitCode} ${ran.stderr.slice(0, 60)}`)
      }
    } catch (erreur) {
      $.ui.status(`lexique-sous-agent : ${String(erreur).slice(0, 60)}`)
    }
    return next(e)
  })
}
