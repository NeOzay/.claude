+++
id = "def-vide-retombe-sur-le-squelette"
title = "list-dir init --def \"\" rend le squelette sans dire que la définition a été ignorée"
date = 2026-08-30
source = "chantier semences-de-listes, audit R10"
+++

## Constat

`list-dir init <cible> --def ""` sort **0** et produit le contrat squelette. Vérifié :
`list-dir init .claude/t9 --def ""` rend une liste dont le contrat porte `name = "t9"`, celui du
squelette générique.

La cause tient en une ligne : `commands/init.py` déclare `--def` avec `default=""` et teste
`if nom:`, ce qui rend l'option vide indiscernable de l'option absente.

Le cas voisin, lui, est traité : `--name` ou `--description` combinés à `--def` sortent 2 en
nommant la cause, précisément parce qu'« un contrat qui ne porte pas ce qui a été demandé sous un
code de succès est un échec ouvert ». La même doctrine s'applique ici mot pour mot.

## Pourquoi c'est gênant

L'utilisateur a demandé une définition et reçoit un squelette, sans un mot. La portée réelle est
faible — il faut écrire l'option vide à la main, ce qu'une frappe humaine fait rarement — mais un
appel programmatique construisant sa ligne de commande depuis une variable non renseignée produit
exactement cette forme, et c'est le cas où personne ne relit la commande.

## Pour solder

Distinguer l'option absente de l'option vide : `default=None` sur `--def` et `--from`, puis refuser
une valeur vide en code 2, avec le même message que le refus de `--name` — la doctrine et le code
de sortie existent déjà, il n'y a qu'à les appliquer.

Un test dans `test_entree_cli.py`, jumeau de `test_name_avec_def_est_refuse`.
