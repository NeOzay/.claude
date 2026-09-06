+++
id = "semence-et-copie-divergent-sans-controle"
title = "Rien ne confronte une liste amorcée à la définition qui l'a semée"
date = 2026-08-30
reviewed = 2026-09-06
category = "a-solder"
+++

## Vérifié par

Le mécanisme réclamé existe désormais. Éprouvé le 2026-09-06 sur un projet jouet, en faisant
avancer la définition sans toucher la copie :

```
$ list-dir init maliste --def jouet
maliste/.list/contract.toml
$ grep -A3 '\[origin\]' maliste/.list/contract.toml
[origin]
def = "jouet"
version = 3
$ # …la définition passe en v4, la liste amorcée n'est pas touchée…
$ list-dir validate maliste; echo "code $?"
maliste : contrat périmé — semé en v3, « jouet » est en v4 ; « list-dir reseed maliste » rattrape
maliste : 0 élément(s) conformes au contrat
code 0
```

Et sur le registre réel, la semence intacte est bien conservée à côté de la copie :

```
$ ls .claude/implementation/todo/technical-debt/.list/
backup/  semence/  templates/  contract.toml
```

## Verdict

Le `Pour solder` demandait exactement trois choses, et les trois sont livrées.

**« Rendre la comparaison exécutable »** — `.list/semence/` garde la définition telle qu'elle a
semé, et `validate` la confronte à la définition courante par son `[origin] version`.

**« Trancher ce qu'une divergence signifie »** — c'est fait, et dans le sens que l'entrée
suggérait : une copie en avance est une redéfinition assumée (le local gagne à la fusion), une
semence en avance est un oubli de propagation que `reseed` rattrape. `provenance.py` porte la
doctrine en toutes lettres : « Une liste dont la semence a bougé n'est pas en faute ».

**« Signaler sans échouer »** — l'avertissement sort sur une commande qui rend **0** : c'est la
piste écrite au `Pour solder`, pas une variante.

Ce n'est pas `non-pertinent` : rien n'a disparu, le manque a été comblé. Le résiduel connu — une
définition modifiée sans que sa version soit incrémentée n'est pas vue — fait l'objet d'une entrée
distincte au registre (`version-de-definition-non-incrementee-apres-changement-de-contrat`,
2026-09-06) et ne remet pas ce solde en cause.

## Action

Sortie du registre : `list-dir move .claude/implementation/todo/technical-debt
semence-et-copie-divergent-sans-controle .claude/implementation/todo/technical-debt-solde`, puis
section `## Soldé le` datée du 2026-09-06 citant le mécanisme `semence/` + `reseed` et la
commande ci-dessus avec sa sortie.

## Arbitrage

**Différée.** Même raison que `sortie-du-registre-jamais-exercee` : le verdict `a-solder` tient, le
`move` et la section `## Soldé le` attendent un accord explicite.
