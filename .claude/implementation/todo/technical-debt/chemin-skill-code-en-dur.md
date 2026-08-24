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

## Assumé

arbitré à la clôture — le cas suppose un environnement où `HOME` est cassé ou une
installation non standard.
