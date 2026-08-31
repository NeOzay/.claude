# Préremplissage des champs et sections d'un `contract.toml` — `text` et `command`

## Context

Aujourd'hui, tout champ ou section non fourni à la création d'un élément reçoit un marqueur
(`<À REMPLIR>` / `<OPTIONNEL>`) qu'il faut remplir à la main — y compris quand la valeur est
mécaniquement connue. Le cas porteur : un champ `date` qui devrait valoir la date du jour.

Le chantier ajoute deux clés optionnelles aux `[fields.*]` et `[sections.*]` d'un
`contract.toml` :

- `text = "…"` — texte littéral posé à la place du marqueur ;
- `command = "…"` — commande Bash dont la sortie est posée à la place du marqueur.

Elles s'appliquent **partout où un champ ou une section est posé pour la première fois** :
`new`, `migrate` (champ absent) et `derive` (champ sans `from`). Une commande qui échoue fait
échouer l'opération entière, sans rien écrire, en nommant la commande incriminée.

Brief : `.claude/implementation/2026-08-31-champs-preremplis.brief.md`.

## État des lieux

- `Field.marker` / `Section.marker` (`skills/list-dir/scripts/listdir/types.py:113`, `:131`) sont
  des propriétés pures : `PLACEHOLDER` si `required`, `OPTIONAL` sinon.
- Trois sites posent ce marqueur, dans `skills/list-dir/scripts/listdir/store.py` :
  `create` (`:229-230`), `_realign` — appelé par `migrate` (`:303`, `:331`), `_project` — appelé
  par `derive` (`:512`).
- `parse_contract` (`skills/list-dir/scripts/listdir/contract.py`) valide `type`, `values`,
  `description`, `required`, `from`, et **ignore silencieusement** toute autre clé.
- `gitcmd.py` est aujourd'hui le seul appel de processus externe du paquet.

## Approche

### Frontière marqueur / valeur exécutée

`Field.marker` et `Section.marker` restent des propriétés pures : une valeur issue d'une commande
peut échouer, et une propriété ne rend pas de `Result`. Le calcul faillible vit dans un **nouveau
module `skills/list-dir/scripts/listdir/prefill.py`**, sur le modèle de `gitcmd.py` — « le seul
endroit du paquet qui lance un shell ». Il expose :

```python
@dataclass(frozen=True)
class PrefillContext:      # construit UNE fois par opération, pas par champ
    list_dir: Path         # cwd des commandes, et LISTDIR_LIST
    contract_name: str     # LISTDIR_CONTRACT
    root: Path | None      # LISTDIR_ROOT — racine git, None hors dépôt

def context(list_dir: Path, contract: Contract) -> PrefillContext: ...

def initial_field(f: Field, item_id: str, ctx: PrefillContext) -> Result[FieldValue]: ...
def initial_section(s: Section, item_id: str, ctx: PrefillContext) -> Result[str]: ...
```

Règle des deux fonctions, dans l'ordre : `text` → la valeur littérale ; `command` → sa sortie
standard, `.strip()`ée ; ni l'un ni l'autre → `decl.marker`, comme aujourd'hui.

Pour un champ, la valeur produite par `text` ou `command` est **confrontée au type déclaré** via
`check_value` (`contract.py`) ; un manquement fait échouer, en nommant le champ, la valeur et —
pour `command` — la commande.

### Exécution

`subprocess.run(["bash", "-c", cmd], cwd=ctx.list_dir, capture_output=True, text=True)`, dans un
environnement enrichi de :

| Variable | Valeur |
|---|---|
| `LISTDIR_ID` | l'identifiant de l'élément (nom de fichier sans extension) |
| `LISTDIR_NAME` | le nom du champ ou le titre de la section en cours |
| `LISTDIR_LIST` | chemin absolu du répertoire-liste |
| `LISTDIR_CONTRACT` | le `name` du contrat |
| `LISTDIR_ROOT` | racine git — **variable non définie** si la liste est hors dépôt |

`LISTDIR_ROOT` est résolu une seule fois par opération, via `gitcmd.git("rev-parse",
"--show-toplevel", cwd=…)` ; un échec vaut « hors dépôt » et ne fait rien échouer.

Échec fermé : code retour non nul, `bash` introuvable (`OSError`), ou sortie refusée par
`check_value` → `Result` en échec citant le fichier, le sujet et la commande. Aucun fichier n'est
écrit — les trois sites calculent déjà tout avant d'écrire.

### Validation au chargement du contrat

`parse_contract` accepte `text` et `command` sur `[fields.*]` et `[sections.*]`, et **refuse** :

- `text` et `command` déclarés ensemble sur un même champ ou une même section ;
- une valeur vide (`text = ""`, `command = ""`) — elle ne préremplit rien ;
- une valeur qui n'est pas une chaîne (via `_texte`, déjà en place) ;
- `text` ou `command` sur un champ de type `list` : la valeur produite est du texte, `check_value`
  la rejetterait systématiquement — mieux vaut le dire au chargement qu'à la création.

### Ce que le chantier ne fait pas

- `derive` construit les sections d'une fiche depuis le **gabarit `.md`**, pas depuis le contrat :
  il est lu par `template()` (`store.py:479`) et reçu en paramètre par `_project` (`store.py:502`),
  qui le pose tel quel (`:520`). `text`/`command` d'une *section* n'ont donc pas d'effet en
  `derive`. À documenter, pas à changer.
- Aucune substitution dans `text` (`{{id}}`, `$VAR`) : c'est du texte littéral. Le dynamique passe
  par `command`.
- Pas de `[fields.*.env]`, pas de modification des définitions de listes livrées (`defs`).

## Étapes

### 1. Déclarer `text` et `command` au contrat

`types.py` : ajouter `text: str | None = None` et `command: str | None = None` à `Field` et à
`Section`. `contract.py` : les lire dans les deux boucles de `parse_contract`, avec les quatre
refus ci-dessus. Tests dans `scripts/tests/test_contract.py` : acceptation, refus des deux
ensemble, refus du vide, refus sur `list`, refus d'un non-chaîne.

**Vérification** : `cd skills/list-dir/scripts && uvx pytest tests/test_contract.py -q`

### 2. Le module `prefill.py`

Créer `scripts/listdir/prefill.py` : `PrefillContext`, `context()`, `initial_field()`,
`initial_section()`, l'exécution `bash -c` et les messages d'échec. Aucun appelant encore. Tests
dans un nouveau `scripts/tests/test_prefill.py` : `text` littéral, `command` réussie et strippée,
code retour non nul, binaire absent, sortie refusée par `check_value`, marqueur en l'absence des
deux, présence et valeur de chaque `LISTDIR_*`, `LISTDIR_ROOT` absente hors dépôt.

**Vérification** : `cd skills/list-dir/scripts && uvx pytest tests/test_prefill.py -q`

### 3. Câbler les trois sites de pose

`store.py`, aux quatre endroits qui posent un marqueur : `create` (champs `:229`, sections `:230`),
`_realign` (champs `:303`, **et sections `:331`**, dont le libellé de `Change` en `:333`), et
`_project` (champs `:512`). Chacun appelle `initial_field` / `initial_section` au lieu de
`f.marker` / `section_marker`. `_realign` devient faillible — signature
`Result[tuple[Item, list[Change]]]` — et son unique appelant `migrate` (`:268`) propage l'échec
avant toute écriture ; le libellé du `Change` cite la valeur posée, comme il cite aujourd'hui le
marqueur. Tests dans
`test_store_ecriture.py` et `test_derive_merge.py` : `new` avec `command = "date +%F"`, `migrate`
qui pose la valeur sur un champ absent et ne touche pas un champ déjà rempli, `derive` sur un champ
sans `from`, et l'échec qui n'écrit rien.

**Vérification** : `cd skills/list-dir/scripts && uvx pytest tests -q`

### 4. Documenter

`references/contrat-liste.md` : les deux clés dans « Le contrat » (exemple `command = "date +%F"`
sur `[fields.date]`), le tableau des variables d'environnement, et dans « Les marqueurs » la règle
« un champ prérempli est une valeur ordinaire : `validate --filled` ne le réclame pas ». Y noter
les deux limites : pas d'effet sur les sections en `derive`, `list` refusé. Mettre `SKILL.md` à
jour si sa description du contrat le mentionne.

**Vérification** : aucun test ne lit `references/contrat-liste.md` — la suite ne prouve rien ici.
Jouer le bloc « Vérification de bout en bout » ci-dessous **en copiant les extraits de contrat
depuis la doc qui vient d'être écrite** : c'est le seul contrôle qui confronte la doc au moteur.
Plus relecture du diff.

### 5. Contrôles finaux

**Vérification** : `cd skills/list-dir && uvx ruff check scripts && cd scripts && uvx pytest tests -q`
(307 tests verts avant chantier, plus les nouveaux). `uvx ruff format --check` n'est pas un
critère : 4 fichiers y sont déjà signalés avant le chantier.

## Vérification de bout en bout

```bash
cd $(mktemp -d)
list-dir init ma-liste --name essai
cat >> ma-liste/.list/contract.toml <<'EOF'

[fields.date]
type = "date"
required = true
command = "date +%F"
description = "date du constat"

[sections."Origine"]
required = false
text = "Créé automatiquement."
description = ""
EOF
list-dir new ma-liste premier
cat ma-liste/premier.md          # date = date du jour, ## Origine porte le texte
list-dir validate ma-liste --filled   # le champ date n'est PAS réclamé

# échec fermé
sed -i 's|command = "date +%F"|command = "false"|' ma-liste/.list/contract.toml
list-dir new ma-liste second     # échoue, nomme la commande ; ma-liste/second.md n'existe pas
```
