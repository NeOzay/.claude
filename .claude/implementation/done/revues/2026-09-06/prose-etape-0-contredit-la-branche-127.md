+++
id = "prose-etape-0-contredit-la-branche-127"
title = "La prose de l'Étape 0 affirme que le code 127 ne se distingue pas, alors que le bloc le distingue"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n 'ou sur un `list-dir`' skills/debt-review/SKILL.md
93:aussi bien sur un répertoire absent que sur des éléments non conformes ou sur un `list-dir`

$ sed -n '92,95p' skills/debt-review/SKILL.md
**Chaque registre imprime son état, et chaque état a sa puce plus bas.** `list-dir validate` sort 1
aussi bien sur un répertoire absent que sur des éléments non conformes ou sur un `list-dir`
introuvable, et rend 0 sur une liste vide comme sur une liste pleine : aucun de ces états ne se
déduit de son seul code de retour.

$ grep -n 'rc" -eq 127' skills/debt-review/SKILL.md
77:  if [ "$rc" -eq 127 ]; then
```

## Verdict

Le membre fautif — « ou sur un `list-dir` introuvable » — est toujours dans l'énumération, et la
conclusion « aucun de ces états ne se déduit de son seul code de retour » le suit toujours. Quinze
lignes plus haut, le bloc distingue pourtant ce même état par `if [ "$rc" -eq 127 ]`.

La prose contredit donc toujours le code qu'elle introduit, dans le sens qui invite à supprimer la
branche 127. Le geste du `Pour solder` — retirer le membre, mentionner le 127 à part — n'a pas été
fait.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
