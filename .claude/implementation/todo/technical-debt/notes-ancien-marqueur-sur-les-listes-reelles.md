+++
id = "notes-ancien-marqueur-sur-les-listes-reelles"
title = "`validate` note l'ancien Marqueur sur chaque entrée des trois listes de dette"
date = 2026-10-07
source = "chantier socle-contrat-evolutif, audit de clôture (d5be681), R2"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Depuis le chantier `socle-contrat-evolutif`, `list-dir validate` avertit sur stderr de tout
Marqueur générique laissé sur un champ `int`, `date`, `bool` ou `list`. Les trois listes de dette
sont dans ce cas : leurs entrées portent `reviewed = "<OPTIONNEL>"`, que le contrat déclare en
`date`. Le code de retour reste 0.

Établi par, le 2026-10-07 :

```
$ for l in technical-debt technical-debt-solde technical-debt-ecarte; do
>   list-dir validate .claude/implementation/todo/$l 2>&1 >/dev/null | grep -c 'ancien marqueur'
> done
39
22
2
```

## Pourquoi c'est gênant

Soixante-trois lignes sur stderr à chaque `validate` d'une liste de dette. Elles couvrent les
avertissements de provenance qui les précèdent et toute note utile : l'écart que `validate` doit
faire voir se noie dans un bruit connu.

## Pour solder

Lancer `list-dir migrate` sur les trois listes. La conversion est mécanique : `<OPTIONNEL>`
devient `<OPTIONNEL date>`, aucune valeur écrite n'est touchée. Les Registres sont du ressort du
Chantier du registre de dette, qui reprend aussi leur contrat ; c'est lui qui migre, en commits
séparés des changements de contenu.

Solde établi par la commande du Constat, qui rend `0` pour chacune des trois listes.

## Assumé

Le bruit est voulu par le critère du chantier (« non migré, ce Marqueur est accepté par `validate`,
qui avertit sur stderr sans changer son code de retour »), et la migration des listes du pipeline
est hors de son périmètre.
