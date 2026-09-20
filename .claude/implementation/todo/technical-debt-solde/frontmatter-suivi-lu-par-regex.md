+++
id = "frontmatter-suivi-lu-par-regex"
title = "Le frontmatter des suivis est lu et réécrit par expressions régulières"
date = 2026-09-14
source = "Identifié par `git-smart-commit-trois-commits`, à la demande de l'utilisateur pendant la vérification d'ensemble."
+++

## Constat

Le frontmatter d'un suivi est au format `clé: valeur` entre deux `---`, avec des commentaires `# …`
en fin de ligne (`gabarit-suivi.md`). Ce n'est ni du TOML, que `tomllib` lirait, ni un YAML
qu'on puisse lire avec la bibliothèque standard. Deux lecteurs indépendants l'analysent donc par
expression régulière : `commit_chantier.py` (fonctions `frontmatter` et `remplacer_champ`, en lecture
et en réécriture) et le contrôle 5 de `check_pipeline.py`. Leurs motifs sont alignés à la main : tous
deux retirent le commentaire de fin de ligne, que la réécriture conserve.

## Pourquoi c'est gênant

Le format n'est défini par aucune grammaire, seulement par l'usage. Une valeur contenant ` #`, un
guillemet, une valeur sur plusieurs lignes ou une clé en double sont lus au mieux de façon
divergente d'un lecteur à l'autre, au pire sans erreur. `commit-chantier cloture` réécrit alors
`plan:`, `brief:` ou `audit:` vers une valeur tronquée. Rien n'échoue. Et un motif modifié d'un
seul côté fait diverger les deux lecteurs : le garde-fou reste vert sur un champ que le script a mal
compris, ou vire au rouge sur une archive correcte (constat R17 de l'audit du 2026-09-15, corrigé
en alignant le contrôle 5).

## Pour solder

Adopter un format de frontmatter doté d'une grammaire et d'un lecteur unique, partagé par le script
de clôture et le garde-fou. Par exemple, du TOML entre `+++` lu par `tomllib` et écrit par `tomlkit`,
comme les registres `list-dir`. Il faudra migrer les suivis actifs et le gabarit, et décider du sort
des archives de `done/`. La dette est soldée quand les deux lecteurs n'en font plus qu'un, et qu'un
test rejette une valeur ambiguë au lieu de la tronquer.

## Assumé

Hors périmètre de `git-smart-commit-trois-commits` : changer le format touche le contrat, le gabarit,
le garde-fou et les archives. La lecture par regex reprend celle du contrôle 5, et les tests du
script couvrent le commentaire de fin de ligne.

## Soldé le

**2026-09-19, chantier `pipeline-gabarit`** — le front matter des fiches est du TOML entre `+++` ;
`commit_chantier.py` et le contrôle 5 de `check_pipeline.py` le lisent par un lecteur unique,
`skills/implementation-tracker/scripts/fiche.py` (`tomllib`, YAML en repli pour les seules
archives), et la clôture le réécrit par `gabarit`. Reste, assumé : `gabarit.items` découpe aussi le
bloc `+++` pour réécrire, parce que `fiche.py` doit rester en bibliothèque standard pour le
garde-fou.
Établi par : `.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/test_fiche.py
-k "double or diese"` → 3 passés (clé en double refusée, ` #` lu intact) ; `grep -c "def
frontmatter\|def remplacer_champ\|re.search(rf\"^{champ}"` sur les deux lecteurs → 0 et 0.
