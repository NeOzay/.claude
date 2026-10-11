"""Le modèle d'un rapport d'audit, en classes Pydantic, et son contrôle.

PORTÉE : un rapport par audit, `.claude/implementation/<slug>.audit/<NN>-<sha>.toml`. Ce module
dit ce qu'un rapport doit porter, et le vérifie : seul, puis contre l'audit qui le précède. Il
n'écrit aucun fichier.

DEUX MAINS : la commande pose l'en-tête, la copie de la Dette précédente, les cumuls de Dette
corrigée et de Dette écartée, et les textes repris du Brief ; l'auditeur remplit le reste, et le
verdict en dernier. Ce que l'auditeur remplit est posé au Marqueur `<À REMPLIR>`, et seul ce
qu'il remplit peut l'être : un en-tête au Marqueur est une faute.

DEUX VERDICTS, comme `gabarit check` : sans `rempli`, le Marqueur est admis, et une dette
précédente peut rester à ranger ; avec, il ne reste ni l'un ni l'autre. Les contrôles de
cohérence — renvois, cotes d'office, verdict admis — sautent un champ resté au Marqueur, et
s'appliquent donc tous à un rapport rempli. Le contexte de validation porte le mode.

DEUX NIVEAUX DE CONTRÔLE : `Audit` vérifie ce qu'un fichier dit de lui-même ; `verifier_suite`
vérifie ce qu'il doit à l'audit précédent, et rien de plus ancien : le rapport se suffit avec un
seul précédent.

LE VERDICT EST ÉCRIT PAR L'AUDITEUR. Ce module ne fait que vérifier qu'il est admis par la Dette
actuelle : `verdicts_admis` le dit d'avance, le contrôle le refuse après.
"""

import datetime as dt
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, ClassVar, Literal, Self, cast, get_args

from gabarit.contract import is_marker
from gabarit.types import PLACEHOLDER, Result, fail, ok
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    StringConstraints,
    Tag,
    ValidationError,
    ValidationInfo,
    model_validator,
)

# --- Le Marqueur -----------------------------------------------------------------------------

# Un `Literal` exige une chaîne écrite en toutes lettres : le Marqueur est donc recopié ici, et
# la garde qui suit refuse l'import le jour où il diverge de celui de gabarit, seul à le définir.
type Marqueur = Literal["<À REMPLIR>"]
# `__value__` est déclaré Any dans les stubs, comme dans `gabarit/types.py`.
if get_args(Marqueur.__value__) != (PLACEHOLDER,):  # pyright: ignore[reportAny]
    raise ImportError(f"rapport_audit : le Marqueur diverge de celui de gabarit, {PLACEHOLDER}")


# Les deux branches de `Rempli`. Leurs noms entrent dans le lieu d'une faute, que `_fautes` en
# retire : AUCUN CHAMP NE PEUT LES PORTER, sans quoi son nom disparaîtrait du lieu.
VALEUR, AU_MARQUEUR = "rempli", "au-marqueur"


def _branche(valeur: object) -> str:
    return AU_MARQUEUR if valeur == PLACEHOLDER else VALEUR


# CE QUE L'AUDITEUR REMPLIT : une valeur, ou le Marqueur. Le discriminant choisit la branche
# d'avance : une valeur fautive ne reçoit que le refus de son type, pas celui du Marqueur en plus.
type Rempli[T] = Annotated[
    Annotated[T, Tag(VALEUR)] | Annotated[Marqueur, Tag(AU_MARQUEUR)],
    Discriminator(_branche),
]


def _pas_un_marqueur(texte: str) -> str:
    if is_marker(texte):
        raise ValueError(f"« {texte} » : seul {PLACEHOLDER} se pose, là où l'auditeur écrit")
    return texte


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
# UN TEXTE N'EST JAMAIS UN MARQUEUR : sans ce refus, `<À REMPLIR>` passerait pour un texte écrit.
type Texte = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1), AfterValidator(_pas_un_marqueur)
]

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

# Les mêmes, énumérables, pour les options d'`audit dette`. `__value__` d'un alias est déclaré Any
# dans les stubs, comme dans `gabarit/types.py` : le cast rétablit ce que l'alias affirme.
SEVERITES: tuple[Severite, ...] = cast(
    "tuple[Severite, ...]",
    get_args(Severite.__value__),  # pyright: ignore[reportAny]
)
NATURES: tuple[Nature, ...] = cast(
    "tuple[Nature, ...]",
    get_args(Nature.__value__),  # pyright: ignore[reportAny]
)


@dataclass(frozen=True)
class Mode:
    """Le contexte de validation : `rempli` refuse tout Marqueur restant."""

    rempli: bool


def _rempli(info: ValidationInfo) -> bool:
    mode = cast("object", info.context)
    return isinstance(mode, Mode) and mode.rempli


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
    """Une commande exécutée par `audit new` ; l'auditeur la juge et renvoie à sa dette."""

    origine: Origine  # l'Étape du Suivi ou le critère du Brief qui porte la commande
    commande: Texte
    statut: Literal["passée", "échouée", "non-exécutée"]
    sortie: Texte  # la sortie réelle ; `non-exécutée` : pourquoi
    # `échouée` : une dette, dont la `solution` dit quoi corriger — le code, ou la commande si
    # c'est elle qui est fausse. Posée au Marqueur : la commande ne connaît pas le R<n>.
    dette: Rempli[IdDette] | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        # `non-exécutée` laisse le renvoi libre : le critère qu'elle prouvait devient
        # invérifiable, et c'est lui qui porte la dette.
        if self.statut != "non-exécutée" and self.dette != PLACEHOLDER:
            _renvoi(f"vérification {self.origine}", self.statut == "échouée", self.dette)
        return self


# --- Conformité au Brief : la revue point par point ------------------------------------------
# Chaque point est posé par la commande avec son texte du Brief ; l'auditeur remplit `etat`,
# `constat` et, en défaut, `dette`. Un point en défaut est une dette de nature `alignement`.


class Critere(Strict):
    """Un critère de réussite du Brief, et s'il est atteint."""

    id: IdCritere
    critere: Texte  # le texte du Brief, sans le numéro
    etat: Rempli[Literal["atteint", "non-atteint", "invérifiable"]]
    constat: Rempli[Texte]  # ce qui l'établit : la vérification qui le prouve, ou le code lu
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        if self.etat != PLACEHOLDER:
            _renvoi(f"critère {self.id}", self.etat != "atteint", self.dette)
        return self


class HorsPerimetre(Strict):
    """Une exclusion du Brief, et si le diff l'a entamée."""

    exclusion: Texte  # la puce du Brief, sans sa source ; le Brief ne les numérote pas
    etat: Rempli[Literal["respecté", "entamé"]]
    constat: Rempli[Texte]  # ce qui a été regardé pour conclure : fichiers, plage du diff
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        if self.etat != PLACEHOLDER:
            _renvoi("hors-périmètre", self.etat == "entamé", self.dette)
        return self


class Signal(Strict):
    """Un Signal de dérive du Brief, et s'il s'est matérialisé."""

    id: IdSignal
    signal: Texte  # le texte du Brief, sans le numéro ni la source
    etat: Rempli[Literal["absent", "matérialisé"]]
    constat: Rempli[Texte]  # ce qui a été cherché dans le diff, et où
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        if self.etat != PLACEHOLDER:
            _renvoi(f"signal {self.id}", self.etat == "matérialisé", self.dette)
        return self


class Symptome(Strict):
    """Le symptôme du Brief, et s'il a disparu."""

    symptome: Texte  # la ligne **Symptôme** du Brief
    etat: Rempli[Literal["disparu", "persiste", "invérifiable"]]
    constat: Rempli[Texte]  # ce qui montre que le symptôme a disparu ou non
    dette: IdDette | None = None

    @model_validator(mode="after")
    def _lien(self) -> Self:
        if self.etat != PLACEHOLDER:
            _renvoi("symptôme", self.etat != "disparu", self.dette)
        return self


class Conformite(Strict):
    """La revue du Brief point par point ; vide pour un Chantier sans Brief."""

    critere: list[Critere] = Field(default_factory=list[Critere])
    hors_perimetre: list[HorsPerimetre] = Field(default_factory=list[HorsPerimetre])
    signal: list[Signal] = Field(default_factory=list[Signal])
    symptome: Symptome | None = None  # absent : Chantier sans Brief

    def renvois(self) -> list[str]:
        """Les dettes auxquelles renvoie un point de la revue."""
        points: list[Critere | HorsPerimetre | Signal | Symptome | None] = [
            *self.critere,
            *self.hors_perimetre,
            *self.signal,
            self.symptome,
        ]
        return [p.dette for p in points if p is not None and p.dette is not None]

    def est_vide(self) -> bool:
        """Vrai si la revue ne porte aucun point."""
        return not (self.critere or self.hors_perimetre or self.signal or self.symptome)


# --- Dettes ----------------------------------------------------------------------------------


class Dette(Strict):
    """Une dette relevée par un audit ; `id` et `trouvee` sont posés par `audit dette`."""

    id: IdDette
    nature: Rempli[Nature]
    emplacement: Rempli[Texte]  # `chemin:lignes`, ou `Brief, C3`
    constat: Rempli[Texte]
    trouvee: IdAudit  # l'audit qui l'a relevée
    solution: Rempli[Texte]  # comment la solder : ce qui alimente « Pour solder » au Registre
    severite: Rempli[Severite]  # en dernier : la dernière colonne de l'export


class DetteCorrigee(Dette):
    """Une dette dont un audit a constaté la correction."""

    # Hérite de toutes les colonnes : une dette se déplace d'un tableau à l'autre en gagnant des
    # champs, sans en perdre.
    corrigee: IdAudit  # l'audit qui a constaté la correction
    preuve: Texte  # la commande et sa sortie, ou le `chemin:lignes` lu


class DetteEcartee(Dette):
    """Une dette écartée par l'utilisateur, en `## Dettes écartées` du Suivi."""

    ecartee: dt.date  # la date de `## Dettes écartées` du Suivi
    justificatif: Texte  # repris de `## Dettes écartées` du Suivi


class Dettes(Strict):
    """Les quatre tableaux : la précédente se range dans l'un des trois autres."""

    precedente: list[Dette] = Field(default_factory=list[Dette])  # posée par la commande
    actuelle: list[Dette] = Field(default_factory=list[Dette])
    corrigee: list[DetteCorrigee] = Field(default_factory=list[DetteCorrigee])  # cumul
    ecartee: list[DetteEcartee] = Field(default_factory=list[DetteEcartee])  # cumul

    @model_validator(mode="after")
    def _repartition(self, info: ValidationInfo) -> Self:
        rangees = [d.id for d in (*self.actuelle, *self.corrigee, *self.ecartee)]
        doublons = sorted({i for i in rangees if rangees.count(i) > 1})
        if doublons:
            raise ValueError(f"rangées dans deux tableaux : {', '.join(doublons)}")
        # Chaque dette précédente est réévaluée : elle finit dans l'un des trois autres tableaux.
        # Au rapport posé, aucune ne l'est encore : le rangement est un remplissage.
        oubliees = [d.id for d in self.precedente if d.id not in rangees]
        if oubliees and _rempli(info):
            raise ValueError(f"dettes précédentes non réévaluées : {', '.join(oubliees)}")
        return self


# --- Verdict ---------------------------------------------------------------------------------


class Verdict(Strict):
    """Le verdict de l'auditeur, rendu en dernier."""

    valeur: Rempli[Valeur]
    justification: Rempli[Texte]


def verdicts_admis(actuelle: list[Dette]) -> set[Valeur] | None:
    """Les verdicts que la Dette actuelle autorise ; corrigées et écartées ne comptent pas.

    Returns:
        None tant qu'une sévérité au Marqueur peut encore changer l'ensemble.
    """
    severites = {d.severite for d in actuelle}
    if severites & {"bloquant", "critique"}:
        return {"DÉFAVORABLE"}
    if PLACEHOLDER in severites:
        return None
    if "majeur" in severites:
        return {"RÉSERVES"}
    # Peu d'avertissements : FAVORABLE reste possible, et la justification dit pourquoi.
    if "avertissement" in severites:
        return {"RÉSERVES", "FAVORABLE"}
    return {"FAVORABLE"}


# --- L'audit ---------------------------------------------------------------------------------


class Audit(Strict):
    """Un rapport d'audit : l'en-tête posé par la commande, le reste par l'auditeur."""

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
    def _coherence(self, info: ValidationInfo) -> Self:
        constats = [*_en_tete(self), *_renvois(self), *_rangs(self)]
        admis = verdicts_admis(self.dette.actuelle)
        if admis is not None and self.verdict.valeur not in {*admis, PLACEHOLDER}:
            constats.append(
                f"verdict {self.verdict.valeur} : la Dette actuelle n'admet que "
                + " ou ".join(sorted(admis))
            )
        if _rempli(info):
            constats += [f"{lieu} : à remplir" for lieu in marqueurs(self)]
        if constats:
            raise ValueError("\n".join(constats))
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
    renvois = [
        *a.conformite.renvois(),
        *(v.dette for v in a.verification if v.dette is not None and v.dette != PLACEHOLDER),
    ]
    constats += [f"{r} renvoyée mais ni actuelle ni écartée" for r in renvois if r not in cibles]
    # Une dette `alignement` peut aussi venir d'une décision du Suivi : le lien ne vaut que dans
    # ce sens, du point de la revue vers sa dette.
    constats += [
        f"{r} renvoyée par la revue, mais de nature `{actuelles[r].nature}`"
        for r in sorted(set(a.conformite.renvois()))
        if r in actuelles and actuelles[r].nature not in {"alignement", PLACEHOLDER}
    ]
    for id_, attendue in _cotes_d_office(a).items():
        dette = actuelles.get(id_)
        if dette is not None and dette.severite not in {attendue, PLACEHOLDER}:
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
    cotes.update({d: "bloquant" for d in bloquants if d is not None and d != PLACEHOLDER})
    return cotes


def _rangs(a: Audit) -> list[str]:
    constats: list[str] = []
    dettes = [*a.dette.precedente, *a.dette.actuelle, *a.dette.corrigee, *a.dette.ecartee]
    constats += [f"{d.id} trouvée après cet audit" for d in dettes if _rang(d.trouvee) > a.rang]
    constats += [
        f"{d.id} corrigée après cet audit" for d in a.dette.corrigee if _rang(d.corrigee) > a.rang
    ]
    return constats


def marqueurs(modele: BaseModel, lieu: str = "") -> list[str]:
    """Où le Marqueur reste posé : `verdict.valeur`, `dette.actuelle[R3].severite`."""
    trouves: list[str] = []
    for nom in type(modele).model_fields:
        valeur = cast("object", getattr(modele, nom))
        ici = f"{lieu}.{nom}" if lieu else nom
        if valeur == PLACEHOLDER:
            trouves.append(ici)
        elif isinstance(valeur, BaseModel):
            trouves += marqueurs(valeur, ici)
        elif isinstance(valeur, list):
            for i, element in enumerate(cast("list[object]", valeur)):
                if isinstance(element, BaseModel):
                    trouves += marqueurs(element, f"{ici}[{_designation(element, i)}]")
    return trouves


def _designation(element: BaseModel, rang: int) -> str:
    """Un élément de tableau par son `id` ou son `origine`, sinon par son rang à partir de 1."""
    for nom in ("id", "origine"):
        valeur = cast("object", getattr(element, nom, None))
        if isinstance(valeur, str):
            return valeur
    return str(rang + 1)


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


# --- Lecture et contrôle d'un fichier --------------------------------------------------------


def _fautes(erreur: ValidationError) -> list[str]:
    """Une ligne par faute, située dans le rapport, sans le préfixe anglais de Pydantic."""
    lignes: list[str] = []
    for e in erreur.errors():
        lieu = ".".join(
            f"[{p + 1}]" if isinstance(p, int) else p
            for p in e["loc"]
            if p not in (VALEUR, AU_MARQUEUR)
        ).replace(".[", "[")
        message = e["msg"].removeprefix("Value error, ")
        lignes += [f"{lieu} : {m}" if lieu else m for m in message.split("\n")]
    return lignes


def valider(texte: str, nom: str, rempli: bool) -> Result[Audit]:
    """Le texte d'un rapport validé, ou ses fautes, une par ligne, préfixées de `nom`."""
    try:
        donnees = tomllib.loads(texte)
    except tomllib.TOMLDecodeError as e:
        return fail(f"{nom} : TOML invalide ({e})")
    try:
        # strict : un `rang = "2"` ou une date entre guillemets est refusé, pas converti.
        audit = Audit.model_validate(donnees, strict=True, context=Mode(rempli))
    except ValidationError as e:
        return fail("\n".join(f"{nom} : {f}" for f in _fautes(e)))
    return ok(audit)


def lire(chemin: Path, rempli: bool) -> Result[Audit]:
    """Le rapport lu et validé, ou ses fautes, une par ligne."""
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as e:
        return fail(f"{chemin} : illisible ({e.strerror})")
    return valider(texte, chemin.name, rempli)


def controler(chemin: Path, rempli: bool) -> Result[Audit]:
    """Le rapport, contrôlé seul puis contre son précédent, rangé à côté de lui.

    Le précédent est celui que nomme `precedent`, et lui seul : sa propre suite a été contrôlée
    à son tour, et la remonter ici relirait tout le Chantier.
    """
    lu = lire(chemin, rempli)
    if not lu:
        return fail(lu.message)
    audit = lu.unwrap()
    if chemin.stem != audit.audit:
        return fail(f"{chemin.name} : le fichier d'un audit se nomme {audit.audit}.toml")
    if audit.precedent is None:
        return ok(audit)
    avant = lire(chemin.with_name(f"{audit.precedent}.toml"), rempli=False)
    if not avant:
        return fail(f"précédent {audit.precedent} :\n{avant.message}")
    constats = verifier_suite(avant.unwrap(), audit)
    if constats:
        return fail("\n".join(f"{chemin.name} : {c}" for c in constats))
    return ok(audit)
