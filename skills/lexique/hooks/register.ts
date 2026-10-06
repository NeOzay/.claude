// Mod lexique : verse le lexique local à la session principale et à un sous-agent à son lancement.
//
// LE TEXTE VIENT DE LA COMMANDE : `lexique session` et `lexique sous-agent <type>` décident de ce
// qui est versé ; le mod ne porte aucune règle d'injection, il transporte leur sortie. Il les lance
// par `$.commande.lancer`, que le mod commun fournit.
//
// PAS DE HOOK DE `settings.json` : un hook `SessionStart` ou `SubagentStart` plafonne son contexte
// à 10 000 caractères et n'en garde qu'un aperçu de 2 Ko.
//
// ÉCHEC OUVERT : une commande qui échoue se dit sur la ligne d'état, par le mod commun, et laisse la
// session et le sous-agent démarrer sans lexique. Une erreur du hook lui-même (lecture du projet) se
// dit par le `.catch` de son enregistrement, qui laisse passer l'événement intact.
import type { EngineInterface, HookFailure, Register } from 'claude-code'

const ENTETE = 'Lexique versé au démarrage de ce sous-agent par le mod lexique :'

// Le projet dont la commande lit le lexique local : celui de la session, que le processus lancé
// n'hérite pas toujours.
const projet = async ($: EngineInterface) =>
  (await $.env.get('CLAUDE_PROJECT_DIR')) ?? (await $.session.cwd())

// Le moteur saute un hook qui lève et laisse passer l'événement, mais sans rien dire : la ligne
// d'état le dit. `next.error` est un constat du moteur, non l'erreur levée : son motif est dans
// `message`, absent d'un dépassement de délai sans rejet.
const signaler = ($: EngineInterface, echec: HookFailure) =>
  $.ui.status(`lexique : ${(echec.message ?? echec.kind).slice(0, 60)}`)

/** Pose les deux hooks du mod : la section de session, et le préfixe du prompt d'un sous-agent. */
export const register: Register = on => {
  // Une section du prompt système n'a pas de plafond, survit à `/clear`, à la compaction et à la
  // reprise sans se dupliquer, et ne va pas aux sous-agents. Ni `prompt.context` (tous les
  // sous-agents le reçoivent, isolés compris) ni `$.session.append` à `session.start` (perdu à
  // `/clear`, dupliqué à chaque reprise) n'y suffisent. La commande est relancée tant qu'elle ne
  // rend rien.
  let local: string | undefined
  on('prompt.compose', async ($, e, next) => {
    const composition = await next(e)
    local ??= await $.commande.lancer({
      argv: ['lexique', 'session'],
      env: { CLAUDE_PROJECT_DIR: await projet($) },
      source: 'lexique',
    })
    if (!local) return composition
    return {
      sections: [...composition.sections, { id: 'lexique:local', text: local, scope: 'session' }],
    }
  }).catch(($, e, next) => {
    signaler($, next.error)
    return next(e)
  })

  // Le texte passe par le `prompt` du sous-agent : `$.session.append` ne peut pas le viser avant
  // `next`, son `agentId` n'existe qu'après.
  on('agent.spawn', async ($, e, next) => {
    const texte = await $.commande.lancer({
      argv: ['lexique', 'sous-agent', e.subagentType],
      env: { CLAUDE_PROJECT_DIR: await projet($) },
      source: 'lexique',
    })
    return next(texte ? { ...e, prompt: `${ENTETE}\n\n${texte}\n\n---\n\n${e.prompt}` } : e)
  }).catch(($, e, next) => {
    signaler($, next.error)
    return next(e)
  })
}
