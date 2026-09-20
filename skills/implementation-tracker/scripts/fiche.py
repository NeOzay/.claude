"""Lit le front matter d'une fiche du pipeline : brief, suivi, archive.

LECTEUR UNIQUE. `commit_chantier.py` et le contrôle 5 de `scripts/check_pipeline.py` lisent
tous deux le front matter par `lire_front`. Deux lecteurs alignés à la main divergent dès
qu'un motif change d'un seul côté, et rien n'échoue.

DEUX FORMATS, ET UN SEUL EST VIVANT. Une fiche posée par `gabarit` porte un front matter TOML
entre `+++`, lu par `tomllib` : une grammaire, donc une valeur ambiguë refusée au lieu d'être
tronquée. Le YAML plat entre `---` n'est lu qu'en repli, pour les archives figées de `done/`.
Le format lu est rendu à l'appelant : c'est lui qui refuse un YAML là où seule une fiche
vivante est attendue.

BIBLIOTHÈQUE STANDARD SEULE : le garde-fou tourne sous le `python3` du PATH, qui n'a pas
`tomlkit`. Écrire une fiche n'est pas le rôle de ce module, mais celui de `gabarit`.
"""

from __future__ import annotations

import datetime
import re
import tomllib
from dataclasses import dataclass
from typing import Literal

type Format = Literal["toml", "yaml"]

# Les délimiteurs, définis ici et NULLE PART AILLEURS : ce sont eux qui disent le format.
DELIMITEURS: dict[str, Format] = {"+++": "toml", "---": "yaml"}

# Une ligne d'archive : `clé: valeur`, le commentaire `  # …` de fin de ligne retiré, que la
# clôture conservait derrière un chemin réécrit.
LIGNE_YAML = re.compile(r"^(?P<cle>[\w-]+): *(?P<valeur>.*?)(?:\s+#.*)?$")


class FrontMatterError(ValueError):
    """Le front matter est absent, non fermé, ou ne se lit pas dans son format."""


@dataclass(frozen=True)
class Front:
    """Les champs d'un front matter, et le format dans lequel ils ont été lus."""

    format: Format
    champs: dict[str, str]


def lire_front(texte: str) -> Front:
    """Lit le front matter en tête de `texte`.

    Returns:
        Les champs, chacun rendu en texte : une date en `AAAA-MM-JJ`, un entier en chiffres.

    Raises:
        FrontMatterError: pas de délimiteur en première ligne, aucun délimiteur fermant, TOML
            invalide (clé en double comprise), valeur non scalaire, clé YAML en double.
    """
    lignes = texte.splitlines()
    ouvrant = lignes[0].strip() if lignes else ""
    fmt = DELIMITEURS.get(ouvrant)
    if fmt is None:
        raise FrontMatterError(
            "pas de front matter : la première ligne doit être « +++ » ou « --- »"
        )
    try:
        fin = next(i for i, ligne in enumerate(lignes[1:], 1) if ligne.strip() == ouvrant)
    except StopIteration:
        # Nommer CE défaut : lu comme vide, le front matter ferait accuser le premier champ
        # requis d'être absent, alors qu'il est là et que c'est la fermeture qui manque.
        raise FrontMatterError(
            f"front matter non fermé : aucune ligne « {ouvrant} » ne le termine"
        ) from None
    corps = lignes[1:fin]
    return Front(fmt, _lire_toml(corps) if fmt == "toml" else _lire_yaml(corps))


def _lire_toml(corps: list[str]) -> dict[str, str]:
    try:
        brut: dict[str, object] = tomllib.loads("\n".join(corps))
    except tomllib.TOMLDecodeError as exc:
        raise FrontMatterError(f"front matter TOML invalide — {exc}") from None
    return {cle: _texte(cle, valeur) for cle, valeur in brut.items()}


def _texte(cle: str, valeur: object) -> str:
    # Une fiche est plate : un tableau ou une table y est une erreur de saisie, pas une valeur
    # qu'un appelant saurait employer comme chemin ou comme statut.
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    if isinstance(valeur, str | int | float):
        return str(valeur)
    if isinstance(valeur, datetime.date):
        return valeur.isoformat()
    raise FrontMatterError(f"champ « {cle} » : valeur non scalaire ({type(valeur).__name__})")


def _lire_yaml(corps: list[str]) -> dict[str, str]:
    champs: dict[str, str] = {}
    for ligne in corps:
        m = LIGNE_YAML.match(ligne)
        if m is None or not m.group("valeur"):
            continue
        cle = m.group("cle")
        if cle in champs:
            raise FrontMatterError(f"champ « {cle} » en double dans le front matter")
        champs[cle] = m.group("valeur")
    return champs
