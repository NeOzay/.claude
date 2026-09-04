# Provenance et péremption du contrat d'une liste semée

## Contexte

Une liste amorcée par `list-dir init --def <nom>` reçoit **une copie** du contrat de sa
définition, et cette copie est dès lors la seule règle appliquée (`store.init_list`,
`store.open_list`). C'est voulu : un projet peut redéfinir sa liste chez lui. Le prix est qu'une
skill qui écrit dans une liste suppose que le contrat vaut sa semence — et le jour où la semence
évolue, plus rien ne le dit. La seule trace de cette hypothèse aujourd'hui est un message d'erreur
qui **devine** le nom de la définition à partir du `name` du contrat (`listdir/contract.py:323`).

On garde la main locale et on surveille la péremption : la copie reste seule appliquée, mais elle
porte d'où elle vient et à quelle version, `validate` avertit quand la définition a bougé, et
`reseed` rattrape sur ordre. Brief : `.claude/implementation/peremption-contrat.brief.md`.

**Toutes les commandes de vérification se lancent depuis `skills/list-dir/`**, sauf mention
contraire. Les chemins des étapes 1 à 6 sont relatifs à ce répertoire ; les étapes 7 et 8 le
disent quand elles en sortent.

## Le modèle

**`[origin]` vit dans `contract.toml`, et la semence le porte aussi.** La copie reste donc octet
pour octet égale à sa semence — l'invariant que défend la docstring d'`init_list`
(`scripts/listdir/store.py:744`, « les écraser ferait mentir le `diff` qui prouve qu'une semence
est la copie de son original »). `init` n'écrit jamais cette table, il la **reçoit** :
`--from <chemin>` estampille donc exactement comme `--def`.

```toml
[origin]
def = "technical-debt"   # le nom de la définition, ou false : cette liste n'a pas de semence
version = 3              # entier ≥ 1, obligatoire dès que `def` est un nom
frozen = false           # facultatif — cette liste a délibérément pris la main
```

- **`def` nomme, il ne localise pas.** Un chemin dépend de la machine, et c'est le motif pour
  lequel une liste qui référence sa semence a été écartée. `reseed` rerésout ce nom dans les
  quatre rangs (`definitions.resolve`, `scripts/listdir/definitions.py:180`) ;
  `reseed --from <chemin>` reste la porte de sortie quand la définition n'est installée nulle part.
- **`frozen = true`** tait l'avertissement de péremption **et fait refuser `reseed`** ; `--force`
  passe outre, et **rien d'autre** : sur un conflit, `reseed` refuse toujours, `--force` compris.
  C'est ce refus de dégel qui justifie le mot, là où `pinned` n'aurait dit qu'un état.
- **`def = false`** tait l'avertissement d'adoption. Le squelette d'`init` sans `--def` le porte
  d'emblée : une liste née à la main n'a pas de semence à rattraper.

**`.list/semence/` garde la semence intacte** (contrat + gabarits), telle qu'elle était au dernier
semis. C'est le point de référence sans lequel `reseed` ne peut pas distinguer un apport de la
semence d'une édition locale — et il a la forme exacte d'une définition, donc
`contract.load_source` (`scripts/listdir/contract.py:75`) le lit sans rien de neuf.

## Étapes

### 1. `[origin]` au contrat

- `scripts/listdir/types.py` : `Origin` (frozen dataclass) — `name: str | None` (None =
  `def = false`), `version: int`, `frozen: bool` ; `Contract.origin: Origin | None = None`
  (None = table absente). Exporter `Origin` dans `scripts/listdir/__init__.py`.
- `scripts/listdir/contract.py` : `_origin(raw.get("origin"), path)` sur le modèle de
  `_table`/`_texte`. Échecs nommés, jamais de valeur prise sur parole : clé inconnue dans
  `[origin]`, `def` absent, `def` ni chaîne ni `false`, nom vide ou porteur d'une espace (même
  motif que les `values` d'un enum : il traverse une substitution de shell), `version` absente ou
  < 1 quand `def` est un nom, `version`/`frozen` présentes sous `def = false`.
- Tests : `scripts/tests/test_provenance.py`, un cas de refus par règle, plus l'absence de
  `[origin]` qui reste légitime.

**Vérification** : `uvx pytest scripts/tests/test_provenance.py scripts/tests/test_contract.py -q`

### 2. `init` : estampille reçue, semence pristine, contrôle du nom

- `scripts/listdir/store.py`, `init_list` : avec une définition, écrire en plus
  `.list/semence/contract.toml` et `.list/semence/templates/` — mêmes octets que ce qui va dans
  `.list/`. Sans définition, le squelette gagne `[origin]\ndef = false` (après `description`,
  avant les `[fields.*]`).
- `scripts/listdir/commands/init.py` : `--def <nom>` sur une semence dont `[origin].def` déclare
  un autre nom → échec **code 2**, comme `--name` sur une définition (`init.py:60`). L'estampille
  mentirait sur ce que `reseed` ira chercher. `--from` n'est pas concerné : il n'affirme aucun nom.
- Une définition **sans** `[origin]` reste utilisable et sème une liste sans provenance —
  l'avertissement d'adoption de l'étape 3 la signalera.
- Tests : `scripts/tests/test_amorcage.py` / `test_definitions.py` — `diff` semence ↔ copie muet,
  `.list/semence/` identique, squelette porteur de `def = false`, refus du nom discordant.

**Vérification** : `uvx pytest scripts/tests -q`

### 3. Les avertissements

- `scripts/listdir/provenance.py` (neuf) : `warnings(list_dir, contract) -> list[str]`, sans effet
  de bord. Les cas, dans cet ordre :

  | État | Sortie |
  |---|---|
  | pas d'`[origin]` | « aucune provenance déclarée » + le geste d'adoption |
  | `def = false` | rien |
  | `frozen = true` | rien (ni péremption, ni modification locale) |
  | définition introuvable dans les quatre rangs | péremption invérifiable, dit avec le nom cherché |
  | semence illisible ou sans `[origin]` | avertissement nommant le fichier |
  | `version` semence > liste | « périmée : v2 → v5 » + `list-dir reseed <liste>` |
  | `version` semence < liste | la semence est en retard — état anormal, dit tel quel |
  | `.list/semence/` présent et différent du contrat **ou d'un gabarit** en vigueur | « modifié localement depuis le semis », fichier par fichier |

  La dernière ligne ne résout aucune définition : elle vaut encore sur une machine où le skill
  n'est pas installé. `.list/semence/` absent → on se tait sur ce point, la péremption reste dite.

- **Canal** : `Result.message` sur un succès, aujourd'hui inutilisé — `list-dir.py:110` ne l'écrit
  que sur échec. `types.ok()` et `Toolbox.ok()` prennent un `message: str = ""` ; `list-dir.py`
  écrit `result.message` sur **stderr** après avoir imprimé la valeur sur stdout. Un avertissement
  ne change jamais le code de retour et ne pollue jamais stdout — ce que `contract --values` ferait
  avaler à un `while read`.
- `scripts/listdir/commands/validate.py` : joindre les avertissements au succès **comme à
  l'échec** — les éléments d'une liste périmée restent conformes au contrat qu'elle porte.
- Tests : un cas par ligne du tableau, plus un test CLI en sous-processus
  (`scripts/tests/test_entree_cli.py`) prouvant stdout propre / stderr porteur / code inchangé.

**Vérification** : `uvx pytest scripts/tests -q`

### 4. L'émetteur TOML et le moteur de fusion (bibliothèque seule)

Aucune commande ici : la CLI vient à l'étape 5. Tout vit dans
`scripts/listdir/provenance.py`, à côté des avertissements — le module porte un seul sujet,
les rapports d'une liste avec sa semence.

- **Émetteur** `emit(contract) -> str` : `name`, `description`, `[origin]`, `[fields.*]`,
  `[sections."…"]`, dans l'ordre de la semence puis les clés propres au local. Réutiliser
  `items.dump_value` pour les scalaires et les listes plutôt qu'une interpolation — le motif est
  déjà écrit dans `init_list`. Test d'aller-retour : `parse_contract(emit(c)) == c`.
- **Fusion à trois points, clé TOML par clé TOML** (`fields.category.values`,
  `sections."Constat".description` — la granularité du bloc `[fields.x]` noierait un conflit d'une
  seule ligne dans un bloc entier) :

  | base (`.list/semence/`) vs local | Issue |
  |---|---|
  | local = base, semence a bougé | la semence gagne |
  | semence = base, local a bougé | le local gagne, aucun bruit |
  | les deux ont bougé, valeurs différentes | **CONFLIT** — rien n'est écrit |
  | clé absente de la semence, présente ailleurs | **gardée et signalée** (règle de `migrate`) |

- **Gabarits** : même logique à trois points, mais à la granularité du **fichier entier** — un
  gabarit est un texte libre, il ne se fusionne pas par clé. Local = base → la semence gagne ;
  semence = base → le local reste ; les deux ont bougé → conflit.
- **Sans base** (liste antérieure) : seul ce qui **manque** localement est injecté, tout le reste
  est gardé, et toute clé présente des deux côtés avec des valeurs différentes est un conflit —
  l'attribution est impossible sans base, et la refuser vaut mieux que la deviner.
- Le résultat rendu distingue trois choses : le texte fusionné, la liste des changements
  (`types.Change`, déjà fait pour ça), la liste des conflits.

**Vérification** : `uvx pytest scripts/tests/test_fusion.py -q` — aller-retour de l'émetteur, les
quatre lignes du tableau, le cas des gabarits, le mode sans base.

### 5. La commande `reseed`

`scripts/listdir/commands/reseed.py` — un `register()` et un appel de la bibliothèque, comme
`init.py` le documente.

```bash
list-dir reseed <liste> [--def <nom> | --from <chemin>] [--force] [--dry-run]
```

- Semence visée : `--def`/`--from`, sinon `[origin].def` de la liste ; aucune des deux → échec
  nommé. Les deux options s'excluent (`add_mutually_exclusive_group`, comme `init.py:39`).
  Discordance de nom : même refus code 2 qu'à l'étape 2.
- `frozen = true` sans `--force` → échec nommé. **`--force` ne fait que dégeler** : un conflit
  fait sortir non nul en nommant chaque clé, `--force` compris, et rien n'est écrit. Le brief ne
  lui confie pas d'arbitrage, et « aucune résolution automatique » est un signal de dérive.
- Écriture, dans cet ordre : `.list/backup/` (contrat + gabarits en vigueur, **remplacé** à chaque
  reseed — une seule marche arrière, l'historique est le travail de git), puis le contrat fusionné
  et les gabarits, puis `.list/semence/` rafraîchi avec la semence courante.
- **Aucune divergence locale → la semence est recopiée verbatim**, commentaires compris.
  Divergence → contrat reconstruit par l'émetteur, et le rapport **dit** que les commentaires
  locaux sont dans `.list/backup/`.
- `--dry-run` rapporte sans écrire, conflits compris.

**Vérification** : `uvx pytest scripts/tests/test_reseed.py -q` — recopie verbatim, conflit qui
n'écrit rien (avec et sans `--force`), `frozen` refusé puis dégelé, contenu du backup, `--dry-run`
qui ne touche à rien.

### 6. Le mode adoption

- `reseed <liste> --def <nom>` sur une liste **sans** `[origin]` : fusion sans base (étape 4),
  puis écriture de l'`[origin]` de la semence **verbatim** — c'est par là que la liste reçoit son
  `version`, et le critère « l'estampiller à la version de la semence » est servi explicitement,
  pas par déduction.
- **Cas particulier, celui de toutes les listes antérieures** : si le contrat local égale la
  semence une fois `[origin]` mis de côté, `reseed` recopie la semence verbatim — commentaires
  préservés, résultat octet pour octet égal à la semence.
- `.list/semence/` est créé au passage : la liste devient comparable hors ligne.

**Vérification** : `uvx pytest scripts/tests/test_reseed.py -q` — adoption d'une liste identique
à `[origin]` près (verbatim), d'une liste divergente (injection), d'une liste en conflit (refus).

### 7. Documentation

Chemins relatifs à la racine du dépôt.

- `skills/list-dir/references/contrat-liste.md` : section « Provenance et péremption » (la table
  `[origin]`, les trois drapeaux, `.list/semence/`, les avertissements, `reseed` et sa fusion) ;
  nuancer « La définition n'est autorité que le temps de l'`init` » (ligne 103) — elle le reste,
  mais la filiation est désormais **dite** et le rattrapage est un geste explicite ; ajouter
  `.list/semence/` et `.list/backup/` à l'arborescence de tête ; corriger « une définition est un
  répertoire dont le contenu **est** le futur `.list/` » (ligne 41), qui cesse d'être exact — le
  `.list/` d'une liste semée porte en plus sa semence et sa sauvegarde.
- `skills/list-dir/SKILL.md` : douze commandes → treize (lignes 5 et 42), `reseed` dans le
  tableau, un paragraphe sur la péremption.
- `skills/implementation-tracker/references/dette.md` : « une fois amorcés, ils sont détachés » se
  complète du geste de rattrapage.

**Vérification** (depuis la racine du dépôt) :

```bash
grep -rn "douze" skills/list-dir/SKILL.md && echo "RESTE À CORRIGER"
grep -c "semence/" skills/list-dir/references/contrat-liste.md   # > 0
grep -n "contenu \*\*est\*\* le futur" skills/list-dir/references/contrat-liste.md
```

### 8. Adoption dans ce dépôt

- `[origin] def = "<nom>" / version = 1` dans les trois définitions de
  `skills/implementation-tracker/list-dir/*/contract.toml`.
- `list-dir reseed .claude/implementation/todo/<liste> --def <nom>` sur les trois registres : ils
  sont aujourd'hui identiques à leurs semences (`diff -r` muet), l'adoption est donc verbatim et
  sans conflit.

**Vérification** (depuis la racine du dépôt) — le code de retour ET stderr sont inspectés, parce
que c'est là que vont les avertissements :

```bash
T=.claude/implementation/todo
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  diff -r skills/implementation-tracker/list-dir/$l $T/$l/.list/semence || echo "ÉCART semence $l"
  diff skills/implementation-tracker/list-dir/$l/contract.toml $T/$l/.list/contract.toml \
    || echo "ÉCART contrat $l"
  ERR=$(list-dir validate "$T/$l" 2>&1 >/dev/null); CODE=$?
  [ $CODE -eq 0 ] && [ -z "$ERR" ] || echo "ÉCHEC $l : code $CODE, stderr « $ERR »"
done
```

## Vérification d'ensemble

```bash
cd skills/list-dir
uvx pytest scripts/tests -q     # 346 tests aujourd'hui, aucun ne doit tomber
uvx ruff check scripts && uvx ruff format --check scripts
uvx pyright
```

## Ce que ce chantier ne fait pas

Aucun re-semis automatique ; aucune commande autre que `reseed` et l'avertissement de `validate`
ne résout une définition ; `reseed` ne touche pas aux éléments `*.md` — les remettre en ligne
reste le travail de `migrate`, à lancer après ; `debt-review` et le reste du pipeline ne sont pas
retouchés.
