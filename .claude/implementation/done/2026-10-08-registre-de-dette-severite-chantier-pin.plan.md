# Plan — registre de dette : sévérité, chantier, référence, pin

Brief : `.claude/implementation/registre-de-dette-severite-chantier-pin.brief.md` (validé).

## Contexte

Le registre de dette ne se trie ni par chantier ni par gravité : `source` est un texte libre
(« chantier `x`, audit R4 », « Identifié par `y`, R3 du rapport… »). Le Chantier donne au contrat des
trois listes quatre champs (`severite`, `chantier`, `reference`, `pin`), dépréce `source`, migre les
90 entrées de `technical-debt`, et fournit l'outillage pour migrer d'autres registres : une commande
générique `list-dir fill` et un agent de migration.

## Ce que l'exploration a établi

- Le préremplissage `text` (`gabarit/references/format.md`, « Préremplir ») se pose à `new` **et** à
  `migrate`, et convertit en `bool` (`text = "false"`). C'est ainsi que `pin` vaut `false` par défaut.
- Pas de valeur par défaut pour `severite` (décision de l'utilisateur) : `migrate` la pose donc à
  `<À REMPLIR>` ; une commande l'écrit ensuite en `inconnue`. **Aucune commande existante ne pose une
  valeur** : `migrate` ne juge pas, et il n'y a pas de `set`. D'où `fill`.
- `list-dir list <liste> --sort <champ>` imprime `id champ` : l'agent lit toutes les `source` en un
  appel. `--sort=-severite` suit l'ordre des `values` ; `inconnue` en tête des `values` la range donc
  en dernier. Les champs restés au marqueur vont en fin de tri, dans les deux sens.
- `deprecated` refuse `required = true`, `text` et `command` ; `validate` avertit sur stderr pour
  chaque entrée qui porte encore le champ.
- Les `source` actuelles ont quelques formes régulières (`chantier \`<slug>\`, …R<n>`, `Identifié par
  \`<slug>\`, R<n>…`, `hors chantier…`, `audit hors chantier de \`<slug>\`…`). Les slugs cités
  existent tous dans `done/`, sauf `lexique-local-tronque…` (un audit « hors chantier »).
- `check_pipeline.py`, contrôle 4 : un fichier de `agents/` ne doit pas contenir la chaîne
  `contrat.md`. Un agent ne suit pas de renvoi : ses règles s'y écrivent en dur
  (`skill-convention`, `references/prose.md`, « Un sous-agent recopie ses règles »).
- Neovim : `~/.config/nvim/plugins/listdir/lua/listdir/contract.lua` lit `contract.toml` au motif ;
  un type inconnu est gardé comme chaîne, une clé inconnue est ignorée. Aucune modification requise
  (hors-périmètre du brief).

## Modèle

**Opus.** Chantier surtout de prose et de contrats (`dette.md`, `debt-review`, agent), 11 Étapes,
et aucune incertitude du brief n'est tranchée sans jugement : au moindre doute, Opus.

## Décisions de conception

1. **`fill`, quatorzième commande générique de `list-dir`** — `list-dir fill <liste> <champ> <valeur>
   [--id <id>]… [--dry-run]`. Pose `<valeur>` sur `<champ>` des seuls éléments dont le champ est au
   marqueur (tous, ou ceux de `--id`). La valeur passe le contrôle du type du champ (`enum` hors
   `values`, date non ISO, `bool` autre que `true`/`false` : refusés, rien n'est écrit). Une valeur déjà
   écrite n'est jamais touchée : sans `--id`, l'élément est sauté ; avec `--id`, l'appel échoue en le
   nommant. Écriture par reprojection (`Item.with_fields`, `write`), comme `migrate` : le diff ne
   montre que la ligne du champ. Rejouable : rien à faire → aucun fichier touché. Justification : c'est
   la commande que l'utilisateur demande pour `inconnue`, et elle rend l'agent déterministe — il écrit
   par `fill` seulement, jamais par édition libre.
2. **Contrat de `technical-debt` (v2 → v3)** : `severite` (`enum`, `values` = `inconnue`, `note`,
   `avertissement`, `majeur`, `critique`, requis, sans préremplissage), `chantier` (`text`, requis),
   `reference` (`text`, requis), `pin` (`bool`, requis, `text = "false"`), `source` déprécié
   (`deprecated = "Remplacé par chantier et reference ; ne plus l'écrire."`, ni requis ni préremplissage).
   Ordre : `date`, `severite`, `chantier`, `reference`, `pin`, `source`, `reviewed`, `category`.
3. **`technical-debt-solde` et `-ecarte` (v1 → v2)** : les mêmes champs, tous facultatifs et sans
   préremplissage (`pin` compris) ; `source` reste un champ facultatif **non déprécié** (49 entrées non
   traitées : un `deprecated` ferait avertir `validate` sur chacune, sans action qui le résolve).
4. **Patron `review.toml` (v1 → v2)** : un champ `severite` (`enum`, mêmes `values`, requis,
   `from = "severite"`). La fiche reprend donc la sévérité de l'entrée telle quelle ; la revue
   l'ajuste, et remplace `inconnue`. Pas de `pin` : la revue l'ignore.
5. **Agent `agents/migrateur-de-liste.md`**, global, `model: haiku`, `tools: Read, Grep, Bash` — **pas
   d'`Edit`** : il écrit par `fill`. Reçoit des chemins absolus (racine, liste) et une consigne ; lit
   les entrées par `list-dir list … --sort <champ>` et `show` ; écrit par `fill --id` ; ne devine rien :
   ce qu'il ne peut pas établir reste au marqueur et se rapporte (une ligne par entrée : `id`, champ,
   valeur posée ou « laissé », motif). Le contrôle de sa sortie est fait par l'appelant (point 6).
6. **Consigne et garde propres à la dette** : `skills/implementation-tracker/references/migration-dette.md`
   (nouveau) porte la procédure rejouable dans tout projet (`reseed` → `migrate` → `fill severite
   inconnue` → agent → garde → `validate --filled`), le texte de consigne donné à l'agent (formes de
   `source`, ce qu'est une `reference` : un `R<n>` ou le lieu cité, « Hors chantier » quand `source` ne
   nomme aucun Chantier ; « Non précisée » quand `source` ne dit ni `R<n>` ni lieu), et la garde : chaque
   `chantier` est un slug de `done/` — nom d'archive **sans** le préfixe daté, jamais le nom entier —
   ou « Hors chantier », vérifié par commande, et le diff n'a touché que les champs visés. La consigne
   donne à l'agent le contrat avant et après.
7. **Échelle de sévérité (validée par l'utilisateur)**, écrite dans `dette.md` : `critique` — fait mentir
   un contrôle ou corrompt un résultat sans le dire, problème à traiter dans les prochains chantiers ;
   `majeur` — coût récurrent ou défaillance silencieuse probable, perturbe le fonctionnement d'une
   fonction clé ; `avertissement` — gêne ou risque identifié, contournable ; `note` — observation sans
   coût démontré ; `inconnue` — jamais jugée : valeur de migration, que `/debt-review` remplace, jamais une
   valeur de repli pour qui crée une dette.
8. **Limite assumée** : les `values` de `severite` sont recopiées dans cinq fichiers (quatre contrats et
   le patron), comme `category` l'est déjà ; aucun contrôle ne les rapproche. À reporter au registre à
   la clôture si l'audit le confirme.

## Étapes

1. **`fill` : code et tests** — `skills/list-dir/scripts/listdir/commands/fill.py`,
   `skills/list-dir/scripts/listdir/store.py` (méthode `fill`), `skills/list-dir/scripts/tests/test_fill.py`
   (tests sur la liste-jouet de `jouet.py`), et `skills/list-dir/scripts/tests/test_entree_cli.py`
   (l'assertion « Commandes génériques (13) » passe à 14) — vérif: `~/.claude/.venv/bin/python -m pytest
   skills/list-dir/scripts/tests/` puis `uvx ruff check skills/list-dir && uvx ruff format --check
   skills/list-dir && uvx --with pytest basedpyright skills/list-dir`.
2. **`fill` : documentation** — `skills/list-dir/SKILL.md` (« quatorze commandes », description),
   `skills/list-dir/references/operations.md` (section « Remplir ce que `migrate` laisse au Marqueur »),
   `skills/list-dir/references/extension.md` si la liste des commandes y figure — vérif: `list-dir help`
   liste `fill` ; `uvx rumdl fmt --check skills/list-dir`.
3. **Contrats des quatre définitions** — `skills/implementation-tracker/list-dir/technical-debt/contract.toml`,
   `technical-debt-solde/contract.toml`, `technical-debt-ecarte/contract.toml`,
   `technical-debt/patrons/review.toml` — vérif: `list-dir contract --def technical-debt --values severite`
   rend `inconnue note avertissement majeur critique` dans cet ordre ; même sortie pour
   `--def technical-debt --patron review --values severite` ; `list-dir contract --def technical-debt-solde`
   charge sans erreur.
4. **Règles du registre** — `skills/implementation-tracker/references/dette.md` (champs, échelle de
   sévérité, `source` déprécié, `pin` : retrouver une dette, sans autre effet), `references/cloture.md`
   point 2 (celui qui crée une dette renseigne `severite`, `chantier`, `reference` ; `inconnue` n'est pas
   un repli) — vérif: `uvx rumdl fmt --check skills/implementation-tracker` et
   `~/.claude/.venv/bin/python scripts/check_pipeline.py`.
5. **`debt-review`** — `skills/debt-review/SKILL.md` (Phase 2 : ajuster `severite` et remplacer
   `inconnue` ; Phase 5 : écrire `severite` dans l'entrée quand elle diffère ; `pin` ignoré),
   `skills/debt-review/references/gabarit-rapport.md`, `exemple-revue.md`,
   `skills/implementation-tracker/list-dir/technical-debt/patrons/review.md` — vérif: `rg -n "pin"
   skills/debt-review` ne montre que « ignoré » ; `uvx rumdl fmt --check skills/debt-review`.
6. **Agent de migration** — `agents/migrateur-de-liste.md` (règles recopiées en dur, aucune mention de
   `contrat.md`, outils sans `Edit`) — vérif: `~/.claude/.venv/bin/python scripts/check_pipeline.py`
   (contrôle 4) ; `grep -c "contrat.md" agents/migrateur-de-liste.md` rend 0.
7. **Consigne de migration du registre** — `skills/implementation-tracker/references/migration-dette.md`
   (nouveau), renvoi depuis `dette.md` — vérif: `uvx rumdl fmt --check skills/implementation-tracker` ;
   `check_pipeline.py` (renvois résolus).
8. **Migrer `-solde` et `-ecarte`** — `.claude/implementation/todo/technical-debt-solde/`, `…-ecarte/`
   (`reseed`, puis `migrate --dry-run`, puis `migrate`) — vérif: `list-dir validate "$T/<liste>"
   --filled` sort 0 pour chacune des deux listes ; sa sortie stderr ne contient plus de note sur
   l'ancien Marqueur (`list-dir validate "$T/<liste>" 2>&1 >/dev/null | grep -c Marqueur` rend 0) ;
   `list-dir list … | wc -l` rend 44 et 5.
9. **Migrer `technical-debt` : structure** — `.claude/implementation/todo/technical-debt/` (`reseed`,
   `migrate --dry-run`, `migrate`, puis `list-dir fill … severite inconnue`) — vérif: `list-dir list
   "$T/technical-debt" --where severite=inconnue | wc -l` rend 90 ; `validate` avertit de `source`
   déprécié et ne cite plus l'ancien Marqueur de `reviewed`.
10. **Migrer `technical-debt` : `chantier` et `reference`** — lancer l'agent par lots d'environ 30
    entrées, avec la consigne de `migration-dette.md` ; contrôler sa sortie par la garde — vérif: la
    garde de `migration-dette.md` sort 0 ; `list-dir validate "$T/technical-debt" --filled` sort 0, ou
    nomme les entrées laissées au marqueur, que l'utilisateur tranche.
11. **Vérification bout en bout** — aucune modification — vérif: `list-dir list "$T/technical-debt"
    --sort=-severite`, `--sort chantier`, `--sort date`, `--where pin=true` rendent chacun un résultat
    cohérent ; `list-dir validate --filled` sort 0 sur les trois listes ; dans une copie temporaire, `list-dir new` rend `pin = false` et `severite` au marqueur ;
    `list-dir derive` du registre dans un répertoire temporaire puis `validate` de la dérivée sort 0 ;
    `uvx ruff check . && uvx ruff format --check . && uvx --with pytest basedpyright && uvx rumdl fmt
    --check .` ; `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/` ;
    `check_pipeline.py`.

## Critères de réussite du brief → Étapes

| Critère | Étapes |
|---|---|
| `contract --values severite` dans l'ordre voulu | 3 |
| `validate --filled` sur les trois listes, sans note de l'ancien Marqueur, `source` signalé déprécié | 8, 9, 10 |
| `--sort=-severite`, `--sort chantier`, `--sort date` | 9, 10, 11 |
| `--where pin=true`, `pin = false` à la création | 3, 9, 11 |
| `severite`, `chantier` renseignés ; `source` intact | 9, 10 |
| `-solde` et `-ecarte` : champs facultatifs | 3, 8 |
| `review.toml` porte `severite`, pas `pin` ; `debt-review` documentée | 3, 5 |
| agent de migration sous `agents/`, `chantier` et `reference` remplis par lui | 6, 10 |

## Incertitudes du brief → Étapes

- Conception de l'agent (nom, modèle, outils, consigne, garde, rapport, reprise) : décisions 5 et 6,
  Étapes 6 et 7. La reprise sur lot interrompu tient à `fill` : il ne touche que les champs encore au
  marqueur, donc rejouer un lot ne réécrit rien.
- `migrate` de `-solde` et `-ecarte` : il y pose cinq champs facultatifs au marqueur (`<OPTIONNEL…>`),
  entrée par entrée ; Étape 8, avec un `--dry-run` d'abord. `pin` n'y est pas prérempli.
- Modèle de l'agent : Haiku, sous la garde de l'Étape 10 (slug de `done/` ou « Hors chantier »).
- `source` muet : `chantier = "Hors chantier"` s'il ne nomme aucun Chantier ; `reference = "Non
  précisée"` s'il ne nomme ni `R<n>` ni lieu, repli écrit par l'agent et listé dans son rapport.

## Hors-périmètre et signaux de dérive

Rien dans ces Étapes ne touche Neovim, ni le contenu des entrées de `technical-debt` hors champs
migrés, ni les règles de sortie de `debt-review`. Un `chantier` hors `done/` ou « Hors chantier » ou un
`pin` qui protège une entrée arrête l'implémentation.

## Relecture par `plan-reviewer` — verdict RÉSERVES

Le plan sert les huit critères, respecte le Hors-périmètre et ne déclenche aucun Signal de dérive.
Trois défauts de rédaction ont été corrigés sans arbitrage : un test existant
(`test_entree_cli.py`, « Commandes génériques (13) ») qui cassait dès l'Étape 1, une vérification
trop faible à l'Étape 8 (ni `--filled`, ni contrôle de la note sur l'ancien Marqueur) et à l'Étape 11,
et une citation fausse (le brief ne « demande » pas de commande : c'est une réponse de l'utilisateur
au cadrage, non reportée au brief).

**Tranché par l'utilisateur après la relecture :** `chantier` en slug sans préfixe daté, une seule
graphie ; `reference = "Non précisée"` écrite par l'agent quand `source` ne la donne pas, sans relecture
humaine ; `fill` comme quatorzième commande générique de `list-dir` ; échelle de sévérité (décision 7),
avec ses ajouts sur `majeur` et `critique`. `source` non déprécié dans `-solde` et `-ecarte` l'était
déjà. La consigne de l'agent porte le contrat avant et après ; l'Étape 4 n'y recopie pas les champs dans
`dette.md`, qui le proscrit : elle n'écrit que l'échelle de sévérité et le sens de `pin`.
