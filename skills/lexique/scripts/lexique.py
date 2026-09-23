"""Lecture et contrôle des lexiques : le global de la configuration, le local d'un projet.

UN LEXIQUE EST UN TABLEAU MARKDOWN, et rien d'autre ne s'y lit. Le fichier peut porter de la
prose autour, mais un seul tableau, dont l'en-tête est exactement `| Terme | Définition | Lien |`.
Chaque ligne a ses trois cellules remplies, et la cellule `Lien` porte un lien Markdown : un terme
dont on ne sait pas où il vit n'a pas de définition vérifiable.

UN TERME COMMENCE PAR UNE MAJUSCULE : c'est ce qui distingue son sens défini du sens courant du
même mot, écrit en minuscule. La majuscule ne distingue pas deux termes pour autant.

UN TERME N'EST DÉFINI QU'UNE FOIS, tous niveaux confondus. Un terme du global est réservé : le
local ne le redéfinit pas. La comparaison se fait après `casefold` et normalisation des espaces —
un terme peut compter plusieurs mots, et « Signal de dérive » est « signal  de dérive ».

STDLIB SEULE : le hook `SessionStart` lance ce module sous le `python3` du PATH, où le venv du
dépôt n'est pas actif. Rien ici ne doit exiger ce qu'il porte.

LA STRUCTURE EST POSÉE PAR LA COMMANDE : `amorcer` écrit l'en-tête d'un lexique local neuf, pour
que le modèle n'ait à écrire que des lignes — un en-tête recopié à la main est un en-tête que
`lire` refuse.

COLLECTE ET JUGEMENT SÉPARÉS : `lire` collecte, `controler` juge. Aucune fonction n'imprime ni
n'appelle `exit` : c'est la CLI qui traduit.
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Le nom du fichier, au global comme au local. Défini ici et NULLE PART AILLEURS dans le code.
FICHIER = "LEXIQUE.md"

ENTETE = ("Terme", "Définition", "Lien")
GLOBAL = "global"
LOCAL = "local"

_LIEN = re.compile(r"\[[^\]]+\]\([^)]+\)")
_SEPARATEUR = re.compile(r":?-+:?")
# Un `|` échappé appartient à la cellule : il ne la coupe pas.
_COUPURE = re.compile(r"(?<!\\)\|")
# Une clôture de bloc de code : ce qu'elle entoure est un exemple, jamais le lexique.
_CLOTURE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Result[T]:
    """Une opération et son issue. status 0 = succès, tout le reste = échec fermé.

    Redéfini ici plutôt qu'importé de `gabarit` : ce module n'a que la stdlib pour horizon.
    """

    status: int
    value: T | None = None
    message: str = ""

    def __bool__(self) -> bool:
        return self.status == 0


@dataclass(frozen=True)
class Terme:
    """Une ligne de lexique, avec le niveau et la ligne du fichier d'où elle vient."""

    niveau: str
    terme: str
    definition: str
    lien: str
    ligne: int

    @property
    def cle(self) -> str:
        """La forme sous laquelle deux termes se comparent."""
        return normaliser(self.terme)


@dataclass(frozen=True)
class Listing:
    """Les termes des deux niveaux, global d'abord, les constats qui les frappent, et les avis.

    Un avis n'est pas un constat : un lexique vide ou absent est un état légitime, qui se dit
    sans faire échouer la commande.
    """

    termes: list[Terme]
    constats: list[str]
    avis: list[str]


def normaliser(terme: str) -> str:
    """Un terme sans variante de casse ni d'espacement."""
    return " ".join(terme.split()).casefold()


def racine_globale() -> Path:
    """La racine de la configuration globale, déduite de la position de ce fichier.

    Le module vit dans `<racine>/skills/lexique/scripts/` : aucune constante, aucune variable
    d'environnement, et la configuration reste déplaçable.
    """
    return Path(__file__).resolve().parents[3]


def chemin_global() -> Path:
    """Le lexique global."""
    return racine_globale() / FICHIER


def racine_projet(depart: Path) -> Path:
    """Le projet auquel appartient `depart` : la racine du dépôt git, ou `depart` hors dépôt.

    Remonter jusqu'au premier `.claude/LEXIQUE.md` est exclu : au-dessus d'un projet rangé sous
    le HOME, la remontée trouverait le lexique GLOBAL et le lirait comme local.
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(depart), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return depart
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else depart


def chemin_local(projet: Path) -> Path:
    """Le lexique local d'un projet."""
    return projet / ".claude" / FICHIER


def _cellules(ligne: str) -> list[str]:
    corps = ligne.strip().removeprefix("|")
    # Le `|` final ferme la ligne, sauf s'il est échappé et appartient à la dernière cellule.
    if corps.endswith("|") and not corps.endswith("\\|"):
        corps = corps[:-1]
    return [c.strip() for c in _COUPURE.split(corps)]


def _blocs(lignes: list[str]) -> list[list[tuple[int, str]]]:
    """Les tableaux du fichier : des suites de lignes contiguës qui commencent par `|`.

    Les lignes d'un bloc de code sont sautées : un tableau d'exemple n'est pas le lexique.
    """
    blocs: list[list[tuple[int, str]]] = []
    courant: list[tuple[int, str]] = []
    dans_code = False
    for numero, ligne in enumerate(lignes, start=1):
        if _CLOTURE.match(ligne):
            dans_code = not dans_code
        if dans_code or _CLOTURE.match(ligne):
            if courant:
                blocs.append(courant)
                courant = []
            continue
        if ligne.lstrip().startswith("|"):
            courant.append((numero, ligne))
        elif courant:
            blocs.append(courant)
            courant = []
    if courant:
        blocs.append(courant)
    return blocs


def lire(chemin: Path, niveau: str) -> Result[list[Terme]]:
    """Les termes d'un lexique. Un fichier absent n'en porte aucun ; un fichier malformé échoue.

    Toutes les fautes sont relevées d'un coup, une par ligne du message, pour qu'une correction
    ne révèle pas la suivante.
    """
    if not chemin.is_file():
        return Result(0, [])
    try:
        texte = chemin.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Result(1, message=f"{chemin} : pas en UTF-8, illisible.")
    except OSError as e:
        return Result(1, message=f"{chemin} : illisible ({e.strerror}).")
    blocs = _blocs(texte.splitlines())
    if len(blocs) != 1:
        compte = "aucun tableau" if not blocs else f"{len(blocs)} tableaux"
        return Result(1, message=f"{chemin} : {compte}, un seul attendu.")

    (n_entete, entete), *reste = blocs[0]
    fautes: list[str] = []
    if tuple(_cellules(entete)) != ENTETE:
        attendu = "| " + " | ".join(ENTETE) + " |"
        fautes.append(f"{chemin}:{n_entete} : en-tête attendu « {attendu} ».")
    if not reste or not all(_SEPARATEUR.fullmatch(c) for c in _cellules(reste[0][1])):
        fautes.append(f"{chemin}:{n_entete + 1} : ligne de séparation `|---|---|---|` attendue.")
        return Result(1, message="\n".join(fautes))

    termes: list[Terme] = []
    for numero, ligne in reste[1:]:
        cellules = _cellules(ligne)
        if len(cellules) != len(ENTETE):
            fautes.append(f"{chemin}:{numero} : {len(cellules)} cellules, {len(ENTETE)} attendues.")
            continue
        terme, definition, lien = cellules
        if not (terme and definition and lien):
            fautes.append(f"{chemin}:{numero} : cellule vide.")
            continue
        if not _LIEN.search(lien):
            fautes.append(f"{chemin}:{numero} : « {terme} » sans lien Markdown `[…](…)`.")
            continue
        if not terme[0].isupper():
            fautes.append(f"{chemin}:{numero} : « {terme} » doit commencer par une majuscule.")
            continue
        termes.append(Terme(niveau, terme, definition, lien, numero))

    if fautes:
        return Result(1, message="\n".join(fautes))
    return Result(0, termes)


def controler(global_: list[Terme], local: list[Terme]) -> list[str]:
    """Les constats qui frappent deux lexiques : doublons dans un niveau, local qui redéfinit."""
    constats: list[str] = []
    for termes in (global_, local):
        vus: dict[str, Terme] = {}
        for t in termes:
            if (premier := vus.get(t.cle)) is not None:
                constats.append(
                    f"{t.niveau} : « {t.terme} » défini deux fois "
                    f"(lignes {premier.ligne} et {t.ligne})."
                )
            else:
                vus[t.cle] = t

    reserves = {t.cle: t for t in global_}
    for t in local:
        if (g := reserves.get(t.cle)) is not None:
            constats.append(
                f"local : « {t.terme} » (ligne {t.ligne}) est déjà réservé au global "
                f"(« {g.terme} », ligne {g.ligne})."
            )
    return constats


def _avis_vide(chemin: Path, niveau: str, termes: list[Terme]) -> list[str]:
    if termes:
        return []
    if not chemin.is_file():
        return [f"{niveau} : aucun lexique ({chemin} absent)."]
    return [f"{niveau} : lexique vide, aucun terme défini ({chemin})."]


def amorcer(chemin: Path) -> Result[Path]:
    """Pose un lexique local neuf, en-tête seul. Refuse d'écraser un fichier existant."""
    if chemin.exists():
        return Result(1, message=f"{chemin} existe déjà : rien n'est écrasé.")
    entete = "| " + " | ".join(ENTETE) + " |"
    separation = "|" + "---|" * len(ENTETE)
    texte = (
        "# Lexique local\n\n"
        "Termes propres à ce projet. Un terme du lexique global ne s'y redéfinit pas "
        "(`lexique liste`).\n\n"
        f"{entete}\n{separation}\n"
    )
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")
    return Result(0, chemin)


def _est_le_global(fichier_local: Path, fichier_global: Path) -> bool:
    """Vrai quand le « local » d'un projet est le fichier global lui-même.

    C'est le cas d'un projet dont la racine est celle de la configuration — le HOME versionné
    par git, par exemple. Lu comme local, le global s'y réserverait contre lui-même.
    """
    return fichier_local.resolve() == fichier_global.resolve()


def lister(fichier_global: Path, fichier_local: Path) -> Result[Listing]:
    """Les termes des deux lexiques, leurs constats et leurs avis. Échoue si l'un est illisible."""
    g = lire(fichier_global, GLOBAL)
    if _est_le_global(fichier_local, fichier_global):
        lo: Result[list[Terme]] = Result(0, [])
        avis_local = [f"local : {fichier_local} est le lexique global, ignoré comme local."]
    else:
        lo = lire(fichier_local, LOCAL)
        avis_local = _avis_vide(fichier_local, LOCAL, lo.value or [])
    fautes = [r.message for r in (g, lo) if not r]
    if g.value is None or lo.value is None:
        return Result(1, message="\n".join(fautes))
    avis = _avis_vide(fichier_global, GLOBAL, g.value) + avis_local
    return Result(0, Listing(g.value + lo.value, controler(g.value, lo.value), avis))


def annonce_session(fichier_global: Path, fichier_local: Path, projet: Path) -> str:
    """Ce que le démarrage de session verse au contexte : le lexique local, et ses conflits.

    Chaîne vide sans lexique local — un hook qui parle pour ne rien dire finit par ne plus être
    lu.
    """
    if not fichier_local.is_file() or _est_le_global(fichier_local, fichier_global):
        return ""
    try:
        texte = fichier_local.read_text(encoding="utf-8").rstrip()
    except (UnicodeDecodeError, OSError):
        # Le lexique ne se verse pas, mais son existence et la faute se disent : un hook muet
        # laisserait croire que le projet n'a pas de lexique.
        texte = "(illisible — voir l'alerte ci-dessous)"
    parties = [f"Lexique local de {projet} ({fichier_local}) :", "", texte]

    r = lister(fichier_global, fichier_local)
    alertes = r.message.splitlines() if r.value is None else r.value.constats
    if alertes:
        parties += [
            "",
            "ALERTE — lexique non conforme, à signaler à l'utilisateur :",
            *(f"  · {a}" for a in alertes),
        ]
    return "\n".join(parties) + "\n"
