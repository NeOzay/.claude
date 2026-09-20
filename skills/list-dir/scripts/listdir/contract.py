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

import tomllib
from pathlib import Path

from gabarit.contract import CONTRACT as CONTRACT
from gabarit.contract import Extra, declared_fields, declared_sections, entete
from gabarit.contract import check_value as check_value
from gabarit.contract import field_values as field_values
from gabarit.contract import is_marker as is_marker
from gabarit.contract import table as _table

from .types import Contract, Field, Origin, Result, fail, nom_mal_forme, ok

LIST_DIR = ".list"
PATRONS = "patrons"
"""Les paires <nom>.toml / <nom>.md que `derive` projette, sous .list/."""

SEED = "semence"
"""La semence intacte, telle qu'elle était au dernier semis : le point de référence
de `reseed`. Elle a la FORME D'UNE DÉFINITION — un contrat et ses patrons — ce qui
la rend lisible par `load_source` sans une ligne de plus."""

BACKUP = "backup"
"""Ce que le dernier `reseed` a remplacé. Une seule marche arrière : l'historique
plus ancien est le travail de git."""


def contract_path(list_dir: Path) -> Path:
    return list_base(list_dir) / CONTRACT


def list_base(list_dir: Path) -> Path:
    """Le répertoire d'une liste qui porte `contract.toml` et `patrons/`.

    L'ÉQUIVALENT POUR UNE DÉFINITION EST LA DÉFINITION ELLE-MÊME. C'est toute la
    différence entre les deux, et la seule : une fois la base obtenue, plus rien ne
    distingue une liste d'une semence, et rien ne peut donc les traiter
    différemment par mégarde.
    """
    return list_dir / LIST_DIR


def source_path(base: Path, patron: str = "") -> Result[Path]:
    """Le fichier de contrat d'une base : le sien, ou celui d'un de ses patrons.

    LE NOM DE PATRON EST UN NOM, PAS UN CHEMIN. `--patron ../contract` sortirait
    sinon de `patrons/` — sans danger pour une lecture, mais l'aide annonce « le
    `<nom>.toml` de `patrons/` », et une commande qui rend autre chose que ce
    qu'elle annonce est un échec ouvert de plus.

    L'ABSENCE EST DITE AVEC LE CHEMIN COMPLET, et non avec le nom de la cible : une
    définition mal orthographiée, une liste sans `.list/` et un patron inexistant
    se distinguent alors d'un coup d'œil, sans avoir à reconstruire le chemin de
    tête.
    """
    if not patron:
        f = base / CONTRACT
        return ok(f) if f.is_file() else fail(f"{f}: contrat introuvable")

    if patron != Path(patron).name or patron in (".", ".."):
        return fail(
            f"patron « {patron} » — un nom est attendu, pas un chemin : "
            f"le fichier est cherché dans {PATRONS}/"
        )
    f = base / PATRONS / f"{patron}.toml"
    if not f.is_file():
        return fail(f"{f}: patron « {patron} » introuvable — ce fichier manque")
    return ok(f)


def load_source(base: Path, patron: str = "") -> Result[tuple[Path, str, Contract]]:
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
    chemin = source_path(base, patron)
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


def _forme_du_nom(declared: str, path: Path) -> Result[None]:
    """La forme d'un `origin.def`, dite avec le fichier qui la porte.

    LA RÈGLE VIT DANS `types.nom_mal_forme`, ET NULLE PART AILLEURS : `resolve` la
    juge aussi, sur un argument de ligne de commande plutôt que sur un fichier. Ce
    module n'ajoute que ce qu'il est seul à savoir — quel fichier, et sous quelle clé.

    RIEN N'EST OUVERT ICI, à la différence de `source_path` : une estampille se relit
    sur une machine où la définition n'est pas installée, et une forme qu'on ne juge
    qu'à l'ouverture ne s'y juge jamais.

    > *Mode de défaillance* — sans ce contrôle, `def = "technical-debt/revue"` (faute
    > de frappe) passe, et rien ne le dira jamais : le gel tait la péremption, et
    > `reseed` n'est pas appelé sur une liste jetable. Une estampille fausse est pire
    > qu'une absente, parce qu'elle se croit vraie.
    """
    motif = nom_mal_forme(declared)
    if motif is not None:
        return fail(f"{path}: « origin », « def » — « {declared} » n'est pas un nom : {motif}")
    return ok(None)


def _origin(value: object, path: Path) -> Result[Origin | None]:
    """La table `[origin]`, ou None quand le fichier n'en porte pas.

    LES DEUX ABSENCES NE SE VALENT PAS. Pas de table = aucune provenance déclarée,
    l'état d'une liste antérieure à ce dispositif, et ce que l'avertissement
    d'adoption dit. `def = false` = « cette liste n'a pas de semence », une réponse
    qui fait taire cet avertissement. Les confondre ferait taire le rappel sur toutes
    les listes qu'il vise justement.

    UNE CLÉ INCONNUE EST UN ÉCHEC, pas un ornement ignoré. Un `frozen` mal
    orthographié laisserait une liste que son auteur croit gelée se faire réécrire
    par `reseed` sans un mot — un échec ouvert, ce que ce paquet existe pour
    supprimer. Le contrat n'est pas un langage : ici comme pour FIELD_TYPES, la liste
    est fermée.

    LE NOM EST UN JETON, POUR LA RAISON DES `values` D'UN ENUM : il traverse une
    substitution de shell (`list-dir reseed "$L" --def "$NOM"`), et une espace le
    découperait en deux arguments.
    """
    if value is None:
        return ok(None)
    table = _table(value, path, "« origin »")
    if not table:
        return Result(table.status, None, table.message)
    body = table.unwrap()

    inconnues = sorted(set(body) - {"def", "version", "frozen"})
    if inconnues:
        return fail(
            f"{path}: « origin » — clé{'s' if len(inconnues) > 1 else ''} inconnue"
            f"{'s' if len(inconnues) > 1 else ''} : {', '.join(inconnues)} ; "
            "attendues : def, version, frozen"
        )

    if "def" not in body:
        return fail(
            f"{path}: « origin » — « def » manquante : un nom de définition, "
            "ou false si cette liste n'a pas de semence"
        )
    declared = body["def"]

    if declared is False:
        # Une version ou un gel sous `def = false` n'a rien à quoi se rapporter :
        # il n'y a pas de semence à comparer, ni à refuser de recopier. Les accepter
        # en les ignorant ferait croire à une liste gelée qui ne l'est pas.
        surplus = sorted(k for k in ("version", "frozen") if k in body)
        if surplus:
            return fail(
                f"{path}: « origin » — {', '.join(surplus)} sous « def = false » : "
                "une liste sans semence n'a ni version à comparer, ni semis à refuser"
            )
        return ok(Origin(name=None))

    if not isinstance(declared, str):
        return fail(
            f"{path}: « origin », « def » — un nom de définition ou false est attendu, "
            f"trouvé {type(declared).__name__}"
        )
    if not declared or declared.split() != [declared]:
        return fail(
            f"{path}: « origin », « def » — un nom ne peut être vide ni contenir "
            f"d'espace, trouvé « {declared} »"
        )
    forme = _forme_du_nom(declared, path)
    if not forme:
        return Result(forme.status, None, forme.message)

    version = body.get("version")
    if version is None:
        return fail(
            f'{path}: « origin » — « version » manquante sous « def = "{declared}" » : '
            "c'est elle qui dit si la liste a décroché de sa semence"
        )
    # `isinstance(True, int)` est vrai en Python : sans ce refus, `version = true`
    # passerait pour la version 1.
    if isinstance(version, bool) or not isinstance(version, int):
        return fail(
            f"{path}: « origin », « version » — un entier est attendu, "
            f"trouvé {type(version).__name__}"
        )
    if version < 1:
        return fail(
            f"{path}: « origin », « version » — un entier >= 1 est attendu, trouvé {version}"
        )

    frozen = body.get("frozen", False)
    if not isinstance(frozen, bool):
        return fail(
            f"{path}: « origin », « frozen » — un booléen est attendu, "
            f"trouvé {type(frozen).__name__}"
        )

    return ok(Origin(name=declared, version=version, frozen=frozen))


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

    Séparé de la lecture pour que `derive` puisse juger un patron AVANT de créer
    quoi que ce soit : un contrat refusé après un mkdir laisserait une destination
    à moitié construite, que la tentative suivante refuserait comme « existe déjà ».
    `path` ne sert qu'aux messages — il nomme le fichier fautif.
    """
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return fail(f"{path}: TOML invalide — {exc}")

    # LE NOM PASSE EN TÊTE : le message de l'ancien format de [sections], plus bas,
    # cite le nom du contrat fautif — il lui faut donc être connu avant d'y arriver.
    tete = entete(raw, path, "une liste se nomme")
    if not tete:
        return fail(tete.message)
    contract_name, contract_description = tete.unwrap()

    fields = declared_fields(raw.get("fields"), path, Field, _source(path))
    if not fields:
        return fail(fields.message)

    declared = _table(raw.get("sections"), path, "« sections »")
    if not declared:
        return fail(declared.message)
    raw_sections = declared.unwrap()

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
            f"{contract_name} » (« list-dir defs » liste les définitions "
            "disponibles)."
        )

    sections = declared_sections(raw_sections, path)
    if not sections:
        return fail(sections.message)

    origin = _origin(raw.get("origin"), path)
    if not origin:
        return fail(origin.message)

    return ok(
        Contract(
            name=contract_name,
            description=contract_description,
            fields=fields.unwrap(),
            sections=sections.unwrap(),
            origin=origin.unwrap(),
        )
    )


# ---------------------------------------------------------- propre à une liste
def _source(path: Path) -> Extra:
    """Le contrôle du `from` d'un champ : le nom du champ source d'un contrat dérivé.

    PROPRE À UNE LISTE, joué par `gabarit.contract.parse_field` à l'endroit exact où ce
    contrôle l'a toujours été — après la description, avant le préremplissage. `path`
    ne sert qu'aux messages.
    """

    def controle(name: str, body: dict[str, object]) -> Result[dict[str, object]]:
        source = body.get("from")
        if source is not None and not isinstance(source, str):
            return fail(
                f"{path}: champ « {name} », « from » — un nom de champ source est attendu, "
                f"trouvé {type(source).__name__}"
            )
        return ok({"source": source})

    return controle
