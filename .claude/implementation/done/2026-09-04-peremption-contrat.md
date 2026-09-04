---
slug: peremption-contrat
titre: Provenance et péremption du contrat d'une liste semée
branche: peremption-contrat
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-09-04-peremption-contrat.plan.md
brief: .claude/implementation/done/2026-09-04-peremption-contrat.brief.md
audit: .claude/implementation/done/2026-09-04-peremption-contrat.audit.md
créé: 2026-09-04
maj: 2026-09-04
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : une skill s'attend à ce que le contrat d'une liste soit identique à sa semence ;
dès que la semence est modifiée, il y a divergence, et rien ne la signale.
**But** : « on conserve la main locale, tout en surveillant le risque de péremption » — la copie
reste la seule appliquée, mais on sait d'où elle vient, à quelle version, et si la définition a
bougé depuis.

**Critères de réussite** :

- après `list-dir init <cible> --def <nom>`, `diff <définition>/contract.toml
  <cible>/.list/contract.toml` reste muet — `[origin]` compris
- `list-dir validate` sur une liste dont la semence a été incrémentée affiche l'avertissement de
  péremption **et conserve son code de retour**
- `frozen = true` fait disparaître l'avertissement de péremption, et fait **refuser** `reseed` ;
  `reseed --force` passe outre
- `list-dir reseed <liste>` sauvegarde le contrat d'origine, injecte les apports de la semence,
  et sort **non nul en nommant les clés** dès qu'une même clé a bougé des deux côtés
- `reseed <liste> --def <nom>` sur une liste sans `[origin]` l'estampille à la version de la
  semence, apports injectés
- `validate` sur une liste sans `[origin]` signale l'absence de provenance ; `def = false` la tait
- le squelette d'`init` sans `--def` porte `def = false` ; `init --def <nom>` sur une semence qui
  déclare un autre nom échoue en code 2
- `pytest` passe ; `ruff` et `pyright` restent propres
- les trois définitions d'`implementation-tracker` portent une version, et les trois listes de
  `.claude/implementation/todo/` sont estampillées sans être modifiées autrement

**Hors-périmètre** :

- aucun re-semis automatique : rien ne resynchronise une liste sans qu'on l'ait demandé
- une liste qui **référence** sa semence — écarté, la résolution dépend de la machine
- `reseed` ne touche pas aux éléments `*.md` : c'est le travail de `migrate`
- `debt-review`, `road-map` et le reste du pipeline ne sont pas retouchés

**Signaux de dérive** :

- si une commande **autre que** `reseed` et l'avertissement de `validate` se met à résoudre une
  définition, c'est raté
- si l'avertissement de péremption devient un échec, c'est raté
- si `reseed` résout un conflit tout seul, c'est raté : il refuse et nomme les clés
- si `reseed` écrit dans une liste `frozen` sans `--force`, c'est raté
- si la copie cesse d'être octet pour octet égale à sa semence pour une autre raison que `frozen`,
  c'est raté

## Étapes

- [x] 1. `[origin]` au contrat — `scripts/listdir/types.py`, `contract.py` — vérif: `uvx pytest scripts/tests/test_provenance.py scripts/tests/test_contract.py -q`
- [x] 2. `init` : estampille reçue, semence pristine, contrôle du nom — `scripts/listdir/store.py`, `commands/init.py` — vérif: `uvx pytest scripts/tests -q`
- [x] 3. Les avertissements — `scripts/listdir/provenance.py`, `commands/validate.py`, `list-dir.py` — vérif: `uvx pytest scripts/tests -q`
- [x] 4. Émetteur TOML et moteur de fusion — `scripts/listdir/provenance.py` — vérif: `uvx pytest scripts/tests/test_fusion.py -q`
- [x] 5. La commande `reseed` — `scripts/listdir/commands/reseed.py` — vérif: `uvx pytest scripts/tests/test_reseed.py -q`
- [x] 6. Le mode adoption — `scripts/listdir/provenance.py`, `commands/reseed.py` — vérif: `uvx pytest scripts/tests/test_reseed.py -q`
- [x] 7. Documentation — `references/contrat-liste.md`, `SKILL.md`, `implementation-tracker/references/dette.md` — vérif: `grep -rn "douze" skills/list-dir/SKILL.md` sans résultat
- [x] 8. Adoption dans ce dépôt — `implementation-tracker/list-dir/*/contract.toml`, `.claude/implementation/todo/*` — vérif: boucle `diff` + `validate` du plan, code 0 et stderr vide

## État courant

**Prochaine action** : aucune — chantier clos. R1 à R3 et R7 à R19 sont levés ; R4, R5, R6 et R8
sont au registre de dette.
**Vérification** : `cd skills/list-dir && uvx pytest scripts/tests -q && uvx ruff check scripts && uvx pyright`
**Dernier audit** : `7a9fe62` — RÉSERVES — 2026-09-04 (7e passage ; `5d4a4d8` DÉFAVORABLE, les
suivants RÉSERVES). R18 et R19 ont été traités après lui, sans nouvel audit, sur arbitrage de
l'utilisateur : deux messages d'erreur, tests à l'appui.
**Notes** : les tests tournent par `uvx pytest` — le Python du PATH est un 3.14 sans pytest
installé. Deux gates du plan ne sont pas propres **avant** ce chantier, et ne le seront pas après :
`uvx ruff format --check` signale 4 fichiers (le dépôt coupe ses longs messages à la main), et
`uvx pyright` rend 9 erreurs (pytest non résolu dans l'environnement uvx, plus un défaut ancien de
`test_prefill.py:127`). Les fichiers touchés par ce chantier, eux, doivent rester à zéro.

## Journal de décisions

- **2026-09-04** — tout nom entrant dans une clé plate passe par `_cle` ou `_titre`, à tous les
  étages. *Pourquoi* : la même faute est ressortie trois fois à trois niveaux (R14, R16, R17), et
  `parse_contract` ne refuse une clé inconnue que dans `[origin]` — partout ailleurs un nom écrit à
  la main traverse la lecture et revient à l'écriture. *Rejeté* : colmater la variante signalée,
  qui appelait un quatrième tour.
- **2026-09-04** — une clé supprimée localement reste supprimée. *Pourquoi* : la suppression est
  une modification comme une autre, et le contrat local est déjà validé avant la fusion — ce que le
  parseur refuse de perdre ne peut donc pas avoir été supprimé. *Rejeté* : que la semence la repose,
  qui ferait de `reseed` un aligneur là où il est un rattrapeur.
- **2026-09-04** — sept audits de clôture : `5d4a4d8` DÉFAVORABLE (R1, R2), puis six RÉSERVES.
  Dix-neuf constats, quinze traités. *Contraint la suite* : R4, R5, R6 et R8 sont au registre de
  dette, et la couverture CLI de `reseed` (R4) est le trou qui a laissé passer le premier bloquant.

- **2026-09-04** — `[origin]` vit dans le `contract.toml`, et la semence le porte aussi.
  *Pourquoi* : la copie reste octet pour octet égale à sa semence, invariant que défend
  `init_list`. *Rejeté* : un `.list/origin.toml` séparé, et une liste qui référence sa semence
  (résolution dépendante de la machine).
- **2026-09-04** — `.list/semence/` garde la semence intacte au dernier semis. *Pourquoi* : sans
  ce point de référence, `reseed` ne peut pas distinguer un apport de la semence d'une édition
  locale, et toute évolution de semence deviendrait un conflit. *Rejeté* : comparaison directe
  semence ↔ liste, qui aurait fait de `--force` le geste courant.
- **2026-09-04** — `.list/backup/` est ignoré par git (`**/.list/backup/`), `.list/semence/` est
  versionné. *Pourquoi* : la sauvegarde est une marche arrière locale, l'historique long est le
  travail de git ; la semence, elle, doit suivre le clone pour que la fusion garde son troisième
  point. *Rejeté* : versionner les deux, qui ajoutait un contrat périmé en double à chaque re-semis.
- **2026-09-04** — le mode adoption n'a coûté aucun code : la fusion avec une base vide donne
  exactement la règle voulue, et l'estampille arrive comme n'importe quelle clé absente localement.
  *Pourquoi* : une seule voie de code à tester. *Rejeté* : une branche « adoption » séparée.
- **2026-09-04** — `--force` ne fait que dégeler une liste `frozen` ; un conflit refuse toujours.
  *Pourquoi* : le brief ne lui confie aucun arbitrage, et « aucune résolution automatique » est un
  signal de dérive. *Rejeté* : un `--force` qui tranche aussi en faveur de la semence.
