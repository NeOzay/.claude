---
slug: semences-de-listes
titre: Amorcer les répertoires-listes dans un projet neuf
branche: semences-de-listes
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-30-semences-de-listes.plan.md
brief: .claude/implementation/done/2026-08-30-semences-de-listes.brief.md
audit: .claude/implementation/done/2026-08-30-semences-de-listes.audit.md
créé: 2026-08-30
maj: 2026-08-30
---

## Objectif et périmètre

Repris du brief, pas réinventé.

**Symptôme** : « un problème survient quand c'est utilisé dans un projet qui ne possède pas encore
les listes ». Les trois registres de dette n'existent que dans ce dépôt-ci ; ailleurs, l'Étape 0 de
`debt-review` rend trois `ÉCHEC` et aucune étape ne dit quoi faire ensuite.

**But** : « un répertoire dédié aux définitions de listes que lui et les autres skills pourront
utiliser comme référence, une structure précise qu'attend la skill list-dir pour trouver et
initialiser une nouvelle liste ».

**Critères de réussite** :
- amorcer une liste par le nom de sa définition produit une liste dont `list-dir validate` sort 0
- les trois registres s'amorcent dans un projet vide, puis `validate` passe sur les trois
- `list-dir derive` fonctionne après amorçage : `templates/review.{toml,md}` ont suivi
- une définition posée dans `<projet>/.claude/list-dir/<nom>/` s'amorce sans qu'aucun skill la porte
- `list-dir init` sans définition nommée produit le squelette actuel, inchangé
- deux définitions de même rang portant le même nom font sortir la commande non nul, en les nommant
- `grep -ril 'dette\|debt' skills/list-dir/` ne rend toujours aucune sortie

**Hors-périmètre** :
- les contrats eux-mêmes ne changent pas : les semences sont la copie de l'existant
- aucune commande **existante** autre que `init` n'est modifiée ; `defs` et `contract` sont neuves
- les plugins ne forment pas un cinquième rang — aucun plugin installé ne porte de skill
- `debt-review/references/gabarit-rapport.md` n'est pas touché (Q2) — au registre de dette à la clôture
- pas de re-semis : rien ne remet une liste existante en phase avec sa définition

**Signaux de dérive** :
- `list-dir` connaît le mot « dette »
- un **registre** de définitions au lieu d'une découverte par arborescence
- l'amorçage compose des contrats (héritage, surcharge, fusion) au lieu de copier
- l'amorçage crée des entrées : une liste neuve est vide
- une documentation qui décrit un contrat que l'outil n'applique pas

## Étapes

- [x] 1. `listdir/definitions.py` — découvrir et résoudre — `skills/list-dir/scripts/listdir/definitions.py` — vérif: `cd skills/list-dir && uvx pytest scripts/tests/test_definitions.py -q`
- [x] 2. `init_list` accepte une définition — `skills/list-dir/scripts/listdir/store.py` — vérif: `cd skills/list-dir && uvx pytest scripts/tests/test_store_ecriture.py -q`
- [x] 3. `init --def` / `--from` — `skills/list-dir/scripts/listdir/commands/init.py` — vérif: `cd skills/list-dir && uvx pytest scripts/tests/test_entree_cli.py -q -k "init_def"`
- [x] 4. `commands/defs.py` — découvrir les définitions — `skills/list-dir/scripts/listdir/commands/defs.py` — vérif: `cd skills/list-dir && uvx pytest scripts/tests/test_entree_cli.py::test_defs_liste_et_origine -q`
- [x] 5. `commands/contract.py` — imprimer le contrat en vigueur — `skills/list-dir/scripts/listdir/commands/contract.py` — vérif: `cd skills/list-dir && uvx pytest scripts/tests/test_entree_cli.py::test_contract_imprime_le_contrat -q`
- [x] 6. Documenter la convention — `skills/list-dir/SKILL.md`, `skills/list-dir/references/contrat-liste.md` — vérif: `grep -c 'douze commandes' skills/list-dir/SKILL.md`
- [x] 7. Les trois semences — `skills/implementation-tracker/list-dir/` — vérif: boucle `init --def` + `validate` + `derive` sur les trois (plan, étape 7)
- [x] 8. `dette.md` renvoie au contrat en vigueur — `skills/implementation-tracker/references/dette.md` — vérif: `grep -c 'list-dir contract' skills/implementation-tracker/references/dette.md`
- [x] 9. `debt-review` route l'échec de l'Étape 0 — `skills/debt-review/SKILL.md` — vérif: `awk '/## Étape 0/,/## Étape 1/' skills/debt-review/SKILL.md | grep -c 'dette.md'`
- [x] 10. Contrôle final — vérif: `cd skills/list-dir && uvx pytest scripts/tests/ -q && uvx ruff check . && uvx --with pytest basedpyright`

## État courant

**Prochaine action** : aucune — chantier clos.
**Vérification** : `cd skills/list-dir && uvx pytest scripts/tests/ -q` → 282 passed ;
`uvx ruff check .` et `uvx --with pytest basedpyright` propres ; `python3 scripts/check_pipeline.py`
conforme ; bout en bout rejoué dans un projet neuf hors dépôt.
**Dernier audit** : `3f12f2a` — RÉSERVES — 2026-08-30. Sept audits successifs, 22 constats : 14
traités, 7 versés au registre de dette à la clôture, R21 résolu par ce versement même.
**Notes** : clos avec réserves sur arbitrage de l'utilisateur.

## Journal de décisions

- **2026-08-30** — une définition de liste ne vit pas forcément dans un skill : `list-dir` résout un
  nom dans quatre rangs ordonnés (projet, skills du projet, config, skills de la config), la
  spécificité prime, l'ambiguïté ne vaut qu'à rang égal. *Rejeté* : rang unique `<skill>/list-dir/`,
  qui obligerait à inventer un skill coquille pour porter un contrat.
- **2026-08-30** — deux remontées distinctes, et non une : un projet *contient* un `.claude`, la
  configuration *est* un `.claude`. *Pourquoi* : sur ce dépôt (`~/.claude` porte `~/.claude/.claude`)
  une règle unique ferait viser le mauvais répertoire à l'un des ancrages. Divergence avec le brief,
  qui fixait `which("list-dir")` — rendu `None` sur un appel par chemin, les rangs disparaîtraient
  en silence. Ratifiée par l'utilisateur.
- **2026-08-30** — la définition fait autorité le temps de l'`init` et pas au-delà : toute commande
  lit `<liste>/.list/contract.toml` (`contract.py`, `contract_path`). *Conséquence* : `dette.md`
  renvoie à `list-dir contract`, jamais au fichier de semence, et il n'existe aucun re-semis — un
  projet qui redéfinit sa liste au rang 1 a délibérément pris la main.
- **2026-08-30** — `--name` et `--description` avec `--def`/`--from` sortent en code 2 plutôt que
  d'être ignorés : rendre 0 sur un contrat qui ne porte pas ce qui a été demandé est un échec ouvert.
- **2026-08-30** — l'Étape 0 de `debt-review` imprime une étiquette par registre, et les trois
  registres n'y sont **pas symétriques** : `technical-debt` est la source dont l'Étape 1 dérive,
  `-solde` et `-ecarte` les destinations où l'Étape 5 écrit. *Pourquoi* : aucun des états ne se
  déduit du seul code de retour de `validate`, et une règle uniforme se trompe sur deux registres
  sur trois.
- **2026-08-30** — `uvx ruff format --check` retiré du contrôle final : il échoue sur cinq fichiers
  antérieurs, et `contrat.md` ne déclare que `ruff check` et `basedpyright`. Porté au registre.
- **2026-08-30** — clos avec réserves sur arbitrage de l'utilisateur. Sept correctifs successifs ont
  chacun produit un constat neuf sur la **même** Étape 0 de `debt-review` : chaque correction
  relisait la ligne visée, jamais son voisinage. C'est la leçon du chantier, et elle est écrite dans
  le mode de défaillance de cette étape.
