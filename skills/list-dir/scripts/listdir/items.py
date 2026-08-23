"""Lecture et écriture d'un élément : front matter TOML + sections Markdown.

DEUX RÈGLES, ET LEUR FRONTIÈRE :

  1. Un élément lu conserve le texte brut de son front matter (`raw_front`), et
     render() le reconduit TEL QUEL. Un aller-retour lecture/écriture ne change
     donc pas un octet — guillemets, ordre des clés, commentaires compris.

  2. Un élément dont un champ a changé (raw_front is None, cf. Item.with_fields)
     est resérialisé par un sérialiseur BORNÉ aux seuls types du contrat. Un type
     non couvert est une erreur qui le nomme, jamais une écriture approximative.

POURQUOI CETTE FRONTIÈRE : tomllib lit mais n'écrit pas, et la stdlib n'a aucun
écrivain TOML. Sérialiser à la main est exactement le travail que ce chantier
supprime — on le réduit donc au strict nécessaire, et la règle 1 prime partout où
elle s'applique.
"""

from __future__ import annotations

import datetime
import re
import tomllib
from collections.abc import Iterator
from pathlib import Path
from typing import cast

from .types import Item, Result, fail, ok

DELIM = "+++"


# --------------------------------------------------------------------- lecture
def split_front(text: str, path: Path) -> Result[tuple[str, str]]:
    """Sépare le bloc de front matter du corps. Échec fermé sur délimiteur manquant."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != DELIM:
        return fail(f"{path}: front matter absent — la première ligne doit être « {DELIM} »")
    for n, line in enumerate(lines[1:], start=2):
        if line.strip() == DELIM:
            return ok(("\n".join(lines[1 : n - 1]), "\n".join(lines[n:])))
    return fail(f"{path}: front matter non fermé — « {DELIM} » manquant après la ligne 1")


FENCE = re.compile(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


def outside_fences(text: str) -> Iterator[tuple[str, bool]]:
    """Chaque ligne du texte, avec un drapeau : est-elle hors bloc de code ?

    SOURCE UNIQUE DE LA RÈGLE. `parse_sections` s'en sert pour ne pas découper sur
    un `## ` de bloc de code, et `ListStore.merge_text` pour ne pas le compter
    comme un élément. Les deux ont divergé une fois — le parsing avait appris les
    fences, le recomptage non — et le flux de revue échouait sur une preuve
    exécutée collée telle quelle, avec un diagnostic faux. Une règle, un endroit.

    Suivi au sens CommonMark : un bloc s'ouvre sur ``` ou ~~~ (au plus trois
    espaces d'indentation) et ne se ferme que sur le MÊME caractère, répété au
    moins autant de fois — ce qui laisse un bloc contenir une clôture plus courte.
    Une CLÔTURE NE PORTE JAMAIS D'INFO STRING : « ```python » à l'intérieur d'un
    bloc ouvert par « ``` » est du contenu, pas une fermeture. Et une info string
    de bloc à backticks ne peut pas contenir de backtick.
    """
    fence: str | None = None
    for line in text.splitlines():
        marker = FENCE.match(line)
        if marker is not None:
            found, info = marker.group("fence"), marker.group("info")
            if fence is None:
                if found[0] != "`" or "`" not in info:
                    fence = found
            elif found[0] == fence[0] and len(found) >= len(fence) and not info.strip():
                fence = None
                yield line, False
                continue
        yield line, fence is None


def parse_sections(body: str) -> dict[str, str]:
    """Les `## ` du corps, dans l'ordre. Ce qui précède le premier est ignoré.

    UN `## ` DANS UN BLOC DE CODE N'OUVRE PAS DE SECTION. C'est du contenu, pas
    une structure : une entrée qui colle la sortie réelle d'une commande — ce que
    toute preuve exécutée exige — y verrait sinon apparaître des sections
    fantômes, que `validate` refuserait comme « non déclarées au contrat ».
    """
    sections: dict[str, str] = {}
    title: str | None = None
    buffer: list[str] = []

    for line, libre in outside_fences(body):
        if libre and line.startswith("## "):
            if title is not None:
                sections[title] = "\n".join(buffer).strip("\n")
            title = line[3:].strip()
            buffer = []
        elif title is not None:
            buffer.append(line)

    if title is not None:
        sections[title] = "\n".join(buffer).strip("\n")
    return sections


def read_item(path: Path) -> Result[Item]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return fail(f"{path}: illisible — {exc.strerror}")

    parts = split_front(text, path)
    if not parts:
        return Result(parts.status, None, parts.message)
    raw_front, body = parts.unwrap()

    try:
        fields = tomllib.loads(raw_front)
    except tomllib.TOMLDecodeError as exc:
        return fail(f"{path}: front matter TOML invalide — {exc}")

    return ok(Item(path, fields, parse_sections(body), raw_front=raw_front))


# ---------------------------------------------------------------- sérialisation
class SerialiseError(Exception):
    """Un type que le sérialiseur borné ne couvre pas."""


# Les seules séquences d'échappement qu'une chaîne TOML « basic » admet en plus de
# \\ et \" — les autres caractères de contrôle n'ont aucune écriture légale sur une
# ligne, et l'écrivain refuse plutôt que d'en inventer une.
ESCAPES = {"\n": "\\n", "\r": "\\r", "\t": "\\t", "\b": "\\b", "\f": "\\f"}


def dump_value(value: object, key: str) -> str:
    """Une valeur TOML, pour les seuls types déclarables au contrat.

    TOUT CE QUI EST ÉCRIT DOIT SE RELIRE. N'échapper que `\\` et `"` laissait un
    saut de ligne fermer la chaîne au milieu : `migrate` écrivait alors un fichier
    que `tomllib` refuse, en rendant « 1 changement appliqué » et le code 0 — une
    donnée valide détruite par un succès annoncé. C'est le mode d'échec ouvert que
    ce paquet existe pour supprimer, et il n'a pas d'exception pour l'écriture.
    """
    if isinstance(value, str):
        out = value.replace("\\", "\\\\").replace('"', '\\"')
        for brut, echappe in ESCAPES.items():
            out = out.replace(brut, echappe)
        illegal = next((c for c in out if ord(c) < 0x20 or ord(c) == 0x7F), None)
        if illegal is not None:
            raise SerialiseError(
                f"champ « {key} » : caractère de contrôle U+{ord(illegal):04X} — "
                "aucune écriture TOML sur une ligne ne le porte"
            )
        return f'"{out}"'
    if isinstance(value, bool):  # avant int : bool EST un int en Python
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        seq = cast("list[object] | tuple[object, ...]", value)
        return "[" + ", ".join(dump_value(v, key) for v in seq) + "]"
    raise SerialiseError(
        f"champ « {key} » : type {type(value).__name__} hors contrat — "
        "attendus : texte, date, entier, booléen, liste"
    )


def dump_front(fields: dict[str, object]) -> str:
    return "\n".join(f"{k} = {dump_value(v, k)}" for k, v in fields.items())


def render_item(item: Item) -> str:
    """Le fichier tel qu'il sera écrit.

    raw_front présent → reconduit à l'octet près (règle 1).
    raw_front None    → resérialisé (règle 2).
    """
    front = item.raw_front if item.raw_front is not None else dump_front(dict(item.fields))
    corps = "\n\n".join(f"## {t}\n\n{p}" for t, p in item.sections.items())
    return f"{DELIM}\n{front}\n{DELIM}\n\n{corps}\n"


def write_item(item: Item) -> Result[Path]:
    try:
        text = item.render()
    except SerialiseError as exc:
        return fail(f"{item.path}: {exc}")
    try:
        item.path.parent.mkdir(parents=True, exist_ok=True)
        item.path.write_text(text, encoding="utf-8")
    except OSError as exc:
        return fail(f"{item.path}: écriture impossible — {exc.strerror}")
    return ok(item.path)
