+++
id = "prefill-marqueur-produit-accepte-en-silence"
title = "Deux échecs silencieux du préremplissage : un marqueur produit, et une section vide"
date = 2026-08-31
source = "chantier 2026-08-31-champs-preremplis, audit de clôture R4"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Deux cas, tous deux reproduits :

- `command = "echo '<À REMPLIR>'"` sur un champ `date` est **accepté** et écrit
  `champ = "<À REMPLIR>"` : `check_value` suspend le contrôle de type sur `is_marker`. Le champ
  ressort réclamé par `validate --filled`, alors que le contrat l'annonçait prérempli.
- `command = "true"` (sortie vide) sur une **section** pose une section vide, ni marquée ni
  signalée : `initial_section` ne confronte rien, une section n'ayant pas de type déclaré.

## Pourquoi c'est gênant

`listdir/prefill.py` proclame en en-tête « ÉCHEC FERMÉ […] Rien n'est avalé ». Ces deux chemins
avalent. Le premier produit un élément qui se dit à remplir sur un champ que le contrat prétend
remplir tout seul — l'utilisateur cherchera l'erreur dans son élément, pas dans son contrat.

## Pour solder

Refuser une valeur produite qui vaut l'un des deux marqueurs (`is_marker` sur la sortie, avant
`check_value`), et refuser une sortie vide pour une section comme pour un champ. Les deux refus
appartiennent à `prefill`, pas à `check_value` : ils ne portent que sur une valeur **produite**,
jamais sur une valeur écrite à la main.

## Assumé

<OPTIONNEL>
