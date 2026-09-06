+++
id = "point-3-premisse-harness-sans-repli"
title = "Le point 3 du tracker repose sur une prémisse de harness sans repli écrit"
date = 2026-08-16
source = "Identifié par `revue-plan-deleguee`, R4 du rapport d'audit."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

le point 3 de l'Étape 2 de `skills/implementation-tracker/SKILL.md` (« Faire relire le
plan avant de le présenter ») fait appeler `plan-reviewer` avant `ExitPlanMode`, en s'appuyant
sur le fait que « le harness assigne un fichier de plan dès l'entrée en plan mode et en autorise
l'écriture ». C'est vrai aujourd'hui, vérifié pendant ce
chantier, mais aucun repli n'est écrit si le harness change.

## Pourquoi c'est gênant

sans fichier de plan à lire, l'appel n'a plus d'entrée et le point 3
devient inexécutable, sans que rien n'indique quoi faire à la place.

## Pour solder

écrire le repli en une phrase : relancer `plan-reviewer` après `ExitPlanMode` sur
le fichier de plan persisté, au prix d'un aller-retour si le verdict est défavorable.

## Assumé

la prémisse a été constatée empiriquement, et le brief l'avait justement notée comme
incertitude à lever.
