---
slug: retouches-et-modele-du-chantier
---

## 2026-10-05 — clôture — `e1d15c7`

**Verdict** : RÉSERVES

Lus : le brief (validé, inchangé depuis `AE0`), le suivi (8 Étapes `[x]`), le plan
`.claude/plans/silly-sparking-nebula.md`, et `git diff master...retouches-et-modele-du-chantier`
(22 fichiers, +712 −262).

### Vérifications exécutées

- V-garde `.venv/bin/python scripts/check_pipeline.py` → « Pipeline conforme. », 9 contrôles
  verts, sortie 0.
- V-tests `.venv/bin/python -m pytest -q skills/git-smart-commit/scripts/tests scripts/tests skills/gabarit/scripts/tests`
  → 217 passés (211 à `AE0` selon la Passation).
- Critère 2 `.venv/bin/python -m pytest skills/git-smart-commit` → 36 passés.
- `uvx ruff format --check skills/git-smart-commit/scripts scripts/check_pipeline.py` → 3 fichiers
  déjà formatés.
- `uvx ruff check skills/git-smart-commit/scripts scripts/check_pipeline.py` → All checks passed.
- `uvx --with pytest basedpyright skills/git-smart-commit/scripts scripts/check_pipeline.py`
  (depuis la racine, qui porte `pyrightconfig.json`) → 0 erreur, 3 fichiers vérifiés. Même
  résultat sur l'arbre extrait de `master` : aucune régression.
- Critère 3 `git grep -n -e step-implementer -e délégu -e execution -- ':!.claude/implementation/done' ':!.claude/implementation/todo' ':!.claude/plans'`
  → hors des fichiers du Chantier : `execution.md` comme nom de fichier (`LEXIQUE.md:28`,
  `SKILL.md:153`, `creation.md:138`) et `gabarit/items.py:232` (« délégué à `toml_value` »),
  étrangers au mécanisme ; dans les fichiers du Chantier : brief et suivi, qui citent le
  critère et la décision, et `brief.md:6`, `execution = "direct"` (voir R2).
- `gabarit contract suivi | grep -c execution` → 0 ; `gabarit contract brief | grep -c execution`
  → 0 ; `gabarit contract suivi` déclare `[fields."modèle"]`, enum `sonnet`/`opus`.
- `gabarit check .claude/implementation/retouches-et-modele-du-chantier.md --filled` → conforme.
- `gabarit check .claude/implementation/retouches-et-modele-du-chantier.brief.md --filled` →
  1 manquement, champ « execution » non déclaré au contrat (R2).
- `lexique liste | grep -F Retouche` → la ligne globale, lien vers `etape.md`.
- `test ! -e agents/step-implementer.md` → 0.
- `git grep -n -e step-implementer -e délégu -e délégab -- skills/implementation-tracker scripts/check_pipeline.py shadow-skills LEXIQUE.md agents`
  → vide.
- `grep -c 'MODÈLE' agents/plan-reviewer.md` → 3.
- `list-dir validate .claude/implementation/todo/technical-debt --filled` → 80 éléments conformes ;
  `… technical-debt-ecarte --filled` → 5 éléments conformes.
- V-md `uvx rumdl fmt --check` sur les 16 `.md` touchés → sortie 0 pour chacun. Restent des
  constats non formatables : MD028 de `contrat.md`, préexistant (présent sur `master`), et des
  lignes longues du suivi et du plan.
- `commit-chantier retouche` sur ce dépôt : `A 8` → `AE8.1` ; `A 3` → refus, `AE4` présent ;
  `Z 1` → refus, `ZE1` absent ; `a 1`, `AB 1` → refus de lettre ; `A x` → refus argparse, sortie 2.
- Motif d'Abandon `git tag --list 'AE[0-9]*'` dans un dépôt jetable (scratchpad) → rend `AE0 AE1
  AE1.1 AE1.10 AE12`, laisse `BE1.1` et `AEX`.
- `commit-chantier cloture retouches-et-modele-du-chantier --message <msg> --dry-run` → aucun
  refus ; 3 déplacements vers `done/`, tags `AE0`…`AE8` supprimés, arbre inchangé.

### Conformité à l'intention

- Critère « type 2 a un cas Retouche, message `<slug>: E<N>.<k> — …`, tag `<L>E<N>.<k>` » :
  atteint, vérifié — `etape.md`, cinquième ligne du tableau, procédure point 5,
  `commit-chantier retouche`.
- Critère « Clôture et Abandon suppriment aussi les tags `<L>E<N>.<k>`, et un test le montre » :
  atteint. Pour la Clôture, `test_cloture_supprime_les_tags_de_retouche` le montre et passe ;
  pour l'Abandon, procédure manuelle, que nul test ne peut couvrir : le motif l'établit, vérifié
  ci-dessus.
- Critère « plus aucune trace vivante de la délégation » : atteint au sens du critère, sous
  réserve de R2 et R3. Aucune trace dans `skills/`, `agents/`, `scripts/`, `shadow-skills/`,
  `LEXIQUE.md` ; les seules lignes du mécanisme restantes sont dans les fichiers du Chantier, qui
  partent en `done/` à la Clôture. Une trace hors du motif : R5.
- Critère « `gabarit contract suivi` déclare le champ du modèle ; ni `suivi` ni `brief` ne
  déclarent `execution` » : atteint, vérifié.
- Critère « `check_pipeline.py` passe, ainsi que ruff et basedpyright sur le Python touché » :
  atteint, vérifié, y compris sur `scripts/check_pipeline.py`, que le Plan ne lintait pas (constat
  `plan-reviewer` repris aux Notes du suivi).
- Hors-périmètre : respecté. Aucun Suivi d'un autre Chantier touché ; `.claude/implementation/done/`
  intact (`git diff --stat` vide).
- Signaux de dérive : aucun matérialisé. Aucun hook, script ni appel à `/model` ; la reprise
  signale l'écart de modèle sans rien changer (`SKILL.md:130-132`). Un modèle pour tout le
  Chantier (`contrat.md:165-167`). La Retouche ne crée aucune Étape (`execution.md`, section
  Retouche ; `etape.md:24`). Aucune archive de `done/` modifiée.
- Symptôme d'origine : disparu. La Retouche a son déclencheur (`execution.md:12`), son cas de
  commit, son tag rendu par script ; le modèle est choisi au Plan (`creation.md:30-32`), jugé par
  `plan-reviewer`, porté au Suivi.
- Incertitudes du brief : toutes tranchées au Plan et appliquées — Passation hors numérotation,
  seuil de 12 Étapes, « Retouche » au Lexique global (accord déclaré au Plan validé).
- **R1** — `contrat.md:169` et `agents/plan-reviewer.md:90` écrivent « Opus pour un travail
  complexe **ou** mal délimité », là où le brief (décision « dit », ligne 65-66) et le Plan
  (ligne 162) disent « complexe **et** mal délimité ». Ce n'est pas une nuance : un travail
  complexe mais bien délimité relève de Sonnet sous la formulation de l'utilisateur, et de
  « au moindre doute, Opus » sous celle du code, puisque les deux branches s'appliquent. Aucune
  entrée au journal ne trace ce changement. À confirmer par l'utilisateur, ou à réaligner.

### Qualité du code

- `commit_chantier.py` : `rang` et `prochaine_retouche` sont justes sur les cas exercés ; le
  `ValueError` de `rang` est inatteignable (seuls des tags déjà filtrés par `TAG_ETAPE` y
  passent) ; `retouche` est servi avant `bibliotheques()`, comme `lettre`. Style des voisins
  respecté (`prochaine_retouche` sans docstring, comme `lettre_libre`). Rien à signaler.
- **R2** — `.claude/implementation/retouches-et-modele-du-chantier.brief.md:6` porte encore
  `execution = "direct"` : le brief, figé à `AE0`, échoue désormais à
  `gabarit check … --filled`, et c'est la seule ligne du `git grep` du critère 3 qui *est* le
  mécanisme supprimé plutôt qu'une citation. Conforme au hors-périmètre (on ne migre pas un
  Chantier ouvert) et à la règle du brief figé ; la ligne quitte le motif du grep à
  l'archivage. À savoir avant de lire « critère 3 atteint » : il ne l'est strictement qu'après
  la Clôture.
- **R3** — `scripts/tests/test_controle_1.py:95` teste encore `slugify("Format d'étape et
  délégabilité")`. Les Notes du suivi le gardaient pour la vérification d'ensemble ; il y est
  toujours, et le grep du critère 3 ne le voit pas (`délégu` ne prend pas `délégab`). Le test
  reste juste, il porte sur la ponctuation, mais l'exemple cite une section qui n'existe plus.
- **R4** — `skills/git-smart-commit/SKILL.md:21` énumère les commits du type 2 : « état initial,
  session, étape terminée ou Passation ». La Retouche n'y est pas. Le routage tient, la ligne
  commençant par « Un commit sur la branche d'un chantier », mais l'énumération ne dit plus tous
  les cas que `etape.md` déclare.
- **R5** — `skills/git-smart-commit/references/etape.md:37`, procédure du type 2 : un fichier
  hors liste « c'est souvent le travail partiel d'un agent, dont le sort se tranche avant le
  commit ». Dans un Chantier, l'agent qui laissait un travail partiel était `step-implementer`
  en `ÉCART` ; il n'existe plus et les deux agents restants n'écrivent pas de code. La phrase
  est préexistante, et peut viser un agent d'un autre projet : invérifiable, mais c'est
  l'endroit où une trace de la délégation survit sans que le grep la voie.
- **R6** — `.claude/implementation/todo/technical-debt/ruff-format-absent-des-agents.md:31` : la
  coupe de `step-implementer` laisse la ligne « pas. `implementation-auditor` juge » orpheline
  au milieu du paragraphe, et la prémisse « ceux qui écrivent le code ne la lisent pas » ne vaut
  plus : aucun agent restant n'écrit de code. L'entrée reste valide (`list-dir validate`), son
  « Pourquoi c'est gênant » est à relire.

### Dette induite

- **R7** — `commit-chantier retouche` refuse quand `<L>E<n+1>` existe, mais ne peut pas voir que
  l'Étape n+1 a *commencé* (`[>]`, sans tag) : il rendra `AE<n>.<k>` pendant une Étape en
  cours. Le Plan l'a voulu (« Ne lit pas le Suivi »), la règle n'est donc tenue que par la prose
  d'`etape.md` et d'`execution.md`. Coût futur : une Retouche taguée par erreur au milieu de
  l'Étape suivante brouille la plage `AE<n>.<k>..AE<n+1>`, sans qu'aucun contrôle ne le signale.
  Accessoire : `retouche A -1` rend « tag AE-1 absent », message trompeur mais refus correct.

### Bloquants

Aucun.
