---
slug: renvoi-contrat-des-categories
---

## 2026-08-30 — clôture — `1e7d6ef`

**Verdict** : RÉSERVES

### Vérifications exécutées

Toutes depuis la racine du dépôt, `list-dir` = `/home/debian/.claude/bin/list-dir`.

- `cd skills/list-dir/scripts && uvx --from pytest pytest tests/ -q` → **300 passés, 0 échec** (8,26 s)
- `uvx ruff check .` → `All checks passed!`
- `uvx ruff format --check .` → **4 fichiers seraient reformatés** : `tests/test_contract.py`,
  `tests/test_items.py`, `tests/test_loader.py`, `tests/test_move.py` — aucun n'est touché par le
  chantier (voir R4)
- `uvx pyright` → 4 erreurs, toutes `Import "pytest" could not be resolved`, préexistantes et
  conformes à ce que le suivi annonce
- `list-dir contract --def technical-debt --template review` → imprime `templates/review.toml` de la
  définition, commentaires compris, code 0
- `list-dir contract --from skills/implementation-tracker/list-dir/technical-debt --template review`
  → même contenu, code 0
- `list-dir contract .claude/implementation/todo/technical-debt --template review` → même contenu, code 0
- `list-dir contract --def technical-debt` et `list-dir contract <liste>` (sans `--template`) →
  le `contract.toml`, code 0
- `list-dir derive … "$T/revue" --template review` puis `list-dir contract "$T/revue" --values category`
  → `a-solder`, `non-pertinent`, `doublon`, `pas-une-dette`, `aggravee`, `pertinent`, `inverifiable`
  — sept lignes, ordre du contrat, code 0
- boucle des piles rejouée sur `"$T/revue"` → sept piles dans cet ordre, effectif 0 partout
  (revue non instruite)
- `grep -rn "a-solder non-pertinent" skills/debt-review/` → code 1, aucune sortie
- `grep -rn "sept\b" skills/debt-review/` → code 1, aucune sortie
- `diff skills/implementation-tracker/list-dir/technical-debt/templates/review.toml .claude/implementation/todo/technical-debt/.list/templates/review.toml` → identiques
- `list-dir validate .claude/implementation/todo/technical-debt --filled` → 29 éléments conformes, code 0
- `list-dir validate .claude/implementation/todo/technical-debt-solde --filled` → 16 éléments conformes, code 0
- `list-dir list …-solde | grep gabarit-rapport` → `gabarit-rapport-recopie-les-categories`
- `git log --follow` sur la fiche soldée → remonte à `d8a06ac` : le `move` a bien préservé l'historique
- commande « Pour solder » de la nouvelle entrée de dette (`diff <(--values category) <(grep -oP …)`)
  → code 0, sortie vide : le garde-fou est exécutable et ne signale rien aujourd'hui
- chemins d'échec de `contract`, exécutés un par un : aucune cible → code 2 ; `--def` + `--from` →
  code 2 (argparse) ; `<liste>` + `--def` → code 2 (argparse, le positionnel est bien dans le
  groupe) ; `--def` inconnu → code 1 avec « connues : … » ; `--template` inexistant → code 1 avec le
  chemin complet ; `--values` champ inconnu → code 1 avec les champs déclarés ; `--values` sur un
  champ sans `values` → code 1 avec le type ; contrat absent → code 1 avec le chemin attendu
- `list-dir help | grep contract` → `affiche un contrat : celui d'une liste, ou celui d'une définition`
- `grep -n "Ce que \`contract\` vise" skills/list-dir/references/contrat-liste.md` → l. 119

### Conformité à l'intention

- **Critère « `contract --def technical-debt --template review` imprime `templates/review.toml` ;
  `--from <chemin>` et `<liste réelle>` font de même »** : **atteint, vérifié**. Les trois cibles
  rendent le même texte, avec et sans `--template`, et l'exclusion mutuelle est réellement portée par
  argparse — y compris entre le positionnel et les options, ce qui n'allait pas de soi avec un
  `nargs="?"`.
- **Critère « `contract "$R" --values category` imprime les sept identifiants, un par ligne, dans
  l'ordre du contrat »** : **atteint, vérifié** sur une liste réellement dérivée, pas sur la semence.
  L'ordre rendu est bien l'ordre non alphabétique du fichier.
- **Critère « la boucle des piles n'énumère plus aucun identifiant »** : **atteint, vérifié**.
  `skills/debt-review/SKILL.md:276` tire sa liste de `--values category` ; `grep -rn "a-solder
  non-pertinent" skills/debt-review/` ne trouve plus rien. La prose voisine a suivi : elle dit
  désormais que l'ordre est celui du contrat et renvoie au commentaire qui le justifie.
- **Critère « `gabarit-rapport.md` ne recopie plus le compte “sept” : il renvoie à la commande »** :
  **atteint, vérifié**. Le renvoi vise la définition (`--def technical-debt --template review`),
  donc un fichier qui existe avant `derive` — c'est exactement le blocage que la fiche de dette
  invoquait pour reporter la correction, et il est levé. Aucun « sept » ne subsiste dans tout
  `skills/debt-review/`.
- **Critère « la suite `skills/list-dir/scripts/tests/` passe »** : **atteint, vérifié** — 300 tests,
  dont 18 ajoutés qui couvrent les trois cibles, `--template`, `--values`, et six chemins d'échec.
- **Hors-périmètre** : **respecté**. Le garde-fou sur `categories.md` n'a pas été construit ; il est
  porté au registre sous `sections-de-categories-jamais-confrontees-au-contrat`, avec une commande de
  solde que j'ai exécutée et qui fonctionne. La prose de `categories.md` n'est touchée qu'aux deux
  endroits où elle porte un **compte** (le titre, et « Aucune des sept ») — ce que le plan carve
  explicitement et que le suivi note comme ratifié par l'utilisateur.
- **Signaux de dérive** : **aucun matérialisé**. `contract` n'a gagné aucune capacité de tri, de
  filtre ni de jugement : `--values` rend `field.values` tel quel, le texte du contrat est rendu
  brut (seul le `\n` final est ôté, comme avant). La validation du contrat avant impression est
  conservée, elle n'est pas une nouveauté — elle a seulement changé de véhicule
  (`utils.open()` → `parse_contract`).
- **Symptôme d'origine** : **disparu**. Une huitième catégorie ajoutée à `review.toml` entre
  désormais seule dans la boucle des piles et dans ce que lit qui suit `gabarit-rapport.md`. Ce qui
  reste à recopier — les sections de `categories.md` — est nommé, tracé et outillé.

Point vérifié parce que le journal le signale : la phrase « jamais depuis une définition » est
toujours dans `contrat-liste.md` (coupée par un retour à la ligne, d'où le `grep -q` du plan qui ne
pouvait pas matcher). Elle n'est pas devenue fausse : elle décrit `contract_path`, fonction de
bibliothèque encore employée par `load_contract` et qui lit bien toujours `<liste>/.list/`. La
nouvelle section l. 119 lève l'ambiguïté sur la commande. Rien à reprocher ici.

### Qualité du code

- **R1** — `skills/debt-review/SKILL.md:276` — `for c in $(list-dir contract "$R" --values category)`
  ne contrôle pas le code de retour. Vérifié en le rejouant sur une liste inexistante : la commande
  échoue (code 1, message sur stderr), la substitution rend une chaîne vide, la boucle itère zéro
  fois et le bloc se termine à 0. Le tableau des piles est alors **vide**, ce qui se lit comme
  « aucune fiche » plutôt que comme « la liste n'a pas pu être lue ». La régression reste modeste —
  l'ancienne énumération en dur ne pouvait pas être vide, mais elle ne pouvait pas non plus être
  juste — et le message d'erreur est bien imprimé sur stderr, donc visible de qui exécute le bloc.
  Coût : un opérateur qui ne lit que la sortie standard conclut à un registre vide.
- **R2** — `listdir/contract.py:_liste` n'impose aucune contrainte de forme aux `values` d'un enum :
  ce sont des chaînes quelconques. Une valeur portant une espace serait donc découpée par le
  `$(...)` de la boucle des piles en deux pseudo-catégories, chacune comptée 0, sans qu'aucune
  commande n'échoue. `--values` fait le bon contrat de son côté (une valeur par ligne) ; c'est
  l'appelant shell qui suppose des valeurs sans blanc, et rien ne le garantit. Aucun critère ne
  demandait cette garantie — réserve, pas défaut. Le cas est hypothétique aujourd'hui : les sept
  valeurs sont en kebab-case, et le commentaire ajouté au contrat s'adresse justement à qui les
  édite (sans mentionner cette contrainte-là).
- **R3** — `listdir/commands/contract.py:_fichier` — `--template ../contract` sort de `templates/`
  (`base / "templates" / "../contract.toml"`). Sans conséquence ici : la commande est locale et en
  lecture seule. Mais l'aide et la doc annoncent « le `<nom>.toml` de `templates/` », et rien ne le
  fait respecter. Constat de cohérence, pas de sécurité.

Style : conforme au voisinage. Le `_ = groupe.add_argument(...)` sur les options du groupe mutuel et
le `parser.add_argument(...)` nu ailleurs reproduisent exactement `init.py` ; les `cast("str", …)`,
la densité des docstrings en capitales sur le pourquoi, et la forme des messages d'échec (« connues :
… », chemin complet en tête) suivent `definitions.resolve` et `ListStore.template` comme le plan
l'annonçait. Les tests ajoutés respectent le nommage et les docstrings-justification des voisins.

### Dette induite

- **R4** — `uvx ruff format --check .` échoue sur quatre fichiers de tests
  (`test_contract.py`, `test_items.py`, `test_loader.py`, `test_move.py`). **Aucun n'est touché par
  le chantier** : la dérive est antérieure (elle remonte à `cb16629`). Ce n'est donc pas un défaut à
  imputer ici, mais la « Vérification d'ensemble » du plan, qui inclut cette commande, ne peut pas
  passer telle qu'elle est écrite — et le suivi ne le mentionne pas. Coût futur : la commande de
  vérification globale du plan reste rouge, ce qui la rend inutilisable comme garde-fou tant que la
  cause préexistante n'est pas traitée.
- **R5** — la logique de résolution (`_base`, `_fichier`, `_valeurs`) vit dans le module de commande,
  pas dans la bibliothèque. `init.py` énonce la doctrine maison en tête de fichier : « AUCUNE LOGIQUE
  ICI […] c'est ce qui garantit qu'un script tiers et la ligne de commande font exactement la même
  chose ». Un script qui importerait `listdir` ne peut aujourd'hui obtenir ni la résolution
  liste-ou-définition ni les `values` d'un champ sans réécrire ces trois fonctions. À décharge :
  `defs.py`, `list.py` et `help.py` portent déjà des helpers privés, la commande n'est donc pas une
  exception isolée, et la logique en question est courte. Coût futur : le jour où une autre commande
  ou un script a besoin de viser « une liste ou une définition », la duplication se fera là.
- **R6** — le commentaire de doctrine sur l'ordre des `values` est écrit **deux fois**, dans les deux
  `review.toml`, et rien ne les confronte : `diff` est une vérification d'étape, pas un contrôle
  permanent. C'est la conséquence assumée du modèle « une liste amorcée est détachée de sa semence »,
  documenté comme tel, et le chantier n'a pas le choix — mais la divergence future ne fera échouer
  aucune commande. Même famille que la dette qui vient d'être ouverte, sans y être rattachée.

### Bloquants

Aucun.

---

## 2026-08-30 — clôture — `bd85bc7`

**Verdict** : DÉFAVORABLE

Deuxième passage. Le diff jugé est `master...renvoi-contrat-des-categories` **en entier**, pas le
seul correctif `bd85bc7`. Les constats R1 à R6 du passage précédent sont repris en tête pour dire
leur état réel, mesuré ; les constats nouveaux sont numérotés à partir de R7.

### Vérifications exécutées

Depuis la racine du dépôt, `list-dir` = `/home/debian/.claude/bin/list-dir`. Suite et linters par
`uvx` (ni `python` ni `pytest` dans le `PATH`).

- `cd skills/list-dir/scripts && uvx --from pytest pytest tests/ -q` → **303 passés, 0 échec** (8,77 s)
- `uvx ruff check .` → `All checks passed!`
- `uvx ruff format --check .` → **4 fichiers seraient reformatés** : `tests/test_contract.py`,
  `tests/test_items.py`, `tests/test_loader.py`, `tests/test_move.py` (voir R4, corrigé)
- `uvx pyright` → 4 erreurs, toutes `Import "pytest" could not be resolved`, préexistantes
- `list-dir contract --def technical-debt --template review`, `--from skills/…/technical-debt
  --template review`, `.claude/implementation/todo/technical-debt --template review` → **même
  contenu au md5** (`0308988667db…`), code 0 dans les trois cas
- `list-dir contract --def technical-debt` (sans `--template`) → `contract.toml`, code 0
- `list-dir contract --def technical-debt --template review --values category` → les sept
  identifiants, ordre du contrat, code 0
- `derive` dans un `mktemp -d`, puis le bloc de `debt-review/SKILL.md:275-280` **rejoué tel quel
  sous zsh** → sept piles, ordre du contrat, effectif 0 partout (revue non instruite)
- même bloc sur une liste inexistante, **sous zsh** → `contrat introuvable` sur stderr, puis
  `ÉCHEC : contrat illisible`, **code 1**
- `grep -rn "a-solder non-pertinent" skills/debt-review/` → code 1, aucune sortie
- **`grep -rn "sept\b" skills/debt-review/` → code 0, une occurrence : `SKILL.md:289`** (voir R7)
- chemins d'échec de `contract` : aucune cible → 2 ; `--def`+`--from` → 2 ; `<liste>`+`--def` → 2 ;
  `--def` inconnu → 1 avec « connues : … » ; `--template inexistant` → 1 avec le chemin complet ;
  `--template ../contract`, `--template templates/review`, `--template .` → **1 avec « un nom est
  attendu, pas un chemin »** ; `--values` champ inconnu → 1 avec les champs déclarés ; liste
  inexistante → 1
- `diff` des deux `review.toml` → identiques
- `list-dir validate` sur les trois registres réels (`technical-debt`, `-solde`, `-ecarte`)
  `--filled` → 29, 16 et 2 éléments conformes, code 0 partout
- `list-dir contract --def` sur les trois définitions → code 0 (la nouvelle contrainte sur `values`
  ne casse aucun contrat du dépôt)
- commande « Pour solder » de la nouvelle entrée de dette → code 0, sortie vide
- `git log --follow` sur la fiche soldée → remonte à `d8a06ac`
- `list-dir help | grep contract` → description à jour ; `grep -n "Ce que \`contract\` vise"
  contrat-liste.md` → l. 119 ; `grep -c -- "--def\|--from\|--template" skills/list-dir/SKILL.md` → 8

### État des constats du passage précédent

- **R1 — clos, vérifié.** Le bloc passe par une affectation testée puis `printf | while read -r`.
  Rejoué sous zsh : sept itérations sur le cas nominal, **code 1 et message** sur le cas en échec.
  Le mode de défaillance est de plus écrit à côté du bloc.
- **R2 — clos, vérifié.** `parse_contract` refuse une `values` vide ou porteuse d'un blanc, avec
  deux tests dédiés. Voir cependant R8 : la règle n'est écrite nulle part dans la spécification.
- **R3 — clos, vérifié.** `source_path` refuse tout `--template` qui n'est pas un nom nu ; les
  trois formes hostiles essayées sont rejetées code 1.
- **R4 — toujours ouverte, et le constat précédent était inexact.** `uvx ruff format --check .`
  échoue encore sur quatre fichiers. Le rapport précédent affirmait qu'« aucun n'est touché par le
  chantier » : **`tests/test_contract.py` l'est** (17 lignes ajoutées). Vérifié ligne à ligne : les
  quatre hunks que `ruff format` réclame portent tous sur des lignes **antérieures** au chantier,
  les lignes ajoutées ici sont propres. La conclusion tient donc — dérive préexistante — mais la
  « Vérification d'ensemble » du plan reste rouge, et le suivi ne le mentionne toujours pas.
- **R5 — close pour l'essentiel.** `list_base`, `source_path`, `load_source` et `field_values`
  vivent désormais dans `listdir/contract.py` ; un script tiers obtient la lecture validée et les
  `values` sans réécrire quoi que ce soit. Reste `_base` dans le module de commande, qui traduit
  les trois formes d'argparse en une base — c'est un aiguillage d'arguments, sa place y est
  défendable et la docstring le dit. Résiduel : un script tiers qui veut viser « une liste ou une
  définition » à partir des mêmes trois entrées refait cet aiguillage.
- **R6 — toujours ouverte, par décision.** Le commentaire de doctrine est écrit dans les deux
  `review.toml` et rien ne les confronte en permanence.

### Conformité à l'intention

- **Critère « les trois cibles impriment `templates/review.toml` »** : **atteint, vérifié** — même
  md5 dans les trois cas, exclusion mutuelle réellement portée par argparse (code 2), y compris
  entre le positionnel et les options.
- **Critère « `--values category` imprime les sept identifiants, un par ligne, dans l'ordre du
  contrat »** : **atteint, vérifié** sur une liste réellement dérivée comme sur la définition.
- **Critère « la boucle des piles n'énumère plus aucun identifiant »** : **atteint, vérifié**.
  Aucune énumération en dur ne subsiste, et la boucle corrigée tourne juste sous zsh comme sous
  bash.
- **Critère « `gabarit-rapport.md` ne recopie plus le compte “sept” : il renvoie à la commande »** :
  **atteint** pour `gabarit-rapport.md` lui-même — le renvoi vise la définition, donc un fichier
  qui existe avant `derive`. Mais la forme mécanique que le plan et le suivi donnent à ce critère
  (« plus aucun “sept” ne subsiste dans `skills/debt-review/` ») est **redevenue fausse** : voir R7.
- **Critère « la suite `skills/list-dir/scripts/tests/` passe »** : **atteint, vérifié** — 303
  tests, dont 21 ajoutés par le chantier.
- **Hors-périmètre** : **respecté**. Le garde-fou sur `categories.md` n'est pas construit ; il est
  porté au registre sous `sections-de-categories-jamais-confrontees-au-contrat`, avec une commande
  de solde que j'ai exécutée (code 0, sortie vide). `categories.md` n'est touchée qu'aux deux
  endroits qui portent un **compte**.
- **Signaux de dérive** : **aucun matérialisé**. `contract` ne trie, ne filtre ni ne juge :
  `field_values` rend `field.values` tel quel et sa docstring en fait une garantie explicite.
- **Symptôme d'origine** : **disparu**. Une huitième catégorie ajoutée à `review.toml` entre seule
  dans la boucle des piles et dans ce que lit qui suit `gabarit-rapport.md`. Elle laisserait en
  revanche `SKILL.md:289` parler de « sept » (R7) et `categories.md` en décrire une de moins —
  ce dernier point est nommé, tracé et outillé.

### Constats nouveaux

- **R7 — bloquant** — `skills/debt-review/SKILL.md:289` — le correctif de R1 a **réintroduit le
  mot « sept »** dans `skills/debt-review/`, dans la note qui justifie le `while read` : « la
  boucle y tournait **une fois** sur les sept catégories collées ». Conséquences mesurées :
  1. la vérification de l'étape 6, telle qu'elle est écrite dans le suivi
     (`grep -rn "sept" skills/debt-review/ && echo ÉCHEC`), **imprime désormais ÉCHEC** — je l'ai
     exécutée, code 0, une occurrence ;
  2. le suivi, l. 89-90, affirme que ce `grep` « sort muet ». Cette affirmation est **fausse au
     commit audité** : elle date d'avant le correctif et n'a pas été rejouée après lui.
  `git log -S` confirme que l'occurrence entre en `bd85bc7`, c'est-à-dire dans le commit qui
  répondait à l'audit. Le fond est vénielle — la phrase relate une mesure passée, elle ne prescrit
  rien — mais elle est exactement du genre que le chantier existe pour supprimer : un lecteur qui
  ajoute une huitième catégorie lit « sept » à deux lignes de la boucle qui, elle, ne recopie plus
  rien. Correction attendue : ôter le compte de la phrase, et rejouer la vérification de l'étape 6.
- **R8** — `skills/list-dir/references/contrat-liste.md:202` — la nouvelle règle « une `values` ne
  peut être ni vide ni porteuse d'un blanc » est **appliquée par le parseur mais absente de la
  spécification**. Le fichier qui décrit le langage de contrat se contente de « `enum` (avec
  `values`) ». Or c'est un **durcissement rétroactif** : il vaut pour toutes les listes, pas
  seulement pour la revue de dette, et une liste tierce déclarant `values = ["à traiter"]` verrait
  désormais **toutes** ses commandes échouer (`validate`, `new`, `show`, `migrate`), pas seulement
  `--values`. Vérifié : aucun contrat du dépôt n'est concerné, les trois définitions et les trois
  registres passent. Coût futur : la règle ne se découvre qu'en la violant, et le message d'échec
  est le seul endroit où elle est écrite.
- **R9** — `skills/list-dir/references/contrat-liste.md:138` — la référence continue de présenter
  `for c in $(list-dir contract … --values category)` comme la forme d'emploi prévue, alors que
  `debt-review/SKILL.md:283-286` documente désormais ce même motif comme un mode de défaillance
  (code de retour avalé, et découpage absent sous zsh). Deux fichiers du même dépôt donnent
  l'exemple contraire l'un de l'autre. Même motif dans la docstring de
  `listdir/commands/contract.py` — atténué là par l'avertissement qui suit immédiatement — et dans
  la docstring du test `test_contract_values_rend_une_valeur_par_ligne` (« c'est elle qui rend
  `for c in $(...)` sûr »), sans avertissement. Coût futur : le prochain appelant copie l'exemple
  de la référence et retombe dans R1.
- **R10** — `skills/debt-review/SKILL.md:277` — le bloc corrigé contient `exit 1`. Collé dans un
  shell interactif — ce que la procédure demande de faire des blocs de ce skill — il **ferme la
  session** au lieu d'afficher une erreur. L'idiome a un précédent maison
  (`implementation-tracker/references/cloture.md:131,137`), il n'est donc pas hors style ; c'est un
  inconfort connu, pas un défaut de correction. Signalé pour que le choix soit conscient.

### Qualité du code

`listdir/contract.py` : la nouvelle bibliothèque est cohérente avec le voisinage — `Result` propagé
sans exception, échecs nommés avec le chemin complet en tête, docstrings en capitales sur le
pourquoi. `load_source` rendant le triplet `(chemin, texte, contrat)` est justifié dans sa
docstring et évite un second parsage ; le contrat reste jugé avant d'être imprimé, comme avant.
`source_path` fait respecter « un nom, pas un chemin » à un seul endroit, ce qui est le bon.

`listdir/commands/contract.py` : le module est redevenu ce que la doctrine maison demande — un
`register()`, un aiguillage d'arguments, des appels de bibliothèque. Le `_ = groupe.add_argument`
sur les membres du groupe mutuel et le `parser.add_argument` nu ailleurs reproduisent `init.py`.

Tests : 21 ajoutés, nommage et docstrings-justification conformes aux voisins ; les chemins
d'échec sont couverts un par un, y compris les deux nouveaux (valeur à blanc, gabarit-chemin).
Les lignes ajoutées passent `ruff format` — la dérive de format est ailleurs (R4).

### Dette induite

Outre R4, R6, R8 et le résiduel de R5 ci-dessus, rien de nouveau : le chantier a **retiré** de la
duplication (quatre recopies de la liste des catégories) sans en introduire, et a factorisé la
résolution de contrat au lieu de la laisser dans une commande.

### Bloquants

- **R7** — le mot « sept » est revenu dans `skills/debt-review/` par le correctif d'audit, la
  vérification de l'étape 6 est en échec au commit audité, et le suivi la déclare passante.

---

## 2026-08-30 — clôture — `f7c15b9`

**Verdict** : RÉSERVES

Troisième passage. Le diff jugé est `master...renvoi-contrat-des-categories` **en entier**
(8 commits, 18 fichiers), pas le seul correctif `f7c15b9`. R1 à R10 sont repris pour dire leur état
réel, mesuré au commit audité ; les constats nouveaux sont numérotés à partir de R11.

### Vérifications exécutées

Depuis la racine du dépôt, `list-dir` = `/home/debian/.claude/bin/list-dir`. Suite et linters par
`uvx` (ni `python` ni `pytest` dans le `PATH`).

- `cd skills/list-dir/scripts && uvx --from pytest pytest tests/ -q` → **303 passés, 0 échec** (7,62 s)
- `uvx ruff check .` → `All checks passed!`
- `uvx ruff format --check .` → **4 fichiers seraient reformatés** (voir R4)
- `uvx pyright` → 4 erreurs, toutes `Import "pytest" could not be resolved`, préexistantes
- les trois cibles avec `--template review` → **même md5** (`0308988667db3192142f1c1a4bf106f4`),
  code 0 dans les trois cas
- `list-dir contract --def technical-debt` (sans `--template`) → `contract.toml`, code 0
- `list-dir contract --def technical-debt --template review --values category` → les sept
  identifiants, ordre du contrat, code 0
- `derive` dans un `mktemp -d`, puis `--values category` sur la liste dérivée → mêmes sept, même ordre
- **bloc de `debt-review/SKILL.md:275-282` rejoué tel quel sous zsh** → sept piles, ordre du
  contrat, effectif 0 partout, code 0
- même bloc sur une liste inexistante, sous zsh → `contrat introuvable` sur stderr, puis
  `ÉCHEC : contrat illisible`, **code 1**, session non tuée (plus d'`exit`)
- **`grep -rn "sept" skills/debt-review/` → code 1, aucune sortie** (R7 clos)
- `grep -rn "a-solder non-pertinent" skills/debt-review/` → code 1, aucune sortie
- chemins d'échec de `contract`, un par un : aucune cible → 2 ; `--def`+`--from` → 2 ;
  `<liste>`+`--def` → 2 ; `--template` seul sans cible → 2 ; `--def` inconnu → 1 avec
  « connues : … » ; `--template nawak` → 1 avec le chemin complet ; `--template` valant
  `../contract`, `templates/review`, `.` ou `..` → 1 avec « un nom est attendu, pas un chemin » ;
  `--values nawak` → 1 avec les champs déclarés ; `--values title` → 1 avec le type
- `diff` des deux `review.toml` → identiques
- `list-dir contract --def` sur les trois définitions → code 0 (la contrainte sur `values` ne casse
  aucun contrat du dépôt)
- `list-dir validate --filled` sur les trois registres → 29, 16 et 2 éléments conformes, code 0
- commande « Pour solder » de `sections-de-categories-jamais-confrontees-au-contrat` → code 0,
  sortie vide
- `git log --follow` sur la fiche soldée → remonte à `d8a06ac`
- `list-dir help | grep contract` → description à jour ;
  `grep -c -- "--def\|--from\|--template" skills/list-dir/SKILL.md` → 8 ;
  `grep -n "Ce que \`contract\` vise" contrat-liste.md` → l. 119
- `git status --short` → arbre propre au commit audité

### État des constats antérieurs

- **R1, R2, R3 — clos, revérifiés.** Bloc à affectation testée (code 1 sur l'échec, sous zsh) ;
  `values` vide ou porteuse d'un blanc refusée par `parse_contract`, deux tests dédiés ;
  `source_path` rejette les quatre formes de `--template` hostiles essayées.
- **R4 — toujours ouverte, mais déjà tracée ailleurs.** `uvx ruff format --check .` échoue encore
  sur quatre fichiers. Revérifié hunk par hunk sur `tests/test_contract.py`, le seul fichier
  concerné que le chantier touche : les trois hunks réclamés portent sur les l. 49-65, 120-125 et
  151, toutes antérieures ; les 17 lignes ajoutées ici (l. 97-114) sont propres. **Point que le
  suivi ne dit pas** : cette dérive fait déjà l'objet de l'entrée active
  `ruff-format-jamais-applique` (ouverte par le chantier `semences-de-listes`, présente sur
  `master`). R4 n'a donc pas besoin d'une entrée nouvelle — elle en a une.
- **R5 — close pour l'essentiel.** `list_base`, `source_path`, `load_source`, `field_values` vivent
  dans `listdir/contract.py`. Résiduel inchangé : `_base` traduit les trois formes d'argparse en une
  base, dans le module de commande ; sa docstring l'assume comme le seul aiguillage du module.
- **R6 — toujours ouverte, par décision.** Voir R12 pour son état au registre.
- **R7 — clos, vérifié.** `grep -rn "sept" skills/debt-review/` rend code 1 et aucune sortie au
  commit audité. La phrase de `SKILL.md` dit désormais « une seule fois, sur toutes les catégories
  collées en une chaîne » : le compte est parti sans que la mesure relatée soit perdue. La
  vérification de l'étape 6 telle qu'écrite dans le suivi passe donc réellement, et je l'ai jouée.
- **R8 — clos.** `contrat-liste.md:219` porte désormais « Une valeur de `values` est un jeton : ni
  vide, ni porteuse d'espace », avec le mode de défaillance à côté. La règle est écrite dans le
  fichier qui décrit le langage de contrat, plus seulement dans le message d'échec.
- **R9 — clos pour l'essentiel, un résidu.** `contrat-liste.md:138` ne donne plus
  `for c in $(...)` comme forme d'emploi : elle le présente comme l'échec à éviter et donne le bloc
  correct. La docstring de `commands/contract.py` renvoie à cette forme. Résidu : voir R11.
- **R10 — clos.** L'`exit 1` a disparu du bloc de `SKILL.md`, remplacé par `if … ; false`, et le
  choix est justifié à côté (« ces blocs se collent dans un shell interactif »). Rejoué sous zsh :
  code 1 rendu, shell survivant.

### Conformité à l'intention

- **Critère « `--def`, `--from` et `<liste réelle>` impriment `templates/review.toml` »** :
  **atteint, vérifié** — md5 identique dans les trois cas, exclusion mutuelle réellement portée par
  argparse (code 2), y compris entre le positionnel et les options.
- **Critère « `--values category` imprime les sept identifiants, un par ligne, dans l'ordre du
  contrat »** : **atteint, vérifié** sur la définition comme sur une liste réellement dérivée.
- **Critère « la boucle des piles n'énumère plus aucun identifiant »** : **atteint, vérifié**.
  Aucune énumération en dur ne subsiste dans `skills/debt-review/` ; le bloc tourne juste sous zsh
  et rend un code non nul quand le contrat est illisible.
- **Critère « `gabarit-rapport.md` ne recopie plus le compte “sept” : il renvoie à la commande »** :
  **atteint, vérifié**, y compris dans sa forme mécanique — `grep -rn "sept" skills/debt-review/`
  est muet, ce qui n'était pas le cas au passage précédent. Le renvoi vise la définition, donc un
  fichier qui existe avant `derive` : c'est exactement le blocage que la fiche de dette invoquait.
- **Critère « la suite `skills/list-dir/scripts/tests/` passe »** : **atteint, vérifié** — 303
  tests, dont 21 ajoutés par le chantier.
- **Hors-périmètre** : **respecté**. Le garde-fou sur `categories.md` n'est pas construit ; il est
  porté au registre sous `sections-de-categories-jamais-confrontees-au-contrat`, dont j'ai exécuté
  la commande « Pour solder » (code 0, sortie vide : le garde-fou est exécutable et ne signale rien
  aujourd'hui). `categories.md` n'est touchée qu'aux deux endroits qui portent un **compte**.
- **Signaux de dérive** : **aucun matérialisé**. `contract` ne trie, ne filtre ni ne juge :
  `field_values` rend `field.values` tel quel et sa docstring en fait une garantie ; le texte du
  contrat sort brut, commentaires compris.
- **Symptôme d'origine** : **disparu**. Une huitième catégorie ajoutée à `review.toml` entre seule
  dans la boucle des piles et dans ce que lit qui suit `gabarit-rapport.md`. Le seul reste — les
  sections de `categories.md` — est nommé, tracé, outillé.

### Constats nouveaux

- **R11 — résidu de R9** — `skills/list-dir/scripts/tests/test_entree_cli.py:539` — la docstring de
  `test_contract_values_rend_une_valeur_par_ligne` dit toujours « c'est elle qui rend
  `for c in $(...)` sûr », sans l'avertissement que le correctif a ajouté partout ailleurs. C'est
  désormais la **seule** occurrence du dépôt qui présente ce motif comme sûr, alors que trois
  fichiers voisins le documentent comme un mode de défaillance. Le test lui-même est juste ; c'est
  sa justification qui contredit la doctrine que le chantier vient d'établir. Coût futur : faible,
  mais c'est la ligne qu'un lecteur du test prendra pour la doctrine.
- **R12** — le suivi annonce que R4 et R6 « iront au registre de dette » à la clôture. Au commit
  audité, **ni l'une ni l'autre n'y est** sous une entrée propre. Pour R4, ce n'est pas nécessaire :
  `ruff-format-jamais-applique` la couvre déjà (constat vérifié en lisant l'entrée). Pour **R6** —
  le commentaire de doctrine écrit dans les deux `review.toml` sans que rien ne les confronte — il
  n'existe aucune entrée : `verification-derive-inoperante-sur-liste-amorcee`, la plus proche par le
  sujet, traite d'autre chose. Le registre actif compte 29 entrées, dont la seule ouverte par ce
  chantier. Ce n'est pas un défaut du code produit, c'est un geste de clôture non encore posé —
  signalé pour qu'il ne se perde pas entre l'audit et la fermeture.

### Qualité du code

Rien à reprendre depuis le passage précédent. `listdir/contract.py` propage par `Result` sans
exception, nomme ses échecs avec le chemin complet en tête, et documente le pourquoi en capitales
comme ses voisins. `load_source` rendant `(chemin, texte, contrat)` est justifié dans sa docstring
et évite un second parsage avec un chemin potentiellement divergent dans les messages.
`source_path` fait respecter « un nom, pas un chemin » à un seul endroit.
`listdir/commands/contract.py` est réduit à un `register()`, un aiguillage et des appels de
bibliothèque, conformément à la doctrine qu'`init.py` énonce ; le `_ = groupe.add_argument` sur les
membres du groupe mutuel et le `parser.add_argument` nu ailleurs reproduisent `init.py` à
l'identique.

Une régression de message a été cherchée et non trouvée : le passage de `utils.open()` à
`parse_contract` conserve la validation avant impression, et un répertoire sans `.list/` échoue
toujours code 1, désormais avec le chemin de `contract.toml` attendu — plus précis qu'avant.

Tests : 21 ajoutés, nommage et docstrings-justification conformes aux voisins, chemins d'échec
couverts un par un. Les lignes ajoutées passent `ruff format`.

### Dette induite

Outre R4 (déjà tracée), R6 (ouverte par décision, voir R12) et le résiduel de R5, **rien de
nouveau**. Le chantier a retiré quatre recopies de la liste des catégories sans en introduire, et a
factorisé la résolution de contrat au lieu de la laisser dans une commande.

### Bloquants

Aucun.
