"""`audit new` : poser le rapport d'un audit, depuis le Suivi, le Brief, git et l'audit précédent.

PORTÉE : la commande écrit tout ce que l'auditeur n'a pas à juger — l'en-tête, la copie de la
Dette précédente, les cumuls de Dette corrigée et de Dette écartée, les points de la revue avec
leur texte du Brief —, et le Marqueur partout où il écrit. Elle ne range aucune dette et n'écrit
aucun verdict : ce sont les jugements de l'auditeur.

UN SEUL PRÉCÉDENT : le dernier rapport du répertoire, lu et exigé rempli. Les plus anciens ne se
lisent pas — le précédent porte déjà leurs cumuls.

LES SECTIONS SE LISENT PAR LEUR SEMENCE : le Contrat vient de l'estampille du Suivi et du Brief,
et `section_values` rend ce que porte chaque section structurée, ou un échec qui nomme la puce
fautive. Aucune regex ne redit ici le format d'une ligne : il est déclaré une fois, au Contrat.

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
from gabarit.commandes import ESTAMPILLE, trouver_semence
from gabarit.contract import is_marker
from gabarit.definitions import DEFS, roots
from gabarit.gitcmd import git
from gabarit.items import read_item, toml_value
from gabarit.prefill import racine_git
from gabarit.structure import Captures, Valeur, section_values
from gabarit.types import PLACEHOLDER, Contract, Result, fail, ok
from gabarit.types import Item as Fiche
from pydantic import ValidationError
from tomlkit.items import AoT, Item, Table

from rapport_audit.modele import Audit, Mode, lire

type Type = Literal["intermédiaire", "clôture"]

# Où vivent le Suivi et les rapports d'un Chantier : l'arborescence du pipeline, dans
# `skills/implementation-tracker/references/contrat.md#arborescence-et-nommage`.
IMPLEMENTATION = Path(".claude") / "implementation"
RAPPORT = re.compile(r"^([0-9]{2})-[0-9a-f]{7,40}\.toml$")

# Les sections du Brief que la revue reprend, et les captures de leurs motifs : la Semence `brief`.
INTENTION, SYMPTOME = "Intention", "Symptôme"
CRITERES = "Critères de réussite"
HORS_PERIMETRE = "Hors-périmètre"
SIGNAUX = "Signaux de dérive"
# La source qui clôt la capture de texte d'une puce, `(dit)`, `(dit ; dépôt: …)`, `(dépôt: …)`,
# point final compris : le rapport cite le texte sans elle, point gardé. Elle juge une valeur
# capturée, pas le format d'une ligne : le motif laisse la source dans la capture.
SOURCE = re.compile(r"\s*\((?:dit|dépôt\s*:)[^()]*\)(\.?)$")

# La section du Suivi qui porte les Étapes, et l'état d'une Étape faite : la Semence `suivi`.
ETAPES = "Étapes"
FAITE = "x"
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


def _sans_source(texte: object) -> str:
    return SOURCE.sub(r"\1", str(texte)).strip()


def contrat(racine: Path, fiche: Fiche, quoi: str) -> Result[Contract]:
    """Le Contrat de la Semence qu'estampille `fiche`, résolue depuis le dépôt `racine`."""
    estampille = fiche.fields.get(ESTAMPILLE)
    if not isinstance(estampille, str):
        return fail(f"{quoi} : aucune estampille « {ESTAMPILLE} »")
    semence = trouver_semence(estampille, None, roots(DEFS, cwd=racine))
    if not semence:
        return fail(f"{quoi} : {semence.message}")
    return ok(semence.unwrap().contrat)


def puces(c: Contract, fiche: Fiche, titre: str) -> Result[list[Captures]]:
    """Les captures de chaque puce d'une section à motif."""
    lu = section_values(c, fiche, titre)
    if not lu:
        return Result(lu.status, None, lu.message)
    valeurs = lu.unwrap()
    if not isinstance(valeurs, list):
        return fail(f"{fiche.path}: section « {titre} » — des labels, pas un motif")
    return ok(valeurs)


def _labels(c: Contract, fiche: Fiche, titre: str) -> Result[dict[str, Valeur]]:
    """Les labels d'une section à labels."""
    lu = section_values(c, fiche, titre)
    if not lu:
        return Result(lu.status, None, lu.message)
    valeurs = lu.unwrap()
    if not isinstance(valeurs, dict):
        return fail(f"{fiche.path}: section « {titre} » — un motif, pas des labels")
    return ok(valeurs)


def revue(c: Contract, brief: Fiche) -> Result[dict[str, object]]:
    """Les points de la revue, posés depuis les sections du Brief, `etat` et `constat` à remplir."""
    a_remplir = {"etat": PLACEHOLDER, "constat": PLACEHOLDER}
    intention = _labels(c, brief, INTENTION)
    if not intention:
        return fail(intention.message)
    lues: dict[str, list[Captures]] = {}
    for titre in (CRITERES, HORS_PERIMETRE, SIGNAUX):
        puces_lues = puces(c, brief, titre)
        if not puces_lues:
            return fail(puces_lues.message)
        lues[titre] = puces_lues.unwrap()
    conformite: dict[str, object] = {
        "critere": [
            {"id": f"C{p['n']}", "critere": _sans_source(p["critere"]), **a_remplir}
            for p in lues[CRITERES]
        ],
        "hors_perimetre": [
            {"exclusion": _sans_source(p["exclusion"]), **a_remplir} for p in lues[HORS_PERIMETRE]
        ],
        "signal": [
            {"id": f"S{p['n']}", "signal": _sans_source(p["signal"]), **a_remplir}
            for p in lues[SIGNAUX]
        ],
    }
    symptome = intention.unwrap().get(SYMPTOME)
    if isinstance(symptome, str):
        # UNE LIGNE : le formateur enroule le label, le rapport le cite d'un tenant.
        conformite["symptome"] = {"symptome": " ".join(symptome.split()), **a_remplir}
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


def verifications(racine: Path, c: Contract, suivi: Fiche) -> Result[list[dict[str, object]]]:
    """Les vérifications des Étapes faites de la section `## Étapes`, dans leur ordre."""
    etapes = puces(c, suivi, ETAPES)
    if not etapes:
        return fail(etapes.message)
    return ok(
        [
            executer(racine, f"Étape {e['n']}", str(e["verif"]))
            for e in etapes.unwrap()
            if e["etat"] == FAITE
        ]
    )


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
    fiche_suivi = lu.unwrap()
    champs = fiche_suivi.fields
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
        c_brief = contrat(racine, lu_brief.unwrap(), f"Brief de {slug}")
        if not c_brief:
            return fail(c_brief.message)
        points = revue(c_brief.unwrap(), lu_brief.unwrap())
        if not points:
            return fail(f"Brief de {slug} :\n{points.message}")
        donnees["brief"] = brief
        donnees["conformite"] = points.unwrap()
    c_suivi = contrat(racine, fiche_suivi, f"Suivi de {slug}")
    if not c_suivi:
        return fail(c_suivi.message)
    faites = verifications(racine, c_suivi.unwrap(), fiche_suivi)
    if not faites:
        return fail(f"Suivi de {slug} :\n{faites.message}")
    donnees["verification"] = faites.unwrap()

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
