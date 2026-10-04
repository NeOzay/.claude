+++
id = "repli-contexte-jamais-purge"
title = "Le repli `~/.cache/claude-contexte/` de la commande `contexte` n'est jamais purgé"
date = "2026-10-04"
source = "chantier `contexte-tracker`, audits de clôture, constat R7"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Sans `XDG_RUNTIME_DIR`, `contexte ecrire` range ses mesures dans `~/.cache/claude-contexte/`,
un fichier par session. Rien ne les supprime. Sous `XDG_RUNTIME_DIR`, un tmpfs vidé à la
déconnexion, la question ne se pose pas.

## Pourquoi c'est gênant

Le répertoire grossit d'un fichier par session sans borne. Le coût est de quelques octets par
session, mais rien ne le signale jamais.

## Pour solder

Purger à l'écriture les mesures plus vieilles qu'un délai fixé dans `contexte.py`, ou les
supprimer à la fin de session par un hook.

## Assumé

Reporté à la Clôture de `contexte-tracker` : la machine de l'utilisateur fournit
`XDG_RUNTIME_DIR`, et le repli n'y sert pas.
