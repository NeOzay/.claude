+++
id = "prefill-marqueur-produit-accepte-en-silence"
title = "Deux échecs silencieux du préremplissage : un marqueur produit, et une section vide"
date = 2026-08-31
source = "chantier 2026-08-31-champs-preremplis, audit de clôture R4"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

Deux cas, tous deux reproduits, et rejoués le 2026-09-06 dans un même élément :

- `command = "echo '<À REMPLIR>'"` sur un champ `date` est **accepté** et écrit
  `champ = "<À REMPLIR>"` : `check_value` suspend le contrôle de type sur `is_marker`. Le contrat
  annonçait le champ prérempli ; l'élément porte un marqueur.
- `command = "true"` (sortie vide) sur une **section** pose une section vide, ni marquée ni
  signalée : `initial_section` ne confronte rien, une section n'ayant pas de type déclaré.

`list-dir new` sort **0** dans les deux cas.

**Précisé le 2026-09-06** — le constat d'origine ajoutait que le champ « ressort réclamé par
`validate --filled` ». Ce n'est vrai que d'un champ **requis** : posé en `required = false`,
l'élément passe `validate --filled` avec le marqueur en place, sans qu'aucune commande ne le
réclame jamais. Le défaut est donc plus large que décrit, pas plus étroit — mesuré sur un contrat
jouet portant les deux déclarations ci-dessus.

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
