---
slug: description-obligatoire-partout
titre: « description » obligatoire sur les champs comme sur les sections
branche: description-obligatoire-partout
base: master
statut: terminé
session: 1
execution: délégué
plan: .claude/implementation/done/2026-09-06-description-obligatoire-partout.plan.md
brief: .claude/implementation/done/2026-09-06-description-obligatoire-partout.brief.md
audit: .claude/implementation/done/2026-09-06-description-obligatoire-partout.audit.md
créé: 2026-09-05
maj: 2026-09-06
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : un contrat déclare ses champs et ses sections sur le même modèle, mais `validate`
refuse une section sans `description` et laisse passer un champ sans. « L'asymétrie n'est pas
voulue. »

**But** : rendre la règle symétrique — `description` obligatoire sur les champs, les sections et
la racine du contrat — puis l'écrire dans `skills/list-dir/references/format.md` et solder la
dette `description-obligatoire-sur-les-sections-seulement`.

**Critères de réussite** :

- un contrat sans `description` sur un `[fields.*]` est refusé par `list-dir validate`, en nommant
  le champ, comme il l'est aujourd'hui pour une section
- `description = ""` reste accepté partout : c'est la **clé** qui est exigée, pas son texte
- `uv run --with pytest pytest skills/list-dir/scripts/tests` passe
- `format.md` ne décrit plus d'asymétrie et ne renvoie plus à cette dette
- la fiche de dette est passée en `technical-debt-solde`

**Hors-périmètre** :

- la dette `deux-conventions-de-mode-de-defaillance` — retirée du chantier : « l'autre induit une
  réécriture importante, propice à des modifications plus larges »
- aucune réécriture de prose dans `contrat.md`, `dette.md`, `debt-review/`

**Signaux de dérive** :

- si le chantier commence à réécrire de la prose de référence au-delà du paragraphe de `format.md`
  qui énonce la règle, s'arrêter
- si la correction des fixtures de test devient l'occasion de les remanier, s'arrêter — on ajoute
  une clé, on ne refactore pas

## Étapes

- [x] 1. Compléter les contrats produits par l'outil, les données et la doc — `store.py`, les 4 `templates/review.toml`, les 9 `contract.toml`, `format.md`, `operations.md` — vérif: `uv run --with pytest pytest skills/list-dir/scripts/tests -q`
- [x] 2. Compléter les fixtures de tests — `skills/list-dir/scripts/tests/` — vérif: `uv run --with pytest pytest skills/list-dir/scripts/tests -q`
- [x] 3. Exiger `description` dans `contract.py` (champ, racine) + tests de refus — `contract.py`, `test_contract.py` — vérif: `uv run --with pytest pytest skills/list-dir/scripts/tests -q`
- [x] 4. Écrire la règle dans `format.md` — `skills/list-dir/references/format.md` — vérif: `uv run scripts/check_pipeline.py`
- [x] 5. Solder la dette — `.claude/implementation/todo/technical-debt{,-solde}/` — vérif: `list-dir validate .claude/implementation/todo/technical-debt-solde`

## État courant

**Terminé.** Les 5 étapes sont faites, l'audit de clôture est passé, la dette est soldée et le
registre alimenté.

**Vérification** : `uv run --with pytest pytest skills/list-dir/scripts/tests -q` (444 passed ;
baseline d'origine : 440), `uv run scripts/check_pipeline.py` (8 contrôles verts) et `list-dir
validate` sur les 3 registres — 51 / 19 / 2 conformes à la clôture (46 / 19 / 2 après le solde de
l'étape 5, avant les 5 entrées de dette induite ; 47 / 18 / 2 avant le solde).

**Dernier audit** : `e441337` — RÉSERVES, aucun bloquant — 2026-09-05. Les deux réserves de
chiffres (R6, R7) ont été corrigées avant le commit de preuve. R1 à R5 sont versés au registre de
dette, l'utilisateur ayant choisi de clore avec.

## Journal de décisions

- **2026-09-06** — Clôture avec le verdict `RÉSERVES` : R1 (message de refus de la racine muet sur
  la racine) et R2 (préremplissage dans la semence de `test_reseed.py`) ne sont pas traités, mais
  versés au registre de dette avec R3, R4 et R5. *Pourquoi* : arbitrage de l'utilisateur, aucun
  bloquant, et les deux seules réserves chiffrées étaient déjà corrigées.

- **2026-09-05** — La suppression locale simulée par trois tests de `test_reseed.py` porte
  désormais sur `text = "titre par défaut"`, ajouté à `[fields.title]` de `SEMENCE`, et non plus
  sur `description`. *Pourquoi* : cette clé n'est plus supprimable sans invalider le contrat, et
  `reseed` échouait avant d'atteindre le comportement visé. *Conséquence assumée* : une liste
  dont le contrat local a perdu une `description` ne peut plus être re-semée.

- **2026-09-05** — Ce qui est exigé est la présence de la clé `description`, pas son contenu ;
  `description = ""` reste accepté partout. *Pourquoi* : rend un contrat à moitié documenté
  visible à la déclaration sans forcer à rédiger. *Rejeté* : exiger un texte non vide, qui
  invaliderait des contrats du dépôt.

- **2026-09-05** — `.list/backup/` n'est jamais corrigé, à la différence de `.list/semence/`.
  *Pourquoi* : un backup est l'instantané de ce qu'un `reseed` a remplacé, que rien ne relit ; le
  corriger le ferait mentir.
