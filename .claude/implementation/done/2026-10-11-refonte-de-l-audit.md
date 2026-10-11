+++
gabarit = "suivi"
slug = "refonte-de-l-audit"
titre = "Refondre le rapport d'audit : un fichier TOML par audit, le suivi des dettes, un verdict aligné sur leur sévérité"
branche = "refonte-de-l-audit"
base = "master"
statut = "terminé"
session = 3
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-11-refonte-de-l-audit.plan.md"
brief = ".claude/implementation/done/2026-10-11-refonte-de-l-audit.brief.md"
audit = ".claude/implementation/done/2026-10-11-refonte-de-l-audit.audit"
road-map = "refonte-de-l-audit"
skills = ["skill-convention"]
"créé" = 2026-10-11
maj = 2026-10-11
+++

## Objectif et périmètre

**Symptôme** : « les audits sont empilés dans un fichier .md qui gonfle à chaque audit » ; le
verdict ne conclut presque jamais (74 `RÉSERVES`, 12 `DÉFAVORABLE`, 1 `FAVORABLE` dans les
rapports archivés).

**But** : un rapport par audit, en TOML, qui reprend l'état des dettes de l'audit précédent et
suit leur évolution ; un verdict rendu par l'auditeur selon une échelle de sévérité.

**Critères de réussite** :

- **C1** — `audit new <slug> --intermediaire` pose `01-<sha>.toml` sur un Chantier sans audit,
  puis `02-<sha>.toml` dont la Dette précédente est la Dette actuelle du `01`, cumuls repris
  (`pytest`).
- **C2** — `audit new` exécute les `vérif:` des Étapes du Suivi et consigne `statut` et `sortie`
  en `[[verification]]` (`pytest`).
- **C3** — `audit check --filled` accepte les deux audits factices et refuse chaque faute de
  l'annexe : dette précédente non rangée, renvoi vers une dette absente, `R<n>` déjà servi,
  verdict non admis, cote d'office non respectée (`pytest`).
- **C4** — `audit range` range une dette précédente sans recopie, vers `ecartee` avec le
  justificatif lu dans `## Dettes écartées` du Suivi ; `audit dette` attribue le `R<n>` suivant
  et `trouvee` (`pytest`).
- **C5** — `grep -rn '\.audit\.md' agents/ skills/` ne rend rien, et
  `git diff --name-only master...refonte-de-l-audit | grep '\.audit\.md$'` non plus.
- **C6** — `grep '^tools:.*Edit' agents/implementation-auditor.md` rend une ligne,
  `gabarit contract suivi | grep 'Dettes écartées'` aussi, et
  `grep -n 'plus sévère' agents/implementation-auditor.md` rien.
- **C7** — `~/.claude/.venv/bin/python -c 'import pydantic'` réussit, Pydantic étant déclaré
  dans `requirements.txt`.
- **C8** — L'audit de Clôture de ce Chantier est écrit au nouveau format, dans
  `refonte-de-l-audit.audit/`, et passe `audit check --filled`.

**Hors-périmètre** :

- Quand un audit intermédiaire est pertinent : décidé au Plan, en road-map
  (`audit-intermediaire-au-plan`).
- Un nombre d'audits borné par Chantier ; un contre-audit borné au diff depuis le SHA audité :
  l'audit reste complet.
- La restitution du verdict en une ligne et un tableau, déjà livrée.
- La correspondance d'une dette de l'audit avec le contrat du Registre, en road-map
  (`dette-d-audit-au-format-du-registre`).
- Les rapports `.audit.md` existants, dans `done/` comme `lexique-local-tronque.audit.md`.
- Le Brief et sa semence.

**Signaux de dérive** :

- **S1** — Une instruction fait recopier une dette à la main par l'auditeur ou l'orchestrateur,
  au lieu d'`audit new`, `audit range` ou `audit dette`.
- **S2** — Une commande ou une instruction lit des audits antérieurs au précédent : le rapport se
  suffit avec un seul précédent.
- **S3** — Le verdict est écrit par une commande et non par l'auditeur ; `audit check` ne fait que
  vérifier qu'il est admis.
- **S4** — Le diff touche la semence `brief`, le contrat du Registre, le seuil de 400 lignes ou un
  `.audit.md` existant.
- **S5** — L'échelle de l'audit change hors décision : `inconnue` revient, ou `bloquant` entre au
  contrat du Registre.

## Étapes

- [x] 1. Pydantic au venv — `requirements.txt`, `OUTILLAGE.md` — vérif:
      `~/.claude/.venv/bin/python -c 'import pydantic' && ~/.claude/.venv/bin/python -m pytest scripts/tests/test_sante_skills.py -q`
- [x] 2. Le modèle et `audit check` —
      `skills/implementation-tracker/scripts/rapport_audit/modele.py`,
      `skills/implementation-tracker/scripts/audit-cli.py`, `bin/audit`,
      `skills/implementation-tracker/pyrightconfig.json`, `OUTILLAGE.md`,
      `skills/implementation-tracker/scripts/tests/` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_modele.py -q`
- [x] 3. `audit new`, la pose — `skills/implementation-tracker/scripts/rapport_audit/pose.py`,
      `skills/implementation-tracker/scripts/tests/test_pose.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_pose.py -q`
- [x] 4. `audit new`, les vérifications —
      `skills/implementation-tracker/scripts/rapport_audit/pose.py`,
      `skills/implementation-tracker/scripts/tests/test_pose.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_pose.py -q -k verification`
- [x] 5. `audit range` et `audit dette` —
      `skills/implementation-tracker/scripts/rapport_audit/dettes.py`,
      `skills/implementation-tracker/scripts/tests/test_dettes.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_dettes.py -q`
- [x] 6. `audit export` — `skills/implementation-tracker/scripts/rapport_audit/export.py`,
      `skills/implementation-tracker/scripts/tests/test_export.py` — vérif:
      `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_export.py -q`
- [x] 7. Le Suivi et l'archivage — `skills/gabarit/gabarit/suivi/contract.toml`,
      `skills/git-smart-commit/scripts/commit_chantier.py`,
      `skills/git-smart-commit/references/aplatissement.md`, `scripts/check_pipeline.py`, leurs
      tests — vérif:
      `gabarit contract suivi | grep 'Dettes écartées' && ~/.claude/.venv/bin/python -m pytest skills/git-smart-commit/scripts/tests/ scripts/tests/ -q && python3 scripts/check_pipeline.py`
- [x] 8. L'agent — `agents/implementation-auditor.md` — vérif:
      `grep '^tools:.*Edit' agents/implementation-auditor.md && ! grep -n 'plus sévère\|\.audit\.md' agents/implementation-auditor.md`
- [x] 9. Les références — `skills/implementation-tracker/references/audit.md`, `cloture.md`,
      `contrat.md`, `dette.md`, `skills/implementation-tracker/SKILL.md`, et
      `rapport_audit/pose.py`, `test_pose.py`, les fixtures — vérif:
      `! grep -rn '\.audit\.md' agents/ skills/ | grep -v -e scripts/impl_list.py -e list-dir/technical-debt/migrations/ && python3 scripts/check_pipeline.py && git diff --name-only --diff-filter=d master...HEAD -- '*.md' | xargs -r uvx rumdl fmt --check`
- [x] 10. Formatage et typage du périmètre — le code des Étapes 2 à 7 — vérif:
      `uvx ruff check skills/implementation-tracker skills/git-smart-commit scripts && uvx ruff format --check skills/implementation-tracker skills/git-smart-commit scripts && uvx --with pytest --with pydantic basedpyright -p skills/implementation-tracker`
- [x] 11. Recharger l'agent réécrit — aucun fichier — vérif: dans la session neuve, la liste des
      agents donne à `implementation-auditor` l'outil `Edit`

## État courant

**Prochaine action** : l'audit de Clôture — `audit new refonte-de-l-audit --cloture`, puis
`implementation-auditor` sur le rapport posé.

**Vérification** :
`~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/ scripts/tests/ skills/git-smart-commit/scripts/tests/ -q && python3 scripts/check_pipeline.py`

**Dernier audit** : ef2b907 — FAVORABLE — 2026-10-11

**Notes** : les deux audits factices du cadrage sont les fixtures de
`skills/implementation-tracker/scripts/tests/fixtures/contexte-tracker.audit/`.

## Passation

**Écrite** : session 2, après AE9.

**En cours** : rien.

**À savoir** :

- AE5 a embarqué `refonte-de-l-audit.audit/01-9b0016f.toml`, posé à 13:21 par un `audit new`
  qu'aucune commande de la session n'a lancé ; retiré en AE5.1. Avant l'audit de Clôture,
  `refonte-de-l-audit.audit/` ne doit pas exister : `audit new` refuse un précédent non rempli.
- `uvx rumdl fmt --check` sort en 1 dès qu'il sait corriger quelque chose, en 0 s'il ne signale
  que des lignes qu'il ne sait pas enrouler. Le Suivi est désormais enroulé par `rumdl fmt`.
- basedpyright sur `skills/implementation-tracker` rend déjà 0 erreur ; pour E10, reste la part
  de `skills/git-smart-commit` (4 erreurs avant le Chantier), à comparer sur un arbre extrait.
- `audit new refonte-de-l-audit --cloture` rejouera les `vérif:` des Étapes 1 à 10 : la suite
  entière, une minute environ ; celle de l'Étape 11, en prose, sortira `non-exécutée`.

## Journal de décisions

- **2026-10-11** — C5 se vérifie hors de `skills/implementation-tracker/scripts/impl_list.py` et de
  `list-dir/technical-debt/migrations/3.md`. *Pourquoi* : le filtre d'`impl-list` doit continuer
  d'écarter les `.audit.md` existants, et une migration passée ne se réécrit pas. *Rejeté* :
  réécrire ces deux fichiers pour tenir C5 à la lettre.
- **2026-10-11** — Pas d'audit intermédiaire ; la Clôture se lance après redémarrage de Claude
  Code (Étape 11). *Pourquoi* : le nouveau format ne sert qu'une fois l'agent réécrit, et une
  session ne recharge pas l'agent qu'elle a modifié.
- **2026-10-11** — Seuls les champs de l'auditeur admettent le Marqueur (`Rempli[T]`, union
  discriminée) ; l'en-tête, les `id`, `trouvee`, `corrigee`, `preuve` et la Dette écartée le
  refusent, et `dette` d'une vérification `échouée` se pose au Marqueur. *Pourquoi* : la commande
  pose ces champs, un Marqueur y serait sa faute. *Rejeté* : un balayage du TOML brut hors de
  Pydantic.
- **2026-10-11** — `audit new` exige un précédent qui passe `--filled` ; un audit interrompu se
  supprime avant d'en poser un autre. *Pourquoi* : la Dette précédente serait copiée au Marqueur.
  *Rejeté* : poser sur un précédent incomplet.
- **2026-10-11** — Une vérification `non-exécutée` : une `vérif:` qui n'est pas une seule portée
  de code, un code 126 ou 127, ou 600 s dépassées. *Pourquoi* : rien n'y a été vérifié, et
  l'auditeur la mène lui-même. *Rejeté* : la compter `échouée`, avec une dette `bloquant` d'office.
- **2026-10-11** — `audit range` d'une dette déjà rangée par cet audit la déplace ; le tableau
  `dette` se réécrit depuis le modèle, sans ses commentaires. *Pourquoi* : l'auditeur corrige un
  rangement sans toucher aux tableaux à la main (S1). *Rejeté* : refuser un second rangement.
- **2026-10-11** — `implementation-auditor` perd `Write` en gagnant `Edit`. *Pourquoi* : l'appelant
  pose le rapport, l'auditeur ne crée aucun fichier. *Rejeté* : garder `Write`, qui permettrait de
  réécrire le rapport en entier, dettes recopiées comprises (S1).
- **2026-10-11** — `audit new` lit une Étape enroulée sur plusieurs lignes, et le Suivi suit
  `rumdl fmt`. *Pourquoi* : la vérif d'E9 passe `rumdl fmt --check` sur le Suivi, qui enroule les
  Étapes longues. *Rejeté* : exclure le Suivi du formateur.
- **2026-10-11** — `audit export <rapport> <scratchpad>` : la commande nomme l'export
  `<slug>-<NN>-<sha>.md` et affiche son chemin complet. *Pourquoi* : le nom se lit dans le rapport,
  l'appelant n'a pas à le composer. *Rejeté* : `<destination.md>`, le chemin complet donné par
  l'appelant, comme au Plan.
