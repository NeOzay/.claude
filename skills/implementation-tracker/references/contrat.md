# Contrat du pipeline

Les règles **partagées** par `intent-brief`, `implementation-tracker`, `git-smart-commit` et les
deux sous-agents. Chacune est définie **ici et nulle part ailleurs** ; les fichiers qui l'appliquent
portent un renvoi ancré, jamais une copie.

**Ce qui entre ici** : ce qui est **défini** à plusieurs endroits — un format, un champ, une convention que deux fichiers
doivent respecter à l'identique.

**Pas** ce qui est seulement **appliqué** à plusieurs endroits. « Hors-périmètre » et « signaux de
dérive » apparaissent dans presque tous les fichiers du pipeline : ils y sont *utilisés*, pas
redéfinis. Les déplacer ici viderait ces fichiers de ce qui les rend opérants.

Une règle déplacée ici laisse, à son ancien emplacement, **une ligne d'appel portant sa
conséquence** — jamais un vide. `« Interdits git : lecture seule — [Contrat des sous-agents](contrat.md#contrat-des-sous-agents) »`
se lit ; l'absence, non.

**Les deux agents sont hors de ce dispositif.** `agents/step-implementer.md` et
`agents/implementation-auditor.md` dupliquent volontairement les règles qui les concernent : ils se
chargent dans leur propre fenêtre, où cette redondance ne coûte rien, et un agent en isolation qui
ne suivrait pas un renvoi perdrait le garde-fou. Cette section 5 est leur **référence de contrôle**,
pas une cible de renvoi.

Chaque règle porte **son mode de défaillance**. Sans le pourquoi, un contrat devient un schéma, et
un schéma se survole.

---

## Arborescence et nommage

```
<repo>/.claude/implementation/
  <slug>.md                      # suivi actif — commité avec le code
  <slug>.brief.md                # brief d'intention, figé après validation
  <slug>.audit.md                # rapports d'audit successifs, appendus
  done/
    <AAAA-MM-DD>-<slug>.md       # archivés à la clôture
    <AAAA-MM-DD>-<slug>.brief.md
    <AAAA-MM-DD>-<slug>.audit.md
    <AAAA-MM-DD>-<slug>.plan.md
  todo/
    README.md
    technical-debt.md            # registre de dette, alimenté à la clôture
    technical-debt-solde.md      # ce qui a été soldé, avec la commande qui l'établit
```

`done/` porte des **archives figées** ; `todo/` des registres **vivants**, relus et élagués, jamais
archivés. Le pipeline alimente `todo/` sans jamais le lire de lui-même.

**Slug** : kebab-case, court (`auth-refactor`, pas `refonte-complete-du-systeme-dauth`). Arrêté au
brief, il ne change plus — le suivi le reprend **exactement**.

> *Mode de défaillance* — le slug est la seule chose qui apparie brief, suivi, audit et plan
> archivé. Réinventé au suivi, il désapparie les quatre : plus rien ne relie l'intention au travail.

Le plan est archivé `<AAAA-MM-DD>-<slug>.plan.md`, **jamais sous son nom généré** : le harness
réattribue ces noms d'un chantier à l'autre.

> *Mode de défaillance* — c'est arrivé : le plan d'`audit-integre` a été écrasé par celui de
> `dette-technique`, et le repli `mv` de la boucle d'archivage l'a fait sans un mot.

## Frontmatter

| Fichier | Champs |
|---|---|
| `<slug>.brief.md` | `slug`, `titre`, `statut` (`brouillon` \| `validé`), `execution`, `créé` |
| `<slug>.md` (suivi) | `slug`, `titre`, `branche`, `base`, `statut` (`en-cours` \| `bloqué` \| `terminé` \| `abandonné`), `session`, `execution`, `plan`, `brief`, `audit`, `créé`, `maj` |
| `<slug>.audit.md` | `slug` |

- `branche` = `<slug>` ; `base` = la branche principale, cible de l'aplatissement final.
- `audit` n'apparaît qu'au premier audit du chantier.
- `execution` vaut `délégué` ou `direct`. Le suivi le **reprend tel quel** du brief.
  **Une valeur absente vaut `direct`.**
- `maj` est actualisé à chaque écriture dans le suivi, en même temps que le contenu.

> *Mode de défaillance* — lire un `execution` absent comme « délégable » enverrait un exécutant en
> contexte isolé sur un chantier dont personne n'a jugé la délégabilité : sans hors-périmètre ni
> signaux de dérive écrits, il n'a rien qui l'arrête et personne à qui demander.

> *Mode de défaillance* — les champs `plan`, `brief` et `audit` sont réécrits vers leurs chemins
> `done/` **pendant l'archivage**. Sans cela ils pointent vers des fichiers qui n'existent plus, ou
> pire, vers le plan d'un autre chantier — ce qui a l'air de fonctionner.

## Autorité et divergence

Le brief porte l'intention et ses bornes, **figées** à la validation. Le suivi porte les étapes et
leur avancement, **mis à jour en continu**.

**En cas de divergence, le suivi fait foi.** Le brief reste le témoin de l'intention d'origine et
n'est plus modifié.

Un périmètre qui change réellement s'amende **dans le suivi**, daté, avec une entrée au journal de
décisions.

> *Mode de défaillance* — sans cette écriture, un chantier qui évolue n'a plus de périmètre écrit
> nulle part : l'exécutant refuse en `ÉCART` un travail pourtant validé, et l'auditeur le compte
> comme un hors-périmètre entamé.

La divergence entre brief et réel est une **information** : l'effacer la détruit.

## Format d'étape et délégabilité

```
- [état] N. Intitulé — <fichier(s)> — vérif: <commande>
```

`[ ]` à faire · `[>]` en cours · `[x]` fait · `[!]` bloqué

Le suivi porte **l'intitulé et l'état** ; le **plan porte le contenu** de l'étape. C'est là que
l'exécutant va le chercher, via le champ `plan`.

- Une étape tient en **un seul tour d'exécution**. Elle se découpe au figeage, pas en cours de route.
- Une étape **sans commande de vérification n'est pas délégable**.
- Une étape **déjà entamée** puis interrompue se termine en direct, jamais en la re-déléguant.

> *Mode de défaillance* — un appel de sous-agent est atomique et ne se reprend pas : un agent froid
> lancé sur un travail à moitié fait le rapportera en `ÉCART`. Si le cas se répète, les étapes sont
> trop grosses.

## Contrat des sous-agents

Vaut pour `step-implementer` et `implementation-auditor`.

**Entrée** — l'appelant transmet des **chemins absolus**. Les chemins lus *à l'intérieur* des
fichiers (champ `plan`, fichiers d'une étape) sont relatifs à la **racine du dépôt** : l'appelant
peut la donner, sinon l'agent la calcule par `git rev-parse --show-toplevel`. Le répertoire courant
n'est pas nécessairement cette racine.

**L'appelant ne recopie rien** que les fichiers contiennent déjà — ni le diff, ni les critères, ni
les étapes.

> *Mode de défaillance* — recopier, c'est transmettre sa propre lecture à l'agent : exactement
> l'indépendance qu'on paie en le lançant.

**Git en lecture seule** : `status`, `diff`, `log`, `show`, `rev-parse`. Jamais `commit`, `add`,
`checkout`, `stash`, `reset`, `restore`, `branch`. L'agent ne commit pas et **n'écrit dans aucun
fichier de suivi**.

**Sortie** — chaque agent termine par son bloc normalisé, et rien après. L'appelant reste
responsable au retour : relire le fichier de suivi avant d'y écrire, il a pu vieillir pendant
l'exécution.

> *Mode de défaillance* — un travail partiel laissé dans l'arbre par un agent arrêté en `ÉCART` est
> voulu (il n'a pas les commandes pour revenir en arrière). Son sort se tranche **avant** toute
> autre action, sinon le prochain commit le ramasse en silence.

## Branche et commits

Le chantier vit sur une branche nommée **exactement `<slug>`**, créée depuis `base`. Tous les
commits s'y font ; ils sont aplatis en **un seul commit sur `base`** à la clôture.

- Message de commit de session : `<slug>: session N — <étape en cours>`.
- `session` est incrémenté **à chaque reprise**, pas à chaque étape : une étape peut être à cheval
  sur deux sessions.
- Une étape qui passe en `[x]` reçoit un **commit dédié**, même si un commit de session vient
  d'être fait.
- Ces commits de suivi sont **directs** : leur message est prédéterminé, ils ne passent pas par
  `git-smart-commit`. L'aplatissement de clôture, lui, est une réécriture d'historique et suit le
  workflow complet de ce skill.
- **Stager les chemins, jamais `-A`** : `git add <chemins> && git commit -m "..."`.

> *Mode de défaillance* — `-A` ramasse ce qui traîne dans l'arbre, y compris le travail partiel
> d'un agent arrêté ; `-u` raterait les fichiers créés.

**Jamais de commit, squash, rebase ou amend sans accord explicite de l'utilisateur** (règle
globale, `CLAUDE.md`). Proposer, attendre, exécuter.

## Dates et listing

**Date** — toujours obtenue par `date +%F`, jamais devinée.

> *Mode de défaillance* — le registre de dette est ordonné par date et les archives sont nommées
> par date : une date inventée casse l'ordre et l'appariement, sans qu'aucune commande n'échoue.

**Listing des suivis actifs** — passer par le script, ne jamais réécrire le filtre en ligne :

```bash
bash "$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh" .claude/implementation
```

Il remonte les seuls fichiers de suivi : ni `.brief.md`, ni `.audit.md`, ni `.plan.md`.

Le chemin est **absolu et ancré dans la skill**, jamais relatif au dépôt courant. Règle générale
pour tout script appelé depuis un skill : soit un chemin absolu ancré dans la skill, soit un appel
relatif **gardé par un test d'existence portant sur ce même script**, quand celui-ci est
légitimement local au dépôt.

> *Mode de défaillance* — un skill s'invoque depuis n'importe quel projet, où un `scripts/` local
> n'existe pas : l'appel relatif y renvoie code 127 et une **sortie vide**, que l'Étape 1 du tracker
> lit comme « aucune implémentation en cours » avant de proposer d'en créer une — en ignorant les
> chantiers réellement présents. Constaté à l'audit du 2026-08-14.

> *Mode de défaillance* — le hook `rtk` réécrit `ls` en ajoutant une colonne de taille en fin de
> ligne, ce qui empêche toute ancre `$` de matcher : un `grep -vE '\.(brief|audit)\.md$'` écrit en
> ligne n'exclut plus rien, et les trois copies du filtre ont cassé ensemble. Un script échappe à
> cette réécriture, qui ne s'applique qu'aux appels Bash du modèle.
