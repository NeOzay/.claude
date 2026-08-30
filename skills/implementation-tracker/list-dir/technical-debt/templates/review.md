Moule d'une fiche de revue. Tout ce qui précède le premier `##` est ignoré par
`derive` : seules les sections comptent, et le front matter est injecté depuis
`review.toml`. Ces lignes ne se retrouvent donc dans aucune fiche.

Le corps de chaque section est **exactement** le marqueur de son statut au
contrat — requise à `<À REMPLIR>`, facultative à `<OPTIONNEL>` — et rien d'autre.
`validate --filled` compare le corps au marqueur : une consigne écrite sous lui
suffirait à faire passer une fiche vierge pour instruite. Ce que chaque section
attend est dit ici, jamais dans la fiche.

- **Vérifié par** — la commande exécutée et sa sortie réelle. Elle doit se rejouer
  seule, sans contexte : c'est elle qui sera recopiée au registre. Sans commande
  exécutée, le verdict est `pertinent` — la plausibilité ne fait sortir personne du
  registre. `inverifiable` et `doublon` en sont dispensés, et disent ici pourquoi.
- **Verdict** — ce que la commande établit, et pourquoi cette catégorie plutôt que
  la voisine. Pour un `doublon`, citer l'intitulé de l'entrée conservée : c'est la
  preuve.
- **Action** — ce qu'il faut écrire au registre une fois l'arbitrage rendu : la
  liste de destination pour une entrée qui sort, le constat réécrit pour une
  `aggravee`, rien pour un `pertinent`.
- **Arbitrage** — rempli après l'arbitrage de l'utilisateur, et par lui seul :
  décision suivie, renversée, différée, ou élargie en règle. Laissée au marqueur,
  la section est omise de l'aggloméré.

## Vérifié par

<À REMPLIR>

## Verdict

<À REMPLIR>

## Action

<À REMPLIR>

## Arbitrage

<OPTIONNEL>
