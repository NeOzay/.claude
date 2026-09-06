+++
id = "point-3-premisse-harness-sans-repli"
title = "Le point 3 du tracker repose sur une prémisse de harness sans repli écrit"
date = 2026-08-16
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ sed -n '124,132p' skills/implementation-tracker/SKILL.md
3. **Faire relire le plan avant de le présenter.** Le harness assigne un fichier de plan dès
   l'entrée en plan mode et en autorise l'écriture : y écrire le plan, puis lancer le sous-agent
   `plan-reviewer` **avant `ExitPlanMode`**.
   [...]
   **Pas de brief** → le lui dire explicitement : il ne jugera alors que la qualité du plan.

$ grep -n "repli\|si le harness\|à défaut" skills/implementation-tracker/SKILL.md
(aucun résultat)
```

## Verdict

La prémisse est toujours écrite telle quelle, et le seul repli prévu au point 3 porte sur
l'absence de **brief**, pas sur l'absence de **fichier de plan**. La phrase que le `Pour solder`
demande d'ajouter — relancer `plan-reviewer` après `ExitPlanMode` — n'est nulle part. Le
constat tient, sans extension mesurable.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
