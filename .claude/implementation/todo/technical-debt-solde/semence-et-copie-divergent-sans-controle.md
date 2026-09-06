+++
id = "semence-et-copie-divergent-sans-controle"
title = "Rien ne confronte une liste amorcée à la définition qui l'a semée"
date = 2026-08-30
source = "chantier renvoi-contrat-des-categories, audit R6 ; revu par sections-en-forme-longue, audit R7"
reviewed = 2026-09-06
category = "a-solder"
+++

## Constat

`skills/implementation-tracker/list-dir/technical-debt/` et
`.claude/implementation/todo/technical-debt/.list/` portent aujourd'hui le même `contract.toml` et
les mêmes gabarits, au caractère près. Rien ne l'établit : `diff` est une vérification d'étape,
jouée à la main par qui y pense.

**2026-08-31, chantier `sections-en-forme-longue`** — le coût annoncé a été payé une fois de plus :
le passage des `[sections]` en forme longue a imposé de réécrire **huit** `contract.toml` à la main
là où quatre auraient suffi, les quatre paires étant maintenues identiques par un `diff` joué à la
main en fin d'étape. Les paires sont à nouveau identiques (vérifié à `752449e`) ; rien ne le
garantira à la prochaine évolution du format. Le constat ci-dessous est inchangé — c'est sa
fréquence qui se précise : toute évolution du format de contrat double son propre coût.

Le chantier `renvoi-contrat-des-categories` a rendu l'écart plus coûteux sans le créer. Il a ajouté
aux deux `templates/review.toml` un commentaire de cinq lignes qui **justifie l'ordre non
alphabétique** des `values` — la doctrine que `debt-review/SKILL.md` ne porte plus depuis que sa
boucle des piles la lit par `list-dir contract … --values category`. Cette justification n'existe
donc plus qu'à ces deux endroits, et ils peuvent diverger.

## Soldé le

**2026-09-06, revue de dette** — le **constat** que le *Pour solder* réclamait existe désormais, et
sous la forme exacte qu'il envisageait. `.list/semence/` conserve la définition telle qu'elle a
semé ; `validate` la confronte à la définition courante par son `[origin] version` et **avertit
sans échouer** ; `reseed` rattrape. La question de fond — ce qu'une divergence signifie — est
tranchée dans le sens suggéré : une copie en avance est une redéfinition assumée (le local gagne à
la fusion), une semence en avance est un oubli de propagation.

Établi par : une liste amorcée depuis une définition jouet, dont la définition avance seule.

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

$ ls .claude/implementation/todo/technical-debt/.list/
backup/  semence/  templates/  contract.toml
```

**Ce que le solde ne couvre pas** : la comparaison repose sur le numéro de version de la
définition. Une définition modifiée **sans** que sa version soit incrémentée reste invisible — c'est
une entrée distincte du registre, `version-de-definition-non-incrementee-apres-changement-de-contrat`
(2026-09-06).

## Pourquoi c'est gênant

La divergence est le comportement **voulu** — `definitions.md`, « La définition n'est autorité
que le temps de l'`init` » : une liste qu'un projet a délibérément redéfinie ne doit pas se faire
rattraper par sa semence. Ce qui manque n'est pas un re-semis, c'est un **constat** : aujourd'hui,
une définition modifiée sans sa copie (ou l'inverse) ne fait échouer aucune commande, et personne
ne sait laquelle des deux est en avance.

Le cas concret est déjà là : une catégorie ajoutée à la définition mais pas à la copie amorcée
donnerait deux registres aux verdicts différents, dont un seul serait celui que `derive` projette.
Et le commentaire de doctrine, s'il ne subsiste que d'un côté, laisse l'autre éditeur ranger sa
valeur à la fin par commodité — ce que le commentaire existe précisément pour empêcher.

## Pour solder

Rendre la comparaison exécutable et la faire jouer. La commande est triviale ; c'est son
déclenchement qui est la vraie question :

```bash
diff -r skills/implementation-tracker/list-dir/technical-debt \
        .claude/implementation/todo/technical-debt/.list
```

Trancher d'abord **ce qu'une divergence signifie**, faute de quoi le contrôle criera sur un état
légitime : une copie en avance est une redéfinition assumée, une semence en avance est un oubli de
propagation. Les deux se distinguent par l'intention, pas par le diff — un contrôle qui ne sait pas
les séparer sera désarmé au premier cri.

Piste : ne comparer que les listes que ce dépôt-ci amorce depuis ses propres définitions, et
signaler sans échouer. Le contrôle de santé du pipeline (`scripts/check_pipeline.py`) est le seul
endroit qui tourne à chaque session sans qu'on y pense.

## Assumé

Le chantier n'avait pas le choix : le commentaire devait vivre dans le contrat, là où le lira qui
édite les `values`. L'écrire deux fois est la conséquence directe du modèle « une liste amorcée est
détachée de sa semence », qui est documenté et voulu. C'est l'absence de constat qui est la dette,
pas la duplication.
