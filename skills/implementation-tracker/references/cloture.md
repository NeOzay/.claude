# Clôture et abandon d'une implémentation

## Clôture

Déclenchée par `/implementation-tracker close`, ou quand l'utilisateur déclare l'implémentation
terminée.

### 1. Audit — obligatoire, et bloquant

**Si le dépôt porte un garde-fou de pipeline, le lancer d'abord.** Il n'existe que dans les dépôts
qui hébergent le pipeline lui-même — ailleurs, ce contrôle n'a pas d'objet et se saute :

```bash
if [ -f scripts/check-pipeline.sh ]; then bash scripts/check-pipeline.sh; fi
```

C'est un contrôle **mécanique**, pas un jugement : il constate que chaque règle partagée reste
définie à un seul endroit et que les renvois y menant résolvent encore. Il passe avant l'audit
parce qu'il coûte une seconde là où l'audit coûte un agent, et qu'auditer la conformité à une
intention n'a guère de sens si le contrat qui la porte est déjà incohérent. Sortie ≠ 0 → traiter
avant d'auditer.

Vérifier ensuite que toutes les étapes sont cochées — sinon demander quoi faire des restantes ;
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

### 2. Alimenter le registre de dette

Ce que le chantier laisse derrière lui part dans `.claude/implementation/todo/technical-debt.md` —
procédure, gabarit d'entrée et règle de solde : `references/dette.md`.

**Ici et pas ailleurs.** Après l'audit, parce que c'est lui qui produit les constats et que les
arbitrages qu'il déclenche (« clore avec ces réserves ») en font partie. Avant l'archivage, pour que
l'écriture entre dans l'aplatissement de la branche. Et **une seule fois par chantier** : un audit
intermédiaire ne l'alimente pas, sinon l'audit de clôture, qui rejuge le diff entier, y réécrirait
les mêmes constats.

C'est l'orchestrateur qui écrit, jamais l'auditeur (pourquoi : `references/dette.md`, « Un état, pas
un journal »).

Un chantier qui **solde** une entrée du registre la déplace vers `technical-debt-solde.md`, avec la
commande exécutée qui l'établit. Sans cette sortie réelle, l'entrée reste.

**Mettre le registre à l'index dès qu'il est écrit** :

```bash
git add .claude/implementation/todo/
```

Au premier usage, ces fichiers ne sont **pas suivis** par git. Le commit du point 3 ne stage que le
fichier de suivi et l'aplatissement du point 4 ne reprend que ce qui est déjà commité : sans ce
`git add`, le registre reste dans l'arbre de travail, la clôture se déroule sans une seule erreur, et
l'écriture est perdue. C'est un chemin d'échec silencieux — le seul type qui ne se rattrape pas.

### 3. Finaliser le fichier de suivi

**Sur la branche `<slug>`** : `statut: terminé`, compacter le journal. Le committer avec le registre
mis à l'index au point 2 (commit de suivi direct), pour que ces derniers changements entrent dans
l'aplatissement.

```bash
git add .claude/implementation/<slug>.md .claude/implementation/todo/
```

### 4. Aplatir la branche d'implémentation

Passer la main à `git-smart-commit` (cas « aplatissement d'une branche d'implémentation »,
voir ce skill). Tous les commits de la branche `<slug>` sont réunis en **un seul commit posé
sur `base:`**, puis la branche `<slug>` est supprimée.

Ce n'est **pas** un commit de suivi ordinaire — c'est une réécriture d'historique, donc elle
suit le workflow de vérification et de confirmation complet de `git-smart-commit` :
[Branche et commits](contrat.md#branche-et-commits).

**Conflit sur le `git merge --squash`** (`base:` a avancé pendant le chantier) → **s'arrêter net** :
ne rien committer, ne rien déplacer, ne pas supprimer la branche. Rendre la main à l'utilisateur
avec l'état de l'index. Une clôture à moitié faite est pire qu'une clôture reportée.

**Déplacement des fichiers du chantier** : une fois sur `base:` avec le `git merge --squash`
appliqué, mais **avant le commit unique**, déplacer suivi, brief, rapport d'audit et plan vers
`done/` pour que les renommages entrent dans l'aplatissement. Ces trois derniers peuvent ne pas être
suivis par git (créés avant le premier commit du chantier) : `git mv` échouerait en plein squash,
d'où le repli `mv` **suivi d'un `git add`** — sans lui, le fichier resterait hors du commit.

**Le plan est renommé d'après le slug**, `<AAAA-MM-DD>-<slug>.plan.md`, jamais d'après son nom
généré — pourquoi, et ce que l'oubli a déjà coûté :
[Arborescence et nommage](contrat.md#arborescence-et-nommage).

**Les champs `plan:`, `brief:` et `audit:` du suivi sont réécrits** vers leurs chemins `done/` dans
la même passe. Sans cela ils désignent des fichiers qui n'existent plus, et le champ `plan:` peut
même résoudre vers le plan d'un **autre** chantier — ce qui a l'air de fonctionner.

```bash
d=.claude/implementation/done
set -e
git mv .claude/implementation/<slug>.md $d/<AAAA-MM-DD>-<slug>.md

for f in .claude/implementation/<slug>.brief.md .claude/implementation/<slug>.audit.md; do
  [ -e "$f" ] || continue
  t=$d/<AAAA-MM-DD>-$(basename "$f")
  [ -e "$t" ] && { echo "REFUS : $t existe déjà"; exit 1; }
  git mv "$f" "$t" 2>/dev/null || { mv "$f" "$t"; git add "$t"; }
done

p=<chemin-du-plan>
t=$d/<AAAA-MM-DD>-<slug>.plan.md
[ -e "$t" ] && { echo "REFUS : $t existe déjà"; exit 1; }
git mv "$p" "$t" 2>/dev/null || { mv "$p" "$t"; git add "$t"; }

# Réécrire les chemins du frontmatter vers leurs cibles définitives. Un champ dont la
# cible n'existe pas est laissé tel quel : le garde-fou le signalera plutôt que de le
# remplacer par un autre chemin mort.
s=$d/<AAAA-MM-DD>-<slug>.md
for champ in plan brief audit; do
  cible=$d/<AAAA-MM-DD>-<slug>.$champ.md
  [ -e "$cible" ] && sed -i "s|^$champ: .*|$champ: $cible|" "$s"
done
git add "$s"
```

Le test `[ -e "$t" ]` avant chaque déplacement est ce qui transforme un écrasement silencieux en
arrêt. Sur un `REFUS`, s'arrêter et rendre la main : ne rien committer.

Le plan est archivé avec le reste : il porte le contenu des étapes, et n'a de sens qu'à côté du
suivi qu'il a produit. Le rapport d'audit de même — c'est la trace de ce qui a été constaté au
moment de clore, et elle ne vaut qu'accompagnée de ce qu'elle jugeait.

### 5. Rendre la main

**Pas de résumé prêt à coller.** Tout ce qu'il contiendrait est déjà écrit et versionné : l'objectif
dans le brief, ce qui a changé dans le diff du commit unique, les décisions au journal du suivi, les
points laissés de côté dans le registre de dette. Le réécrire en fin de clôture produit une copie
qui vieillit sans que rien ne la mette à jour.

Dire ce qui a été fait en deux ou trois lignes — commit produit, branche supprimée, ce qui reste à
la main de l'utilisateur (le push, typiquement) — et s'arrêter là.

---

## Abandon

Déclenché par `/implementation-tracker abandon`. On abandonne plus de chantiers qu'on n'en clôt ;
sans cette porte de sortie, il reste un suivi à moitié coché et une branche orpheline qui polluent
tous les listings suivants.

1. **Demander la raison** et l'écrire au journal — c'est la seule information que l'abandon
   produit, et celle qui évitera de rouvrir le même chantier dans trois mois.
2. `statut: abandonné`, `maj:` à jour. Committer sur la branche `<slug>`.
3. **Proposer** de verser au registre de dette ce que l'abandon laisse ouvert — le problème qui
   restait à traiter, la raison de l'abandon à l'appui (`references/dette.md`). Proposer, jamais
   imposer : un chantier abandonné parce que le besoin a disparu ne laisse aucune dette, et une
   entrée écrite d'office serait exactement le bruit que le registre doit éviter.

   On décide **ici**, on écrit au point 4. Même raison qu'au point 2 de la clôture : le registre
   n'a de valeur que sur `base:`, et l'abandon n'y passe qu'au point suivant.
4. **Décider du sort du travail avec l'utilisateur**, sans rien supposer :
   - *tout jeter* → archiver le suivi, le brief et le rapport d'audit éventuel en `done/` sur
     `base:` (commit direct), puis supprimer la branche : `git branch -D <slug>` ;
   - *garder la branche* → ne rien supprimer, archiver seulement le suivi ; le dire clairement.

   Les **deux** branches de ce choix passent sur `base:` — *tout jeter* pour y archiver, *garder la
   branche* pour y déposer le suivi. C'est là, et seulement là, qu'on écrit l'entrée décidée au
   point 3 :

   ```bash
   git add .claude/implementation/todo/
   ```

   puis on la joint au commit direct d'archivage. Si *garder la branche* n'avait rien d'autre à
   committer, ce commit existe quand même : il porte l'entrée.

   Écrite sur `<slug>`, elle n'atteindrait jamais `base:` : la branche est soit supprimée, soit
   conservée sans jamais être aplatie (point 5). C'est le même chemin d'échec silencieux qu'au
   point 2 de la clôture, et il se ferme de la même façon.
5. Ne **jamais** aplatir un chantier abandonné dans `base:` : il n'a pas vocation à y entrer.
