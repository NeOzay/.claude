---
slug: tests-listdir
titre: Suite de tests du paquet listdir
statut: validé
execution: direct
créé: 2026-08-24
---

## Intention

**Symptôme** : le paquet `listdir` compte 19 modules et 2306 lignes sans aucun test (dépôt:
skills/list-dir/scripts/listdir/). Deux défauts de comportement ont été trouvés par un auditeur
qui lisait le code, non par une commande, et « rien ne garantit qu'un troisième ne dort pas »
(dépôt: .claude/implementation/todo/technical-debt/listdir-sans-suite-de-tests.md).

**But** : une suite `pytest` rejouable en une commande, qui remplace les preuves d'exécution
recopiées à la main dans les suivis de chantier et rend la non-régression gratuite.

## Critères de réussite

- les tests couvrent **la logique métier et les commandes** (dit)
- ils **garantissent et cadrent le comportement du module** (dit)
- pas de seuil de couverture chiffré : la couverture n'est pas l'objectif, le comportement l'est (dit)
- les tests vivent dans `skills/list-dir/scripts/tests/`, lancés par
  `uvx pytest skills/list-dir/scripts/tests -q` (arbitré) — symétrie avec `scripts/tests/`, et
  `pyrightconfig.json` (`include: ["scripts"]`) les couvre sans retouche
- le gros des cas passe par la **bibliothèque importée** ; la CLI n'est exercée en sous-processus
  que pour ce qu'elle seule porte — codes de sortie, messages sur stderr, garde de version
  Python (arbitré)
- `uvx ruff check .` et `uvx --with pytest basedpyright` restent verts sur le skill (dépôt: skills/implementation-tracker/references/contrat.md)
- « le mieux serait de corriger en même temps que les tests ; sinon, il faudrait en permanence
  réécrire les tests » (dit) — un comportement jugé faux se corrige DANS ce chantier, il ne se
  fige pas

## Hors-périmètre

- **`debt-review` et les trois registres de `todo/`** : consommateurs non testés ici (arbitré). On
  teste le paquet générique. `grep -ril 'dette\|debt' skills/list-dir/` doit rester sans résultat —
  invariant posé en 53eff2d.
- **Refonte du paquet** : aucune amélioration de testabilité, aucun découpage de module (arbitré). Voir les
  signaux de dérive.
- **CI** : le dépôt n'en a pas (dépôt: `.github/workflows` absent) ; ce chantier n'en crée pas.
- **Seuil de couverture chiffré** : écarté (dit).

## Signaux de dérive

- toute modification de `listdir/` qui n'est pas **la correction d'un comportement qu'un test
  nomme** s'arrête et se discute (arbitré) — c'est la ligne entre « corriger en même temps » et
  refondre le paquet
- si le diff sur `listdir/` dépasse le diff sur les tests, la ligne est franchie (arbitré)
- si un test lit le vrai dépôt au lieu d'une arborescence montée sur `tmp_path`, c'est raté
  (dépôt: scripts/tests/conftest.py — « un contrôle qui passerait au vert seulement ici serait
  invérifiable »)

## Contraintes connues de l'utilisateur

- **Réutiliser** : le paquet est importable sans la CLI, `Result[T]` rend les échecs inspectables
  sans capturer de sortie (dépôt: skills/list-dir/scripts/listdir/__init__.py, types.py)
- **Déploiement** : `ruff.toml` et `pyrightconfig.json` vivent au niveau du skill, « parce que ce
  skill est destiné à être déployé ailleurs : sa configuration doit voyager avec lui »
  (dépôt: skills/list-dir/ruff.toml)
- **Tests existants à imiter** : « il y a déjà des tests dans ce dépôt » (dit) — `scripts/tests/`,
  7 fichiers issus de c71e6fe : dépôt-jouet sur `tmp_path`, `sys.path.insert` dans `conftest.py`,
  aucun test ne lit le vrai dépôt (dépôt: scripts/tests/conftest.py)
- **Outillage arrêté** : `uvx pytest <chemin> -q`, et `uvx --with pytest basedpyright` — sans
  `--with pytest`, 52 erreurs d'import non résolu noient les vraies (dépôt:
  skills/implementation-tracker/references/contrat.md, table des dépendances)
- **Référence de départ** : « on peut prendre le brief utilisé lors de la création de ce
  module » (dit) — `.claude/implementation/done/2026-08-23-format-registres.brief.md`, dont les
  critères de réussite décrivent déjà le comportement attendu bout en bout

## Incertitudes à lever en plan

- **Combien de correctifs dorment** : le chantier corrige ce que les tests révèlent, donc son
  volume réel n'est pas connu avant d'avoir écrit les tests. Si les correctifs s'accumulent au
  point de dépasser les tests en volume, le signal de dérive se déclenche et l'arbitrage revient
  à l'utilisateur.
