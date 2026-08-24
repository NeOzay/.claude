---
slug: tests-listdir
titre: Suite de tests du paquet listdir
branche: tests-listdir
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-24-tests-listdir.plan.md
brief: .claude/implementation/done/2026-08-24-tests-listdir.brief.md
audit: .claude/implementation/done/2026-08-24-tests-listdir.audit.md
créé: 2026-08-24
maj: 2026-08-24
---

## Objectif et périmètre

Repris du brief (`brief:`).

**Symptôme** : le paquet `listdir` compte 19 modules et 2306 lignes sans aucun test. Deux défauts
de comportement ont été trouvés par un auditeur qui lisait le code, non par une commande, et « rien
ne garantit qu'un troisième ne dort pas ».

**But** : une suite `pytest` rejouable en une commande, qui remplace les preuves d'exécution
recopiées à la main dans les suivis de chantier et rend la non-régression gratuite.

**Critères de réussite** :
- les tests couvrent **la logique métier et les commandes** (dit)
- ils **garantissent et cadrent le comportement du module** (dit)
- pas de seuil de couverture chiffré : la couverture n'est pas l'objectif, le comportement l'est (dit)
- les tests vivent dans `skills/list-dir/scripts/tests/`, lancés par
  `uvx pytest skills/list-dir/scripts/tests -q` (arbitré)
- le gros des cas passe par la **bibliothèque importée** ; la CLI n'est exercée en sous-processus
  que pour ce qu'elle seule porte — codes de sortie, messages sur stderr, garde de version (arbitré)
- `uvx ruff check .` et `uvx --with pytest basedpyright` restent verts sur le skill
- « le mieux serait de corriger en même temps que les tests ; sinon, il faudrait en permanence
  réécrire les tests » (dit) — un comportement jugé faux se corrige DANS ce chantier, il ne se
  fige pas

**Hors-périmètre** :
- **`debt-review` et les trois registres de `todo/`** : consommateurs non testés ici (arbitré).
  `grep -ril 'dette\|debt' skills/list-dir/` doit rester sans résultat — invariant posé en 53eff2d.
- **Refonte du paquet** : aucune amélioration de testabilité, aucun découpage de module.
- **CI** : le dépôt n'en a pas ; ce chantier n'en crée pas.
- **Seuil de couverture chiffré** : écarté (dit).

**Signaux de dérive** :
- toute modification de `listdir/` qui n'est pas **la correction d'un comportement qu'un test
  nomme** s'arrête et se discute (arbitré)
- si le diff sur `listdir/` dépasse le diff sur les tests, la ligne est franchie (arbitré)
- si un test lit le vrai dépôt au lieu d'une arborescence montée sur `tmp_path`, c'est raté

## Étapes

- [x] 1. Amorçage : `conftest.py` et fixtures partagées — `skills/list-dir/scripts/tests/conftest.py`, `test_amorcage.py` — vérif: `uvx pytest skills/list-dir/scripts/tests -q`
- [x] 2. Lecture, sérialisation, frontière des deux règles — `tests/test_items.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_items.py -q`
- [x] 3. Le contrat et la confrontation d'une valeur — `tests/test_contract.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_contract.py -q`
- [x] 4. Lire, filtrer, valider — `tests/test_store_lecture.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_store_lecture.py -q`
- [x] 5. Créer et migrer — `tests/test_store_ecriture.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_store_ecriture.py -q`
- [x] 6. Projeter et agglomérer — `tests/test_derive_merge.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_derive_merge.py -q`
- [x] 7. Déplacer, sur un dépôt git jetable — `tests/test_move.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_move.py -q`
- [x] 8. Découverte, surcharge, dépendances — `tests/test_loader.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_loader.py -q`
- [x] 9. Ce que la CLI seule porte — `tests/test_entree_cli.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_entree_cli.py -q`
- [x] 10. Passe finale : linters, suite complète, invariant de généricité — vérif: bloc de l'étape 10 du plan

## État courant

**Prochaine action** : aucune — chantier clos le 2026-08-24.
**Vérification** : `uvx pytest skills/list-dir/scripts/tests -q`
**Dernier audit** : `f1923d2` — RÉSERVES — 2026-08-24
**Notes** : audit de clôture RÉSERVES, aucun bloquant. Les deux constats (R2 fence en préambule,
R3 collision des deux `conftest.py`) sont au registre de dette, sur arbitrage de l'utilisateur.

## Preuves d'exécution

Passe finale du 2026-08-24, depuis la racine du dépôt :

```
uvx pytest skills/list-dir/scripts/tests -q   → 241 passed
uvx pytest scripts/tests -q                   → 67 passed   (suite existante intacte)
(cd skills/list-dir && uvx ruff check .)      → All checks passed!
(cd skills/list-dir && uvx --with pytest basedpyright) → 0 errors, 0 warnings, 0 notes
uvx --with pytest basedpyright                → 0 errors, 0 warnings, 0 notes  (racine)
grep -ril 'dette\|debt' skills/list-dir/      → aucun résultat  (invariant tenu)
python3 scripts/check_pipeline.py             → Pipeline conforme, code 0
```

Diff cumulé `master...HEAD` : 2726 insertions. Part `listdir/` : **70 lignes sur 2 fichiers**.
Part `tests/` : 2270 lignes sur 11 fichiers. Le signal de dérive « diff sur `listdir/` supérieur au
diff sur les tests » n'a jamais été proche de se déclencher.

## Constats à verser au registre de dette à la clôture

- `derive` et `migrate` ne sont exercés que par la bibliothèque ; leurs `register()` et leurs
  drapeaux (`--template`, `--drop`, `--dry-run`) ne passent par aucun test de la CLI. Les huit
  autres commandes le sont. Reste de la réserve Q2 du relecteur de plan.
- La garde de version de `list-dir.py` est vérifiée par son RANG dans l'AST, faute d'un Python
  antérieur à 3.12 sur la machine : le message qu'elle imprime n'est jamais exécuté.

## Journal de décisions

- **2026-08-24** — Les tests vivent dans `skills/list-dir/scripts/tests/`, pas `skills/list-dir/tests/`
  comme l'annonçait l'entrée de dette. *Pourquoi* : symétrie avec `scripts/tests/`, et
  `pyrightconfig.json` (`include: ["scripts"]`) les couvre sans retouche.
- **2026-08-24** — Bibliothèque importée pour le gros des cas, sous-processus réservé à ce que la CLI
  seule porte. *Pourquoi* : `Result[T]` rend les échecs inspectables sans capturer de sortie.
  *Rejeté* : tout en sous-processus.
- **2026-08-24** — Les helpers de test vivent dans `tests/jouet.py`, jamais dans `conftest.py`.
  *Pourquoi* : deux suites du dépôt portent un `conftest.py`, et `from conftest import …` résolvait
  vers le mauvais. *Conséquence* : `extraPaths` élargi dans les deux `pyrightconfig.json`.
- **2026-08-24** — `fence-non-fermee-diagnostic-trompeur` traitée **partiellement** : la fence est
  nommée à sa source pour les blocs ouverts dans une section, pas pour ceux ouverts en préambule.
  *Pourquoi* : couvrir le préambule impose que `Item` conserve son corps brut — modification
  structurelle hors plan. L'entrée reste au registre, son Constat corrigé.
- **2026-08-24** — `where-compare-textuellement` soldée : comparaison textuelle conservée (voulue),
  mais un champ absent ne vaut plus la chaîne « None » ; le critère vide devient la forme explicite
  de l'absence. *Rejeté* : comparer sur les types déclarés — refonte de la sémantique de filtrage.
- **2026-08-24** — Clôture prononcée avec les réserves de l'audit, sur arbitrage de l'utilisateur.
  Trois entrées versées au registre : `deux-conftest-collision-collecte`, `derive-migrate-hors-cli`,
  `garde-version-jamais-executee`.
