+++
id = "def-vide-retombe-sur-le-squelette"
title = "list-dir init --def \"\" rend le squelette sans dire que la définition a été ignorée"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ list-dir init t9 --def ""
t9/.list/contract.toml
$ echo "code $?"
code 0
$ head -1 t9/.list/contract.toml
name = "t9"
```
Le contrat rendu est bien celui du squelette générique (`name` pris du nom de la cible), alors
qu'une définition avait été demandée.

## Verdict

Rejoué le 2026-09-06 : le comportement est identique au constat. `--def ""` sort **0** et rend le
squelette, sans un mot. La distinction entre l'option absente et l'option vide (`default=None`
puis refus en code 2) n'a pas été faite, et aucun test jumeau de `test_name_avec_def_est_refuse`
ne couvre le cas.

C'est bien une dette et non une préférence : le paquet se réclame de l'« échec fermé », et un
contrat qui ne porte pas ce qui a été demandé sous un code de succès en est la violation exacte.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
