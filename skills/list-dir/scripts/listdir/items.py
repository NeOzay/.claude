"""Lecture et écriture d'un élément : front matter TOML + sections Markdown.

UNE SEULE RÈGLE : écrire, c'est REPROJETER. Le texte brut du front matter lu
(`raw_front`) est le document sur lequel on repose les champs, et seuls ceux dont
la valeur a changé sont réécrits. Tout le reste — tableau mis en forme sur
plusieurs lignes, guillemets choisis, commentaire posé au-dessus d'un champ —
ressort tel qu'il a été écrit. Un aller-retour lecture/écriture ne change donc pas
un octet, et une réécriture qui ne portait pas sur un champ ne le touche pas non
plus.

IL Y AVAIT UNE FRONTIÈRE ICI, et elle coûtait cher : `raw_front is None`
déclenchait une resérialisation intégrale, si bien qu'un simple ajout de champ au
contrat aplatissait d'un coup tous les tableaux de tous les éléments. Le diff git
mélangeait alors la migration et un reformatage que personne n'avait demandé.

CE QUI L'A RENDUE INUTILE : tomlkit. L'ancienne justification — « tomllib lit mais
n'écrit pas, et la stdlib n'a aucun écrivain TOML » — tenait tant qu'écrire voulait
dire sérialiser à la main. Un parseur préservant supprime la prémisse.

DEUX ÉCRIVAINS COHABITENT, et ce n'est pas un oubli : `dump_front` (tomlkit)
n'écrit QUE le front matter des éléments, seul endroit où quelqu'un met en forme à
la main. `dump_value` reste borné à une ligne et sert les contrats et les semences
(`store.init_list`, `provenance`), qui sont recopiés à l'octet et n'ont donc rien à
préserver.
"""

from __future__ import annotations

import datetime
import re
import tomllib
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import cast

import tomlkit
from tomlkit.items import Item as TomlItem
from tomlkit.items import Key as TomlKey

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
    for line, libre, _ in _scan_fences(text):
        yield line, libre


def _scan_fences(text: str) -> Iterator[tuple[str, bool, str | None]]:
    """Le parcours réel : chaque ligne, son drapeau, et le bloc ENCORE OUVERT après elle.

    L'IMPLÉMENTATION EST ICI, ET NULLE PART AILLEURS. `outside_fences` en jette le
    troisième élément, `fence_ouverte` ne garde que lui : deux lecteurs, une seule
    définition de ce qu'est un bloc de code. Les recopier aurait reproduit la
    divergence que `outside_fences` existe précisément pour avoir supprimée.
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
                yield line, False, None
                continue
        yield line, fence is None, fence


def fence_ouverte(text: str) -> str | None:
    """Le marqueur du bloc de code resté ouvert en fin de texte, ou None.

    POURQUOI CETTE FONCTION EXISTE : un bloc jamais refermé avale tout `## `
    postérieur — c'est CommonMark, et l'aller-retour reste exact. Mais les deux
    diagnostics qui en découlaient étaient faux et ne nommaient jamais la fence :
    `validate` annonçait « section manquante » sur une section écrite sous les yeux
    du lecteur, et `merge` une perte qui n'existait pas. Le défaut se signale donc
    À SA SOURCE, à l'élément, avant que le document aggloméré n'ait à en juger.
    """
    ouverte: str | None = None
    for _line, _libre, fence in _scan_fences(text):
        ouverte = fence
    return ouverte


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
    """Une valeur TOML sur une ligne — DÉPRÉCIÉ, ne prend plus de nouvel appelant.

    Remplacé par `toml_value` partout où quelqu'un met en forme à la main. Il ne
    survit que pour les contrats et les semences (`store.init_list`, `provenance`),
    recopiés à l'octet et qui n'ont donc rien à préserver. Sa suppression est écrite :
    dette `deux-ecrivains-toml-coexistent`, road-map `supprimer-dump-value`.

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


def toml_value(value: object, key: str) -> object:
    """La valeur, en item tomlkit, pour les seuls types déclarables au contrat.

    LA GARDE DE TYPE RESTE À NOUS. tomlkit accepte un `dict` sans broncher et l'écrit
    en table `[x]` — un type hors contrat passerait donc silencieusement, et le
    fichier relu porterait une structure que rien dans le contrat ne décrit. C'est
    exactement le mode d'échec ouvert que `dump_value` avait été écrit pour fermer,
    et il ne se ferme pas tout seul en changeant d'écrivain.

    Un saut de ligne n'est plus une erreur : il devient une chaîne multiligne, que la
    lecture accepte déjà. Les autres caractères de contrôle, `\\x00` compris, sont
    échappés par tomlkit et se relisent à l'identique — vérifié avant d'écrire ceci.
    """
    if isinstance(value, str):
        return tomlkit.string(value, multiline="\n" in value)
    if isinstance(value, bool):  # avant int : bool EST un int en Python
        return value
    if isinstance(value, (int, datetime.date)):
        return value
    if isinstance(value, (list, tuple)):
        seq = cast("list[object] | tuple[object, ...]", value)
        # `Array.extend` est hérité de `list` sans paramètre de type : basedpyright le
        # rend « partially unknown ». Construire la liste puis la confier à
        # `tomlkit.item` dit le type sans changer le rendu.
        return tomlkit.item([toml_value(element, key) for element in seq])
    raise SerialiseError(
        f"champ « {key} » : type {type(value).__name__} hors contrat — "
        "attendus : texte, date, entier, booléen, liste"
    )


def dump_front(fields: Mapping[str, object], raw_front: str | None = None) -> str:
    """Le front matter écrit, en ne touchant QUE ce qui a changé.

    `raw_front` n'est pas un texte à recopier : c'est le document sur lequel on
    reprojette. Un champ dont la valeur n'a pas bougé n'est pas réécrit, donc garde
    sa mise en forme — tableau sur plusieurs lignes, guillemets choisis, commentaire
    posé au-dessus. C'est toute la raison d'être de tomlkit ici.

    SANS `raw_front`, le document est neuf : un élément créé de toutes pièces n'a
    aucune mise en forme à préserver, et sort donc canonique.

    LE SAUT DE LIGNE FINAL EST GARANTI AVANT DE PARSER, et ce n'est pas cosmétique.
    `split_front` rend le front matter par un `"\\n".join(…)`, donc sans retour final :
    le dernier item du document porte alors un `trail` vide. Invisible tant qu'il
    reste dernier — et dès qu'un réordonnancement le remonte, le champ suivant se
    colle à lui. `migrate` écrivait ainsi `id = "x"title = "y"` en annonçant
    « 1 changement appliqué » et en rendant 0 : une donnée valide détruite par un
    succès annoncé, exactement ce que ce paquet existe pour rendre impossible.
    """
    if raw_front is None:
        doc = tomlkit.document()
    else:
        doc = tomlkit.parse(raw_front if raw_front.endswith("\n") else raw_front + "\n")

    # LA QUEUE SE DÉTACHE AVANT TOUT AJOUT. Une clé neuve se pose en fin de document,
    # donc DERRIÈRE un commentaire final — et `_reordonne` la lui rattacherait alors
    # comme si ce commentaire avait toujours été sa légende, puis l'emporterait avec
    # elle au premier réordonnancement. C'est exactement ce que fait un `migrate` qui
    # ajoute un champ, et ce que la règle du commentaire orphelin interdit.
    queue = _detacher_queue(doc)

    for cle, valeur in fields.items():
        if cle not in doc or doc[cle] != valeur:
            doc[cle] = toml_value(valeur, cle)

    neuf = _reordonne(doc, fields)
    neuf.body.extend(queue)
    return tomlkit.dumps(neuf).strip("\n")


def _detacher_queue(doc: tomlkit.TOMLDocument) -> list[tuple[TomlKey | None, TomlItem]]:
    """Retire du document ce qui suit son dernier champ, et le rend.

    Ce qui traîne là ne précède aucune clé : sous la règle « un commentaire appartient
    au champ qu'il précède », personne ne le possède. Il est donc mis de côté, puis
    reposé en fin de document — là où il a été écrit.
    """
    corps = doc.body
    dernier = max((i for i, (cle, _) in enumerate(corps) if cle is not None), default=-1)
    queue = corps[dernier + 1 :]
    del corps[dernier + 1 :]
    return queue


def _reordonne(doc: tomlkit.TOMLDocument, ordre: Iterable[str]) -> tomlkit.TOMLDocument:
    """Le document réduit aux champs donnés, dans cet ordre — sans rien reformater.

    UN COMMENTAIRE APPARTIENT AU CHAMP QU'IL PRÉCÈDE, et voyage donc avec lui. C'est
    la seule règle décidable sur un front matter plat : un commentaire posé entre
    deux champs n'a sinon aucun propriétaire, et celui qui l'a écrit le voyait bien,
    lui, comme la légende de ce qui suit.

    D'OÙ LA SUPPRESSION PAR OMISSION : un champ absent de `ordre` n'est pas recopié,
    et son commentaire s'en va avec lui. `migrate --drop` laissait sinon derrière lui
    la légende d'un champ qui n'existe plus — un commentaire devenu faux, que plus
    rien ne rattache à quoi que ce soit.

    LA QUEUE A DÉJÀ ÉTÉ DÉTACHÉE par l'appelant (`_detacher_queue`, qui dit pourquoi) :
    tout ce qui reste ici se termine par un champ, et il n'y a pas de reliquat à
    reposer.

    Les blocs sont DÉPLACÉS, jamais reconstruits : c'est ce qui distingue « remettre
    dans l'ordre » de « réécrire », et ce qui laisse intacts les tableaux mis en
    forme à la main.
    """
    blocs: dict[str, list[tuple[TomlKey | None, TomlItem]]] = {}
    bloc: list[tuple[TomlKey | None, TomlItem]] = []
    for cle, item in doc.body:
        bloc.append((cle, item))
        if cle is not None:
            blocs[cle.key] = bloc
            bloc = []

    neuf = tomlkit.document()
    for nom in ordre:
        neuf.body.extend(blocs[nom])
    return neuf


def render_item(item: Item) -> str:
    """Le fichier tel qu'il sera écrit.

    Un seul chemin, sans condition : `dump_front` reprojette les champs sur le
    document d'origine quand il y en a un, et en construit un neuf sinon.
    """
    front = dump_front(item.fields, item.raw_front)
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
