+++
id = "migrateur-se-dit-sans-outil-d-ecriture"
title = "`migrateur-de-liste` affirme n'avoir aucun outil d'édition, alors qu'il a `Bash`"
date = 2026-10-08
severite = "note"
chantier = "registre-de-dette-severite-chantier-pin"
reference = "R14"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

La consigne de `agents/migrateur-de-liste.md` dit « N'édite aucun fichier. Tu n'as pas d'outil pour
le faire » ; son en-tête lui donne `Bash`, qui peut écrire n'importe quel fichier. Ses trois
lancements du 2026-10-08 n'ont écrit que par `list-dir fill`.

## Pourquoi c'est gênant

La règle repose sur une prémisse fausse : un modèle qui constate qu'il peut écrire n'a plus de motif
écrit pour s'en abstenir. Rien ne s'est produit, aucun coût n'est démontré.

## Pour solder

La consigne dit que `Bash` peut écrire et que seul `list-dir fill` est admis, ou l'agent n'a plus
d'outil d'écriture.

## Assumé

<OPTIONNEL>
