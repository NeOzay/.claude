+++
gabarit = "brief"
slug = "retouches-et-modele-du-chantier"
titre = "Cadrer les retouches post-étape et choisir au Plan le modèle d'implémentation"
statut = "validé"
execution = "direct"
"créé" = 2026-10-05
+++

## Intention

**Symptôme** : « De nombreux commits de retouches post-étape ont dû être réalisés, mais rien dans
implementation-tracker ne cadre ce cas » ; et le modèle d'implémentation, Sonnet ou Opus, n'est
choisi nulle part.

**But** : une retouche d'Étape livrée a son nom de commit et son tag, `<slug>: E<N>.<k>` et
`<L>E<N>.<k>` ; le Plan choisit le modèle qui conduira toute l'implémentation, et le Suivi le
porte.

## Critères de réussite

- Le type 2 de `git-smart-commit` a un cas « Retouche » : message `<slug>: E<N>.<k> — …`, tag
  `<L>E<N>.<k>`
- La Clôture et l'Abandon suppriment aussi les tags `<L>E<N>.<k>`, et un test le montre :
  `.venv/bin/python -m pytest skills/git-smart-commit`
- Plus aucune trace vivante de la délégation :
  `git grep -n -e step-implementer -e délégu -e execution -- ':!.claude/implementation/done'
  ':!.claude/implementation/todo' ':!.claude/plans'` ne rend que ce qui ne parle pas du
  mécanisme supprimé
- `gabarit contract suivi` déclare le champ du modèle ; ni `suivi` ni `brief` ne déclarent
  `execution`
- `scripts/check_pipeline.py` passe, ainsi que ruff et basedpyright sur le Python touché

## Hors-périmètre

- Migrer les Suivis des Chantiers déjà ouverts (claude-translator compris) : le champ
  `execution` est supprimé, l'utilisateur corrige à la main si nécessaire

## Signaux de dérive

- Un mécanisme qui choisit ou change le modèle à la place de l'utilisateur : hook, script, appel
  à `/model` (dit)
- Un modèle choisi par Étape ou par session, et non pour tout le Chantier (dit)
- Une retouche qui crée une Étape au Suivi au lieu de rester rattachée à l'Étape N (dit)
- Une archive de `done/` modifiée pour en retirer `execution` (dit)

## Contraintes connues de l'utilisateur

- **Décision** : est une retouche toute modification, et tout commit, faits après le commit d'une
  Étape et avant l'Étape suivante (dit)
- **Décision** : commits `<slug>: E<N>.1`, `E<N>.2`…, tags de même forme (dit)
- **Décision** : l'Étape N+1 passe en `[>]` quand son travail commence, non plus au cochage de
  l'Étape N ; d'ici là, tout commit est une retouche `E<N>.<k>` (dit)
- **Décision** : le Suivi ne trace pas les retouches, git suffit ; une décision prise en retouche
  va au journal comme toute autre (dit)
- **Historique** : l'Étape se committe avant ses retouches pour que son diff ne montre qu'elle
  (dit)
- **Existant** : une retouche part aujourd'hui en commit de session, nommé d'après l'Étape en
  cours, non d'après l'Étape retouchée (dépôt: claude-translator dad40e0, 5a3b15d)
- **Existant** : la Clôture ne supprime que les tags `^[A-Z]E\d+$` ; un `AE16.1` survivrait à sa
  branche (dépôt: skills/git-smart-commit/scripts/commit_chantier.py:70)
- **Décision** : le modèle vaut pour toute l'implémentation et s'écrit dans le Suivi (dit)
- **Décision** : l'utilisateur fait `/model` dans une session vierge, celle qui suit la Passation
  d'après le commit `<L>E0` (dit)
- **Décision** : critère du choix — Sonnet pour un travail bien délimité, Opus pour un travail
  complexe et mal délimité, tel le Chantier `reecrire-docs-dans-docs2` de claude-translator (dit).
  Ce qui le dit :
  - la vérification : du code se contrôle bien plus facilement que de la prose (dit) ;
  - les incertitudes reportées au brief ne s'accordent avec Sonnet que si le Plan les tranche
    toutes (dit) ;
  - le nombre d'Étapes : beaucoup d'Étapes est un signe de complexité (dit) ;
  - au moindre doute, Opus (dit)
- **Rejeté d'emblée** : le couplage entre Étapes comme critère — il y en a toujours, les Étapes
  suivantes dépendent des précédentes (dit)
- **Décision** : le Plan justifie son choix en une phrase, et `plan-reviewer` juge ce choix au
  regard du critère (dit)
- **Décision** : à la reprise, l'agent compare son modèle au champ du Suivi et signale l'écart,
  sans bloquer ni rien changer (dit)
- **Existant** : `step-implementer` est figé en `model: sonnet` (dépôt: agents/step-implementer.md)
- **Décision** : `step-implementer` est supprimé, avec la délégation, la valeur `délégué` et le
  champ `execution` des Semences `brief` et `suivi` ; la Passation rend le Subagent inutile pour
  la gestion du contexte (dit)
- **Décision** : les dettes qui portent sur l'agent sont écartées, non soldées (dit)
- **Existant** : un champ non déclaré au Contrat est une violation de `gabarit check` (dépôt:
  skills/gabarit/scripts/gabarit/check.py:45)

## Incertitudes à lever en plan

- Le commit de Passation, quand il suit un commit d'Étape, garde-t-il sa forme `passation —`,
  hors numérotation des retouches ?
- À partir de combien d'Étapes le nombre fait-il pencher vers Opus ?
- « Retouche » entre-t-il au Lexique global ? À proposer à l'utilisateur, jamais à écrire
  d'office.
