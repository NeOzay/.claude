# Plan — modele-hors-de-settings-json

Brief : `.claude/implementation/modele-hors-de-settings-json.brief.md` (validé).
Entrée de road-map : `modele-hors-de-settings-json`.

## Contexte

Le pipeline dit à l'utilisateur de faire `/model <modèle>` dans la session qui suit la Passation
(`skills/implementation-tracker/references/creation.md`, point 10 ;
`skills/implementation-tracker/references/contrat.md`, « Modèle d'implémentation »). Fait en
mode « défaut », `/model` écrit le champ `model` de `~/.claude/settings.json`, qui est versionné :
dans un Chantier de la configuration, l'arbre est sale dès la première commande.

Ce qui existe déjà et suffit à éviter toute écriture versionnée (brief, contraintes) :

- `/model` peut ne changer que la session en cours, sans écrire aucun fichier ;
- `~/.claude/.claude/settings.local.json`, ignoré par git (`~/.config/git/ignore:1`), fixe le
  modèle au démarrage d'une session ouverte sur ce dépôt, et l'emporte sur le `settings.json`
  utilisateur. Il porte aujourd'hui `"model": "sonnet"`.

Le Chantier ne construit donc rien : il change la consigne du pipeline et documente le réglage
local au dépôt. Ni filtre git ni hook (hors-périmètre), et `~/.claude/settings.local.json` n'est
pas utilisé.

## Incertitudes du brief, tranchées par le plan

### Le champ `"model"` de `~/.claude/settings.json`

| Option | Effet | Coût |
|---|---|---|
| **A. Le garder, ne plus l'écrire depuis un Chantier** (retenue) | Reste le défaut des autres projets ; dans ce dépôt, `.claude/settings.local.json` l'emporte | Repose sur le `/model` de session : un « défaut » enregistré ailleurs resalit `~/.claude` |
| B. Le retirer | Défaut de Claude Code partout, sauf réglage local | Ne protège de rien : le prochain `/model` en mode « défaut » le réécrit ; et le défaut des autres projets est perdu |
| C. Le garder et tolérer sa modification dans le pipeline | Plus aucun blocage | C'est la tolérance « en dernier recours » de la Décision du brief : elle n'entre pas tant que A suffit |

A est retenue : seule une écriture évitée garde l'arbre propre, et `/model` de session l'évite
quel que soit le contenu du champ. Le champ n'est **pas modifié** par ce Chantier.

### Les autres signaux de dérive

En plus de ceux du brief :

- le diff touche `settings.json`, à quelque champ que ce soit — l'option A ne le modifie pas ;
- le diff touche un fichier hors de ceux des Étapes ci-dessous ;
- la consigne fait écrire le modèle par l'agent (dans `.claude/settings.local.json` ou ailleurs) :
  `contrat.md` pose que rien ne change le modèle à la place de l'utilisateur, et le brief ne
  demande pas de revenir là-dessus.

## Étapes

### 1. La consigne `/model` du pipeline

Fichiers : `skills/implementation-tracker/references/contrat.md`,
`skills/implementation-tracker/references/creation.md`.

- `contrat.md`, « Modèle d'implémentation », premier paragraphe : l'utilisateur fait
  `/model <modèle>` **pour la session seulement**, sans l'enregistrer comme défaut. Ajouter le
  pourquoi en une phrase : le défaut s'écrit dans `~/.claude/settings.json`, versionné, et salit
  l'arbre des Chantiers de la configuration — création refusée, Passation dite périmée.
- `creation.md`, point 10 : même précision, en renvoyant à `contrat.md` plutôt qu'en recopiant le
  pourquoi.
- `SKILL.md:131` (« seul l'utilisateur fait `/model` ») ne dit pas comment : il reste tel quel.
- `contrat.md:167` porte déjà « Rien ne change le modèle à sa place, ni par Étape, ni par
  session » : là, « session » veut dire session de Chantier. La reformuler pour qu'elle ne se lise
  pas contre « pour la session seulement », par exemple « ni d'une Étape à l'autre, ni d'une
  reprise à l'autre ».

Vérif — la chaîne « pour la session seulement » n'existe pas avant l'Étape :

```bash
grep -c 'pour la session seulement' skills/implementation-tracker/references/contrat.md skills/implementation-tracker/references/creation.md   # attendu : ≥ 1 dans chacun
git diff --stat master -- settings.json   # attendu : vide
```

### 2. Le réglage du modèle propre à ce dépôt

Fichier : `.claude/CLAUDE.md` (règle qui ne vaut que pour ce dépôt : elle ne va pas dans le
`CLAUDE.md` racine).

Une courte section : le modèle d'une session ouverte sur ce dépôt se règle dans
`.claude/settings.local.json`, ignoré par git ; `/model` s'y fait pour la session seulement,
jamais en défaut, parce que `settings.json` est versionné ici ; `~/.claude/settings.local.json`
n'est pas le bon fichier (il est versionné).

Vérif :

```bash
grep -n 'settings.local.json' .claude/CLAUDE.md
git check-ignore -q .claude/settings.local.json && echo IGNORÉ   # attendu : IGNORÉ
git diff --stat master -- settings.json settings.local.json      # attendu : vide
```

## Vérification de bout en bout

Le critère qui compte se vérifie par l'usage, et ce Chantier en fournit l'occasion : à la Passation
de la création, l'utilisateur fait `/model opus` **pour la session seulement** dans la session
neuve, puis `/implementation-tracker @<suivi>`. La Phase 3 de la reprise doit trouver
`git status --short` vide et dire la Passation à jour — sans exception pour `settings.json`.

Ce contrôle a lieu avant les Étapes : il prouve le mécanisme (`/model` de session n'écrit aucun
fichier), pas la consigne réécrite. Celle-ci se vérifie par la relecture de l'Étape 1, puis à la
création du Chantier suivant.

Si `settings.json` apparaît malgré la consigne, l'option A ne suffit pas : s'arrêter et rouvrir
la Décision « dernier recours » avec l'utilisateur, pas l'appliquer d'office.

## Modèle

**Opus** : le Chantier n'est fait que de prose (consigne du pipeline et `CLAUDE.md` de projet),
que la vérification par commande ne contrôle qu'en surface.

## Shadow-skills

`skill-convention` — les deux Étapes écrivent de la prose de skill et de configuration.
