+++
id = "verification-derive-inoperante-sur-liste-amorcee"
title = "La vérification de l'étape 7 du plan semences-de-listes imprime ÉCHEC derive"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ sed -n '181,187p' .claude/implementation/done/2026-08-30-semences-de-listes.plan.md
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  list-dir init "$D/$l" --def "$l" || echo "ÉCHEC init : $l"
  list-dir validate "$D/$l"        || echo "ÉCHEC validate : $l"
done
list-dir derive "$D/technical-debt" "$D/revue" --template review || echo "ÉCHEC derive"
diff <(cat .claude/implementation/todo/technical-debt/.list/contract.toml) \
     <(cat skills/implementation-tracker/list-dir/technical-debt/contract.toml) \
  || echo "ÉCHEC : la semence diverge de l'existant"
```

## Verdict

Le plan archivé porte toujours la boucle telle quelle : les trois registres sont amorcés — donc
vides — et `derive` est lancé immédiatement après, sans qu'aucune entrée soit créée. Rejouée, elle
imprimerait `ÉCHEC derive` sur un critère pourtant atteint. Ni la correction de la boucle, ni la
note disant qu'un code non nul est attendu, n'ont été écrites.

L'`Assumé` de l'entrée reste vrai (le chantier a été clos avec cette réserve), ce qui explique le
report mais ne solde rien.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
