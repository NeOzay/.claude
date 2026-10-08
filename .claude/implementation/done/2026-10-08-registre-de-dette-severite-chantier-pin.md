+++
gabarit = "suivi"
slug = "registre-de-dette-severite-chantier-pin"
titre = "Faire évoluer le registre de dette : sévérité, chantier, référence, pin, découpage de `source`"
branche = "registre-de-dette-severite-chantier-pin"
base = "master"
statut = "terminé"
session = 3
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-08-registre-de-dette-severite-chantier-pin.plan.md"
brief = ".claude/implementation/done/2026-10-08-registre-de-dette-severite-chantier-pin.brief.md"
audit = ".claude/implementation/done/2026-10-08-registre-de-dette-severite-chantier-pin.audit.md"
road-map = "registre-de-dette-severite-chantier-pin"
skills = ["skill-convention"]
"créé" = 2026-10-07
maj = 2026-10-08
+++

## Objectif et périmètre

**Symptôme** : on ne peut pas trier les entrées du registre par chantier, ni repérer rapidement les
dettes qui valent la peine d'être traitées ; rien ne permet de retrouver facilement certaines
dettes.

**But** : trier le registre par date et par chantier, classer les dettes par sévérité pour voir
celles qui valent d'être traitées, et épingler (`pin`) celles qu'on veut retrouver sans effort.

**Critères de réussite** :

- `list-dir contract "$T/technical-debt" --values severite` rend `inconnue`, `note`,
  `avertissement`, `majeur`, `critique`, dans cet ordre.
- `list-dir validate "$T/<liste>" --filled` passe sur les trois listes, sans note sur l'ancien
  Marqueur, et signale `source` comme `deprecated` tant qu'une entrée de `technical-debt` le porte.
- `list-dir list "$T/technical-debt" --sort=-severite` classe les entrées de la plus grave à la
  moins grave ; `--sort chantier` les groupe par chantier ; `--sort date` les date.
- `list-dir list "$T/technical-debt" --where pin=true` retrouve les entrées épinglées ; une entrée
  neuve porte `pin = false`.
- Chaque entrée de `technical-debt` porte `severite` (`inconnue` par défaut), et `chantier` valant un
  slug de `done/` ou « Hors chantier » ; son `source` garde son texte d'origine.
- `list-dir contract` de `-solde` et `-ecarte` déclare `source`, `severite`, `chantier`, `pin` et
  `reference` facultatifs.
- L'agent de migration existe sous `agents/`, et les `chantier` et `reference` de `technical-debt`
  ont été remplis par lui.
- Le patron `review.toml` porte `severite` et pas `pin` ; `debt-review` documente qu'elle peut
  remplacer `inconnue` et qu'elle ignore `pin`.

**Hors-périmètre** :

- L'adaptation de Neovim aux Marqueurs typés et au type `bool` : son propre Chantier.
- Le traitement des entrées de `technical-debt-solde` et de `technical-debt-ecarte`.
- Toute relecture de fond des entrées de `technical-debt`.
- Tout changement des règles de sortie de `/debt-review`, hors le remplacement de `inconnue` et
  l'ignorance de `pin`.

**Signaux de dérive** :

- Une entrée de `technical-debt` dont le contenu change au-delà des champs migrés.
- Un `chantier` rempli qui n'est ni un slug de `done/` ni « Hors chantier ».
- `pin` qui protège une entrée dans `/debt-review`.
- Une modification du plugin Neovim.

## Étapes

- [x] 1. `fill` : code et tests — `skills/list-dir/scripts/listdir/commands/fill.py`, `skills/list-dir/scripts/listdir/store.py`, `skills/gabarit/scripts/gabarit/prefill.py`, `skills/list-dir/scripts/tests/test_fill.py`, `skills/list-dir/scripts/tests/test_entree_cli.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` puis `uvx ruff check skills/list-dir && uvx ruff format --check skills/list-dir && uvx --with pytest basedpyright skills/list-dir`
- [x] 2. `fill` : documentation — `skills/list-dir/SKILL.md`, `skills/list-dir/references/operations.md`, `skills/list-dir/references/extension.md` — vérif: `list-dir help` liste `fill` ; `uvx rumdl fmt --check skills/list-dir`
- [x] 3. Contrats des quatre définitions — `skills/implementation-tracker/list-dir/technical-debt/contract.toml`, `technical-debt-solde/contract.toml`, `technical-debt-ecarte/contract.toml`, `technical-debt/patrons/review.toml` — vérif: `list-dir contract --def technical-debt --values severite` rend `inconnue note avertissement majeur critique` dans cet ordre ; même sortie avec `--patron review` ; `list-dir contract --def technical-debt-solde` charge sans erreur
- [x] 4. Règles du registre — `skills/implementation-tracker/references/dette.md`, `skills/implementation-tracker/references/cloture.md` — vérif: `uvx rumdl fmt --check skills/implementation-tracker` et `~/.claude/.venv/bin/python scripts/check_pipeline.py`
- [x] 5. `debt-review` — `skills/debt-review/SKILL.md`, `skills/debt-review/references/gabarit-rapport.md`, `skills/debt-review/references/exemple-revue.md`, `skills/implementation-tracker/list-dir/technical-debt/patrons/review.md` — vérif: `rg -n "pin" skills/debt-review` ne montre que « ignoré » ; `uvx rumdl fmt --check skills/debt-review`
- [x] 6. Agent de migration — `agents/migrateur-de-liste.md` — vérif: `~/.claude/.venv/bin/python scripts/check_pipeline.py` (contrôle 4) ; `grep -c "contrat.md" agents/migrateur-de-liste.md` rend 0
- [x] 7. Note de migration du registre — `skills/implementation-tracker/list-dir/technical-debt/migrations/3.md`, `skills/implementation-tracker/list-dir/technical-debt-solde/migrations/2.md`, `skills/implementation-tracker/list-dir/technical-debt-ecarte/migrations/2.md` — vérif: `uvx rumdl fmt --check skills/implementation-tracker` ; `check_pipeline.py` (renvois résolus) ; `list-dir defs` liste toujours les trois définitions
- [x] 8. `list-dir` : l'avertissement de péremption nomme les notes de migration — `skills/list-dir/scripts/listdir/contract.py`, `skills/list-dir/scripts/listdir/provenance.py`, `skills/list-dir/scripts/tests/test_provenance.py`, `skills/list-dir/references/definitions.md`, `skills/list-dir/references/provenance.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` puis `uvx ruff check skills/list-dir` ; `list-dir validate "$T/technical-debt"` nomme `technical-debt/migrations/3.md` ; `uvx rumdl fmt --check skills/list-dir`
- [x] 9. Migrer `-solde` et `-ecarte` — `.claude/implementation/todo/technical-debt-solde/`, `.claude/implementation/todo/technical-debt-ecarte/` — vérif: `list-dir validate "$T/<liste>" --filled` sort 0 pour chacune ; `list-dir validate "$T/<liste>" 2>&1 >/dev/null | grep -c Marqueur` rend 0 ; `list-dir list … | wc -l` rend 44 et 5
- [x] 10. Migrer `technical-debt` : structure — `.claude/implementation/todo/technical-debt/`, `skills/implementation-tracker/list-dir/technical-debt/contract.toml` — vérif: `list-dir list "$T/technical-debt" --where severite=inconnue | wc -l` rend 90 ; `validate` avertit de `source` déprécié et ne cite plus l'ancien Marqueur de `reviewed`
- [x] 11. Migrer `technical-debt` : `chantier` et `reference` — `.claude/implementation/todo/technical-debt/` — vérif: la garde de `technical-debt/migrations/3.md` sort 0 ; `list-dir validate "$T/technical-debt" --filled` sort 0, ou nomme les entrées laissées au marqueur
- [x] 12. Vérification bout en bout — aucune modification — vérif: `list-dir list "$T/technical-debt" --sort=-severite`, `--sort chantier`, `--sort date`, `--where pin=true` cohérents ; `list-dir validate --filled` sort 0 sur les trois listes ; `list-dir derive` du registre dans un répertoire temporaire puis `validate` ; `uvx ruff check . && uvx ruff format --check . && uvx --with pytest basedpyright && uvx rumdl fmt --check .` ; `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/` ; `check_pipeline.py`

## État courant

**Prochaine action** : Clôture en cours — aplatissement par `commit-chantier cloture`.

**Vérification** : `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/`
puis `uvx ruff check . && uvx --with pytest basedpyright` et `~/.claude/.venv/bin/python scripts/check_pipeline.py`.

**Dernier audit** : cfad0f7 — RÉSERVES — 2026-10-08

**Notes** : `$T` vaut `.claude/implementation/todo`. Commits : jamais sans l'accord explicite de
l'utilisateur ; vider puis contrôler l'index juste avant chaque commit.

## Passation

**Écrite** : session 1, après AE0.

**En cours** : rien. L'étape 1 n'est pas commencée, l'arbre est propre.

**À savoir** :

- Lancer `/model opus` avant de reprendre : le Plan l'a choisi.
- `text = "…"` préremplit à `new` **et** à `migrate`. `severite` n'ayant aucune valeur par défaut,
  `migrate` la pose à `<À REMPLIR>`, et `fill … severite inconnue` l'écrit ensuite.
- `list-dir list <liste> --sort <champ>` imprime `id champ` : c'est ainsi que l'agent lit toutes les
  `source` d'un coup. Les champs restés au marqueur se rangent en fin de tri, dans les deux sens.
- `check_pipeline.py`, contrôle 4 : un fichier de `agents/` ne doit pas contenir la chaîne
  `contrat.md`. Les règles de l'agent s'y écrivent en dur.
- Le seul slug cité en `source` qui n'est pas dans `done/` est
  `lexique-local-tronque-par-le-hook-session`, un audit « hors chantier » : `chantier = "Hors
  chantier"`.
- La semence `brief` refuse toute section qu'elle ne déclare pas : l'annexe sur l'agent est dans les
  puces du brief, pas dans un fichier ni dans une section.
- Tests : `~/.claude/.venv/bin/python -m pytest` ; linters et formateurs par `uvx` (voir
  `OUTILLAGE.md`). Le répertoire courant du shell persiste d'un appel à l'autre : rester à la racine.

## Journal de décisions

- **2026-10-07** — `chantier` s'écrit en slug sans préfixe daté, une seule graphie. *Pourquoi* :
  `--sort chantier` ne regroupe que si un Chantier n'a qu'une forme. *Rejeté* : le nom d'archive
  entier de `done/`.
- **2026-10-07** — `reference = "Non précisée"` est écrite par l'agent quand `source` ne donne ni
  `R<n>` ni lieu. *Pourquoi* : le brief exclut la relecture humaine des entrées, et `validate
  --filled` doit passer. *Rejeté* : laisser le champ au Marqueur.
- **2026-10-07** — `fill`, quatorzième commande générique de `list-dir`, pose une valeur sur les
  champs restés au Marqueur. *Pourquoi* : l'utilisateur veut une commande pour écrire `inconnue`, et
  l'agent écrit par elle, sans édition libre. *Rejeté* : un script propre à la dette.
- **2026-10-07** — `source` reste facultatif et non déprécié dans `-solde` et `-ecarte`. *Pourquoi* :
  49 entrées non traitées ; un `deprecated` ferait avertir `validate` sur chacune sans action qui le
  résolve. *Rejeté* : le déprécier comme dans `technical-debt`.
- **2026-10-07** — échelle de sévérité fixée par l'utilisateur : `note` observation sans coût
  démontré ; `avertissement` gêne ou risque identifié, contournable ; `majeur` coût récurrent ou
  défaillance silencieuse probable, perturbe le fonctionnement d'une fonction clé ; `critique` fait
  mentir un contrôle ou corrompt un résultat sans le dire, problème à traiter dans les prochains
  chantiers.
- **2026-10-07** — `gabarit.prefill.typed_value` est la seule conversion d'une chaîne en valeur de
  champ : `text`, `command` et `fill` la partagent. *Pourquoi* : deux conversions finiraient par
  accepter des formes différentes d'un même type. *Rejeté* : recopier la conversion dans `fill`.
- **2026-10-07** — `fill` exige `--id` (répétable) ou `--all`, exclusifs l'un de l'autre.
  *Pourquoi* : demandé par l'utilisateur ; un `--id` oublié ne doit pas remplir toute la liste avec
  une valeur pensée pour un seul élément. *Rejeté* : « sans `--id`, tous », livré à l'Étape 1.
- **2026-10-07** — `reference` d'une entrée migrée prend une forme fermée : les `R<n>` du Chantier
  retenu, sinon le premier lieu d'une liste ordonnée (`Étape <n>`, `session <n>`, `journal du
  Suivi`, `relecture du Plan, Q<n>`, `Hors-périmètre du Brief`, `Clôture`), sinon « Non précisée ».
  La garde vérifie cette forme. *Pourquoi* : « le lieu cité » laissé libre ferait paraphraser un petit
  modèle, et rien ne le verrait. *Rejeté* : recopier le lieu tel que `source` l'écrit.
- **2026-10-07** — La procédure de migration est une note de la définition qu'elle migre,
  `<définition>/migrations/<version>.md`, que l'avertissement de péremption de `list-dir` nomme ;
  elle reste en place une fois la migration faite. `dette.md` n'y renvoie pas. *Pourquoi* : choix de
  l'utilisateur ; la note suit le contrat qu'elle concerne, et le lecteur d'un autre projet la
  trouve au moment où `validate` lui dit que son registre est périmé. `init` et `reseed` ne copient
  que `contract.toml` et `patrons/`. *Rejeté* : `references/migration-dette.md` renvoyé par
  `dette.md` ; un répertoire de migrations propre au skill ou à la racine de la config. Ajoute
  l'Étape 8 au Plan ; les suivantes sont renumérotées.
- **2026-10-08** — `[fields.source]` de `technical-debt` v3 garde `required = false` à côté de
  `deprecated`. *Pourquoi* : `reseed` garde une clé que la semence retire, et le contrat fusionné,
  différent de la semence, était réémis au lieu d'être recopié. *Rejeté* : changer la fusion de
  `reseed`, hors du périmètre.
- **2026-10-08** — Réserve R1 de l'audit de clôture traitée : `migrations/3.md` dit que `migrate`
  pose aussi au Marqueur les champs et sections facultatifs absents, et réordonne les sections.
  *Pourquoi* : choix de l'utilisateur ; la garde ne voit pas ces lignes. *Rejeté* : clore avec.
- **2026-10-08** — Clôture avec les réserves R9 et R11 du second audit. Versés au registre :
  `list-dir-list-trace-brokenpipe-sous-head`, `reseed-garde-une-cle-retiree-par-la-definition`,
  `validate-toml-invalide-masque-les-autres-manquements`, `migrateur-ne-selectionne-que-a-remplir`,
  `migrateur-se-dit-sans-outil-d-ecriture`, `values-de-severite-recopiees-sans-controle`,
  `note-de-migration-tait-la-reecriture-de-reviewed`. Les échecs de `ruff` et `basedpyright` sur la
  Base y étaient déjà (`ruff-echoue-sur-les-tests-de-list-dir`, `basedpyright-treize-erreurs-non-tenues`).
