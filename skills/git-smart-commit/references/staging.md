# Stager des chemins nommés

**Stager les chemins, jamais `-A`** — ni `-u`, ni `.` :

```bash
git add <chemin> [<chemin>…] && git commit -m "<titre>" [-m "<corps>"]
```

Les chemins stagés sont exactement ceux présentés à l'utilisateur au moment de l'accord
([`confirmation.md`](confirmation.md)).

> *Mode de défaillance* — `-A` ramasse ce qui traîne dans l'arbre, y compris le travail partiel
> d'un outil ou d'un agent arrêté en cours de route ; `-u` raterait les fichiers créés.

Vérifier après coup que rien d'autre n'est parti : `git show --stat HEAD`.
