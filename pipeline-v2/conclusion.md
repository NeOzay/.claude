# Conclusion de l'exploration de pipeline-v2

**Mitigé : l'exploration s'arrête pour le moment**, décision de l'utilisateur du 2026-10-13. Le
critère « décevante » du Plan, élargi à Desktop, n'est pas rempli : panneau et bande s'affichent
dans l'onglet Code de Desktop et au terminal, boutons, liens et `Markdown` compris
(`constats.md`, « Surfaces »). Mais le navigateur ne dessine rien, et c'est là que l'utilisateur
travaille.

**Le navigateur ne dessine rien.** Une session suivie sur claude.ai/code par Remote Control ne
montre ni panneau, ni bande, ni ligne d'état, ni toast ; ce qu'un mod dessine apparaît au terminal
de la machine. La documentation le dit
([Where mods run](https://code.claude.com/docs/en/plugins/mods/overview#where-mods-run)), et la
sonde l'a vu. L'utilisateur travaille au navigateur pour ses extensions (synthèse vocale,
correcteur, autocomplétion) : une v2 graphique ne lui servirait aujourd'hui que dans Desktop ou au
terminal. La spécification n'est pas écrite (Étapes 8 et 9 sans objet).

**Reprendre quand le navigateur dessinera.** L'API des mods est en accès anticipé ; cette limite
peut tomber. Le signe se lit dans les types d'une nouvelle version : une surface de plus dans
`Elements`, ou une ligne « Remote Control » qui dessine dans le tableau de la documentation.

```bash
python3 -I pipeline-v2/api/inventaire.py <types de la nouvelle version> \
  --compare pipeline-v2/api/2.1.296.txt | grep élément
```

Constats, prototypes et inventaire restent : la reprise part d'eux.

## Les douze éléments

| # | Élément | Voie essayée | Constat | Pour une spécification |
|---|---|---|---|---|
| 1 | Étapes passées, en cours, à venir | bande et panneau `/etat`, lus dans le Suivi | affichés dans Desktop ; texte du panneau non sélectionnable | à garder |
| 2 | Propositions de commit générées | `/proposer`, `$.model.complete` sur le diff, panneau et boutons | fonctionnel, 1 à 2 s avec Haiku | à garder : le mod génère, l'utilisateur valide |
| 3 | Ouvrir Suivi, Brief, audit | `/suivi`, `/brief`, `/audit` : panneau et lien `file:` | fonctionnel | à garder |
| 4 | Contexte et seuil de Passation | ligne d'état, commande `contexte` | `contexte` échoue sous un mod ; `$.session.usage()` donne le bon chiffre après le premier tour | le mod lit le moteur, sans la commande |
| 5 | Fichiers prévus face aux fichiers touchés | `tool.call` sur `Edit` et `Write` | prévus affichés ; un fichier écrit par `Bash` échappe | lire l'arbre de travail, pas les appels d'outil |
| 6 | Passation en attente, à la reprise | toast et bande au démarrage | non essayé : aucune Passation pendant l'observation | à voir à la prochaine Passation |
| 7 | État et verdict des sous-agents | `tool.call` sur `Agent` | lancement et fin vus ; verdict absent du résultat, rendu par un message à part | lire le message de rapport |
| 8 | Blocages | panneau `/etat` | « aucun » affiché ; aucun blocage réel | à garder |
| 9 | Incertitudes du Plan | panneau `/etat`, lues dans le Plan | affichées ; la lecture de la prose est fragile | une incertitude devient une donnée |
| 10 | Dette notée | panneau `/etat` | le Marqueur `<OPTIONNEL>` s'affiche tel quel | un Marqueur se lit comme une section vide |
| 11 | Choix de fin d'Étape, sans tour du modèle | quatre boutons de bande | `onPress` et `$.prompt.fill` marchent ; `$.ui.ask` bloque Desktop ; un mod ne lance pas sa propre commande | le bouton fait le travail lui-même |
| 12 | Signaux de dérive par commande | commandes du Brief par `$.process.run` | S2 vu ; S6 manqué, relancé seulement après `Edit` ou `Write` | relancer à chaque fin de tour |

## Les incertitudes du Brief

- **Qui observe** : l'utilisateur, dans une session témoin ; le prototype écrit `journal.log`, et le
  journal `--debug` et la transcription disent le reste. Un constat porte qui l'a vu, quand, sur
  quelle version.
- **Suivre l'API** : `pipeline-v2/api/inventaire.py` relève l'API dans les types du moteur et
  compare deux versions. Entre 2.1.291 et 2.1.296 : `$.ui.notify` et `prompt.autocomplete` sont
  apparus. Desktop en SSH tourne sa propre CLI, 2.1.295, à côté de la 2.1.296 du terminal : un mod
  se vérifie sur les deux.
- **Ce qui remplace l'échec ouvert** : un mod qui lève se voit mal. Une commande qui lève fait dire
  au moteur qu'aucun hook n'a répondu ; une bande qui lève disparaît, avec la barre d'état. Le mod
  doit rendre son échec visible lui-même ; la spécification le règle sans prose de recours (S7).
- **Le TypeScript à maintenir** : quatre prototypes d'une centaine de lignes chacun. Les erreurs
  qu'on y a faites, `tsc` et `claude plugin validate` les ont prises (props de `Code`, contrat de
  `$.state`) ; les fragiles étaient les lectures de prose (incertitudes, Marqueurs), que
  `rules/claude-typescript-style.md` renvoie déjà à une commande Python. La règle suffit, à une
  condition : qu'une commande rende au mod des données structurées, et non du texte à verser.
- **Spécification partielle** : son minimum est celui de C5 (Décisions du Plan).
- **Les surfaces au navigateur** : aucune.
- **Où Claude Code mémorise l'état du Chantier** : `$.state` se perd à chaque session, et à chaque
  `/clear` de Desktop ; `$.store` survit à tout, mais hors du dépôt. Le Suivi versionné reste la
  source ; `$.store` peut porter ce qui n'a pas à être versionné.
- **« Décevante »** : ni panneau ni bande, au navigateur d'abord, élargi à Desktop ensuite ;
  ni l'un ni l'autre ne tranche seul, d'où le verdict mitigé.
