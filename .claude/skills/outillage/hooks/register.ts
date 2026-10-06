// Mod outillage : rappelle l'outillage de ce dépôt à chaque sous-agent, à son lancement.
//
// LE TEXTE VIENT DU SCRIPT : `scripts/rappel.sh` décide de ce que le sous-agent reçoit, et se
// tait hors du dépôt ; le mod lance le script par `$.commande.lancer` et transporte sa sortie.
//
// LES SOUS-AGENTS SEULS : la session principale lit l'outillage par `.claude/CLAUDE.md`. Le
// rappel passe par le `prompt` du sous-agent, réécrit avant `next` : `$.session.append` ne peut
// pas viser le sous-agent avant, son `agentId` n'existe qu'après.
//
// ÉCHEC OUVERT : un script qui échoue se dit sur la ligne d'état, par le mod commun ; une erreur
// du hook lui-même, par le `.catch` de son enregistrement. Le sous-agent démarre dans les deux cas.
import type { Register } from 'claude-code'

const RAPPEL = '.claude/skills/outillage/scripts/rappel.sh'

/** Pose le hook du mod : le rappel d'outillage en tête du prompt d'un sous-agent. */
export const register: Register = on => {
  on('agent.spawn', async ($, e, next) => {
    const racine = await $.session.root()
    const texte = await $.commande.lancer({
      argv: [`${racine}/${RAPPEL}`],
      cwd: racine,
      source: 'outillage',
    })
    return next(texte ? { ...e, prompt: `${texte}\n\n---\n\n${e.prompt}` } : e)
  }).catch(($, e, next) => {
    // `next.error` est un constat du moteur : son motif est dans `message`.
    $.ui.status(`outillage : ${(next.error.message ?? next.error.kind).slice(0, 60)}`)
    return next(e)
  })
}
