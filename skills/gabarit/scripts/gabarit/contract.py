"""Le contrat d'un gabarit : ce qu'un fichier doit contenir, lu et jugé.

PORTÉE : ce module lit un contrat et vérifie qu'il est lui-même cohérent — un type
inconnu, un enum sans valeurs, une clé mal typée. Il ne juge aucun fichier : c'est le
travail de check.py.

ÉCHEC FERMÉ : un contrat incohérent rend un Result en échec nommant le fichier et la
cause.

RIEN N'EST PRIS SUR PAROLE. tomllib rend des objets quelconques : un contrat où
`sections` est une chaîne, ou `description` un entier, est un contrat qu'on écrit à
la main et qu'on peut donc écrire de travers. Chaque valeur lue passe par `table`,
`texte` ou `liste`, qui rendent un échec nommé plutôt que de laisser un AttributeError
remonter nu trois appels plus loin.

LES MORCEAUX SONT PUBLICS, et c'est pour `listdir` : le contrat d'une liste est celui
d'un gabarit, plus un `from` par champ, une table `[origin]` et le refus d'un ancien
format. Il se compose donc avec `entete`, `declared_fields` et `declared_sections`, dans
l'ordre où ces contrôles ont toujours été joués — c'est cet ordre qui décide du message
rendu sur un contrat fautif à plusieurs endroits.
"""

from __future__ import annotations

import datetime
import tomllib
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import cast

from .motif import Trou, decoupe, trous
from .types import (
    ALL_MARKERS,
    DEBUT,
    FIELD_TYPES,
    FIN,
    FIN_LIGNE,
    FORMES,
    RANG_MAX,
    RANG_SECTION,
    SECTION_TYPES,
    TYPED_MARKER_TYPES,
    Capture,
    Contract,
    Field,
    Result,
    Section,
    accepted_markers,
    fail,
    ok,
)

CONTRACT = "contract.toml"
"""Le nom du fichier de contrat dans une semence."""

_SANS_GUILLEMETS = ", ".join(t for t in FIELD_TYPES if t in TYPED_MARKER_TYPES)
_AVEC_GUILLEMETS = ", ".join(t for t in FIELD_TYPES if t not in TYPED_MARKER_TYPES)

REGLE_GUILLEMETS = (
    f"Règle des guillemets : seuls les champs {_AVEC_GUILLEMETS} gardent les leurs. "
    f"Un champ {_SANS_GUILLEMETS} s'écrit sans guillemets : en le remplissant, "
    'retirer ceux de son marqueur (reviewed = "<OPTIONNEL date>" devient '
    "reviewed = 2026-10-07)."
)
"""Ce que `contract` dit sur stderr : où poser des guillemets. DÉRIVÉE de
`TYPED_MARKER_TYPES`, jamais recopiée — c'est la règle qui décide quels types ont un
marqueur typé, et la dire autrement ailleurs la ferait diverger."""

type Extra = Callable[[str, dict[str, object]], Result[dict[str, object]]]
"""Un contrôle propre à l'appelant sur la table d'un champ : rend les arguments en plus
à passer au constructeur. Joué après la description et avant le préremplissage."""


# ------------------------------------------------------------ lecture prudente
def table(value: object, path: Path, subject: str) -> Result[dict[str, object]]:
    """La valeur si c'est une table TOML, un échec nommé sinon."""
    if value is None:
        return ok({})
    if not isinstance(value, dict):
        return fail(f"{path}: {subject} — une table est attendue, trouvé {type(value).__name__}")
    # cast, et non isinstance : `isinstance(x, dict)` ne dit rien des clés ni des
    # valeurs. Les clés sont ramenées à des chaînes, les valeurs restent quelconques —
    # c'est à l'appelant de dire ce qu'il attend de chacune.
    return ok({str(k): v for k, v in cast("dict[object, object]", value).items()})


def texte(value: object, path: Path, subject: str, default: str = "") -> Result[str]:
    """La valeur si c'est une chaîne, le défaut si elle est absente, un échec sinon."""
    if value is None:
        return ok(default)
    if not isinstance(value, str):
        return fail(f"{path}: {subject} — une chaîne est attendue, trouvé {type(value).__name__}")
    return ok(value)


def liste(value: object, path: Path, subject: str) -> Result[list[str]]:
    """La valeur si c'est une liste de chaînes, un échec nommé sinon."""
    if value is None:
        return ok([])
    if not isinstance(value, list):
        return fail(f"{path}: {subject} — une liste est attendue, trouvé {type(value).__name__}")
    out: list[str] = []
    for entry in cast("list[object]", value):
        if not isinstance(entry, str):
            return fail(
                f"{path}: {subject} — une liste de chaînes est attendue, "
                f"trouvé {type(entry).__name__}"
            )
        out.append(entry)
    return ok(out)


def _prefill(
    body: dict[str, object], path: Path, subject: str, *, list_type: bool = False
) -> Result[tuple[str | None, str | None]]:
    """`text` et `command` d'un champ ou d'une section, validés ensemble.

    Rendent `None` quand la clé est absente — à distinguer d'une chaîne vide,
    refusée : elle ne préremplirait rien. Les deux ne peuvent être déclarées
    ensemble ; sur un champ de type `list`, ni l'une ni l'autre n'a de sens, la
    valeur produite étant toujours du texte que `check_value` rejetterait.
    """
    text_val = body.get("text")
    if text_val is not None and not isinstance(text_val, str):
        return fail(
            f"{path}: {subject}, « text » — une chaîne est attendue, "
            f"trouvé {type(text_val).__name__}"
        )
    command_val = body.get("command")
    if command_val is not None and not isinstance(command_val, str):
        return fail(
            f"{path}: {subject}, « command » — une chaîne est attendue, "
            f"trouvé {type(command_val).__name__}"
        )

    if text_val is not None and command_val is not None:
        return fail(
            f"{path}: {subject} — « text » et « command » ne peuvent être déclarés ensemble"
        )
    if text_val == "":
        return fail(f"{path}: {subject}, « text » — une valeur vide ne préremplit rien")
    if command_val == "":
        return fail(f"{path}: {subject}, « command » — une valeur vide ne préremplit rien")
    if list_type and (text_val is not None or command_val is not None):
        return fail(
            f"{path}: {subject} — « text »/« command » refusés sur un champ de type « list » : "
            "la valeur produite est toujours du texte"
        )
    return ok((text_val, command_val))


def _deprecated(
    body: dict[str, object],
    path: Path,
    subject: str,
    *,
    required: bool,
    text: str | None,
    command: str | None,
) -> Result[str | None]:
    """La consigne de `deprecated`, ou None si la clé est absente.

    UNE CHAÎNE NON VIDE : la consigne est ce que `validate` redira à qui porte encore le
    champ, et une valeur vide ne dirait rien. Refusée avec `required`, `text` ou `command` :
    un champ qu'on ne pose plus ne se préremplit pas et ne se réclame pas. Le contrat
    contradictoire est NOMMÉ, jamais corrigé en silence.
    """
    valeur = body.get("deprecated")
    if valeur is None:
        return ok(None)
    if not isinstance(valeur, str):
        return fail(
            f"{path}: {subject}, « deprecated » — une chaîne est attendue, "
            f"trouvé {type(valeur).__name__}"
        )
    if not valeur.strip():
        return fail(f"{path}: {subject}, « deprecated » — la consigne ne peut être vide")
    contradictoires = [
        nom
        for nom, present in (
            ("required", required),
            ("text", text is not None),
            ("command", command is not None),
        )
        if present
    ]
    if contradictoires:
        return fail(
            f"{path}: {subject} — « deprecated » contredit « {contradictoires[0]} » : "
            "ce qu'on ne pose plus ne se préremplit pas et ne se réclame pas"
        )
    return ok(valeur)


# ------------------------------------------------------------------ morceaux
def entete(raw: dict[str, object], path: Path, anonyme: str) -> Result[tuple[str, str]]:
    """Le `name` et la `description` d'un contrat. `anonyme` dit pourquoi un nom est dû.

    LA CLÉ `description` EST EXIGÉE, PAS SON TEXTE — ici, sur chaque champ et sur
    chaque section. `description = ""` reste donc accepté partout. Ce qui est visé est
    le contrat à moitié documenté : sans ce test, `texte` rend `""` pour une clé
    absente, et rien ne distingue plus « pas de texte » de « pas documenté ». Le
    contrôle de `name` reste avant celui-ci : un contrat anonyme s'annonce comme tel
    d'abord.
    """
    nom = texte(raw.get("name"), path, "« name »")
    if not nom:
        return fail(nom.message)
    if not nom.unwrap():
        return fail(f"{path}: champ « name » manquant — {anonyme}")

    if "description" not in raw:
        return fail(f"{path}: « description » manquante — la clé se déclare, fût-elle vide")
    description = texte(raw.get("description"), path, "« description »")
    if not description:
        return fail(description.message)
    return ok((nom.unwrap(), description.unwrap()))


def parse_field[F: Field](
    name: str, value: object, path: Path, make: Callable[..., F], extra: Extra | None = None
) -> Result[F]:
    """Un champ déclaré, construit par `make` — `Field` ou ce qu'un appelant en dérive."""
    decl = table(value, path, f"champ « {name} »")
    if not decl:
        return fail(decl.message)
    body = decl.unwrap()

    ftype = body.get("type")
    if ftype not in FIELD_TYPES:
        return fail(
            f"{path}: champ « {name} » — type « {ftype} » inconnu ; "
            f"attendus : {', '.join(FIELD_TYPES)}"
        )

    values = liste(body.get("values"), path, f"champ « {name} », « values »")
    if not values:
        return fail(values.message)
    if ftype == "enum" and not values.unwrap():
        return fail(f"{path}: champ « {name} » — un enum sans `values` n'admet rien")

    # UNE VALEUR EST UN JETON, PAS UNE PHRASE. Une valeur portant une espace se
    # découpait en deux pseudo-valeurs dès qu'un appelant itérait dessus — une boucle
    # shell sur les valeurs d'un enum en est un, et elle comptait alors deux
    # catégories fantômes à zéro sans qu'aucune commande n'échoue. La vide est refusée
    # pour la même raison : elle traverse une substitution sans laisser de trace.
    for v in values.unwrap():
        if not v or v.split() != [v]:
            return fail(
                f"{path}: champ « {name} », « values » — une valeur ne peut être vide "
                f"ni contenir d'espace, trouvé « {v} »"
            )

    if "description" not in body:
        return fail(f"{path}: champ « {name} » — « description » manquante")
    description = texte(body.get("description"), path, f"champ « {name} », « description »")
    if not description:
        return fail(description.message)

    extras: dict[str, object] = {}
    if extra is not None:
        en_plus = extra(name, body)
        if not en_plus:
            return fail(en_plus.message)
        extras = en_plus.unwrap()

    prefill = _prefill(body, path, f"champ « {name} »", list_type=ftype == "list")
    if not prefill:
        return fail(prefill.message)
    text_val, command_val = prefill.unwrap()

    required = bool(body.get("required", False))
    deprecated = _deprecated(
        body, path, f"champ « {name} »", required=required, text=text_val, command=command_val
    )
    if not deprecated:
        return fail(deprecated.message)

    return ok(
        make(
            name=name,
            type=ftype,
            required=required,
            description=description.unwrap(),
            values=values.unwrap(),
            text=text_val,
            command=command_val,
            deprecated=deprecated.unwrap(),
            **extras,
        )
    )


def declared_fields[F: Field](
    value: object, path: Path, make: Callable[..., F], extra: Extra | None = None
) -> Result[dict[str, F]]:
    """La table `[fields]` d'un contrat, champ par champ, dans l'ordre du fichier."""
    declared = table(value, path, "« fields »")
    if not declared:
        return fail(declared.message)
    fields: dict[str, F] = {}
    for name, body in declared.unwrap().items():
        f = parse_field(name, body, path, make, extra)
        if not f:
            return fail(f.message)
        fields[name] = f.unwrap()
    return ok(fields)


_CLES_MOTIF = ("motif", "debut", "fin", "captures")
"""Les clés qu'une section ne porte que si elle est de type « motif »."""

_CLES_LABEL = ("forme", "labels", "prefix")
"""Les clés qu'une section ne porte que si elle est de type « label »."""

_CLES_CAPTURE = ("description", "required", "values", "min", "max", "sequence")
"""Les seules clés d'une capture. Son type se déclare dans le motif, et nulle part ailleurs."""


def parse_section(title: str, value: object, path: Path) -> Result[Section]:
    """Une section déclarée, ses labels compris."""
    return _section(title, value, path, f"section « {title} »", rang=RANG_SECTION + 1, label=False)


def _section(
    name: str, value: object, path: Path, sujet: str, *, rang: int, label: bool
) -> Result[Section]:
    """Une section ou un label, nommé dans les messages par `sujet` — son chemin.

    `rang` est celui que prendraient ses propres labels s'ils étaient des titres : 3 sous
    une section, un de plus à chaque label `title` qui en porte d'autres.
    """
    decl = table(value, path, sujet)
    if not decl:
        return fail(decl.message)
    body = decl.unwrap()

    if "description" not in body:
        return fail(f"{path}: {sujet} — « description » manquante")
    description = texte(body.get("description"), path, f"{sujet}, « description »")
    if not description:
        return fail(description.message)

    prefill = _prefill(body, path, sujet)
    if not prefill:
        return fail(prefill.message)
    text_val, command_val = prefill.unwrap()

    required = bool(body.get("required", False))
    deprecated = _deprecated(
        body, path, sujet, required=required, text=text_val, command=command_val
    )
    if not deprecated:
        return fail(deprecated.message)

    if "order" in body and not label:
        return fail(f"{path}: {sujet} — « order » réservé à un label")
    order = _entier(body.get("order"), path, f"{sujet}, « order »")
    if not order:
        return fail(order.message)

    section = Section(
        name=name,
        required=required,
        description=description.unwrap(),
        text=text_val,
        command=command_val,
        deprecated=deprecated.unwrap(),
        order=order.unwrap(),
    )

    # SANS `type`, LE CHEMIN D'AVANT, À L'IDENTIQUE — une clé de structure y est refusée
    # plutôt qu'ignorée : un `motif` sans `type` ne vérifierait rien, en silence.
    type_ = body.get("type")
    if type_ is not None and type_ not in SECTION_TYPES:
        return fail(
            f"{path}: {sujet} — type « {type_} » inconnu ; attendus : {', '.join(SECTION_TYPES)}"
        )
    for reserve, cles in (("motif", _CLES_MOTIF), ("label", _CLES_LABEL)):
        etrangeres = [cle for cle in cles if cle in body]
        if type_ != reserve and etrangeres:
            # Pour un label, c'est le refus de DEUX FORMES À UN NIVEAU : la forme se déclare
            # sur la table qui porte les labels, et un label qui en déclare une sans en
            # porter lui-même en imposerait une seconde à ses voisins.
            return fail(
                f"{path}: {sujet} — « {etrangeres[0]} » réservé à une section "
                f'de `type = "{reserve}"`'
            )
    if type_ is None:
        return ok(section)
    if type_ == "motif":
        return _motif(section, body, path, sujet)
    return _labels(section, body, path, sujet, rang)


def _labels(
    section: Section, body: dict[str, object], path: Path, sujet: str, rang: int
) -> Result[Section]:
    """La section, complétée de sa forme, de son préfixe et de ses labels, lus récursivement."""
    forme = body.get("forme")
    if forme is None:
        return fail(f"{path}: {sujet} — « forme » manquante ; attendues : {', '.join(FORMES)}")
    if forme not in FORMES:
        return fail(
            f"{path}: {sujet} — forme « {forme} » inconnue ; attendues : {', '.join(FORMES)}"
        )
    if forme == "title" and rang > RANG_MAX:
        return fail(
            f"{path}: {sujet} — des labels « title » y seraient de rang {rang}, "
            f"au-delà de {RANG_MAX}"
        )

    prefix = texte(body.get("prefix"), path, f"{sujet}, « prefix »")
    if not prefix:
        return fail(prefix.message)
    if "prefix" in body and not prefix.unwrap().strip():
        return fail(f"{path}: {sujet} — « prefix » vide : il dit ce que la prose admise contient")

    tables = table(body.get("labels"), path, f"{sujet}, « labels »")
    if not tables:
        return fail(tables.message)
    if not tables.unwrap():
        return fail(f"{path}: {sujet} — aucun label déclaré sous « labels »")

    labels: dict[str, Section] = {}
    precedent: tuple[str, int] | None = None  # le dernier label à porter un `order`
    for nom, corps in tables.unwrap().items():
        lu = _section(nom, corps, path, f"{sujet}, label « {nom} »", rang=rang + 1, label=True)
        if not lu:
            return fail(lu.message)
        label = lu.unwrap()
        if forme == "bold" and label.type == "label":
            return fail(
                f"{path}: {sujet}, label « {nom} » — un label « bold » ne porte pas de labels"
            )
        # L'ORDRE DÉCLARÉ EST L'ORDRE DE POSE : le squelette se pose dans l'ordre de
        # déclaration, et doit passer `check`. Un `order` qui ne croît pas le ferait échouer.
        if label.order is not None:
            if precedent is not None and label.order <= precedent[1]:
                return fail(
                    f"{path}: {sujet}, label « {nom} » — « order » {label.order} ne croît "
                    f"pas après celui de « {precedent[0]} » ({precedent[1]}) : les "
                    "labels se déclarent dans leur ordre"
                )
            precedent = (nom, label.order)
        labels[nom] = label

    return ok(
        replace(
            section,
            type="label",
            forme="bold" if forme == "bold" else "title",
            labels=labels,
            prefix=prefix.unwrap() if "prefix" in body else None,
        )
    )


def _motif(section: Section, body: dict[str, object], path: Path, sujet: str) -> Result[Section]:
    """La section, complétée de son motif, de ses bornes et de ses captures."""
    motif = texte(body.get("motif"), path, f"{sujet}, « motif »")
    if not motif:
        return fail(motif.message)
    if not motif.unwrap().strip():
        return fail(
            f"{path}: {sujet} — « motif » manquant ou vide : une section à motif le déclare"
        )

    # UNE BORNE EST UN JETON : la puce s'ouvre sur `debut` suivi d'un blanc, et un blanc
    # dans la borne rendrait ce découpage ambigu. Seule `fin` peut valoir le saut de ligne.
    bornes: list[str] = []
    for cle, defaut in (("debut", DEBUT), ("fin", FIN)):
        borne = texte(body.get(cle), path, f"{sujet}, « {cle} »", default=defaut)
        if not borne:
            return fail(borne.message)
        if cle == "fin" and borne.unwrap() == FIN_LIGNE:
            bornes.append(FIN_LIGNE)
            continue
        if borne.unwrap().split() != [borne.unwrap()]:
            return fail(
                f"{path}: {sujet}, « {cle} » — ni vide ni blanc, trouvé « {borne.unwrap()} »"
            )
        bornes.append(borne.unwrap())

    morceaux = decoupe(motif.unwrap())
    if not morceaux:
        return fail(f"{path}: {sujet}, « motif » — {morceaux.message}")

    declarees = table(body.get("captures"), path, f"{sujet}, « captures »")
    if not declarees:
        return fail(declarees.message)
    tables = declarees.unwrap()
    attendus = trous(morceaux.unwrap())
    noms = {t.nom for t in attendus}
    for nom in tables:
        if nom not in noms:
            return fail(f"{path}: {sujet}, capture « {nom} » — déclarée mais absente du motif")

    # UNE CAPTURE SIMPLE NE SE DÉCLARE PAS : sans table, elle est requise, sans contrainte,
    # et prend la description de sa section ou de son label. Une `enum` sans table reste
    # refusée, faute de `values`.
    captures: dict[str, Capture] = {}
    for t in attendus:
        capture = parse_capture(sujet, t, tables.get(t.nom), path, repli=section.description)
        if not capture:
            return fail(capture.message)
        captures[t.nom] = capture.unwrap()

    debut, fin = bornes
    return ok(
        replace(
            section, type="motif", motif=motif.unwrap(), debut=debut, fin=fin, captures=captures
        )
    )


def _entier(value: object, path: Path, subject: str) -> Result[int | None]:
    """La valeur si c'est un entier — un booléen n'en est pas un —, None si elle est absente."""
    if value is None:
        return ok(None)
    if isinstance(value, bool) or not isinstance(value, int):
        return fail(f"{path}: {subject} — un entier est attendu, trouvé {type(value).__name__}")
    return ok(value)


def parse_capture(
    section: str, trou: Trou, value: object, path: Path, *, repli: str = ""
) -> Result[Capture]:
    """Une capture déclarée par `[….captures.<nom>]`, du type que le motif lui donne.
    `section` est le chemin de la section ou du label qui la porte, pour les messages ;
    `repli`, sa description, que prend une capture qui n'en déclare pas — table absente,
    clé absente ou blanche.

    L'ESPACE EST ADMISE DANS SES `values`, et là seulement : « [ ] » doit pouvoir valoir
    `" "`. Les `values` d'un champ restent des jetons — `parse_field` n'est pas touchée.
    La vide reste refusée : elle ne se distinguerait d'aucune absence.
    """
    sujet = f"{section}, capture « {trou.nom} »"
    decl = table(value, path, sujet)
    if not decl:
        return fail(decl.message)
    body = decl.unwrap()

    refusees = sorted(set(body) - set(_CLES_CAPTURE))
    if refusees:
        return fail(
            f"{path}: {sujet} — clé « {refusees[0]} » refusée : le type se déclare dans le "
            f"motif, et une capture n'admet que {', '.join(_CLES_CAPTURE)}"
        )

    description = texte(body.get("description"), path, f"{sujet}, « description »")
    if not description:
        return fail(description.message)

    required = body.get("required", True)
    if not isinstance(required, bool):
        return fail(
            f"{path}: {sujet}, « required » — un booléen est attendu, "
            f"trouvé {type(required).__name__}"
        )

    values = liste(body.get("values"), path, f"{sujet}, « values »")
    if not values:
        return fail(values.message)
    if trou.type == "enum" and not values.unwrap():
        return fail(f"{path}: {sujet} — un enum sans `values` n'admet rien")
    if trou.type != "enum" and "values" in body:
        return fail(f"{path}: {sujet} — « values » réservé à une capture enum")
    if "" in values.unwrap():
        return fail(f"{path}: {sujet}, « values » — une valeur ne peut être vide")

    if trou.type != "int":
        hors_type = [cle for cle in ("min", "max", "sequence") if cle in body]
        if hors_type:
            return fail(f"{path}: {sujet} — « {hors_type[0]} » réservé à une capture int")
    bornes: list[int | None] = []
    for cle in ("min", "max"):
        borne = _entier(body.get(cle), path, f"{sujet}, « {cle} »")
        if not borne:
            return fail(borne.message)
        bornes.append(borne.unwrap())
    minimum, maximum = bornes
    if minimum is not None and maximum is not None and minimum > maximum:
        return fail(f"{path}: {sujet} — « min » ({minimum}) dépasse « max » ({maximum})")
    sequence = body.get("sequence", False)
    if not isinstance(sequence, bool):
        return fail(
            f"{path}: {sujet}, « sequence » — un booléen est attendu, "
            f"trouvé {type(sequence).__name__}"
        )

    return ok(
        Capture(
            name=trou.nom,
            type=trou.type,
            required=required,
            description=description.unwrap() if description.unwrap().strip() else repli,
            values=values.unwrap(),
            min=minimum,
            max=maximum,
            sequence=sequence,
        )
    )


def declared_sections(raw_sections: dict[str, object], path: Path) -> Result[dict[str, Section]]:
    """Les sections d'une table `[sections]` déjà lue, dans l'ordre du fichier — c'est
    cet ordre qui ordonne les sections d'un fichier créé."""
    sections: dict[str, Section] = {}
    for title, body in raw_sections.items():
        s = parse_section(title, body, path)
        if not s:
            return fail(s.message)
        sections[title] = s.unwrap()
    return ok(sections)


# ------------------------------------------------------------------- contrat
def parse_contract(text: str, path: Path) -> Result[Contract]:
    """Le contrat d'un gabarit, depuis son texte. `path` ne sert qu'aux messages."""
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return fail(f"{path}: TOML invalide — {exc}")

    tete = entete(raw, path, "un gabarit se nomme")
    if not tete:
        return fail(tete.message)
    name, description = tete.unwrap()

    fields = declared_fields(raw.get("fields"), path, Field)
    if not fields:
        return fail(fields.message)

    raw_sections = table(raw.get("sections"), path, "« sections »")
    if not raw_sections:
        return fail(raw_sections.message)
    sections = declared_sections(raw_sections.unwrap(), path)
    if not sections:
        return fail(sections.message)

    return ok(
        Contract(
            name=name,
            description=description,
            fields=fields.unwrap(),
            sections=sections.unwrap(),
        )
    )


def field_values(contrat: Contract, champ: str, chemin: Path) -> Result[list[str]]:
    """Les `values` déclarées d'un champ, DANS L'ORDRE DU FICHIER.

    L'ORDRE EST UNE DONNÉE, PAS UN DÉTAIL DE PRÉSENTATION. Un contrat peut ranger
    ses valeurs par ce qu'elles signifient plutôt que par l'alphabet ; les trier ici
    détruirait exactement ce qu'une prose venait chercher en s'y référant. Rien
    n'est trié, filtré ni jugé.

    DEUX ÉCHECS NOMMÉS, et aucune liste vide sous un succès. Un champ mal
    orthographié ou sans `values` rendrait zéro élément, et une boucle appelante
    tournerait à vide en réussissant — précisément l'échec ouvert que ce paquet
    existe pour supprimer.
    """
    field = contrat.fields.get(champ)
    if field is None:
        connus = ", ".join(contrat.fields) or "aucun"
        return fail(f"{chemin}: champ « {champ} » non déclaré ; déclarés : {connus}")
    if not field.values:
        return fail(
            f"{chemin}: champ « {champ} » — aucune `values` déclarée (type « {field.type} »)"
        )
    return ok(field.values)


# ------------------------------------------------- confrontation d'une valeur au contrat
def is_marker(value: object) -> bool:
    """Vrai si la valeur est un marqueur — générique ou typé —, et rien d'autre.

    Ni la chaîne vide, ni un tiret, ni None : un champ ABSENT et un champ À REMPLIR
    sont deux états différents, et les confondre ferait passer un oubli pour une
    intention. Le `isinstance` précède le test d'appartenance : une valeur non hachable
    (une liste lue d'un front matter) le ferait lever.
    """
    return isinstance(value, str) and value in ALL_MARKERS


def _lisible(valeur: str) -> str:
    """La valeur telle qu'elle se lit dans une liste séparée par des virgules."""
    # Une valeur vide ou bordée de blanc S'Y PERDRAIT sans guillemets : « x,  » cache « " " ».
    return f'"{valeur}"' if not valeur or valeur != valeur.strip() else valeur


def check_value(field: Field, value: object) -> str:
    """La raison du manquement, ou une chaîne vide si la valeur convient.

    LE CONTRÔLE DE TYPE EST SUSPENDU SUR UN MARQUEUR : `date = "<À REMPLIR>"` doit
    être signalé comme *à remplir*, jamais comme *type invalide*. Un message qui
    parle de type devant un marqueur dit au lecteur de corriger ce qui va bien.

    SEUL LE MARQUEUR D'UN AUTRE TYPE EST UN MANQUEMENT : `<OPTIONNEL int>` sur un champ
    `date` ne dit pas quelle valeur écrire, et le laisser passer cacherait un contrat
    ou un fichier mal posé. Le marqueur générique reste accepté : c'est l'ancienne forme.
    """
    if is_marker(value):
        if value in accepted_markers(field.type):
            return ""
        return f"« {value} » est le marqueur d'un autre type que « {field.type} »"

    match field.type:
        case "slug":
            if not isinstance(value, str) or not value.strip():
                return "un identifiant non vide est attendu"
            if value != value.strip() or " " in value:
                return f"« {value} » n'est pas un slug — ni espace ni bord blanc"
        case "text":
            if not isinstance(value, str):
                return f"du texte est attendu, trouvé {type(value).__name__}"
            if not value.strip():
                return "vide — un champ se remplit ou porte son marqueur"
        case "date":
            if isinstance(value, datetime.date):
                return ""
            if not isinstance(value, str):
                return f"une date est attendue, trouvé {type(value).__name__}"
            try:
                _ = datetime.date.fromisoformat(value)
            except ValueError:
                return f"« {value} » n'est pas une date ISO (AAAA-MM-JJ)"
        case "enum":
            if not isinstance(value, str) or value not in field.values:
                declarees = ", ".join(_lisible(v) for v in field.values)
                return f"« {value} » hors des valeurs déclarées : {declarees}"
        case "int":
            # `isinstance(True, int)` est vrai en Python : sans ce refus, `true` passerait
            # pour l'entier 1.
            if isinstance(value, bool) or not isinstance(value, int):
                return f"un entier est attendu, trouvé {type(value).__name__}"
        case "bool":
            if not isinstance(value, bool):
                return f"un booléen est attendu, trouvé {type(value).__name__}"
        case "list":
            if not isinstance(value, list):
                return f"une liste est attendue, trouvé {type(value).__name__}"
            for entry in cast("list[object]", value):
                if not isinstance(entry, str):
                    return f"une liste de chaînes est attendue, trouvé {type(entry).__name__}"
    return ""
