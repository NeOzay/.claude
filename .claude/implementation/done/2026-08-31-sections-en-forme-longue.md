---
slug: sections-en-forme-longue
titre: Sections du contrat list-dir en forme longue
branche: sections-en-forme-longue
base: master
statut: terminé
session: 2
execution: délégué
plan: .claude/implementation/done/2026-08-31-sections-en-forme-longue.plan.md
brief: .claude/implementation/done/2026-08-31-sections-en-forme-longue.brief.md
audit: .claude/implementation/done/2026-08-31-sections-en-forme-longue.audit.md
créé: 2026-08-30
maj: 2026-08-31
---

## Objectif et périmètre

Repris du brief (`brief:`).

**Symptôme** : rien ne documente ce qu'il faut écrire dans les sections d'un élément.
`list-dir contract` sert une `description` par champ, mais `[sections]` n'est que deux listes de
noms — le corps, c'est-à-dire l'essentiel, n'a aucune doc là où l'outil la lit. « Il faudrait que
la documentation soit dans le "contract" ».

**But** : étendre le format `[sections]` en une table par section, sur le modèle de `[fields.*]`,
portant `required` et `description`, et ouverte à d'autres clés plus tard.

**Critères de réussite** :
- `list-dir contract <liste>` rend une description pour chaque section déclarée
- un contrat à l'ancien format échoue avec un message qui nomme la migration à faire
- une section sans clé `description` échoue ; `description = ""` passe
- le message renvoie à la semence de la liste ; la réécriture est manuelle
- `list-dir validate` passe sur les trois registres de dette et sur la liste de revue
- la suite `scripts/tests/` passe

**Hors-périmètre** :
- pas de clé de section au-delà de `required` et `description` — le format doit seulement les
  rendre possibles
- pas de nouvelle option de `contract` (pas de `--sections`)
- aucun outil de réécriture de contrat : ni `migrate --contract`, ni commande dédiée
- la prose d'en-tête de `templates/review.md` reste où elle est
- pas de rédaction du contenu des descriptions : tout migre à `description = ""`, la rédaction se
  fera dans son propre chantier

**Signaux de dérive** :
- si les deux formats coexistent, même transitoirement, c'est raté : l'ancien lève une erreur
- si une commande hors `contract`/`types` se met à connaître la forme du TOML, s'arrêter

## Étapes

- [x] 1. Le format en lecture (`Section`, `Contract.sections`, boucle de parsing) — `listdir/types.py`, `listdir/contract.py`, `tests/test_contract.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_contract.py -q`
- [x] 2. Le refus nommé de l'ancien format (remontée `name`, détection, message) — `listdir/contract.py`, `tests/test_contract.py` — vérif: `uvx pytest skills/list-dir/scripts/tests/test_contract.py -q`
- [x] 3. Consommateurs et fixtures (squelette d'`init`, 5 fichiers de tests) — `listdir/store.py`, `tests/` — vérif: `uvx pytest skills/list-dir/scripts/tests -q` + `uvx ruff check scripts`
- [x] 4. Migrer les 8 contrats du dépôt (4 semences, 4 copies en vigueur) — `skills/implementation-tracker/list-dir/`, `.claude/implementation/todo/` — vérif: `list-dir validate` sur les 3 registres + une liste de revue dérivée
- [x] 5. Documenter le format — `skills/list-dir/references/contrat-liste.md` — vérif: `grep -rn 'optional = \[' skills/ .claude/implementation/todo/` ne rend que `test_contract.py`

## État courant

**Prochaine action** : aucune — chantier clos.
**Vérification** : `uvx pytest skills/list-dir/scripts/tests -q` (307), `uvx ruff check scripts`,
`list-dir validate` sur les 3 registres + une liste de revue dérivée
**Dernier audit** : `752449e` — RÉSERVES — 2026-08-31
**Notes** : les 6 critères de réussite du brief sont vérifiés par exécution réelle. R1 (tableau des
marqueurs contredisant le nouveau format) et R5 (ligne trop longue) corrigées avant clôture, sur
arbitrage. R2/R3, R4 et le hors-périmètre assumé versés au registre de dette ; R7 a complété
`semence-et-copie-divergent-sans-controle`, déjà présente.

## Journal de décisions

- **2026-08-30** — l'ancien format lève une erreur au lieu d'être toléré en parallèle. *Pourquoi* :
  deux écritures d'une même chose divergent, et c'est la plus lisible qu'on croit. *Rejeté* :
  lecture des deux formes, qui rouvrait la double écriture qu'on ferme.
- **2026-08-30** — l'ordre du TOML ordonne les sections, en remplacement du « requises d'abord ».
  *Pourquoi* : le contrat porte désormais du sens par section, et l'ordre en fait partie.
- **2026-08-30** — le `name` du contrat est lu en tête de `parse_contract`, sous
  `contract_name` : le message de l'ancien format le cite, et les variables de boucle `name` /
  `description` des champs l'écraseraient sinon.
- **2026-08-30** — `description` est une clé obligatoire à valeur libre. *Pourquoi* : rendre
  visible qu'une section n'est pas documentée, sans imposer d'en rédiger le texte tout de suite.
- **2026-08-31** — pas de propriété `optional_sections` sur `Contract` ; les appelants dérivent le
  filtre depuis `sections.values()`. *Pourquoi* : `required_sections` suffisait aux besoins réels,
  une seconde propriété symétrique n'avait qu'un appelant de test. *Rejeté* : ajouter la propriété
  par symétrie avec l'étape 1.
