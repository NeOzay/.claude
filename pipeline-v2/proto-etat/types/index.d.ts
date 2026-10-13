/** Valeur jetable : quand la session a écrit le compteur, en ISO 8601. */
export type Horodatage = string

declare module 'claude-code' {
  interface PluginState {
    'pv2-etat': {
      /** Valeur jetable : combien de fois la session a écrit, pour voir ce qui en survit. */
      compteur: number
      /** Valeur jetable : quand la session a écrit le compteur. */
      horodatage: Horodatage
    }
  }
}
