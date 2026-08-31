"""Chargement et validation du contrat d'une liste : .list/contract.toml.

PORTÉE : ce module lit le contrat et vérifie qu'il est lui-même cohérent — un type
inconnu, un enum sans valeurs, une section déclarée deux fois. Il ne juge aucun
élément : c'est le travail de validate.

ÉCHEC FERMÉ : un contrat absent ou incohérent rend un Result en échec nommant le
fichier et la cause. Une liste sans contrat n'est pas une liste.

RIEN N'EST PRIS SUR PAROLE. tomllib rend des objets quelconques : un contrat où
`sections` est une chaîne, ou `description` un entier, est un contrat qu'on écrit à
la main et qu'on peut donc écrire de travers. Chaque valeur lue passe par _table,
_texte ou _liste, qui rendent un échec nommé plutôt que de laisser un AttributeError
remonter nu trois appels plus loin.
"""

from __future__ import annotations

import datetime
import tomllib
from pathlib import Path
from typing import cast

from .types import FIELD_TYPES, OPTIONAL, PLACEHOLDER, Contract, Field, Result, Section, fail, ok

LIST_DIR = ".list"
CONTRACT = "contract.toml"
TEMPLATES = "templates"
"""Les paires <nom>.toml / <nom>.md que `derive` projette, sous .list/."""


def contract_path(list_dir: Path) -> Path:
    return list_base(list_dir) / CONTRACT


def list_base(list_dir: Path) -> Path:
    """Le répertoire d'une liste qui porte `contract.toml` et `templates/`.

    L'ÉQUIVALENT POUR UNE DÉFINITION EST LA DÉFINITION ELLE-MÊME. C'est toute la
    différence entre les deux, et la seule : une fois la base obtenue, plus rien ne
    distingue une liste d'une semence, et rien ne peut donc les traiter
    différemment par mégarde.
    """
    return list_dir / LIST_DIR


def source_path(base: Path, template: str = "") -> Result[Path]:
    """Le fichier de contrat d'une base : le sien, ou celui d'un de ses gabarits.

    LE NOM DE GABARIT EST UN NOM, PAS UN CHEMIN. `--template ../contract` sortirait
    sinon de `templates/` — sans danger pour une lecture, mais l'aide annonce « le
    `<nom>.toml` de `templates/` », et une commande qui rend autre chose que ce
    qu'elle annonce est un échec ouvert de plus.

    L'ABSENCE EST DITE AVEC LE CHEMIN COMPLET, et non avec le nom de la cible : une
    définition mal orthographiée, une liste sans `.list/` et un gabarit inexistant
    se distinguent alors d'un coup d'œil, sans avoir à reconstruire le chemin de
    tête.
    """
    if not template:
        f = base / CONTRACT
        return ok(f) if f.is_file() else fail(f"{f}: contrat introuvable")

    if template != Path(template).name or template in (".", ".."):
        return fail(
            f"gabarit « {template} » — un nom est attendu, pas un chemin : "
            f"le fichier est cherché dans {TEMPLATES}/"
        )
    f = base / TEMPLATES / f"{template}.toml"
    if not f.is_file():
        return fail(f"{f}: gabarit « {template} » introuvable — ce fichier manque")
    return ok(f)


def load_source(base: Path, template: str = "") -> Result[tuple[Path, str, Contract]]:
    """Le fichier de contrat d'une base, son texte BRUT, et le contrat qu'il déclare.

    LE TEXTE EST RENDU TEL QUEL, commentaires compris : ils portent souvent le
    pourquoi d'un champ, et un contrat reformaté par un aller-retour de parseur
    perdrait justement ce que le lecteur venait chercher. Le contrat est pourtant
    JUGÉ AVANT D'ÊTRE RENDU — rendre un contrat cassé sous un code de succès ferait
    croire à l'appelant qu'il tient la règle en vigueur alors qu'aucune commande ne
    peut l'appliquer.

    LES TROIS SORTENT ENSEMBLE parce qu'il a fallu les trois pour conclure : rendre
    le seul texte obligerait l'appelant qui veut le contrat à reparser un fichier
    déjà parsé ici, et rien ne garantirait qu'il le fasse avec le même chemin dans
    les messages.
    """
    chemin = source_path(base, template)
    if not chemin:
        return Result(chemin.status, None, chemin.message)
    f = chemin.unwrap()
    try:
        texte = f.read_text(encoding="utf-8")
    except OSError as exc:
        return fail(f"{f}: illisible — {exc.strerror}")
    lu = parse_contract(texte, f)
    if not lu:
        return Result(lu.status, None, lu.message)
    return ok((f, texte, lu.unwrap()))


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


def _table(value: object, path: Path, subject: str) -> Result[dict[str, object]]:
    """La valeur si c'est une table TOML, un échec nommé sinon."""
    if value is None:
        return ok({})
    if not isinstance(value, dict):
        return fail(f"{path}: {subject} — une table est attendue, trouvé {type(value).__name__}")
    # cast, et non isinstance : `isinstance(x, dict)` ne dit rien des clés ni des
    # valeurs. Les clés sont ramenées à des chaînes, les valeurs restent quelconques —
    # c'est à l'appelant de dire ce qu'il attend de chacune.
    return ok({str(k): v for k, v in cast("dict[object, object]", value).items()})


def _texte(value: object, path: Path, subject: str, default: str = "") -> Result[str]:
    """La valeur si c'est une chaîne, le défaut si elle est absente, un échec sinon."""
    if value is None:
        return ok(default)
    if not isinstance(value, str):
        return fail(f"{path}: {subject} — une chaîne est attendue, trouvé {type(value).__name__}")
    return ok(value)


def _liste(value: object, path: Path, subject: str) -> Result[list[str]]:
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


def load_contract(list_dir: Path) -> Result[Contract]:
    """Le contrat d'une liste, lu sur le disque."""
    path = contract_path(list_dir)
    if not path.is_file():
        return fail(f"{list_dir}: contrat introuvable — {LIST_DIR}/{CONTRACT} attendu")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return fail(f"{path}: illisible — {exc.strerror}")
    return parse_contract(text, path)


def parse_contract(text: str, path: Path) -> Result[Contract]:
    """Le même contrat, depuis un texte déjà en mémoire.

    Séparé de la lecture pour que `derive` puisse juger un gabarit AVANT de créer
    quoi que ce soit : un contrat refusé après un mkdir laisserait une destination
    à moitié construite, que la tentative suivante refuserait comme « existe déjà ».
    `path` ne sert qu'aux messages — il nomme le fichier fautif.
    """
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return fail(f"{path}: TOML invalide — {exc}")

    # NAME REMONTE EN TÊTE : le message de l'ancien format de [sections], plus bas,
    # cite le nom du contrat fautif — il lui faut donc être connu avant d'y arriver.
    # Le résultat est capturé sous un autre nom que la variable de boucle `name`
    # utilisée plus loin pour chaque champ, qui l'écraserait sinon.
    contract_name = _texte(raw.get("name"), path, "« name »")
    if not contract_name:
        return fail(contract_name.message)
    if not contract_name.unwrap():
        return fail(f"{path}: champ « name » manquant — une liste se nomme")

    contract_description = _texte(raw.get("description"), path, "« description »")
    if not contract_description:
        return fail(contract_description.message)

    declared = _table(raw.get("fields"), path, "« fields »")
    if not declared:
        return fail(declared.message)

    fields: dict[str, Field] = {}
    for name, value in declared.unwrap().items():
        decl = _table(value, path, f"champ « {name} »")
        if not decl:
            return fail(decl.message)
        body = decl.unwrap()

        ftype = body.get("type")
        if ftype not in FIELD_TYPES:
            return fail(
                f"{path}: champ « {name} » — type « {ftype} » inconnu ; "
                f"attendus : {', '.join(FIELD_TYPES)}"
            )
        # Pas de cast ni d'assert ici : le test d'appartenance ci-dessus suffit au
        # vérificateur pour tenir ftype pour un FieldType. C'est le contrôle qui
        # porte le typage, et non l'inverse.

        values = _liste(body.get("values"), path, f"champ « {name} », « values »")
        if not values:
            return fail(values.message)
        if ftype == "enum" and not values.unwrap():
            return fail(f"{path}: champ « {name} » — un enum sans `values` n'admet rien")

        # UNE VALEUR EST UN JETON, PAS UNE PHRASE. Rien n'y obligeait, et une valeur
        # portant une espace se découpait en deux pseudo-valeurs dès qu'un appelant
        # itérait dessus — `for c in $(list-dir contract … --values category)` en est
        # un, et il comptait alors deux catégories fantômes à zéro sans qu'aucune
        # commande n'échoue. La vide est refusée pour la même raison : elle traverse
        # une substitution sans laisser de trace.
        for v in values.unwrap():
            if not v or v.split() != [v]:
                return fail(
                    f"{path}: champ « {name} », « values » — une valeur ne peut être vide "
                    f"ni contenir d'espace, trouvé « {v} »"
                )

        description = _texte(body.get("description"), path, f"champ « {name} », « description »")
        if not description:
            return fail(description.message)

        source = body.get("from")
        if source is not None and not isinstance(source, str):
            return fail(
                f"{path}: champ « {name} », « from » — un nom de champ source est attendu, "
                f"trouvé {type(source).__name__}"
            )

        fields[name] = Field(
            name=name,
            type=ftype,
            required=bool(body.get("required", False)),
            description=description.unwrap(),
            values=values.unwrap(),
            source=source,
        )

    declared_sections = _table(raw.get("sections"), path, "« sections »")
    if not declared_sections:
        return fail(declared_sections.message)
    raw_sections = declared_sections.unwrap()

    # L'ANCIEN FORMAT SE REPÈRE À CECI PRÈS : deux clés, `required` et `optional`,
    # portant chacune une LISTE de noms — une section légitimement titrée « required »
    # porterait une table, jamais une liste, donc pas de faux positif ici.
    if isinstance(raw_sections.get("required"), list) or isinstance(
        raw_sections.get("optional"), list
    ):
        return fail(
            f"{path}: [sections] à l'ancien format — deux listes de noms là où une "
            "table par section est attendue. La réécriture est manuelle : voir la "
            "forme à jour dans la semence de cette liste, « list-dir contract --def "
            f"{contract_name.unwrap()} » (« list-dir defs » liste les définitions "
            "disponibles)."
        )

    sections: dict[str, Section] = {}
    for title, value in raw_sections.items():
        decl = _table(value, path, f"section « {title} »")
        if not decl:
            return fail(decl.message)
        body = decl.unwrap()

        if "description" not in body:
            return fail(f"{path}: section « {title} » — « description » manquante")
        description = _texte(body.get("description"), path, f"section « {title} », « description »")
        if not description:
            return fail(description.message)

        sections[title] = Section(
            name=title,
            required=bool(body.get("required", False)),
            description=description.unwrap(),
        )

    return ok(
        Contract(
            name=contract_name.unwrap(),
            description=contract_description.unwrap(),
            fields=fields,
            sections=sections,
        )
    )


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
                return "vide — un champ requis se remplit ou porte son marqueur"
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
        case "list":
            if not isinstance(value, list):
                return f"une liste est attendue, trouvé {type(value).__name__}"
            for entry in cast("list[object]", value):
                if not isinstance(entry, str):
                    return f"une liste de chaînes est attendue, trouvé {type(entry).__name__}"
    return ""
