---
slug: decoupe-contrat-liste
titre: Découper et réécrire la référence de list-dir
branche: decoupe-contrat-liste
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-09-05-decoupe-contrat-liste.plan.md
brief: .claude/implementation/done/2026-09-05-decoupe-contrat-liste.brief.md
audit: .claude/implementation/done/2026-09-05-decoupe-contrat-liste.audit.md
créé: 2026-09-05
maj: 2026-09-05
---

## Objectif et périmètre

Repris du brief (`brief:`).

**Symptôme** : `skills/list-dir/references/contrat-liste.md` « a fortement gonflé » — 828 lignes,
13 sections, accrétées chantier après chantier.
**But** : « couper les responsabilités en plusieurs fichiers », et « en profiter aussi pour
factoriser la documentation, comme réagencer et réécrire les sections ». La gêne principale est la
**dispersion d'un même sujet** — `derive` décrit à trois endroits, le contrat à trois autres —
puis la taille brute.
**Critères de réussite** :
- `python3 scripts/check_pipeline.py` passe (le contrôle 8 sanctionne tout renvoi inter-skill mort)
- `skills/list-dir/SKILL.md` référence les nouveaux documents
- `contrat-liste.md` supprimé, aucun renvoi résiduel hors archives `done/`
- inventaire des règles, chacune cochée contre les nouveaux fichiers avant toute suppression
**Élargissement du 2026-09-05** : l'écart entre `description` obligatoire sur une section et
facultative sur un champ, constaté par l'utilisateur en cours d'étape 7, est décrit dans
`format.md` et porté au registre de dette. La correction du code reste hors de ce chantier.

**Hors-périmètre** :
- `contrat-liste.md` non modifié pendant le chantier : c'est le document de référence, source
  jusqu'à la fin, supprimé une fois les nouveaux fichiers validés
- pas de changement de comportement de `list-dir` : ni `scripts/listdir/`, ni les tests
- élargir le contrôle 8 aux renvois voisins/intra-fichier : non abordé, dette laissée ouverte
**Signaux de dérive** :
- si une règle change de sens sous couvert de réécriture, s'arrêter : c'est de la doctrine
- si un `> *Mode de défaillance*` disparaît sans être intégré ailleurs, c'est une perte
- si le chantier touche `scripts/listdir/` ou les tests, il a débordé — **exception ratifiée le
  2026-09-05** : la seule docstring de `commands/contract.py`, qui cite le fichier supprimé

## Étapes

- [x] 1. Inventaire des règles — `.claude/implementation/decoupe-contrat-liste.inventaire.md` — vérif: `grep -c '^- R' <inv>` > 0 et `grep -o 'l\. *[0-9]*' <inv> | tr -dc '0-9\n' | sort -n | tail -1` ≥ 818
- [x] 2. `format.md` — `skills/list-dir/references/format.md` — vérif: `python3 scripts/check_pipeline.py` + `grep -c '^- R.*→ format\.md' <inv>` > 0
- [x] 3. `definitions.md` — `skills/list-dir/references/definitions.md` — vérif: `python3 scripts/check_pipeline.py` + `grep -c '^- R.*→ definitions\.md' <inv>` > 0
- [x] 4. `provenance.md` — `skills/list-dir/references/provenance.md` — vérif: `python3 scripts/check_pipeline.py` + `grep -c '^- R.*→ provenance\.md' <inv>` > 0
- [x] 5. `operations.md` — `skills/list-dir/references/operations.md` — vérif: `python3 scripts/check_pipeline.py` + `grep -c '^- R.*→ operations\.md' <inv>` > 0
- [x] 6. `extension.md` — `skills/list-dir/references/extension.md` — vérif: `python3 scripts/check_pipeline.py` + `grep -c '^- R.*→ extension\.md' <inv>` > 0
- [x] 7. Repointer les renvois — `list-dir/SKILL.md`, `debt-review/SKILL.md`, `implementation-tracker/references/dette.md`, `listdir/commands/contract.py` — vérif: `python3 scripts/check_pipeline.py`
- [x] 8. Asymétrie de `description` — `references/format.md`, fiche de dette — vérif: `list-dir validate .claude/implementation/todo/technical-debt` + `python3 scripts/check_pipeline.py`
- [x] 9. Repointer les fiches de dette — `todo/technical-debt/` (9 fiches) + `technical-debt-solde/where-compare-textuellement.md` — vérif: `grep -rn 'contrat-liste\.md' .claude/implementation/todo/` ne rend que des mentions **historiques** du fichier supprimé (`renvois-sans-prefixe-hors-du-controle-des-ancres.md`, `deux-conventions-de-mode-de-defaillance.md`) et aucun renvoi vivant — le motif sans `.md` matche en plus le slug du chantier, cité en `source` des fiches qu'il a produites
- [x] 10. Complétude et suppression — `git rm contrat-liste.md` + l'inventaire — vérif: inventaire `COMPLET` + `python3 scripts/check_pipeline.py` + `grep -rn 'contrat-liste\.md' skills/ scripts/` sans résultat

## État courant

**Prochaine action** : clôture — audit par `implementation-auditor`, puis aplatissement. L'inventaire est gardé jusque-là (l'auditeur en a besoin) et supprimé à l'archivage.
**Vérification** : `python3 scripts/check_pipeline.py` ; `cd skills/list-dir/scripts && uvx pytest tests -q` ; inventaire `COMPLET`
**Dernier audit** : `476292a` — RÉSERVES — 2026-09-05
**Notes** : 193/193 règles affectées. `contrat-liste.md` supprimé. 440 tests passent, pipeline conforme. `plan-reviewer` a rendu NON CONFORME ; les trois points ont été tranchés avec
l'utilisateur avant démarrage (voir journal).

## Journal de décisions

- **2026-09-05** — Découpage en cinq fichiers par sujet : `format`, `definitions`, `provenance`,
  `operations`, `extension`. *Pourquoi* : la gêne est la dispersion, pas la taille — un sujet,
  une autorité. *Rejeté* : découpage par audience, qui redisperse `derive` et `validate`.
- **2026-09-05** — Les renvois entre fichiers voisins s'écrivent `../references/<f>.md#<ancre>`.
  *Pourquoi* : le contrôle 8 n'accepte que les chemins en `../` ; cette forme y fait entrer les
  renvois internes sans toucher `check_pipeline.py`. *Rejeté* : solder la dette du contrôle 8.
- **2026-09-05** — `migrate --dry-run` a pour autorité `operations.md`, pas `format.md`.
  *Pourquoi* : réserve R4 — une règle de `migrate` énoncée hors du fichier qui fait autorité sur
  `migrate` est la dispersion même que le chantier corrige.
- **2026-09-05** — `description` est obligatoire sur `[sections.*]`, facultative sur `[fields.*]`
  et à la racine (`contract.py:422` vs `:475`). Asymétrie non voulue, décrite dans `format.md` ;
  dette `description-obligatoire-sur-les-sections-seulement`. *Rejeté* : corriger le code ici — le
  sens de la symétrie n'est pas tranché, et « obligatoire partout » est cassant.
- **2026-09-05** — Les mentions de `contrat-liste.md` restées dans `todo/` sont des constats
  historiques, pas des renvois : le critère « aucun renvoi résiduel » vise les cibles à lire.
- **2026-09-05** — Audit de clôture `476292a` : RÉSERVES, aucun bloquant. R2, R4, R5 traitées ;
  R6 portée au registre ; R3 assumée — 828 → 834 lignes, le gain est dans la dispersion et le plus
  gros fichier (828 → 241), pas dans le volume.
