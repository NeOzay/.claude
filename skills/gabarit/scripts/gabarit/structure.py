"""Une section structurée — à motif ou à labels — confrontée à son contrat.

PORTÉE : ce module juge le corps d'une section qui déclare un `type`. Une section sans
`type` n'y passe jamais : elle suit le chemin d'avant, dans check.py, à l'identique.

LES BLANCS SE RÉDUISENT AVANT DE COMPARER : rumdl réenroule à 100 colonnes une ligne qui
dépasse, et le marqueur d'une section à motif dépasse vite. Reconnu sur une ligne, il doit
l'être encore sur deux.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .contract import check_value, is_marker
from .items import outside_fences
from .motif import compile_motif, decoupe, reduit_blancs
from .types import (
    ENTIER,
    FIN_LIGNE,
    MOTIF_MARKER,
    OPTIONAL,
    PLACEHOLDER,
    RANG_SECTION,
    Capture,
    Contract,
    Item,
    Result,
    Section,
    fail,
    ok,
)

type Faute = tuple[str, str]
"""Un manquement : son sujet — le chemin jusqu'à la puce ou la capture — et sa raison."""

_BOLD = re.compile(r"^\*\*(?P<nom>[^*]+?)\*\*[ \t]*:(?P<reste>.*)$")
"""`**Nom** :` ou `**Nom**:`, en début de ligne ; le corps peut suivre sur la même ligne."""

_OUVERTURES_MOTIF = tuple(f"{base[:-1]} {MOTIF_MARKER} " for base in (PLACEHOLDER, OPTIONAL))


def is_section_marker(texte: str) -> bool:
    """Vrai si le corps d'une section structurée est un marqueur — générique, ou d'un motif.

    Le motif n'est pas comparé à celui du contrat : un marqueur reste un marqueur, même posé
    par une version antérieure du contrat. Seule sa forme compte.
    """
    reduit = reduit_blancs(texte).strip()
    if is_marker(reduit):
        return True
    return reduit.endswith(">") and reduit.startswith(_OUVERTURES_MOTIF)


# --------------------------------------------------------------------- les puces
@dataclass(frozen=True)
class Puce:
    """Une puce d'une section à motif : son rang (depuis 1) et son texte, bornes retirées,
    blancs réduits, rogné."""

    numero: int
    texte: str


def _ouvre(ligne: str, debut: str) -> str | None:
    """Le reste de la ligne si elle ouvre une puce — `debut` suivi d'un blanc —, sinon None."""
    nue = ligne.strip()
    if nue == debut:
        return ""
    if nue.startswith(debut) and nue[len(debut)].isspace():
        return nue[len(debut) :]
    return None


def decoupe_puces(section: Section, corps: str, sujet: str) -> tuple[list[Puce], list[Faute]]:
    """Les puces bien closes d'une section à motif, et les fautes de découpe.

    UNE PUCE SE CLÔT PAR UNE LIGNE TERMINÉE PAR `fin`, suivie d'une ligne vide, d'une
    puce, ou de la fin de la section. Un « ;; » en fin de ligne suivi d'une ligne de texte
    est intérieur : la puce continue. Une puce ouverte avant la `fin` de la précédente —
    une puce imbriquée — ou une dernière puce sans `fin` est une faute, et la puce fautive
    n'est pas jugée plus loin. Un texte non blanc hors puce est une faute, nommée une fois
    par passage. Une `fin` de ligne suit sa propre règle : `_decoupe_lignes`.
    """
    if section.fin == FIN_LIGNE:
        return _decoupe_lignes(section, corps, sujet)
    puces: list[Puce] = []
    fautes: list[Faute] = []
    courante: list[str] | None = None
    numero = 0
    hors_puce_signale = False

    def close_possible() -> bool:
        pleines = [ligne for ligne in courante or [] if ligne.strip()]
        return bool(pleines) and pleines[-1].rstrip().endswith(section.fin)

    def clore() -> None:
        texte = "\n".join(courante or []).rstrip()
        texte = reduit_blancs(texte[: -len(section.fin)]).strip()
        puces.append(Puce(numero, texte))

    for ligne in corps.splitlines():
        reste = _ouvre(ligne, section.debut)
        if courante is not None:
            if reste is None and ligne.strip():
                courante.append(ligne)
                continue
            if close_possible():
                clore()
            elif reste is not None:
                fautes.append(
                    (
                        f"{sujet}, puce {numero}",
                        f"« {section.fin} » manquant avant la puce suivante — une puce se "
                        "clôt avant qu'une autre s'ouvre, et ne s'imbrique pas",
                    )
                )
            else:
                courante.append(ligne)  # une ligne vide dans une puce encore ouverte
                continue
            courante = None
        if reste is not None:
            numero += 1
            courante = [reste]
            hors_puce_signale = False
        elif ligne.strip() and not hors_puce_signale:
            fautes.append(
                (
                    sujet,
                    f"texte hors puce : « {ligne.strip()} » — une section à motif ne porte "
                    "que des puces",
                )
            )
            hors_puce_signale = True

    if courante is not None:
        if close_possible():
            clore()
        else:
            fautes.append((f"{sujet}, puce {numero}", f"« {section.fin} » final manquant"))
    return puces, fautes


def _decoupe_lignes(section: Section, corps: str, sujet: str) -> tuple[list[Puce], list[Faute]]:
    """Les puces d'une section à `fin` de ligne, et les fautes de découpe.

    UNE PUCE FINIT À LA LIGNE, ET SA SUITE S'ÉCRIT EN RETRAIT, comme dans une liste Markdown :
    c'est la forme que rumdl laisse à une puce qu'il réenroule. Une ligne vide, une puce ou
    un texte collé à la marge la closent ; aucune `fin` ne peut donc manquer. Une puce en
    retrait est imbriquée : une faute, comptée dans la `sequence`, sa suite comprise.
    """
    puces: list[Puce] = []
    fautes: list[Faute] = []
    courante: list[str] | None = None
    fautive = False
    numero = 0
    hors_puce_signale = False

    def clore() -> None:
        if courante is not None and not fautive:
            puces.append(Puce(numero, reduit_blancs("\n".join(courante)).strip()))

    for ligne in corps.splitlines():
        reste = _ouvre(ligne, section.debut)
        en_retrait = ligne[:1].isspace()
        if courante is not None and reste is None and ligne.strip() and en_retrait:
            courante.append(ligne)
            continue
        clore()
        courante = None
        if reste is not None:
            numero += 1
            courante = [reste]
            fautive = en_retrait
            hors_puce_signale = False
            if fautive:
                fautes.append(
                    (
                        f"{sujet}, puce {numero}",
                        "puce imbriquée — une puce s'ouvre à la marge, sa suite seule va en "
                        "retrait",
                    )
                )
        elif ligne.strip() and not hors_puce_signale:
            fautes.append(
                (
                    sujet,
                    f"texte hors puce : « {ligne.strip()} » — une section à motif ne porte "
                    "que des puces",
                )
            )
            hors_puce_signale = True
    clore()
    return puces, fautes


# -------------------------------------------------------------------- les captures
def _valeur(capture: Capture, brute: str) -> str | int | None:
    """La valeur d'une capture telle que `check_value` la jugera, None si elle est vide.

    UNE ENUM SE COMPARE BRUTE, PUIS ROGNÉE : c'est ce qui laisse « [ ] » valoir `" "`.
    Un `int` bien écrit passe par `int()` ; tout autre texte part en chaîne, et
    `check_value` le refuse — le type n'est défini qu'à un endroit.
    """
    if capture.type == "enum" and brute in capture.values:
        return brute
    valeur = brute.strip()
    if not valeur:
        return None
    if capture.type == "int" and ENTIER.fullmatch(valeur):
        return int(valeur)
    return valeur


def check_motif(section: Section, corps: str, sujet: str) -> list[Faute]:
    """Les fautes d'une section à motif hors marqueur : découpe, motif, captures."""
    if section.motif is None:
        return []
    puces, fautes = decoupe_puces(section, corps, sujet)
    expression = compile_motif(decoupe(section.motif).unwrap(), section.captures)
    for puce in puces:
        ici = f"{sujet}, puce {puce.numero}"
        trouve = expression.fullmatch(puce.texte)
        if trouve is None:
            fautes.append((ici, f"« {puce.texte} » ne suit pas le motif « {section.motif} »"))
            continue
        for nom, capture in section.captures.items():
            raison = _juge(capture, _valeur(capture, trouve.group(nom)), puce.numero - 1)
            if raison:
                fautes.append((f"{ici}, capture « {nom} »", raison))
    return fautes


def _juge(capture: Capture, valeur: str | int | None, rang: int) -> str:
    """La raison du manquement d'une capture, ou une chaîne vide.

    `rang` compte depuis 0 TOUTES les puces ouvertes, fautives comprises : une puce mal
    close ne décale pas la séquence des suivantes.
    """
    if valeur is None:
        return "vide — la capture est requise" if capture.required else ""
    raison = check_value(capture, valeur)
    if raison or not isinstance(valeur, int):
        return raison
    if capture.min is not None and valeur < capture.min:
        return f"{valeur} est sous le minimum {capture.min}"
    if capture.max is not None and valeur > capture.max:
        return f"{valeur} dépasse le maximum {capture.max}"
    if capture.sequence:
        attendu = (capture.min if capture.min is not None else 1) + rang
        if valeur != attendu:
            return f"{valeur} rompt la séquence — {attendu} attendu à cette puce"
    return ""


# ---------------------------------------------------------------------- les labels
@dataclass(frozen=True)
class Bloc:
    """Un label tel que le fichier l'écrit : son étiquette, son corps, et s'il suit une
    ligne non vide."""

    nom: str
    corps: str
    colle: bool


def _etiquette(ligne: str, section: Section, rang: int) -> tuple[str, str] | None:
    """L'étiquette et le début du corps si la ligne ouvre un label de cette table."""
    if section.forme == "bold":
        trouve = _BOLD.match(ligne)
        if trouve is None:
            return None
        return trouve.group("nom").strip(), trouve.group("reste").strip()
    diese = "#" * rang + " "
    if not ligne.startswith(diese):
        return None
    return ligne[len(diese) :].strip().rstrip("#").strip(), ""


def decoupe_labels(section: Section, corps: str, rang: int) -> tuple[str, list[Bloc]]:
    """La prose avant le premier label, et les labels dans l'ordre du fichier.

    Un label court jusqu'au suivant de même niveau, ou la fin de son parent. Une étiquette
    dans un bloc de code n'en est pas une — la règle d'`outside_fences`, la même que celle
    des sections. Une étiquette non déclarée ouvre un label comme une autre : c'est le
    contrat qui la dira inconnue.
    """
    avant: list[str] = []
    blocs: list[tuple[str, list[str], bool]] = []
    precedente = ""
    for ligne, libre in outside_fences(corps):
        etiquette = _etiquette(ligne, section, rang) if libre else None
        if etiquette is not None:
            nom, reste = etiquette
            blocs.append((nom, [reste] if reste else [], bool(precedente.strip())))
        elif blocs:
            blocs[-1][1].append(ligne)
        else:
            avant.append(ligne)
        precedente = ligne
    return "\n".join(avant).strip(), [
        Bloc(nom, "\n".join(lignes).strip("\n"), colle) for nom, lignes, colle in blocs
    ]


def _corps_au_marqueur(label: Section, corps: str, rang: int) -> bool:
    """Vrai si le corps d'un label, ou d'une section, n'a pas été entamé."""
    nu = corps.strip()
    if not nu:
        return False  # un corps vidé a été touché : `new` pose toujours un marqueur
    if label.type == "label" and not is_section_marker(nu):
        return _squelette_au_marqueur(label, nu, rang)
    return is_section_marker(nu) if label.type else is_marker(nu)


def _squelette_au_marqueur(section: Section, corps: str, rang: int) -> bool:
    """Vrai si la prose et chaque label présent d'une table sont restés au marqueur.

    UN LABEL PRÉREMPLI N'Y COMPTE PAS : `new` le pose plein, et sa valeur ne dit pas que
    la table a été entamée. Une étiquette non déclarée, si : quelqu'un l'a écrite.
    """
    avant, blocs = decoupe_labels(section, corps, rang)
    if (avant and not is_marker(avant)) or not (avant or blocs):
        return False
    for bloc in blocs:
        label = section.labels.get(bloc.nom)
        if label is None:
            return False
        if label.text is not None or label.command is not None:
            continue
        if not _corps_au_marqueur(label, bloc.corps, rang + 1):
            return False
    return True


def is_section_untouched(section: Section, corps: str) -> bool:
    """Vrai si une section structurée est restée au marqueur — le sien, ou le squelette de
    ses labels tel que `new` l'a posé, sans rien d'entamé.

    C'est ce que `merge` omet d'une section facultative, et ce que `--filled` ne réclame
    jamais d'une table facultative : les facultatifs ne sont jamais réclamés.
    """
    return _corps_au_marqueur(section, corps, RANG_SECTION + 1)


def _labels(
    section: Section, corps: str, sujet: str, rang: int, filled: bool
) -> tuple[list[Faute], list[Faute]]:
    """Les fautes et les notes d'une section à labels, labels emboîtés compris.

    UNE TABLE FACULTATIVE LAISSÉE AU MARQUEUR N'EST PAS JUGÉE : ses labels requis ne le
    sont qu'une fois la table entamée. Sans cela, un fichier qu'on vient de poser échouerait
    à `--filled`, et l'on ne s'en sortirait qu'en supprimant la section.
    """
    fautes: list[Faute] = []
    notes: list[Faute] = []
    if not section.required and _squelette_au_marqueur(section, corps, rang):
        return fautes, notes
    avant, blocs = decoupe_labels(section, corps, rang)
    if avant and section.prefix is None:
        fautes.append(
            (
                sujet,
                f"prose avant le premier label : « {avant.splitlines()[0].strip()} » — sans "
                "« prefix », la section ne porte que des labels",
            )
        )
    # LA PROSE D'UN `prefix` PREND LE `required` DE SA TABLE : réclamée si la table l'est,
    # jamais sinon.
    elif section.prefix is not None and section.required:
        if not avant:
            fautes.append((sujet, f"prose d'introduction manquante — {section.prefix}"))
        elif filled and is_marker(avant):
            fautes.append((sujet, "prose d'introduction à remplir"))

    vus: set[str] = set()
    precedent: tuple[str, int] | None = None  # le dernier label lu à porter un `order`
    for bloc in blocs:
        ici = f"{sujet}, label « {bloc.nom} »"
        if bloc.colle:
            fautes.append((ici, "non séparé de ce qui précède par une ligne vide"))
        label = section.labels.get(bloc.nom)
        if label is None:
            notes.append((ici, "étiquette non déclarée au contrat"))
            continue
        if bloc.nom in vus:
            fautes.append((ici, "en double"))
            continue
        vus.add(bloc.nom)
        if label.deprecated is not None:
            notes.append((ici, f"déprécié : {label.deprecated}"))
        if label.order is not None:
            if precedent is not None and label.order < precedent[1]:
                fautes.append(
                    (
                        ici,
                        f"« order » {label.order} placé après « {precedent[0]} » ({precedent[1]})",
                    )
                )
            precedent = (bloc.nom, label.order)
        f, n = _juge_corps(label, bloc.corps, ici, rang + 1, filled)
        fautes.extend(f)
        notes.extend(n)

    for nom, label in section.labels.items():
        if label.required and nom not in vus:
            fautes.append((f"{sujet}, label « {nom} »", "manquant"))
    return fautes, notes


def _juge_corps(
    label: Section, corps: str, sujet: str, rang: int, filled: bool
) -> tuple[list[Faute], list[Faute]]:
    """Un label présent : vide, au marqueur, ou jugé selon son propre `type`."""
    nu = corps.strip()
    if not nu:
        return ([(sujet, "vide")] if label.required else []), []
    au_marqueur = is_section_marker(nu) if label.type else is_marker(nu)
    if au_marqueur:
        return ([(sujet, "à remplir")] if filled and label.required else []), []
    return _juge_section(label, nu, sujet, rang, filled)


def _juge_section(
    section: Section, corps: str, sujet: str, rang: int, filled: bool
) -> tuple[list[Faute], list[Faute]]:
    if section.type == "motif":
        return check_motif(section, corps, sujet), []
    if section.type == "label":
        return _labels(section, corps, sujet, rang, filled)
    return [], []


def check_structure(section: Section, corps: str, sujet: str, filled: bool = False) -> list[Faute]:
    """Les fautes d'une section structurée, hors marqueur. Rien pour une section sans `type`.

    `filled` ne vaut que pour les labels : une section restée au marqueur n'arrive pas ici.
    """
    return _juge_section(section, corps, sujet, RANG_SECTION + 1, filled)[0]


def structure_notes(section: Section, corps: str, sujet: str) -> list[Faute]:
    """Ce qu'il y a à dire d'une section structurée sans que ce soit un manquement :
    étiquette non déclarée, label déprécié encore présent."""
    return _juge_section(section, corps, sujet, RANG_SECTION + 1, False)[1]


# ------------------------------------------------------------------ section_values
type Captures = dict[str, str | int | None]
"""Les captures d'une puce, par nom : un `int` converti, None pour une facultative vide."""

type Valeur = str | list[Captures] | dict[str, Valeur]
"""Ce qu'un label vaut : son corps rogné, les puces de son motif, ou ses propres labels."""


def section_values(
    contract: Contract, item: Item, titre: str
) -> Result[list[Captures] | dict[str, Valeur]]:
    """Ce que porte une section structurée : une entrée par puce d'un motif, un label par
    clé d'une section à labels.

    LA SECTION EST JUGÉE D'ABORD, PAR `check_structure` : une section mal formée rend un
    échec qui nomme chaque faute, jamais une lecture partielle. Une section absente, non
    déclarée ou sans `type` est un échec nommé — elle n'a rien de structuré à rendre.

    UN MARQUEUR NE VAUT RIEN : une section ou un label restés au marqueur rendent une
    liste ou un dict vides ; un label en prose au marqueur, absent ou vide n'a pas de clé.
    Une étiquette non déclarée n'en a pas non plus : le contrat ne dit pas ce qu'elle vaut.
    """
    sujet = f"section « {titre} »"
    section = contract.sections.get(titre)
    if section is None:
        return fail(f"{item.path}: {sujet} — non déclarée au contrat « {contract.name} »")
    if section.type is None:
        return fail(f"{item.path}: {sujet} — sans `type` : de la prose, rien de structuré")
    corps = item.sections.get(titre)
    if corps is None:
        return fail(f"{item.path}: {sujet} — absente du fichier")
    if section.type == "motif":
        vide: list[Captures] | dict[str, Valeur] = []
    else:
        vide = {}
    if not corps.strip() or is_section_marker(corps):
        return ok(vide)

    fautes = check_structure(section, corps, sujet)
    if fautes:
        return fail("\n".join(f"{item.path}: {s} — {r}" for s, r in fautes))
    lu = _lire(section, corps, RANG_SECTION + 1)
    if isinstance(lu, str):  # une section typée ne rend jamais sa prose
        return ok(vide)
    return ok(lu)


def _lire(section: Section, corps: str, rang: int) -> Valeur:
    """La valeur d'une section ou d'un label déjà jugés conformes."""
    nu = corps.strip()
    if section.type == "motif":
        if section.motif is None or not nu or is_section_marker(nu):
            return []
        puces, _ = decoupe_puces(section, nu, "")
        expression = compile_motif(decoupe(section.motif).unwrap(), section.captures)
        lues: list[Captures] = []
        for puce in puces:
            trouve = expression.fullmatch(puce.texte)
            if trouve is not None:
                lues.append(
                    {nom: _valeur(c, trouve.group(nom)) for nom, c in section.captures.items()}
                )
        return lues
    if section.type == "label":
        if not nu or is_section_marker(nu):
            return {}
        labels: dict[str, Valeur] = {}
        for bloc in decoupe_labels(section, nu, rang)[1]:
            label = section.labels.get(bloc.nom)
            if label is None or bloc.nom in labels:
                continue
            texte = bloc.corps.strip()
            if label.type is not None:
                labels[bloc.nom] = _lire(label, texte, rang + 1)
            elif texte and not is_marker(texte):
                labels[bloc.nom] = texte
        return labels
    return nu
