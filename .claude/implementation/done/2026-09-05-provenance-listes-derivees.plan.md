# Provenance des listes dérivées

## Contexte

Le chantier b2c4c35 a donné à chaque liste une estampille `[origin]` : elle sait de quelle
définition elle vient, `validate` avertit quand la définition a bougé, `reseed` rattrape sur ordre.
**Les listes engendrées par `derive` sont restées hors du dispositif.**

`derive` (`store.py:475`) copie le gabarit `<src>/.list/templates/<nom>.toml` verbatim en
`<dst>/.list/contract.toml` et n'écrit rien d'autre. Le seul gabarit en circulation,
`technical-debt/templates/review.toml`, n'a pas de table `[origin]` : toute liste de revue naît donc
sans provenance, et `debt-review` — qui enchaîne `derive` puis `validate` (`SKILL.md:170`) — se fait
dire à chaque revue :

```
.../rev : aucune provenance déclarée — « list-dir reseed <liste> --def <nom> » pour l'adopter…
```

L'estampille visée est **documentaire** : `def = "technical-debt/review"` nomme le gabarit source
pour qu'un lecteur sache quoi taper (`list-dir contract --def technical-debt --template review`
existe déjà). Elle ne devient **pas** une définition résolvable — les gabarits servent à transformer
une liste existante, pas à en amorcer une. Et parce qu'une liste de revue est jetable, le gabarit
porte `frozen = true` : elle naît gelée, il n'y a rien à y rattraper.

**Fait vérifié en cadrage** : `_origin` accepte déjà un `/` (il n'interdit que le vide et l'espace),
et `frozen = true` fait déjà taire tous les avertissements. Poser la table à la main dans le contrat
d'une dérivée suffit à ramener `validate` à rc 0 sans un mot. Le chantier n'est donc **pas** de
faire marcher l'estampille, mais de la rendre **sûre** — un format validé plutôt que toléré — et
**honnête** là où du code irait chercher un gabarit comme s'il était une définition.

## Approche

Trois changements de code, tous petits, et de la doctrine. Aucune commande ni option nouvelle.

### 1. Le format composite devient une règle, au lieu d'être toléré

Aujourd'hui `def = "technical-debt/revue"` (faute de frappe) passe, et personne ne le saura jamais :
une estampille fausse est pire qu'une absente.

- `scripts/listdir/contract.py`, `_origin` : après le refus du vide et de l'espace, valider la forme
  — soit un segment unique, soit exactement deux séparés par `/`, chacun non vide et différent de
  `.` / `..`. Le modèle existe déjà juste au-dessus, dans `source_path` (`contract.py:84`), qui
  refuse qu'un nom de gabarit soit un chemin ; reprendre sa formulation d'échec.
- Exposer la décomposition **une seule fois**, sous forme de propriétés sur `Origin`
  (`scripts/listdir/types.py`) : `definition` (premier segment) et `template` (second, ou `None`).
  `Origin` n'est construit que par `_origin`, donc les propriétés peuvent supposer un nom déjà
  validé — le dire dans la docstring.

### 2. Un message honnête là où le nom composite serait résolu

Deux chemins de code iraient chercher `technical-debt/review` dans les quatre rangs et rendraient
« définition introuvable », ce qui est faux et envoie chercher au mauvais endroit.

- `scripts/listdir/definitions.py`, `resolve` : refuser d'emblée un nom composite en disant ce
  qu'il est — un gabarit ne s'amorce ni ne se rattrape. C'est ce qui donne son message à
  `list-dir reseed <liste> --def technical-debt/review` (`commands/reseed.py:70`) et, par le même
  chemin, à `init --def technical-debt/review`, explicitement hors-périmètre.
- `scripts/listdir/provenance.py`, `_peremption` : traiter le nom composite **avant** l'appel à
  `resolve`, et rendre un avertissement disant que la péremption d'un gabarit n'est pas suivie.
  Ce cas ne se produit que sur une dérivée qu'on aurait dégelée à la main — mais il ne doit pas
  mentir pour autant.

Ne pas en faire un quatrième silence : `warnings()` en documente trois (`def = false`, `frozen`,
pas de `.list/semence/`), et un gabarit dégelé n'est aucun des trois.

### 3. Estampiller le gabarit, et rattraper le registre vivant

Le gabarit existe en deux exemplaires, aujourd'hui identiques au diff près :

| Exemplaire | Rôle |
|---|---|
| `skills/implementation-tracker/list-dir/technical-debt/templates/review.toml` | la définition |
| `.claude/implementation/todo/technical-debt/.list/templates/review.toml` | la copie du registre vivant |
| `…/.list/semence/templates/review.toml` | le point de référence, réécrit par le `reseed` |
| `…/.list/backup/templates/review.toml` | la marche arrière locale, hors dépôt (`.gitignore`) |

- Poser dans le gabarit de la **définition** la table `[origin]` : `def = "technical-debt/review"`,
  `version = 1`, `frozen = true`. Un commentaire dit pourquoi le gel — une liste de revue vit une
  journée, elle n'a rien à rattraper.
- Bumper `origin.version` de `technical-debt/contract.toml` de 1 à 2 : la version estampille la
  définition **entière**, gabarits compris, et c'est le seul signal qui dira au registre vivant
  qu'il a décroché.
- Rattraper le registre par le dispositif lui-même, plutôt qu'à la main des deux côtés :
  `list-dir reseed .claude/implementation/todo/technical-debt`. La fusion à trois points n'a aucun
  conflit à trancher — le local n'a pas bougé, la semence gagne (`fusionner_gabarits`,
  `provenance.py:492`, appelée l. 591). Le même geste réécrit `.list/semence/`, ce qui est le point :
  c'est lui qui rend le rattrapage idempotent.

C'est la seule étape qui **mute des données de l'utilisateur**. Passer d'abord `--dry-run`. Si la
fusion rendait un conflit — elle ne le devrait pas, les quatre copies étant identiques aujourd'hui —
`reseed` n'écrit rien : **s'arrêter et le remonter**, ne trancher aucune clé à la place de qui l'a
écrite.

### 4. La doctrine

- `skills/list-dir/references/contrat-liste.md` :
  - section « Provenance et péremption » — la forme `mère/dérivée` d'une estampille de gabarit, ce
    qu'elle nomme et ce qu'elle ne permet pas (pas de résolution), et `frozen = true` comme norme
    d'une liste jetable ;
  - section « Listes dérivées » — la dérivée reçoit son estampille du gabarit, comme toute liste la
    reçoit de sa semence ; `derive` n'écrit pas de `.list/semence/`, une liste gelée n'ayant rien à
    rattraper.
- `skills/list-dir/SKILL.md` : un mot dans le paragraphe « Une liste sait d'où elle vient », qui
  n'évoque aujourd'hui que les listes semées par `init`.

Chaque règle à un seul endroit (e9f6a81) : le `SKILL.md` renvoie, il ne redit pas.

## Étapes

1. **Valider le format d'un nom d'estampille** — `scripts/listdir/contract.py`,
   `scripts/listdir/types.py`, `scripts/tests/test_provenance.py`
   vérif: `uvx pytest skills/list-dir/scripts/tests -q && (cd skills/list-dir && uvx --with pytest basedpyright)`

2. **Dire la vérité sur un nom composite là où il serait résolu** — `scripts/listdir/definitions.py`,
   `scripts/listdir/provenance.py`, `scripts/tests/test_provenance.py`,
   `scripts/tests/test_definitions.py`
   vérif: `uvx pytest skills/list-dir/scripts/tests -q && (cd skills/list-dir && uvx --with pytest basedpyright)`

3. **Garder la dérivée silencieuse par un test** — `scripts/tests/test_derive_merge.py` : une liste
   dérivée d'un gabarit estampillé ne produit aucun avertissement de provenance
   vérif: `uvx pytest skills/list-dir/scripts/tests/test_derive_merge.py -q`

4. **Estampiller `review.toml` et rattraper le registre** —
   `skills/implementation-tracker/list-dir/technical-debt/{contract.toml,templates/review.toml}`,
   puis `reseed --dry-run` et `reseed` du registre
   vérif: `list-dir validate .claude/implementation/todo/technical-debt` rc 0 sans avertissement,
   et le 1er encadré de la section Vérification

5. **Écrire la doctrine** — `skills/list-dir/references/contrat-liste.md`,
   `skills/list-dir/SKILL.md`
   vérif: `uvx pytest skills/list-dir/scripts/tests -q`, plus le contrôle d'ancre ci-dessous

## Vérification

Le critère central, qui est le symptôme lui-même :

```bash
S=$(mktemp -d)
list-dir derive .claude/implementation/todo/technical-debt "$S/rev" --template review
list-dir validate "$S/rev"        # attendu : rc 0, AUCUNE ligne sur stderr
grep -A3 '^\[origin\]' "$S/rev/.list/contract.toml"
```

Le format refusé, avec la clé nommée — sur une liste-jouet dont on écrit l'estampille à la main :

```bash
# def = "a/b/c", def = "a/", def = "../x"  →  validate non nul, message nommant « origin », « def »
```

Le message honnête, sur une dérivée dégelée à la main (`frozen = false`) :

```bash
list-dir validate "$S/rev"    # doit parler de gabarit, JAMAIS de « introuvable dans les quatre rangs »
list-dir reseed "$S/rev" --def technical-debt/review   # refus qui dit qu'un gabarit ne se rattrape pas
```

Le registre vivant rattrapé, et intact :

```bash
list-dir validate .claude/implementation/todo/technical-debt   # rc 0, aucun avertissement
list-dir list .claude/implementation/todo/technical-debt | wc -l   # 43, inchangé
```

Tout renvoi ajouté au `SKILL.md` doit viser une ancre qui existe — le dépôt en utilise déjà
(`#listes-dérivées`, cité par `debt-review/SKILL.md`) :

```bash
# pour chaque ancre citée dans SKILL.md, le titre correspondant doit exister dans le contrat
grep -o 'contrat-liste\.md#[a-zà-ÿ0-9-]*' skills/list-dir/SKILL.md | sort -u
grep -n '^#\{2,4\} ' skills/list-dir/references/contrat-liste.md
```

L'ensemble :

```bash
uvx pytest skills/list-dir/scripts/tests -q                      # 428 aujourd'hui, + les nouveaux
(cd skills/list-dir && uvx --with pytest basedpyright)           # 0 error
```

## Hors-périmètre (rappel du brief)

- pas d'`init --def technical-debt/review` — un gabarit transforme une liste existante
- pas de commande qui suivrait l'estampille (`contract <rev> --seed` écarté explicitement)
- l'**instance** source du `derive` n'entre pas dans `[origin]` : elle n'est connue qu'au moment du
  `derive`, l'écrire romprait « `init` n'écrit jamais cette table, il la reçoit »
- `derive` n'écrit pas de `.list/semence/`

**Signaux de dérive** : une commande ou une option nouvelle ; `derive` qui écrirait l'estampille au
lieu de la recopier ; `resolve()` qui rendrait autre chose qu'un répertoire de définition.
