+++
id = "sections-de-categories-jamais-confrontees-au-contrat"
title = "les sections de categories.md recopient l'ensemble des valeurs du contrat"
date = 2026-08-30
source = "chantier renvoi-contrat-des-categories, hors-périmètre assumé"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/debt-review/references/categories.md` consacre une section `## ` à chaque valeur du champ
`category`, déclarée par `skills/implementation-tracker/list-dir/technical-debt/templates/review.toml`.
Chaque section porte le **sens** d'une catégorie — ce qui y entre, la preuve exigée, la destination
— et ce sens ne vit nulle part ailleurs. Mais l'**ensemble** qu'elles forment, lui, est une copie
de la liste `values`.

Le chantier `renvoi-contrat-des-categories` a supprimé les recopies voisines : `gabarit-rapport.md`
renvoie désormais à `list-dir contract --def technical-debt --template review --values category`,
et la boucle des piles de `SKILL.md` tire sa liste de la même commande. Ce cas-ci a été écarté par
arbitrage : la prose porte du jugement, qu'un renvoi ne remplace pas.

## Pourquoi c'est gênant

L'arbitrage tient pour le contenu des sections, pas pour leur ensemble. Une valeur ajoutée au
contrat laisserait `categories.md` en décrire une de moins, sans qu'aucune commande n'échoue —
`validate` juge les fiches contre le contrat, jamais la doc contre lui. Et le manque serait
silencieux là où il coûte le plus : `SKILL.md` envoie lire ce fichier **avant d'instruire**, si
bien qu'un verdict légitime resterait invisible au moment de classer.

C'est le mode de défaillance que le registre nomme déjà — une prose qui décrit un contrat que
l'outil n'applique pas — avec la circonstance aggravante qu'on la croit, parce qu'elle se lit plus
vite que le fichier qu'elle décrit.

## Pour solder

Confronter les titres de section de `categories.md` aux valeurs déclarées, et faire échouer la
divergence. `--values category` rend la comparaison faisable en une ligne, ce qui n'était pas le
cas avant ce chantier :

```bash
diff <(list-dir contract --def technical-debt --template review --values category) \
     <(grep -oP '^## .*— `\K[a-z-]+' skills/debt-review/references/categories.md)
```

Reste à décider **où ce contrôle vit** pour qu'il soit réellement joué : une commande propre à la
liste sous `.list/commands/`, un point de la procédure de `debt-review`, ou le contrôle de santé
des skills. Un contrôle écrit et jamais lancé serait une seconde prose qui décrit sans appliquer.

## Assumé

Le report est assumé : l'arbitrage du chantier a jugé que ce cas ne valait pas d'élargir son
périmètre, et cette entrée existe pour qu'il ne disparaisse pas avec lui.
