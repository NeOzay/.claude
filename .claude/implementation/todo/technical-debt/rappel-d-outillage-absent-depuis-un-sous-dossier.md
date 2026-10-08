+++
id = "rappel-d-outillage-absent-depuis-un-sous-dossier"
title = "Un sous-agent lancé depuis un sous-dossier du dépôt ne reçoit aucune règle d'outillage"
date = 2026-10-06
severite = "avertissement"
chantier = "mods-a-la-racine-des-skills"
reference = "R11"
pin = true
source = "chantier `mods-a-la-racine-des-skills`, audit de clôture du 2026-10-06 sur `349bb96`, `.claude/implementation/mods-a-la-racine-des-skills.audit.md`, R11"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le mod `outillage`, sous `.claude/skills/`, ne se charge que dans une session ouverte à la racine
du dépôt. Ouverte dans `skills/lexique/`, la session charge `lexique` et `mod-commun`, pas
`outillage` (journal `claude -p --debug` de l'audit du 2026-10-06). Le Chantier a retiré
`ruff`, `basedpyright` et l'interdit de `pyright` d'`implementation-auditor` et de
`plan-reviewer` : dans ce cas, ils n'en reçoivent plus rien. Ni `OUTILLAGE.md`, ni
`claude-code-mods`, ni l'en-tête de `rappel.sh` ne disent qu'un sous-dossier n'est pas une
session ouverte sur le dépôt.

## Pourquoi c'est gênant

Le mode de défaillance du 2026-09-09, trois audits menés sous `pyright` au lieu de
`basedpyright`, redevient possible pour qui ouvre une session dans un skill. La session principale
n'y perd rien : elle lit `OUTILLAGE.md` par `.claude/CLAUDE.md`, chargé en remontant.

## Pour solder

Faire arriver le rappel à un sous-agent lancé depuis un sous-dossier, ou écrire la limite là où un
lecteur la cherche (`OUTILLAGE.md`, `claude-code-mods`) ; la transcription d'un sous-agent lancé
par `claude -p` ouvert dans `skills/lexique/` porte « Outillage de ce dépôt ».

## Assumé

Réserve de l'audit de clôture, close telle quelle par choix de l'utilisateur le 2026-10-06.
