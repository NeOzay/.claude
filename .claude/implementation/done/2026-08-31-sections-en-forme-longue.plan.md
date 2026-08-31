# Sections du contrat list-dir en forme longue

## Contexte

Un élément de liste se remplit sans que rien ne dise **quoi** y écrire. `list-dir contract` sert une
`description` par champ (`[fields.*]`), mais `[sections]` n'est que deux listes de noms
(`contract.py:251-262`) : le corps de l'élément — l'essentiel — n'a aucune documentation là où
l'outil la lit. Le seul endroit du dépôt qui documente réellement des sections est l'en-tête en
prose de `skills/implementation-tracker/list-dir/technical-debt/templates/review.md`, que
`contract --template` ne rend jamais (« cette commande ne rend pas le `.md` »).

Ce chantier **ouvre le format** : `[sections]` devient une table par section, sur le modèle de
`[fields.*]`, portant `required` et `description`, et extensible à d'autres clés. Il n'écrit
aucune description : toutes les sections existantes migrent à `description = ""`, la rédaction
appartient à un chantier suivant.

Brief : `.claude/implementation/sections-en-forme-longue.brief.md`.

## Format cible

```toml
[sections."Constat"]
required = true
description = ""

[sections."Assumé"]
required = false
description = ""
```

- **L'ordre du TOML ordonne les sections** — il remplace le « requises d'abord, facultatives
  ensuite » de `types.py:134-136`. C'est l'ordre dans lequel `new` et `migrate` les posent.
- **`description` est une clé obligatoire à valeur libre** : absente → échec nommé ; `""` → passe.
- `required` reste facultatif, défaut `false`, comme pour un champ (`types.py:106`).
- Le contrôle « à la fois requise et optionnelle » (`contract.py:263-265`) disparaît : une clé TOML
  est unique, l'incohérence n'est plus représentable.

L'ancien format lève une erreur, sans repli ni tolérance transitoire :

```
<path>: [sections] à l'ancien format — deux listes de noms là où une table par section
est attendue. La réécriture est manuelle : voir la forme à jour dans la semence de cette
liste, « list-dir contract --def <name> » (« list-dir defs » liste les définitions
disponibles).
```

`<name>` est tiré du contrat fautif, sans vérifier qu'une définition de ce nom existe (tranché au
cadrage). Conséquence sur la lecture : `name` et `description` sont aujourd'hui lus **après** les
sections (`contract.py:267-275`) ; leur bloc remonte en tête de `parse_contract` pour que le
message puisse citer `name`.

Détection : dans la table `sections`, une clé `required` ou `optional` dont la valeur est une
**liste**. Une section légitimement nommée « required » porte une table, jamais une liste — pas de
faux positif.

## Étapes

### 1 — Le format en lecture

`skills/list-dir/scripts/listdir/types.py` :

- nouvelle dataclass `Section` (frozen) : `name`, `required: bool = False`, `description: str = ""`,
  et une property `marker` calquée sur `Field.marker` (`types.py:111-120`) ;
- `Contract.sections: Mapping[str, Section]` remplace `required_sections` / `optional_sections`
  (`types.py:127-136`), ordonné comme `Contract.fields` ;
- `required_sections` **reste**, en property `list[str]` dérivée dans l'ordre TOML : c'est ce que
  lit `store.py:198`, et l'API publique la documente ;
- `section_marker(title)` devient un lookup, et **conserve son comportement actuel sur un titre
  inconnu** : `<OPTIONNEL>`, jamais une exception.

`skills/list-dir/scripts/listdir/contract.py` :

- remplacer la lecture de `sections.required` / `sections.optional` par une boucle sur la table,
  calquée sur celle des champs (`contract.py:191-249`) : chaque entrée passe par `_table`, puis
  `_texte` pour `description`, avec un contrôle d'**absence de clé** (`"description" not in body`)
  distinct du contrôle de type.

Tests dans la même étape (`scripts/tests/test_contract.py`) : `MINIMAL` passe en forme longue ;
`test_sections_requises_d_abord` devient un test d'ordre TOML (`Assumé` déclaré avant `Constat`
ressort dans cet ordre) ; `test_section_a_la_fois_requise_et_optionnelle` et
`test_sections_required_n_est_pas_une_liste` disparaissent, remplacés par : `description` absente
refusée, `description = ""` acceptée, `description` non textuelle refusée. Les assertions
`c.sections == [...]` deviennent `list(c.sections) == [...]`.

À ce stade, l'ancien format échoue déjà — sur un message générique. C'est l'étape 2 qui le nomme.

Vérif : `uvx pytest skills/list-dir/scripts/tests/test_contract.py -q` vert.

**La suite complète est rouge des étapes 1 à 2**, et c'est attendu : `jouet.py` porte encore
l'ancien format, que l'étape 1 vient de faire échouer. Ne pas conclure à une régression — la vérif
des étapes 1 et 2 est volontairement restreinte à `test_contract.py`.

### 2 — Le refus nommé de l'ancien format

`skills/list-dir/scripts/listdir/contract.py` :

- remonter le bloc `name` / `description` en tête de `parse_contract`, pour que le message puisse
  citer `name` ;
- détecter l'ancien format avant la boucle des sections — une clé `required` ou `optional` dont la
  valeur est une **liste** — et rendre le message de migration donné plus haut.

Tests (`test_contract.py`) : un contrat à l'ancien format est refusé, le message cite
`list-dir contract --def <name>` avec le `name` du contrat fautif et mentionne `list-dir defs`.

Vérif : `uvx pytest skills/list-dir/scripts/tests/test_contract.py -q` vert.

### 3 — Les consommateurs et les fixtures

- `store.py:752` — le squelette écrit par `init` passe en forme longue
  (`[sections."Constat"]` / `required = true` / `description = ""`).
- `store.py:179,198,230,326,336` — vérifier que chaque usage tient avec un `Mapping` : itérer
  dessus donne les titres, `set(...)` et la compréhension de `create` restent justes. Aucun autre
  module ne doit apprendre la forme du TOML.
- Fixtures : `scripts/tests/jouet.py:36-38,99-101`, `test_derive_merge.py:194`,
  `test_entree_cli.py:326` et `test_store_ecriture.py:357` (deux assertions sur le squelette
  d'`init`, dont `donnees["sections"] == {"required": ["Constat"], "optional": []}`),
  `test_amorcage.py:32-33` (`required_sections` / `optional_sections` → forme retenue à l'étape 1).

Vérif : `uvx pytest skills/list-dir/scripts/tests -q` vert (303 tests avant chantier) et
`cd skills/list-dir && uvx ruff check scripts` propre.

### 4 — Migrer les contrats du dépôt

**Huit fichiers**, et non sept comme l'estimait le brief — la copie en vigueur de `review.toml`
avait été oubliée :

| Semence | Copie en vigueur |
|---|---|
| `skills/implementation-tracker/list-dir/technical-debt/contract.toml` | `.claude/implementation/todo/technical-debt/.list/contract.toml` |
| `…/technical-debt-solde/contract.toml` | `…/todo/technical-debt-solde/.list/contract.toml` |
| `…/technical-debt-ecarte/contract.toml` | `…/todo/technical-debt-ecarte/.list/contract.toml` |
| `…/technical-debt/templates/review.toml` | `…/todo/technical-debt/.list/templates/review.toml` |

Une liste amorcée est détachée de sa semence : migrer l'une ne migre pas l'autre. Réécriture à la
main, à l'identique de part et d'autre, `description = ""` partout, ordre des sections inchangé
(les requises précèdent déjà les facultatives dans ces quatre contrats — la bascule vers l'ordre
TOML ne change donc rien pour eux). Les commentaires existants de `review.toml` sont conservés.

Vérif : `list-dir contract <liste>` sur les trois registres rend la forme longue, et
`list-dir validate` passe sur chacun ; `list-dir contract .claude/implementation/todo/technical-debt
--template review` rend le gabarit migré.

**La liste de revue n'existe pas dans le dépôt** — elle naît d'un `derive`. Le critère du brief
« `validate` passe sur la liste de revue » s'exerce donc sur une liste jetable, dérivée puis
supprimée :

```bash
list-dir derive .claude/implementation/todo/technical-debt /tmp/essai-revue --template review
list-dir validate /tmp/essai-revue && rm -rf /tmp/essai-revue
```

### 5 — Documenter le format

`skills/list-dir/references/contrat-liste.md` :

- « Le contrat » (`:188-215`) — l'exemple passe en forme longue, avec la règle de `description`
  obligatoire et l'ordre TOML ;
- le tableau des marqueurs (`:244-247`) — « section de `required` » devient
  « section `required = true` », par symétrie avec les deux lignes de champ ;
- l'API Python (`:395`) — `contract.sections # Mapping[str, Section], ordonné`, plus les attributs
  de `Section` ;
- une sous-section **« Migrer un contrat »** : ce que l'ancien format déclenche, et la réécriture
  manuelle vers la semence — c'est la cible du message d'erreur.

`skills/list-dir/SKILL.md` ne décrit pas la forme de `[sections]` : rien à y changer, vérifier par
`grep -n 'sections' skills/list-dir/SKILL.md`.

Vérif : plus aucun contrat du dépôt n'est à l'ancien format — les seules occurrences restantes
sont les cas de test qui l'exercent volontairement :

```bash
grep -rn 'optional = \[' skills/ .claude/implementation/todo/
# attendu : uniquement skills/list-dir/scripts/tests/test_contract.py
```

## Vérification d'ensemble

```bash
uvx pytest skills/list-dir/scripts/tests -q                  # 303+ verts
cd skills/list-dir && uvx ruff check scripts                 # propre
list-dir contract .claude/implementation/todo/technical-debt # forme longue
list-dir validate .claude/implementation/todo/technical-debt
list-dir validate .claude/implementation/todo/technical-debt-solde
list-dir validate .claude/implementation/todo/technical-debt-ecarte
# ordre TOML de bout en bout, sur une liste jetable
list-dir init /tmp/essai-liste && list-dir new /tmp/essai-liste essai && cat /tmp/essai-liste/essai.md
```

Contrôle de non-régression du message d'erreur : rejouer `list-dir contract` sur une copie d'un
contrat resté à l'ancien format et lire le renvoi.

## Hors-périmètre

- aucune description rédigée (tout à `""`), aucune autre clé de section ajoutée ;
- aucun outil de réécriture de contrat, ni option `--sections` sur `contract` ;
- la prose d'en-tête de `templates/review.md` ne bouge pas.
