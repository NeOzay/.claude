"""`audit range` et `audit dette` : ranger une dette précédente, en ajouter une neuve.

PORTÉE : les deux seules écritures de l'auditeur qui touchent aux tableaux de dettes. Ranger copie
une dette précédente dans la Dette actuelle, corrigée ou écartée, sans que l'auditeur la recopie ;
ajouter pose une dette neuve avec son `R<n>` et `trouvee`, le reste au Marqueur, que l'auditeur
remplit par `Edit`.

LE TABLEAU `dette` EST RÉÉCRIT DEPUIS LE MODÈLE, le reste du fichier laissé tel quel : les
commentaires d'un tableau de dettes ne survivent pas, ses valeurs si.

ÉCHEC FERMÉ : le rapport doit être valide avant, et l'être encore après ; sinon rien n'est écrit.
"""

import datetime as dt
import re
from pathlib import Path
from typing import Literal

import tomlkit
from gabarit.items import read_item
from gabarit.prefill import racine_git
from gabarit.types import PLACEHOLDER, Result, fail, ok

from rapport_audit.modele import Audit, Dette, Nature, Severite, valider
from rapport_audit.pose import puces, table_toml

type Tableau = Literal["actuelle", "corrigee", "ecartee"]

# Les tableaux de dettes, dans l'ordre du modèle et de l'écriture.
TABLEAUX = ("precedente", "actuelle", "corrigee", "ecartee")
# La section du Suivi d'où se lit une dette écartée, déclarée par la Semence `suivi`, et sa ligne :
# `R<n> — justificatif — date`, une puce par dette.
DETTES_ECARTEES = "Dettes écartées"
ECARTEE = re.compile(r"^(R[1-9][0-9]*)\s+—\s+(.+)\s+—\s+([0-9]{4}-[0-9]{2}-[0-9]{2})$")


def _lire(fichier: Path) -> Result[tuple[str, Audit]]:
    try:
        texte = fichier.read_text(encoding="utf-8")
    except OSError as e:
        return fail(f"{fichier} : illisible ({e.strerror})")
    audit = valider(texte, fichier.name, rempli=False)
    if not audit:
        return fail(
            f"{fichier.name} n'est pas un rapport valide, rien n'est écrit :\n{audit.message}"
        )
    return ok((texte, audit.unwrap()))


def _ecrire(fichier: Path, texte: str, dettes: dict[str, list[dict[str, object]]]) -> Result[None]:
    """Réécrit le tableau `dette` du rapport, le verdict gardé en dernier, après validation."""
    doc = tomlkit.parse(texte)
    table = table_toml({t: dettes.get(t, []) for t in TABLEAUX})
    if "dette" in doc:
        doc["dette"] = table
    else:
        verdict = doc.item("verdict")
        doc.remove("verdict")
        doc.add("dette", table)
        doc.add("verdict", verdict)
    nouveau = tomlkit.dumps(doc)
    r = valider(nouveau, fichier.name, rempli=False)
    if not r:
        return fail(f"le rapport rangé serait invalide, rien n'est écrit :\n{r.message}")
    fichier.write_text(nouveau, encoding="utf-8")
    return ok(None)


def _tableaux(audit: Audit) -> dict[str, list[dict[str, object]]]:
    d = audit.dette
    listes: dict[str, list[Dette]] = {
        "precedente": d.precedente,
        "actuelle": d.actuelle,
        "corrigee": [*d.corrigee],
        "ecartee": [*d.ecartee],
    }
    return {t: [x.model_dump() for x in listes[t]] for t in TABLEAUX}


def ecartee(fichier: Path, suivi: str, id_: str) -> Result[tuple[str, dt.date]]:
    """Le justificatif et la date de `id_`, lus en `## Dettes écartées` du Suivi."""
    racine = racine_git(fichier.parent)
    if racine is None:
        return fail(f"{fichier} : hors d'un dépôt git, le Suivi est introuvable")
    lu = read_item(racine / suivi)
    if not lu:
        return fail(f"Suivi : {lu.message}")
    for puce in puces(lu.unwrap().sections.get(DETTES_ECARTEES, "")):
        m = ECARTEE.match(puce)
        if m is not None and m.group(1) == id_:
            try:
                return ok((m.group(2).strip(), dt.date.fromisoformat(m.group(3))))
            except ValueError:
                return fail(f"{suivi}, {DETTES_ECARTEES} : date invalide pour {id_}")
    return fail(
        f"{id_} n'est pas en `## {DETTES_ECARTEES}` de {suivi} : l'utilisateur l'y écrit, "
        f"`{id_} — justificatif — date`, avant qu'elle ne s'écarte"
    )


def ranger(fichier: Path, id_: str, vers: Tableau, preuve: str | None) -> Result[str]:
    """Range la dette précédente `id_` vers `vers`, et rend la ligne qui le dit.

    UNE DETTE DÉJÀ RANGÉE PAR CET AUDIT SE DÉPLACE : une dette précédente ne peut se trouver
    ailleurs que là où cet audit l'a mise, et le refus forcerait l'auditeur à la défaire à la main.
    """
    if (preuve is not None) != (vers == "corrigee"):
        return fail("`--preuve` est requis vers corrigee, et seulement là")
    lu = _lire(fichier)
    if not lu:
        return fail(lu.message)
    texte, audit = lu.unwrap()
    dette = next((d for d in audit.dette.precedente if d.id == id_), None)
    if dette is None:
        return fail(f"{id_} n'est pas une dette précédente de {audit.audit}")
    tableaux = _tableaux(audit)
    for t in ("actuelle", "corrigee", "ecartee"):
        tableaux[t] = [d for d in tableaux[t] if d["id"] != id_]
    rangee: dict[str, object] = dette.model_dump()
    if vers == "corrigee":
        rangee |= {"corrigee": audit.audit, "preuve": preuve}
    elif vers == "ecartee":
        lue = ecartee(fichier, audit.suivi, id_)
        if not lue:
            return fail(lue.message)
        justificatif, date = lue.unwrap()
        rangee |= {"ecartee": date, "justificatif": justificatif}
    tableaux[vers].append(rangee)
    ecrit = _ecrire(fichier, texte, tableaux)
    if not ecrit:
        return fail(ecrit.message)
    return ok(f"{id_} rangée en {vers}")


def ajouter(fichier: Path, nature: Nature, severite: Severite) -> Result[str]:
    """Ajoute à la Dette actuelle une dette neuve, et rend son `R<n>`.

    LE NUMÉRO SUIT LE PLUS HAUT DU RAPPORT : toute dette servie dans le Chantier y figure encore,
    en précédente ou dans un cumul, puisque rien ne sort ni de l'un ni des autres.
    """
    lu = _lire(fichier)
    if not lu:
        return fail(lu.message)
    texte, audit = lu.unwrap()
    tableaux = _tableaux(audit)
    servis = [int(str(d["id"])[1:]) for t in TABLEAUX for d in tableaux[t]]
    id_ = f"R{max(servis, default=0) + 1}"
    tableaux["actuelle"].append(
        {
            "id": id_,
            "nature": nature,
            "emplacement": PLACEHOLDER,
            "constat": PLACEHOLDER,
            "trouvee": audit.audit,
            "solution": PLACEHOLDER,
            "severite": severite,
        }
    )
    ecrit = _ecrire(fichier, texte, tableaux)
    if not ecrit:
        return fail(ecrit.message)
    return ok(id_)
