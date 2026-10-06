+++
id = "lexique-depend-du-path-de-la-session"
title = "Le mod lexique dépend du PATH de la session"
date = 2026-10-06
source = "chantier `mods-a-la-racine-des-skills`, audit de clôture du 2026-10-06 sur `349bb96`, `.claude/implementation/mods-a-la-racine-des-skills.audit.md`, R6 (premier audit intermédiaire, `ff927cc`), resté ouvert"
+++

## Constat

Le mod `lexique` lance `lexique` par son nom de `bin/`, résolu par le `PATH` de la session ;
il lançait auparavant `python3 <chemin absolu>/lexique-cli.py`. Une session ouverte hors d'un
shell dont le `PATH` porte `bin/` (lanceur graphique, IDE) n'a plus de lexique ; l'échec est dit
sur la ligne d'état par `mod-commun`. `skills/lexique/SKILL.md`, « Charger le mod », ne le dit
pas ; seul `claude-code-mods` le note.

## Pourquoi c'est gênant

Le lexique manque sans que rien d'autre qu'une ligne d'état fugace ne le dise, et la limite ne se
lit pas là où l'on apprend à charger le mod.

## Pour solder

Écrire la dépendance au `PATH` dans « Charger le mod » de `skills/lexique/SKILL.md`, ou faire
résoudre la commande sans le `PATH` de la session sans ancrage sur le `HOME` ;
`grep -n PATH skills/lexique/SKILL.md` rend la ligne.

## Assumé

Prix assumé du solde de `chemins-de-la-configuration-ancres-sur-le-home-dans-le-mod`, décidé au
Journal du Chantier ; laissé ouvert par choix de l'utilisateur.
