# Plan — solder sept dettes relues le 2026-10-14

## Relecture

Relu par `plan-reviewer` sans Brief : seule la qualité du Plan est jugée.

```
VERDICT : RÉSERVES
CRITÈRES : SANS OBJET
HORS-PÉRIMÈTRE : SANS OBJET
DÉRIVE : SANS OBJET
INCERTITUDES : SANS OBJET
MODÈLE : opus → SOUTENU — deux Étapes de prose (6, 7) qui se vérifient mal par commande, et « au moindre doute, Opus »
QUALITÉ : Q1 — Étape 1 : le test « cite shadow-skills/y/SKILL.md … ne rend aucun rouge » échoue tel qu'écrit. Sans autre citation, le contrôle 7 rend le rouge « aucun chemin de skill cité — contrôle sans objet » (scripts/check_pipeline.py, check_chemins_skill). Le montage doit contenir une citation valide de plus.
Q2 — Étape 1 : pour le cas homonyme, le critère « absence de la citation dans les constats » passe aussi avant le correctif : la citation, lue comme skills/x/seul-la.md qui existe, ne produisait déjà aucun constat. Seul le compte du message vert, avec une deuxième citation dans le fichier, distingue avant et après.
Q3 — Étape 5, test 4 : `--def autre` passe d'abord par resolve("autre"), qui échoue en code 1 (commands/reseed.py) sans définition nommée `autre`. Le code 2 demande une définition `autre` dont le contrat déclare origin.def = "jouet", montage que le plan ne décrit pas.
Q4 — Étape 5, test 5 : la condition « si son contrat ne déclare pas d'origin » est fausse à la lettre. jouet.CONTRAT déclare `[origin] def = false`. Le résultat tient quand même : origin.name est vide, et le message « aucune semence à rattraper » est bien atteint.
Q5 — Étape 6 : la vérification `grep -n "PATH" .claude/CLAUDE.md` réussit déjà avant l'Étape (ligne 36, « l'appelle par le `PATH` »). Elle ne prouve donc pas que le paragraphe a été écrit.
Q6 — Étape 3 : la vérification « list-dir validate » ne nomme pas la liste. Il manque l'argument `.claude/implementation/todo/technical-debt`.
Q7 — Étapes 2 et 3 : les modifications de skills/shadow-skill/SKILL.md, de l'aide de shadow-skill-cli.py et de skills/lexique/SKILL.md ne sont vérifiées par aucune commande de leur Étape (rumdl, contrôle du texte). Seule la vérification de fin les couvre.
Q8 — Étape 2 : shadow_skill.py n'importe pas `re`, que la règle proposée utilise. C'est mineur, mais le plan ne le mentionne pas.
Q9 — Étape 4 : test_prefill.py teste initial_field et initial_section, pas `migrate`, d'où viennent les Change. Les tests annoncés y demandent un montage de liste que ce fichier n'a pas encore. Ce n'est pas bloquant.
Q10 — Décisions, dette 3 : le contrôle 8 ne couvre que les liens Markdown `](../…)` des fichiers de skills/ et shadow-skills/. Une citation `shadow-skills/…` écrite entre backticks, ou faite depuis un .md de la racine, n'est plus vérifiée par aucun contrôle. C'est sans perte réelle, puisque le contrôle 7 vérifiait alors le mauvais fichier, mais la décision ne le dit pas.
```

**Corrigés sans arbitrage**, parce que ce sont des défauts de rédaction (tests ou vérifications
inopérants tels qu'écrits, citations inexactes) :

- Q1 et Q2 : les deux tests de l'Étape 1 montent aussi une citation valide de `skills/`, et
  affirment sur le compte du message vert.
- Q3 : le test 4 de l'Étape 5 monte une définition `autre` dont le contrat déclare
  `origin.def = "jouet"`.
- Q4 : la condition du test 5 est réécrite (`def = false`).
- Q5 : la vérification de l'Étape 6 cherche le texte du nouveau paragraphe.
- Q6 : le chemin de la liste est ajouté.
- Q7 : rumdl est ajouté aux vérifications des Étapes 2 et 3.
- Q8 : l'import de `re` est mentionné.
- Q9 : les tests de `migrate` vont dans `test_store_ecriture.py`, qui appelle déjà
  `migrate()`, avec ses montages.
- Sans numéro : la limite de `claude-code-mods` commence à la ligne 297, pas 298.

**Q10, tranché par l'utilisateur** : accepter la perte de vérification, et l'écrire dans les
Décisions et dans le commentaire de `CHEMIN_SKILL`.

## Contexte

Le chantier part de l'entrée de road-map `solder-sept-dettes-relues-le-2026-10-14`
(`.claude/implementation/todo/road-map/solder-sept-dettes-relues-le-2026-10-14.md`). Il n'a pas de
Brief : l'utilisateur a choisi de s'en passer, parce que l'entrée fixe déjà, pour chaque dette, ce
qu'il faut faire et comment le tester. **L'entrée fait foi pour l'intention.** Elle traite sept
dettes du registre `.claude/implementation/todo/technical-debt/` : deux de documentation, quatre
correctifs et un manque de tests. Chacune a été revérifiée dans le dépôt le 2026-10-14.

Le solde des dettes (leur `move` vers `technical-debt-solde/` avec leur preuve) et la sortie de
l'entrée de road-map se font à la Clôture, comme le prévoit `references/cloture.md`. Ils ne sont pas
des Étapes.

## Modèle

**Opus** : deux Étapes sont de la prose (6 et 7), qui se vérifie mal par commande, et la règle dit
« au moindre doute, Opus ».

## Shadow-skills

- `skill-convention` : chaque Étape écrit dans un fichier de skill (`SKILL.md`, code, tests).
- `claude-code-mods` : l'Étape 7 corrige ce Shadow-skill et le commentaire du mod `lexique`.

## Décisions prises au Plan

- **Point « À établir » de la dette 3** : le contrôle 8 (`check_renvois_skill`,
  `scripts/check_pipeline.py:670`) suit déjà les liens Markdown `](../…)` des fichiers de `skills/`.
  Il vérifie que la cible existe et que l'ancre existe, y compris pour une cible sous
  `shadow-skills/`. Une fois le lien réécrit sous cette forme, le contrôle 7 peut cesser de voir
  `shadow-skills/…`. Une perte est acceptée (Q10, tranché par l'utilisateur) : une citation
  `shadow-skills/…` qui n'est pas un lien `](../…)`, par exemple entre backticks ou dans un `.md`
  de la racine, n'est plus vérifiée par aucun contrôle. Ce n'est pas un trou nouveau : le
  contrôle 7 vérifiait alors le mauvais fichier. Le commentaire de `CHEMIN_SKILL` le dit.
- **Dette 4, comparaison** (arbitrée par l'utilisateur) : un mot cherché doit **commencer un mot**
  du texte, après pliage de la casse et des accents par `_plier`. « test » trouve « tests » mais pas
  « latest ». « skill » trouve encore « This skill », qui contient le mot entier ; « kill » ne le
  trouve plus.
- **Dette 6, portée** (arbitrée par l'utilisateur) : la fonction de libellé sert aussi au `Change`
  de `fill`/`_poser` (`store.py:529`), qui a le même défaut. Le message d'échec de `store.py:505`
  n'est pas un `Change` et ne change pas.

## Étapes

### 1. Contrôle 7 : ne plus lire `shadow-skills/x/…` comme `skills/x/…`

- `scripts/check_pipeline.py` : ajouter `-` à la garde arrière de `CHEMIN_SKILL`, qui devient
  `(?<![\w/.-])`. Mettre à jour le commentaire du motif : la garde exclut aussi un nom qui se
  termine par `skills/`, comme `shadow-skills/`. Le commentaire dit aussi qu'une citation
  `shadow-skills/…` qui n'est pas un lien `](../…)` n'est donc vérifiée par aucun contrôle (Q10).
- `scripts/tests/test_controle_7.py`, deux tests, montés avec `depot_jouet.ecrire` comme les tests
  existants :
  - un `SKILL.md` de `skills/x/` cite `shadow-skills/y/SKILL.md` (avec `skills/y/` absent) **et**
    un chemin valide de `skills/x/`. Il ne rend aucun rouge, et le vert dit « 1 chemins de skill
    cités ». Sans la citation valide, le contrôle rendrait le rouge « contrôle sans objet » (Q1) ;
  - cas homonyme : `skills/x/` et `shadow-skills/x/` existent tous deux. Un `.md` cite
    `shadow-skills/x/seul-la.md`, alors qu'il n'existe que `skills/x/seul-la.md`, et cite aussi un
    chemin valide de `skills/x/`. Le vert dit « 1 chemins de skill cités », et non 2 : c'est le
    seul critère qui distingue l'avant de l'après (Q2).
- `skills/mod-commun/SKILL.md:15-16` : remplacer `` `claude-code-mods` `` par le lien
  `[claude-code-mods](../../shadow-skills/claude-code-mods/SKILL.md)`, en gardant
  `(shadow-skill charge claude-code-mods)`.
- vérif :
  `~/.claude/.venv/bin/python -m pytest scripts/tests/test_controle_7.py scripts/tests/test_controle_8.py && python3 scripts/check_pipeline.py`

### 2. `shadow-skill cherche` compare en début de mot

- `skills/shadow-skill/scripts/shadow_skill.py`, `chercher` : un mot plié `m` est retenu quand
  `re.search(rf"(?<!\w){re.escape(m)}", texte_plié)` trouve une correspondance (importer `re`,
  absent du module aujourd'hui). Docstring : dire la règle (début de mot) et la raison (un mot court
  comme « test » ou « lua » ne ramène plus « latest » ou « evaluate »).
- Les deux textes qui décrivent la recherche : l'aide `cherche` de `shadow-skill-cli.py:179` et
  `skills/shadow-skill/SKILL.md:75`.
- `skills/shadow-skill/scripts/tests/test_lire.py`, à côté de `test_chercher_ignore_les_accents` :
  un skill dont la description porte « This skill covers latest tests » ; « skill » et « test »
  le trouvent, « kill » et « atest » ne le trouvent pas. Les tests existants restent verts.
- vérif :
  `~/.claude/.venv/bin/python -m pytest skills/shadow-skill/scripts/tests/ && uvx rumdl fmt --check skills/shadow-skill/SKILL.md && grep -n "début de mot" skills/shadow-skill/SKILL.md skills/shadow-skill/scripts/shadow-skill-cli.py`

### 3. `lexique` sans `--projet` sous un HOME versionné par git

- D'abord, compléter le `## Constat` de la dette
  `.claude/implementation/todo/technical-debt/lexique-home-versionne-par-git.md` : le projet se
  résout une seule fois, à `lexique-cli.py:188`, pour toutes les sous-commandes à `--projet`. Donc
  `chemin`, `termes`, `definition` et `definitions`, appelées par Neovim, ont le même défaut que
  `liste` et `init`. Ajouter le constat sans réécrire l'existant. Vérif :
  `list-dir validate .claude/implementation/todo/technical-debt`.
- `skills/lexique/scripts/lexique.py`, `racine_projet` : prend en plus le chemin du lexique global.
  Si `chemin_local(racine git)` désigne ce même fichier (même comparaison que `_est_le_global`), il
  retombe sur `depart`. Réécrire la docstring : la raison actuelle (« la remontée trouverait le
  lexique GLOBAL ») décrit le défaut que l'on corrige. `lexique-cli.py:188` lui passe
  `chemin_global()`.
- `skills/lexique/SKILL.md:58-61` (« Sans `--projet`… ») : ajouter l'exception, quand la racine git
  est celle qui porte le lexique global.
- `skills/lexique/scripts/tests/test_projet.py` : un HOME git simulé. `tmp_path` est un dépôt git,
  `tmp_path/.claude/LEXIQUE.md` joue le global, et `tmp_path/proj/` n'est pas versionné. Alors
  `racine_projet(proj, global)` rend `proj`. Les trois tests existants restent verts, adaptés à la
  nouvelle signature.
- vérif :
  `~/.claude/.venv/bin/python -m pytest skills/lexique/scripts/tests/ && uvx rumdl fmt --check skills/lexique/SKILL.md`

### 4. Un changement, une ligne : libellé des valeurs multi-lignes

- `skills/list-dir/scripts/listdir/store.py` : une fonction `libelle(valeur) -> str`, placée à côté
  de `forme_texte`. Elle s'appuie sur `forme_texte`, rend la première ligne suivie de « … » quand la
  valeur a plusieurs lignes, et rend la valeur inchangée quand elle tient sur une ligne. Elle est
  appliquée aux trois libellés de `Change` qui interpolent une valeur : champ ajouté (`:339`),
  section ajoutée (`:376`, `corps` aujourd'hui brut) et `_poser` (`:529`, les deux valeurs).
  `forme_texte` ne change pas : elle sert aussi aux filtres (`:862`) et à `list`.
- Tests :
  - `tests/test_store_ecriture.py`, qui appelle déjà `migrate()` (Q9) : une section `text` sur
    plusieurs lignes donne un seul `Change`, dont le libellé ne contient pas de `\n` et finit par
    « … » ;
  - une section `command` qui imprime deux lignes, même attente ;
  - une valeur d'une ligne garde son libellé à l'identique ;
  - `tests/test_fill.py` : `fill --override` d'une valeur multi-lignes, même attente sur le libellé.
- vérif :
  `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_store_ecriture.py skills/list-dir/scripts/tests/test_fill.py`

### 5. `reseed` testé de bout en bout par la ligne de commande

- Déplacer `SEMENCE` et `semer` de `tests/test_reseed.py` vers `tests/jouet.py`. `test_reseed.py`
  les importe de là. `semer` garde son `os.chdir`, sur lequel comptent les tests de bibliothèque.
- `tests/test_entree_cli.py`, cinq tests par `lancer(..., cwd=tmp_path)`, dans une rubrique
  `reseed` :
  1. conflit : code non nul, contrat inchangé, rien dans `.list/backup/` ;
  2. `--force` sur une liste gelée : code 0 ;
  3. `--dry-run` : code 0, contrat inchangé, la sortie dit « seraient appliqués » ;
  4. nom discordant : une définition `autre`, montée au rang projet, dont le contrat déclare
     `origin.def = "jouet"`, puis `reseed --def autre`. Attendu : code 2. Sans cette définition,
     `resolve` échoue avant, avec le code 1 (Q3) ;
  5. une liste sans `origin.def`, ni `--def` ni `--from` : code 1, et le message
     « aucune semence à rattraper » sur stderr. C'est un refus que seule la commande porte. La
     liste vient de `monter_liste` de `jouet` : son `CONTRAT` déclare `[origin] def = false`, donc
     `origin.name` est vide (Q4).
- vérif :
  `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_entree_cli.py skills/list-dir/scripts/tests/test_reseed.py`

### 6. Les commandes de `bin/` supposent le `PATH` de la session

- `.claude/CLAUDE.md` : un paragraphe, placé dans « Outillage » ou en tête de « Neovim,
  visionneuse… ». Il dit que les commandes de `bin/` s'appellent par leur nom et supposent une
  session lancée depuis un shell dont le `PATH` porte `bin/`. Il dit aussi ce qui manque sans ce
  `PATH` : le lexique local que verse le mod `lexique` (l'échec ne se voit que sur la ligne d'état),
  et les commandes qu'appelle Neovim. Il renvoie à `OUTILLAGE.md` pour la ligne à ajouter au profil,
  sans la recopier.
- vérif : `grep -n "lexique local" .claude/CLAUDE.md && uvx rumdl fmt --check .claude/CLAUDE.md`
  (Q5 : un simple `PATH` figure déjà à la ligne 36)

### 7. Une conversation reprise garde son lexique local d'origine

- `skills/lexique/SKILL.md`, « Ce que reçoit la session » : un paragraphe. Il dit qu'une
  conversation reprise (`--resume`, `--continue`) réutilise le prompt système qu'elle a enregistré
  jusqu'à sa prochaine compaction, et donc garde le lexique local qu'elle avait à son début, ou
  son absence. Il donne le remède : `/compact` ou une nouvelle conversation.
- `shadow-skills/claude-code-mods/SKILL.md:85` : remplacer « survit à `/clear`, à `/compact` et à
  `--continue` » par une formulation qui ne promet pas de recomposition à la reprise, et renvoyer à
  la limite déjà écrite aux lignes 297-299.
- `skills/lexique/hooks/register.ts:30-31`, commentaire de `prompt.compose` : même correction pour
  « survit à la reprise ». Seul le commentaire change, pas le code.
- vérif :
  `npx --yes @biomejs/biome@2 format skills/lexique && claude plugin test skills/lexique && uvx rumdl fmt --check skills/lexique/SKILL.md shadow-skills/claude-code-mods/SKILL.md && python3 scripts/check_pipeline.py`

## Vérification de fin

```bash
~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/ \
  skills/lexique/scripts/tests/ skills/shadow-skill/scripts/tests/
uvx ruff check . && uvx ruff format --check .
uvx --with pytest basedpyright
uvx rumdl fmt --check .
python3 scripts/check_pipeline.py
```

Le nombre d'erreurs `basedpyright` se compare à celui de la Base, sur un arbre extrait
(`OUTILLAGE.md`), jamais par `git stash`.

## Hors-périmètre

- Chercher un événement de reprise qui recomposerait la section du lexique (dette 2) : l'entrée
  l'exclut.
- Le sous-agent chercheur de Shadow-skills (`sous-agent-chercheur-de-shadow-skills`) : c'est une
  autre entrée de road-map.
- Résoudre `lexique` sans le `PATH` de la session (l'autre voie de la dette 1) : l'entrée retient la
  documentation.
- Le message d'échec de `fill` (`store.py:505`), qui n'est pas un `Change`.
