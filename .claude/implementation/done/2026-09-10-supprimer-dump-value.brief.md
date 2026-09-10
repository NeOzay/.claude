---
slug: supprimer-dump-value
titre: "Supprimer dump_value : faire passer ses deux derniers appelants par tomlkit"
statut: validé
execution: direct
créé: 2026-09-10
---

## Intention

**Symptôme** : deux écrivains TOML cohabitent dans `listdir` et ne répondent pas pareil à la même
question. Sur la **forme**, un saut de ligne s'écrit `"""…"""` par `toml_value` et `"a\\nb"` échappé
par `dump_value` ; sur le **fond**, un caractère de contrôle non blanc (`\x00`) est écrit et relu
exact par le premier, refusé par un message nommé par le second (dépôt: vérifié au cadrage le
2026-09-10 ; `test_store_ecriture.py:389` et `:394`).

*Correction du 2026-09-10, brief rouvert sur décision de l'utilisateur* : ce symptôme disait
d'abord qu'un saut de ligne « lève `SerialiseError` par `dump_value` ». C'est faux — `dump_value`
l'échappe via `ESCAPES` avant son contrôle de caractères de contrôle. L'erreur venait de l'entrée
de dette `deux-ecrivains-toml-coexistent` et de l'entrée de road-map, qui la portent toutes deux
et restent à corriger à la clôture.
**But** : n'en garder qu'un. Faire passer `store.init_list` et `provenance.emit` par tomlkit, puis
retirer `dump_value`, `ESCAPES` et leurs tests. Et poser la règle d'écriture des chaînes, valable
partout : « ces strings sont faites pour être lues par un humain ou l'agent, mise en forme
multiligne et caractères blancs autorisés — je les autorise partout sauf dans les objets (liste,
dictionnaire) » (dit).

## Critères de réussite

- `grep -rn "dump_value\|ESCAPES" skills/list-dir/scripts/` ne rend plus rien (dépôt: dette)
- `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/` reste vert
- l'en-tête d'`items.py` n'annonce plus deux écrivains (dépôt: items.py:20-22)
- une chaîne scalaire à saut de ligne s'écrit `"""…"""` ; la même **dans une liste** s'écrit
  échappée sur une ligne (`"a\\nb"`) et se relit identique (dit ; rendu vérifié avec
  `tomlkit.string(v, multiline=False)`)

## Hors-périmètre

- pas de refonte de la représentation plate de la fusion : `flatten`, `_couper`, `_cle` et les clés
  pointées restent tels quels (proposé, validé)
- `reseed` et la détection de conflits ne sont pas touchés (proposé, validé)
- la **lecture** du contrat n'est pas touchée — `contract.py` a ses propres dettes ouvertes, dont
  `parsing-du-contrat-avale-les-cles-inconnues` (proposé, validé)
- les contrats déjà présents dans le dépôt ne sont pas corrigés (proposé, validé)

## Signaux de dérive

- si `flatten`, `_couper` ou `_cle` apparaissent dans le diff, s'arrêter — c'est l'option B qui
  rentre par la fenêtre (proposé, validé)
- si un test de `test_reseed.py` ou `test_fusion.py` doit être modifié pour passer, s'arrêter — le
  chantier ne devait rien changer à la fusion (proposé, validé)
- si `ESCAPES` se retrouve en deux exemplaires, s'arrêter — c'est exactement ce que la dette
  reprochait (proposé, validé)
- si le diff dépasse `items.py`, `store.py`, `provenance.py` et leurs tests, s'arrêter
  (proposé, validé)

## Contraintes connues de l'utilisateur

- **Comment vivent les contrats** : « les contrats sont modifiés par édition du fichier. La seule
  règle intransigeante est que, lors de la première semence, le résultat doit être identique à la
  graine. Le réensemencement ne peut être fait qu'en l'absence de conflit entre la graine et la
  cible » (dit). Vérifié : le chemin qui tient cette règle — `init_list` avec définition — recopie
  le texte sans sérialiseur (dépôt: store.py:796-800) ; le squelette qui appelle `dump_value`
  n'écrit pas de semence ; `emit` n'écrit que sur re-semis sans conflit (dépôt:
  provenance.py:625-637). Le chantier ne peut donc pas atteindre cet invariant, et la mise en forme
  produite par `emit` est libre (dépôt: test_reseed.py:340-351, R7)

- **Zones ouvertes ici, fermées avant** : l'écriture des contrats et `provenance.py` étaient un
  signal de dérive du chantier précédent ; ici c'est l'objet même de la tâche
  (dépôt: road-map `supprimer-dump-value`)
- **À traiter à part** : `ESCAPES` sert dans `provenance._titre` à échapper un **nom** de champ,
  pas une valeur — cas distinct (dépôt: provenance.py:306,328)
- **Règle générale, pas locale au contrat** : la règle « pas de multiligne dans un objet » vaut pour
  tout ce que `listdir` écrit. Elle corrige donc `toml_value`, qui propage aujourd'hui le multiligne
  dans les éléments d'une liste (`["""a\\nb""", "c"]`) — et par là le front matter des éléments via
  `dump_front`, hors du périmètre annoncé par la dette (dit, sur signalement de l'écart)

## Arbitrages tranchés au cadrage

- **`emit` garde son assemblage de texte** : seul le membre droit du `=` change d'écrivain
  (`tomlkit.item(toml_value(v, feuille)).as_string()`). *Rejeté* : reconstruire le contrat comme un
  document tomlkit — il faudrait dé-citer et dés-échapper chaque segment de clé, c'est-à-dire écrire
  la réciproque exacte de `_titre` dans le seul endroit du paquet où une erreur est silencieuse
  (une adresse mal reconstruite invente ou masque un conflit de fusion)
- **`ESCAPES` déménage dans `provenance.py`**, auprès de son unique appelant restant, `_titre`, qui
  échappe des **noms** de table. L'objection de `provenance.py:306` (« deux tables qui se
  ressemblent finissent par diverger ») visait une duplication qui n'existe plus une fois
  `dump_value` supprimé. *Rejeté* : `tomlkit.key`, qui cite selon la forme du nom (`fields.id` nu,
  `sections."Pour solder"` cité) alors que `_titre` cite TOUJOURS — vérifié

## Incertitudes à lever en plan

- les caractères de contrôle **non blancs** (`\x00`, `\x1b`) : l'utilisateur a autorisé le
  multiligne et les blancs, sans se prononcer sur ceux-là. `dump_value` les refuse par un message
  nommé, `toml_value` les échappe (`"a\\u0000b"`, relu exact — vérifié). Sa suppression retire donc
  un refus que personne n'a décidé de retirer : le plan doit dire s'il le réimplante et où
