// Mod commun : ajoute `$.commande` au moteur, le code que les autres mods partagent.
//
// UN NOM SUR `$` : un import hors du dossier d'un plugin est refusé au chargement. Un nom ajouté à
// `$` par `engine.create` est la seule voie par laquelle un mod appelle le code d'un autre.
//
// ÉCHEC OUVERT : `lancer` ne lève jamais. Un code non nul ou une exception se dit sur la ligne
// d'état, préfixé du mod appelant, et `lancer` rend `undefined` : un rappel n'empêche ni une
// session ni un sous-agent de démarrer.
import type { Register } from 'claude-code'
import type { CommandeLancer } from '../types/index.d.ts'

/** Ajoute `$.commande` au moteur, à chaque construction de `$`. */
export const register: Register = on => {
  on('engine.create', async (_$, e, next) => {
    // `lancer` appelle le moteur par le `$` que les étapes inférieures ont bâti : à
    // `engine.create`, le `$` du hook est vide. Le validateur refuse que `built` passe en
    // argument : la méthode vit donc ici, où `built.process.run` s'écrit tel quel.
    const built = await next(e)
    const lancer = async ({
      argv,
      cwd,
      env,
      source,
    }: CommandeLancer): Promise<string | undefined> => {
      try {
        const ran = await built.process.run(argv, { cwd, env })
        if (ran.exitCode !== 0) {
          built.ui.status(`${source} : ${argv[0]} rend ${ran.exitCode} ${ran.stderr.slice(0, 60)}`)
          return undefined
        }
        // Une commande qui sort en 0 sans rien rendre reste muette : rien à verser n'est pas une
        // erreur.
        return ran.stdout.trim() || undefined
      } catch (erreur) {
        built.ui.status(`${source} : ${String(erreur).slice(0, 60)}`)
        return undefined
      }
    }
    return { ...built, commande: { lancer } }
  })
}
