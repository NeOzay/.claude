+++
gabarit = "brief"
slug = "modele-hors-de-settings-json"
titre = "Changer de modèle sans modifier le `settings.json` versionné"
statut = "validé"
"créé" = 2026-10-09
+++

## Intention

**Symptôme** : `/model` enregistre le modèle dans `~/.claude/settings.json`, versionné. L'arbre
de travail est sale dès la première commande d'un Chantier de la configuration : création bloquée,
Passation dite périmée, « `settings.json` exclu » à chaque commit.

**But** : choisir le modèle d'une session de Chantier sans toucher un fichier versionné.

## Critères de réussite

- Après un changement de modèle dans une session de Chantier de la configuration, suivi de la
  consigne du pipeline, `git status --short` ne montre pas `settings.json`.
- La consigne de choix du modèle (`creation.md`, point 10 ; `contrat.md`, « Modèle
  d'implémentation ») ne conduit plus à écrire un fichier versionné.
- Une création de Chantier et une reprise après Passation passent leur contrôle d'arbre propre
  sans exception pour `settings.json`.

## Hors-périmètre

- Aucun filtre git (`clean`/`smudge`) sur `settings.json`.
- Aucun hook qui écrit ou restaure `settings.json`.
- `~/.claude/settings.local.json` n'est pas utilisé.

## Signaux de dérive

- Un `.gitattributes`, une entrée `filter.*` de config git ou un hook touchant `settings.json`
  apparaît dans le diff : « cela peut créer plus de problèmes que de solutions » (dit)
- `~/.claude/settings.local.json` est modifié (dit)

## Contraintes connues de l'utilisateur

- **Existant** : `~/.claude/.claude/settings.local.json` fixe le modèle au démarrage de Claude
  Code ; il est ignoré par git et porte déjà `"model": "sonnet"` (dit ; dépôt:
  `~/.config/git/ignore:1`)
- **Existant** : `/model` peut écrire le modèle dans la configuration globale, ou ne changer que
  la session en cours, sans écrire aucun fichier (dit)
- **Rejeté d'emblée** : `~/.claude/settings.local.json`, qui est d'ailleurs versionné ; seul le
  fichier local au dépôt, `~/.claude/.claude/settings.local.json`, sert (dit ; dépôt: `git ls-files`)
- **Existant** : le problème ne se pose que pour les Chantiers de la configuration ; dans les
  autres projets, `~/.claude/settings.json` n'est pas vu par git (dit)
- **Existant** : le modèle change en permanence, selon les besoins (dit)
- **Décision** : la tolérance du pipeline à une modification de `settings.json` limitée au champ
  `model` (contrôle d'arbre propre, test de Passation à jour) reste « en dernier recours » : elle
  n'entre que si le choix du modèle hors fichier versionné ne suffit pas (dit)

## Incertitudes à lever en plan

- Le sort du champ `"model"` de `~/.claude/settings.json` : le garder et ne plus l'écrire par
  `/model`, le retirer, ou autre chose. Dit : « On change en permanence de modèle en fonction des
  besoins ; je ne sais pas quelle est la meilleure option. » Le plan doit présenter les options et
  leur coût.
- Les autres signaux de dérive. Dit : « Le reste est à voir au plan. » Candidats évoqués, non
  retenus : des changements au-delà de la consigne `/model` de `creation.md`, `contrat.md` et
  `SKILL.md` ; une modification des autres champs de `settings.json`.
