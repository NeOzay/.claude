+++
id = "reprise-de-cloture-sans-test-aux-rangs-intermediaires"
title = "Deux chemins de reprise de `commit-chantier cloture` ne sont couverts par aucun test"
date = 2026-09-14
source = "chantier `git-smart-commit-trois-commits`, R15 du rapport d'audit (reliquat de R5)"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Les tests de `commit_chantier.py` couvrent un échec pendant la finalisation sur `<slug>` et un échec
sur `base:` au commit final (`test_un_echec_sur_la_branche_se_relance_tel_quel`,
`test_un_echec_sur_la_base_dit_ce_qui_reste_a_faire`). Deux chemins restent sans test :

- l'échec de `git checkout <base>`, second geste, lui aussi annoncé « relancée telle quelle » ;
- l'échec au milieu du geste d'archivage, après des `git mv` partiels, où la sortie prévient
  « le premier a pu être entamé ».

## Pourquoi c'est gênant

C'est sur ces deux rangs que le conseil « relancer » ou « finir à la main » engage l'utilisateur
sur un dépôt à moitié modifié. Un conseil faux y laisse une base avec un aplatissement partiel.

## Pour solder

Ajouter deux tests en sous-processus sur le dépôt jouet : un checkout refusé (fichier non suivi en
conflit sur `base:`), et un `git mv` qui échoue après un premier déplacement réussi. Vérifier le
conseil affiché et l'état laissé.
