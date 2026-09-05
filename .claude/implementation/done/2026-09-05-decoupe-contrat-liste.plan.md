# Découper et réécrire la référence de `list-dir`

## Contexte

`skills/list-dir/references/contrat-liste.md` fait **828 lignes / 41 Ko** — trois fois le plus
gros fichier de référence du dépôt (`implementation-tracker/references/contrat.md`, 16 Ko). Il a
grossi par accrétion : chaque chantier de `list-dir` y a ajouté sa section, les deux derniers
(`b2c4c35`, `15ad011`) à eux seuls ~170 lignes.

La gêne principale n'est pas la taille mais **la dispersion d'un même sujet** :

| Sujet | Décrit aujourd'hui à |
|---|---|
| `derive` | « L'API Python » (l. 610-618), « Listes dérivées » (762-816), « `def` prend deux formes » (205-245) |
| le contrat | « Le contrat » (372-500), « Définitions de listes » (44-173), « Provenance » (175-341) |
| `validate` | « L'API Python » (580-596), « Ce que `validate` avertit » (247-267), « Les marqueurs » (502-535) |
| `merge` | « L'API Python » (620-630), « Le rendu de `merge` » (818-828) |
| `move`, `list`, `help` | enfouis dans « L'API Python », qui n'est pas leur sujet |

`## L'API Python` (l. 537-683) est le nœud : sous un titre qui annonce une surface de
programmation, il documente en réalité la sémantique de six commandes.

**Résultat visé** : un sujet = un fichier = une autorité, les autres y renvoyant par lien plutôt
que de redire (doctrine déjà appliquée entre skills, `e9f6a81`). `contrat-liste.md` est la source
de la réécriture, n'est pas modifié pendant le chantier, et est supprimé à la fin.

Brief : `.claude/implementation/decoupe-contrat-liste.brief.md`.

## Le découpage

Cinq fichiers dans `skills/list-dir/references/`, ~100 à 250 lignes chacun :

| Fichier | Sujet — une autorité | Repris de `contrat-liste.md` |
|---|---|---|
| `format.md` | ce qu'est une liste, un élément, un contrat, un marqueur | préambule (1-7), §Structure (8-42), §Un élément (344-370), §Le contrat + Préremplir (372-500), §Les marqueurs (502-535) |
| `definitions.md` | amorcer depuis une définition : les quatre racines, la précédence, l'autorité bornée à l'`init`, ce que `contract` vise | §Définitions de listes et ses 4 sous-sections (44-173) |
| `provenance.md` | `[origin]`, les deux formes de `def`, ce que `validate` avertit, `reseed`, l'adoption | §Provenance et péremption et ses 4 sous-sections (175-341) |
| `operations.md` | les commandes qui agissent : `validate`, `migrate`, `move`, `list`, `derive`, `merge` | §API Python (580-596, 610-646), §Quand le contrat change (721-761), §Listes dérivées (762-816), §Le rendu de `merge` (818-828) |
| `extension.md` | la surface d'extension : bibliothèque Python (`Result`, `ListStore`, `Item`, `Contract`) et commandes personnalisées | §API Python (537-578, 597-608, 647-681), §Commandes : déclaration, découverte, surcharge (685-719) |

**Pourquoi `extension.md` réunit la lib et les commandes** : ce sont les deux façons d'ajouter du
comportement à `list-dir` sans toucher au paquet — même lecteur, même moment. Ce qui en sort, la
sémantique des six commandes, part en `operations.md`, où chacune est décrite une seule fois.

**Pourquoi `definitions.md` et `provenance.md` restent séparés** alors que les deux parlent de
semis : « d'où vient une liste » se lit à la création, « est-elle encore à jour » des mois plus
tard. Les fusionner rendrait un fichier de 300 lignes, c'est-à-dire le défaut qu'on corrige.

## Ce que la réécriture fait au texte

- **Condenser** deux passages qui disent la même chose sous deux angles (p. ex. « `derive`
  projette, il ne copie pas » écrit deux fois, l. 610-618 et 774-780).
- **Intégrer les `> *Mode de défaillance*`** (12 occurrences) à l'exemple ou à la description de
  la fonctionnalité qu'ils justifient, au lieu de les laisser en blocs cités isolés. Aucun ne
  disparaît sans être intégré ailleurs — c'est un signal de dérive du brief.
- **Ne rien changer au fond.** Une règle qui change de sens sous couvert de réécriture arrête le
  chantier.

## Les renvois, et le garde-fou qui les couvre

Le contrôle 8 de `scripts/check_pipeline.py` vérifie chemin **et ancre** de tout renvoi
documentaire, mais son motif `RENVOI_INTER_SKILL` (l. 638) n'accepte que les chemins commençant
par `../`. Un renvoi entre fichiers voisins — `[X](provenance.md#ancre)` — lui échappe, c'est une
dette ouverte (`todo/technical-debt/renvois-sans-prefixe-hors-du-controle-des-ancres.md`), et le
découpage va justement en créer beaucoup.

**Décision : écrire les renvois voisins sous la forme `../references/<fichier>.md#<ancre>`.**
`cible = md.parent / rel` résout correctement (`references/../references/x.md`), le lien reste
cliquable, et les renvois entrent sous le contrôle 8 **sans modifier `check_pipeline.py`** — ce
que le hors-périmètre du brief interdit. La dette reste ouverte pour les renvois intra-fichier.

**Conséquence sur l'ordre des étapes** : un renvoi vers un fichier pas encore écrit est un renvoi
mort, que le contrôle 8 refuse. Les étapes 2 à 6 ne posent donc que les renvois vers les fichiers
**déjà écrits** (l'ordre `format` → `definitions` → `provenance` → `operations` → `extension` est
choisi pour ça) ; l'étape 7 pose les renvois restants — ceux qui pointent vers l'aval — en même
temps que les externes. `python3 scripts/check_pipeline.py` doit donc rester vert **à chaque
étape**, ce qui donne aux étapes d'écriture une vérification réelle plutôt qu'un comptage.

Renvois externes à repointer (tous en `../`, donc déjà couverts par le contrôle 8) :

| Fichier | Ancre actuelle | Cible |
|---|---|---|
| `debt-review/SKILL.md:178` | `#listes-dérivées` | `operations.md` |
| `debt-review/SKILL.md:287` | `#ce-que-contract-vise-et-ce-que-ça-engage` | `definitions.md` |
| `implementation-tracker/references/dette.md:13,135` | `#structure-dun-répertoire-liste`, `#un-élément` | `format.md` |
| `implementation-tracker/references/dette.md:37,127` | `#définitions-de-listes` | `definitions.md` |
| `implementation-tracker/references/dette.md:42` | `#provenance-et-péremption` | `provenance.md` |
| `implementation-tracker/references/dette.md:200,215` | `#quand-le-contrat-change`, `#lapi-python` (règle du commit mixte) | `operations.md` |
| `list-dir/SKILL.md:87,95,99,145` | renvois par titre, sans ancre | les cinq fichiers |
| `list-dir/scripts/listdir/commands/contract.py:34` | `references/contrat-liste.md` (forme d'appel de `--values`) | `references/definitions.md` |

**Exception au signal de dérive, ratifiée le 2026-09-05** : le brief dit « si le chantier touche
`scripts/listdir/`, il a débordé », et liste pourtant `contract.py` en consommateur à repointer.
Le signal vise un changement de comportement ; une docstring n'en est pas un. Seule cette
docstring est modifiée dans `scripts/listdir/` — tout le reste, code et tests, est intouchable.

Les archives `.claude/implementation/done/` ne sont **pas** touchées : ce sont des instantanés
datés, et `check_pipeline` n'examine que `skills/`.

**Les fiches de dette ouvertes, si** (ratifié le 2026-09-05). 12 mentions dans 8 fiches de
`.claude/implementation/todo/technical-debt/` citent `contrat-liste.md`, dont des consignes
directement inexécutables une fois le fichier supprimé — `gabarit-jamais-retire-par-re-semis.md:31`
(« Documenter la règle côté gabarits dans `contrat-liste.md`, section "Provenance et péremption" »),
`validate-avertit-hors-machine-semeuse.md:32`, `where-compare-textuellement.md:49`,
`regles-hors-contrat-sans-empreinte.md:14,39`, `remontee-sarrete-au-premier-claude.md:35`,
`definition-aplatit-les-sous-repertoires-de-templates.md:21,34`,
`version-de-gabarit-comparee-a-rien.md:15`, `ruff-format-jamais-applique.md:11`,
`semence-et-copie-divergent-sans-controle.md:32`. Une étape dédiée les repointe vers le fichier
compétent. Aucun `.md` de `todo/` n'est examiné par `check_pipeline` : la vérification est un
`grep`.

## Le garde-fou de complétude

Aucune règle ne doit se perdre entre 828 lignes et cinq fichiers. Un inventaire est produit
**avant** la première réécriture, dans `.claude/implementation/decoupe-contrat-liste.inventaire.md`
(versionné, supprimé à la clôture) :

```markdown
- R001 (l. 32) Tout `*.md` à la racine d'une liste est un élément, sans exception.
- R002 (l. 38) Une liste sans élément est valide pour `init` et `validate`, erreur pour `merge` et `derive`.
```

Chaque règle reçoit sa destination au fil des étapes : `→ format.md`. Le contrôle final est
mécanique :

```bash
INV=.claude/implementation/decoupe-contrat-liste.inventaire.md
AFFECTE='^- R[0-9]\{3\} (l\. [0-9]*) → [a-z]*\.md'   # la flèche de destination, pas celle d'un texte de règle
[ "$(grep -c '^- R' $INV)" = "$(grep -c "$AFFECTE" $INV)" ] && echo COMPLET || echo "RÈGLES ORPHELINES"
grep '^- R' $INV | grep -v "$AFFECTE\|→ [a-z]*\.md'   # les nommer
```

> **Écart au brief ratifié le 2026-09-05** : le brief dit « inventaire figé **dans le plan** ». Il
> vit dans un fichier annexe versionné — aussi traçable et rejouable, sans gonfler le plan de
> ~120 lignes de règles à relire deux fois.

## Étapes

1. **Inventaire des règles** — `.claude/implementation/decoupe-contrat-liste.inventaire.md` : une
   ligne par règle normative de `contrat-liste.md`, numérotée, avec sa ligne d'origine, dans
   l'ordre du fichier. Les **11** sections `##` réelles doivent toutes être représentées —
   `## Constat` et `## Pour solder` (l. 356, 360) sont dans le bloc de code d'exemple, pas des
   sections.
   *Vérif* : `grep -c '^- R' <inv>` > 0 ; la dernière règle citée porte une ligne ≥ 818 (dernière
   section du fichier source) :
   ```bash
   grep -o 'l\. *[0-9]*' <inv> | tr -dc '0-9\n' | sort -n | tail -1   # attendu >= 818
   ```

2. **`format.md`** — structure d'une liste, un élément, le contrat (types, sections en table,
   préremplissage `text`/`command`), les marqueurs. Modes de défaillance intégrés aux exemples.
   *Vérif* : `python3 scripts/check_pipeline.py` passe ; `grep -c '^- R.*→ format\.md' <inv>` > 0.

3. **`definitions.md`** — forme d'une définition, les quatre racines, qui gagne, « la définition
   n'est autorité que le temps de l'`init` », ce que `contract` vise (les trois cibles,
   `--template`, `--values` et la règle du code de retour).
   *Vérif* : `python3 scripts/check_pipeline.py` passe ; `grep -c '^- R.*→ definitions\.md' <inv>` > 0.

4. **`provenance.md`** — table `[origin]`, `def` nomme sans localiser, les deux formes du nom,
   ce que `validate` avertit, `reseed` (fusion à trois points, ordre d'écriture, `--force`),
   adopter une liste antérieure.
   *Vérif* : `python3 scripts/check_pipeline.py` passe ; `grep -c '^- R.*→ provenance\.md' <inv>` > 0.

5. **`operations.md`** — `validate` (ce qu'il confronte, avec et sans `--filled`), `migrate`,
   `move` (renommage pur, commit séparé), `list` (format de sortie, `--where`), `derive`
   (projection, `from`, estampille du gabarit), `merge` (rendu, recomptage hors blocs de code).
   *Vérif* : `python3 scripts/check_pipeline.py` passe ; `grep -c '^- R.*→ operations\.md' <inv>` > 0.

6. **`extension.md`** — import de la bibliothèque, `Result`, la surface de `ListStore`, `Item`
   immuable et le pourquoi, `Contract` ; déclaration/découverte/surcharge des commandes,
   `DESCRIPTION`/`REQUIRES`, `help` et sa lecture par `ast.parse`.
   *Vérif* : `python3 scripts/check_pipeline.py` passe ; `grep -c '^- R.*→ extension\.md' <inv>` > 0.

7. **Repointer les renvois** — `list-dir/SKILL.md` (section « Pour aller plus loin » et les
   quatre renvois en ligne), `debt-review/SKILL.md`, `implementation-tracker/references/dette.md`,
   `skills/list-dir/scripts/listdir/commands/contract.py`.
   *Vérif* : `python3 scripts/check_pipeline.py` — contrôle 8 vert, aucun renvoi mort.

8. **Repointer les fiches de dette** — les 12 mentions des 8 fiches de
   `.claude/implementation/todo/technical-debt/` listées plus haut, chacune vers le nouveau
   fichier compétent, en gardant la section visée quand elle est nommée.
   *Vérif* : `grep -rn 'contrat-liste\.md' .claude/implementation/todo/` ne rend que des mentions
   **historiques** du fichier supprimé, et aucun renvoi vivant — le motif sans `.md` matche aussi le
   slug du chantier, cité en `source` des fiches qu'il produit.

9. **Contrôle de complétude et suppression** — toute règle de l'inventaire porte sa destination,
   puis `git rm skills/list-dir/references/contrat-liste.md` **et** `git rm` de l'inventaire : son
   suffixe `.inventaire.md` n'est pas dans `ANNEXES` (`check_pipeline.py:330`), il serait donc
   remonté comme fichier de suivi parasite s'il partait à l'archivage.
   *Vérif* : le bloc de contrôle ci-dessus rend `COMPLET` ; `python3 scripts/check_pipeline.py`
   passe ; `grep -rn 'contrat-liste' skills/ scripts/ .claude/implementation/todo/` sans résultat.

## Vérification de bout en bout

```bash
cd /home/debian/.claude
python3 scripts/check_pipeline.py                 # tous contrôles, dont le 8
grep -rn 'contrat-liste' skills/ scripts/ .claude/implementation/todo/   # aucun résultat
wc -l skills/list-dir/references/*.md             # aucun fichier au-delà de ~250 lignes
list-dir help                                     # le skill reste opérationnel
cd skills/list-dir/scripts && uvx pytest tests -q  # inchangé — aucun code touché
```

Le dernier point est un contrôle de non-régression du hors-périmètre : le chantier ne touche
ni `scripts/listdir/` (hors la docstring de `contract.py`) ni les tests, la suite doit passer
telle quelle.
