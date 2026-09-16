---
name: gabarit
description: >
  Crée un fichier préstructuré à remplir depuis une semence, hors de toute liste, et le vérifie
  ensuite contre elle. Fournit quatre commandes (new, check, contract, defs), des semences
  réutilisables résolues par leur nom — dont `suivi`, le fichier de suivi d'implementation-tracker —
  et la bibliothèque Python sur laquelle list-dir est construit. Se déclenche dès qu'il s'agit de
  poser un fichier depuis un contrat, de dire ce qu'il attend, ou de vérifier qu'il est rempli.
  Ne juge aucun contenu.
---

# gabarit — un fichier préstructuré, depuis une semence

Un **gabarit** est un fichier Markdown à front matter TOML (`+++`), dont les champs et les sections
sont déclarés par un **contrat**. Une **semence** est un répertoire qui porte ce contrat. `gabarit`
pose le fichier, prérempli de tout ce qui est mécaniquement connu, et le vérifie ensuite.

**Une list-dir est une liste de gabarits.** Le format d'un fichier, le contrat et le préremplissage
sont exactement ceux d'un élément de liste, et `list-dir` les tient de ce paquet :
[Le contrat](../list-dir/references/format.md#le-contrat). Ce qui n'appartient qu'à une liste —
l'`id` égal au nom du fichier, `.list/`, `from`, `[origin]`, `reseed` — reste dans list-dir.

**Partage des rôles** : les commandes font la structure — poser, vérifier, imprimer un contrat.
Remplir reste au modèle, qui écrit directement dans le fichier ; `check` repasse après.

## Les quatre commandes

```bash
gabarit new <nom> <fichier>            # pose le fichier, prérempli et estampillé
gabarit new --from <chemin> <fichier>  # ... depuis le répertoire d'une semence, tel quel
gabarit check <fichier> [--filled]     # vérifie contre la semence de son estampille
gabarit check <fichier> --def <nom>    # ... ou contre une semence imposée (--from <chemin>)
gabarit contract <nom> [--values <c>]  # le contrat tel qu'écrit, ou les valeurs d'un champ
gabarit defs                           # les semences disponibles, leur rang et leur origine
```

`gabarit` est un lien de `bin/` vers `scripts/gabarit-cli.py`, résolu par le `PATH`.

Codes de sortie : **0** succès, la valeur seule sur stdout ; **1** refus ou échec, message sur
stderr ; **2** erreur d'appel. Un avertissement sort sur stderr sans toucher au code.

**Un fichier posé ne dit pas ce qu'il attend.** Avant de le remplir, lire
`gabarit contract <nom>` : chaque champ et chaque section y porte sa description. Un marqueur dit
qu'il faut écrire, jamais quoi écrire.

**Deux verdicts**, ceux de `list-dir validate`. Sans `--filled`, la structure seule : les marqueurs
sont légitimes. Avec, plus aucun `<À REMPLIR>` là où le contrat exige quelque chose — les
facultatifs restés `<OPTIONNEL>` ne sont jamais réclamés.

**Rien n'est écrasé ni écrit à moitié** : `new` refuse un fichier existant, et une commande de
préremplissage qui échoue n'écrit rien.

## L'estampille

Tout fichier posé par `new` porte en tête `gabarit = "<nom>"` : le nom sous lequel sa semence se
résout. `check` s'en sert pour la retrouver, et c'est ce qui permet de vérifier un fichier sans rien
dire d'autre que son chemin — même après un renommage ou un déplacement. Le nom est réservé, et
jamais compté comme champ non déclaré.

Semences, racines, estampille et environnement du préremplissage :
[`references/semences.md`](references/semences.md).

## Les semences livrées

| Semence | Ce qu'elle pose |
|---|---|
| `suivi` | le fichier de suivi d'implementation-tracker — `skills/gabarit/gabarit/suivi/` |

## La bibliothèque

La commande n'est qu'une façade : tout passe par le paquet `gabarit`, importable.

```python
import shutil, sys
from pathlib import Path

cmd = shutil.which("gabarit")
if cmd is None:
    raise SystemExit("gabarit introuvable dans le PATH — ajouter bin/ au profil du shell")
sys.path.insert(0, str(Path(cmd).resolve().parent))
from gabarit.commandes import check, new, trouver_semence

semence = trouver_semence("suivi", None).unwrap()
new(Path("mon-suivi.md"), semence).unwrap()
```

| Module | Ce qu'il porte |
|---|---|
| `types` | `Result`, marqueurs, `Field`, `Section`, `Contract`, `Item`, `Violation` |
| `items` | lecture et écriture d'un fichier : front matter reprojeté, sections, fences |
| `contract` | lecture et jugement d'un contrat, `check_value` |
| `check` | un fichier confronté à un contrat |
| `prefill` | `text`/`command`, à environnement fourni par l'appelant |
| `definitions` | les quatre racines, paramétrées par le nom de répertoire |
| `commandes` | `new`, `check`, `contract`, `defs`, l'estampille |

**`gabarit` n'importe jamais `listdir`** : la dépendance va dans l'autre sens, et elle ne se
retourne pas.
