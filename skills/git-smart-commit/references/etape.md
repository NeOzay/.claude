# Type 2 — commit rapide de chantier

Commit pris sur la branche d'un chantier conduit par `implementation-tracker`. Le message est
**prédéterminé** : on n'analyse pas le diff et on ne rédige rien. L'appelant fournit le slug, la
lettre, le cas, et les chemins à stager.

Branche et nom : [`branche-chantier.md`](branche-chantier.md). Lettre et tags :
[`tags-etape.md`](tags-etape.md).

## Les trois cas

| Cas | Quand | Message | Tag |
|---|---|---|---|
| État initial | à la création, une fois brief, plan et suivi écrits | `<slug>: E0 — état initial` | `<L>E0` |
| Session | à la reprise sur un arbre modifié, ou en fin de session | `<slug>: session N — <étape en cours>` | aucun |
| Étape | quand l'étape n passe en `[x]`, même juste après un commit de session | `<slug>: E<n> — <intitulé de l'étape>` | `<L>E<n>` |

`N` est la valeur de `session:` au frontmatter du suivi.

## Procédure

1. **Vérifier la branche** : `git branch --show-current` doit rendre `<slug>`. Sinon, s'arrêter et
   le dire.
2. **Confronter l'arbre aux chemins fournis** : `git status --short`. Un fichier modifié ou non
   suivi qui n'est pas dans la liste **ne se stage pas**, il se signale — c'est souvent le travail
   partiel d'un agent, dont le sort se tranche avant le commit.
3. **Cas état initial** : la lettre doit déjà figurer dans `lettre:` du suivi. Sinon, l'obtenir
   ([`tags-etape.md`](tags-etape.md#lettre)) et l'écrire avant de continuer.
4. **Proposer** le message, les chemins et le tag, puis attendre l'accord :
   [`confirmation.md`](confirmation.md).
5. **Committer** en stageant les chemins présentés : [`staging.md`](staging.md). Puis, pour les cas
   état initial et étape :

   ```bash
   git tag <L>E<n>
   ```

   Si le tag existe déjà, git refuse : s'arrêter là, le commit reste, et l'utilisateur tranche.
6. **Confirmer** : `git log --oneline --decorate -1`.
