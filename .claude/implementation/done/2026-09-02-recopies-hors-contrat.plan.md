# Une règle, un endroit — résorber les recopies hors `contrat.md`

## Context

Une même règle écrite cinq fois a fini par donner deux réponses contradictoires. La preuve exigée
d'une entrée classée `doublon` est **l'`id`** de l'entrée conservée selon `dette.md` « Écarter »,
`categories.md` « Doublon » et `gabarit-rapport.md` — mais **l'intitulé** selon la règle de preuve
en tête de `categories.md` (qui se contredit donc lui-même à cinquante lignes d'écart) et selon
`templates/review.md`, la semence de fiche que lit l'agent qui instruit une revue.

`scripts/check_pipeline.py` ne l'a pas vu : son mécanisme d'empreintes ne couvre que les 9 sections
de `contrat.md`. Les règles dont l'autorité est ailleurs — `dette.md`, `contrat-liste.md`,
`templates/review.md` — ne sont protégées par rien.

Le chantier tranche la contradiction en faveur de l'`id`, puis résorbe les recopies qui l'ont
produite, pour que chaque règle reste définie à un seul endroit **y compris quand cet endroit n'est
pas `contrat.md`**.

**Arbitrages déjà rendus, et par qui :**

| Décision | Rendue |
|---|---|
| L'autorité de l'`id` est `contrat-liste.md` ; l'intitulé n'est jamais une référence | **en cadrage** (brief) |
| Le mécanisme anti-recopie est hors de ce chantier ; le renoncement s'écrit | **en cadrage** (brief) |
| Autorité du comptage `merge` : `debt-review/SKILL.md` Étape 3 | **en planification** — le brief la porte en « à désigner » ; à ratifier avec ce plan |
| `contrat-liste.md:572`, 7ᵉ écriture hors tableau, entre au périmètre | **en planification** — à ratifier avec ce plan |

## Principe directeur

Une correction ne supprime **jamais** la prose qui porte du *jugement* — c'est l'arbitrage de
`renvoi-contrat-des-categories`, en vigueur : « la prose porte du jugement, qu'un renvoi ne
remplace pas ». Ce qui se supprime, c'est la règle **re-développée** ; ce qui la remplace, c'est un
renvoi.

`gabarit-rapport.md:59-61` fournit le patron interne à imiter, sur les catégories :

> Ce que chacune veut dire et la preuve qu'elle exige : `categories.md`. Ce fichier-ci ne les
> recopie pas — une énumération de plus à tenir à jour se désynchroniserait sans qu'aucune commande
> ne le dise.

**Écrire les renvois en lien markdown relatif** (`[Solder](../implementation-tracker/references/dette.md#solder)`),
jamais en prose à backticks. Le contrôle 8 du garde-fou ne capte que la forme `](../…#ancre)` et
vérifie alors chemin **et** ancre : c'est ce qui rend le travail vérifiable par commande. Il compte
16 renvois aujourd'hui.

Ancres vérifiées contre `slugify()` de `check_pipeline.py` : `#solder`, `#un-élément`,
`#ce-que-contract-vise-et-ce-que-ça-engage`, `#étape-3--agglomérer-et-restituer`,
`#contrat-des-sous-agents`, `#format-détape-et-délégabilité`.

**Les greps de vérification portent tous `--include='*.md'`** : les docstrings de
`listdir/commands/*.py` et des tests énoncent les mêmes règles pour le code, elles sont hors sujet
et hors périmètre. Sans le filtre, chaque vérification rendrait rouge sur une exécution correcte.

## Étapes

### 1. Trancher la contradiction `doublon` en faveur de l'`id`

Les deux écritures fautives passent à `id` :

- `skills/debt-review/references/categories.md:17` — « où la preuve est l'intitulé de l'entrée
  conservée » → l'`id` ;
- `skills/implementation-tracker/list-dir/technical-debt/templates/review.md:16` — « Pour un
  `doublon`, citer l'intitulé de l'entrée conservée » → l'`id`.

`review.md` est une **semence** : la corriger à la main dans la définition *et* dans sa copie
amorcée `.claude/implementation/todo/technical-debt/.list/templates/review.md` (aujourd'hui
identiques, `diff` vide). Le re-semis automatique est hors-périmètre — dernière démonstration de son
coût, à consigner au journal.

*Vérification* — attendu : aucune sortie, puis `diff` vide.

```bash
grep -rn "intitulé de l'entrée conservée" skills/ .claude/implementation/
diff skills/implementation-tracker/list-dir/technical-debt/templates/review.md \
     .claude/implementation/todo/technical-debt/.list/templates/review.md
```

### 2. Recopie « `id` = seule identité » — `dette.md:127` → renvoi

`dette.md:127-129` (« L'`id` est la clé de référence et de dédoublonnage. Il ne change jamais »)
re-développe la règle dont `contrat-liste.md` « Un élément » (l. 179) est l'autorité. Remplacer le
développement par un renvoi, en gardant ce qui est **propre au registre** : que le point 3
d'*Alimenter* dédoublonne sur l'`id`, et qu'un `doublon` cite l'`id` de la conservée.

*Vérification* — « ne change jamais » vaut 1 aujourd'hui, attendu **0** ; garde-fou vert avec un
renvoi de plus.

```bash
grep -rn --include='*.md' "ne change jamais" skills/
python3 scripts/check_pipeline.py
```

### 3. Recopie « commit mixte / détection de renommage » — trois copies → renvois

Autorité : `dette.md` « Solder » (l. 207-209). Trois écritures la re-développent :

- `skills/implementation-tracker/references/cloture.md:69-72` — **prose courante, pas un
  blockquote**, et elle porte déjà le renvoi inline `([Solder](dette.md#solder))` en fin de phrase.
  La correction est un raccourcissement : garder la prescription (« le déplacement et l'écriture de
  la preuve ne partagent jamais un commit »), retirer le *pourquoi* re-développé, conserver le
  renvoi ;
- `skills/debt-review/SKILL.md:379-381` — blockquote *Mode de défaillance*, à supprimer ; le renvoi
  existe déjà l. 375-377, à passer en lien markdown avec ancre ;
- `skills/list-dir/references/contrat-liste.md:572` — **7ᵉ écriture, entrée au périmètre par
  arbitrage.** Applique la règle à `migrate` au lieu de `move` ; garder la prescription propre à
  `migrate`, renvoyer pour le motif.

*Vérification* — vaut 4 en `.md` aujourd'hui, attendu **1** (`dette.md:209`). Les deux occurrences
en `.py` (`move.py:5`, `test_move.py:74`) sont hors périmètre et restent.

```bash
grep -rn --include='*.md' "détection de renommage" skills/
python3 scripts/check_pipeline.py
```

### 4. Recopie « substitution qui avale l'échec » — `debt-review` Ét. 3 → renvoi

Autorité : `contrat-liste.md` « Ce que `contract` vise, et ce que ça engage » (l. 141-155).
`skills/debt-review/SKILL.md:285-293` re-développe l'intégralité du raisonnement — substitution
vide, `while read` contre découpage de mots zsh.

**Garder** ce qui est local et absent de l'autorité : le choix du `if … ; false` plutôt qu'un
`|| exit 1`, motivé par le collage dans un shell interactif. C'est un jugement propre à ce skill.
Le bloc de code reste ; c'est la prose explicative qui devient un renvoi.

*Vérification* — vaut 2 en `.md` aujourd'hui, attendu **1** (`contrat-liste.md:142`, qui écrit
« avale l'échec »).

```bash
grep -rn --include='*.md' "avale" skills/
python3 scripts/check_pipeline.py
```

### 5. Recopie « sections de la fiche de revue » — `gabarit-rapport.md` → renvoi

Autorité : `technical-debt/templates/review.md`, dont le préambule décrit déjà les quatre sections.
`gabarit-rapport.md:70-86` les redécrit une par une. Appliquer aux sections le patron que ce même
fichier applique déjà aux catégories (l. 59-61) : renvoyer, ne pas énumérer.

**Garder** le blockquote *Mode de défaillance* sur le marqueur (l. 88-92) : il porte sur
`validate --filled` un jugement qu'aucune autre écriture ne fait.

*Vérification* — vaut 2 aujourd'hui, attendu **0**.

```bash
grep -c "^- \*\*Vérifié par\*\*\|^- \*\*Verdict\*\*" skills/debt-review/references/gabarit-rapport.md
python3 scripts/check_pipeline.py
```

### 6. Recopie « comptage `merge` / préambule 16 — 16 » — autorité désignée

**`debt-review/SKILL.md` Étape 3** devient l'autorité : le geste s'y fait, et le blockquote « 16
fiches de 17 entrées → préambule 16 — 16 » (l. 264-266) y reste.

`gabarit-rapport.md:140-146` garde sa phrase descriptive (« le préambule dit ce que `merge` a pu
vérifier, et rien de plus »), perd le « 16 — 16 » redit, et son renvoi vers « `SKILL.md`, Étape 3 »
(l. 145) passe en lien markdown avec ancre `#étape-3--agglomérer-et-restituer`.

*Vérification* — vaut 2 aujourd'hui, attendu **1** (`SKILL.md:265`).

```bash
grep -rn --include='*.md' "16 — 16" skills/
python3 scripts/check_pipeline.py
```

### 7. Recopie « 3 modes de défaillance des sous-agents » — `tracker/SKILL.md` Ét. 4 → renvois

Autorité : `contrat.md`, sections « Format d'étape et délégabilité » (l. 140-142) et « Contrat des
sous-agents » (l. 164-169). `skills/implementation-tracker/SKILL.md` Étape 4 les re-développe :
sous-agent atomique (l. 175 et 268), travail partiel dans l'arbre (l. 289), relire le suivi avant
d'y écrire.

**Attention** — les empreintes `« un seul tour »`, `« rev-parse --show-toplevel »` et
`« ramasse ce qui traîne »` doivent rester à **exactement une occurrence**, dans `contrat.md`. Ne
rien déplacer qui les contienne : c'est le contrôle 2 qui l'attrape.

**Garder** la table `RÉSULTAT` → action et la règle « rendre la main après chaque étape déléguée » :
elles sont opératoires, pas définitionnelles.

*Vérification* — « atomique » vaut 3 aujourd'hui, attendu **1** (`contrat.md:140`) ; « travail
partiel » vaut 3, attendu **2** (`contrat.md:167` et `:186`, deux sections distinctes du contrat).

```bash
grep -rn --include='*.md' "atomique" skills/
grep -rn --include='*.md' "travail partiel" skills/
python3 scripts/check_pipeline.py
```

### 8. Consigner le renoncement au mécanisme

Une entrée au registre de dette : les règles dont l'autorité n'est pas `contrat.md` ne sont
couvertes par aucune empreinte ; une huitième recopie passerait au vert. Consigner les options
étudiées (empreintes libres indexées par `(fichier-autorité, ancre)` / sections marquées) et la
raison du report.

Écriture par `list-dir`, jamais à la main.

*Vérification* — l'entrée existe **et** le registre valide (38 éléments aujourd'hui, 39 attendus).

```bash
list-dir list .claude/implementation/todo/technical-debt | wc -l
list-dir validate .claude/implementation/todo/technical-debt --filled
```

## Vérification d'ensemble

```bash
python3 scripts/check_pipeline.py                                    # 8 contrôles verts
grep -rn "intitulé de l'entrée conservée" skills/ .claude/implementation/   # vide
git diff --stat master...HEAD
```

Les deux contrôles qui portent réellement ce chantier : **contrôle 2** (une empreinte du contrat ne
doit jamais passer à 2 occurrences — filet contre un déplacement maladroit) et **contrôle 8** (tout
renvoi ajouté résout, chemin et ancre).

Relecture humaine indispensable sur le point qu'aucune commande ne couvre : **aucune prose de
jugement n'a été remplacée par un renvoi.** C'est le premier signal de dérive du brief.

## Signaux de dérive (rappel du brief)

**Arrêt sec** : une prose de jugement remplacée par un renvoi ; une ligne de mécanisme écrite avant
que les recopies soient soldées.

**Arrêt pour arbitrage** : un fichier hors du tableau des recopies est touché (`contract.toml`,
fiches dérivées, `agents/*.md`) ; une correction de rédaction s'ajoute sans résorber de recopie.
Recevable si pertinente — mais c'est l'utilisateur qui le dit. `contrat-liste.md:572` a suivi
exactement ce chemin et a été admis.
