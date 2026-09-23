+++
id = "contrat-employe-en-deux-sens"
title = "« Contrat » est réservé au sens gabarit/list-dir, mais implementation-tracker l'emploie dans un autre sens"
date = 2026-09-23
source = "Identifié par `lexique`, R3 du rapport d'audit de clôture."
+++

## Constat

Le lexique global réserve **Contrat** : « Déclaration des champs et des sections qu'un Gabarit ou
un Élément doit porter ». `implementation-tracker` nomme aussi « contrat » le document de règles
partagées du pipeline (`references/contrat.md`, « Contrat du pipeline ») et l'interface d'appel des
sous-agents (« Contrat des sous-agents »), deux sens distincts du terme réservé.

Établi par : `grep -rn "Contrat des sous-agents" skills/implementation-tracker/SKILL.md` → trois
renvois ; `lexique liste | grep Contrat` → le terme est réservé au global.

## Pourquoi c'est gênant

Le lexique interdit d'employer un terme hors de sa définition. Tant que la prose du tracker dit
« Contrat du pipeline », l'agent lit ce mot avec sa majuscule dans un sens que le lexique ne lui
donne pas, et la règle se contredit dans le dépôt même qui la pose. Le prochain terme qui
dérivera ainsi ne se distinguera pas de celui-ci.

## Pour solder

Choisir un autre mot pour les deux sens du tracker (par exemple « règles du pipeline », « interface
des sous-agents »), avec l'accord de l'utilisateur, et l'appliquer à `implementation-tracker`,
`intent-brief`, `git-smart-commit` et `check_pipeline.py` (constante `CONTRAT`, ancres citées) —
puis relancer `check_pipeline.py`, dont les renvois ancrés vers `contrat.md` casseront.
