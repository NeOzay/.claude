+++
id = "chemin-skill-code-en-dur"
title = "Le chemin de la skill est codé en dur et répété en trois points d'édition"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R15 et R19 du rapport d'audit."
reviewed = 2026-08-17
category = "aggravee"
+++

## Constat

**cinq** points d'édition, et non plus trois : deux dans
`implementation-tracker/SKILL.md`, un dans `contrat.md`, deux dans `debt-review/SKILL.md` — tous
écrivant en dur `$HOME/.claude/skills/…`. Une installation hors `~/.claude`, ou un renommage de la
skill, retombe dans le mode de défaillance de `R2` : code 127, `stdout` vide, que l'Étape 1 du
tracker lit comme « aucune implémentation en cours ».
Établi par : `git grep -c '\$HOME/\.claude/skills' master -- skills` → 3, `… HEAD -- skills` → 5.

**À noter** — le contrôle 6 du garde-fou **impose** la forme `$HOME/…` pour tout appel de script
depuis un `.md` de `skills/`. Cette extension était structurellement forcée : elle ne se solde pas
sans traiter le problème générique.

**Amendée le 2026-08-24 par `check-pipeline-python`** — le **symptôme** est soldé, la **cause**
reste. Le contrôle 7 du garde-fou vérifie désormais que chaque chemin `$HOME/.claude/…` cité dans
un `.md` de `skills/` désigne un fichier ou un répertoire existant : un point d'édition oublié
devient rouge au lieu de dormir. C'est ce qui a validé la bascule des trois appels d'`impl-list.sh`
vers `impl_list.py` dans ce chantier même.
Établi par : `python3 scripts/check_pipeline.py` → contrôle 7 « 12 chemins de skill cités, tous
existent » ; `test_chemin_inexistant` le fait crier.

Ce que le contrôle 7 **ne fait pas** : empêcher le compte de croître. Les points d'édition sont
passés de 3 à 8 depuis l'ouverture de cette entrée, et chaque skill neuve en ajoute, puisque le
contrôle 6 impose cette écriture. Seule une résolution du chemin de skill à la source y mettrait
fin — écarté du périmètre de `check-pipeline-python`, qui n'aurait pas pu la mener sans changer la
convention d'appel de toutes les skills.

## Pourquoi c'est gênant

c'est exactement le défaut qui a bloqué la clôture de ce chantier, sous
une forme plus étroite. Aucune des cinq éditions n'échoue bruyamment si elle est oubliée.

## Pour solder

soit un contrôle du garde-fou vérifiant que chacun de ces chemins désigne un
fichier existant, soit une résolution du chemin de la skill au lieu d'une constante. La seconde est
la seule qui empêche le compte de croître : le contrôle 6 impose la forme, donc chaque skill neuve
ajoute ses points d'édition.

## Soldé le

**2026-08-29, chantier `resolution-chemin-skill`** — la cause est traitée, pas seulement le
symptôme. Les exécutables de skill sont exposés dans `bin/` par des liens **relatifs** versionnés
(`bin/list-dir`, `bin/impl-list`) et s'appellent par leur nom via le `PATH` ; plus aucun `.md` ne
porte de chemin de skill ancré sur le `HOME`. Le contrôle 7 du garde-fou refuse désormais cette
forme, ce qui empêche le compte de repartir à la hausse — c'est la condition que cette entrée
posait pour son solde.

Établi par :
- `git grep -q '$HOME/.claude/skills' -- skills .claude/implementation/todo/README.md` → **code 1**,
  aucune occurrence (le compte passe de 8 points d'édition à 0).
- Injection d'un appel `"$HOME/.claude/skills/list-dir/scripts/list-dir.py" list .` dans
  `skills/list-dir/SKILL.md`, puis `python3 scripts/check_pipeline.py` → **1 anomalie** :
  « chemin ancré sur le HOME : skills/list-dir/scripts/list-dir.py — écrire le chemin relatif à la
  racine du dépôt, ou appeler la commande de bin/ ». Arbre restauré, pipeline conforme.
- `python3 scripts/sante_skills.py` → **code 0** : chaque lien de `bin/` est relatif, résout, est
  exécutable, et gagne dans le `PATH`.

Ce que le solde ne couvre pas : un `.md` reste libre de **citer** un chemin relatif à la racine du
dépôt (`skills/list-dir/scripts/`), forme vérifiée par le contrôle 7 mais non résolue par `bin/`.
Le cas d'une bibliothèque importée est traité à part, par `shutil.which`.

## Assumé

arbitré à la clôture — le cas suppose un environnement où `HOME` est cassé ou une
installation non standard.
