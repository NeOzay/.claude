# Clôture et abandon d'une implémentation

## Clôture

Déclenchée par `/implementation-tracker close`, ou quand l'utilisateur déclare l'implémentation
terminée.

### 1. Audit — obligatoire, et bloquant

Vérifier d'abord que toutes les étapes sont cochées — sinon demander quoi faire des restantes ;
auditer un chantier inachevé fait juger du travail que personne n'a fini.

Puis lancer l'audit de clôture : voir `audit.md` — sous-agent `implementation-auditor`, ce qu'on
lui transmet, ce qu'on fait de son verdict.

C'est lui qui **confronte le résultat aux critères de réussite** et constate si le **symptôme**
d'origine a disparu, en rejouant les commandes plutôt qu'en concluant sur mémoire. C'est le seul
moment où l'on peut voir qu'on a construit la bonne solution au mauvais problème — et la raison
pour laquelle ce regard est confié à un agent qui n'a pas écrit le code.

**Sans avis favorable, la clôture s'arrête ici.** `DÉFAVORABLE` → `statut: bloqué`, verdict au
journal, rendre la main. `RÉSERVES` → l'utilisateur tranche entre clore avec, ou traiter d'abord ;
ne pas décider à sa place, et ne pas requalifier une réserve en détail pour pouvoir continuer.

### 2. Finaliser le fichier de suivi

**Sur la branche `<slug>`** : `statut: terminé`, compacter le journal. Le committer (commit de
suivi direct) pour que ces derniers changements entrent dans l'aplatissement.

### 3. Aplatir la branche d'implémentation

Passer la main à `git-smart-commit` (cas « aplatissement d'une branche d'implémentation »,
voir ce skill). Tous les commits de la branche `<slug>` sont réunis en **un seul commit posé
sur `base:`**, puis la branche `<slug>` est supprimée.

Ce n'est **pas** un commit de suivi ordinaire — c'est une réécriture d'historique, donc elle
suit le workflow de vérification et de confirmation complet de `git-smart-commit`, pas le
commit direct utilisé pour les sessions/étapes.

**Conflit sur le `git merge --squash`** (`base:` a avancé pendant le chantier) → **s'arrêter net** :
ne rien committer, ne rien déplacer, ne pas supprimer la branche. Rendre la main à l'utilisateur
avec l'état de l'index. Une clôture à moitié faite est pire qu'une clôture reportée.

**Déplacement des fichiers du chantier** : une fois sur `base:` avec le `git merge --squash`
appliqué, mais **avant le commit unique**, déplacer suivi, brief, rapport d'audit et plan vers
`done/` pour que les renommages entrent dans l'aplatissement. Ces trois derniers peuvent ne pas être
suivis par git (créés avant le premier commit du chantier) : `git mv` échouerait en plein squash,
d'où le repli `mv` **suivi d'un `git add`** — sans lui, le fichier resterait hors du commit.

```bash
d=.claude/implementation/done
git mv .claude/implementation/<slug>.md $d/<AAAA-MM-DD>-<slug>.md

for f in .claude/implementation/<slug>.brief.md .claude/implementation/<slug>.audit.md <chemin-du-plan>; do
  [ -e "$f" ] || continue
  t=$d/<AAAA-MM-DD>-$(basename "$f")
  git mv "$f" "$t" 2>/dev/null || { mv "$f" "$t"; git add "$t"; }
done
```

Le plan est archivé avec le reste : il porte le contenu des étapes, et n'a de sens qu'à côté du
suivi qu'il a produit. Le rapport d'audit de même — c'est la trace de ce qui a été constaté au
moment de clore, et elle ne vaut qu'accompagnée de ce qu'elle jugeait.

### 4. Résumé

Produire un **résumé prêt à coller** : objectif, ce qui a changé, décisions notables, points
laissés de côté. Utile pour une PR, un message d'équipe ou simplement la trace du chantier.

---

## Abandon

Déclenché par `/implementation-tracker abandon`. On abandonne plus de chantiers qu'on n'en clôt ;
sans cette porte de sortie, il reste un suivi à moitié coché et une branche orpheline qui polluent
tous les listings suivants.

1. **Demander la raison** et l'écrire au journal — c'est la seule information que l'abandon
   produit, et celle qui évitera de rouvrir le même chantier dans trois mois.
2. `statut: abandonné`, `maj:` à jour. Committer sur la branche `<slug>`.
3. **Décider du sort du travail avec l'utilisateur**, sans rien supposer :
   - *tout jeter* → archiver le suivi, le brief et le rapport d'audit éventuel en `done/` sur
     `base:` (commit direct), puis supprimer la branche : `git branch -D <slug>` ;
   - *garder la branche* → ne rien supprimer, archiver seulement le suivi ; le dire clairement.
4. Ne **jamais** aplatir un chantier abandonné dans `base:` : il n'a pas vocation à y entrer.
