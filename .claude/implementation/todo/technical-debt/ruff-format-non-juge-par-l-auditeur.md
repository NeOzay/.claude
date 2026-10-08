+++
id = "ruff-format-non-juge-par-l-auditeur"
title = "Rien ne fait compter à l'auditeur un fichier Python hors format comme un écart"
date = 2026-10-06
severite = "inconnue"
chantier = "mods-a-la-racine-des-skills"
reference = "R12"
pin = false
source = "chantier `mods-a-la-racine-des-skills`, audit de clôture du 2026-10-06 sur `349bb96`, `.claude/implementation/mods-a-la-racine-des-skills.audit.md`, R12"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

La dette `ruff-format-absent-des-agents` voulait que l'auditeur lance `ruff format --check` et
compte un fichier hors format comme un écart, et que `plan-reviewer` l'exige d'une vérification
d'Étape sur du Python. Le Chantier l'a soldée à l'inverse : le rappel du mod `outillage` dit
`uvx ruff format <chemins>` « avant de commiter du Python ». C'est une consigne d'auteur : ni
l'un ni l'autre agent n'est tenu de juger le format.

## Pourquoi c'est gênant

Un Chantier peut livrer du Python hors format sans qu'aucun audit ne le relève, sauf si l'auditeur
le lance de lui-même.

## Pour solder

Faire juger le format par l'auditeur et `plan-reviewer`, sans recopier la commande dans leur
fichier (le rappel d'outillage la porte déjà) : un audit sur une branche qui porte un `.py` hors
format le cite parmi ses constats.

## Assumé

Réserve de l'audit de clôture, close telle quelle par choix de l'utilisateur le 2026-10-06.
