+++
id = "prefill-marqueur-produit-accepte-en-silence"
title = "Deux échecs silencieux du préremplissage : un marqueur produit, et une section vide"
date = 2026-08-31
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

Les deux cas reproduits le 2026-09-06 dans un même élément — contrat portant
`[fields.marque] type = "date"`, `command = "echo '<À REMPLIR>'"` et `[sections."Notes"]`,
`command = "true"` :

```
$ list-dir new l a; echo "code $?"
code 0
$ cat l/a.md
+++
id = "a"
jour = "2026-09-06"
marque = "<À REMPLIR>"
ou = "l"
+++

## Notes

```
Le champ `marque`, de type `date`, porte le marqueur ; la section `Notes` est vide, sans marqueur
et sans message. `new` sort 0 dans les deux cas.

```
$ grep -n -A3 "def initial_section" skills/list-dir/scripts/listdir/prefill.py
165:def initial_section(s: Section, item_id: str, ctx: PrefillContext) -> Result[str]:
167:    son marqueur. Une section n'a pas de type déclaré : rien à confronter."""
```

## Verdict

Les deux chemins avalent toujours, exactement comme au constat. `check_value` suspend le contrôle
de type sur `is_marker`, donc un marqueur **produit** par une commande passe pour une valeur
légitime ; et `initial_section` ne confronte rien, donc une sortie vide pose une section vide.

Le refus demandé au `Pour solder` — `is_marker` sur la sortie **avant** `check_value`, et refus
d'une sortie vide — n'a été écrit ni pour les champs ni pour les sections. Le module continue de
proclamer « ÉCHEC FERMÉ […] Rien n'est avalé » en en-tête.

**Une nuance mesurée, à verser à l'entrée** : le champ marqué n'a été *réclamé* par
`validate --filled` que parce qu'il était requis dans le cas d'origine ; posé en `required = false`
comme ici, il ne l'est pas, et l'élément passe `--filled` avec le marqueur en place. Le défaut est
donc au moins aussi large que décrit.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

**Correction appliquée le 2026-09-06.** Le Constat porte désormais la nuance mesurée : la réclamation
par `validate --filled` ne vaut que pour un champ **requis**, et un champ facultatif passe le
contrôle avec son marqueur en place. Le défaut est donc plus large que ce que l'entrée décrivait.
