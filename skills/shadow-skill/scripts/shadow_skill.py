"""Shadow-skills : des skills rangés hors de `skills/`, que l'agent liste, cherche et charge.

PORTÉE : lire les Shadow-skills de deux niveaux — le global, `<config>/shadow-skills/`, et le
local d'un projet, `<projet>/.claude/shadow-skills/` —, les chercher, en résoudre un par son nom,
lire le registre des tags de chaque niveau et vérifier l'ensemble. Un Shadow-skill est un
répertoire qui porte un `SKILL.md`, Gabarit de la Semence `shadow-skill`. Ce module ne juge pas le
contenu d'un skill.

COLLECTE ET JUGEMENT SÉPARÉS : `verifie` reçoit des lectures et rend des constats ; il n'imprime
rien, et la CLI seule décide du code de sortie.

LE FRONT MATTER SE LIT PAR LA BIBLIOTHÈQUE GABARIT, jamais par un second lecteur : deux
lecteurs d'un même format finissent par ne plus accepter les mêmes fichiers.

UN NIVEAU ABSENT N'EST PAS UNE ERREUR : un projet sans Shadow-skill local est l'état ordinaire.
Un `SKILL.md` mal formé est une faute nommée, et le reste du niveau est servi quand même.
"""

import shutil
import sys
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import cast

# LE PAQUET `gabarit` SE TROUVE PAR SON LIEN DE `bin/`, comme dans
# `skills/list-dir/scripts/listdir/__init__.py`, qui en donne le raisonnement : le `bin/` du
# dépôt d'abord, en remontant, le PATH seulement en repli, et un échec nommé sinon.
if (
    _gabarit := next(
        (
            str(a / "bin" / "gabarit")
            for a in Path(__file__).resolve().parents
            if (a / "bin" / "gabarit").exists()
        ),
        None,
    )
    or shutil.which("gabarit")
) is None:
    raise ImportError(
        "shadow_skill exige le paquet gabarit : aucun bin/gabarit en remontant depuis "
        f"{Path(__file__).resolve().parent}, ni de commande « gabarit » dans le PATH"
    )
if (_scripts := str(Path(_gabarit).resolve().parent)) not in sys.path:
    sys.path.append(_scripts)

from gabarit.commandes import check
from gabarit.items import read_item
from gabarit.prefill import racine_git
from gabarit.types import Result, fail, ok

GLOBAL = "global"
LOCAL = "local"

# Définis ici et NULLE PART AILLEURS : le répertoire d'un niveau, le fichier principal d'un skill.
REPERTOIRE = "shadow-skills"
FICHIER = "SKILL.md"
TAGS = "tags.toml"
SEMENCE = "shadow-skill"
# Le champ du Suivi qui nomme les Shadow-skills d'un Chantier, déclaré par la Semence `suivi`.
CHAMP_SUIVI = "skills"
# Où vit le Suivi actif d'un Chantier, `<slug>.md` : l'arborescence du pipeline, dans
# `skills/implementation-tracker/references/contrat.md#arborescence-et-nommage`.
IMPLEMENTATION = Path(".claude") / "implementation"


@dataclass(frozen=True)
class Niveau:
    """Un niveau de Shadow-skills : son nom (`global` ou `local`) et son répertoire."""

    nom: str
    racine: Path


@dataclass(frozen=True)
class Skill:
    """Un Shadow-skill lu : son niveau, son nom, son fichier principal et ses champs."""

    niveau: str
    nom: str
    chemin: Path
    description: str
    when_to_load: str
    tags: tuple[str, ...]
    estampille: object = None


@dataclass(frozen=True)
class Lecture:
    """Les skills lus sur un ou plusieurs niveaux, et ce qui n'a pas pu l'être.

    `fautes` porte un message par `SKILL.md` écarté ; `illisible` dit qu'un niveau entier n'a
    pas pu être parcouru — le seul cas qui change le code de sortie de `liste`.
    """

    skills: tuple[Skill, ...]
    fautes: tuple[str, ...]
    illisible: bool


def racine_globale() -> Path:
    """La racine de la configuration globale, déduite de la position de ce fichier.

    Le module vit dans `<racine>/skills/shadow-skill/scripts/` : aucune constante, aucune
    variable d'environnement, et la configuration reste déplaçable.
    """
    return Path(__file__).resolve().parents[3]


def racine_projet(depart: Path) -> Path:
    """Le projet de `depart` : la racine du dépôt git, ou `depart` hors dépôt."""
    return racine_git(depart) or depart


def niveaux(projet: Path, globale: Path | None = None) -> list[Niveau]:
    """Le global puis le local de `projet`.

    UN MÊME RÉPERTOIRE N'EST LU QU'UNE FOIS : sur un projet dont le `.claude` est la
    configuration globale elle-même, local et global se confondent, et chaque skill serait
    sinon rapporté deux fois, donc ambigu.
    """
    g = Niveau(GLOBAL, (globale or racine_globale()) / REPERTOIRE)
    loc = Niveau(LOCAL, projet / ".claude" / REPERTOIRE)
    if loc.racine.resolve() == g.racine.resolve():
        return [g]
    return [g, loc]


def _texte(valeur: object) -> str | None:
    """Une valeur texte, ses blancs internes réduits à une espace ; None si ce n'en est pas une.

    Une description TOML peut tenir sur plusieurs lignes : la sortie, elle, est une ligne par
    skill, et un saut de ligne y ouvrirait une ligne fantôme.
    """
    if not isinstance(valeur, str) or not valeur.strip():
        return None
    return " ".join(valeur.split())


def _tags(valeur: object) -> tuple[str, ...] | None:
    """Une liste de chaînes, en tuple ; None si la valeur n'en est pas une."""
    if not isinstance(valeur, list):
        return None
    # `isinstance(…, list)` ne dit rien du type des éléments : le cast l'élargit à `object`,
    # le contrôle qui suit le rétrécit à `str`.
    entrees = cast("list[object]", valeur)
    if not all(isinstance(t, str) for t in entrees):
        return None
    return tuple(cast("list[str]", entrees))


def lire_skill(niveau: str, chemin: Path) -> Result[Skill]:
    """Le Shadow-skill dont `chemin` est le `SKILL.md`, ou un échec qui nomme le champ fautif."""
    lu = read_item(chemin)
    if not lu:
        return fail(lu.message)
    champs = lu.unwrap().fields
    nom, description, quand = (
        _texte(champs.get(c)) for c in ("name", "description", "when-to-load")
    )
    tags = _tags(champs.get("tags"))
    if nom is None:
        return fail(f"{chemin}: champ « name » absent ou vide")
    if description is None:
        return fail(f"{chemin}: champ « description » absent ou vide")
    if quand is None:
        return fail(f"{chemin}: champ « when-to-load » absent ou vide")
    if tags is None:
        return fail(f"{chemin}: champ « tags » — une liste de chaînes est attendue")
    return ok(Skill(niveau, nom, chemin, description, quand, tags, champs.get("gabarit")))


def lire_niveau(niveau: Niveau) -> Lecture:
    """Les skills d'un niveau, dans l'ordre de leurs répertoires."""
    if not niveau.racine.is_dir():
        return Lecture((), (), False)
    try:
        fichiers = sorted(d / FICHIER for d in niveau.racine.iterdir() if (d / FICHIER).is_file())
    except OSError as exc:
        return Lecture((), (f"{niveau.racine}: illisible — {exc.strerror}",), True)
    skills: list[Skill] = []
    fautes: list[str] = []
    for f in fichiers:
        r = lire_skill(niveau.nom, f)
        if r:
            skills.append(r.unwrap())
        else:
            fautes.append(r.message)
    return Lecture(tuple(skills), tuple(fautes), False)


def lister(ou: list[Niveau]) -> Lecture:
    """Les skills de tous les niveaux, global puis local."""
    lectures = [lire_niveau(n) for n in ou]
    return Lecture(
        tuple(s for lu in lectures for s in lu.skills),
        tuple(f for lu in lectures for f in lu.fautes),
        any(lu.illisible for lu in lectures),
    )


def _plier(texte: str) -> str:
    """Le texte sans casse ni accents : « Écrire » et « ecrire » se plient en « ecrire ».

    LES ACCENTS NE DÉPARTAGENT PAS UNE RECHERCHE : l'agent tape un mot sans savoir comment le
    skill l'écrit, et un « deploiement » qui manque « déploiement » cache un skill pertinent.
    La décomposition NFKD détache les diacritiques, qu'on retire ensuite.
    """
    return "".join(
        c for c in unicodedata.normalize("NFKD", texte.casefold()) if not unicodedata.combining(c)
    )


def chercher(skills: tuple[Skill, ...], mots: list[str]) -> list[Skill]:
    """Les skills où figure chaque mot, sans casse ni accents.

    Un mot se cherche dans le nom, la description, `when-to-load` et les tags.
    """
    voulus = [_plier(m) for m in mots]
    return [
        s
        for s in skills
        if all(
            m in _plier(" ".join((s.nom, s.description, s.when_to_load, *s.tags))) for m in voulus
        )
    ]


def trouver(skills: tuple[Skill, ...], nom: str) -> Result[Skill]:
    """Le skill de ce nom.

    UN NOM PRÉSENT AUX DEUX NIVEAUX EST UNE AMBIGUÏTÉ, jamais un masquage : choisir en silence
    ferait charger un skill que l'appelant n'a pas désigné. L'échec nomme les deux chemins.
    """
    trouves = [s for s in skills if s.nom == nom]
    if not trouves:
        connus = ", ".join(sorted({s.nom for s in skills})) or "aucun"
        return fail(f"« {nom} » : aucun Shadow-skill de ce nom. Connus : {connus}")
    if len(trouves) > 1:
        chemins = ", ".join(str(s.chemin) for s in trouves)
        return fail(f"« {nom} » : défini à plusieurs niveaux — {chemins}")
    return ok(trouves[0])


def charger(skill: Skill) -> Result[str]:
    """Le fichier principal, précédé de son répertoire, d'où se résolvent ses liens relatifs."""
    try:
        texte = skill.chemin.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return fail(f"{skill.chemin}: illisible — {exc}")
    return ok(f"Répertoire : {skill.chemin.parent}\n\n{texte}")


@dataclass(frozen=True)
class Tag:
    """Un tag déclaré au registre d'un niveau, et sa description."""

    niveau: str
    nom: str
    description: str


@dataclass(frozen=True)
class Registre:
    """Les tags lus sur un ou plusieurs niveaux, et les registres qui n'ont pas pu l'être."""

    tags: tuple[Tag, ...]
    fautes: tuple[str, ...]


def lire_tags(niveau: Niveau) -> Result[tuple[Tag, ...]]:
    """Le registre `tags.toml` d'un niveau : une table plate `tag = "description"`.

    UN REGISTRE ABSENT EST VIDE, pas fautif : un niveau sans tag propre emploie ceux du global.
    """
    chemin = niveau.racine / TAGS
    if not chemin.is_file():
        return ok(())
    try:
        brut: dict[str, object] = tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return fail(f"{chemin}: illisible — {exc}")
    except tomllib.TOMLDecodeError as exc:
        return fail(f"{chemin}: TOML invalide — {exc}")
    tags: list[Tag] = []
    for nom, valeur in brut.items():
        description = _texte(valeur)
        if description is None:
            return fail(f"{chemin}: tag « {nom} » — une description non vide est attendue")
        tags.append(Tag(niveau.nom, nom, description))
    return ok(tuple(tags))


def registre(ou: list[Niveau]) -> Registre:
    """Les tags de tous les niveaux, global puis local, chacun dans l'ordre de son registre."""
    tags: list[Tag] = []
    fautes: list[str] = []
    for n in ou:
        r = lire_tags(n)
        if r:
            tags.extend(r.unwrap())
        else:
            fautes.append(r.message)
    return Registre(tuple(tags), tuple(fautes))


def chemin_suivi(projet: Path, slug: str) -> Result[Path]:
    """Le Suivi actif du Chantier `slug` dans `projet`, ou un échec qui nomme le chemin cherché.

    UN SLUG N'EST PAS UN CHEMIN : un `/` ou un `..` ferait lire un fichier hors de
    `.claude/implementation/`, qu'aucun Chantier ne désigne.
    """
    if not slug or slug != slug.strip() or "/" in slug or slug.startswith("."):
        return fail(f"« {slug} » n'est pas un slug de Chantier")
    chemin = projet / IMPLEMENTATION / f"{slug}.md"
    if not chemin.is_file():
        return fail(f"« {slug} » : aucun Suivi actif ({chemin} absent)")
    return ok(chemin)


def noms_du_suivi(chemin: Path) -> Result[list[str]]:
    """Les noms du champ `skills` d'un Suivi, ou un échec nommé."""
    lu = read_item(chemin)
    if not lu:
        return fail(lu.message)
    champs = lu.unwrap().fields
    if CHAMP_SUIVI not in champs:
        return fail(f"{chemin}: aucun champ « {CHAMP_SUIVI} »")
    noms = _tags(champs[CHAMP_SUIVI])
    if noms is None:
        return fail(f"{chemin}: champ « {CHAMP_SUIVI} » — une liste de noms est attendue")
    return ok(list(noms))


def verifier(lecture: Lecture, tags: Registre) -> list[str]:
    """Les constats sur des skills lus et leur registre de tags. Liste VIDE = conforme.

    UN CONTRÔLE QUI N'EXAMINE RIEN ÉCHOUE : aucun skill lu est un constat, jamais un succès.
    Un niveau vidé par erreur passerait sinon pour un niveau conforme.
    """
    constats = [*lecture.fautes, *tags.fautes]
    if not lecture.skills:
        constats.append("aucun Shadow-skill examiné")

    globaux = {t.nom for t in tags.tags if t.niveau == GLOBAL}
    for t in tags.tags:
        if t.niveau != GLOBAL and t.nom in globaux:
            constats.append(f"tag « {t.nom} » : déjà déclaré au registre global")

    for s in lecture.skills:
        controle = check(s.chemin, filled=True)
        if not controle:
            constats.append(controle.message)
        if s.estampille != SEMENCE:
            constats.append(f"{s.chemin}: estampillé autrement que « {SEMENCE} »")
        if s.nom != s.chemin.parent.name:
            constats.append(
                f"{s.chemin}: « name » vaut « {s.nom} », le répertoire « {s.chemin.parent.name} »"
            )
        connus = globaux | {t.nom for t in tags.tags if t.niveau == s.niveau}
        constats.extend(
            f"{s.chemin}: tag « {t} » absent du registre ({TAGS})"
            for t in s.tags
            if t not in connus
        )

    vus: dict[str, Skill] = {}
    for s in lecture.skills:
        if s.nom in vus:
            constats.append(
                f"« {s.nom} » : défini à plusieurs niveaux — {vus[s.nom].chemin}, {s.chemin}"
            )
        vus.setdefault(s.nom, s)
    return constats
