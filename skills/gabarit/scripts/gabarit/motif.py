"""Le motif d'une section : un gabarit de ligne, découpé en littéraux et en captures.

PORTÉE : ce module découpe un motif — `"[{etat: enum}] {n: int}. {intitule}"` — et le
compile en expression ancrée. Il ne lit aucun fichier et ne juge aucune valeur capturée :
le type d'une capture se juge par `check_value`, et par elle seule.

PAS UNE REGEX : l'auteur d'un contrat écrit des littéraux et des `{nom}` ou `{nom: type}`,
rien d'autre. L'expression compilée est un détail d'implémentation ; en accepter une
écrite à la main ferait du motif une seconde syntaxe.

LES BLANCS SE RÉDUISENT À UNE ESPACE, dans le motif comme dans la puce : une puce peut
courir sur plusieurs lignes, et rumdl réenroule ce qui dépasse.

Ne dépend que de `types`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .types import Capture, FieldType, Result, fail, ok

CAPTURE_TYPES: tuple[FieldType, ...] = ("slug", "text", "date", "enum", "int")
"""Les types qu'une capture peut déclarer. `bool` et `list` n'y sont pas : aucun cas ne
les demande, et `list` exigerait un séparateur à déclarer."""

DEFAULT_CAPTURE_TYPE: FieldType = "text"
"""Le type d'une capture écrite `{nom}`, sans type."""

_BLANCS = re.compile(r"\s+")


@dataclass(frozen=True)
class Trou:
    """Une capture telle que le motif l'écrit : son nom et son type."""

    nom: str
    type: FieldType


type Morceau = str | Trou
"""Un littéral ou une capture, dans l'ordre du motif."""


def reduit_blancs(texte: str) -> str:
    """Chaque suite de blancs ramenée à une espace, bords compris — jamais retirés."""
    return _BLANCS.sub(" ", texte)


def _trou(contenu: str) -> Result[Trou]:
    """`nom` ou `nom: type`, lu entre deux accolades."""
    nom, deux_points, type_ = contenu.partition(":")
    nom = nom.strip()
    if not nom.isidentifier():
        return fail(f"nom de capture « {nom} » invalide — un identifiant est attendu")
    declare = type_.strip() if deux_points else DEFAULT_CAPTURE_TYPE
    for connu in CAPTURE_TYPES:
        if declare == connu:
            return ok(Trou(nom, connu))
    return fail(
        f"capture « {nom} », type « {declare} » inconnu ; attendus : {', '.join(CAPTURE_TYPES)}"
    )


def decoupe(motif: str) -> Result[list[Morceau]]:
    """Les littéraux et les captures d'un motif, dans l'ordre.

    LE MESSAGE D'ÉCHEC EST LA RAISON SEULE : l'appelant le place après le chemin de la
    section, qu'il est seul à connaître.

    Refusés : une accolade non appariée, une accolade dans une capture, un nom invalide,
    un type hors `CAPTURE_TYPES`, deux captures de même nom, deux captures sans littéral
    entre elles — rien ne dirait où finit la première.
    """
    morceaux: list[Morceau] = []
    vus: set[str] = set()
    reste = motif
    while reste:
        ouvre = reste.find("{")
        ferme = reste.find("}")
        if ferme != -1 and (ouvre == -1 or ferme < ouvre):
            return fail("accolade « } » sans « { » qui l'ouvre")
        if ouvre == -1:
            morceaux.append(reste)
            break
        if ouvre > 0:
            morceaux.append(reste[:ouvre])
        if ferme == -1:
            return fail("accolade « { » jamais fermée")
        if "{" in reste[ouvre + 1 : ferme]:
            return fail("accolade « { » dans une capture")
        trou = _trou(reste[ouvre + 1 : ferme])
        if not trou:
            return fail(trou.message)
        t = trou.unwrap()
        if t.nom in vus:
            return fail(f"capture « {t.nom} » déclarée deux fois")
        if morceaux and isinstance(morceaux[-1], Trou):
            return fail(f"captures « {morceaux[-1].nom} » et « {t.nom} » sans littéral entre elles")
        vus.add(t.nom)
        morceaux.append(t)
        reste = reste[ferme + 1 :]
    return ok(morceaux)


def trous(morceaux: Sequence[Morceau]) -> list[Trou]:
    """Les captures seules, dans l'ordre du motif."""
    return [m for m in morceaux if isinstance(m, Trou)]


def compile_motif(morceaux: Sequence[Morceau], captures: Mapping[str, Capture]) -> re.Pattern[str]:
    """L'expression qu'une puce, `debut` et `fin` retirés et blancs réduits, doit couvrir.

    Un littéral est échappé, ses blancs réduits, ceux des deux bords du motif retirés —
    la puce est rognée. Une capture requise couvre au moins un caractère, une facultative
    peut rester vide ; chacune est un groupe nommé, de son nom. À appliquer par
    `fullmatch`.

    L'ESPACE QUI BORDE UNE CAPTURE FACULTATIVE EST FACULTATIVE ELLE AUSSI : la puce est
    rognée, et `— vérif: {verif}` laissé vide finit sur « vérif: », sans l'espace que le
    motif écrit.
    """

    def facultative(m: Morceau | None) -> bool:
        return isinstance(m, Trou) and m.nom in captures and not captures[m.nom].required

    parties: list[str] = []
    for i, m in enumerate(morceaux):
        if isinstance(m, Trou):
            parties.append(f"(?P<{m.nom}>{'.*?' if facultative(m) else '.+?'})")
            continue
        litteral = reduit_blancs(m)
        if i == 0:
            litteral = litteral.lstrip()
        if i == len(morceaux) - 1:
            litteral = litteral.rstrip()
        avant = i > 0 and facultative(morceaux[i - 1]) and litteral.startswith(" ")
        apres = i + 1 < len(morceaux) and facultative(morceaux[i + 1]) and litteral.endswith(" ")
        coeur = litteral[1 if avant else 0 : len(litteral) - 1 if apres else len(litteral)]
        parties.append(("[ ]?" if avant else "") + re.escape(coeur) + ("[ ]?" if apres else ""))
    return re.compile("".join(parties))
