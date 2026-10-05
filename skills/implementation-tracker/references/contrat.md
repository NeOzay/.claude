# Contrat du pipeline

Les règles **partagées** par `intent-brief`, `implementation-tracker` et les
deux sous-agents. Chacune est définie **ici et nulle part ailleurs** ; les fichiers qui l'appliquent
portent un renvoi ancré, jamais une copie.

**Ce qui entre ici** : ce qui est **défini** à plusieurs endroits — un format, un champ, une
convention que deux fichiers doivent respecter à l'identique.

**Pas** ce qui est seulement **appliqué** à plusieurs endroits. « Hors-périmètre » et « signaux de
dérive » apparaissent dans presque tous les fichiers du pipeline : ils y sont *utilisés*, pas
redéfinis. Les déplacer ici viderait ces fichiers de ce qui les rend opérants.

Une règle déplacée ici laisse, à son ancien emplacement,
**une ligne d'appel portant sa conséquence** — jamais un vide.
`« Interdits git : lecture seule — [Contrat des sous-agents](contrat.md#contrat-des-sous-agents) »`
se lit ; l'absence, non.

**Les deux agents sont hors de ce dispositif.** `agents/implementation-auditor.md` et
`agents/plan-reviewer.md` dupliquent volontairement les règles
qui les concernent : ils se chargent dans leur propre fenêtre, où cette redondance ne coûte rien, et
un agent en isolation qui ne suivrait pas un renvoi perdrait le garde-fou. Cette section 5 est leur
**référence de contrôle**, pas une cible de renvoi.

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
    revues/
      <AAAA-MM-DD>-revue.md      # rapports de revue du registre, un par passage
  todo/
    README.md
    technical-debt/              # registre de dette, alimenté à la clôture
      .list/contract.toml        #   le contrat : ce qu'une entrée doit porter
      <id>.md                    #   une entrée = un fichier
    technical-debt-solde/        # ce qui a été soldé, avec la commande qui l'établit
    technical-debt-ecarte/       # ce qui en est sorti sans avoir été payé, avec son motif
    road-map/                    # les tâches qu'on veut accomplir, notées à la demande
    road-map-fait/               # celles qu'un chantier a portées, avec ce chantier
    road-map-ecarte/             # celles qu'on a cessé de vouloir, avec leur motif
```

`done/` porte des **archives figées** ; `todo/` des registres **vivants**, relus et élagués, jamais
archivés. Une archive relate le Chantier tel qu'il a été clos : elle n'a pas à passer
`gabarit check --filled` contre la Semence courante, et ne se réécrit jamais pour s'y conformer.
Qu'une archive ne passe plus un contrat qui a évolué depuis n'est pas une dette. Le pipeline
alimente `todo/` à la clôture et ne l'ouvre à aucun autre moment ; seul `debt-review`, invoqué à la
main, le relit et le met à jour.

Les six registres sont des **répertoires-listes** : un répertoire = une liste, un fichier = une
entrée, un `.list/contract.toml` qui déclare la structure. Ils ne s'éditent jamais à la main — les
commandes du skill `list-dir` créent, valident, déplacent et agglomèrent. Contrat des entrées et
gestes autorisés : `dette.md` pour la dette, `road-map.md` pour la road-map. Les deux familles se
distinguent par ce qu'elles portent — un constat vérifié d'un côté, une tâche voulue de l'autre — et
par qui les alimente : [Road-map](road-map.md#la-frontière-avec-le-registre-de-dette).

> *Mode de défaillance* — les trois listes de dette ont d'abord été trois fichiers Markdown uniques.
> Solder une entrée revenait à découper trente lignes de prose et à les recoller ailleurs, sans
> qu'aucune commande ne signale une perte. Un `mv` ou une édition de front matter à la main
> ramène exactement ce mode d'échec.

Un rapport de revue est daté, non slugué : il ne se rattache à aucun chantier. Le
**sous-répertoire** `done/revues/` n'est pas cosmétique — il le tient hors de portée du listing
des suivis, qui ne descend qu'à un niveau.

> *Mode de défaillance* — posé à plat dans `done/`, un rapport de revue serait remonté comme un
> fichier de suivi : le contrôle des chemins de frontmatter y chercherait des champs `plan`, `brief`
> et `audit` qu'il n'a pas, et le listing lui-même compterait un chantier qui n'existe pas.

**Slug** : kebab-case, court (`auth-refactor`, pas `refonte-complete-du-systeme-dauth`). Arrêté au
brief, il ne change plus — le suivi le reprend **exactement**.

> *Mode de défaillance* — le slug est la seule chose qui apparie brief, suivi, audit et plan
> archivé. Réinventé au suivi, il désapparie les quatre : plus rien ne relie l'intention au travail.

Le plan est archivé `<AAAA-MM-DD>-<slug>.plan.md`, **jamais sous son nom généré** : le harness
réattribue ces noms d'un chantier à l'autre.

> *Mode de défaillance* — c'est arrivé : le plan d'`audit-integre` a été écrasé par celui de
> `dette-technique`, et le repli `mv` de la boucle d'archivage l'a fait sans un mot.

## Frontmatter

Les champs d'un brief et d'un suivi, leurs valeurs admises et ce que chacun porte sont déclarés par
leur semence, et nulle part ailleurs : `gabarit contract brief`, `gabarit contract suivi`. La
fiche est posée par `gabarit new` et vérifiée par `gabarit check --filled` ; une structure recopiée
d'un modèle en prose divergerait du contrat sans que rien ne le signale. Le front matter est du
TOML entre `+++`. Seules les archives de `done/` antérieures aux semences restent en YAML `---`,
lues en repli et jamais réécrites. Le rapport d'audit `<slug>.audit.md` n'a pas de semence : son
front matter ne porte que `slug`.

Ce qui suit est ce que les champs **font** au pipeline, et que leur description ne suffit pas à
garantir :

- `session` est incrémenté **à chaque reprise**, pas à chaque étape : une étape peut être à cheval
  sur deux sessions.
- `lettre` est attribuée à la création, et le script de clôture refuse un suivi qui n'en porte
  pas : [Tags d'étape](../../git-smart-commit/references/tags-etape.md).
- `modèle` est repris du Plan, pour tout le Chantier :
  [Modèle d'implémentation](#modèle-dimplémentation).
- `audit` n'apparaît qu'au premier audit du chantier.
- `plan`, `brief` et `audit` sont réécrits vers leurs chemins `done/` **pendant l'archivage**.
  Sans cela ils pointeraient vers des fichiers qui n'existent plus, ou pire, vers le plan d'un
  autre chantier — ce qui a l'air de fonctionner.
- `road-map` porte l'**`id`** de l'entrée dont le chantier est parti, pas un chemin : il n'est
  **pas** réécrit à l'archivage, puisqu'il ne désigne aucun fichier qui bouge vers `done/`. C'est
  lui qui dit à la clôture quoi déplacer vers `road-map-fait/`
  ([Road-map](road-map.md#le-champ-road-map)).
- `maj` est actualisé à chaque écriture dans le suivi, en même temps que le contenu.
- `skills` nomme les Shadow-skills du Chantier, `[]` si aucun ; `shadow-skill depuis-suivi` le lit
  à la reprise. Les archives de `done/` antérieures au champ ne le portent pas.

## Autorité et divergence

Le brief porte l'intention et ses bornes, **figées** à la validation. Le suivi porte les étapes et
leur avancement, **mis à jour en continu**.

**En cas de divergence, le suivi fait foi.** Le brief reste le témoin de l'intention d'origine et
n'est plus modifié.

Un périmètre qui change réellement s'amende **dans le suivi**, daté, avec une entrée au journal de
décisions.

> *Mode de défaillance* — sans cette écriture, un chantier qui évolue n'a plus de périmètre écrit
> nulle part : l'auditeur compte comme un hors-périmètre entamé un travail pourtant validé.

La divergence entre brief et réel est une **information** : l'effacer la détruit.

## Format d'étape

```
- [état] N. Intitulé — <fichier(s)> — vérif: <commande>
```

`[ ]` à faire · `[>]` en cours · `[x]` fait · `[!]` bloqué

`[>]` se pose quand le travail de l'étape commence, pas au commit de la précédente : entre les deux,
une modification est une Retouche de l'étape livrée
([Commit rapide de chantier](../../git-smart-commit/references/etape.md)).

Le suivi porte **l'intitulé et l'état** ; le **plan porte le contenu** de l'étape. C'est là que la
session qui l'exécute va le chercher, via le champ `plan`.

Une étape tient en **un seul tour d'exécution**. Elle se découpe au figeage, pas en cours de route.

> *Mode de défaillance* — une étape trop grosse ne tient pas dans une session : interrompue, elle
> se reprend à froid sur un travail à moitié fait, que son commit d'étape réunit sans que personne
> l'ait vu d'un bloc.

## Modèle d'implémentation

Un Chantier est conduit par **un seul modèle**, Sonnet ou Opus, choisi au Plan pour toute
l'implémentation. La session qui suit la Passation de la création démarre à vide : l'utilisateur y
fait `/model <modèle>`. Rien ne change le modèle à sa place, ni par Étape, ni par session.

**Sonnet** pour un travail bien délimité, **Opus** pour un travail complexe et mal délimité. Trois
critères le disent :

- **la vérification** — le code se contrôle bien plus facilement que la prose : un Chantier fait
  surtout de prose penche vers Opus ;
- **les incertitudes du brief** — Sonnet seulement si le Plan les tranche toutes ;
- **le nombre d'Étapes** — plus de 12 : Opus.

**Au moindre doute, Opus.**

> *Mode de défaillance* — un Chantier de prose mené par Sonnet se paie en Retouches : le texte a
> l'air juste, la vérification n'y voit pas d'écart, et la relecture le découvre après le commit
> d'étape.

## Contrat des sous-agents

Vaut pour `implementation-auditor` et `plan-reviewer`.

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

## Dates et listing

**Date** — toujours obtenue par `date +%F`, jamais devinée.

> *Mode de défaillance* — le registre de dette est ordonné par date et les archives sont nommées
> par date : une date inventée casse l'ordre et l'appariement, sans qu'aucune commande n'échoue.

**Listing des suivis actifs** — passer par le script, ne jamais réécrire le filtre en ligne :

```bash
impl-list .claude/implementation
```

Il remonte les seuls fichiers de suivi : ni `.brief.md`, ni `.audit.md`, ni `.plan.md`.

Le chemin est **absolu et ancré dans la skill**, jamais relatif au dépôt courant. Règle générale
pour tout script appelé depuis un skill : soit un chemin absolu ancré dans la skill, soit un appel
relatif **gardé par un test d'existence portant sur ce même script**, quand celui-ci est
légitimement local au dépôt.

> *Mode de défaillance* — un skill s'invoque depuis n'importe quel projet, où un `scripts/` local
> n'existe pas : l'appel relatif y renvoie code 127 et une **sortie vide**, que la Phase 1 du
> tracker lit comme « aucune implémentation en cours » avant de proposer d'en créer une — en
> ignorant les chantiers réellement présents. Constaté à l'audit du 2026-08-14.

> *Mode de défaillance* — le hook `rtk` réécrit `ls` en ajoutant une colonne de taille en fin de
> ligne, ce qui empêche toute ancre `$` de matcher : un `grep -vE '\.(brief|audit)\.md$'` écrit en
> ligne n'exclut plus rien, et les trois copies du filtre ont cassé ensemble. Un script échappe à
> cette réécriture, qui ne s'applique qu'aux appels Bash du modèle.
