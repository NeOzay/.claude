+++
gabarit = "suivi"
slug = "modele-hors-de-settings-json"
titre = "Changer de modèle sans modifier le `settings.json` versionné"
branche = "modele-hors-de-settings-json"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-09-modele-hors-de-settings-json.plan.md"
brief = ".claude/implementation/done/2026-10-09-modele-hors-de-settings-json.brief.md"
audit = ".claude/implementation/done/2026-10-09-modele-hors-de-settings-json.audit.md"
road-map = "modele-hors-de-settings-json"
skills = ["skill-convention"]
"créé" = 2026-10-09
maj = 2026-10-09
+++

## Objectif et périmètre

**Symptôme** : `/model` enregistre le modèle dans `~/.claude/settings.json`, versionné. L'arbre
de travail est sale dès la première commande d'un Chantier de la configuration : création bloquée,
Passation dite périmée, « `settings.json` exclu » à chaque commit.

**But** : choisir le modèle d'une session de Chantier sans toucher un fichier versionné.

**Critères de réussite** :

- Après un changement de modèle dans une session de Chantier de la configuration, suivi de la
  consigne du pipeline, `git status --short` ne montre pas `settings.json`.
- La consigne de choix du modèle (`creation.md`, point 10 ; `contrat.md`, « Modèle
  d'implémentation ») ne conduit plus à écrire un fichier versionné.
- Une création de Chantier et une reprise après Passation passent leur contrôle d'arbre propre
  sans exception pour `settings.json`.

**Hors-périmètre** :

- Aucun filtre git (`clean`/`smudge`) sur `settings.json`.
- Aucun hook qui écrit ou restaure `settings.json`.
- `~/.claude/settings.local.json` n'est pas utilisé.

**Signaux de dérive** :

- Un `.gitattributes`, une entrée `filter.*` de config git ou un hook touchant `settings.json`
  apparaît dans le diff (brief).
- `~/.claude/settings.local.json` est modifié (brief).
- Le diff touche `settings.json`, à quelque champ que ce soit (plan).
- Le diff touche un fichier hors de ceux des Étapes (plan).
- La consigne fait écrire le modèle par l'agent, dans `.claude/settings.local.json` ou ailleurs
  (plan).

## Étapes

- [x] 1. La consigne `/model` du pipeline — `skills/implementation-tracker/references/contrat.md`, `skills/implementation-tracker/references/creation.md` — vérif: `grep -c 'pour la session seulement' skills/implementation-tracker/references/contrat.md skills/implementation-tracker/references/creation.md` (≥ 1 chacun) ; `git diff --stat master -- settings.json` (vide)
- [x] 2. Le réglage du modèle propre à ce dépôt — `.claude/CLAUDE.md` — vérif: `grep -n 'settings.local.json' .claude/CLAUDE.md` ; `git check-ignore -q .claude/settings.local.json && echo IGNORÉ` ; `git diff --stat master -- settings.json settings.local.json` (vide)

## État courant

**Prochaine action** : aplatissement et archivage (`commit-chantier cloture`).

**Vérification** : `git diff --stat master -- settings.json settings.local.json` vide, et
`git status --short` vide à la reprise après un `/model` pour la session seulement.

**Dernier audit** : `1a2282b` — RÉSERVES — 2026-10-09 (R1 vérifiée en session 2, R2 traitée par `AE2.1`, R3 versée à la dette ; `AE2.1` non réaudité, sur décision de l'utilisateur)

**Notes** : le champ `"model"` de `settings.json` est gardé tel quel (option A du plan). Un
`/model` pour la session seulement ne survit pas à la session : à chaque reprise, le modèle se
refait, et la Phase 3 signale l'écart au champ `modèle` (écrit dans `contrat.md` à l'Étape 1).

## Passation

**Écrite** : session 1, après AE2.1

**En cours** : rien. Toutes les Étapes sont faites ; l'audit de clôture (`1a2282b`) a rendu
RÉSERVES. R2 est traitée (`AE2.1`). Reste R1, à vérifier à la reprise, puis la Clôture avec R3
versée au registre de dette.

**À savoir** :

- R1 se vérifie ainsi : l'utilisateur ouvre la session par `/model sonnet` **pour la session
  seulement**, puis lance la reprise. `settings.json` porte `"opus"` sur `master` : une écriture en
  défaut y laisserait un diff visible. `git status --short` ne doit montrer que le rapport
  `.audit.md`, non suivi.
- L'écart entre le modèle de la session (sonnet) et le champ `modèle` (opus) est **voulu** pour ce
  test : le signaler, sans rien changer.
- `.claude/settings.local.json` porte `"opus"` au lieu du `"sonnet"` du cadrage ; ce n'est pas
  le fait de la session 1.
- R2 traitée a produit un nouveau diff : la Clôture relance un audit complet avant d'aller plus
  loin (`audit.md`, « Au retour »).

## Journal de décisions

- **2026-10-09** — Le champ `"model"` de `~/.claude/settings.json` est gardé et n'est plus écrit
  depuis un Chantier : `/model` pour la session seulement, `.claude/settings.local.json` pour le
  défaut du dépôt. *Pourquoi* : seule une écriture évitée garde l'arbre propre. *Rejeté* : le
  retirer (le prochain `/model` en défaut le réécrit) ; tolérer sa modification dans le pipeline
  (« dernier recours » du brief).
- **2026-10-09** — Clôture avec les RÉSERVES de `1a2282b`, sans nouvel audit après `AE2.1`.
  *Pourquoi* : l'utilisateur a tranché ; R1 vérifiée en session 2 (`/model sonnet` pour la session
  seulement, `git status --short` ne montre que le rapport d'audit, `settings.json` intact), R2
  traitée, R3 versée à `technical-debt/motif-du-modele-ecrit-dans-contrat-et-claude-md`.
