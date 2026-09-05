"""Affiche un contrat, tel qu'il est sur le disque : celui d'une liste, ou celui d'une définition.

TROIS CIBLES, ET UNE SEULE À LA FOIS. `<liste>` vise le contrat EN VIGUEUR d'une
liste ; `--def <nom>` et `--from <chemin>` visent une DÉFINITION, exactement comme
pour `init`. Les trois sont dans le même groupe mutuellement exclusif — argparse
refuse lui-même la combinaison, et l'absence totale de cible est une erreur d'appel.

CE QUE LA DISTINCTION ENGAGE, et elle n'est pas cosmétique. Une liste amorcée est
détachée de la définition qui l'a semée : elle porte sa propre copie, et c'est cette
copie seule que `validate`, `new` et `migrate` appliquent. `<liste>` rend donc la
règle RÉELLEMENT APPLIQUÉE ; `--def`/`--from` rendent celle d'une semence, qui ne
s'applique à aucune liste tant qu'elle n'en a pas amorcé une. La doc qui renvoie ici
doit dire laquelle des deux elle décrit.

POURQUOI `--def`/`--from` EXISTENT MALGRÉ ÇA : une liste engendrée par `derive`
n'existe qu'après coup. Une prose qui la décrit d'avance ne peut pas renvoyer à son
contrat — il n'y en a pas encore. Le gabarit source, lui, est là dès le départ.

`--template <nom>` VISE LE `<nom>.toml` DE `templates/` au lieu du contrat. C'est un
NOM, pas un chemin — la règle est portée par `contract.source_path`. Seul le `.toml`
est exigé : cette commande ne rend pas le `.md`, et réclamer un fichier qu'on
n'imprime pas ferait échouer une impression pour une raison étrangère à elle.

`--values <champ>` REND LES VALEURS DÉCLARÉES DE CE CHAMP, une par ligne et rien
d'autre — de quoi boucler dessus sans découper du TOML au `sed`, qui rend une liste
vide dès que le formatage bouge et le fait sous un code 0. Une valeur vide ou portant
un blanc est refusée à la lecture du contrat, pour qu'une substitution ne puisse pas
en fabriquer deux.

CE QUE CETTE OPTION NE PEUT PAS FAIRE À LA PLACE DE L'APPELANT : une substitution de
commande avale le code de retour. `for c in $(list-dir contract … --values category)`
itère donc zéro fois et réussit quand la commande a échoué — l'erreur part bien sur
stderr, mais un tableau vide se lit « rien à compter ». L'appelant affecte, teste,
puis lit ligne à ligne ; la forme exacte est dans `references/definitions.md`.

D'OÙ CETTE COMMANDE. `show` rend un élément, `validate` confronte des éléments au
contrat — rien n'imprimait le contrat lui-même. Une prose qui recopie les champs
d'un contrat est une copie de plus à tenir à jour ; un renvoi vers cette commande
n'en est pas une.

LE TEXTE EST RENDU TEL QUEL, commentaires compris : ils portent souvent le pourquoi
d'un champ, et un contrat reformaté par un aller-retour de parseur perdrait
justement ce que le lecteur venait chercher.

AUCUNE LOGIQUE ICI. Comme toutes les commandes, ce module se réduit à un register()
et à des appels de bibliothèque : c'est ce qui garantit qu'un script tiers et la
ligne de commande font exactement la même chose. La résolution d'un nom de
définition vit dans definitions.py ; celle d'un fichier de contrat, sa lecture
validée et l'extraction des `values` vivent dans contract.py.

IMPORTS ABSOLUS, jamais relatifs : un module de commande est chargé par chemin de
fichier, hors de tout paquet.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

from listdir.contract import field_values, list_base, load_source
from listdir.definitions import resolve, roots
from listdir.types import Result, Utils, fail, ok

DESCRIPTION = "affiche un contrat : celui d'une liste, ou celui d'une définition"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    cible = parser.add_mutually_exclusive_group()
    _ = cible.add_argument("liste", nargs="?", default="", help="le répertoire-liste")
    _ = cible.add_argument(
        "--def", dest="definition", default="", help="une définition, par son nom"
    )
    _ = cible.add_argument(
        "--from", dest="depuis", default="", help="une définition, par son chemin"
    )
    parser.add_argument(
        "--template", default="", help="le gabarit <nom>.toml de templates/, au lieu du contrat"
    )
    parser.add_argument(
        "--values",
        default="",
        metavar="CHAMP",
        help="les valeurs déclarées de ce champ, une par ligne, au lieu du contrat",
    )


def _base(args: argparse.Namespace) -> Result[Path]:
    """La base désignée par la ligne de commande, quelle que soit la forme employée.

    Le seul aiguillage que ce module porte : trois cibles, une base. Ce qu'une base
    contient et comment on y lit un contrat ne le regarde pas — c'est contract.py.
    """
    nom = cast("str", args.definition)
    chemin = cast("str", args.depuis)
    liste = cast("str", args.liste)

    if nom:
        return resolve(nom, roots())
    if chemin:
        return ok(Path(chemin))
    if liste:
        return ok(list_base(Path(liste)))
    # Code 2 : une commande sans cible est une erreur d'appel, au même titre que
    # `--def` et `--from` ensemble, qu'argparse refuse déjà avec ce code.
    return fail("aucune cible — <liste>, --def <nom> ou --from <chemin> est attendu", 2)


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    base = _base(args)
    if not base:
        return utils.fail(base.message, base.status)

    lu = load_source(base.unwrap(), cast("str", args.template))
    if not lu:
        return utils.fail(lu.message)
    chemin, texte, contrat = lu.unwrap()

    champ = cast("str", args.values)
    if not champ:
        return utils.ok(texte.rstrip("\n"))

    valeurs = field_values(contrat, champ, chemin)
    if not valeurs:
        return utils.fail(valeurs.message)
    return utils.ok("\n".join(valeurs.unwrap()))
