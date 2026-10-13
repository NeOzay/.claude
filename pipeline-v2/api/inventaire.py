"""Inventaire de l'API des mods, tiré des types que le moteur de Claude Code pose.

CE QU'IL RELÈVE : les événements que le moteur lève (`EngineEventOf`), ceux que lèvent les appels
sur `$` (`OpEventOf`), les noms de `$` et leurs méthodes (`CoreEngineInterface`), et les éléments
que chaque surface dessine (`Elements`). Une ligne par entrée, triées : deux inventaires se
comparent ligne à ligne.

POURQUOI LES TYPES : la référence de `plugin-authoring` les dit « EARLY ACCESS » et changeant
sans préavis ; le fichier de types est la seule description complète qu'une version porte, et il
nomme cette version sur sa première ligne.

LECTURE PAR BLOCS : le fichier est généré, son indentation est stable (deux espaces par niveau).
Un bloc se lit de son en-tête à son accolade fermante au même niveau ; un en-tête introuvable est
un échec nommé, jamais un inventaire vide.

Usage, depuis la racine du dépôt :

    python3 -I pipeline-v2/api/inventaire.py <types> [--compare <inventaire>]

Sans `--compare`, écrit `pipeline-v2/api/<version>.txt` à côté de ce script. Avec, compare
l'inventaire des types à celui du fichier donné et sort 1 s'ils diffèrent.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

# L'en-tête de chaque bloc, tel que le moteur l'écrit, et ce qu'on y relève.
BLOC_EVENEMENTS = "  export type EngineEventOf = {"
BLOC_OPERATIONS = "  export type OpEventOf = {"
BLOC_NOMS = "  export interface CoreEngineInterface {"
BLOC_ELEMENTS = "  export type Elements = {"

VERSION = re.compile(r"^// Written by Claude Code (\S+?)\.?$")
CLE_EVENEMENT = re.compile(r"^      '([a-zA-Z.]+)': ")
NOM = re.compile(r"^      (\w+): \{$")
MEMBRE = re.compile(r"^          (\w+)\??: ")


@dataclass(frozen=True)
class Inventaire:
    """Une version de l'API et ses lignes d'inventaire, triées."""

    version: str
    lignes: list[str]


@dataclass(frozen=True)
class Echec:
    """Ce qui empêche de dresser l'inventaire, dit pour l'utilisateur."""

    message: str


def bloc(lignes: list[str], entete: str) -> list[str] | Echec:
    """Rend les lignes du bloc ouvert par `entete`, jusqu'à son accolade fermante."""
    if entete not in lignes:
        return Echec(f"en-tête introuvable dans les types : {entete.strip()}")
    debut = lignes.index(entete) + 1
    for fin in range(debut, len(lignes)):
        if lignes[fin] in ("  };", "  }"):
            return lignes[debut:fin]
    return Echec(f"bloc non fermé : {entete.strip()}")


def cles(lignes: list[str], prefixe: str) -> list[str]:
    """Rend une ligne `<prefixe> <clé>` par clé d'événement du bloc."""
    return [f"{prefixe} {m.group(1)}" for ligne in lignes if (m := CLE_EVENEMENT.match(ligne))]


def membres(lignes: list[str], prefixe: str) -> list[str]:
    """Rend une ligne `<prefixe> <nom>.<membre>` par membre de chaque nom du bloc."""
    sortie: list[str] = []
    courant = ""
    for ligne in lignes:
        if m := NOM.match(ligne):
            courant = m.group(1)
        elif courant and (m := MEMBRE.match(ligne)):
            sortie.append(f"{prefixe} {courant}.{m.group(1)}")
    return sortie


def inventorier(texte: str) -> Inventaire | Echec:
    """Dresse l'inventaire de l'API d'après le texte d'un fichier de types."""
    lignes = texte.splitlines()
    version = VERSION.match(lignes[0]) if lignes else None
    if version is None:
        return Echec("première ligne inattendue : le fichier ne nomme pas sa version")
    blocs: list[list[str]] = []
    for entete in (BLOC_EVENEMENTS, BLOC_OPERATIONS, BLOC_NOMS, BLOC_ELEMENTS):
        lu = bloc(lignes, entete)
        if isinstance(lu, Echec):
            return lu
        blocs.append(lu)
    evenements, operations, noms, elements = blocs
    return Inventaire(
        version.group(1),
        sorted(
            {
                *cles(evenements, "événement"),
                *cles(operations, "opération"),
                *membres(noms, "$"),
                *membres(elements, "élément"),
            }
        ),
    )


def comparer(ancien: list[str], nouveau: list[str]) -> list[str]:
    """Rend `- ligne` pour chaque entrée disparue, `+ ligne` pour chaque entrée apparue."""
    retirees = sorted(set(ancien) - set(nouveau))
    ajoutees = sorted(set(nouveau) - set(ancien))
    return [f"- {ligne}" for ligne in retirees] + [f"+ {ligne}" for ligne in ajoutees]


def main() -> int:
    """Lit les arguments, dresse l'inventaire, l'écrit ou le compare."""
    parseur = argparse.ArgumentParser(description="Inventaire de l'API des mods.")
    _ = parseur.add_argument("types", type=Path, help="fichier de types du moteur")
    _ = parseur.add_argument("--compare", type=Path, help="inventaire précédent")
    arguments = parseur.parse_args()
    # argparse rend un Namespace sans types : `type=Path` garantit ce que `cast` affirme.
    types = cast("Path", arguments.types)
    compare = cast("Path | None", arguments.compare)
    inventaire = inventorier(types.read_text(encoding="utf-8"))
    if isinstance(inventaire, Echec):
        print(f"inventaire : {inventaire.message}", file=sys.stderr)
        return 2
    if compare is None:
        sortie = Path(__file__).parent / f"{inventaire.version}.txt"
        _ = sortie.write_text("\n".join(inventaire.lignes) + "\n", encoding="utf-8")
        print(f"{sortie} : {len(inventaire.lignes)} entrées, version {inventaire.version}")
        return 0
    ecarts = comparer(compare.read_text(encoding="utf-8").splitlines(), inventaire.lignes)
    for ecart in ecarts:
        print(ecart)
    return 1 if ecarts else 0


if __name__ == "__main__":
    sys.exit(main())
