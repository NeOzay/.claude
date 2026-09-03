Moule d'une fiche de revue. Tout ce qui précède le premier `##` est ignoré par
`derive` : seules les sections comptent, et le front matter est injecté depuis
`review.toml`. Ces lignes ne se retrouvent donc dans aucune fiche.

Le corps de chaque section est **exactement** le marqueur de son statut au
contrat — requise à `<À REMPLIR>`, facultative à `<OPTIONNEL>` — et rien d'autre.
`validate --filled` compare le corps au marqueur : une consigne écrite sous lui
suffirait à faire passer une fiche vierge pour instruite.

Ce que chaque section attend est dit au contrat, `review.toml` — jamais ici, et
jamais dans la fiche : `list-dir contract <revue>` l'imprime. Ce qui suit n'y tient
pas, et c'est pourquoi c'est écrit ici :

- **Vérifié par** — sans commande exécutée, le verdict est `pertinent` : la
  plausibilité ne fait sortir personne du registre. `inverifiable` et `doublon` en
  sont dispensés, et disent ici pourquoi.
- **Verdict** — pour un `doublon`, citer l'`id` de l'entrée conservée : c'est la
  preuve, à la place d'une commande.
- **Action** — la liste de destination pour une entrée qui sort, le constat réécrit
  pour une `aggravee`, rien pour un `pertinent`.
- **Arbitrage** — rempli après l'arbitrage de l'utilisateur, et par lui seul.
  Laissée au marqueur, la section est omise de l'aggloméré.

## Vérifié par

<À REMPLIR>

## Verdict

<À REMPLIR>

## Action

<À REMPLIR>

## Arbitrage

<OPTIONNEL>
