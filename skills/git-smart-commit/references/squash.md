# Aplatissement d'une branche d'implémentation (clôture)

Cas déclenché explicitement (ex. par `implementation-tracker` en fin de chantier), pas par simple
mention de "commit".

Le chantier a été mené sur une **branche d'implémentation nommée `<slug>`** (voir
`implementation-tracker`, Étape 2). La clôture réunit tous ses commits en **un seul commit posé sur la
branche principale** (`base:` du fichier de suivi). La branche `<slug>` étant locale et jetable, et
l'aplatissement n'ajoutant qu'un commit ordinaire sur la principale (aucune réécriture de la
principale), il n'y a pas de force-push à craindre.

1. **Identifier la branche et la base.** La branche d'implémentation est `<slug>` ; la branche
   principale cible est `base:` (par ex. `main`). Lister ce qui sera aplati :

   ```bash
   git log --oneline <base>..<slug>
   ```

2. **Construire un message de commit unique** résumant l'ensemble (objectif, décisions notables) —
   suivre le même format Conventional Commits que l'Étape 4 du workflow normal (voir
   [`conventional-commits.md`](conventional-commits.md)). Pour une clôture d'implémentation, s'appuyer
   sur le journal de décisions du fichier de suivi plutôt que de relire tous les diffs individuellement.

3. **Confirmation explicite obligatoire** avant d'exécuter quoi que ce soit (règle globale, voir
   `CLAUDE.md` : jamais de commit, squash, rebase ou amend sans accord explicite). Afficher la branche
   principale cible, la plage de commits concernée et le message final proposé, attendre la validation.

4. **Aplatir sans rebase interactif** (pas de `-i`, saisie interactive non supportée). Se placer sur la
   branche principale et y poser un unique commit contenant tout le travail de la branche `<slug>` :

   ```bash
   git checkout <base>
   git merge --squash <slug>
   # opérations de clôture éventuelles de l'appelant, à stager ici avant le commit
   # (ex. implementation-tracker : git mv du fichier de suivi vers done/)
   git commit -m "<titre>" -m "<corps>"
   ```

   `git merge --squash` stage tous les changements de `<slug>` sans créer de commit de merge ni
   déplacer `HEAD` : le commit suivant est un commit ordinaire, unique, sur `<base>`. Si l'appelant a
   des opérations de clôture à intégrer (renommage, déplacement de fichier), les stager **entre** le
   `merge --squash` et le `git commit` pour qu'elles fassent partie du commit unique.

5. **Supprimer la branche d'implémentation** une fois l'aplatissement validé (le travail est désormais
   sur `<base>`) :

   ```bash
   git branch -D <slug>
   ```

6. Confirmer le résultat avec `git log --oneline -3` (sur `<base>`) et rappeler que le push reste une
   étape distincte à la charge de l'utilisateur.
