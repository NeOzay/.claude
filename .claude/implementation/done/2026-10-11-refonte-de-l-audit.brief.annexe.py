"""Annexe au Brief refonte-de-l-audit : les structures d'un rapport d'audit, en classes Pydantic.

PROPOSITION, PAS CODE DU DÉPÔT : ce fichier décrit le format qu'implementation-auditor remplira,
un fichier TOML par audit, `.claude/implementation/<slug>.audit/<NN>-<sha>.toml`. Il sert de
référence au Plan, et rien ne l'importe. Pydantic entrera au venv du dépôt par uv ; d'ici là,
la validation se lance par

    uv run --with pydantic python <cette annexe> <audit.toml> [<audit précédent.toml>]

DEUX MAINS : la commande pose l'en-tête, la copie de la Dette précédente, les cumuls de Dette
corrigée et de Dette écartée, et les textes repris du Brief ; l'auditeur remplit le reste, et le
verdict en dernier.

DEUX NIVEAUX DE CONTRÔLE : `Audit` vérifie ce qu'un fichier dit de lui-même ; `verifier_suite`
vérifie ce qu'il doit à l'audit précédent.
"""

import datetime as dt
import sys
import tomllib
from pathlib import Path
from typing import Annotated, ClassVar, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)

# --- Identifiants ----------------------------------------------------------------------------

type Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
type Sha = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
# Le rang sur deux chiffres, puis le SHA audité : le nom du fichier, et la colonne « Depuis ».
type IdAudit = Annotated[str, StringConstraints(pattern=r"^[0-9]{2}-[0-9a-f]{7,40}$")]
# UNIQUE DANS LE CHANTIER : un R<n> ne désigne qu'une dette, d'un audit à l'autre.
type IdDette = Annotated[str, StringConstraints(pattern=r"^R[1-9][0-9]*$")]
type IdCritere = Annotated[str, StringConstraints(pattern=r"^C[1-9][0-9]*$")]
type IdSignal = Annotated[str, StringConstraints(pattern=r"^S[1-9][0-9]*$")]
type Origine = Annotated[str, StringConstraints(pattern=r"^(Étape [1-9][0-9]*|C[1-9][0-9]*)$")]
type Texte = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

# --- Échelles --------------------------------------------------------------------------------

# L'échelle du Registre (skills/implementation-tracker/references/dette.md), sans `inconnue` —
# une dette non testable est cotée `majeur` —, plus `bloquant`, PROPRE À L'AUDIT : aucune dette
# `bloquant` n'entre au Registre. Un défaut qui rend le résultat inutilisable est `bloquant`.
type Severite = Literal["bloquant", "critique", "majeur", "avertissement", "note"]
# `alignement` : un écart au Brief ou à une décision du Journal de décisions du Suivi ;
# `qualité` : un défaut du code, son style compris ; `style` : un défaut de la documentation ou
# de la prose ; `dette induite` : un coût futur ajouté au dépôt.
type Nature = Literal["alignement", "qualité", "style", "dette induite"]
type Valeur = Literal["FAVORABLE", "RÉSERVES", "DÉFAVORABLE"]


class Strict(BaseModel):
    # Un champ inconnu est une faute de frappe de l'auditeur, pas une extension : refusé.
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)


def _rang(audit: str) -> int:
    return int(audit.split("-", 1)[0])


def _renvoi(quoi: str, en_defaut: bool, dette: str | None) -> None:
    """Un point en défaut renvoie à sa dette ; un point satisfait n'en a pas."""
    if en_defaut and dette is None:
        raise ValueError(f"{quoi} en défaut : `dette` manque")
    if not en_defaut and dette is not None:
        raise ValueError(f"{quoi} satisfait : `dette` est de trop")


# --- Vérifications exécutées -----------------------------------------------------------------


class Verification(Strict):
    origine: Origine  # l'Étape du Suivi ou le critère du Brief qui porte la commande
    commande: Texte
    statut: Literal["passée", "échouée", "non-exécutée"]
    sortie: Texte  # la sortie réelle ; `non-exécutée` : pourquoi
    # `échouée` : une dette, dont la `solution` dit quoi corriger — le code, ou la commande si
    # c'est elle qui est fausse.
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        # `non-exécutée` laisse le renvoi libre : le critère qu'elle prouvait devient
        # invérifiable, et c'est lui qui porte la dette.
        if self.statut != "non-exécutée":
            _renvoi(f"vérification {self.origine}", self.statut == "échouée", self.dette)
        return self


# --- Conformité au Brief : la revue point par point ------------------------------------------
# Chaque point est posé par la commande avec son texte du Brief ; l'auditeur remplit `etat`,
# `constat` et, en défaut, `dette`. Un point en défaut est une dette de nature `alignement`.


class Critere(Strict):
    id: IdCritere
    critere: Texte  # le texte du Brief, sans le numéro
    etat: Literal["atteint", "non-atteint", "invérifiable"]
    constat: Texte  # ce qui l'établit : la vérification qui le prouve, ou le code lu
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        _renvoi(f"critère {self.id}", self.etat != "atteint", self.dette)
        return self


class HorsPerimetre(Strict):
    exclusion: Texte  # la puce du Brief, sans sa source ; le Brief ne les numérote pas
    etat: Literal["respecté", "entamé"]
    constat: Texte  # ce qui a été regardé pour conclure : fichiers, plage du diff
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        _renvoi("hors-périmètre", self.etat == "entamé", self.dette)
        return self


class Signal(Strict):
    id: IdSignal
    signal: Texte  # le texte du Brief, sans le numéro ni la source
    etat: Literal["absent", "matérialisé"]
    constat: Texte  # ce qui a été cherché dans le diff, et où
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        _renvoi(f"signal {self.id}", self.etat == "matérialisé", self.dette)
        return self


class Symptome(Strict):
    symptome: Texte  # la ligne **Symptôme** du Brief
    etat: Literal["disparu", "persiste", "invérifiable"]
    constat: Texte  # ce qui montre que le symptôme a disparu ou non
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        _renvoi("symptôme", self.etat != "disparu", self.dette)
        return self


class Conformite(Strict):
    critere: list[Critere] = Field(default_factory=list[Critere])
    hors_perimetre: list[HorsPerimetre] = Field(default_factory=list[HorsPerimetre])
    signal: list[Signal] = Field(default_factory=list[Signal])
    symptome: Symptome | None = None  # absent : Chantier sans Brief

    def renvois(self) -> list[str]:
        points: list[Critere | HorsPerimetre | Signal | Symptome | None] = [
            *self.critere,
            *self.hors_perimetre,
            *self.signal,
            self.symptome,
        ]
        return [p.dette for p in points if p is not None and p.dette is not None]

    def est_vide(self) -> bool:
        return not (self.critere or self.hors_perimetre or self.signal or self.symptome)


# --- Dettes ----------------------------------------------------------------------------------


class Dette(Strict):
    id: IdDette
    nature: Nature
    emplacement: Texte  # `chemin:lignes`, ou `Brief, C3`
    constat: Texte
    trouvee: IdAudit  # l'audit qui l'a relevée
    solution: Texte  # comment la solder : ce qui alimente « Pour solder » au Registre
    severite: Severite  # en dernier : la dernière colonne de l'export


class DetteCorrigee(Dette):
    # Hérite de toutes les colonnes : une dette se déplace d'un tableau à l'autre en gagnant des
    # champs, sans en perdre.
    corrigee: IdAudit  # l'audit qui a constaté la correction
    preuve: Texte  # la commande et sa sortie, ou le `chemin:lignes` lu


class DetteEcartee(Dette):
    ecartee: dt.date  # la date de `## Dettes écartées` du Suivi
    justificatif: Texte  # repris de `## Dettes écartées` du Suivi


class Dettes(Strict):
    precedente: list[Dette] = Field(default_factory=list[Dette])  # posée par la commande
    actuelle: list[Dette] = Field(default_factory=list[Dette])
    corrigee: list[DetteCorrigee] = Field(default_factory=list[DetteCorrigee])  # cumul
    ecartee: list[DetteEcartee] = Field(default_factory=list[DetteEcartee])  # cumul

    @model_validator(mode="after")
    def _repartition(self) -> Self:
        rangees = [d.id for d in (*self.actuelle, *self.corrigee, *self.ecartee)]
        doublons = sorted({i for i in rangees if rangees.count(i) > 1})
        if doublons:
            raise ValueError(f"rangées dans deux tableaux : {', '.join(doublons)}")
        # Chaque dette précédente est réévaluée : elle finit dans l'un des trois autres tableaux.
        oubliees = [d.id for d in self.precedente if d.id not in rangees]
        if oubliees:
            raise ValueError(f"dettes précédentes non réévaluées : {', '.join(oubliees)}")
        return self


# --- Verdict ---------------------------------------------------------------------------------


class Verdict(Strict):
    valeur: Valeur
    justification: Texte


def verdicts_admis(actuelle: list[Dette]) -> set[Valeur]:
    """Les verdicts que la Dette actuelle autorise ; corrigées et écartées ne comptent pas."""
    severites = {d.severite for d in actuelle}
    if severites & {"bloquant", "critique"}:
        return {"DÉFAVORABLE"}
    if "majeur" in severites:
        return {"RÉSERVES"}
    # Peu d'avertissements : FAVORABLE reste possible, et la justification dit pourquoi.
    if "avertissement" in severites:
        return {"RÉSERVES", "FAVORABLE"}
    return {"FAVORABLE"}


# --- L'audit ---------------------------------------------------------------------------------


class Audit(Strict):
    # En-tête : posé par la commande, jamais par l'auditeur.
    slug: Slug
    audit: IdAudit
    rang: int = Field(ge=1, le=99)
    type: Literal["intermédiaire", "clôture"]
    date: dt.date
    base: Texte
    commit: Sha  # le HEAD de la branche au lancement
    precedent: IdAudit | None = None  # absent au premier audit
    brief: Texte | None = None  # absent : Chantier sans Brief
    suivi: Texte
    plan: Texte
    # Rempli par l'auditeur, le verdict en dernier.
    verification: list[Verification] = Field(default_factory=list[Verification])
    conformite: Conformite = Field(default_factory=Conformite)
    dette: Dettes = Field(default_factory=Dettes)
    verdict: Verdict

    @model_validator(mode="after")
    def _coherence(self) -> Self:
        constats = [*_en_tete(self), *_renvois(self), *_rangs(self)]
        admis = verdicts_admis(self.dette.actuelle)
        if self.verdict.valeur not in admis:
            constats.append(
                f"verdict {self.verdict.valeur} : la Dette actuelle n'admet que "
                + " ou ".join(sorted(admis))
            )
        if constats:
            raise ValueError(" ; ".join(constats))
        return self


def _en_tete(a: Audit) -> list[str]:
    constats: list[str] = []
    if a.audit != f"{a.rang:02d}-{a.commit}":
        constats.append(f"`audit` vaut {a.audit}, attendu {a.rang:02d}-{a.commit}")
    if (a.precedent is None) != (a.rang == 1):
        constats.append("`precedent` est requis à partir du deuxième audit, et seulement là")
    if a.brief is None and not a.conformite.est_vide():
        constats.append("une revue de conformité sans Brief")
    return constats


def _renvois(a: Audit) -> list[str]:
    constats: list[str] = []
    actuelles = {d.id: d for d in a.dette.actuelle}
    # Un critère invérifiable validé par l'utilisateur passe en Dette écartée : le renvoi tient.
    cibles = actuelles.keys() | {d.id for d in a.dette.ecartee}
    renvois = [*a.conformite.renvois(), *(v.dette for v in a.verification if v.dette)]
    constats += [f"{r} renvoyée mais ni actuelle ni écartée" for r in renvois if r not in cibles]
    # Une dette `alignement` peut aussi venir d'une décision du Suivi : le lien ne vaut que dans
    # ce sens, du point de la revue vers sa dette.
    constats += [
        f"{r} renvoyée par la revue, mais de nature `{actuelles[r].nature}`"
        for r in set(a.conformite.renvois())
        if r in actuelles and actuelles[r].nature != "alignement"
    ]
    for id_, attendue in _cotes_d_office(a).items():
        dette = actuelles.get(id_)
        if dette is not None and dette.severite != attendue:
            constats.append(f"{id_} cotée `{dette.severite}`, attendu `{attendue}` d'office")
    return constats


def _cotes_d_office(a: Audit) -> dict[str, Severite]:
    """La sévérité qu'un point en défaut impose à sa dette ; la plus grave l'emporte."""
    c = a.conformite
    # BLOQUANT D'OFFICE : les cas qui rendaient l'ancien verdict DÉFAVORABLE.
    bloquants = [
        *(x.dette for x in c.critere if x.etat == "non-atteint"),
        *(x.dette for x in c.hors_perimetre if x.etat == "entamé"),
        *(x.dette for x in c.signal if x.etat == "matérialisé"),
        *(v.dette for v in a.verification if v.statut == "échouée"),
    ]
    # Non testable : `majeur`. Un symptôme qui persiste n'impose rien, l'auditeur le cote.
    majeurs = [x.dette for x in c.critere if x.etat == "invérifiable"]
    if c.symptome is not None and c.symptome.etat == "invérifiable":
        majeurs.append(c.symptome.dette)
    cotes: dict[str, Severite] = {d: "majeur" for d in majeurs if d is not None}
    cotes.update({d: "bloquant" for d in bloquants if d is not None})
    return cotes


def _rangs(a: Audit) -> list[str]:
    constats: list[str] = []
    dettes = [*a.dette.precedente, *a.dette.actuelle, *a.dette.corrigee, *a.dette.ecartee]
    constats += [f"{d.id} trouvée après cet audit" for d in dettes if _rang(d.trouvee) > a.rang]
    constats += [
        f"{d.id} corrigée après cet audit" for d in a.dette.corrigee if _rang(d.corrigee) > a.rang
    ]
    return constats


# --- La suite des audits ---------------------------------------------------------------------


def verifier_suite(precedent: Audit, courant: Audit) -> list[str]:
    """Ce que l'audit courant doit au précédent ; une liste vide si rien ne manque."""
    constats: list[str] = []
    if courant.slug != precedent.slug:
        constats.append(f"Chantier {courant.slug}, le précédent est de {precedent.slug}")
    if courant.precedent != precedent.audit or courant.rang != precedent.rang + 1:
        constats.append(f"{courant.audit} ne suit pas {precedent.audit}")
    if courant.dette.precedente != precedent.dette.actuelle:
        constats.append("la Dette précédente n'est pas la Dette actuelle du précédent")
    # Cumuls : rien ne sort de Dette corrigée ni de Dette écartée.
    constats += [
        f"{d.id} sortie de Dette corrigée"
        for d in precedent.dette.corrigee
        if d not in courant.dette.corrigee
    ]
    constats += [
        f"{d.id} sortie de Dette écartée"
        for d in precedent.dette.ecartee
        if d not in courant.dette.ecartee
    ]
    anciennes = {d.id for d in precedent.dette.corrigee} | {d.id for d in precedent.dette.ecartee}
    connues = anciennes | {d.id for d in precedent.dette.actuelle}
    constats += [
        f"{d.id} corrigée par {d.corrigee}, attendu {courant.audit}"
        for d in courant.dette.corrigee
        if d.id not in anciennes and d.corrigee != courant.audit
    ]
    # R<n> unique dans le Chantier : une dette neuve prend un numéro jamais servi.
    plus_haut = max((int(i[1:]) for i in connues), default=0)
    for d in courant.dette.actuelle:
        if d.id in connues:
            continue
        if d.trouvee != courant.audit:
            constats.append(f"{d.id} neuve, mais trouvée par {d.trouvee}")
        if int(d.id[1:]) <= plus_haut:
            constats.append(f"{d.id} neuve, mais un numéro déjà servi dans le Chantier")
    return constats


def charger(chemin: Path) -> Audit:
    # strict : un `rang = "2"` ou une date entre guillemets est refusé, pas converti.
    return Audit.model_validate(tomllib.loads(chemin.read_text(encoding="utf-8")), strict=True)


def main(argv: list[str]) -> int:
    if len(argv) not in (1, 2):
        print("usage : <audit.toml> [<audit précédent.toml>]", file=sys.stderr)
        return 2
    try:
        courant = charger(Path(argv[0]))
        constats = verifier_suite(charger(Path(argv[1])), courant) if len(argv) == 2 else []
    except ValidationError as erreur:
        print(erreur, file=sys.stderr)
        return 1
    for constat in constats:
        print(constat, file=sys.stderr)
    return 1 if constats else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
