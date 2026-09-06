+++
id = "absent-masque-outil-absent"
title = "Un projet neuf sans list-dir affiche ABSENT plutôt que OUTIL ABSENT"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ sed -n '71,76p' skills/debt-review/SKILL.md
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  if [ ! -d "$T/$l" ]; then
    echo "ABSENT : $l"
    continue
  fi
  list-dir validate "$T/$l" >/dev/null; rc=$?
```

## Verdict

L'ordre est inchangé : le test de présence du répertoire précède toujours l'appel à `list-dir` et
fait `continue`. Sur un projet neuf **sans** `list-dir` au `PATH`, la boucle imprime trois
`ABSENT` et n'atteint jamais `rc -eq 127`, donc jamais `OUTIL ABSENT`. Rien dans l'Étape 0 ne
sonde l'outil une fois avant la boucle, ce qui était la piste du `Pour solder`.

Le constat tient tel quel, et la forme du correctif reste à trouver — ce n'est ni payé ni sans
objet.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
