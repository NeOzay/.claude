+++
gabarit = "suivi"
slug = "socle-contrat-evolutif"
titre = "Socle gabarit/list-dir : type bool, marqueurs typés, champs et sections dépréciés, tri"
branche = "socle-contrat-evolutif"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "sonnet"
plan = ".claude/implementation/done/2026-10-07-socle-contrat-evolutif.plan.md"
brief = ".claude/implementation/done/2026-10-07-socle-contrat-evolutif.brief.md"
audit = ".claude/implementation/done/2026-10-07-socle-contrat-evolutif.audit.md"
road-map = "<OPTIONNEL>"
skills = ["skill-convention"]
"créé" = 2026-10-07
maj = 2026-10-07
+++

## Objectif et périmètre

**Symptôme** : les Marqueurs actuels induisent le modèle en erreur — il écrit
`reviewed = "2026-10-07"` sans omettre les guillemets ; et une List-dir ne sait pas faire évoluer
ses champs (les modifier, pas seulement en ajouter).

**But** : un socle `gabarit`/`list-dir`, couvert par des tests, qui donne au modèle des Marqueurs
du type du champ, un type `bool`, une clé `deprecated` sur champs et sections, et un tri utile à
la priorisation — base du Chantier du registre de dettes.

**Critères de réussite** :

- `gabarit new` et `list-dir new` posent `<À REMPLIR int>` / `<OPTIONNEL int>` sur un `int` sans
  préremplissage, et `<À REMPLIR date>` / `<OPTIONNEL date>` sur un `date` ; `check`/`validate` les
  tiennent pour des Marqueurs, `--filled` réclame les seuls requis.
- Un champ `bool` est déclarable ; `text = "false"` pose le booléen TOML `false`, pas la chaîne.
- `migrate` remplace un Marqueur générique sur un champ `int` ou `date` par sa forme typée, et ne
  touche à aucune valeur écrite ; non migré, ce Marqueur est accepté par `validate`, qui avertit
  sur stderr sans changer son code de retour.
- Un champ ou une section `deprecated` : absent d'un fichier neuf, jamais ajouté par `migrate`,
  jamais réclamé ni signalé comme non déclaré ; tant qu'un élément le porte, `validate` avertit sur
  stderr avec la consigne, sans changer son code de retour.
- `list --sort` trie en décroissant sur demande, un `enum` dans l'ordre de ses `values`, un `int`
  en nombre.
- `contract` et la référence de format disent que seuls `text`, `enum` et `slug` gardent leurs
  guillemets.
- Tests verts, linters propres — **amendé le 2026-10-07** : linters et typeur **sans erreur
  nouvelle par rapport à la base** (voir Journal de décisions).

**Hors-périmètre** :

- Le registre de dettes : champs sévérité (enum `note`/`avertissement`/`majeur`/`critique`),
  chantier, référence, pin, découpage de `source`, migration des listes du pipeline — Chantier
  distinct, qui s'appuie sur ce socle.
- L'adaptation de Neovim aux nouveaux Marqueurs et au type `bool` — son propre Chantier.

**Signaux de dérive** :

- Le diff modifie un contrat existant — une semence (`skills/*/list-dir/*/contract.toml`,
  `skills/*/gabarit/*/contract.toml`) ou le `.list/contract.toml` d'une liste.

## Étapes

- [x] 1. Type `bool` — `gabarit/{types,contract,prefill}.py`, `listdir/store.py`,
  `listdir/commands/list.py`, tests — vérif: pytest
- [x] 2. Marqueurs typés : pose et reconnaissance — `gabarit/{types,contract}.py`, tests —
  vérif: pytest
- [x] 3. Ancien Marqueur : avertissement — `gabarit/{check,commandes}.py`, `listdir/store.py`,
  `listdir/commands/validate.py`, tests — vérif: pytest
- [x] 4. `migrate` convertit les anciens Marqueurs — `listdir/store.py`, tests — vérif: pytest
- [x] 5. `deprecated` : lecture, pose, migration, contrôle —
      `gabarit/{types,contract,prefill,check}.py`, `listdir/store.py`, tests — vérif: pytest
- [x] 6. `deprecated` : avertissement — `gabarit/check.py`, tests — vérif: pytest
- [x] 7. Tri typé et décroissant — `listdir/commands/list.py`, tests — vérif: pytest
- [x] 8. Règle des guillemets dans `contract` — `gabarit/commandes.py`,
  `listdir/commands/contract.py`, tests — vérif: pytest
- [x] 9. Documentation et lexique — `skills/{gabarit,list-dir}/references/*.md`, `SKILL.md`,
  `debt-review/references/gabarit-rapport.md`, `LEXIQUE.md` (avec accord) — vérif:
  `uvx rumdl fmt --check .`
- [x] 10. Vérification d'ensemble, sans régression — aucun fichier — vérif: commandes du Plan,
  Étape 10

« pytest » :
`~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/ skills/list-dir/scripts/tests/`

## État courant

**Prochaine action** : Clôture avec réserves, décidée par l'utilisateur. Le Registre de dette
est écrit (R1 à R4 du second audit) ; reste l'aplatissement sur `master` par `commit-chantier`.

**Vérification** :
`~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/ skills/list-dir/scripts/tests/ scripts/tests/`,
puis ruff et basedpyright comparés à la base (Plan, Étape 10).

**Dernier audit** : d5be681 — RÉSERVES — 2026-10-07

**Notes** : 648 tests passent sur la base (relevé de `plan-reviewer`, 2026-10-07) ; 763 après
la Retouche de l'Étape 10. `ruff check`, `ruff format --check` et `basedpyright` sont propres sur
les fichiers Python touchés. `~/.config/nvim/lua/chantier.lua:14` ne reconnaît que les deux
Marqueurs génériques : hors périmètre (Neovim), mais à reprendre dans son Chantier.

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien — la session de création s'arrête au commit de l'état initial.

**À savoir** :

- `parse_field` ne refuse pas une clé inconnue dans `[fields.*]` : une faute de frappe
  (`deprecaed = "…"`) passerait sans un mot. `reseed` aplatit le contrat en clés pointées sans
  liste blanche (`provenance.py`) : `deprecated` y circule sans changement.
- Un succès porteur d'un message (`ok(value, message)`) sort ce message sur stderr : c'est le
  canal des avertissements de `validate`, des notes de `check`, et de la règle des guillemets.
- `skills/gabarit/scripts/tests/` n'est pas dans la commande pytest d'`OUTILLAGE.md` ; avec elle
  et `scripts/tests/`, la base compte 648 tests verts (relevé du 2026-10-07, à AE0).
- Pour le Chantier du registre, dit par l'utilisateur et écrit nulle part ailleurs : `chantier`
  vaut le nom du Chantier ou « Hors chantier », `référence` un `R<n>` ou le lieu du constat,
  `pin` est un `bool` à défaut `false`, et la sévérité est remplie par celui qui crée la dette ;
  le découpage de `source` passera par `deprecated`.

## Journal de décisions

- **2026-10-07** — Critère « linters propres » ramené à « aucune erreur nouvelle par rapport à la
  base », comparée sur un arbre extrait par `git archive`. *Pourquoi* : la base est déjà rouge
  (`ruff` : 2 E501 dans `test_fusion.py` ; `basedpyright` : 133 erreurs sur l'arbre extrait, le
  6580 du Plan étant celui de l'arbre de travail, qui compte `skills/synced/` hors suivi) ;
  décision de l'utilisateur. *Rejeté* : une Étape de nettoyage, qui élargissait le périmètre.
- **2026-10-07** — Marqueur typé pour `int`, `date`, `bool` et `list` ; générique pour `text`,
  `enum`, `slug` et les sections. *Pourquoi* : la règle des guillemets — seule une valeur finale
  en chaîne garde un Marqueur générique ; tranche l'incertitude du Brief. *Rejeté* : dates
  sentinelles `0001-01-01` / `9999-01-01`.
- **2026-10-07** — Tri décroissant : `--sort=-champ`, collé. *Pourquoi* : argparse prend
  `--sort -champ` pour une option (code 2) ; l'aide de `list` le dit. *Rejeté* : un suffixe
  (`champ-`), qui s'écarte du Plan sans lever le problème d'`argparse` ailleurs.
- **2026-10-07** — Clôture avec réserves. Audits `22f3139` puis `d5be681` : RÉSERVES, aucun
  bloquant. R3, R5, R6 corrigés en Retouche `E10.1` ; l'utilisateur clôt avec le reste, versé au
  Registre : deux entrées créées (`notes-ancien-marqueur-sur-les-listes-reelles`,
  `consommateurs-des-marqueurs-generiques-hors-etat`), deux complétées
  (`dates-entre-guillemets-acceptees`, `parsing-du-contrat-avale-les-cles-inconnues`). La ligne de
  Marqueur du `LEXIQUE.md` a reçu l'accord de l'utilisateur avant le commit E9.
