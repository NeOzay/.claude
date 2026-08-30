# Le renvoi au contrat remplace la recopie des catégories de verdict

Brief : `.claude/implementation/renvoi-contrat-des-categories.brief.md` (validé, `execution: direct`)

## Contexte

La doc de `debt-review` porte une copie de ce que le contrat de la liste de revue déclare — les
sept catégories de verdict. La copie littérale est la boucle des piles de
`skills/debt-review/SKILL.md:276` ; le compte « sept » est recopié dans `gabarit-rapport.md:50`,
`SKILL.md:49` et `:53`. Une huitième catégorie ajoutée à
`skills/implementation-tracker/list-dir/technical-debt/templates/review.toml` laisserait toute
cette prose en décrire sept, sans qu'aucune commande n'échoue : `validate` juge les fiches contre
le contrat, jamais la doc contre lui. C'est la dette
`.claude/implementation/todo/technical-debt/gabarit-rapport-recopie-les-categories.md`.

Ce qui a fait reporter la correction : la liste de revue n'existe qu'après `derive`, si bien qu'un
renvoi à `list-dir contract <revue>` vise une liste qui n'existe pas au moment où le lecteur lit le
gabarit. Le renvoi doit viser le **gabarit source** de la définition `technical-debt` — et
`list-dir contract` ne sait aujourd'hui imprimer que le contrat d'une liste existante
(`skills/list-dir/scripts/listdir/commands/contract.py`).

Le chantier lève ce blocage, puis solde la dette.

**Fait qui structure la solution** : le `values` de `review.toml` porte déjà exactement l'ordre non
alphabétique de la boucle des piles — ce qui sort du registre d'abord, ce qui y reste ensuite.
L'ordre n'est donc pas une information que seule la prose détient.

## Ce que le chantier ne fait pas

- **le garde-fou sur `categories.md`** — confronter ses sept titres de section aux `values` du
  contrat. Trou réel, écarté par arbitrage, porté au registre de dette à l'étape 7.
- la prose de `categories.md` : elle porte le sens de chaque catégorie et sa preuve exigée, que le
  contrat ne porte pas. Seuls les **comptes** « sept » y sont touchés.

**Signaux d'arrêt** — si `contract` se met à faire autre chose qu'imprimer (filtrer, juger,
reformater), c'est raté : `--values` extrait, il ne trie ni ne valide. Si la prose de
`categories.md` se fait réécrire, s'arrêter.

---

## Étape 1 — `contract` accepte trois cibles, et un gabarit

`skills/list-dir/scripts/listdir/commands/contract.py`.

La commande ne sait viser qu'une liste. Lui donner les deux options d'`init` — `--def <nom>` (par
son nom, résolu dans les quatre rangs par `definitions.resolve`) et `--from <chemin>` (un
répertoire de définition, tel quel) — plus `--template <nom>`, qui vise la paire de gabarits au
lieu du contrat.

Le positionnel `liste` devient `nargs="?"` et rejoint le groupe mutuellement exclusif : une cible,
et une seule. Aucune cible du tout est une erreur d'appel (code 2), comme `--def` et `--from`
ensemble.

**Le point qui unifie les trois cas** : une liste range ses gabarits sous `<liste>/.list/templates/`,
une définition sous `<def>/templates/`. Résoudre d'abord une **base** — `<liste>/.list` ou
`<def>` — rend le reste identique dans les trois cas :

| | base | sans `--template` | avec `--template <n>` |
|---|---|---|---|
| `<liste>` | `<liste>/.list` | `base/contract.toml` | `base/templates/<n>.toml` |
| `--def <nom>` | `resolve(nom)` | idem | idem |
| `--from <chemin>` | `<chemin>` | idem | idem |

Réutiliser sans les recopier : `definitions.resolve`/`roots` (déjà importés par `init.py`),
`contract.CONTRACT`, `contract.TEMPLATES`, `contract.LIST_DIR`, et `contract.parse_contract`.

**La validation reste, et change de véhicule.** `utils.open()` ne sait ouvrir qu'une liste :
le remplacer par `parse_contract(texte, chemin)` sur le texte lu. La garde d'origine est conservée
telle quelle — imprimer sans juger rendrait un contrat cassé sous un code de succès, et le lecteur
croirait tenir la règle en vigueur. Le texte reste **rendu tel quel**, commentaires compris : c'est
la règle de la commande, et les `#` d'un contrat portent souvent le pourquoi d'un champ.

Fichier absent → échec nommant le fichier attendu, sur le modèle de
`store._read_definition` (« définition sans contrat — `contract.toml` attendu ») et de
`ListStore.template` (« gabarit « <nom> » incomplet — ce fichier manque »). Ici seul le `.toml` est
exigé : `contract` ne rend pas le `.md`, et l'exiger ferait échouer une commande d'impression sur
un fichier qu'elle n'imprime pas.

Vérifier au passage que `sniff_list_dir` (`list-dir.py`) n'est pas perturbée : elle retient le
premier positionnel portant un `.list/`, or ni un nom de définition ni un répertoire de définition
n'en porte — les commandes propres à une liste restent invisibles dans ces deux cas, ce qui est
correct.

Tests dans `skills/list-dir/scripts/tests/test_entree_cli.py`, à la suite de la section
`# ---- contract` (l. 383) et sur le modèle des tests d'`init --def/--from` (l. 274, 314) :
les trois cibles, avec et sans `--template` ; `--def` inconnu ; `--def` et `--from` ensemble
(code 2) ; aucune cible (code 2) ; gabarit inexistant ; contrat de définition cassé refusé.

**Vérification** : `cd skills/list-dir/scripts && python -m pytest tests/ -q`

> *Étape dense* — argparse restructuré, base résolue à trois cas, bascule de `utils.open()` vers
> `parse_contract`, trois échecs nommés et sept cas de test. Elle tient parce que tout vit dans un
> seul fichier de commande, mais c'est la plus susceptible de déborder : si elle déborde, couper
> après la résolution des trois cibles et traiter `--template` à part.

## Étape 2 — `contract --values <champ>`

Même fichier. `--values <nom-de-champ>` imprime les `values` déclarées du champ, **une par ligne,
dans l'ordre du contrat**, et rien d'autre — pas de préambule, pour que
`for c in $(...)` soit sûr.

Se combine avec les trois cibles et avec `--template`. Le contrat est de toute façon déjà parsé
par l'étape 1 : les valeurs se lisent sur `Contract.fields[nom].values`
(`skills/list-dir/scripts/listdir/types.py:109`), sans second parseur.

Deux échecs nommés :

- champ inconnu → message listant les champs déclarés, sur le modèle du « connues : … » de
  `definitions.resolve` et de la commande inconnue de `list-dir.py` ;
- champ sans `values` → le dire en nommant le champ. Un `enum` en a toujours (`parse_contract`
  refuse un enum vide) ; tout autre type n'en a en général pas, et rendre zéro ligne sous un code 0
  serait précisément l'échec silencieux que ce paquet existe pour supprimer.

`--values` **extrait**, il ne trie ni ne filtre ni ne juge : l'ordre rendu est celui du fichier.

Tests : sortie exacte sur un enum du contrat-jouet ; ordre préservé (et non alphabétique) ; champ
inconnu ; champ sans `values` ; combinaison avec `--def … --template …`.

**Vérification** : `cd skills/list-dir/scripts && python -m pytest tests/ -q`

## Étape 3 — Documenter la commande étendue

- `skills/list-dir/SKILL.md` — le tableau des douze commandes (l. 53) gagne les trois formes de
  `contract`, sur la mise en page déjà employée par `init` juste au-dessus (l. 47-49).
- `skills/list-dir/references/contrat-liste.md` l. 106-116 — **la prose y devient fausse** : elle
  affirme que `contract` lit toujours `<liste>/.list/contract.toml`, « jamais depuis une
  définition ». La corriger sans perdre ce qu'elle protège : sans option, `contract` imprime la
  règle **réellement appliquée** ; avec `--def`/`--from`, il imprime celle d'une **définition**,
  qui ne s'applique à aucune liste tant qu'elle n'en a pas semé une. Dire les deux, et pourquoi
  la distinction compte — une liste amorcée est détachée de sa semence, rien ne les
  resynchronise (`store.init_list`).

**Vérification** — trois contrôles mécaniques, depuis la racine du dépôt :

```bash
grep -c -- "--def\|--from\|--template" skills/list-dir/SKILL.md          # >= 6 (init + contract)
grep -q "jamais depuis une définition" skills/list-dir/references/contrat-liste.md \
  && echo "ÉCHEC : la prose devenue fausse est toujours là"
list-dir help | grep contract                                            # les formes annoncées
```

Attendu : le premier compte augmente des trois formes de `contract`, le deuxième n'imprime rien,
le troisième rend la description à jour.

## Étape 4 — L'ordre des `values` s'écrit dans le contrat

La boucle des piles va tirer sa liste du contrat (étape 5) ; la doctrine que la prose de
`debt-review/SKILL.md` porte aujourd'hui — cet ordre est sémantique, pas alphabétique — doit alors
vivre là où on la lira en éditant les `values`, c'est-à-dire dans le contrat lui-même.

Ajouter un commentaire au-dessus de `values` du champ `category`, dans **les deux exemplaires**,
qui doivent rester identiques :

- `skills/implementation-tracker/list-dir/technical-debt/templates/review.toml` — la définition ;
- `.claude/implementation/todo/technical-debt/.list/templates/review.toml` — la copie amorcée.

> *Incertitude du brief, tranchée ici* : la doctrine va au contrat, pas à la prose. Elle contraint
> qui édite `values` ; le laisser dans `SKILL.md` la mettrait hors de vue de la seule personne
> qu'elle concerne. Une ligne reste néanmoins près de la boucle (étape 5) pour dire au lecteur que
> l'ordre n'est pas arbitraire et où il est fixé.

**Vérification** :
`diff skills/implementation-tracker/list-dir/technical-debt/templates/review.toml .claude/implementation/todo/technical-debt/.list/templates/review.toml`
(sortie vide) puis
`list-dir contract .claude/implementation/todo/technical-debt --template review --values category`
(les sept, dans l'ordre).

## Étape 5 — La boucle des piles cesse d'énumérer

`skills/debt-review/SKILL.md` l. 276-278. **État courant** — la boucle porte les sept
identifiants en dur :

```bash
for c in a-solder non-pertinent doublon pas-une-dette aggravee pertinent inverifiable; do
  printf '%-16s %s\n' "$c" "$(list-dir list "$R" --where category=$c | wc -l)"
done
```

**Cible** :

```bash
for c in $(list-dir contract "$R" --values category); do
  printf '%-16s %s\n' "$c" "$(list-dir list "$R" --where category=$c | wc -l)"
done
```

`"$R"` est la liste de revue, qui **existe** à ce point de la procédure (Étape 3 du skill l'a
dérivée) : c'est bien le contrat en vigueur qui est interrogé, pas la semence.

Réécrire la prose qui suit (« c'est l'énumération ci-dessus qui le porte, et elle suit
`categories.md` ») : l'ordre est désormais porté par le `values` du contrat, où le commentaire de
l'étape 4 dit pourquoi il n'est pas alphabétique. Conserver le contraste avec `--sort category`,
qui ordonne alphabétiquement, et avec `--sort date`, qui ordonne l'intérieur d'une pile.

**Vérification** — rejouer la boucle sur le vrai registre, après `derive` dans un répertoire jetable :

```bash
T=$(mktemp -d)
list-dir derive .claude/implementation/todo/technical-debt "$T/revue" --template review
list-dir contract "$T/revue" --values category
for c in $(list-dir contract "$T/revue" --values category); do
  printf '%-16s %s\n' "$c" "$(list-dir list "$T/revue" --where category=$c | wc -l)"
done
rm -rf "$T"
```

Attendu : les sept identifiants dans l'ordre du contrat, un seul portant l'effectif (le marqueur
`<À REMPLIR>` sur une revue non instruite), les autres à 0.

## Étape 6 — Le renvoi dans `gabarit-rapport.md`, et les comptes

`skills/debt-review/references/gabarit-rapport.md` l. 50 — remplacer « un des sept identifiants de
`categories.md` » par un renvoi exécutable **avant toute dérivation**, donc vers la définition :

```bash
list-dir contract --def technical-debt --template review --values category
```

Ne garder en prose que ce que le contrat ne porte pas : le sens de chaque catégorie et sa preuve
exigée vivent dans `categories.md`, qui reste le renvoi pour cela. La phrase sur `validate` qui
refuse une valeur hors liste est conservée — elle dit ce que l'outil fait, pas ce qu'il contient.

Puis les comptes « sept », qui sont la même copie sous une autre forme :

- `skills/debt-review/SKILL.md:49` « les sept catégories » et `:53` « sept fiches instruites, une
  par catégorie » ;
- `skills/debt-review/references/categories.md:1` (le titre) et `:26` (« Aucune des sept ») ;
- `skills/debt-review/references/exemple-revue.md:4` « sept verdicts possibles ».

**Rien d'autre n'est touché dans `categories.md` et `exemple-revue.md`** : leur prose porte le sens,
et c'est un signal d'arrêt du brief.

Les cinq occurrences sont **toutes** reformulées sans le compte — « les catégories de verdict »,
« une fiche instruite par catégorie », « # Les catégories », « Aucune d'elles », « un verdict par
fiche ». Le critère devient alors mécanique : plus aucun « sept » ne subsiste.

**Vérification** :

```bash
list-dir contract --def technical-debt --template review --values category
grep -rn "sept" skills/debt-review/ && echo "ÉCHEC : un compte subsiste"
grep -rn "a-solder non-pertinent" skills/debt-review/ && echo "ÉCHEC : énumération en dur"
```

Attendu : la commande rend les sept identifiants ; les deux `grep` ne trouvent rien (code 1) et
n'impriment donc aucun « ÉCHEC ». Les mentions isolées d'un identifiant dans les sections
d'arbitrage (`SKILL.md` l. 337-352) restent : elles nomment une catégorie à la fois pour dire quoi
en faire, ce n'est pas une liste recopiée — d'où le motif à deux termes du second `grep`.

## Étape 7 — Solder la dette, ouvrir celle du garde-fou

Par commandes de `list-dir`, jamais à la main.

1. Reporter au registre les deux champs de revue de l'entrée
   `gabarit-rapport-recopie-les-categories`, puis la déplacer :
   `list-dir move .claude/implementation/todo/technical-debt gabarit-rapport-recopie-les-categories .claude/implementation/todo/technical-debt-solde`
   — la preuve du solde est la sortie de la commande de vérification de l'étape 6.
2. Créer l'entrée du garde-fou écarté, sous l'id
   **`sections-de-categories-jamais-confrontees-au-contrat`** :

   ```bash
   list-dir new .claude/implementation/todo/technical-debt \
     sections-de-categories-jamais-confrontees-au-contrat
   ```

   Constat à écrire, et rien de plus : les titres de section de `categories.md` sont une copie de
   l'**ensemble** des `values` du champ `category` ; une valeur ajoutée au contrat laisserait le
   fichier en décrire une de moins, sans qu'aucune commande n'échoue. `--values category` (étape 2)
   rend désormais la confrontation possible en une ligne — c'est ce qui fait de ce trou une dette
   soldable plutôt qu'un vœu. `source` : ce chantier.

Le format exact d'une entrée et la règle de solde : `skills/implementation-tracker/references/dette.md`.

**Vérification** :

```bash
list-dir validate .claude/implementation/todo/technical-debt --filled
list-dir validate .claude/implementation/todo/technical-debt-solde --filled
list-dir list .claude/implementation/todo/technical-debt-solde | grep gabarit-rapport
```

---

## Vérification d'ensemble

```bash
cd skills/list-dir/scripts && python -m pytest tests/ -q && ruff check . && ruff format --check .
```

puis, depuis la racine du dépôt, les commandes des étapes 4 à 7 — ce sont elles qui prouvent que le
renvoi est exécutable, et non seulement écrit.
