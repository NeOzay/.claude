# Mettre des commandes à la disposition d'un agent

Une commande que l'agent appelle par son nom doit être dans le `PATH` de ses commandes Bash. Deux
portées, deux mécanismes, et aucun autre.

---

## Commande globale : une skill de `~/.claude/skills`

Une commande qui vaut pour tous les projets n'est déclarée **que par une skill de
`~/.claude/skills`** : son exécutable vit dans la skill, et un lien de `bin/` l'expose. Règle,
motif et geste d'installation : [l'outillage du dépôt](../../../OUTILLAGE.md), qui en est
l'autorité.

Un projet ne déclare jamais de commande globale : ce qu'il ajouterait au `PATH` de l'utilisateur
vaudrait dans tous les autres projets, où la commande n'a aucun sens et peut masquer un homonyme.

## Commande locale : `.claude/bin/` et un hook de projet

Une commande qui n'existe que pour un projet vit dans ce projet :

```
<projet>/
└── .claude/
    ├── bin/
    │   └── <commande>              un exécutable par commande, versionné
    ├── hooks/
    │   └── commandes-locales.sh    copie du modèle
    └── settings.json               les settings DU PROJET
```

1. Créer `.claude/bin/` et y poser les exécutables, avec leur bit `x`.
2. Copier le modèle [`commandes-locales.sh`](../modeles/commandes-locales.sh) dans
   `.claude/hooks/`, tel quel, et le rendre exécutable.
3. Le brancher dans `.claude/settings.json` **du projet**, sur `SessionStart` :

   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/commandes-locales.sh"
             }
           ]
         }
       ]
     }
   }
   ```

   Si le fichier a déjà une entrée `SessionStart`, y ajouter ce hook plutôt que la remplacer.
4. Ouvrir une nouvelle session dans le projet : la sortie du hook liste les commandes, et
   `command -v <commande>` les trouve.

Ce que fait le modèle de hook :

- il ajoute `.claude/bin/` au `PATH` par un `export` dans `$CLAUDE_ENV_FILE`, que Claude Code
  source avant chaque commande Bash de la session — le shell de l'utilisateur reste intact, et un
  autre projet n'en voit rien ;
- il écrit avec `>>`, jamais `>` : `>` effacerait ce qu'un autre hook a déjà exporté ;
- il sort en 0 quoi qu'il arrive — projet sans `.claude/bin/`, session ouverte ailleurs, variable
  absente : un rappel n'empêche pas une session de démarrer ;
- il **annonce** les commandes sur sa sortie. L'agent ne parcourt pas son `PATH` ; une commande
  qu'on ne lui nomme pas n'existe pas pour lui.

**Une skill qui veut fournir des commandes locales** livre ses exécutables et renvoie à cette
procédure ; elle ne réécrit pas le hook.

## Portée du mécanisme

Vérifié sous Claude Code 2.1.274 :

- la commande est trouvée par l'agent **et par les sous-agents** qu'il lance, bien que ceux-ci ne
  reçoivent pas `SessionStart` ;
- chaque hook `SessionStart` reçoit son propre `$CLAUDE_ENV_FILE`
  (`session-env/<session>/sessionstart-hook-<n>.sh`) : deux hooks du même projet s'appliquent tous
  les deux ;
- le hook RTK (`PreToolUse`) et le hook `SessionStart` global du dépôt n'interfèrent pas.

Ces trois points dépendent de la version de Claude Code. Après une mise à jour, les rejouer avec
la commande consignée au journal du chantier `skill-convention` plutôt que les supposer acquis.

## Mécanismes exclus

- **Les alias** : Bash ne les développe pas en mode non interactif sans
  `shopt -s expand_aliases`, et les commandes de l'agent sont non interactives.
- **Les fonctions shell** : elles marchent, mais ne sont ni visibles sur disque ni testables
  isolément.
- **La clé `env` des settings** : elle ne développe pas `$PATH`, et écraserait le `PATH` au lieu de
  l'étendre.
- **Un chemin absolu dans chaque consigne** : un point d'édition par citation, que le prochain
  déplacement du projet casse en silence.
