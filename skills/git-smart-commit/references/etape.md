# Type 2 — commit rapide de chantier

Commit pris sur la branche d'un chantier conduit par `implementation-tracker`. Le message est
**prédéterminé** : on n'analyse pas le diff et on ne rédige rien. L'appelant fournit le slug, la
lettre et le cas.

Branche et nom : [`branche-chantier.md`](branche-chantier.md). Lettre et tags :
[`tags-etape.md`](tags-etape.md).

## Les cinq cas

| Cas | Quand | Message | Tag |
|---|---|---|---|
| État initial | à la création, une fois brief, plan et suivi écrits | `<slug>: E0 — état initial` | `<L>E0` |
| Session | pendant une étape `[>]`, à la reprise sur un arbre modifié ou en fin de session | `<slug>: session N — <étape en cours>` | aucun |
| Étape | quand l'étape n passe en `[x]`, même juste après un commit de session | `<slug>: E<n> — <intitulé de l'étape>` | `<L>E<n>` |
| Retouche | après le tag `<L>E<n>`, tant que l'étape n+1 n'est pas passée en `[>]` | `<slug>: E<n>.<k> — <objet>` | `<L>E<n>.<k>` |
| Passation | la Passation acceptée, une fois la section `## Passation` du suivi réécrite | `<slug>: passation — session N, après <tag>` | aucun |

`N` est la valeur de `session` au frontmatter du suivi. `<tag>` est le dernier tag posé, d'étape
ou de Retouche. L'`<objet>` d'une Retouche est fourni par l'appelant, en quelques mots ; son tag
est rendu par `commit-chantier retouche <L> <n>` ([`tags-etape.md`](tags-etape.md#tags)).

Une Retouche modifie une étape livrée : elle reste rattachée à l'étape n, et ne crée aucune étape
au suivi. Le commit de Passation garde sa forme et n'entre pas dans la numérotation des Retouches.

> *Mode de défaillance* — une Retouche commitée en commit de session porte le nom de l'étape
> suivante, qui n'a pas commencé : rien ne dit plus quelle étape est reprise, et aucun tag ne la
> borne.

## Procédure

1. **Vérifier la branche** : `git branch --show-current` doit rendre `<slug>`. Sinon, s'arrêter et
   le dire.
2. **Relever les exclusions** : `git status --short`. Un fichier modifié ou non suivi sans rapport
   avec le Chantier est une exclusion, présentée avec la proposition — c'est souvent le travail
   partiel d'un outil ou d'une session interrompue, dont l'utilisateur tranche le sort à l'accord.
3. **Cas état initial** : la lettre doit déjà figurer dans `lettre` du suivi. Sinon, l'obtenir
   ([`tags-etape.md`](tags-etape.md#lettre)) et l'écrire avant de continuer.
4. **Proposer**, puis attendre l'accord ([`confirmation.md`](confirmation.md)), exclusions
   comprises s'il y en a :
   - état initial, session, Passation — des commits mécaniques : l'accord se demande sans le
     titre ;
   - Étape — sous cette forme :

     ```md
     Commit d'Étape proposé :
     - Message : `<slug>: E<n> — <intitulé de l'étape>`.
     - Tag : <L>E<n>.
     ```

   - Retouche — sous la même forme, titrée `Commit de Retouche proposé :`, avec son message et son
     tag.
5. **Committer** selon [`staging.md`](staging.md). Puis, pour les cas
   état initial et étape :

   ```bash
   git tag <L>E<n>
   ```

   Pour le cas Retouche, le tag rendu par `commit-chantier retouche <L> <n>` avant la
   proposition :

   ```bash
   git tag <L>E<n>.<k>
   ```

   Si le tag existe déjà, git refuse : s'arrêter là, le commit reste, et l'utilisateur tranche.
6. **Confirmer** : `git log --oneline --decorate -1`.
