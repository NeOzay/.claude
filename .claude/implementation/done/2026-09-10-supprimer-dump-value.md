---
slug: supprimer-dump-value
titre: "Supprimer dump_value : un seul écrivain TOML dans listdir"
branche: supprimer-dump-value
base: master
statut: terminé
session: 2
execution: direct
plan: .claude/implementation/done/2026-09-10-supprimer-dump-value.plan.md
brief: .claude/implementation/done/2026-09-10-supprimer-dump-value.brief.md
audit: .claude/implementation/done/2026-09-10-supprimer-dump-value.audit.md
road-map: supprimer-dump-value
créé: 2026-09-10
maj: 2026-09-10
---

## Objectif et périmètre

Repris du brief (`brief:`).

**Symptôme** : deux écrivains TOML cohabitent dans `listdir` et ne répondent pas pareil à la même
question. Sur la **forme**, un saut de ligne s'écrit `"""…"""` par `toml_value` et `"a\nb"` échappé
par `dump_value` ; sur le **fond**, un caractère de contrôle non blanc (`\x00`) est écrit et relu
exact par le premier, refusé par un message nommé par le second.

**But** : n'en garder qu'un. Faire passer `store.init_list` et `provenance.emit` par tomlkit, puis
retirer `dump_value`, `ESCAPES` et leurs tests. Et poser la règle d'écriture des chaînes, valable
partout : mise en forme multiligne et caractères blancs autorisés, sauf dans les objets (liste,
dictionnaire) ; caractères de contrôle non blancs refusés partout.

**Critères de réussite** :

- `git grep -n "dump_value\|ESCAPES" -- skills/list-dir/scripts/` ne rend plus rien
- `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` reste vert
- l'en-tête d'`items.py` n'annonce plus deux écrivains
- une chaîne scalaire à saut de ligne s'écrit `"""…"""` ; la même **dans une liste** s'écrit
  échappée sur une ligne et se relit identique

**Hors-périmètre** :

- pas de refonte de la représentation plate de la fusion : `flatten`, `_couper`, `_cle` et les clés
  pointées restent tels quels
- `reseed` et la détection de conflits ne sont pas touchés
- la **lecture** du contrat n'est pas touchée — `contract.py` a ses propres dettes ouvertes
- les contrats déjà présents dans le dépôt ne sont pas corrigés

**Signaux de dérive** :

- si `flatten`, `_couper` ou `_cle` apparaissent dans le diff, s'arrêter
- si un test de `test_reseed.py` ou `test_fusion.py` doit être modifié pour passer, s'arrêter
- si `ESCAPES` se retrouve en deux exemplaires, s'arrêter
- si le diff dépasse `items.py`, `store.py`, `provenance.py` et leurs tests, s'arrêter

## Étapes

- [x] 1. `toml_value` porte la règle des chaînes — `listdir/items.py`, `tests/test_items.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_items.py`
- [x] 2. `emit` passe par tomlkit, la table d'échappements déménage — `listdir/provenance.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_fusion.py skills/list-dir/scripts/tests/test_provenance.py skills/list-dir/scripts/tests/test_reseed.py`
- [x] 3. `init_list` passe par tomlkit — `listdir/store.py`, `tests/test_store_ecriture.py` — vérif: `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_store_ecriture.py`
- [x] 4. Supprimer `dump_value`, `ESCAPES` et leurs tests — `listdir/items.py`, `tests/test_items.py` — vérif: `git grep -n "dump_value\|ESCAPES" -- skills/list-dir/scripts/` vide + suite complète

## État courant

**Prochaine action** : aucune — chantier terminé, clôturé le 2026-09-10.

**Vérification** : `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/`
→ 447 passés ; `git grep -n "dump_value\|ESCAPES" -- skills/list-dir/scripts/` → vide ;
`uvx ruff check` et `uvx --with pytest basedpyright` sans régression sur `master`.

**Dernier audit** : `a86645` — RÉSERVES — 2026-09-10 (trois passes : `471d58b` R1+R2 traités,
`f6ca5b8` R7 traité, `a86645` R4/R6/R8 arbitrés).

**Notes** : R6 est soldé — l'entrée de dette portait bien l'affirmation fausse et a été rectifiée
avant sa sortie ; l'entrée de road-map, elle, ne la portait pas en propre, elle déléguait l'énoncé
à la dette. R4 et R8 sont partis au registre de dette sur arbitrage de l'utilisateur.

## Journal de décisions

- **2026-09-10** — `emit` garde son assemblage de texte ; seul le membre droit du `=` change
  d'écrivain. *Pourquoi* : un document tomlkit exigerait de dé-citer chaque segment de clé, réciproque
  exacte de `_titre`, là où une erreur invente ou masque un conflit de fusion. *Rejeté* : reconstruire
  le contrat comme document tomlkit.
- **2026-09-10** — la règle des chaînes est portée par `toml_value`, donc vaut aussi pour le front
  matter des éléments. *Pourquoi* : décision de l'utilisateur, « la règle est générale ». *Rejeté* :
  la borner aux contrats, ce qui laissait deux comportements.
- **2026-09-10** — les caractères de contrôle non blancs sont refusés partout. *Pourquoi* : blancs
  autorisés, le reste non ; garde le refus nommé de `test_store_ecriture.py:394`. *Rejeté* : les
  échapper comme tomlkit le fait aujourd'hui pour les éléments.
- **2026-09-10** — une valeur portant un `\r` ne part jamais en `"""…"""`, quelle que soit sa mise
  en forme. *Pourquoi* : la grammaire TOML normalise CRLF en LF dans une chaîne multiligne, donc
  cette forme perd le `\r` en silence ; échappée sur une ligne, la valeur se relit exacte. *Rejeté* :
  refuser le `\r`, ou accepter la perte.
- **2026-09-10** — la table d'échappements de `_titre` vit dans `provenance.py` sous le nom
  `ECHAPPEMENTS_DE_NOM`. *Pourquoi* : elle échappe un nom de table, pas une valeur, et l'écrivain
  de valeurs (tomlkit) ne rend plus de table à emprunter. *Rejeté* : la garder dans `items.py`.
- **2026-09-10** — la règle des chaînes vit dans `toml_value`, `toml_text` n'en porte aucune.
  *Pourquoi* : un second point d'entrée qui déciderait quoi que ce soit recréerait les deux
  écrivains qu'on supprime. *Rejeté* : appeler `tomlkit.item(...).as_string()` chez les appelants.
- **2026-09-10** — brief rouvert pour corriger son symptôme, faux (le saut de ligne n'était pas
  refusé par `dump_value`). *Pourquoi* : préférer un brief juste à la trace de l'erreur. *Rejeté* :
  corriger dans le suivi en laissant le brief figé.
- **2026-09-10** — clôture avec les réserves R4 et R8, versées au registre de dette. *Pourquoi* :
  arbitrage de l'utilisateur, trois lignes de test ne valant pas une quatrième passe d'audit.
  *Rejeté* : ajouter le test puis réauditer.
