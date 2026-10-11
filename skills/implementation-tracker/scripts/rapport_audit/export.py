"""`audit export` : le rapport d'un audit, rendu en Markdown pour être lu.

PORTÉE : une vue, jamais une source. L'export se régénère depuis le TOML, s'écrit dans le
répertoire que l'appelant donne — un scratchpad, hors du dépôt — et ne se relit par aucune
commande. Son nom, `<slug>-<NN>-<sha>.md`, vient du rapport : l'appelant ne le compose pas.

L'ORDRE EST CELUI DU RAPPORT : l'en-tête, les vérifications, la revue du Brief, les quatre tableaux
de dettes, et le verdict en dernier, comme l'auditeur l'a rendu.
"""

from collections.abc import Sequence
from pathlib import Path

from gabarit.types import Result, fail, ok

from rapport_audit.modele import Audit, Dette, DetteCorrigee, DetteEcartee, lire

COLONNES = ("#", "Nature", "Emplacement", "Constat", "Solution", "Depuis")
SEVERITE = "Sévérité"


def _ligne(texte: str) -> str:
    """Un texte sur une ligne : un saut de ligne casserait la puce ou la cellule qui le porte."""
    return " ".join(texte.split())


def _cellule(texte: str) -> str:
    """Un texte dans une cellule de tableau, sans barre qui la fermerait."""
    return _ligne(texte).replace("|", "\\|")


def _renvoi(dette: str | None) -> str:
    return f" → {dette}" if dette else ""


def _tableau(titre: str, dettes: Sequence[Dette]) -> list[str]:
    """Un tableau de dettes ; corrigées et écartées gagnent leurs colonnes avant la sévérité."""
    lignes = [f"### {titre}", ""]
    if not dettes:
        return [*lignes, "Aucune.", ""]
    propres: tuple[str, ...] = ()
    if isinstance(dettes[0], DetteCorrigee):
        propres = ("Corrigée par", "Preuve")
    elif isinstance(dettes[0], DetteEcartee):
        propres = ("Écartée le", "Justificatif")
    entetes = (*COLONNES, *propres, SEVERITE)
    lignes += ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    for d in dettes:
        cellules = [d.id, d.nature, d.emplacement, d.constat, d.solution, d.trouvee]
        if isinstance(d, DetteCorrigee):
            cellules += [d.corrigee, d.preuve]
        elif isinstance(d, DetteEcartee):
            cellules += [d.ecartee.isoformat(), d.justificatif]
        cellules.append(d.severite)
        lignes.append("| " + " | ".join(_cellule(c) for c in cellules) + " |")
    return [*lignes, ""]


def _entete(a: Audit) -> list[str]:
    suite = f", après {a.precedent}" if a.precedent else ""
    lignes = [
        f"# Audit {a.audit} — {a.slug}",
        "",
        f"- **Type** : {a.type}",
        f"- **Date** : {a.date.isoformat()}",
        f"- **Rang** : {a.rang}{suite}",
        f"- **Commit audité** : {a.commit}, sur la base {a.base}",
        f"- **Suivi** : `{a.suivi}`",
        f"- **Plan** : `{a.plan}`",
    ]
    if a.brief:
        lignes.append(f"- **Brief** : `{a.brief}`")
    return [*lignes, ""]


def _verifications(a: Audit) -> list[str]:
    lignes = ["## Vérifications exécutées", ""]
    if not a.verification:
        return [*lignes, "Aucune.", ""]
    for v in a.verification:
        lignes += [
            f"- **{v.origine}** — {v.statut}{_renvoi(v.dette)} — `{v.commande}`",
            "",
            "  ```text",
            *(f"  {ligne}" for ligne in v.sortie.splitlines()),
            "  ```",
            "",
        ]
    return lignes


def _point(tete: str, etat: str, dette: str | None, texte: str, constat: str) -> str:
    """Un point de la revue : son état, son renvoi, le texte du Brief et le constat."""
    return f"- {tete}{etat}{_renvoi(dette)} — {_ligne(texte)} *Constat* : {_ligne(constat)}"


def _conformite(a: Audit) -> list[str]:
    c = a.conformite
    if c.est_vide():
        return ["## Conformité au Brief", "", "Chantier sans Brief.", ""]
    lignes = ["## Conformité au Brief", "", "### Critères de réussite", ""]
    lignes += [_point(f"**{x.id}** — ", x.etat, x.dette, x.critere, x.constat) for x in c.critere]
    lignes += ["", "### Hors-périmètre", ""]
    lignes += [_point("", x.etat, x.dette, x.exclusion, x.constat) for x in c.hors_perimetre]
    lignes += ["", "### Signaux de dérive", ""]
    lignes += [_point(f"**{x.id}** — ", x.etat, x.dette, x.signal, x.constat) for x in c.signal]
    if c.symptome is not None:
        s = c.symptome
        lignes += ["", "### Symptôme", "", _point("", s.etat, s.dette, s.symptome, s.constat)]
    return [*lignes, ""]


def exporter(a: Audit) -> str:
    """Le rapport en Markdown."""
    d = a.dette
    lignes = [
        *_entete(a),
        *_verifications(a),
        *_conformite(a),
        "## Dettes",
        "",
        *_tableau("Dette précédente", d.precedente),
        *_tableau("Dette actuelle", d.actuelle),
        *_tableau("Dette corrigée", d.corrigee),
        *_tableau("Dette écartée", d.ecartee),
        "## Verdict",
        "",
        f"**{a.verdict.valeur}** — {a.verdict.justification}",
    ]
    return "\n".join(lignes) + "\n"


def exporter_vers(fichier: Path, repertoire: Path) -> Result[Path]:
    """Écrit l'export dans `repertoire`, sous `<slug>-<NN>-<sha>.md`, et rend son chemin absolu."""
    lu = lire(fichier, rempli=False)
    if not lu:
        return fail(lu.message)
    a = lu.unwrap()
    cible = repertoire.resolve() / f"{a.slug}-{a.audit}.md"
    try:
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(exporter(a), encoding="utf-8")
    except OSError as e:
        return fail(f"{cible} : écriture impossible ({e.strerror})")
    return ok(cible)
