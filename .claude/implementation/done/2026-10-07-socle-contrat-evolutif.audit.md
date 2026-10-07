---
slug: socle-contrat-evolutif
---

## 2026-10-07 — clôture — `22f3139`

**Verdict** : RÉSERVES

Diff audité : `git diff master...socle-contrat-evolutif`, 29 fichiers, +1953 −83, dix Étapes
cochées. Brief, Suivi et Plan (`.claude/plans/valiant-strolling-liskov.md`) lus. Le critère
« linters propres » est jugé dans sa forme amendée et datée au Suivi (« aucune erreur nouvelle par
rapport à la base »), qui fait foi.

### Vérifications exécutées

- `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ skills/gabarit/scripts/tests/ scripts/tests/`
  → **762 passed**, 0 échec (19,7 s).
- `uvx ruff check . --output-format concise`, sur les arbres extraits par `git archive` de `master`
  et de `HEAD` → 2 erreurs de chaque côté, les mêmes (`test_fusion.py:268` et `:295`, E501) ;
  aucune erreur nouvelle.
- `uvx ruff format --check .`, mêmes arbres → base « 99 files already formatted », branche
  « 103 files already formatted » ; aucun fichier à reformater.
- `uvx --with pytest basedpyright`, mêmes arbres → **133 erreurs de chaque côté** ; les listes
  normalisées (chemin, règle et message, sans numéro de ligne) sont identiques. Aucune erreur dans
  un fichier touché par le diff, sauf `listdir/provenance.py` (4) et `gabarit/items.py` (52), non
  modifiés et présents à l'identique sur la base.
- `git diff --stat master...socle-contrat-evolutif -- '*contract.toml'` → vide : aucun contrat
  touché.
- `uvx rumdl fmt --check .` (vérif de l'Étape 9) → **code 1**, sur la branche comme sur la base
  extraite : 23 corrections dans 5 fichiers, tous sous `.claude/implementation/` et hors du diff.
  Restreint aux 10 Markdown du diff : code 0 (3 constats non corrigibles, MD041/MD013 dans le Suivi
  et le Brief, propres au format des fichiers du pipeline). Aucune erreur nouvelle.
- Critères vérifiés à la main, dans une liste et une semence de bac à sable (scratchpad) déclarant
  `int`, `date`, `bool` (`text = "false"`), `list`, `enum`, `text`, un champ et une section
  `deprecated` :
  - `list-dir new` et `gabarit new --from` → `prio = "<À REMPLIR int>"`,
    `poids = "<OPTIONNEL int>"`, `date = "<À REMPLIR date>"`, `reviewed = "<OPTIONNEL date>"`,
    `tags = "<OPTIONNEL list>"`, `pin = false` (booléen nu), `sev = "<OPTIONNEL>"` ; ni le champ ni
    la section `deprecated` ne sont posés.
  - `list-dir validate` → code 0 ; `validate --filled` → code 1, ne réclame que `title`, `prio`,
    `date` et `Constat` (les requis). `gabarit check` / `check --filled` → mêmes verdicts.
  - Élément aux anciens Marqueurs et portant `source` et `## Ancien` dépréciés → `validate` code 0,
    une note par ancien Marqueur (avec la forme typée) et par élément déprécié (avec la consigne).
  - `<OPTIONNEL date>` sur un `int` → manquement nommé, code 1.
  - `list-dir migrate --dry-run` puis `migrate` → seuls les trois Marqueurs génériques convertis à
    statut égal, commentaire `# légende de prio` gardé, `source` et `## Ancien` gardés et jamais
    ajoutés ailleurs, valeurs écrites intactes ; second `--dry-run` : « déjà conforme ».
  - `list --sort prio` → `9` avant `10`, Marqueurs en fin ; `--sort=-prio` → `10`, `9`, Marqueurs
    en fin ; `--sort sev` → `note`, `majeur`, `critique`, `<OPTIONNEL>` ; `--where pin=true` → `b` ;
    `--sort=-` → code 1 nommé ; `--sort -prio` → code 2 d'argparse (documenté).
  - `gabarit contract --from` → stdout identique octet pour octet au `contract.toml`, règle des
    guillemets sur stderr ; `--values sev` → les valeurs seules, sans règle.
  - Refus de contrat : `deprecated` avec `required = true`, avec `text`, vide, non chaîne → code 1
    nommé. `bool` prérempli `"True"` ou `"0"` → refusé en le nommant ; `"true"` → `f = true`.
- `list-dir validate` sur les listes réelles `technical-debt`, `road-map`, `technical-debt-solde`
  → code 0 partout ; 39, 0 et 22 notes « ancien marqueur » sur stderr (voir R4).
- `gabarit check` sur le Suivi, le Brief et les 136 fichiers de `done/` → aucune note d'ancien
  Marqueur.

### Conformité à l'intention

- Critère « Marqueurs typés posés par `new`, tenus pour des Marqueurs, `--filled` ne réclame que
  les requis » : atteint, vérifié par `gabarit` et par `list-dir`.
- Critère « `bool` déclarable, `text = "false"` pose le booléen » : atteint, vérifié.
- Critère « `migrate` convertit l'ancien Marqueur sur `int`/`date` sans toucher de valeur écrite ;
  non migré, accepté par `validate` avec avertissement sur stderr, code inchangé » : atteint,
  vérifié (aussi sur `bool` et `list`, conformément à la décision du Suivi).
- Critère « `deprecated` : absent d'un fichier neuf, jamais ajouté par `migrate`, jamais réclamé ni
  non déclaré ; avertissement avec consigne, code inchangé » : atteint, vérifié pour un champ et une
  section, par `new`, `migrate`, `validate`, `check` (et `derive` par les tests).
- Critère « `list --sort` décroissant, `enum` dans l'ordre des `values`, `int` en nombre » :
  atteint, vérifié.
- Critère « `contract` et la référence de format disent que seuls `text`, `enum`, `slug` gardent
  leurs guillemets » : atteint — stderr de `gabarit contract` et `list-dir contract`,
  `gabarit/references/format.md` § Les marqueurs.
- Critère « tests verts, linters sans erreur nouvelle » (forme amendée au Suivi) : atteint, vérifié
  sur arbres extraits.
- Hors-périmètre : respecté. Aucun fichier de `~/.config/nvim`, aucune donnée ni contrat de
  registre ; les listes du pipeline ne sont pas migrées.
- Signal de dérive (« le diff modifie un contrat existant ») : non matérialisé, diff de
  `*contract.toml` vide.
- **R1** — Symptôme d'origine : **atténué, non éliminé, et toujours indétectable.** Le Marqueur d'un
  `date` reste une chaîne TOML (`reviewed = "<OPTIONNEL date>"`) ; c'est désormais son contenu et la
  règle de `contract` qui disent de retirer les guillemets. Mais `reviewed = "2026-10-07"` — la
  faute exacte du Brief — passe encore `gabarit check` et `list-dir validate` **sans aucune note**
  (vérifié : code 0, stderr muet sur ce champ), parce que `check_value` accepte une date ISO en
  chaîne (`gabarit/contract.py`, branche `case "date"`). Aucun critère n'exigeait de la refuser, et
  le Brief a choisi la voie préventive : ce n'est pas un manquement au contrat, mais l'utilisateur
  doit savoir que la disparition du symptôme n'est vérifiable par aucun outil livré, et qu'une date
  écrite entre guillemets continuera de passer inaperçue.
- **R2** — Changement de `LEXIQUE.md` : la définition de Marqueur est modifiée (texte identique à la
  proposition du Plan). Le Brief et le Plan exigent l'accord explicite de l'utilisateur ; ni le
  Journal de décisions du Suivi ni le message de commit E9 ne le consignent. Invérifiable d'ici :
  à confirmer avant l'aplatissement.

### Qualité du code

- **R3** — Docstrings restées à l'état de l'Étape 3 après l'ajout de `deprecated` aux notes (Étape
  6) : le module `gabarit/check.py` (« `notes` dit ce qui est périmé sans être faux — un ancien
  marqueur générique sur un champ typé »), `ListStore.notes()` dans `listdir/store.py` (« un ancien
  marqueur générique sur un champ typé —, une note par champ ») et le module
  `listdir/commands/validate.py` ne nomment que l'ancien Marqueur. Le code émet aussi les notes de
  champ et de section dépréciés : la prose du fichier dit moins que ce qu'il fait, ce que ces
  docstrings en capitales prétendent justement garantir.
- **R4** — Effet immédiat sur les listes réelles : dès l'aplatissement, `list-dir validate` sur
  `technical-debt` imprime 39 notes, et 22 sur `technical-debt-solde` (`reviewed = "<OPTIONNEL>"`),
  jusqu'à un `migrate` que le Brief renvoie au Chantier du registre. Comportement voulu par le
  critère, code 0 vérifié ; mais ce bruit couvrira, dans l'intervalle, l'avertissement de
  provenance qui le précède et toute note utile.
- **R5** — `listdir/store.py`, `_realign`, message de `Change` « ajouté, {valeur} » : un `bool`
  ajouté s'y affiche `False` (vérifié : `champ « pin » — ajouté, False`), alors que la décision 7
  du Plan pose `forme_texte` comme la seule graphie affichée d'une valeur. Le message préexiste ;
  c'est le type `bool`, nouveau, qui rend la graphie fausse.
- **R6** — Style d'import incohérent avec les fichiers voisins : `commands/list.py` importe
  `check_value` et `is_marker` de `gabarit.contract`, alors que `listdir.contract` les réexporte et
  que `store.py` prend `is_marker` par cette réexportation ; dans `store.py`, `PLACEHOLDER` vient de
  `gabarit.types` et `OPTIONAL`, sa constante sœur, de `.types`. Rien ne casse ; deux chemins
  d'import pour les mêmes noms rendent la règle « `listdir` réexporte plutôt que redéfinir » moins
  lisible.

Le reste est sain : cas limites du tri couverts (`-` seul, champ inconnu, valeurs non conformes,
Marqueurs et absents en fin dans les deux sens), `is_marker` gardé contre une valeur non hachable,
refus de contrat nommés plutôt que corrigés, pose stricte d'un `bool`, aucun échec avalé en
silence ; la seule suppression de typeur (`list.py`, `reportOperatorIssue`) est commentée et
conforme à l'usage du dépôt.

### Dette induite

- **R7** — `parse_field` / `parse_section` ne refusent toujours pas une clé inconnue : une faute de
  frappe `deprecaed = "…"` donne un contrat accepté (vérifié : `gabarit contract` code 0) et un
  champ qui reste posé et réclamable. Le défaut préexiste (noté en Passation), mais la nouvelle clé
  en relève le coût : l'erreur ne se voit qu'au moment où `new` repose le champ qu'on croyait
  retiré. Absent du Registre à ce jour.
- **R8** — Le Chantier laisse trois consommateurs des Marqueurs génériques hors d'état : Neovim
  (`plugins/listdir/lua/listdir/picker/items.lua:12`, `lua/chantier.lua:14`), qui affichera
  `<OPTIONNEL date>` comme une valeur, et `skills/implementation-tracker/references/dette.md:164`.
  Reporté et nommé au Plan (« Hors de ce Chantier, à reporter ») : dette assumée, à verser au
  Registre ou à la road-map à la Clôture pour qu'elle ne vive pas que dans un Plan archivé.

### Bloquants

Aucun.

## 2026-10-07 — clôture — `d5be681`

**Verdict** : RÉSERVES

Second audit de clôture, après la Retouche `E10.1` (`d5be681`), qui répond aux constats R3, R5 et
R6 de l'audit `22f3139`. Diff audité : `git diff master...socle-contrat-evolutif`, 30 fichiers,
+1992 −85 ; diff de la Retouche (`git show d5be681`) lu ligne à ligne : 7 fichiers, +53 −16. Brief,
Suivi et Plan relus. Le critère « linters propres » est jugé dans sa forme amendée et datée au
Suivi (« aucune erreur nouvelle par rapport à la base »), qui fait foi.

Les numéros ci-dessous sont ceux de cette section ; la correspondance avec l'audit `22f3139` est
donnée sur chaque constat repris.

### Vérifications exécutées

- `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ skills/gabarit/scripts/tests/ scripts/tests/`
  → **763 passed**, 0 échec (20,0 s). Un test de plus qu'au premier audit, ajouté par la Retouche.
- `uvx ruff check . --output-format concise`, sur les arbres extraits par `git archive` de `master`
  et de `d5be681` → 2 erreurs de chaque côté, les mêmes (`test_fusion.py:268` et `:295`, E501).
  Aucune erreur nouvelle.
- `uvx ruff format --check .`, mêmes arbres → base « 99 files already formatted », branche « 103
  files already formatted ».
- `uvx --with pytest basedpyright --outputjson`, mêmes arbres → **133 erreurs de chaque côté** ;
  listes normalisées (fichier, règle, message, sans numéro de ligne) **identiques** à l'octet.
- `git diff --stat master...socle-contrat-evolutif -- '*contract.toml'` → vide.
- `uvx rumdl fmt --check` sur les 10 Markdown du diff → code 0 (3 constats non corrigibles,
  inchangés depuis le premier audit).
- Critères rejoués à la main sur une liste et une Semence de bac à sable (scratchpad) déclarant
  `int`, `date`, `bool` (`text = "false"`), `list`, `enum`, `text`, un champ et une section
  `deprecated` :
  - `list-dir new` et `gabarit new --from` → `prio = "<À REMPLIR int>"`,
    `poids = "<OPTIONNEL int>"`, `date = "<À REMPLIR date>"`, `reviewed = "<OPTIONNEL date>"`,
    `tags = "<OPTIONNEL list>"`, `pin = false` (booléen nu), `sev = "<OPTIONNEL>"` ; champ et
    section `deprecated` absents.
  - `validate` / `check` → code 0 ; `--filled` → code 1, ne réclame que `title`, `prio`, `date`,
    `Constat`.
  - Élément aux anciens Marqueurs, portant `source` et `## Ancien` dépréciés → `validate` et `check`
    code 0, une note par ancien Marqueur (avec la forme typée) et par élément déprécié (avec la
    consigne).
  - `<OPTIONNEL date>` posé sur un `int` → manquement nommé, code 1.
  - `migrate --dry-run` puis `migrate` → trois Marqueurs génériques convertis à statut égal,
    commentaire `# légende de prio` gardé, valeurs écrites intactes, `source` et `## Ancien` gardés
    et ajoutés nulle part ; message **`champ « pin » — ajouté, false`** ; second `--dry-run` :
    « déjà conforme ».
  - `list --sort prio` → `9`, `10`, Marqueurs en fin ; `--sort=-prio` → `10`, `9`, Marqueurs en
    fin ; `--sort sev` → `note`, `majeur`, `critique`, `<OPTIONNEL>` ; `--sort=-sev` → l'inverse,
    Marqueur en fin ; `--where pin=true` → `b` ; `--sort=-` → code 1 nommé.
  - `list-dir contract` → stdout identique octet pour octet à `.list/contract.toml`, règle des
    guillemets sur stderr ; `--values sev` → les seules valeurs.
  - `bool` prérempli `text = "True"` → `gabarit new` refuse en le nommant, code 1.
- `list-dir validate` sur les sept listes réelles de `.claude/implementation/` → code 0 partout ;
  notes « ancien marqueur » : 39 (`technical-debt`), 22 (`technical-debt-solde`), 2
  (`technical-debt-ecarte`), 0 ailleurs.
- `gabarit check` sur le Suivi et le Brief → conformes, code 0.

### Conformité à l'intention

- Critère « Marqueurs typés posés par `new`, tenus pour des Marqueurs, `--filled` ne réclame que
  les requis » : atteint, vérifié côté `gabarit` et côté `list-dir`.
- Critère « `bool` déclarable, `text = "false"` pose le booléen » : atteint, vérifié.
- Critère « `migrate` convertit l'ancien Marqueur sur `int`/`date` sans toucher de valeur écrite ;
  non migré, accepté par `validate` avec avertissement sur stderr, code inchangé » : atteint,
  vérifié.
- Critère « `deprecated` : absent d'un fichier neuf, jamais ajouté par `migrate`, jamais réclamé ni
  signalé comme non déclaré ; avertissement avec consigne, code inchangé » : atteint, vérifié pour
  un champ et une section.
- Critère « `list --sort` décroissant, `enum` dans l'ordre des `values`, `int` en nombre » :
  atteint, vérifié.
- Critère « `contract` et la référence de format disent que seuls `text`, `enum`, `slug` gardent
  leurs guillemets » : atteint, vérifié sur stderr de `contract` ; la référence n'a pas changé
  depuis le premier audit.
- Critère « tests verts, linters sans erreur nouvelle » (forme amendée) : atteint, vérifié sur
  arbres extraits.
- Hors-périmètre : respecté. Aucun fichier Neovim ni du Registre ; listes du pipeline non migrées.
- Signal de dérive : non matérialisé, aucun `contract.toml` dans le diff.
- Accord sur `LEXIQUE.md` (R2 de `22f3139`) : **levé**. Le Journal de décisions consigne désormais
  l'accord de l'utilisateur sur la ligne exacte avant le commit E9 ; le Suivi fait foi.
- **R1** (reprend R1 de `22f3139`) — Symptôme d'origine : atténué, non éliminé, toujours
  indétectable. Revérifié : `reviewed = "2026-10-07"` entre guillemets passe `gabarit check`, code
  0, sans aucune note. Aucun critère ne demandait de le refuser ; le Suivi prévoit de verser ce
  constat au Registre à la Clôture.

### Qualité du code

La Retouche `E10.1` lève les trois constats qu'elle visait, sans en ouvrir de nouveau :

- R3 de `22f3139` (docstrings) : **levé**. Le module `gabarit/check.py`, `ListStore.notes()` et le
  module `listdir/commands/validate.py` nomment maintenant les champs et sections `deprecated` à
  côté de l'ancien Marqueur.
- R5 de `22f3139` (`False` affiché) : **levé**. `_realign` passe par `forme_texte` ; vérifié par le
  CLI (`ajouté, false`) et couvert par le test `test_migrate_dit_un_booleen_ajoute_a_sa_forme_toml`.
- R6 de `22f3139` (deux chemins d'import) : **levé**. `commands/list.py` importe de
  `listdir.contract` ; `store.py` prend `PLACEHOLDER`, `TYPED_MARKER_TYPES` et `marker` par
  `listdir.types`, qui les réexporte selon l'idiome `X as X` du fichier. Les imports directs de
  `gabarit.check` et `gabarit.prefill` qui restent dans `store.py` existaient déjà sur la base.
- **R2** (reprend R4 de `22f3139`) — Bruit sur les listes réelles dès l'aplatissement : 39 notes sur
  `technical-debt`, 22 sur `technical-debt-solde` et 2 sur `technical-debt-ecarte` (cette dernière
  n'avait pas été relevée au premier audit). Le comportement est voulu par le critère et le code de
  retour reste 0. Le bruit dure jusqu'au `migrate` du Chantier du registre ; le Suivi prévoit de le
  verser au Registre.

### Dette induite

- **R3** (reprend R7 de `22f3139`) — `parse_field` / `parse_section` acceptent toujours une clé
  inconnue : une faute de frappe dans `deprecated` passe sans un mot. Inchangé. Le Suivi prévoit de
  le verser au Registre à la Clôture.
- **R4** (reprend R8 de `22f3139`) — Trois consommateurs des Marqueurs génériques restent hors
  d'état : Neovim (`plugins/listdir/lua/listdir/picker/items.lua:12`, `lua/chantier.lua:14`) et
  `skills/implementation-tracker/references/dette.md`. C'est une dette assumée et hors périmètre ;
  le Suivi prévoit de la verser au Registre à la Clôture.

### Bloquants

Aucun. Le verdict reste RÉSERVES et non FAVORABLE pour une raison : R1 (le symptôme d'origine reste
indétectable) et R2 à R4 sont des dettes ouvertes. L'utilisateur doit les connaître avant
l'aplatissement, et le Suivi s'engage à les verser au Registre à la Clôture : c'est cette
inscription qui les rend traçables.
