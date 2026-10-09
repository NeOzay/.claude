# Stager tout, sauf les exclusions

Un commit prend **toutes les modifications en attente, sauf les exclusions** : les fichiers sans
rapport avec la tâche en cours. L'agent en juge, et les présente avec la proposition
([`confirmation.md`](confirmation.md)).

```bash
git add -A
git reset -q -- <exclu> [<exclu>…]
git diff --staged --name-only
git commit -m "<titre>" [-m "<corps>"]
```

Sans exclusion, le `reset` saute. Avec, il retire aussi un fichier exclu que l'utilisateur aurait
indexé lui-même pendant sa relecture. Le `diff --staged` contrôle, avant le commit, qu'aucune
exclusion n'est restée dans l'index.

Les exclusions sont la seule liste présentée : une exclusion oubliée fait entrer dans l'historique
un travail sans rapport avec la tâche — le travail partiel d'un outil, d'un agent arrêté en cours
de route, ou d'une autre tâche de l'utilisateur —, et rien d'autre dans la proposition ne le laisse
voir. Avant de proposer, l'agent relit donc `git status --short` en entier, et chaque fichier qu'il
ne rattache pas à la tâche devient une exclusion.

Vérifier après coup que le commit porte ce qui était attendu : `git show --stat HEAD`.
