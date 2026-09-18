---
slug: skill-convention
---

## 2026-09-18 — clôture — `cea0665`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `.venv/bin/python scripts/check_pipeline.py` → sortie 0, « Pipeline conforme. » — les 9 contrôles
  passent (30 renvois au contrat, 7 empreintes uniques, 102 renvois entre skills, 5 chemins de skill
  cités, 44 fichiers sans appel relatif non gardé).
- `list-dir validate .claude/implementation/todo/technical-debt` → sortie 0, « 69 élément(s)
  conformes au contrat ».
- `bash -n skills/skill-convention/modeles/commandes-locales.sh` → sortie 0.
- `head -5 rules/python-style.md` → montre bien `paths`.
- `grep -c '^## ' references/prose.md` = 16 ; `grep -c 'Pratiqué dans'` = 16 → une citation par
  section.
- Borne « aucune skill existante éditée » :
  `{ git diff --name-only master -- skills OUTILLAGE.md rules/lua-style.md; git ls-files --others
  --exclude-standard -- skills; } | grep -v '^skills/skill-convention/'` → sortie vide.
- Essai du modèle de hook (projet jetable du scratchpad, `CLAUDE_ENV_FILE` sur un fichier
  préexistant) : deux lancements → deux lignes `export PATH=…` **ajoutées**, la ligne préexistante
  intacte ; lancement hors du projet → sortie 0, fichier inchangé ; sans `CLAUDE_ENV_FILE` →
  sortie 0, rien d'écrit ; annonce des commandes de `.claude/bin/` sur stdout. Conforme à ce que
  la référence promet.
- Existence des 15 chemins cités par `rules/python-style.md` et `references/prose.md` (non couverts
  par `check_pipeline.py` pour `rules/`) → tous existent.
- Résolution manuelle de tous les liens Markdown relatifs des trois fichiers `.md` livrés (y compris
  `../../../scripts/…`, `../../../hooks/…`, `../../../agents/…`, `../../../OUTILLAGE.md`) → aucun
  lien cassé.
- `uvx --with pytest basedpyright scripts` → `12 errors`, toutes `reportPrivateUsage` dans
  `scripts/tests/test_sante_skills.py` : le décompte de l'entrée de dette
  `typage-strict-non-tenu-dans-scripts-tests` est exact.
- `uvx ruff check` : NON EXÉCUTÉE — le diff n'introduit aucun fichier Python ; aucune cible dans le
  périmètre du chantier.

### Conformité à l'intention

- **Critère « `scripts/check_pipeline.py` passe toujours »** : atteint, vérifié (sortie ci-dessus).
- **Critère « chaque convention cite au moins un site du dépôt où elle est pratiquée »** (élargi le
  2026-09-17) : atteint, vérifié. 16 sections de `prose.md`, 16 lignes « Pratiqué dans » ; dans
  `rules/python-style.md`, chaque puce porte une citation entre parenthèses, à la seule exception
  des docstrings Google, marquée « *Prescrite, pas encore pratiquée* » — la dérogation ratifiée en
  relecture du plan. Tous les chemins cités existent.
- **Critère « une entrée de dette par skill en écart, conforme à `list-dir validate` »** : conforme
  au contrat (vérifié) ; **exhaustivité non établie** — voir R1.
- **Critère « l'entrée `commandes-locales-au-projet` sort de la road-map à la clôture »** : non
  encore atteint **par construction** — le plan l'assigne à la clôture, pas à une étape, et le
  suivi porte bien `road-map: commandes-locales-au-projet` dans son frontmatter. L'entrée est
  toujours dans `.claude/implementation/todo/road-map/`. Sur le fond, les quatre « points à
  trancher » de l'entrée sont tous traités par `references/commandes-locales.md` (forme du
  livrable, sous-agents, cohabitation RTK et `>>`, garde hors dépôt et échec ouvert) : la sortie
  est justifiée.
- **Hors-périmètre « les skills existantes ne sont pas corrigées »** : respecté, vérifié — la
  commande de borne rend une sortie vide ; `OUTILLAGE.md` et `rules/lua-style.md` sont intacts.
- **Signaux de dérive** : aucun matérialisé. La skill renvoie au lieu de recopier (`OUTILLAGE.md`
  pour l'exécutable et les linters, `contrat.md#dates-et-listing` pour les dates,
  `contrat.md#frontmatter` pour les champs), et le contrôle des empreintes de `check_pipeline.py`
  confirme qu'aucune phrase du contrat n'est dupliquée. Aucune skill existante éditée.
- **Symptôme d'origine** : le brief n'en énonce aucun (« non abordé »). Le but — poser les
  conventions et solder la road-map — est servi.
- **Écart au brief assumé et daté** : le `SKILL.md` ne renvoie pas à `rules/lua-style.md`. L'écart
  est consigné dans l'élargissement du 2026-09-18 du suivi, qui fait foi. Pas un constat.

### Qualité du code

- **R1** — *Exhaustivité de la dette (critère 3) non établie, un cas probable manquant.* Le
  périmètre « skills en écart » n'a jamais été énuméré : 16 conventions × 8 skills existantes, et
  le chantier a produit 8 entrées. Un sondage sur la seule convention « La description dit quoi,
  quand, et ce que la skill ne fait pas » relève que la `description` de `skills/intent-brief/
  SKILL.md` ne porte aucune phrase de limite négative (elle se termine sur « Alimente
  implementation-tracker. ») et qu'aucune entrée de dette ne la couvre — alors que le même écart a
  bien donné lieu à `emmylua-ls-description-sans-limite`. Soit l'écart existe et une entrée manque,
  soit il a été écarté en jugement, mais rien n'en garde la trace. Le cas de
  `git-smart-commit` est plus discutable (« ne committe qu'avec l'accord explicite » tient lieu de
  limite). Je n'ai pas sondé les 15 autres conventions : l'exhaustivité reste **invérifiable** de
  l'extérieur.
- **R2** — `rules/python-style.md:3` — *le champ `paths` diffère de ce que le plan annonçait, et
  peut ne jamais déclencher dans ce dépôt.* Le plan (§ « Frontière `rules/` ↔ skill ») prescrivait
  `paths: ["**/*.py"]`, sur le modèle de `rules/lua-style.md` (`"**/*.lua"`) ; le livré porte
  `"**/.claude/**/*.py"`. Si Claude Code apparie ce motif au chemin **relatif à la racine du
  projet**, aucun fichier Python de ce dépôt ne le satisfait (`scripts/check_pipeline.py`,
  `skills/gabarit/scripts/…` ne contiennent pas de segment `.claude`) : la convention ne se
  chargerait jamais là où elle a le plus de sens. Si l'appariement se fait sur le chemin absolu,
  tout va bien, puisque la racine est `~/.claude`. Je n'ai aucun moyen de trancher depuis ce dépôt
  — aucun fichier n'y documente la sémantique de `paths`, et aucun contrôle ne la vérifie (dette
  `garde-fou-borne-a-skills`). Le changement n'est ni justifié au journal de décisions, ni
  mentionné dans les élargissements.
- **R3** — `skills/skill-convention/SKILL.md:45` — la table annonce `rules/python-style.md`
  « chargé au contact d'un `*.py` », sans réserve, ce qui contredit la restriction `.claude/**` du
  champ `paths` effectivement écrit. Quelle que soit l'issue de R2, l'une des deux formulations est
  fausse.
- **R4** — Cohérence de forme des entrées de dette produites par le chantier : trois entrées
  (`emmylua-ls-description-sans-limite`, `list-dir-codes-de-sortie-non-dits`,
  `nvim-mini-test-redigee-en-anglais`, plus la mise à jour de
  `deux-conventions-de-mode-de-defaillance`) écrivent `date = "2026-09-17"` entre guillemets, les
  cinq autres `date = 2026-09-18` sans guillemets. Le dépôt compte 63 entrées non quotées contre 6
  quotées : la forme dominante des voisins est la date TOML nue. `list-dir validate` accepte les
  deux, donc rien ne le signalera ; c'est un écart de style au sein d'un même lot.

Rien d'autre à signaler sur les fichiers livrés. Le modèle `commandes-locales.sh` est de bonne
facture : en-tête qui dit sa portée et son mode d'échec, `set -uo pipefail`, garde sur le répertoire
de travail, `printf %q` pour les chemins à espaces, `>>` jamais `>`, et sortie 0 sur toute absence —
conforme au style de `hooks/outillage-rappel.sh` dont il se réclame, et vérifié à l'exécution.

### Dette induite

- **R5** — `.gitignore` gagne `skills/synced/` et `plugins/synced/`. Le geste est justifié au
  journal (2026-09-17 : `check_pipeline.py` lisait une copie de `skill-creator`) et il est sain,
  mais il n'apparaît ni au brief, ni au plan, ni dans l'arborescence livrée : un lecteur du diff ne
  le rattache au chantier que par le journal. Coût futur : la copie `skills/synced/` reste sur
  disque, hors du garde-fou, et l'entrée de dette
  `pyrightconfig-racine-inclut-les-skills-synced` constate qu'elle rend toujours 8097 erreurs
  `basedpyright` à la racine. La dette est consignée, donc assumée ; elle n'est pas résolue.
- **R6** — Le plan `.claude/plans/zany-napping-teacup.md` s'arrête à 8 étapes quand le suivi en
  porte 11, et la section « Vérification » du plan ignore les étapes 8 à 11. Le choix est motivé au
  journal (`execution: direct`, aucune délégation n'ira lire le plan) : coût faible, mais le plan
  archivé ne sera plus une description fidèle du chantier.

### Bloquants

Aucun. R1 deviendrait bloquant si l'utilisateur juge que `intent-brief` est bien en écart : le
critère « une entrée de dette par skill en écart » serait alors non atteint, et se lève en une
entrée `list-dir new`.
