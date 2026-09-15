# Type 3 — aplatissement d'un chantier

Clôture d'un chantier conduit par `implementation-tracker` : toute la branche `<slug>` devient **un
seul commit sur `base:`**, les fichiers du chantier partent en `done/`, puis la branche et ses tags
sont supprimés. Branche : [`branche-chantier.md`](branche-chantier.md). Tags :
[`tags-etape.md`](tags-etape.md).

Les opérations sont faites par un script, `commit-chantier cloture`. **Ce qui relève du jugement est
fait avant, et hors du script** : audit, registre de dette, journal du suivi compacté, rédaction du
message.

## Procédure

1. **Écrire le message dans un fichier** (le répertoire temporaire de la session, jamais le dépôt).
   Il résume le chantier entier — objectif et décisions notables — en s'appuyant sur le journal de
   décisions du suivi plutôt qu'en relisant chaque diff. Format :
   [`conventional-commits.md`](conventional-commits.md).
2. **Simuler**, depuis la racine du dépôt et sur la branche `<slug>` :

   ```bash
   commit-chantier cloture <slug> --message <fichier> --dry-run
   ```

   `REFUS` → s'arrêter et rendre la main avec le message du script. Il n'a rien touché.
3. **Présenter la sortie du dry-run et attendre l'accord** : elle liste exactement ce que
   l'exécution fera — commits réunis, déplacements, champs réécrits, branche et tags supprimés,
   message. [`confirmation.md`](confirmation.md).
4. **Exécuter** la même commande, sans `--dry-run`.

   `ÉCHEC` → **s'arrêter net** et rendre la main avec la sortie du script, sans rien réparer
   d'office. Elle dit ce qui est fait, ce qui reste, et où l'on se trouve :
   - *toujours sur `<slug>`* → la même commande se relance telle quelle, après accord ;
   - *sur `base:`, aplatissement entamé* → les gestes restants se font à la main, dans l'ordre
     affiché, chacun présenté et accordé.
5. **Rendre compte** en deux ou trois lignes : commit produit, branche et tags supprimés. Le push
   reste à la main de l'utilisateur.

## Ce que fait le script

Refus, tous **avant la première écriture** :

- lancement hors d'un dépôt git, ou hors de sa racine ;
- branche courante différente de `<slug>` ;
- suivi introuvable, sans frontmatter fermé, ou sans `base:`, `lettre:`, `plan:`, `statut:` ou `maj:` ;
- `lettre:` qui n'est pas une lettre de A à Z ;
- plan ou branche de base introuvable ;
- fichier modifié ou non suivi qui n'est pas une annexe du chantier (suivi, brief, audit, plan,
  `todo/`) ;
- fichier de message introuvable, message vide, titre de plus de 50 caractères, ligne 2 non vide ;
- une cible `done/<date>-…` déjà présente ;
- un conflit prévisible entre `<slug>` et `base:` (`git merge-tree`).

Puis, dans l'ordre :

1. sur `<slug>` : `statut: terminé`, `maj:` du jour, indexation de toutes les annexes présentes, et
   commit `<slug>: finalisation du suivi` s'il y a quelque chose à committer — une relance le trouve
   déjà fait ;
2. `git checkout <base>` et `git merge --squash <slug>` ;
3. `git mv` du suivi, du brief, de l'audit et du plan vers `done/<date>-<slug>[.brief|.audit|.plan].md`,
   et réécriture des champs `plan:`, `brief:` et `audit:` du suivi archivé ;
4. `git commit -F <fichier>`, `git branch -D <slug>`, `git tag -d` des tags de sa lettre.

Pourquoi chacun de ces gestes :

- **Les annexes sont commitées sur `<slug>` avant de changer de branche.** Non suivies, elles
  resteraient hors de l'aplatissement. Suivies et modifiées, elles feraient refuser le
  `git checkout`.
- **Une cible existante arrête tout.** C'est ce qui transforme un écrasement silencieux en refus.
- **Le plan est archivé sous le slug**, jamais sous son nom généré, et avec le reste : il porte le
  contenu des étapes, et le rapport d'audit ne vaut qu'accompagné de ce qu'il jugeait.
  [Arborescence et nommage](../../implementation-tracker/references/contrat.md#arborescence-et-nommage).
- **Les champs du suivi archivé sont réécrits** :
  [Frontmatter](../../implementation-tracker/references/contrat.md#frontmatter).

## Abandon

Pas d'aplatissement ici ([`branche-chantier.md`](branche-chantier.md)). Les commits sont nommés, chacun
présenté et accordé ([`confirmation.md`](confirmation.md)), stagés par chemins
([`staging.md`](staging.md)). La décision — raison, dette, sort de la branche — appartient à
l'appelant ; seuls les gestes sont ici.

1. **Sur `<slug>`**, une fois le suivi passé en `statut: abandonné` : commit
   `<slug>: abandon` du suivi.
2. **Sur `base:`**, l'archivage. `git checkout <base>`, puis selon la décision :

   - *tout jeter* — ramener depuis la branche le suivi, le brief, l'audit et le plan présents,
     les archiver sous le slug, réécrire leurs champs, puis supprimer branche et tags :

     ```bash
     d=.claude/implementation/done; j=$(date +%F)
     git checkout <slug> -- <suivi> <brief> <audit> <plan>   # ne citer que ceux qui existent
     git mv <suivi> $d/$j-<slug>.md
     git mv <brief> $d/$j-<slug>.brief.md                    # idem audit et plan
     # réécrire plan:, brief:, audit: du suivi archivé vers ces cibles
     git add $d/$j-<slug>.md .claude/implementation/todo/
     git commit -m "<slug>: abandon — archivage"
     git branch -D <slug>
     git tag --list '<L>E[0-9]*'                             # puis git tag -d sur chacun
     ```

   - *garder la branche* — archiver le seul suivi, sans rien supprimer ; les tags restent, et la
     lettre avec eux :

     ```bash
     git checkout <slug> -- <suivi>
     git mv <suivi> .claude/implementation/done/$(date +%F)-<slug>.md
     git add .claude/implementation/done/$(date +%F)-<slug>.md .claude/implementation/todo/
     git commit -m "<slug>: abandon — archivage"
     ```

   Avant chaque `git mv`, une cible déjà présente arrête tout, pour la même raison qu'à la clôture.
