+++
gabarit = "suivi"
slug = "solder-sept-dettes"
titre = "Solder sept dettes relues le 2026-10-14 : deux de documentation, quatre correctifs, un manque de tests"
branche = "solder-sept-dettes"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-15-solder-sept-dettes.plan.md"
road-map = "solder-sept-dettes-relues-le-2026-10-14"
audit = ".claude/implementation/done/2026-10-15-solder-sept-dettes.audit"
skills = ["skill-convention", "claude-code-mods"]
"créé" = 2026-10-15
maj = 2026-10-15
+++

## Objectif et périmètre

Ouvert sans Brief, sur décision de l'utilisateur : l'entrée de road-map
`solder-sept-dettes-relues-le-2026-10-14` décrit déjà chaque dette, ce qu'il faut faire et comment
le vérifier. Elle fait foi pour l'intention.

**Symptôme** : sept dettes du registre restent ouvertes, alors que la relecture du 2026-10-14 les a
toutes revérifiées : chacune est toujours vraie, bornée et peu coûteuse à solder. Il y a un faux
positif du contrôle 7, qui a fait retirer un lien utile, une recherche `shadow-skill cherche` qui
ramène du bruit, un lexique qui vise le HOME quand celui-ci est versionné par git, une sortie de
`migrate` qui casse l'invariant « un changement, une ligne », un `reseed` sans test par la ligne
de commande, et deux limites du lexique que la documentation ne dit pas.

**But** : solder les sept dettes `lexique-depend-du-path-de-la-session`,
`conversation-reprise-sans-lexique-local-jusqua-compaction`,
`controle-7-lit-shadow-skills-comme-skills`, `cherche-par-sous-chaine`,
`lexique-home-versionne-par-git`, `migrate-valeur-multilignes-casse-une-ligne-par-changement` et
`reseed-sans-test-cli`, en suivant ce que l'entrée a décidé là où elle s'écarte du « Pour solder »
de la dette.

**Critères de réussite** :

- chaque dette a sa preuve, une commande exécutée et sa sortie réelle, et passe dans
  `technical-debt-solde/` à la Clôture ;
- les tests nommés par l'entrée existent et passent : lien `shadow-skills/` et cas homonyme
  (contrôle 7), « skill » contre « This skill » (cherche), HOME git simulé (lexique), section
  multi-lignes et valeur d'une ligne (migrate), et cinq cas de `reseed` par la ligne de commande ;
- le lien vers `claude-code-mods` est rétabli dans `skills/mod-commun/SKILL.md` ;
- la suite de tests, `ruff`, `rumdl` et `check_pipeline.py` sont verts, et `basedpyright` ne
  régresse pas par rapport à la Base.

**Hors-périmètre** :

- chercher un événement de reprise qui recomposerait la section du lexique (dette 2) ;
- le sous-agent chercheur de Shadow-skills, qui a son entrée à part ;
- faire résoudre `lexique` sans le `PATH` de la session : l'entrée retient la documentation.

**Signaux de dérive** :

- le diff touche un mod (`register.ts`) ailleurs que dans le commentaire de `prompt.compose` ;
- la documentation de la dette 1 va dans `skills/lexique/SKILL.md` plutôt que dans
  `.claude/CLAUDE.md`, contre la décision de l'entrée ;
- `forme_texte` change, alors qu'elle sert aussi aux filtres et à `list` ;
- une dette hors des sept est touchée, ou une huitième est soldée en passant.

## Étapes

- [x] 1. Contrôle 7 : garde arrière `-`, tests, lien rétabli — `scripts/check_pipeline.py`, `scripts/tests/test_controle_7.py`, `skills/mod-commun/SKILL.md` — vérif: `~/.claude/.venv/bin/python -m pytest scripts/tests/test_controle_7.py scripts/tests/test_controle_8.py && python3 scripts/check_pipeline.py`
- [x] 2. `shadow-skill cherche` en début de mot — `skills/shadow-skill/scripts/shadow_skill.py`, `shadow-skill-cli.py`, `SKILL.md`, `tests/test_lire.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/shadow-skill/scripts/tests/ && uvx rumdl fmt --check skills/shadow-skill/SKILL.md`
- [x] 3. `lexique` sous un HOME git : Constat complété, `racine_projet`, doc, test — dette `lexique-home-versionne-par-git`, `skills/lexique/scripts/lexique.py`, `lexique-cli.py`, `SKILL.md`, `tests/test_projet.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests/ && list-dir validate .claude/implementation/todo/technical-debt`
- [x] 4. Libellé multi-lignes des `Change` — `skills/list-dir/scripts/listdir/store.py`, `tests/test_store_ecriture.py`, `tests/test_fill.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_store_ecriture.py skills/list-dir/scripts/tests/test_fill.py`
- [x] 5. `reseed` testé par la ligne de commande — `skills/list-dir/scripts/tests/jouet.py`, `test_reseed.py`, `test_entree_cli.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_entree_cli.py skills/list-dir/scripts/tests/test_reseed.py`
- [x] 6. Dépendance des commandes de `bin/` au `PATH` — `.claude/CLAUDE.md` — vérif: `grep -n "lexique local" .claude/CLAUDE.md && uvx rumdl fmt --check .claude/CLAUDE.md`
- [x] 7. Conversation reprise sans recomposition du lexique — `skills/lexique/SKILL.md`, `shadow-skills/claude-code-mods/SKILL.md`, `skills/lexique/hooks/register.ts` — vérif: `npx --yes @biomejs/biome@2 format skills/lexique && claude plugin test skills/lexique && python3 scripts/check_pipeline.py`
- [x] 8. Corriger R1, R2, R3 de l'audit `e2b506a` : `libelle` sans saut de ligne résiduel, Plan formaté, basedpyright sans régression — `skills/list-dir/scripts/listdir/store.py`, `tests/test_store_ecriture.py`, `skills/shadow-skill/scripts/tests/test_lire.py`, `.claude/plans/robust-soaring-hejlsberg.md` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_store_ecriture.py skills/shadow-skill/scripts/tests/ && uvx rumdl fmt --check .claude/plans/robust-soaring-hejlsberg.md && test "$(uvx --with pytest basedpyright scripts skills/shadow-skill skills/lexique skills/list-dir | grep -oE '^[0-9]+ errors' | cut -d' ' -f1)" -le 81`

## État courant

**Prochaine action** : relancer l'audit de Clôture, complet.

**Vérification** : chaque suite dans son propre `pytest` (voir le journal),
`~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ && ~/.claude/.venv/bin/python -m pytest scripts/tests/ && ~/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests/ && ~/.claude/.venv/bin/python -m pytest skills/shadow-skill/scripts/tests/ && python3 scripts/check_pipeline.py`

**Dernier audit** : 51fb1a8 — FAVORABLE — 2026-10-15

**Preuves relevées** :

- `controle-7-lit-shadow-skills-comme-skills` : sans le correctif, `check_pipeline.py` rend
  « ✗ skills/mod-commun/SKILL.md:16 → chemin de skill inexistant :
  skills/claude-code-mods/SKILL.md » ; avec, « ✓ 34 chemins de skill cités, tous existent »,
  et les deux nouveaux tests échouent avant, passent après (28 passed).
- `cherche-par-sous-chaine` : `test_chercher_en_debut_de_mot` échoue avant, passe après
  (44 passed). Sur les Shadow-skills réels, `cherche kill`, `est` et `ion` ramenaient 2 à 4
  skills, plus aucun après ; `test`, `lsp`, `code` rendent les mêmes.
- `lexique-home-versionne-par-git` : sur un HOME git simulé, un projet non versionné dessous
  dont le local redéfinit « Semence ». Avant, `liste` rend « … est le lexique global, ignoré
  comme local » et sort 0, `chemin` sort 1 ; après, `liste` signale « « Semence » … est déjà
  réservé au global » et sort 1, `chemin` rend le local du projet. 91 passed.
- `migrate-valeur-multilignes-casse-une-ligne-par-changement` : une section à
  `command = "printf 'ligne1\nligne2\n'"`, `list-dir migrate` rendait « … ajoutée, ligne1 »
  puis « ligne2 » à part ; il rend « … ajoutée, ligne1 … » sur une ligne. Les trois tests
  nouveaux échouent avant, passent après (84 passed).
- `reseed-sans-test-cli` : cinq tests `reseed` par `lancer` dans `test_entree_cli.py` (conflit,
  `--force` sur liste gelée, `--dry-run`, nom discordant, sans provenance) ; 534 passed. Remettre
  `utils.fail(r.message)` sans le code, le bloquant d'origine, fait échouer
  `test_reseed_nom_discordant_rend_le_code_2`.
- `lexique-depend-du-path-de-la-session` : `grep -n "lexique local" .claude/CLAUDE.md` rend la
  ligne 25, dans « Outillage » ; documentation seule, comme l'entrée l'a décidé.
- `conversation-reprise-sans-lexique-local-jusqua-compaction` : la limite et son remède sont
  écrits dans « Ce que reçoit la session » de `skills/lexique/SKILL.md`, avec la lecture unique
  par processus (remède : relancer Claude Code dans une nouvelle conversation) ; « survit à
  `--continue` » et « survit à la reprise » sont corrigés dans `claude-code-mods` et dans le
  commentaire de `register.ts`. `claude plugin test skills/lexique` : 8 pass.
- Étape 8 (R1, R3 de l'audit `e2b506a`) : trois cas de `test_libelle_tient_sur_une_ligne_sans_ligne_vide`
  échouent sur l'ancien `libelle`, passent après (542 passed) ; basedpyright sur `scripts
  skills/shadow-skill skills/lexique skills/list-dir` rend 81 erreurs, comme la Base.

**Notes** : sans Brief, c'est l'entrée de road-map qui fait foi pour l'intention. Les arbitrages
du Plan (comparaison en début de mot, `fill` inclus, Q10) sont dans sa section « Décisions ».

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien. L'Étape 1 n'a pas commencé.

**À savoir** :

- la commande de tests d'`OUTILLAGE.md` ne couvre ni `skills/lexique/scripts/tests/` ni
  `skills/shadow-skill/scripts/tests/` : il faut les lancer en plus, comme le fait la vérification
  du Suivi ;
- `semer` (`test_reseed.py`) fait un `os.chdir(tmp_path)`. Une fois déplacé dans `jouet.py`, il le
  garde pour les tests de bibliothèque ; les tests CLI de l'Étape 5 passent par
  `lancer(..., cwd=tmp_path)`, parce que `reseed --def` résout la définition depuis le répertoire
  courant (rang projet `.claude/list-dir/`) ;
- `shadow-skill cherche` avec plusieurs mots exige que chacun soit présent (un ET) : une recherche
  `cherche tests conventions mods` ne rend rien. Il faut chercher mot par mot.

## Dettes écartées

- R2 — le Suivi reste hors du format de `rumdl` : son format d'Étape sur une ligne, que lit
  `audit new`, contredit le réenroulement à 100 colonnes ; le Plan est formaté, le défaut sort
  avec le Suivi en `done/`, et la contradiction ira au registre de dette à la Clôture — 2026-10-15

## Journal de décisions

- **2026-10-15** — Chantier ouvert sans Brief. *Pourquoi* : l'entrée de road-map fixe déjà les
  critères de chaque dette. *Rejeté* : un Brief minimal, un cadrage complet.
- **2026-10-15** — `shadow-skill cherche` compare en début de mot. *Pourquoi* : « test » ne ramène
  plus « latest », et un pluriel tapé ou omis trouve encore le skill. *Rejeté* : le mot entier.
- **2026-10-15** — Une citation `shadow-skills/…` qui n'est pas un lien `](../…)` n'est plus
  vérifiée par aucun contrôle (Q10). *Pourquoi* : le contrôle 7 vérifiait alors le mauvais
  fichier, donc la perte n'est pas nouvelle. *Rejeté* : étendre le contrôle 7, inscrire une dette.
- **2026-10-15** — Le cache du lexique dans `register.ts` reste ; son retrait va en road-map,
  `lexique-relu-a-chaque-composition`. *Pourquoi* : toucher le code du mod est un Signal de dérive.
  *Rejeté* : le retirer dans ce Chantier.
- **2026-10-15** — Audit `e2b506a` DÉFAVORABLE (R2 `rumdl`, R3 basedpyright) : R1 et R3 corrigées
  en Étape 8, R2 écartée pour le Suivi seul, R4 et deux problèmes hors périmètre au registre
  (`format-d-etape-contredit-rumdl`, `suites-de-tests-homonymes-entre-skills`). Audit `51fb1a8`
  FAVORABLE. *Pourquoi* : choix de l'utilisateur. *Rejeté* : exempter les Suivis dans
  `.rumdl.toml`, faire lire à `pose.py` une Étape enroulée.
