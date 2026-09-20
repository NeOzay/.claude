---
slug: deux-sens-de-gabarit
---

## 2026-09-20 — clôture — `ffc2297`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `grep -rni 'template' skills/list-dir skills/debt-review --include='*.py' --include='*.md'` → aucune occurrence (rc=1)
- `grep -rn 'gabarit' skills/list-dir --include='*.py' --include='*.md'` → 87 occurrences, toutes le paquet, le module ou le fichier posé ; aucune ne désigne un patron
- `ls .claude/implementation/todo/technical-debt/.list/patrons/` → `review.md`, `review.toml`
- `grep -rn 'list-dir/references\|\.\./list-dir' skills/gabarit/` → aucune (rc=1)
- `grep -n 'Prérequis' -A8 skills/list-dir/SKILL.md` → section présente (l. 37), nomme `gabarit` et renvoie à `../gabarit/SKILL.md` et `../gabarit/references/format.md`
- `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q` → **508 passed** en 14,97 s
- `/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py` → **Pipeline conforme** (109 renvois entre skills résolvent)
- `list-dir validate .claude/implementation/todo/technical-debt` → 67 élément(s) conformes (rc=0)
- `list-dir reseed … --dry-run` → « déjà à jour, rien à faire » (rc=0)
- `list-dir contract … --patron review` → contrat imprimé (rc=0)
- `list-dir derive … --patron review` → 67 fiches (rc=0), puis `validate` sur la dérivée → 67 conformes (rc=0)
- `uvx ruff check skills/list-dir skills/gabarit` → **3 erreurs** ; même commande sur l'arbre `master` extrait par `git archive` → **3 erreurs**, identiques (E501 sur `test_fusion.py`) : aucun écart
- `uvx --with pytest basedpyright` → **5536 errors**, conforme au relevé de base consigné au suivi. Diff des diagnostics restreints à `skills/list-dir` et `skills/gabarit` entre l'arbre `master` extrait et la branche → **aucun diagnostic neuf** (les 52 lignes en plus côté base sont des `tomlkit` non résolus, artefact de l'arbre extrait sans venv)
- `grep -rn 'gabarit' skills/skill-convention skills/intent-brief skills/implementation-tracker --include='*.md' | grep -i 'derive\|moule\|patron\|templates'` → aucune : aucune skill tierce ne désignait un moule
- `git diff master...deux-sens-de-gabarit --stat` → 41 fichiers, tous dans les chemins autorisés par le suivi

### Conformité à l'intention

Critères du suivi (qui fait foi sur le brief, élargissement daté du 2026-09-20 compris) :

- « `grep -rni 'template' skills/list-dir skills/debt-review` → aucune » : **atteint, vérifié**.
- « chaque `gabarit` restant dans `skills/list-dir` désigne le paquet ou le fichier posé » :
  **atteint, vérifié** — les 87 occurrences sont des imports `from gabarit.…`, des docstrings de
  réexportation, les renvois neufs du `SKILL.md` et de `references/format.md`.
- « `ls .list/patrons/` → `review.md`, `review.toml` » : **atteint, vérifié**.
- « `validate` conforme ; `reseed --dry-run` aucun conflit ; `derive … --patron review` puis
  `validate` conforme » : **atteint, vérifié** — la migration croisée semence/copie vive n'a produit
  aucun conflit, c'était l'incertitude principale du brief.
- « `grep -n 'Prérequis' skills/list-dir/SKILL.md` → une section qui nomme `gabarit` et y renvoie » :
  **atteint, vérifié**. La section dit en outre le sens de la dépendance et le mode de localisation,
  ce que réclamait la dette `list-dir-depend-de-gabarit-sans-le-dire`.
- « les six types sont écrits dans une référence de `gabarit` et aucun renvoi de `gabarit` vers
  `list-dir` » : **atteint, vérifié** — `skills/gabarit/references/format.md#les-six-types`, et les
  cinq emprunts (`SKILL.md:20`, `SKILL.md:46`, `semences.md:19`, `semences.md:43`,
  `commandes.py:152`) sont tous retournés.
- « 508 passed », « `check_pipeline.py` conforme », « ruff et basedpyright sans écart avec la base » :
  **atteints, vérifiés** (voir ci-dessus, y compris la comparaison sur arbre extrait).
- Hors-périmètre : **respecté**. Le skill, le paquet, la commande, le lien de `bin/` et l'estampille
  `gabarit = "…"` sont intacts ; aucune commande ne gagne ni ne perd d'option (`--template` →
  `--patron`, un pour un) ; `gabarit-porte-des-residus-de-liste` reste ouverte ; les cinq références
  de `list-dir` gardent leur découpage ; les archives de `done/` gardent leurs `--template`.
- Signaux de dérive : **aucun matérialisé**. Le diff ne sort pas des chemins autorisés ; le socle
  n'est arrivé dans `gabarit` (E3) qu'après le renommage vérifié (E1, E2) ; aucune notion propre à
  une liste (`id`, `.list/`, `from`, `[origin]`, `reseed`, `LISTDIR_*`) n'est écrite dans
  `gabarit/references/format.md` — vérifié ligne à ligne ; le nombre de tests n'a pas bougé et
  aucun message d'erreur n'a été affaibli pour faire passer un test.
- Symptôme d'origine : **largement disparu, une survivance** — voir **R1**. Dans le couple
  `list-dir`/`gabarit`, « gabarit » ne nomme plus qu'une chose. Mais trois fichiers de données que
  ce chantier a lui-même édités continuent d'appeler « gabarit » un patron, et l'un d'eux est servi
  à l'écran par une commande.

### Qualité du code et de la prose

- **R1** — `.claude/implementation/todo/technical-debt/.list/patrons/review.toml:14-15`,
  `.claude/implementation/todo/technical-debt/.list/semence/patrons/review.toml:14-15` et
  `skills/implementation-tracker/list-dir/technical-debt/patrons/review.toml:14-15` portent encore :
  `# LE NOM EST COMPOSITE parce qu'un gabarit n'est pas une définition : il vit dans le`
  `# \`templates/\` de « technical-debt », et c'est là qu'on le retrouve`.
  Deux défauts en deux lignes : le mot « gabarit » y désigne un **patron** — exactement la collision
  que le chantier supprime — et `templates/` y nomme un répertoire qui n'existe plus. Ces lignes
  sont imprimées telles quelles par `list-dir contract .claude/implementation/todo/technical-debt
  --patron review`, commande que `debt-review/references/gabarit-rapport.md:56` fait exécuter à
  chaque revue : la survivance est sur un chemin utilisateur, pas dans un coin mort. Le journal du
  suivi affirme pourtant « les quatre `review.toml` … ont suivi le renommage » : seules les deux
  lignes portant le drapeau `--patron` ont été reprises dans chaque fichier. Aucun critère écrit ne
  tombe (tous les greps sont bornés à `skills/list-dir`, en `*.md`/`*.py`), ce qui est précisément
  la façon dont l'écart est passé.
- **R2** — `skills/gabarit/references/format.md`, « Les six types » : « Elle est dérivée d'un seul
  endroit — `FieldType` dans `scripts/gabarit/types.py` —, jamais recopiée : deux listes qui se
  ressemblent finissent toujours par diverger. » La phrase est vraie du code (`FIELD_TYPES` sort de
  `get_args(FieldType)`), mais elle est posée immédiatement sous une recopie manuelle des six types
  dans la prose — recopie que le brief exigeait. Telle quelle, la prose se contredit à deux lignes
  d'intervalle et n'avertit pas qu'elle est, elle, la copie à tenir à jour si `FieldType` bouge.
- Pour le reste, la prose neuve tient les conventions de `skill-convention/references/prose.md` :
  présent déclaratif sans récit (les imparfaits signalés au journal ont bien été corrigés — vérifié
  sur `format.md` et `semences.md`), chaque règle porte son mode de défaillance dans le corps du
  texte, renvois relatifs avec ancre qui résolvent tous (`check_pipeline.py` § 8), français correct,
  une référence par sujet. Le `SKILL.md` de `gabarit` gagne même la colonne « Lire quand » de sa
  table de références, qui est la convention « lire une référence au moment d'en avoir besoin » —
  `list-dir/SKILL.md` ne l'a toujours pas, mais c'est un état antérieur au chantier, pas une
  régression.
- Renommage de code : cohérent et complet. La constante unique `PATRONS`, les identifiants français
  (`_patrons`, `fusionner_patrons`, `patrons_semence`) et les messages d'erreur assertés ont suivi
  ensemble ; la désambiguïsation de la locale `sections` dans `store.py`, trouvée par le `diff`
  basedpyright, est le bon arbitrage et elle est journalisée. Rien à signaler de plus.

### Dette induite

- **R3** — Le registre de dette vivant garde sept entrées qui citent des chemins `templates/` désormais
  morts : `marqueurs-recopies-dans-gabarits.md:12,31`, `version-de-gabarit-comparee-a-rien.md:13,41`,
  `definition-aplatit-les-sous-repertoires-de-templates.md` (titre, slug et l. 14/17/38),
  `backups-portent-des-contrats-refuses.md:14`, `gabarit-jamais-retire-par-re-semis.md:13`,
  `regles-hors-contrat-sans-empreinte.md:15`,
  `sections-de-categories-jamais-confrontees-au-contrat.md:13`. Ce dernier est incohérent avec
  lui-même : ses lignes 16 et 42 ont été passées à `--patron` par ce chantier, sa ligne 13 cite
  toujours `…/technical-debt/templates/review.toml`. Le coût futur est concret : la commande de
  vérification d'une dette qui nomme un chemin inexistant ne se solde pas telle quelle, et le
  lecteur ne sait pas si `templates/` est un reliquat ou un répertoire qu'il n'a pas trouvé.
- **R4** — Le suivi porte encore, dans « État courant », la note « **À trancher avant l'étape 5** :
  quatre entrées vivantes du registre de dette citent `--template` ». Deux entrées ont été corrigées
  (`derive-migrate-hors-cli.md`, `sections-de-categories-…`), et le journal ne dit pas ce qui a été
  décidé pour les autres. Une question ouverte laissée dans le suivi à la clôture se lit comme un
  oubli, pas comme un arbitrage : c'est ce qui rend **R3** invisible.
- Aucune duplication, aucune abstraction neuve, aucun couplage nouveau : le chantier en retire au
  contraire — cinq emprunts de `gabarit` à `list-dir` supprimés, le socle écrit une seule fois.

### Bloquants

Aucun. Tous les critères écrits sont atteints et vérifiés par exécution, et toutes les commandes de
vérification passent. **R1** est la réserve à trancher avant clôture : elle est d'une ligne à
corriger dans trois fichiers, mais elle laisse le symptôme d'origine visible à l'écran d'une
commande. **R3** et **R4** sont du soldage de registre, à verser en dette si l'utilisateur ne veut
pas les traiter dans ce chantier.
