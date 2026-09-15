---
slug: git-smart-commit-trois-commits
titre: Découper git-smart-commit en trois types de commits
statut: validé
execution: direct
créé: 2026-09-14
---

## Intention

**Symptôme** : `git-smart-commit` est un skill ancien, créé avant `implementation-tracker` (dit).
Son `SKILL.md` mêle le workflow général et le cas d'aplatissement, renvoyé en fin de fichier vers
`references/squash.md` (dépôt: skills/git-smart-commit/SKILL.md).
**But** : trois types de commits distincts — (1) hors `implementation-tracker`, (2) commit rapide
d'une étape du tracker, (3) commit d'aplatissement du tracker. Chacun est lisible
indépendamment, et lu seulement au besoin. Le texte commun va dans des fichiers séparés et
référencés (dit).

## Critères de réussite

- les trois parties sont indépendantes, chacune lue seulement au besoin (dit)
- le texte commun est dans des fichiers séparés et référencés, sans être recopié (dit)
- `scripts/check_pipeline.py` sort avec le code 0 (dit)
- des tests pytest couvrent le script de clôture sur un dépôt jouet : dry-run, aplatissement, suppression des tags, refus sur conflit (dit)
- `uvx ruff check` et `uvx --with pytest basedpyright` passent sur le nouveau script (dit)

## Hors-périmètre

- les chantiers clos (`done/`) ne sont pas touchés (dit)

## Signaux de dérive

- une modification qui ne touche pas au système de commit (dit)
- du jugement introduit, dans le script en particulier (dit)
- du texte recopié d'un skill à l'autre au lieu d'être référencé (dit)

## Contraintes connues de l'utilisateur

**Périmètre**
- toutes les procédures qui concernent les commits sont migrées dans `git-smart-commit` (dit)
- la procédure de clôture est standardisée par un script, limité aux opérations git et fichiers des points 3 (finaliser le suivi) et 4 (aplatir) de `cloture.md`. L'audit, la dette et la road-map n'en font pas partie. L'agent le lance avec le slug en argument (dit)
- `cloture.md` est conservé et renvoie à la nouvelle procédure (dit)

**Structure**
- un seul skill, dont le `SKILL.md` court oriente vers trois fichiers de procédure, un par type (dit)
- les règles communes vivent dans `git-smart-commit/references/`. La section Branche et commits de `contrat.md` devient un renvoi vers le skill, ce qui solde la dette `git-smart-commit-illisible-seul` (dit)

**Commits d'étape (type 2)**
- le tracker appelle désormais `git-smart-commit` pour les commits d'étape et de session (dit)
- chaque chantier reçoit une lettre à la place du slug : `A` si elle est disponible, sinon `B`, etc. La lettre retenue est notée dans le frontmatter (dit)
- tags git `AE0` (état initial : brief, plan, fiche de suivi), `AE1`, `AE2`… posés sur le commit qui clôt chaque étape, pour pouvoir écrire `git log AE0..AE3`. Seuls les tags permettent ces plages, un nom dans le message ne le permet pas (dit)

**Aplatissement (type 3)**
- le script reçoit le message par un fichier (`--message <fichier>`, transmis par `git commit -F`). Il propose un mode `--dry-run` : l'agent en montre la sortie, attend l'accord, puis relance le script sans ce mode (dit)

**Existant**
- jamais de commit, squash, rebase ou amend sans accord explicite (dépôt: CLAUDE.md)
- les commits d'étape et de session sont aujourd'hui « directs », hors `git-smart-commit` (dépôt: skills/implementation-tracker/references/contrat.md:190)
- la clôture passe la main à `git-smart-commit` pour l'aplatissement (dépôt: skills/implementation-tracker/references/cloture.md:116)
- `contrat.md` se veut le seul lieu de définition des règles partagées (dépôt: skills/implementation-tracker/references/contrat.md:3)

## Incertitudes à lever en plan

- à quel moment sont posés le tag `AE0` et la lettre : à la création du suivi, avant ou après le commit de l'état initial ?
- « le frontmatter » où noter la lettre : celui du fichier de suivi (supposé), et nom du champ
- lettres épuisées (plus de 26 chantiers ouverts à la fois) : hors sujet ou à traiter ?
