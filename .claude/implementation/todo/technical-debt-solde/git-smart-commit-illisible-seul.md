+++
id = "git-smart-commit-illisible-seul"
title = "`git-smart-commit` n'est plus lisible sans `implementation-tracker`"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R10 du rapport d'audit."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`squash.md` renvoie désormais à
`../../implementation-tracker/references/contrat.md`. Un déplacement ou un renommage du tracker
casse cette référence.

## Soldé le

**2026-09-15, chantier `git-smart-commit-trois-commits`** — soldé en partie seulement (R7 du rapport
d'audit). `SKILL.md`, le type 1, le type 2 et les fichiers communs ne renvoient plus au contrat du
tracker, et `squash.md` est supprimé. Il reste une dépendance, limitée au type 3, qui ne se lit que
depuis le tracker : `aplatissement.md` renvoie deux fois à `contrat.md` (§ Arborescence et nommage,
§ Frontmatter). Si le tracker est déplacé, le contrôle 8 du garde-fou détectera ces renvois cassés.
Établi par : `grep -rn "implementation-tracker" skills/git-smart-commit` → 4 lignes. `etape.md` et
`aplatissement.md` ne citent le tracker que dans leur ligne d'introduction, et les 2 autres lignes
sont ces deux renvois d'`aplatissement.md`.

## Pourquoi c'est gênant

`git-smart-commit` est la seule skill du pipeline qui serve largement
hors de lui ; elle porte maintenant une dépendance vers une skill de chantier.

## Pour solder

rien tant que le tracker ne bouge pas. Si le noyau devait migrer vers un
emplacement neutre, c'est ce renvoi qui le motiverait.

## Assumé

conséquence directe de la décision d'emplacement du noyau, prise au cadrage. Le
contrôle 1 du garde-fou rend la casse visible (chemin mort), ce qui est le bon niveau de garantie.
