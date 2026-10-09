+++
id = "modele-hors-de-settings-json"
title = "Changer de modèle sans modifier le `settings.json` versionné"
date = 2026-10-09
source = "analyse des dumps de session du 2026-10-09, après le chantier `dump-sessions`"
+++

## À faire

`/model` enregistre le modèle choisi comme défaut, dans le champ `model` de `settings.json` (« Set
model to `Opus 5.5` and saved as your default for new sessions »). Ce fichier est versionné dans
ce dépôt. Or le pipeline fait changer de modèle à chaque Chantier : le Plan choisit Sonnet ou Opus,
et la Passation demande `/model <modèle>` dans la session neuve. L'arbre de travail est donc sale
dès la première commande de chaque Chantier.

Trouver une façon de choisir le modèle d'une session qui ne touche pas un fichier versionné, ou
qui fasse ignorer ce champ par git.

Constats tirés des dumps : `settings.json` est cité 163 fois dans 21 sessions. Il :

- bloque la création d'un Chantier, qui exige un arbre propre (`2026-10-08-commit-rapide`) ;
- fait dire la Passation périmée à la reprise, parce que `git status` n'est plus vide
  (`2026-10-07-commencer-à-ignorer-settings-json`) ;
- ajoute « Hors commit : `settings.json` » à chaque proposition de commit ;
- oblige l'utilisateur à le dire : « Ignorer settings.json et commence », « Commence ignore
  settings.json », « Annule le changement de settings.json et fait l'aplatissement ».

Pistes à vérifier avant d'en retenir une, aucune n'est essayée :

- le modèle passé au lancement (`claude --model`) ou par une variable d'environnement, sans
  `/model` ;
- un `settings.local.json`, non versionné, s'il peut porter le champ et si `/model` y écrit ;
- un filtre git `clean` qui retire le champ `model` à l'indexation ;
- à défaut, une exception explicite : le pipeline ignore une modification de `settings.json`
  limitée au champ `model`, dans le contrôle d'arbre propre et le test de Passation à jour.

## Références

- `settings.json`, champ `model` ; `settings.local.json`
- création, arbre propre : `skills/implementation-tracker/references/creation.md`, prérequis
- Passation à jour : `skills/implementation-tracker/SKILL.md`, Phase 3
- choix du modèle au Plan : `skills/implementation-tracker/references/contrat.md`, « Modèle
  d'implémentation » ; consigne `/model` : `creation.md`, point 10
- dumps : `.claude/session-dump/-home-debian--claude/`
