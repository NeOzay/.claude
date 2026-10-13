# Constats de pipeline-v2

Ce que chaque surface de Claude Code a affiché d'un prototype, puis, pour chacun des douze éléments
à afficher du Brief, ce qu'on en a vu. Format d'un constat et contrôles :
[README](README.md#le-format-dun-constat).

## Surfaces

La sonde, `proto-sonde`, dessine une bande dès le démarrage ; `/sonde` ouvre un panneau
(`Markdown`, un lien `https:`, un lien `file:`, un `Button`), pose une ligne d'état, un toast et
une notification. La documentation dit de même : seuls le terminal et l'onglet Code de Desktop
dessinent un mod ; par Remote Control, le dessin a lieu au terminal de la machine
([Where mods run](https://code.claude.com/docs/en/plugins/mods/overview#where-mods-run)).

### Navigateur, par Remote Control

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.296, surface claude.ai/code.

Rien ne s'affiche : ni bande, ni panneau, ni ligne d'état, ni toast. Le journal `--debug` de la
session (07:12) dit pourquoi : le client web ne se déclare pas surface — aucun `session.attach`,
aucune demande de dessin ; il n'envoie que `initialize`, `get_workspace_diff`,
`get_context_usage`, `end_session`. Le `/sonde` tapé au navigateur arrive (« Injecting inbound
user message: /sonde ») et s'exécute ; le panneau se place au terminal (`asked, 185 columns:
placed`). Desktop attaché à la même session par Remote Control : même résultat, rien.

### Terminal de la machine

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.296, surface terminal.

Ce qu'une commande lancée au navigateur ouvre s'affiche au terminal hôte. Le journal `--debug` :
panneau placé, `$.ui.status` et `$.ui.toast` reçus ; `$.ui.notify` rend `no-channel`.

### Desktop, session lancée depuis l'application

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

Session ouverte par Desktop en SSH sur la machine, dans `~/.claude`, branche `pipeline-v2` ; le
prototype chargé par `CLAUDE_CODE_PLUGIN_DIRS` posé le temps de l'observation dans `settings.json`.
La bande et son bouton, le panneau, son `Markdown`, ses deux liens et son bouton s'affichent et
fonctionnent ; le toast s'affiche. La ligne d'état s'affiche, à l'étroit, sur une ligne partagée
avec d'autres éléments de l'interface, préfixée du nom du mod :
`pv2-sonde pv2-sonde : ligne d'état`. `journal.log` : `session.attach` de surface `desktop`
(`clientId` `desktop-2`, 89 × 34, plein écran), `ui.open` → `isPlaced: true`, dessins de `Pane` et
`AbovePrompt` pour `desktop`, appui `ui.press bande surface=desktop`. `$.ui.notify` rend
`no-surface` : aucune notification native.

### Mémoire du mod, `$.state` et `$.store`

Vu par agent, le 2026-10-13, Claude Code 2.1.295, surface desktop.

D'après `proto-etat/journal.log`, un compteur écrit dans les deux : `$.store` survit à tout, d'une
session à l'autre et du terminal à Desktop sur la même machine (de 10 à 18 sur la journée) ;
`$.state` survit à un rechargement à chaud du mod, mais pas à une nouvelle session, ni au `/clear`
de Desktop, qui relance `session.start`.

## 1. Étapes passées, en cours, à venir

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

`proto-etat` lit le Suivi au démarrage et à chaque fin de tour. Sa bande, une ligne au-dessus de
l'invite : `pipeline-v2 · 2/9 Étapes · en-cours · Étape 3 en cours`. Le panneau `/etat` liste les
neuf Étapes et leur état (fait, en cours, à venir) ; il est lisible, mais son texte ne se
sélectionne pas dans Desktop (au terminal, si).

## 2. Propositions de commit générées

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

`/proposer` (`proto-actions`) passe `git diff HEAD` et son `--stat` à Haiku par
`$.model.complete`, et affiche le message rendu dans un panneau (`Code`) avec « Valider » et
« Refuser ». Fonctionnel : 1 à 2 s vu de l'utilisateur, 2,4 s et 422 tokens rendus pour 1 225
caractères de diff (`journal.log`). Les boutons arrivent au mod ; « Refuser » ferme le panneau.
Le mod génère et affiche sans tour du modèle de la session.

## 3. Ouvrir le Suivi, le Brief, l'audit en un clic ou une commande

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

`/suivi`, `/brief` et `/audit` ouvrent chacun un panneau : un lien `file:` vers le fichier, puis
son texte en `Markdown`. Suivi et Brief s'affichent ; `/audit`, faute d'audit, montre le chemin
attendu et « absent ». Une commande suffit : aucun tour du modèle.

## 4. Contexte consommé et seuil de Passation

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

La ligne d'état reste `pv2-etat contexte ? / seuil 300000` : le prototype ne lit que la commande
`contexte`, qui échoue sous un mod (« CLAUDE_CODE_SESSION_ID absent de l'environnement ») ; au
terminal aussi (2.1.296). En `claude -p` lancé depuis la session du Chantier, elle rend le
contexte de **cette** session, non celui de la session du mod : la variable vient du shell
appelant. Le moteur, lui, donne le bon chiffre : `$.session.usage()` rend `? / 1000000` avant la
première requête, puis `51745 / 1000000 (5 %)` après un tour (`journal.log`). Le seuil se calcule
donc dans le mod, sans la commande.

## 5. Fichiers prévus par l'Étape face aux fichiers touchés

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

La bande de `proto-veille` affiche les fichiers prévus, lus sur la ligne `[>]` du Suivi :
`pipeline-v2/proto-veille/, pipeline-v2/constats.md`. Le fichier écrit hors prévus n'y est pas
apparu : le modèle a écrit par `Bash` (`printf … >`), et le prototype n'écoutait que `Edit` et
`Write` (transcription de la session). Un mod qui veut les fichiers touchés les lit dans
l'arbre de travail (`git status` après chaque outil ou chaque tour), pas dans les appels d'outil.

## 6. Passation en attente, à la reprise

### Non essayé

Le prototype affiche la Passation (toast et bande) quand le dernier commit de la branche est un
commit de Passation ; pendant l'observation, le dernier commit était celui de l'Étape 2. À voir à
la prochaine Passation réelle, ou à la conclusion.

## 7. État et verdict des sous-agents

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

Un hook `tool.call` sur `Agent` voit le lancement avant `next` et la fin quand `next` rend : la
bande affiche « 0 en cours · dernier general-purpose terminé » ; l'état « en cours » n'a duré que
trois secondes. Le verdict manque : le sous-agent rend son rapport par un message à part
(« SubagentHandback »), et le résultat de l'outil ne dit que « This agent's report was delivered
to you as a message ». Le verdict est à lire dans ce message, pas dans le résultat de `Agent`.

## 8. Blocages

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

La section « Blocages » du panneau affiche `aucun` : aucune Étape n'était `[!]`. Un blocage réel
n'a pas été affiché ; la lecture (`[!]` et `statut`) est la même que pour les Étapes.

## 9. Incertitudes du Plan

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

Le panneau liste les incertitudes du bloc de relecture du Plan, une par ligne. Une ligne de trop
(`MODÈLE : …`) passait le filtre, corrigé depuis : lire le Plan en prose est fragile, une
incertitude gagnerait à être une donnée.

## 10. Dette notée

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

La section « Dette notée » affiche le Marqueur `<OPTIONNEL>` tel quel, celui de `## Dettes
écartées` du Suivi : un mod qui lit un Gabarit doit traiter un Marqueur comme une section vide.

## 11. Choix de fin d'Étape, sans tour du modèle

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

`/fin` montre une bande de quatre boutons, chacun essayant une voie du moteur :

- **`$.prompt.submit`** : marche. Le message part comme un tour, origine `plugin`, et le modèle y
  répond ; c'est un tour du modèle.
- **`$.prompt.fill`** : marche. L'invite se remplit sans envoi (`isFilled: true`) ; l'utilisateur
  valide d'une touche.
- **`$.command.run` d'une commande du même mod** : échoue. Le moteur exclut les hooks de
  l'appelant : « registered /suivi but no command.run hook answered it ». Le mod appelle sa
  fonction directement.
- **`$.ui.ask`** : le dialogue du moteur s'affiche, et le mod reçoit l'option choisie (`Retouche`,
  `Passation`) ; mais Desktop tourne ensuite dans le vide. Inutilisable tel quel sous Desktop.

Un choix sans tour du modèle tient donc à un bouton dont l'`onPress` fait le travail lui-même, ou
remplit l'invite.

## 12. Signaux de dérive vérifiables par commande

### Desktop

Vu par utilisateur, le 2026-10-13, Claude Code 2.1.295, surface desktop.

Les Signaux S1, S2 et S6 se vérifient par leur commande du Brief, lancée par `$.process.run` : au
démarrage, la bande affiche « tombés S2 », juste, puisque `CLAUDE_CODE_PLUGIN_DIRS` était dans
`settings.json` le temps de l'observation. S6, provoqué par une ligne ajoutée à `LEXIQUE.md`, n'a
pas été vu : la vérification ne se relançait qu'après un `Edit` ou un `Write`, et le modèle a
écrit par `Bash`. À relancer après chaque appel d'outil, ou à chaque fin de tour.

Un hook qui lève, `/lever-commande` dans `command.run` : Desktop affiche « pv2-veille registered
/lever-commande but no command.run hook answered it », l'erreur elle-même n'est pas dite. Un
`ui.render` qui lève (`/lever`) : la bande disparaît, et la barre d'état sous l'invite avec elle.
Ni l'un ni l'autre n'arrête la session : un échec de mod se voit mal, et reste à rendre visible
par le mod lui-même.
