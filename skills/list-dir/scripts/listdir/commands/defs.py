"""Les définitions de listes disponibles, et d'où elles viennent.

C'EST LE SEUL POINT D'OÙ `init --def` SE DÉCOUVRE. Sans cette commande, les noms
qu'il accepte ne s'apprennent qu'en lisant l'arborescence à la main — et le rang
qui l'emporte ne s'apprend pas du tout.

LA RACINE DE PROJET RETENUE EST IMPRIMÉE, et ce n'est pas un ornement : elle est
trouvée en remontant jusqu'au PREMIER répertoire contenant un `.claude`, qui n'est
pas nécessairement celui qu'on avait en tête. Un dépôt imbriqué dans un autre
donnerait des définitions surprenantes sans que rien ne le signale. L'imprimer rend
le choix visible plutôt que deviné.

LES MASQUÉES SONT MONTRÉES, PAS TUES. Une définition de rang 1 en masque une de
rang 4 : c'est le comportement voulu, mais taire la perdante ferait chercher
longtemps pourquoi une liste n'est pas amorcée avec le contrat attendu.

AUCUNE LOGIQUE ICI : la découverte vit dans definitions.py, ce module la met en page.

IMPORTS ABSOLUS, jamais relatifs : un module de commande est chargé par chemin de
fichier, hors de tout paquet.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from listdir.definitions import Root, config_root, definitions, project_root, roots
from listdir.types import Result, Utils

DESCRIPTION = "les définitions de listes disponibles, avec leur origine"
REQUIRES: list[str] = []


def register(parser: argparse.ArgumentParser) -> None:
    _ = parser  # aucune option : la découverte ne se paramètre pas


def _ancrages() -> list[str]:
    """Les deux points de départ, dits avant la liste qu'ils produisent."""
    projet = project_root(Path.cwd())
    config = config_root(Path(__file__).parent)
    return [
        f"projet : {projet if projet is not None else 'aucun — rangs 1 et 2 absents'}",
        f"config : {config if config is not None else 'aucune — rangs 3 et 4 absents'}",
    ]


def _ligne(nom: str, portee: list[Root]) -> str:
    """Ce que `init --def <nom>` ferait de ce nom, et rien d'autre.

    LE RANG SE COMPARE, IL NE SE SUPPOSE PAS. Prendre `portee[0]` pour gagnante
    reviendrait à désigner une définition que `resolve()` refuse justement de
    choisir : deux racines de MÊME rang sont ambiguës, et l'ordre de parcours n'est
    pas un départage.

    > *Mode de défaillance* — `defs` annonçait « rang 2, projet:a (masque projet:b) »
    > pendant qu'`init --def` sortait 1 en refusant de trancher. La commande de
    > découverte promettait ce que la commande d'amorçage refusait, et c'est la
    > promesse qu'on croit : elle se lit avant.
    """
    premier = portee[0].rank
    exaequo = [r for r in portee if r.rank == premier]
    if len(exaequo) > 1:
        origines = ", ".join(r.origin for r in exaequo)
        return f"  {nom:<28} rang {premier}  AMBIGUË — {origines} ; `init --def` refusera"

    masquees = "".join(f"  (masque {r.origin})" for r in portee[1:])
    return f"  {nom:<28} rang {premier}  {portee[0].origin}{masquees}"


def command(args: argparse.Namespace, utils: Utils) -> Result[str]:
    _ = args
    trouvees = definitions(roots())
    lignes = [*_ancrages(), ""]
    if not trouvees:
        # Une liste vide n'est pas un échec : hors de tout `.claude`, il n'y a
        # simplement rien à proposer. Le dire vaut mieux qu'une sortie muette,
        # qu'on lirait comme un plantage.
        lignes.append("  aucune définition")
    else:
        lignes += [_ligne(nom, trouvees[nom]) for nom in sorted(trouvees)]
    return utils.ok("\n".join(lignes))
