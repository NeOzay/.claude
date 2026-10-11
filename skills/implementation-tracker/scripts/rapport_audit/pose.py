"""`audit new` : poser le rapport d'un audit, depuis le Suivi, le Brief, git et l'audit précédent.

PORTÉE : la commande écrit tout ce que l'auditeur n'a pas à juger — l'en-tête, la copie de la
Dette précédente, les cumuls de Dette corrigée et de Dette écartée, les points de la revue avec
leur texte du Brief —, et le Marqueur partout où il écrit. Elle ne range aucune dette et n'écrit
aucun verdict : ce sont les jugements de l'auditeur.

UN SEUL PRÉCÉDENT : le dernier rapport du répertoire, lu et exigé rempli. Les plus anciens ne se
lisent pas — le précédent porte déjà leurs cumuls.

LES VÉRIFICATIONS S'EXÉCUTENT D'AVANCE : la commande `— vérif:` de chaque Étape cochée du Suivi
est lancée depuis la racine, et son résultat consigné. L'auditeur juge, et rejoue au besoin ; les
commandes des critères du Brief restent les siennes.

ÉCHEC FERMÉ : le rapport posé est validé par le modèle avant d'être écrit, et rien n'est écrit sur
un échec. Un rapport existant n'est jamais écrasé.
"""

import datetime as dt
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, cast

import tomlkit
from gabarit.contract import is_marker
from gabarit.gitcmd import git
from gabarit.items import read_item, toml_value
from gabarit.prefill import racine_git
from gabarit.types import PLACEHOLDER, Result, fail, ok
from pydantic import ValidationError
from tomlkit.items import AoT, Item, Table

from rapport_audit.modele import Audit, Mode, lire

type Type = Literal["intermédiaire", "clôture"]

# Où vivent le Suivi et les rapports d'un Chantier : l'arborescence du pipeline, dans
# `skills/implementation-tracker/references/contrat.md#arborescence-et-nommage`.
IMPLEMENTATION = Path(".claude") / "implementation"
RAPPORT = re.compile(r"^([0-9]{2})-[0-9a-f]{7,40}\.toml$")

# Les sections du Brief que la revue reprend, déclarées par la Semence `brief`.
INTENTION = "Intention"
CRITERES = "Critères de réussite"
HORS_PERIMETRE = "Hors-périmètre"
SIGNAUX = "Signaux de dérive"

# Une puce numérotée du Brief : `**C1** — …`, `**S2** — …`.
NUMEROTEE = re.compile(r"^\*\*([CS][1-9][0-9]*)\*\*\s+—\s+(.+)$")
# La source qui clôt une puce, `(dit)`, `(dit ; dépôt: …)`, `(dépôt: …)`, point final compris : la
# Semence `brief` la déclare, et le rapport cite le texte sans elle, point gardé.
SOURCE = re.compile(r"\s*\((?:dit|dépôt\s*:)[^()]*\)(\.?)$")
SYMPTOME = "**Symptôme** :"

# La section du Suivi qui porte les Étapes, et la forme d'une Étape cochée, puce ôtée :
# `contrat.md`, « Format d'étape ». Une Étape enroulée par le formateur se lit en joignant ses
# lignes de suite.
ETAPES = "Étapes"
COCHEE = re.compile(r"^\[x\] ([1-9][0-9]*)\. .* — vérif: (.+)$")
# Une commande est une seule portée de code ; toute autre forme est une vérification en prose.
COMMANDE = re.compile(r"^`([^`]+)`$")
# Ce que le rapport garde de la sortie : la fin, où se lisent le décompte et l'erreur.
LIGNES, CARACTERES = 20, 2000
DELAI = 600  # secondes : une suite de tests entière y tient
# Le shell n'a pas trouvé ou pas pu lancer la commande : rien n'a été vérifié.
NON_LANCEE = (126, 127)
# Les séquences de couleur, puis tout caractère de contrôle autre que la tabulation et le saut de
# ligne : aucune écriture TOML ne les porte lisiblement.
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
CONTROLE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")

ENTETE = (
    "Posé par `audit new`. L'auditeur remplit chaque <À REMPLIR>, range chaque dette précédente\n"
    "par `audit range`, ajoute les siennes par `audit dette`, et écrit le verdict en dernier."
)


def puces(section: str) -> list[str]:
    """Les puces de premier niveau d'une section, chacune sur une ligne."""
    puces: list[str] = []
    for ligne in section.splitlines():
        if ligne.startswith("- "):
            puces.append(ligne[2:].strip())
        elif puces and ligne.startswith("  ") and ligne.strip():
            puces[-1] += " " + ligne.strip()
    return puces


def _sans_source(texte: str) -> str:
    return SOURCE.sub(r"\1", texte).strip()


def _numerotees(section: str, prefixe: str, nom: str) -> Result[list[tuple[str, str]]]:
    """Les puces `**<prefixe><n>** — texte`, ou un échec qui nomme la puce sans numéro."""
    points: list[tuple[str, str]] = []
    for puce in puces(section):
        m = NUMEROTEE.match(puce)
        if m is None or not m.group(1).startswith(prefixe):
            return fail(f"Brief, {nom} : puce sans numéro `**{prefixe}<n>**` — {puce[:60]}")
        points.append((m.group(1), _sans_source(m.group(2))))
    return ok(points)


def _symptome(intention: str) -> str | None:
    """Le paragraphe `**Symptôme** :` de l'Intention, sur une ligne."""
    lignes: list[str] = []
    for ligne in intention.splitlines():
        if ligne.startswith(SYMPTOME):
            lignes.append(ligne.removeprefix(SYMPTOME).strip())
        elif lignes and ligne.strip() and not ligne.startswith("**"):
            lignes.append(ligne.strip())
        elif lignes:
            break
    return " ".join(lignes) or None


def revue(sections: Mapping[str, str]) -> Result[dict[str, object]]:
    """Les points de la revue, posés depuis les sections du Brief, `etat` et `constat` à remplir."""
    a_remplir = {"etat": PLACEHOLDER, "constat": PLACEHOLDER}
    criteres = _numerotees(sections.get(CRITERES, ""), "C", CRITERES)
    if not criteres:
        return fail(criteres.message)
    signaux = _numerotees(sections.get(SIGNAUX, ""), "S", SIGNAUX)
    if not signaux:
        return fail(signaux.message)
    conformite: dict[str, object] = {
        "critere": [{"id": i, "critere": t, **a_remplir} for i, t in criteres.unwrap()],
        "hors_perimetre": [
            {"exclusion": _sans_source(p), **a_remplir}
            for p in puces(sections.get(HORS_PERIMETRE, ""))
        ],
        "signal": [{"id": i, "signal": t, **a_remplir} for i, t in signaux.unwrap()],
    }
    symptome = _symptome(sections.get(INTENTION, ""))
    if symptome is not None:
        conformite["symptome"] = {"symptome": symptome, **a_remplir}
    return ok(conformite)


def _fin(sortie: str) -> str:
    """La fin de la sortie, nettoyée, bornée en lignes puis en caractères."""
    propre = CONTROLE.sub("", ANSI.sub("", sortie.replace("\r\n", "\n")))
    fin = "\n".join(propre.strip().splitlines()[-LIGNES:])[-CARACTERES:]
    return fin or "aucune sortie"


def executer(racine: Path, origine: str, verif: str) -> dict[str, object]:
    """Une vérification exécutée depuis la racine ; `dette` au Marqueur si elle échoue."""
    m = COMMANDE.match(verif.strip())
    if m is None:
        return {
            "origine": origine,
            "commande": verif.strip(),
            "statut": "non-exécutée",
            "sortie": "vérification en prose, pas une commande : à mener par l'auditeur",
        }
    commande = m.group(1)
    verification: dict[str, object] = {"origine": origine, "commande": commande}
    try:
        p = subprocess.run(
            ["bash", "-c", commande],
            cwd=racine,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=DELAI,
            check=False,
        )
    except OSError as e:
        return {**verification, "statut": "non-exécutée", "sortie": f"bash : {e.strerror}"}
    except subprocess.TimeoutExpired:
        return {**verification, "statut": "non-exécutée", "sortie": f"délai de {DELAI} s dépassé"}
    sortie = _fin(p.stdout + p.stderr)
    if p.returncode in NON_LANCEE:
        return {**verification, "statut": "non-exécutée", "sortie": sortie}
    if p.returncode != 0:
        return {
            **verification,
            "statut": "échouée",
            "sortie": f"code de sortie {p.returncode}\n{sortie}",
            "dette": PLACEHOLDER,
        }
    return {**verification, "statut": "passée", "sortie": sortie}


def verifications(racine: Path, etapes: str) -> list[dict[str, object]]:
    """Les vérifications des Étapes cochées de la section `## Étapes`, dans leur ordre."""
    return [
        executer(racine, f"Étape {m.group(1)}", m.group(2))
        for etape in puces(etapes)
        if (m := COCHEE.match(etape)) is not None
    ]


def _texte(champs: Mapping[str, object], nom: str) -> str | None:
    """Un champ texte du Suivi ; None s'il est absent ou au Marqueur."""
    valeur = champs.get(nom)
    if isinstance(valeur, str) and valeur.strip() and not is_marker(valeur):
        return valeur
    return None


def _git(racine: Path, *argv: str) -> Result[str]:
    r = git(*argv, cwd=racine)
    return ok(r.unwrap().strip()) if r else fail(f"git {' '.join(argv)} : {r.message}")


def _dernier(dossier: Path) -> tuple[int, Path | None]:
    """Le rang du dernier rapport du répertoire et son chemin ; (0, None) s'il n'y en a aucun."""
    rapports = [
        (int(m.group(1)), p)
        for p in dossier.glob("*.toml")
        if (m := RAPPORT.match(p.name)) is not None
    ]
    return max(rapports, default=(0, None), key=lambda r: r[0])


def table_toml(valeurs: Mapping[str, object]) -> Table:
    """Une table ; tomlkit n'en écrit pas l'en-tête si elle ne porte que des tables."""
    table = tomlkit.table()
    for cle, valeur in valeurs.items():
        if valeur is not None and valeur != []:
            table.add(cle, _rendre(valeur, cle))
    return table


def _rendre(valeur: object, cle: str) -> Item:
    """Une valeur du rapport en item tomlkit : table, tableau de tables, ou scalaire de gabarit."""
    if isinstance(valeur, Mapping):
        return table_toml(cast("Mapping[str, object]", valeur))
    if isinstance(valeur, list):
        elements = cast("list[object]", valeur)
        if elements and all(isinstance(e, Mapping) for e in elements):
            return AoT([table_toml(cast("Mapping[str, object]", e)) for e in elements])
        return tomlkit.item(toml_value(elements, cle))
    return tomlkit.item(toml_value(valeur, cle))


def ecrire(audit: Audit) -> str:
    """Le texte TOML du rapport, dans l'ordre du modèle ; un tableau vide ne s'écrit pas."""
    doc = tomlkit.document()
    for ligne in ENTETE.splitlines():
        doc.add(tomlkit.comment(ligne))
    for cle, valeur in cast("dict[str, object]", audit.model_dump(exclude_none=True)).items():
        if valeur not in ([], {}):
            doc.add(cle, _rendre(valeur, cle))
    return tomlkit.dumps(doc)


def poser(cwd: Path, slug: str, type_: Type, date: dt.date) -> Result[Path]:
    """Pose le rapport suivant du Chantier `slug`, dans le dépôt qui contient `cwd`."""
    racine = racine_git(cwd)
    if racine is None:
        return fail(f"{cwd} : hors d'un dépôt git")
    suivi = IMPLEMENTATION / f"{slug}.md"
    lu = read_item(racine / suivi)
    if not lu:
        return fail(f"Suivi de {slug} : {lu.message}")
    champs = lu.unwrap().fields
    sections = lu.unwrap().sections
    branche, base, plan = (_texte(champs, n) for n in ("branche", "base", "plan"))
    if branche is None or base is None or plan is None:
        return fail(f"{suivi} : `branche`, `base` et `plan` sont requis")
    courante = _git(racine, "branch", "--show-current")
    if not courante:
        return fail(courante.message)
    if courante.unwrap() != branche:
        return fail(f"branche {courante.unwrap()} : le Chantier {slug} s'audite sur {branche}")
    commit = _git(racine, "rev-parse", "--short", "HEAD")
    if not commit:
        return fail(commit.message)

    dossier = racine / IMPLEMENTATION / f"{slug}.audit"
    rang_avant, chemin_avant = _dernier(dossier)
    rang = rang_avant + 1
    id_audit = f"{rang:02d}-{commit.unwrap()}"
    donnees: dict[str, object] = {
        "slug": slug,
        "audit": id_audit,
        "rang": rang,
        "type": type_,
        "date": date,
        "base": base,
        "commit": commit.unwrap(),
        "suivi": str(suivi),
        "plan": plan,
        "verdict": {"valeur": PLACEHOLDER, "justification": PLACEHOLDER},
    }
    if chemin_avant is not None:
        avant = lire(chemin_avant, rempli=True)
        if not avant:
            return fail(f"le précédent n'est pas un rapport rempli :\n{avant.message}")
        dettes = avant.unwrap().dette
        donnees["precedent"] = chemin_avant.stem
        donnees["dette"] = {
            "precedente": [d.model_dump() for d in dettes.actuelle],
            "corrigee": [d.model_dump() for d in dettes.corrigee],
            "ecartee": [d.model_dump() for d in dettes.ecartee],
        }
    brief = _texte(champs, "brief")
    if brief is not None:
        lu_brief = read_item(racine / brief)
        if not lu_brief:
            return fail(f"Brief de {slug} : {lu_brief.message}")
        points = revue(lu_brief.unwrap().sections)
        if not points:
            return fail(points.message)
        donnees["brief"] = brief
        donnees["conformite"] = points.unwrap()
    donnees["verification"] = verifications(racine, sections.get(ETAPES, ""))

    try:
        audit = Audit.model_validate(donnees, strict=True, context=Mode(rempli=False))
    except ValidationError as e:
        return fail(f"rapport {id_audit} invalide, rien n'est écrit :\n{e}")
    cible = dossier / f"{id_audit}.toml"
    if cible.exists():
        return fail(f"{cible} existe déjà : un rapport ne s'écrase pas")
    dossier.mkdir(parents=True, exist_ok=True)
    cible.write_text(ecrire(audit), encoding="utf-8")
    return ok(cible)
