---
slug: registre-de-dette-severite-chantier-pin
---

## 2026-10-08 — clôture — `a051cc7`

**Verdict** : RÉSERVES

Brief présent et lu ; le Suivi, le Plan (`.claude/plans/twinkly-stirring-moler.md`) et le diff
`master...registre-de-dette-severite-chantier-pin` (176 fichiers) ont servi de référence. L'arbre de
travail porte deux modifications non commitées : la coche de l'Étape 12 dans le Suivi, et
`settings.json`, hors Chantier et absent du diff. Selon la consigne de l'utilisateur, le contenu des
entrées de dette (titres, sections) n'a pas été lu. Seuls ont été examinés la structure, les champs
migrés et des comparaisons calculées qui ne montrent pas le texte.

### Vérifications exécutées

`$T` = `.claude/implementation/todo`. La Base a été extraite par `git archive master` dans un
répertoire temporaire.

- `list-dir contract "$T/technical-debt" --values severite` → `inconnue`, `note`,
  `avertissement`, `majeur`, `critique`, dans cet ordre, rc 0.
- `list-dir contract --def technical-debt --patron review --values severite` → même sortie, rc 0.
- `list-dir validate "$T/technical-debt" --filled` → rc 0, « 90 élément(s) remplis et conformes ».
  Stderr : 90 lignes, toutes « champ « source » — déprécié ». Aucune note sur l'ancien Marqueur, ni
  de péremption.
- `list-dir validate "$T/technical-debt-solde" --filled` → rc 0, 44 éléments, stderr vide.
- `list-dir validate "$T/technical-debt-ecarte" --filled` → rc 0, 5 éléments, stderr vide.
- Pour comparaison, même `validate` sur la Base extraite : « contrat périmé », qui nomme
  `technical-debt/migrations/3.md`, et les notes « ancien marqueur « <OPTIONNEL> » » sur `reviewed`
  dans les trois listes. Le Chantier les a fait disparaître.
- `list-dir list "$T/technical-debt" --sort=-severite` → 1 critique, 4 majeur, 8 avertissement,
  5 note, 72 inconnue, dans cet ordre (`inconnue` en dernier, comme le contrat le documente).
- `list-dir list "$T/technical-debt" --sort chantier` → 31 groupes contigus, dont « Hors chantier »
  (3 entrées).
- `list-dir list "$T/technical-debt" --sort date` → de 2026-08-14 à 2026-10-07, `sort -c`
  confirme l'ordre.
- `list-dir list "$T/technical-debt" --where pin=true` → 17 entrées, autant que
  `grep -l '^pin = true'`.
- `list-dir new technical-debt entree-de-test-audit`, dans une copie temporaire → `pin = false`,
  `severite = "<À REMPLIR>"`, `chantier` et `reference` au Marqueur, pas de `source`. `validate`
  passe (91 conformes).
- Chaque `chantier` des 90 entrées confronté aux slugs de `done/` (nom d'archive, préfixe daté
  retiré) → 0 absent.
- Règle 1-2 de la consigne de `chantier`, rejouée par script sur le champ `source` de chaque entrée
  → 0 écart sur 90.
- `source` intact : `git diff master...HEAD` sur les entrées de `technical-debt` → aucune ligne
  `-source` ni `+source`.
- `list-dir contract` de `-solde` et de `-ecarte` (lu par `tomllib`) → `source`, `severite`,
  `chantier`, `pin` et `reference` en `required = false`, sans `text` ni `deprecated`.
- Les contrats locaux des trois listes sont identiques à leur définition (`diff`).
- `list-dir derive "$T/technical-debt" <tmp>/revue --patron review` → rc 0. `validate` de la dérivée
  → « 90 élément(s) conformes ». `severite` y est reportée (même répartition), aucun `pin`.
- `rg -n "pin" skills/debt-review` → 2 lignes, toutes deux « ignoré ».
- `rg -n "inconnue" skills/debt-review` → la revue remplace « toujours » `inconnue`.
- `grep -c "contrat.md" agents/migrateur-de-liste.md` → 0.
- `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/` → 642 passés.
- `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/` → 145 passés. `prefill.py` est
  modifié par le Chantier, mais cette suite n'était dans aucune vérification d'Étape.
- `~/.claude/.venv/bin/python scripts/check_pipeline.py` → rc 0, « Pipeline conforme ».
- `uvx ruff check .` → **rc 1**, 2 × E501 dans `skills/list-dir/scripts/tests/test_fusion.py`
  (lignes 268 et 295). Même sortie sur la Base extraite (R3).
- `uvx ruff format --check .` → rc 0, 105 fichiers déjà formatés.
- `uvx --with pytest basedpyright` → **rc 1**. Hors `skills/synced/` (ignoré par git), le compte par
  fichier est identique à celui de la Base. Seule différence : 52 erreurs de
  `gabarit/items.py`, présentes sur la Base extraite seulement. Aucune erreur neuve (R3).
- `uvx rumdl fmt --check .` → **rc 1**. Le Brief, le Suivi et le Plan du Chantier s'ajoutent aux
  6 fichiers déjà signalés sur la Base (R4).
- Garde de `technical-debt/migrations/3.md`, avec `STRUCTURE = 98f43e0` (E10) → **rc 1**,
  « ligne hors des champs migrés : `severite`, `pin` » (R2).
- À la place, diff `98f43e0..a051cc7` des entrées de `technical-debt` → 430 lignes, toutes
  `chantier`, `reference`, `severite` ou `pin` (90/90/18/17 paires) : 0 ligne d'un autre champ ou
  d'une section.
- Transcriptions des sous-agents de la session → 3 lancements de `migrateur-de-liste`
  (`claude-haiku-5-5`), chacun « POSÉS : 60 » (180 valeurs). Aucun appel à `Edit` ou `Write`.
- `git -C ~/.config/nvim log -- plugins/listdir` → dernier commit le 2026-10-03, avant le Chantier.
  `find -newermt 2026-10-07` → rien.

### Conformité à l'intention

- Critère « `--values severite` dans l'ordre » : atteint, vérifié.
- Critère « `validate --filled` passe sur les trois listes, sans note sur l'ancien Marqueur,
  `source` signalé `deprecated` » : atteint, vérifié. L'avertissement porte sur les 90 entrées de
  `technical-debt`, et sur aucune de `-solde` ni de `-ecarte`, où `source` n'est pas déprécié
  (décision du journal du 2026-10-07).
- Critère « `--sort=-severite`, `--sort chantier`, `--sort date` » : atteint, vérifié.
- Critère « `--where pin=true` ; une entrée neuve porte `pin = false` » : atteint, vérifié.
- Critère « `severite`, `chantier` (slug de `done/` ou « Hors chantier ») ; `source` garde son
  texte » : atteint, vérifié.
- Critère « contrat de `-solde` et `-ecarte` : cinq champs facultatifs » : atteint, vérifié.
- Critère « agent sous `agents/`, `chantier` et `reference` remplis par lui » : atteint, vérifié par
  les transcriptions. Le Suivi indique deux `reference` corrigées à la main après confrontation du
  rapport, comme le prévoit le geste 6 de la procédure. Les valeurs de l'agent ne sont plus
  isolables dans un commit, car E11 mêle sa sortie aux annotations de l'utilisateur (R2).
- Critère « `review.toml` porte `severite` et pas `pin` ; `debt-review` documente `inconnue` et
  `pin` » : atteint, vérifié (`review.toml` v2, `SKILL.md` Phase 2 points 4-5 et Phase 5,
  `gabarit-rapport.md`, `exemple-revue.md`).
- Hors-périmètre :
  - Neovim : intact.
  - Relecture de fond des entrées : aucune, le texte des sections est inchangé.
  - Règles de sortie de `/debt-review` : seules s'ajoutent l'écriture de `severite` et
    l'ignorance de `pin`.
  - Entrées de `-solde` et `-ecarte` : non traitées, aucun des champs neufs n'y est rempli.
    `migrate` y a pourtant réordonné des sections (R1).
- Signaux de dérive : aucun matérialisé.
  - `chantier` : toujours un slug de `done/` ou « Hors chantier ».
  - `pin` : ne protège rien, ignoré explicitement par la revue.
  - Neovim : non modifié.
  - « Contenu changé au-delà des champs migrés » : texte des sections inchangé partout, mais
    `migrate` a posé des Marqueurs hors des champs migrés (R1). Je ne le compte pas comme
    matérialisé, et j'explique pourquoi en R1.
- Symptôme d'origine : disparu. Le registre se trie par chantier, par date et par sévérité, et
  s'épingle. 72 entrées sur 90 restent à `inconnue`, comme le Brief l'a décidé : `/debt-review` les
  jugera.

**R1 — `migrate` a touché des entrées au-delà des champs du Chantier, sans que ce soit dit.** La
comparaison Base → HEAD, texte des sections normalisé et non affiché, donne ceci :

- dans `technical-debt` :
  - 22 entrées ont reçu une section vide `## Assumé` avec `<OPTIONNEL>` ;
  - 19 entrées ont reçu `category = "<OPTIONNEL>"` ;
  - 39 `reviewed = "<OPTIONNEL>"` sont devenus `"<OPTIONNEL date>"` (ce que le deuxième critère
    exige) ;
- dans `technical-debt-solde` : 15 entrées ont leurs sections réordonnées, et 7 ont reçu
  `## Assumé`.

Le corps de chaque section existante est identique, à l'octet près une fois les espaces
normalisés. Je ne retiens pas le Signal de dérive « contenu changé au-delà des champs migrés », pour
trois raisons :

- rien de ce qui est écrit n'a changé ;
- seuls des Marqueurs ont été posés, et des sections déplacées ;
- le Brief impose `reseed` puis `migrate`, dont c'est le comportement.

En revanche, ni le Suivi ni `technical-debt/migrations/3.md` ne le disent. Le geste 3 annonce
seulement « `pin` à `false` et les trois autres champs au Marqueur ». La garde ne le voit pas
davantage : elle part du commit de structure. Un autre projet qui suit la note découvrira ces
changements dans son diff sans explication.

### Qualité du code

`fill` (`commands/fill.py`, `ListStore.fill`) est propre :

- la valeur est contrôlée avant toute écriture, par la conversion partagée `typed_value` ;
- un Marqueur et un champ déprécié sont refusés ;
- avec `--id`, un champ déjà rempli ou absent fait échouer l'appel ;
- `--id` et `--all` sont exclusifs et l'un des deux est exigé ;
- 18 tests unitaires et 4 tests CLI couvrent ces cas.

Le style suit les fichiers voisins : `_ = cible.add_argument` comme dans `contract.py`,
commentaires en capitales qui disent pourquoi. La péremption qui nomme les notes de migration
(`provenance._peremption`) a deux tests.

**R2 — La garde de la migration ne se rejoue plus sur HEAD.** La vérification de l'Étape 11 (« la
garde de `migrations/3.md` sort 0 ») échoue aujourd'hui, parce que les annotations de l'utilisateur
(18 `severite`, 17 `pin`) sont dans le même commit E11 que la sortie de l'agent. La garde n'admet
que des lignes `chantier` et `reference`. Le Suivi le dit (« la garde, passée avant, ne passe plus
»). J'ai remplacé la garde par un diff filtré sur les quatre champs : aucune autre ligne.
Conséquence : le Chantier ne conserve aucune trace rejouable de ce que l'agent seul a écrit. La note
de migration gagnerait à dire que la garde ne vaut qu'avant toute autre retouche des entrées.

**R3 — Deux commandes de l'Étape 12 sortent en échec, sans régression.** `ruff check .` (2 × E501
dans `test_fusion.py`) et `basedpyright` rendent les mêmes erreurs que sur la Base, fichier par
fichier. Il en va de même pour la vérification de l'Étape 1 restreinte à `skills/list-dir`. Les
deux constats sont au journal, à verser au Registre à la Clôture.

Je ne retiens pas « commande de vérification en échec » comme motif de `DÉFAVORABLE` : la
comparaison à la Base établit que le Chantier n'y ajoute rien. Si l'utilisateur tient la lettre de
la vérification pour contractuelle, ce constat devient bloquant.

**R4 — `rumdl fmt --check` signale le Brief, le Suivi et le Plan du Chantier.** Ces trois documents
partent en archive à la Clôture. Les formater avant l'archivage coûte un appel.

**R5 — `migrateur-de-liste` ne voit pas les Marqueurs typés ni les Marqueurs facultatifs.** Sa
sélection, `list-dir list <liste> --where '<champ>=<À REMPLIR>'`, compare le texte exactement :

- sur une entrée neuve portant `date = "<À REMPLIR date>"`, `--where 'date=<À REMPLIR>'` rend 0 ;
- `--where 'category=<À REMPLIR>'` rend 0 là où `<OPTIONNEL>` en rend 61.

L'agent se déclare générique (« sert tout registre de tout projet », dit le Brief). Pour un champ
`date`, `int`, `bool` ou facultatif, il conclurait sans bruit qu'il n'a rien à traiter. Cette
migration n'est pas touchée : `chantier` et `reference` sont des `text` requis. Le prochain registre
dont le champ neuf est typé le sera. Le `validate --filled` de l'appelant ne rattrape que les champs
requis.

**R6 — L'agent affirme une garantie que ses outils ne donnent pas.** Sous « N'édite aucun fichier »,
il est écrit : « Tu n'as pas d'outil pour le faire, et c'est voulu ». Or il a `Bash`, qui écrit
(`sed -i`, redirection). La garantie tient à la consigne et à la garde de l'appelant, pas à l'outil.
Dans ce Chantier, les transcriptions ne montrent aucune écriture hors `fill`.

### Dette induite

**R7 — Les `values` de `severite` sont recopiées sans contrôle.** Elles figurent dans quatre
définitions (trois contrats et le patron `review`), plus leurs copies `.list/` et `.list/semence/`.
Aucun contrôle ne les rapproche. La décision 8 du Plan demandait de confirmer cette dette à
l'audit : c'est confirmé. `dette.md` la consigne en « Limite assumée ». Coût futur : une valeur
ajoutée à l'échelle doit l'être partout et dans le même ordre, sinon `--sort=-severite` et `derive`
divergent sans erreur. À verser au Registre à la Clôture.

**R8 — Quatre constats hors périmètre attendent la Clôture.** Le journal du Suivi les destine au
Registre et ils n'y sont pas encore, ce qui est normal à ce stade :

- `BrokenPipeError` de `list-dir list` coupé par `head` ;
- E501 et `basedpyright` de `list-dir` (R3) ;
- clé retirée d'une définition, que `reseed` ne signale pas ;
- `validate` qui masque les autres manquements derrière un TOML invalide.

À ajouter : R1 (effets de `migrate` non documentés), R2, R5, R6 et R7, si l'utilisateur les retient.

### Bloquants

Aucun.

## 2026-10-08 — clôture — `cfad0f7`

**Verdict** : RÉSERVES

Deuxième audit de clôture, après le traitement de la réserve R1 de l'audit `a051cc7`. Depuis cet
audit, deux commits : E12 (coche de l'Étape 12, État courant du Suivi) et E12.1 (paragraphe ajouté
à `technical-debt/migrations/3.md`). Le diff `master...registre-de-dette-severite-chantier-pin`
(176 fichiers, +2794 −341) a été rejugé en entier, pas seulement ces deux commits. Brief présent
et lu, Suivi et Plan (`.claude/plans/twinkly-stirring-moler.md`) lus. L'arbre de travail ne porte
que `settings.json` modifié, hors Chantier et hors diff, et ce rapport non suivi.

Selon la consigne de l'utilisateur, ni les titres ni les sections des entrées de dette n'ont été
lus. Les comparaisons de contenu sont faites par script, qui n'affiche que des comptes et des `id`.

Les numéros de ce rapport continuent ceux de l'audit précédent (R1 à R8), pour qu'aucun numéro
ne désigne deux constats différents dans ce fichier.

### Vérifications exécutées

`$T` = `.claude/implementation/todo`. Base extraite par `git archive master` dans le répertoire de
travail de la session, sans `stash`.

- `list-dir contract "$T/technical-debt" --values severite` → `inconnue`, `note`,
  `avertissement`, `majeur`, `critique`, dans cet ordre, rc 0.
- `list-dir contract --def technical-debt --patron review --values severite` → même sortie, rc 0.
- `list-dir validate "$T/technical-debt" --filled` → rc 0, « 90 élément(s) remplis et conformes ».
  Stderr : 90 lignes, toutes « champ « source » — déprécié ». Aucune note d'ancien Marqueur : les
  quatre lignes où apparaît « marqueur » sont des noms de fichiers.
- `list-dir validate "$T/technical-debt-solde" --filled` → rc 0, 44 éléments, stderr vide.
- `list-dir validate "$T/technical-debt-ecarte" --filled` → rc 0, 5 éléments, stderr vide.
- `list-dir list "$T/technical-debt" --sort=-severite` → rc 0 : 1 `critique`, 4 `majeur`,
  8 `avertissement`, 5 `note`, 72 `inconnue`, en blocs dans cet ordre.
- `list-dir list "$T/technical-debt" --sort chantier` → rc 0 : 31 valeurs distinctes, 31 blocs
  contigus.
- `list-dir list "$T/technical-debt" --sort date` → rc 0 : de 2026-08-14 à 2026-10-07, `sort -c`
  confirme l'ordre.
- `list-dir list "$T/technical-debt" --where pin=true` → 17 lignes ; `grep -l '^pin = true'` → 17 ;
  entrées sans `pin` → 0.
- `list-dir new` dans une copie temporaire du registre → `pin = false`, `severite`, `chantier`,
  `reference` à `<À REMPLIR>`, pas de `source`. `validate` de la copie → 91 conformes, rc 0.
- Chaque `chantier` confronté aux slugs de `done/` (préfixe daté retiré) → aucun absent, hors
  « Hors chantier ».
- Règles 1 et 2 de la consigne de `chantier`, rejouées par script sur `source` → 0 écart, 0 entrée
  hors règle, sur 90.
- Formes de `reference` → 64 `R<n>`, 6 `R<n>, R<n>`, 1 plage, 5 « Non précisée », les autres
  parmi les lieux fermés de la consigne. Aucune forme libre.
- `git diff master...HEAD` sur les entrées de `technical-debt` : 0 ligne `±source`. Lignes
  ajoutées : 90 × `chantier`, `reference`, `severite`, `pin` ; 19 `category = "<OPTIONNEL>"` ;
  22 `## Assumé` suivis de `<OPTIONNEL>` ; 58 `reviewed = "<OPTIONNEL date>"` contre 39
  `reviewed = "<OPTIONNEL>"` retirés. Aucune autre ligne.
- Comparaison des sections Base → HEAD, corps normalisé, par script :
  - `technical-debt` : 0 section changée, 22 sections ajoutées (toutes `<OPTIONNEL>`), 0 réordonnée ;
  - `-solde` : 0 changée, 7 ajoutées (toutes `<OPTIONNEL>`), 16 entrées réordonnées ;
  - `-ecarte` : 0 changée, 0 ajoutée, 0 réordonnée.
- `git diff -U0 98f43e0 HEAD` sur les entrées de `technical-debt` → 90 paires `chantier`, 90
  `reference`, 18 `severite`, 17 `pin`. Aucune autre ligne.
- Contrats locaux de `-solde` et `-ecarte` (lus par `tomllib`) → `source`, `severite`, `chantier`,
  `pin`, `reference` en `required = false`, sans `deprecated` ni `text`. Les contrats locaux des
  trois listes sont identiques à leur définition (`diff -q`).
- `list-dir derive "$T/technical-debt" <tmp>/revue --patron review` → rc 0, 90 fiches ; `validate`
  de la dérivée → 90 conformes, rc 0. `severite` reportée, même répartition ; 0 fiche avec `pin`.
- `list-dir fill`, dans la copie temporaire :
  - valeur hors `values` → rc 1 ;
  - Marqueur passé en valeur → rc 1 ;
  - champ déprécié → rc 1 ;
  - ni `--id` ni `--all` → rc 2 ; les deux → rc 2 ;
  - champ `date` typé → posé nu (`date = 2026-10-08`) ;
  - `--id` valide puis `--id` inexistant → rc 1, rien écrit ;
  - champ `list` (contrat jetable) → rc 1, refusé.
- `rg -n "\bpin\b" skills/debt-review` → 2 lignes, toutes deux « ignoré ».
- `grep -c "contrat.md" agents/migrateur-de-liste.md` → 0.
- `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/ scripts/tests/` → 642 passés.
- `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/` → 145 passés.
- `~/.claude/.venv/bin/python scripts/check_pipeline.py` → rc 0, « Pipeline conforme », 9 contrôles.
- `uvx ruff check .` → **rc 1**, 2 erreurs (E501, `test_fusion.py`). La Base extraite en rend
  autant (R11).
- `uvx ruff format --check .` → rc 0, 105 fichiers déjà formatés.
- `uvx --with pytest basedpyright` → **rc 1**. Le total de 6580 erreurs compte `skills/synced/`,
  ignoré par git et absent de la Base. Hors de ce répertoire : 81 erreurs sur HEAD contre 133 sur la
  Base. Seule différence par fichier : `gabarit/items.py`, 52 sur la Base, 0 sur HEAD. Aucune
  erreur neuve, aucune dans `fill.py` (R11).
- `uvx rumdl fmt --check .` → **rc 1**, 9 fichiers. Par rapport à la Base, s'ajoutent le Brief,
  le Suivi et le Plan du Chantier (R12).
- `uvx rumdl fmt --check skills/list-dir skills/implementation-tracker skills/debt-review
  agents/migrateur-de-liste.md` → rc 0. 4 constats non corrigeables, autant que sur la Base.
- Garde de `technical-debt/migrations/3.md`, extraite du bloc `GARDE` :
  - avec `STRUCTURE = 98f43e0` → **rc 1**, « ligne hors des champs migrés » sur `severite` et
    `pin` (R10) ;
  - avec `STRUCTURE = HEAD` → les contrôles de `chantier` et de `reference` passent, et la garde
    s'arrête sur « aucun changement », comme prévu.
- Neovim : `git -C ~/.config/nvim log -- plugins/listdir` → dernier commit le 2026-10-03.
  `status` vide, aucun fichier modifié depuis le 2026-10-07.
- Diff hors `.claude/implementation/todo`, `skills`, `agents`, `.claude/plans` et des fichiers du
  Chantier → vide.

### Conformité à l'intention

- Critère « `--values severite` dans l'ordre » : atteint, vérifié.
- Critère « `validate --filled` passe sur les trois listes, sans note d'ancien Marqueur, `source`
  signalé déprécié » : atteint, vérifié. L'avertissement ne porte que sur `technical-debt`, où
  `source` est déprécié. Dans `-solde` et `-ecarte`, il ne l'est pas (décision du journal du
  2026-10-07).
- Critère « `--sort=-severite`, `--sort chantier`, `--sort date` » : atteint, vérifié.
  `inconnue`, première des `values`, se range en dernier dans le tri décroissant.
- Critère « `--where pin=true` ; une entrée neuve porte `pin = false` » : atteint, vérifié.
- Critère « `severite`, `chantier` (slug de `done/` ou « Hors chantier »), `source` intact » :
  atteint, vérifié.
- Critère « contrat de `-solde` et `-ecarte` : cinq champs facultatifs » : atteint, vérifié.
- Critère « agent sous `agents/` ; `chantier` et `reference` remplis par lui » : agent présent.
  Que les valeurs viennent de lui, je le tiens de l'audit précédent, qui a lu les transcriptions
  (3 lancements, 180 valeurs posées), et du Suivi (2 `reference` corrigées à la main au geste 6).
  Je ne l'ai pas rejoué. La forme et la règle de `chantier` le sont, ci-dessus.
- Critère « `review.toml` porte `severite` et pas `pin` ; `debt-review` documente `inconnue` et
  `pin` » : atteint, vérifié. `review.toml` est en v2. Voir `SKILL.md` (Phase 2 points 4-5,
  Phase 5 point 4), `gabarit-rapport.md` et `exemple-revue.md`.
- Hors-périmètre : respecté.
  - Neovim intact.
  - Entrées de `-solde` et `-ecarte` : seuls des Marqueurs facultatifs ont été posés, et des
    sections réordonnées par `migrate`.
  - Aucune section d'entrée réécrite.
  - `/debt-review` : seuls s'ajoutent le rejugement de `severite` et l'ignorance de `pin`.
- Signaux de dérive : aucun matérialisé.
  - Le contenu des entrées n'a pas changé au-delà des champs migrés et des Marqueurs posés par
    `migrate`. Ces Marqueurs sont désormais documentés dans la note de migration (voir R9).
  - Tout `chantier` est admis.
  - `pin` ne protège rien.
  - Neovim n'a pas été modifié.
- Symptôme d'origine : disparu. Le registre se trie par date, par chantier et par sévérité, et
  s'épingle. 72 entrées restent à `inconnue`, comme le Brief l'a décidé.

**R9 — La réserve R1 de l'audit `a051cc7` est levée, avec un reste mineur.** Le paragraphe ajouté
à `migrations/3.md` dit que `migrate` pose au Marqueur les champs et sections facultatifs absents
et réordonne les sections. Il dit aussi pourquoi la structure se committe seule avant l'agent. Il ne
dit pas que `migrate` réécrit aussi les Marqueurs déjà présents dans leur forme typée :
`reviewed = "<OPTIONNEL>"` devient `"<OPTIONNEL date>"`, dans 39 entrées de `technical-debt`, 22 de
`-solde` et 2 de `-ecarte`. C'est précisément ce qui fait disparaître la note d'ancien Marqueur
exigée par le deuxième critère. Un lecteur d'un autre projet verra ces lignes dans son diff sans que
la note les annonce. Un mot suffit. Non bloquant.

### Qualité du code

Je n'ai rien relevé de neuf sur le code. `fill` (`commands/fill.py`, `ListStore.fill`) et
`typed_value` (`gabarit/prefill.py`) échouent fermé sur chaque entrée fautive essayée, avant toute
écriture. La conversion est partagée, pas recopiée. Le style suit les fichiers voisins : commentaires
en capitales qui disent pourquoi, `_ = cible.add_argument`, messages qui nomment le lieu. Les tests
couvrent les refus : 18 tests unitaires, 4 tests CLI, 2 tests de provenance.

**R10 — La garde de la migration ne se rejoue toujours pas sur HEAD** (R2 de `a051cc7`,
inchangé). La note dit bien qu'elle se lance « avant le commit de l'agent ». Mais les 18 `severite`
et 17 `pin` annotés par l'utilisateur sont dans le même commit E11 que la sortie de l'agent. Ce que
l'agent seul a écrit n'est donc plus isolable par un commit. Le diff `98f43e0..HEAD`, filtré, ne
montre que les quatre champs migrés : le résultat est sain, mais la trace rejouable est perdue.

**R11 — Deux commandes de l'Étape 12 sortent en échec, sans régression** (R3 de `a051cc7`). Sur
`ruff check .` et `basedpyright`, la comparaison à la Base extraite établit que le Chantier
n'ajoute aucune erreur, fichier par fichier, et en retire même 52 sur `gabarit/items.py`. Je ne les
compte pas comme « commande de vérification en échec » au sens du verdict défavorable, pour deux
raisons. Ces commandes échouent à l'identique sur la Base. Et l'utilisateur a vu cette réserve à
l'audit précédent et n'a fait traiter que R1. Si la lettre de la vérification de l'Étape 12 est
tenue pour contractuelle, ce constat devient bloquant.

**R12 — `rumdl fmt --check .` signale le Brief, le Suivi et le Plan du Chantier** (R4 de
`a051cc7`). Ce n'est que transitoire : `.rumdl.toml` exclut `.claude/implementation/done`, où la
Clôture archive ces trois fichiers. Après archivage, le dépôt n'aura plus de signalement neuf
venant du Chantier.

**R13 — `migrateur-de-liste` ne voit ni les Marqueurs typés ni les Marqueurs facultatifs** (R5 de
`a051cc7`, inchangé). La sélection `--where '<champ>=<À REMPLIR>'` compare le texte exact. Sur
HEAD, `--where 'category=<À REMPLIR>'` rend 0 ligne, `--where 'category=<OPTIONNEL>'` en rend 60.
Sur une entrée neuve, `--where 'date=<À REMPLIR>'` rend 0 ligne, `--where 'date=<À REMPLIR date>'`
en rend 1. Cette migration n'est pas touchée, puisque `chantier` et `reference` sont des `text`
requis. Elle le sera pour le prochain registre dont le champ neuf est typé ou facultatif, alors que
l'agent se déclare générique.

**R14 — L'agent affirme n'avoir « pas d'outil » pour éditer** (R6 de `a051cc7`, inchangé). Il a
`Bash`. La garantie tient à la consigne et à la garde de l'appelant, pas à l'outil.

### Dette induite

**R15 — Les `values` de `severite` sont recopiées sans contrôle** (R7 de `a051cc7`). On les
trouve dans quatre définitions et leurs copies `.list/` et `.list/semence/`. La dette est assumée
dans `dette.md`, mais elle n'est pas encore au Registre. Coût futur : une valeur ajoutée en un seul
endroit fait diverger `--sort=-severite` et `derive`, sans erreur.

**R16 — Constats à verser au Registre à la Clôture** (R8 de `a051cc7`). Le journal du Suivi en
destine quatre au Registre :

- `BrokenPipeError` de `list-dir list` coupé par `head` ;
- E501 et `basedpyright` de `list-dir` (R11) ;
- clé retirée d'une définition que `reseed` ne signale pas ;
- `validate` masqué par un TOML invalide.

S'y ajoutent R10, R13, R14 et R15, si l'utilisateur les retient. R9 se règle en une phrase plutôt
qu'en dette.

### Bloquants

Aucun.
