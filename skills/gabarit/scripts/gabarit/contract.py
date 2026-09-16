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
from pathlib import Path
from typing import cast

from .types import FIELD_TYPES, OPTIONAL, PLACEHOLDER, Contract, Field, Result, Section, fail, ok

CONTRACT = "contract.toml"
"""Le nom du fichier de contrat dans une semence."""

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

    return ok(
        make(
            name=name,
            type=ftype,
            required=bool(body.get("required", False)),
            description=description.unwrap(),
            values=values.unwrap(),
            text=text_val,
            command=command_val,
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


def parse_section(title: str, value: object, path: Path) -> Result[Section]:
    """Une section déclarée."""
    decl = table(value, path, f"section « {title} »")
    if not decl:
        return fail(decl.message)
    body = decl.unwrap()

    if "description" not in body:
        return fail(f"{path}: section « {title} » — « description » manquante")
    description = texte(body.get("description"), path, f"section « {title} », « description »")
    if not description:
        return fail(description.message)

    prefill = _prefill(body, path, f"section « {title} »")
    if not prefill:
        return fail(prefill.message)
    text_val, command_val = prefill.unwrap()

    return ok(
        Section(
            name=title,
            required=bool(body.get("required", False)),
            description=description.unwrap(),
            text=text_val,
            command=command_val,
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
    """Vrai si la valeur est l'un des deux marqueurs, et rien d'autre.

    Ni la chaîne vide, ni un tiret, ni None : un champ ABSENT et un champ À REMPLIR
    sont deux états différents, et les confondre ferait passer un oubli pour une
    intention.
    """
    return value in (PLACEHOLDER, OPTIONAL)


def check_value(field: Field, value: object) -> str:
    """La raison du manquement, ou une chaîne vide si la valeur convient.

    LE CONTRÔLE DE TYPE EST SUSPENDU SUR UN MARQUEUR : `date = "<À REMPLIR>"` doit
    être signalé comme *à remplir*, jamais comme *type invalide*. Un message qui
    parle de type devant un marqueur dit au lecteur de corriger ce qui va bien.
    """
    if is_marker(value):
        return ""

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
                return f"« {value} » hors des valeurs déclarées : {', '.join(field.values)}"
        case "int":
            # `isinstance(True, int)` est vrai en Python : sans ce refus, `true` passerait
            # pour l'entier 1.
            if isinstance(value, bool) or not isinstance(value, int):
                return f"un entier est attendu, trouvé {type(value).__name__}"
        case "list":
            if not isinstance(value, list):
                return f"une liste est attendue, trouvé {type(value).__name__}"
            for entry in cast("list[object]", value):
                if not isinstance(entry, str):
                    return f"une liste de chaînes est attendue, trouvé {type(entry).__name__}"
    return ""
