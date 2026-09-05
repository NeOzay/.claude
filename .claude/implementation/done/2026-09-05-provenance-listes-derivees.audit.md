---
slug: provenance-listes-derivees
---

## 2026-09-05 — clôture — `5fe8927`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `uvx pytest skills/list-dir/scripts/tests -q` → **439 passés**, 0 échec (428 au cadrage, +11)
- `(cd skills/list-dir && uvx --with pytest basedpyright)` → **13 errors**, 0 warning — voir R1
- `list-dir derive .claude/implementation/todo/technical-debt "$S/rev" --template review` → rc 0
- `list-dir validate "$S/rev"` → **rc 0, stderr vide** ; le contrat dérivé porte
  `def = "technical-debt/review"`, `version = 1`, `frozen = true`
- estampille malformée, écrite à la main dans le contrat d'une dérivée puis `list-dir validate` :
  `a/b/c`, `a//b` → rc 1, « « origin », « def » — au plus un « / » … » ;
  `a/`, `../x`, `./a` → rc 1, « « origin », « def » — … n'est pas un nom … ». La clé est nommée
  dans les cinq cas.
- dérivée dégelée à la main (`frozen = false`) puis `validate` → rc 0 et l'avertissement
  « semée par le gabarit « technical-debt/review » — la péremption d'un gabarit n'est pas
  suivie ; « list-dir contract --def technical-debt --template review » … » ; **aucune** mention
  d'« introuvable dans les quatre rangs »
- `list-dir reseed "$S/rev" --def technical-debt/review` → rc 1, message « nomme le gabarit … pas
  une définition »
- `list-dir init … --def technical-debt/review` → rc 1, même message (hors-périmètre tenu par le
  refus, pas par une commande nouvelle)
- `list-dir validate .claude/implementation/todo/technical-debt` → rc 0, stderr vide
- `list-dir list .claude/implementation/todo/technical-debt | wc -l` → **43**, inchangé
- `list-dir contract --def technical-debt --template review --values category` → rc 0, les sept
  catégories, consommateur `debt-review` intact
- `diff` des quatre exemplaires du gabarit et des trois du contrat (définition, `.list/`,
  `.list/semence/`) → **identiques** ; le `reseed` du registre vivant a bien réécrit la semence
- contrôle d'ancre : aucune ancre `contrat-liste.md#…` citée dans `SKILL.md` (renvoi par titre) ;
  toutes les ancres internes de `contrat-liste.md` visent un titre existant (vérifié par script) —
  y compris `#def-prend-deux-formes-et-la-seconde-nomme-un-gabarit`
- `uvx ruff check .` → All checks passed
- `uvx ruff format --check .` → 5 fichiers non formatés, **exactement les mêmes** que sur `master`
  (`contrat-liste.md`, `test_contract.py`, `test_items.py`, `test_loader.py`, `test_move.py`) :
  aucun fichier du chantier n'y figure
- comparaison à la base : `git archive master skills/list-dir` extrait dans un répertoire hors
  dépôt, `basedpyright` y rend **les 13 mêmes erreurs, aux mêmes fichiers, lignes et codes**
  (`diff` des deux sorties : identique)

### Conformité à l'intention

- Critère « `derive` puis `validate` → rc 0 et aucun avertissement » : **atteint, vérifié** — c'est
  le symptôme d'origine, exécuté de bout en bout.
- Critère « estampille malformée refusée en nommant la clé » : **atteint, vérifié** sur les trois
  formes du brief plus `a//b` et `./a`.
- Critère « un nom composite ne s'entend plus dire "définition introuvable" » : **atteint,
  vérifié** sur une dérivée dégelée, et sur `reseed --def` / `init --def`.
- Critère « `uvx pytest … -q` passe » : **atteint, vérifié** — 439 passés.
- Critère « `basedpyright` → 0 error » : **non atteint tel qu'écrit au brief** — 13 erreurs. Voir
  **R1** : elles sont préexistantes et le suivi a redéfini le critère, ce qui fonde le verdict
  RÉSERVES plutôt que DÉFAVORABLE.
- Hors-périmètre : **respecté**. Aucune commande ni option nouvelle (le diff ne touche ni
  `commands/`, ni `list-dir.py` ; seuls `contract.py`, `definitions.py`, `provenance.py`,
  `types.py` sont modifiés). `init --def a/b` est refusé, non implémenté. Aucun `contract --seed`.
  L'instance source du `derive` n'entre pas dans `[origin]`. `derive` n'écrit pas de
  `.list/semence/` — `store.py` est inchangé.
- Signaux de dérive : **aucun matérialisé**. `derive` recopie toujours le gabarit verbatim (aucune
  ligne de `store.py` modifiée) ; `resolve()` rend toujours un `Path` de définition ou un échec.
- Symptôme d'origine : **disparu**, constaté par exécution.

### Qualité du code

- **R1** — `basedpyright` rend 13 erreurs (`provenance.py:193,194,607` ×4,
  `test_prefill.py:127` ×9). J'ai vérifié moi-même, sur une extraction de `master` hors dépôt,
  que la sortie est **strictement identique** : aucune erreur ajoutée par le chantier, aucune sur
  une ligne qu'il a touchée (ses ajouts à `provenance.py` sont aux lignes 61-125). Le suivi
  redéfinit le critère en « aucune erreur ajoutée », journal daté du 2026-09-05 à l'appui, et le
  suivi fait foi sur le brief. La réserve reste : le critère **tel que l'utilisateur l'a écrit**
  n'est pas tenu, et c'est à lui de dire s'il accepte la substitution.
- **R2** — `definitions.resolve()` (`definitions.py:200`) applique son verdict « gabarit » à
  **tout** nom contenant un `/`, sans reprendre la règle de forme de `_forme_du_nom`. Vérifié :
  `--def technical-debt/` répond « nomme le gabarit «  » … » et conseille
  « list-dir contract --def technical-debt --template  » (argument vide) ; `--def /x` conseille
  `--def ` ; `--def ../x` conseille `--def ..` ; `--def a/b/c` invente un gabarit nommé `b/c`. La
  commande échoue bien (rc 1) et rien n'est écrit, donc ce n'est pas un défaut de correction —
  mais le chantier se donne pour objet « un message honnête », et sur ce chemin-là le message
  conseille une commande qui ne marchera pas. La règle de forme existe pourtant, à un import près.
- **R3** — `_peremption(list_dir, nom, origin)` (`provenance.py:74`) reçoit `nom` **et** `origin`,
  alors que `nom` est `origin.name` déjà rétréci par l'appelant. La docstring l'assume, mais la
  signature laisse désormais passer un couple incohérent sans que rien ne le dise, sur une
  fonction dont tout le propos est de ne pas mentir sur la provenance. Un `assert` ou un
  paramètre `str` unique reconstruit depuis `origin` lèverait la question.

### Dette induite

- **R4** — le journal du suivi ouvre l'entrée `basedpyright` « pour le registre de dette », mais
  aucune fiche n'a été déposée : `git diff master...` ne montre aucune entrée nouvelle sous
  `.claude/implementation/todo/technical-debt/`. Le constat n'existe donc que dans un suivi qui
  part en `done/` à la clôture — exactement le sort que le registre existe pour éviter
  (`dette.md`, « Le registre est cet endroit »). À déposer avant archivage.
- **R5** — dette **assumée et documentée** : `origin.version` d'un gabarit n'est comparé à rien.
  Une correction future de `review.toml` ne peut envoyer aucun signal à une liste dérivée, le gel
  fermant aussi ce chemin. `contrat-liste.md` le dit explicitement (« la version d'un gabarit ne se
  compare à rien ») et le brief l'a voulu — noté pour que le coût futur soit su, pas contesté.
- La logique de découpe du nom vit en trois endroits (`Origin.definition`/`template`,
  `_forme_du_nom`, le `partition` de `resolve`), tous adossés à la constante `SEPARATEUR` : le
  couplage est nommé et tenu à un seul point. Rien à signaler au-delà de **R2**.

### Bloquants

Aucun. **R1** serait bloquant si l'utilisateur refuse la substitution de critère consignée au
journal du suivi ; le rétablir suppose un travail hors périmètre sur `test_prefill.py` et
`provenance.py`, sur des lignes que ce chantier n'a pas touchées.
