+++
id = "sante-skills-plante-sur-une-dependance-objet"
title = "Une dépendance de mod écrite en objet fait planter sante_skills.py"
date = 2026-10-06
source = "chantier `mods-a-la-racine-des-skills`, audit de clôture du 2026-10-06 sur `349bb96`, `.claude/implementation/mods-a-la-racine-des-skills.audit.md`, R10"
+++

## Constat

`scripts/sante_skills.py`, `mods_en_defaut`, cherche chaque élément de `dependencies` d'un
`plugin.json` dans l'ensemble des noms de mods. Un élément non hachable, comme
`{"name": "mod-commun"}` ou une liste, lève `TypeError: unhashable type: 'dict'`, et `main()`
n'attrape rien. Établi le 2026-10-06 par une sonde de l'audit sur un mod jouet. Aucun mod du dépôt
n'écrit cette forme, et rien n'établit que Claude Code l'accepte.

## Pourquoi c'est gênant

Le hook `SessionStart` sort sur une trace Python, dont l'hôte n'affiche que la première ligne,
« Traceback (most recent call last): ». Toutes les autres anomalies de la session sont perdues :
`bin/`, venv, `PATH`. C'est le chemin d'échec que le script existe pour fermer.

## Pour solder

Signaler sans lever un élément de `dependencies` qui n'est pas une chaîne, avec un test dans
`scripts/tests/test_sante_skills.py` ; `python3 scripts/sante_skills.py` sur un mod jouet qui
porte `{"name": "x"}` sort en 1 et nomme l'anomalie.

## Assumé

Réserve de l'audit de clôture, close telle quelle par choix de l'utilisateur le 2026-10-06.
