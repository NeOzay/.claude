+++
id = "marqueurs-recopies-dans-gabarits"
title = "Les deux marqueurs sont recopiés en dur dans les gabarits, hors de tout contrôle"
date = 2026-08-23
source = "chantier `format-registres`, R5 des audits de clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`todo/technical-debt/.list/templates/review.md` écrit `<À REMPLIR>` et `<OPTIONNEL>` en dur, quatre
fois au total. La Vérification #9 du plan, qui exige une définition unique de chaque marqueur, ne
balaie que `skills/list-dir/scripts/` : elle est aveugle à ce fichier.

## Pourquoi c'est gênant

C'est le mode de défaillance que la constante `PLACEHOLDER` existe pour interdire. Si le marqueur
change un jour dans `types.py`, `validate --filled` comparera le corps des sections au nouveau
marqueur, ne le trouvera pas — et **laissera passer une fiche vierge pour instruite**. L'échec est
silencieux et arrive au pire moment : un rapport de revue part à l'arbitrage avec des verdicts qui
n'existent pas.

Le préambule de `review.md` énonce bien la règle (« le corps est exactement le marqueur »), mais
aucune commande ne la vérifie.

## Pour solder

Deux voies, à trancher :

- étendre le contrôle de définition unique aux gabarits `.list/templates/` de toutes les listes, en
  acceptant que le marqueur y soit **cité** mais en exigeant qu'il corresponde à la constante ;
- ou faire poser les marqueurs par `derive` plutôt que par le corps du gabarit — le `.md` ne
  porterait que les titres de section, les corps venant de `PLACEHOLDER` / `OPTIONAL`.

La seconde supprime la duplication au lieu de la surveiller, mais change le contrat du gabarit.

## Assumé

<OPTIONNEL>
