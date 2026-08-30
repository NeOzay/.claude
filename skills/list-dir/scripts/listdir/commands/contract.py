"""Affiche le contrat EN VIGUEUR d'une liste, tel qu'il est sur le disque.

CELUI DE LA LISTE, JAMAIS CELUI D'UNE DÉFINITION. Une liste amorcée est détachée de
la définition qui l'a semée : elle porte sa propre copie, et c'est cette copie
seule que `validate`, `new` et `migrate` appliquent. Une documentation qui
renverrait à la définition décrirait donc autre chose que ce que l'outil applique,
et le dirait d'autant plus faux que le projet a délibérément redéfini sa liste.

D'OÙ CETTE COMMANDE. `show` rend un élément, `validate` confronte des éléments au
contrat — rien n'imprimait le contrat lui-même. Une prose qui recopie les champs
d'un contrat est une copie de plus à tenir à jour ; un renvoi vers cette commande
n'en est pas une.

LE TEXTE EST RENDU TEL QUEL, commentaires compris : ils portent souvent le pourquoi
d'un champ, et un contrat reformaté par un aller-retour de parseur perdrait
justement ce que le lecteur venait chercher.

IMPORTS ABSOLUS, jamais relatifs : un module de commande est chargé par chemin de
fichier, hors de tout paquet.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

from listdir.contract import contract_path
from listdir.types import Result, Utils

DESCRIPTION = "affiche le contrat en vigueur d'une liste"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("liste", help="le répertoire-liste")


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    # `utils.open` d'abord : il charge ET valide le contrat. Imprimer sans juger
    # rendrait un contrat cassé sous un code de succès, et le lecteur croirait
    # tenir la règle en vigueur alors qu'aucune commande ne peut l'appliquer.
    store = utils.open(cast("str", args.liste))
    if not store:
        return utils.fail(store.message)

    chemin = contract_path(Path(cast("str", args.liste)))
    try:
        return utils.ok(chemin.read_text(encoding="utf-8").rstrip("\n"))
    except OSError as exc:
        return utils.fail(f"{chemin}: illisible — {exc.strerror}")
