---
name: session-dump
description: >
  Écrit un dump Markdown par discussion d'un projet, avec ses statistiques (tokens, coût, durée,
  tours) en frontmatter TOML, dans `<projet>/.claude/session-dump/<id>/`. Skill exclusivement
  manuelle : elle s'invoque uniquement via /session-dump. N'analyse aucun dump.
disable-model-invocation: true
argument-hint: "[chemin du projet]"
---

# session-dump — extraire les discussions d'un projet

**Partage des rôles** : la commande lit les sessions et écrit les dumps. Le modèle la lance et
rapporte sa sortie, rien de plus : lire, classer ou commenter les dumps est une autre tâche, que
l'utilisateur ouvre dans une discussion à part.

## La commande

```bash
session-dump              # le projet du répertoire courant
session-dump <chemin>     # le projet qui vit à <chemin>
```

`session-dump` est un lien de `bin/` vers `scripts/session-dump-cli.py`, résolu par le `PATH`. Elle
n'emploie que la bibliothèque standard.

| Code | Sens |
|---|---|
| 0 | dumps écrits ; la sortie nomme le répertoire et le nombre de dumps |
| 1 | aucune session pour ce projet, ou écriture impossible ; message sur stderr |
| 2 | erreur d'appel : le chemin n'est pas un répertoire |

Le chemin désigne le répertoire du projet. La commande le résout en chemin absolu, en tire l'`<id>`
(chaque caractère non alphanumérique devient `-`) et lit `projects/<id>/` dans `$CLAUDE_CONFIG_DIR`,
à défaut `~/.claude`.

## Ce qu'elle écrit

Un fichier `<date de création, UTC>-<titre en kebab-case>.md` par session principale. Deux sessions
au même nom portent toutes deux le suffixe des 8 premiers caractères de leur UUID. Le titre est
celui que l'utilisateur a donné, sinon le titre généré, sinon l'UUID.

**Un dump écrase les précédents** : le répertoire `<id>/` est construit à côté puis substitué à
l'ancien, qui reste intact si l'écriture échoue.

**Le frontmatter** écrit ses nombres par groupes de trois chiffres séparés par `_` (`45_372_384`),
que TOML admet et que `tomllib` relit. Il porte, en champs plats : `session`, `titre`, `cree`,
`branches`, `tours`, `mesure`, `cout_usd`, puis les tables `[tokens]` (`total`, `entree`, `sortie`,
`cache_lu`, `cache_cree`) et `[duree]` (`totale_s`, `api_s`).

- Les tokens et le coût viennent de la dernière ligne `cost-state` de la session, sous-agents
  compris. `mesure = "cost-state"` le dit.
- Une session sans `cost-state` a ses tokens recalculés depuis les transcriptions, et ni
  `cout_usd` ni `[duree]` : `mesure = "transcriptions"`.
- `sortie` contient le thinking, déjà compté dans les tokens de sortie.
- `tours` compte les messages que l'utilisateur a saisis, commandes `/` comprises.

**Le corps** ne garde que la discussion, sous `## Utilisateur` et `## Assistant`. Chaque appel
d'outil y tient en une ligne, `` - `<Outil>` <cible> ``, sans le contenu de ses arguments. Résultats
d'outils, thinking, messages méta et blocs `<system-reminder>` en sont absents : la réponse à une
question posée par `AskUserQuestion` est un résultat d'outil, donc absente aussi.

Une session sans aucun tour n'est pas une discussion : elle n'est pas dumpée, et la sortie compte
celles qu'elle écarte. La session en cours y figure, partielle.

## Ignorer les dumps

La commande ne touche à aucun `.gitignore`. Un dump contient des discussions entières : ajouter
`.claude/session-dump/` au `.gitignore` du projet avant de le dumper, pour qu'aucune ne soit
versionnée.
