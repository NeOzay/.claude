+++
id = "cumul-de-dette-sans-controle-de-provenance"
title = "`audit check` accepte une dette inventée ou retouchée dans la Dette corrigée ou écartée"
date = 2026-10-11
severite = "avertissement"
chantier = "refonte-de-l-audit"
reference = "R3"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`verifier_suite`, dans `skills/implementation-tracker/scripts/rapport_audit/modele.py`, ne contrôle
que les identifiants d'une dette qui entre dans un cumul. Il ne vérifie pas qu'elle venait de la
Dette précédente, ni que ses champs sont restés ceux de la précédente. Pour la Dette écartée, rien
ne vérifie non plus que la ligne figure en `## Dettes écartées` du Suivi. Établi à l'audit
`02-ef2b907` sur une copie des fixtures `contexte-tracker.audit/` : un `[[dette.corrigee]]` R50
inventé, ajouté au `02`, passe `audit check --filled` (« verdicts admis : RÉSERVES », sortie 0).

## Pourquoi c'est gênant

Une dette recopiée ou retouchée à la main par `Edit` au moment de la ranger, ce que le Signal de
dérive S1 du Chantier proscrit, passe le contrôle sans rien signaler. Seules les instructions de
l'agent l'interdisent : un auditeur qui s'en écarte ferait disparaître une dette du cumul, ou en
réécrirait le constat, sans qu'aucune commande ne le voie.

## Pour solder

Dans `verifier_suite`, exiger qu'une dette neuve de `courant.dette.corrigee` ou
`courant.dette.ecartee`, absente des cumuls du précédent, soit une dette de
`precedent.dette.actuelle` aux mêmes champs communs, et que son `corrigee` vaille l'audit courant.
Ajouter à `test_modele.py` une faute par cas : dette inventée en corrigée, dette retouchée en
rangeant.

## Assumé

<OPTIONNEL>
