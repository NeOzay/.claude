---
slug: 2026-08-31-champs-preremplis
titre: Préremplissage des champs et sections d'un contract.toml (command / text)
statut: validé
execution: délégué
créé: 2026-08-31
---

## Intention

**Symptôme** : à la création d'un élément, tout champ ou section non fourni reçoit un marqueur
(`<À REMPLIR>` / `<OPTIONNEL>`) qu'il faut remplir à la main, y compris quand la valeur est
mécaniquement connue — « pour une date, une commande, placer directement la date du jour » (dit).

**But** : ajouter deux valeurs optionnelles aux `fields` et aux `sections` d'un `contract.toml` :
`command` (commande Bash dont le résultat sera utilisé comme texte) et `text` (texte utilisé à la
place du placeholder) (dit).

## Critères de réussite

- `cd skills/list-dir/scripts && uvx pytest tests -q` passe (307 tests verts avant chantier)
- un contrat déclarant `command = "date +%F"` sur un champ `date` produit, à `list-dir new`, un
  élément dont ce champ porte la date du jour et non `<À REMPLIR>`
- un contrat déclarant `text = "…"` produit ce texte à la place du marqueur, champ comme section
- `list-dir migrate` et `list-dir derive` posent la même valeur pour un champ absent (dit)
- une `command` qui échoue fait échouer la création : rien n'est écrit, et le message nomme la
  commande incriminée (dit)
- un contrat déclarant `text` et `command` sur un même champ est refusé par `parse_contract`, en
  nommant le champ (tranché)

## Hors-périmètre

- pas de variables déclarées au contrat (`[fields.date.env]`) — « hors sujet pour le moment » (dit)
- les définitions de listes livrées (`defs`) ne sont pas modifiées : moteur + documentation
  seulement (tranché)
- aucun autre changement du contrat : pas de nouveau `type`, pas de nouvelle commande

## Signaux de dérive

- si un mécanisme de substitution ou de gabarit apparaît dans `text` (`{{id}}`, `$VAR`), c'est
  raté : `text` est du texte littéral, le dynamique passe par `command`
- si l'exécution des commandes s'étend au-delà des trois sites de pose de marqueur
  (`create`, `_realign`, `_project`), s'arrêter et en reparler
- si `gitcmd.py` cesse d'être le seul appel de processus du paquet sans qu'un module dédié à
  l'exécution ait été introduit et documenté, s'arrêter
- si le diff dépasse `types.py`, `contract.py`, `store.py`, un module d'exécution, la doc et les
  tests, s'arrêter et en reparler

## Contraintes connues de l'utilisateur

- **Portée** : « cela s'applique à toute création de champ, donc aussi à migrate/derive si le champ
  n'est pas présent » (dit)
- **Échec de `command`** : « ne pas créer l'élément et indiquer dans la sortie l'erreur avec la
  commande incriminée » (dit) — cohérent avec l'échec fermé du paquet
- **Contexte d'exécution** : « exécuter dans le répertoire de la liste » (dit) ; environnement
  enrichi de `LISTDIR_ID`, `LISTDIR_NAME`, `LISTDIR_LIST`, `LISTDIR_CONTRACT` et `LISTDIR_ROOT`
  (dit) — `LISTDIR_ROOT` = racine git, variable non définie si la liste est hors dépôt (dit)
- **Valeur préremplie = valeur ordinaire** : `validate --filled` ne la signale pas, `merge` la fait
  sortir (tranché)
- **Sortie de `command` confrontée au type** du champ via `check_value` (tranché)
- **Aucune exécution de processus externe aujourd'hui** hors `git` — « Le seul appel à git du
  paquet » (dépôt: skills/list-dir/scripts/listdir/gitcmd.py)
- **Trois sites de pose de marqueur** : `create`, `_realign` (migrate), `_project` (derive)
  (dépôt: skills/list-dir/scripts/listdir/store.py:229, :303, :331, :512)
- **Les marqueurs sont définis à un seul endroit** et interdits de recopie
  (dépôt: skills/list-dir/scripts/listdir/types.py:30-33)

## Incertitudes à lever en plan

- `Field.marker` / `Section.marker` sont des propriétés pures (`types.py`) ; une valeur issue d'une
  commande peut échouer et ne peut donc pas y vivre — reste à déterminer où passe la frontière
  entre le marqueur calculé et la valeur exécutée
