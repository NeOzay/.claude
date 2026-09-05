---
slug: provenance-listes-derivees
titre: Provenance des listes dérivées
branche: provenance-listes-derivees
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-09-05-provenance-listes-derivees.plan.md
brief: .claude/implementation/done/2026-09-05-provenance-listes-derivees.brief.md
audit: .claude/implementation/done/2026-09-05-provenance-listes-derivees.audit.md
créé: 2026-09-05
maj: 2026-09-05
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : « le dernier chantier a permis de mettre à jour les contracts des list-dir, mais il
ne prend pas bien en charge les listes dérivées. `review.toml` ne possède pas d'origine. »

**But** : qu'une liste engendrée par `derive` déclare d'où elle vient, sous le format
`liste-mère/liste-dérivée` (ex. `technical-debt/review`), « pour retrouver la graine d'une liste
dérivée ». L'estampille est **documentaire** : elle nomme le gabarit source pour qu'un lecteur sache
quoi taper, elle ne devient pas une définition résolvable.

**Critères de réussite** :

- `list-dir derive <registre> <rev> --template review` puis `list-dir validate <rev>` → rc 0 et
  **aucun avertissement** sur stderr (aujourd'hui : « aucune provenance déclarée » sur 43 fiches)
- une estampille malformée est refusée en nommant la clé — `def = "a/b/c"`, `def = "a/"`,
  `def = "../x"` font sortir `validate` non nul
- une dérivée non gelée dont l'estampille est composite ne s'entend plus dire « définition
  introuvable dans les quatre rangs » : le message dit qu'un nom composite désigne un gabarit
- `uvx pytest skills/list-dir/scripts/tests -q` passe (428 tests aujourd'hui)
- `(cd skills/list-dir && uvx --with pytest basedpyright)` → 0 error

**Hors-périmètre** :

- pas de `init --def technical-debt/review` : les templates transforment une liste existante
- le nom composite n'est **pas** une définition résolvable
- pas de `list-dir contract <rev> --seed` ni d'aucune commande qui suivrait l'estampille
- l'**instance** source du `derive` n'entre pas dans `[origin]` : elle n'est connue qu'au moment du
  `derive`, l'écrire romprait « `init` n'écrit jamais cette table, il la reçoit »
- `derive` n'écrit pas de `.list/semence/` : une dérivée gelée n'a rien à rattraper

**Signaux de dérive** :

- si une commande ou une option nouvelle apparaît, c'est raté : le chantier est une règle de
  format, un message honnête et de la doctrine
- si `derive` se met à écrire tout ou partie de l'estampille au lieu de la recopier, s'arrêter
- si `resolve()` doit rendre autre chose qu'un répertoire de définition, c'est qu'on refait
  l'option écartée

## Étapes

- [x] 1. Valider le format d'un nom d'estampille — `scripts/listdir/{contract.py,types.py}`, `scripts/tests/test_provenance.py` — vérif: `uvx pytest skills/list-dir/scripts/tests -q && (cd skills/list-dir && uvx --with pytest basedpyright)`
- [x] 2. Dire la vérité sur un nom composite là où il serait résolu — `scripts/listdir/{definitions.py,provenance.py}`, `scripts/tests/{test_provenance.py,test_definitions.py}` — vérif: `uvx pytest skills/list-dir/scripts/tests -q && (cd skills/list-dir && uvx --with pytest basedpyright)`
- [x] 3. Garder la dérivée silencieuse par un test — `scripts/tests/test_derive_merge.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_derive_merge.py -q`
- [x] 4. Estampiller `review.toml` et rattraper le registre — `skills/implementation-tracker/list-dir/technical-debt/{contract.toml,templates/review.toml}` — vérif: `list-dir validate .claude/implementation/todo/technical-debt` rc 0 sans avertissement
- [x] 5. Écrire la doctrine — `skills/list-dir/references/contrat-liste.md`, `skills/list-dir/SKILL.md` — vérif: `uvx pytest skills/list-dir/scripts/tests -q` + contrôle d'ancre

## État courant

**Prochaine action** : aucune — chantier clos.
**Vérification** : `uvx pytest skills/list-dir/scripts/tests -q`
**Dernier audit** : `5fe8927` — RÉSERVES — 2026-09-05
**Notes** : clos sur RÉSERVES, l'utilisateur ayant accepté la substitution de critère de R1.
R2 et R3 corrigés avant clôture, R4 déposé au registre (2 entrées), R5 assumée.

## Journal de décisions

- **2026-09-05** — clôture sur RÉSERVES : le critère « basedpyright → 0 error » du brief est
  remplacé par « aucune erreur ajoutée ». *Pourquoi* : les 13 erreurs sont préexistantes, prouvées
  par extraction de `master`. *Rejeté* : les traiter ici — hors périmètre, entrée au registre.

- **2026-09-05** — la règle de forme d'un `origin.def` vit dans `types.nom_mal_forme`, appelée par
  `_origin` et par `resolve`. *Pourquoi* : audit R2 — `resolve` jugeait sur le seul `/` et
  conseillait « --template  » (vide) sur `technical-debt/`. *Rejeté* : dupliquer le contrôle.

- **2026-09-05** — HORS PÉRIMÈTRE, pour le registre de dette : `basedpyright` 1.39.10 rend 13
  erreurs sur `provenance.py` (4) et `test_prefill.py` (9), là où l'audit du 2026-09-03 en relevait
  0. Préexistantes au chantier, vérifiées par `git stash` ; probable montée de version de l'outil.

- **2026-09-05** — l'estampille d'une dérivée est documentaire, pas résolvable : `mère/dérivée`
  nomme le gabarit source, `resolve()` la refuse. *Pourquoi* : « les templates existent pour
  réaliser une transformation sur une liste existante ». *Rejeté* : `init --def a/b`, et une
  commande qui suivrait l'estampille.
- **2026-09-05** — une liste dérivée naît gelée, par `frozen = true` déclaré dans le gabarit.
  *Pourquoi* : elle est jetable, « pas d'utilité à les mettre à jour ». *Rejeté* : un `--frozen`
  sur `derive`, qui ferait écrire l'estampille au lieu de la recevoir.
- **2026-09-05** — l'instance source du `derive` n'entre pas dans `[origin]`. *Pourquoi* : elle
  n'est connue qu'au moment du `derive`, et un chemin dépend de la machine. *Rejeté* : l'y mettre ;
  sa place serait un champ prérempli.
