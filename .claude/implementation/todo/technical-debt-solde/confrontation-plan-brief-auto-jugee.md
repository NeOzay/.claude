+++
id = "confrontation-plan-brief-auto-jugee"
title = "La confrontation plan ↔ brief reste auto-jugée et sans trace"
date = 2026-08-14
source = "Identifié par `audit-integre`, R7 du rapport d'audit."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/intent-brief/SKILL.md:193` (Étape 7) fait confronter le plan au brief par la
session qui vient de produire ce plan, et sa sortie tient « en trois lignes, pas un rapport »
(`:205`). Aucune trace versionnée n'en subsiste.

## Soldé le

**Soldé le 2026-08-16 par le chantier `revue-plan-deleguee`** — l'option « regard extérieur » a été
retenue : l'Étape 7 d'`intent-brief` est supprimée, et la confrontation est rendue par le sous-agent
`plan-reviewer` (contexte isolé, lecture seule), appelé par le tracker **avant** que le plan ne soit
présenté à l'utilisateur. L'option « rapport versionné » a été écartée : un plan pas encore accepté
peut changer plusieurs fois, un historique de verdicts sur des versions mortes n'aiderait personne.
Établi par : `grep -c 'Confrontation plan' skills/intent-brief/SKILL.md` → `0` et ses étapes
s'arrêtent à `## Étape 6 — Passage au suivi` ; `grep -n 'plan-reviewer'
skills/implementation-tracker/SKILL.md` → `126:` l'appel avant `ExitPlanMode` ; `agents/plan-reviewer.md`
existe, `tools: Read, Grep, Glob, Bash` sans droit d'écriture.

## Pourquoi c'est gênant

c'est le tiers restant du symptôme d'origine : un point de contrôle
rendu par l'auteur du travail, sans trace. Le dispositif d'audit démontre qu'un juge indépendant y
change le résultat.

## Pour solder

<OPTIONNEL>

## Assumé

le brief du chantier `audit-integre` nommait trois points de contrôle auto-jugés ; deux
ont été traités (la clôture, et le bloc `VÉRIFICATION` de `step-implementer` désormais rejoué). Le
« But » du brief bornait explicitement le chantier à la clôture — celui-ci n'était couvert par aucun
critère de réussite.
