---
slug: check-pipeline-python
titre: Réécriture du garde-fou de pipeline en Python
branche: check-pipeline-python
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-24-check-pipeline-python.plan.md
brief: .claude/implementation/done/2026-08-24-check-pipeline-python.brief.md
audit: .claude/implementation/done/2026-08-24-check-pipeline-python.audit.md
créé: 2026-08-23
maj: 2026-08-24
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : `scripts/check-pipeline.sh` est en bash, hors de portée du typage statique qui
couvre le reste du code du dépôt, et porte des dettes connues.

**But** : réécrire le script en Python, le placer sous `pyrightconfig.json`, et corriger dans le
même mouvement les dettes existantes.

**Critères de réussite** :

- `python3 scripts/check_pipeline.py` → code 0 sur l'arbre du chantier, tous contrôles verts
- une suite de tests rejouable : unitaires par contrôle **et** injection bout-en-bout d'un défaut
  par contrôle, chacun donnant rouge
- `basedpyright` en mode `all` → 0 erreur, le nouveau code étant couvert par `pyrightconfig.json`
- les cinq dettes retenues sont soldées ou explicitement assumées

**Hors-périmètre** :

- pas de résolution dynamique du chemin de skill : la cause de `chemin-skill-code-en-dur` reste
  ouverte au registre
- `listdir` n'est ni touché ni testé
- `hooks/intent-brief-gate.sh` n'est pas migré — pédagogique et échoue ouvert, autre nature que le
  garde-fou
- les règles portées par `contrat.md` ne sont pas amendées

**Périmètre élargi le 2026-08-24**, sur réserve `R1` de l'audit de clôture : la ligne `ruff`,
`basedpyright` de `contrat.md` § Dépendances est corrigée en `uvx --with pytest basedpyright`. Le
chantier a rendu fausse une dépendance documentée ; la laisser fausse aurait fait rendre à tout
audit suivant un verdict amputé, ce que ce paragraphe du contrat existe précisément pour empêcher.

**Signaux de dérive** :

- si le diff touche `contrat.md` ou un `SKILL.md` au-delà de la ligne d'appel `bash`→`python3`,
  c'est raté : chantier d'outillage, pas de contenu de règles
- si un paquet importable façon `listdir` apparaît (couches, `Result[T]`, modules par
  responsabilité), c'est raté : deux scripts, pas une bibliothèque
- si le comportement d'un contrôle change sans qu'une dette retenue le demande — réécrire n'est pas
  redéfinir ce que le garde-fou juge
- si les tests débordent sur `listdir` : sa dette de tests est un autre chantier
- si une dette hors des cinq retenues se met à être soldée

## Étapes

- [x] 1. `impl_list.py` dans la skill, en-tête et chemin de renvoi corrigés — `skills/implementation-tracker/scripts/impl_list.py` — vérif: sortie identique au `.sh` sur `todo/`, `done/` et un répertoire absent
- [x] 2. Squelette du garde-fou — `scripts/check_pipeline.py` — vérif: s'exécute, annonce 0 contrôle exécuté, code ≠ 0
- [x] 3. Contrôle 1 et création de `scripts/tests/` — vérif: `uvx pytest scripts/tests -q` vert, dont l'injection d'un renvoi mort dans `CLAUDE.md` et `hooks/` ; 30 renvois résolvent sur le dépôt réel
- [x] 4. Contrôle 2 : occurrences et table `{section: [empreintes]}` — vérif: unitaires verts, 8 sections couvertes
- [x] 5. Contrôle 3 : chargement d'`impl_list.py` par `importlib` — vérif: unitaires verts, dont listing vide et script absent
- [x] 6. Contrôle 4 — vérif: unitaires verts, dont `agents/` absent → rouge
- [x] 7. Contrôle 5 — vérif: unitaires verts, dont champ pointant dans le vide → rouge
- [x] 8. Contrôle 6 : garde commandant l'appel, `re.escape` — vérif: 4 formes fautives rouges, 5 absolues vertes, faux positif `# [ -f x.sh ]` rouge
- [x] 9. Contrôle 7 : existence des chemins de skill — vérif: chemin inexistant injecté → rouge
- [x] 10. Test bout-en-bout par injection — vérif: 7 rouges attendus, 1 vert, code 1 puis 0
- [x] 11. Bascule des appels et suppression des deux `.sh` — `cloture.md`, `SKILL.md`, `contrat.md` — vérif: plus aucune mention hors archives ; contrôle 6 vert
- [x] 12. `pyrightconfig.json` élargi à `scripts` — vérif: `uvx basedpyright` → 0 erreur, `uvx ruff check` clean
- [x] 13. Dettes annexes : ancrage du renvoi de l'agent, `.pyc` orphelin supprimé — vérif: contrôle 4 vert, `scripts/__pycache__` vide
- [x] 14. Registre : quatre dettes soldées, `chemin-skill-code-en-dur` amendée — vérif: `list-dir.py validate` vert sur `technical-debt` et `technical-debt-solde`

- [x] 15. **Réserves `R2` et `R3` de l'audit de clôture** — le contrôle 1 ne juge que les `.md` versionnés ou versionnables (`git ls-files --cached --others --exclude-standard`), et `.claude/plans/` rejoint les zones exclues — vérif: `test_fichier_ignore_par_git_est_saute`, `test_plans_exclus` ; 67 tests verts
- [x] 16. **Réserve `R1`** — lanceur corrigé dans `contrat.md` § Dépendances, périmètre élargi — vérif: `uvx --with pytest basedpyright` → 0 erreur ; garde-fou rc 0

## État courant

**Prochaine action** : aucune — chantier clos.
**Vérification** : `python3 scripts/check_pipeline.py` → code 0 ; `uvx pytest scripts/tests -q`
**Dernier audit** : `1552f29` — RÉSERVES — 2026-08-24 (R1, R2, R3 traitées depuis)
**Notes** : le plan a été relu par `plan-reviewer` avant présentation — **NON CONFORME**, cinq
réserves tranchées avec l'utilisateur avant l'ouverture. L'audit de clôture a rendu **RÉSERVES** :
`R1`, `R2` et `R3` ont été traitées aux étapes 15 et 16, `R7` écartée (mémoïsation sans enjeu),
`R8` versée au registre sous `statusline-hors-des-linters`.

## Journal de décisions

- **2026-08-23** — les fichiers Python prennent un nom en underscore (`check_pipeline.py`), contre
  la lettre du brief. *Pourquoi* : les unitaires importent les fonctions de contrôle, ce qu'un nom à
  tiret interdit. *Rejeté* : chargement par `importlib` dans un `conftest.py`.
- **2026-08-23** — `impl_list.py` reste dans la skill, chargé par `importlib` depuis le garde-fou.
  *Pourquoi* : la skill s'invoque depuis n'importe quel dépôt et ne peut pas dépendre d'un
  `scripts/` local à celui-ci. *Rejeté* : déménagement à la racine, qui cassait son auto-suffisance.
- **2026-08-23** — le contrôle 1 exclut `agents/`, `.git/`, `plugins/` et `.claude/implementation/`.
  *Pourquoi* : archives et registre portent des renvois volontairement morts. *Conséquence* :
  l'extension de portée est invisible sur l'arbre actuel, elle ne se prouve que par un test.
- **2026-08-24** — le contrôle 1 ne juge que ce que git suit ou suivrait, jamais un fichier ignoré.
  *Pourquoi* : l'auteur d'un artefact déposé en répertoire ignoré ne peut pas le corriger — le rouge
  serait sans cause. *Rejeté* : allonger la liste d'exclusions, qui aurait grandi sans fin.
- **2026-08-24** — quatre dettes soldées, `chemin-skill-code-en-dur` amendée et laissée ouverte.
  *Pourquoi* : le contrôle 7 solde son symptôme, pas sa cause — le chemin de skill reste écrit en
  dur, et le contrôle 6 impose cette écriture.
