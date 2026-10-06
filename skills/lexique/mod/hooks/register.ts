import type { EngineInterface, Register } from 'claude-code'

// Le `$` d'un hook, tel que tous les hooks du mod le reçoivent.
type Moteur = EngineInterface

// Le texte vient de `lexique sous-agent` : le mod ne porte aucune règle d'injection, il transporte.
// Il passe par le `prompt` du sous-agent : un hook `SubagentStart` de settings.json plafonne son
// `additionalContext` à 10 000 caractères, et `$.session.append` ne peut pas viser le sous-agent
// avant `next` : son `agentId` n'existe qu'après.
const ENTETE = 'Lexique versé au démarrage de ce sous-agent par le mod lexique-sous-agent :'

// Lance une commande de `lexique` et rend son texte, ou rien. Échec ouvert : un
// rappel n'empêche ni une session ni un sous-agent de démarrer, une erreur se dit sur la ligne d'état.
const lancer = async ($: Moteur, ...commande: string[]): Promise<string | undefined> => {
  try {
    const home = await $.env.get('HOME')
    const projet = (await $.env.get('CLAUDE_PROJECT_DIR')) ?? (await $.session.cwd())
    const ran = await $.process.run(
      ['python3', `${home}/.claude/skills/lexique/scripts/lexique-cli.py`, ...commande],
      { env: { CLAUDE_PROJECT_DIR: projet } },
    )
    // Une commande qui échoue (CLI introuvable, erreur d'appel) : à dire. Sous Python < 3.12 la CLI
    // sort en 0 sans rien rendre : ce cas-là reste muet.
    if (ran.exitCode !== 0) {
      $.ui.status(`lexique-sous-agent : la commande rend ${ran.exitCode} ${ran.stderr.slice(0, 60)}`)
      return undefined
    }
    return ran.stdout.trim() || undefined
  } catch (erreur) {
    $.ui.status(`lexique-sous-agent : ${String(erreur).slice(0, 60)}`)
    return undefined
  }
}

export const register: Register = on => {
  // Le lexique local de la session principale : un hook `SessionStart` plafonne son contexte à
  // 10 000 caractères et n'en garde qu'un aperçu de 2 Ko. Une section du prompt système n'a pas ce
  // plafond, survit à `/clear`, à la compaction et à la reprise, sans se dupliquer, et ne va pas
  // aux sous-agents. Ni `prompt.context` (tous les sous-agents le
  // reçoivent, isolés compris) ni `$.session.append` à `session.start` (perdu à `/clear`, dupliqué à
  // chaque reprise) n'y suffisent. Le texte vient de `lexique session`, lancé tant qu'il ne rend rien.
  let local: string | undefined
  on('prompt.compose', async ($, e, next) => {
    const composition = await next(e)
    local ??= await lancer($, 'session')
    if (!local) return composition
    return { sections: [...composition.sections, { id: 'lexique-sous-agent:local', text: local, scope: 'session' }] }
  })

  on('agent.spawn', async ($, e, next) => {
    const texte = await lancer($, 'sous-agent', e.subagentType)
    return next(texte ? { ...e, prompt: `${ENTETE}\n\n${texte}\n\n---\n\n${e.prompt}` } : e)
  })
}
