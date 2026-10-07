+++
id = "registre-de-dette-severite-chantier-pin"
title = "Faire évoluer le registre de dette : sévérité, chantier, référence, pin, découpage de `source`"
date = 2026-10-07
source = "chantier socle-contrat-evolutif (clos), Hors-périmètre du Brief ; précisions de l'utilisateur"
+++

## À faire

Second Chantier annoncé par `socle-contrat-evolutif`, qui en a livré le socle : faire évoluer le
contrat des trois listes `technical-debt`, `technical-debt-solde` et `technical-debt-ecarte`, puis
migrer leurs entrées. Ce que l'utilisateur a dit, et qu'aucun fichier ne porte ailleurs :

- **`severite`**, un `enum` dont les `values` se déclarent dans l'ordre `note`, `avertissement`,
  `majeur`, `critique` : remplie par **celui qui crée la dette**, non par un script ;
- **`chantier`** : le nom du Chantier d'où vient la dette, ou « Hors chantier » ;
- **`reference`** : un `R<n>` du rapport d'audit, ou le lieu du constat ;
- **`pin`**, un `bool` valant `false` par défaut ;
- **le découpage de `source`** : le champ libre actuel se scinde, et passe par `deprecated`
  (jamais posé dans une entrée neuve, signalé tant qu'une entrée le porte), au lieu d'être retiré
  d'un coup ;
- **la migration des listes du pipeline** : `reseed` puis `migrate` sur les trois listes, dont
  les contrats sont des copies détachées de leurs définitions.

Le socle sert chacun de ces points : `bool`, Marqueurs typés (`migrate` convertit aussi les
`reviewed = "<OPTIONNEL>"` des 63 entrées qui portent encore l'ancien), `deprecated`, tri typé
(`list --sort=-severite` classe du plus grave au moins grave, dans l'ordre des `values`).

À trancher au Brief :

- remplir la sévérité des entrées existantes demande de les relire une à une : c'est un jugement,
  hors de portée de `migrate`, qui ne pose que le Marqueur. Faut-il le faire dans ce Chantier, ou
  laisser la sévérité facultative jusqu'à la prochaine `/debt-review` ?
- `/debt-review` lit et dérive le registre : son patron `review.toml` et son rapport doivent-ils
  porter `severite` et `pin` ? Un `pin` doit-il protéger une entrée d'une sortie par la revue ?
- les entrées de `technical-debt-solde` et de `technical-debt-ecarte` portent-elles les mêmes
  champs que `technical-debt` (`move` conserve les champs d'une liste à l'autre) ?

Hors de ce Chantier : l'adaptation de Neovim aux Marqueurs typés et au type `bool`, qui est son
propre Chantier.

## Références

- Chantier source, archivé : `.claude/implementation/done/2026-10-07-socle-contrat-evolutif.md`, son
  Brief (`.brief.md`, section « Hors-périmètre »), son Plan (`.plan.md`) et son audit
  (`.audit.md`) ; commit `c647f97` sur `master`
- contrats à faire évoluer : les définitions
  `skills/implementation-tracker/list-dir/technical-debt/`, `technical-debt-solde/` et
  `technical-debt-ecarte/`, et les copies détachées sous
  `.claude/implementation/todo/<liste>/.list/` ; mode d'emploi de `reseed` et `migrate` :
  `skills/list-dir/references/provenance.md` et `operations.md`
- règles du registre : `skills/implementation-tracker/references/dette.md`, et
  `skills/implementation-tracker/references/cloture.md`, point 2 (alimentation à la clôture)
- consommateur : `skills/debt-review/`, son patron `review.toml` et `references/gabarit-rapport.md`
- syntaxe du socle : `skills/gabarit/references/format.md`, sections « `deprecated` » et « Les
  marqueurs » ; `skills/list-dir/references/operations.md`, sections « Quand le contrat change » et
  « Lister et filtrer »
- dettes liées, dans `technical-debt/` : `notes-ancien-marqueur-sur-les-listes-reelles` (le
  `migrate` de ce Chantier la solde), `dates-entre-guillemets-acceptees`,
  `parsing-du-contrat-avale-les-cles-inconnues` (une faute de frappe sur `deprecated` passe sans un
  mot), `consommateurs-des-marqueurs-generiques-hors-etat` (Neovim et `dette.md`)
