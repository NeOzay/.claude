+++
id = "prose-etape-0-contredit-la-branche-127"
title = "La prose de l'Étape 0 affirme que le code 127 ne se distingue pas, alors que le bloc le distingue"
date = 2026-08-30
source = "chantier semences-de-listes, audit R22"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`skills/debt-review/SKILL.md`, Étape 0, phrase d'introduction du bloc :

> `list-dir validate` sort 1 aussi bien sur un répertoire absent que sur des éléments non conformes
> **ou sur un `list-dir` introuvable** […] aucun de ces états ne se déduit de son seul code de
> retour.

Mesuré : outil introuvable → **127**, répertoire absent → **1**. Le membre ajouté est faux, et la
conclusion l'est avec lui — le 127 se déduit précisément du code de retour, ce que fait le bloc
trois lignes plus bas par `if [ "$rc" -eq 127 ]`, et ce que redit le mode de défaillance en fin de
section.

L'erreur a été introduite en élargissant une énumération dont le point était l'indistinction, sans
vérifier que le nouveau membre y appartenait. C'est le seul état qui, justement, se distingue.

## Pourquoi c'est gênant

La prose contredit le code qu'elle introduit, et dans le sens qui invite à le simplifier : un
lecteur qui la suit peut supprimer la branche `-eq 127` comme inutile, et rouvrir le défaut qu'elle
existe pour corriger — un registre sain affiché `NON CONFORME` quand `list-dir` manque au `PATH`.

Ce fichier a produit un constat à chacun des sept correctifs successifs du chantier, celui-ci
compris. Le motif est constant : chaque correction relit la ligne qu'elle vise, pas ce qui
l'entoure.

## Pour solder

Retirer « ou sur un `list-dir` introuvable » de l'énumération, ce qui rend la conclusion vraie, et
mentionner le 127 à part — comme le seul état que le code de retour suffit à nommer.

Puis relire la phrase **contre le bloc qu'elle introduit**, ligne à ligne : c'est le contrôle qui
manquait, et le mode de défaillance en fin de section le prescrit déjà.
