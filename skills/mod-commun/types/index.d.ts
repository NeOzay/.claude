// Contrat de `$.commande`, le nom que le mod commun ajoute au moteur. Un mod client le type par
// ce fichier ; à l'exécution, il appelle `$.commande.lancer`, avec ou sans `dependencies`.

/** Ce que `$.commande.lancer` reçoit : la commande à lancer, et le mod qui la lance. */
export type CommandeLancer = {
  /** La commande et ses arguments, sans shell ; le premier se résout par le `PATH`. */
  argv: readonly string[]
  /** Le répertoire de travail de la commande ; absent, celui de la session. */
  cwd?: string
  /** Les variables posées sur l'environnement de la session. */
  env?: Record<string, string>
  /** Le nom du mod appelant, en tête de la ligne d'état qui dit un échec. */
  source: string
}

/** Le lancement d'une commande, partagé entre les mods. */
export type Commande = {
  /** Lance la commande et rend sa sortie sans ses blancs ; rien si elle est vide ou échoue. */
  lancer: (input: CommandeLancer) => Promise<string | undefined>
}

declare module 'claude-code' {
  interface EngineInterface {
    /** Le lancement d'une commande, ajouté par le mod commun. */
    commande: Commande
  }
}
