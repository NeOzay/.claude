"""Les rapports d'une liste avec la semence qui l'a produite.

CE MODULE N'ÉCRIT RIEN ET NE DÉCIDE RIEN. Il compare, et rend des phrases. Ce qui
en découle — refuser, réécrire, sauvegarder — est le travail de `reseed`.

POURQUOI DES AVERTISSEMENTS, ET PAS DES MANQUEMENTS. Une liste dont la semence a
évolué n'a AUCUN élément fautif : ses éléments sont conformes au contrat qu'elle
porte, et c'est ce contrat que les commandes appliquent. Faire échouer `validate`
pour ça reviendrait à déclarer invalide une liste parfaitement en règle. Un
avertissement dit ce qu'aucune commande ne peut trancher à la place de l'utilisateur :
la définition a bougé, à lui de voir.

TROIS SILENCES, ET ILS NE DISENT PAS LA MÊME CHOSE :

  - `def = false`      cette liste n'a pas de semence, il n'y a rien à rattraper
  - `frozen = true`    elle a délibérément pris la main, on ne le lui rappelle plus
  - pas de `.list/semence/`  on ne sait pas ce qui a été semé : on se tait sur la
                             modification locale, jamais sur la péremption

L'ABSENCE DE TABLE `[origin]`, ELLE, N'EST PAS UN SILENCE : c'est l'état d'une liste
antérieure à ce dispositif, et le seul moyen qu'elle a d'être retrouvée est qu'on le
dise.
"""

from __future__ import annotations

import shutil
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast, final

from .contract import (
    BACKUP,
    CONTRACT,
    SEED,
    TEMPLATES,
    list_base,
    load_contract,
    load_source,
    parse_contract,
)
from .definitions import resolve, roots
from .items import ESCAPES, SerialiseError, dump_value
from .types import Contract, Result, fail, ok


def seed_base(list_dir: Path) -> Path:
    """Le répertoire de la semence intacte. Il a la forme d'une définition."""
    return list_base(list_dir) / SEED


def warnings(list_dir: Path, contract: Contract) -> list[str]:
    """Ce qu'il y a à dire sur la provenance de cette liste. Vide = rien à signaler.

    L'ORDRE EST CELUI DE LA LECTURE, du plus décisif au plus fin : d'abord ce qui
    empêche de vérifier quoi que ce soit, ensuite l'écart de version, enfin les
    fichiers modifiés sur place.
    """
    origin = contract.origin
    if origin is None:
        return [
            f"{list_dir} : aucune provenance déclarée — "
            "« list-dir reseed <liste> --def <nom> » pour l'adopter, "
            "ou « def = false » sous [origin] si cette liste n'a pas de semence"
        ]
    if origin.name is None or origin.frozen:
        return []

    return _peremption(list_dir, origin.name, origin.version) + _modifications(list_dir)


def _peremption(list_dir: Path, nom: str, version: int) -> list[str]:
    """L'écart de version avec la définition, quand elle est joignable.

    INTROUVABLE N'EST PAS UNE FAUTE, mais ne peut pas non plus se taire : sur une
    machine où le skill qui porte la définition n'est pas installé, la péremption
    devient invérifiable, et le lecteur doit savoir que le silence des lignes
    suivantes ne prouve rien.
    """
    trouve = resolve(nom, roots())
    if not trouve:
        return [
            f"{list_dir} : semée par « {nom} », définition introuvable dans les quatre "
            "rangs — péremption invérifiable (« list-dir defs » montre ce qui est visible)"
        ]

    definition = trouve.unwrap()
    lu = load_source(definition)
    if not lu:
        return [f"{list_dir} : semence « {nom} » illisible — {lu.message}"]

    _, _, semence = lu.unwrap()
    if semence.origin is None or semence.origin.name is None:
        return [
            f"{definition / CONTRACT} : la semence ne déclare pas de provenance — "
            f"péremption de {list_dir} invérifiable"
        ]

    courante = semence.origin.version
    if courante > version:
        return [
            f"{list_dir} : contrat périmé — semé en v{version}, « {nom} » est en "
            f"v{courante} ; « list-dir reseed {list_dir} » rattrape"
        ]
    if courante < version:
        # Une liste en avance sur sa semence : personne n'a pu l'écrire en semant.
        # Le dire tel quel plutôt que d'inventer une cause.
        return [
            f"{list_dir} : semée en v{version}, mais « {nom} » n'est qu'en v{courante} — "
            "état anormal, l'une des deux versions a été écrite à la main"
        ]
    return []


def _modifications(list_dir: Path) -> list[str]:
    """Les fichiers qui ont bougé depuis le semis, contrat et gabarits.

    NE RÉSOUT AUCUNE DÉFINITION : la comparaison se fait avec `.list/semence/`, donc
    elle vaut encore là où rien n'est installé. Sans ce répertoire — liste adoptée
    ou semée avant lui — on ne sait pas ce qui a été semé, et on se tait.
    """
    base = seed_base(list_dir)
    if not (base / CONTRACT).is_file():
        return []

    dits: list[str] = []
    for relatif in _fichiers(base) | _fichiers(list_base(list_dir)):
        semé, vif = base / relatif, list_base(list_dir) / relatif
        if not vif.is_file():
            dits.append(f"{vif} : retiré depuis le semis")
        elif not semé.is_file():
            dits.append(f"{vif} : ajouté depuis le semis")
        elif _differe(semé, vif, contrat=relatif == CONTRACT):
            dits.append(f"{vif} : modifié localement depuis le semis")
    return sorted(dits)


def _differe(semé: Path, vif: Path, *, contrat: bool) -> bool:
    """Deux fichiers diffèrent-ils par ce qu'ils DISENT, et non par leur mise en page.

    LE CONTRAT SE COMPARE SUR SON CONTENU, jamais sur ses octets : un re-semis qui a
    dû réémettre le contrat en perd les commentaires et peut recomposer une écriture
    équivalente. Comparer les textes ferait alors dire « modifié localement » pour
    toujours, sur une liste que personne n'a touchée — un avertissement permanent
    qu'on apprend à ignorer, et qui emporte les vrais avec lui.

    UN GABARIT, LUI, SE COMPARE À L'OCTET. C'est une prose libre : elle n'a pas de
    contenu déclaré dont on pourrait faire abstraction de la forme, et deux mises en
    page différentes y sont deux textes différents.
    """
    gauche, droite = _lire(semé), _lire(vif)
    if gauche is None or droite is None:
        return True
    if not contrat:
        return gauche != droite
    try:
        return flatten(tomllib.loads(gauche)) != flatten(tomllib.loads(droite))
    except tomllib.TOMLDecodeError:
        # Un contrat illisible est un problème que `validate` nommera ailleurs, et
        # d'ici on ne peut que constater qu'il ne dit pas la même chose que l'autre.
        return True


def _fichiers(base: Path) -> set[str]:
    """Le contrat et les gabarits d'une base, en chemins relatifs.

    RIEN D'AUTRE N'EST COMPARÉ : `commands/`, `semence/` et `backup/` ne viennent pas
    d'une définition, et les faire figurer ferait dire « ajouté depuis le semis » à
    tout ce qu'une liste range légitimement chez elle.
    """
    trouves = {CONTRACT} if (base / CONTRACT).is_file() else set()
    return trouves | {
        f"{TEMPLATES}/{f.name}" for f in sorted((base / TEMPLATES).glob("*")) if f.is_file()
    }


def _lire(path: Path) -> str | None:
    """Le texte, ou None si le fichier est illisible — un illisible diffère de tout."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def read_seed(definition: Path) -> Result[tuple[str, dict[str, str], Contract]]:
    """Le contrat d'une définition et ses gabarits, LUS ET VALIDÉS EN MÉMOIRE.

    UN SEUL LECTEUR POUR LES DEUX APPELANTS : `init` sème avec, `reseed` rattrape
    avec. Deux lectures séparées finiraient par juger différemment le même
    répertoire — l'une acceptant ce que l'autre refuse.

    Rien n'est écrit ici, et c'est le point : un contrat de définition invalide
    découvert après un mkdir laisserait une liste à moitié bâtie, que la tentative
    suivante refuserait comme « contrat déjà présent ». L'appelant serait coincé
    entre une erreur qu'il a corrigée et un répertoire qu'il n'a pas créé — c'est
    la raison pour laquelle `derive` construit lui aussi tout en mémoire d'abord.
    """
    contrat = definition / CONTRACT
    if not contrat.is_file():
        return fail(f"{definition}: définition sans contrat — {CONTRACT} attendu")
    try:
        texte = contrat.read_text(encoding="utf-8")
        gabarits = {
            f.name: f.read_text(encoding="utf-8")
            for f in sorted((definition / TEMPLATES).glob("*"))
            if f.is_file()
        }
    except OSError as exc:
        return fail(f"{definition}: définition illisible — {exc.strerror}")

    # Le contrat est jugé ici, pas à la première commande qui ouvrira la liste :
    # une définition fautive doit se dire au moment où on s'en sert, en nommant le
    # fichier de la DÉFINITION, et non plus tard en nommant la copie.
    lu = parse_contract(texte, contrat)
    if not lu:
        return Result(lu.status, None, lu.message)
    return ok((texte, gabarits, lu.unwrap()))


# ------------------------------------------------------ aplatir, fusionner, réécrire
MISSING = object()
"""L'absence d'une clé, distincte de toute valeur qu'elle pourrait porter. `None` ne
conviendrait pas : `tomllib` ne produit jamais None, mais un jour où il le ferait,
une clé écrite se lirait comme une clé absente."""


def flatten(raw: Mapping[str, object]) -> dict[str, object]:
    """Un contrat TOML en clés pointées : `fields.date.required`, `origin.version`.

    L'APLATISSEMENT PORTE SUR LE TEXTE LU, PAS SUR LE `Contract` PARSÉ. Le parseur
    remplit les défauts — `required = false`, `description = ""` — et une clé absente
    y devient indiscernable d'une clé écrite à sa valeur par défaut. La fusion, elle,
    a précisément besoin de cette différence : une clé absente localement et présente
    dans la semence est un apport, une clé écrite des deux côtés à deux valeurs est
    un conflit.

    LES TITRES DE SECTION SONT DES PHRASES : `sections."Pour solder".required`. Les
    guillemets ne sont pas décoratifs, ils font partie de la clé et de son écriture.

    AUCUN NOM N'ENTRE ICI SANS PASSER PAR `_cle` OU `_titre`, à quelque étage qu'il se
    trouve — premier niveau, table, clé terminale. `parse_contract` ne refuse une clé
    inconnue qu'à l'intérieur d'`[origin]` : partout ailleurs, un nom écrit à la main
    traverse la lecture et revient à l'écriture. Un seul étage oublié suffisait à
    réémettre `ma cle = "x"`, que `tomllib` refuse, ou `note.libre = "y"`, qui crée une
    table que personne n'a écrite — et celle-là traverse `validate` sans un mot.
    """
    plat: dict[str, object] = {}
    for cle, valeur in raw.items():
        if cle in ("fields", "sections") and isinstance(valeur, dict):
            for nom, corps in cast("dict[str, object]", valeur).items():
                # UN TITRE DE SECTION EST TOUJOURS CITÉ, un nom de champ jamais.
                # `[sections.Constat]` est un TOML équivalent à `[sections."Constat"]`
                # mais un OCTET différent : un contrat réémis cessait d'égaler sa
                # semence pour cette seule raison, et l'avertissement « modifié
                # localement » devenait permanent.
                prefixe = f"{cle}.{_titre(nom) if cle == 'sections' else _cle(nom)}"
                if isinstance(corps, dict):
                    for sous, v in cast("dict[str, object]", corps).items():
                        plat[f"{prefixe}.{_cle(sous)}"] = v
                else:
                    plat[prefixe] = corps
        elif cle == "origin" and isinstance(valeur, dict):
            for sous, v in cast("dict[str, object]", valeur).items():
                plat[f"origin.{_cle(sous)}"] = v
        else:
            plat[_cle(cle)] = valeur
    return plat


def _cle(nom: str) -> str:
    """Un nom de table : nu s'il est un jeton simple, cité et ÉCHAPPÉ sinon.

    ENROBER NE SUFFIT PAS. Un titre portant un guillemet droit — « Un " ici » —
    produisait `[sections."Un " ici"]` : `reseed` l'écrivait et rendait 0, et c'est le
    `validate` suivant qui découvrait un contrat que `tomllib` refuse. Un fichier
    détruit sous un succès annoncé est le mode d'échec ouvert que ce paquet existe
    pour supprimer, et l'écriture n'y fait pas exception.

    LES MÊMES ÉCHAPPEMENTS QUE `dump_value`, empruntés à `items.ESCAPES` plutôt que
    recopiés : une clé citée et une valeur citée obéissent à la même grammaire TOML,
    et deux tables d'échappement qui se ressemblent finissent par diverger.
    """
    if nom and nom.replace("-", "").replace("_", "").isalnum():
        return nom
    return _titre(nom)


def _titre(nom: str) -> str:
    """Le même, toujours cité : un titre de section est une phrase, pas un jeton.

    LE CITER TOUJOURS EST CE QUI GARDE L'OCTET. `[sections.Constat]` est un TOML
    équivalent à `[sections."Constat"]` mais un fichier différent, et un contrat
    réémis cessait pour cette seule raison d'égaler la semence dont il sortait.

    IL ÉCHAPPE MAIS NE REFUSE RIEN, et c'est un partage, pas un oubli : une clé plate
    est une ADRESSE, et `flatten` l'établit pour comparer deux contrats — y compris
    quand l'un des deux est fautif, ce qu'un avertissement doit pouvoir dire au lieu
    de sortir par une exception. Le refus appartient à `emit`, qui écrit.
    """
    echappe = nom.replace("\\", "\\\\").replace('"', '\\"')
    for brut, remplace in ESCAPES.items():
        echappe = echappe.replace(brut, remplace)
    return f'"{echappe}"'


def _refus(cle: str) -> str:
    """La raison de ne pas écrire cette clé, ou une chaîne vide.

    LE MÊME REFUS QUE `dump_value` SUR UNE VALEUR, appliqué au nom : un caractère de
    contrôle produit un en-tête ou une affectation que `tomllib` rejette, et le contrat
    était écrit quand même, sous un code 0. En-tête de table COMME clé terminale — la
    seconde vient d'un contrat écrit à la main, où `parse_contract` tolère une clé
    inconnue dans un `[fields.*]`.
    """
    illegal = next((c for c in cle if ord(c) < 0x20 or ord(c) == 0x7F), None)
    if illegal is None:
        return ""
    # LA CLÉ EST CITÉE ÉCHAPPÉE. Recopiée telle quelle, elle rendait « clé « macle » »
    # pour `ma\x07cle` : le caractère fautif était invisible dans le message même qui
    # le dénonce, et le lecteur cherchait une clé qui n'existe pas.
    montrable = "".join(f"\\u{ord(c):04X}" if ord(c) < 0x20 or ord(c) == 0x7F else c for c in cle)
    return f"contrat inécrivable — clé « {montrable} » : caractère de contrôle U+{ord(illegal):04X}"


def _couper(cle: str) -> tuple[str, str]:
    """Une clé plate en (table, clé terminale), SANS SE FAIRE PIÉGER PAR UN POINT CITÉ.

    Couper sur le dernier point est faux dès qu'un nom en contient un : la clé
    `fields.id."note.libre"` se serait scindée en `fields.id."note` et `libre"`, et le
    contrat réémis aurait porté une table `[fields.id.note]` que personne n'a écrite —
    une corruption qui traverse `validate` sans un mot, puisque le fichier obtenu est
    du TOML parfaitement valide.

    Les noms cités sont produits par `_cle` et `_titre`, qui échappent le guillemet :
    un `"` précédé d'un nombre PAIR de contre-obliques ferme donc la citation.
    """
    segments: list[str] = []
    courant: list[str] = []
    cite = False
    echappes = 0
    for c in cle:
        if c == '"' and echappes % 2 == 0:
            cite = not cite
        echappes = echappes + 1 if c == "\\" else 0
        if c == "." and not cite:
            segments.append("".join(courant))
            courant = []
            continue
        courant.append(c)
    segments.append("".join(courant))
    return ".".join(segments[:-1]), segments[-1]


def emit(plat: Mapping[str, object]) -> Result[str]:
    """Le contrat réécrit depuis ses clés pointées, dans l'ordre où elles arrivent.

    L'ORDRE DE LA MAPPING EST L'ORDRE DU FICHIER, et c'est à l'appelant de le poser :
    la fusion range la semence d'abord, les clés propres au local ensuite, pour qu'un
    contrat rattrapé se relise comme sa définition.

    LES COMMENTAIRES NE SURVIVENT PAS, et c'est pourquoi `reseed` ne passe par ici
    qu'en cas de divergence réelle : sans divergence, il recopie la semence telle
    quelle, commentaires compris.

    IL REND UN RESULT PARCE QUE CE QU'IL PRODUIT EST ÉCRIT. Le sérialiseur refuse ce
    qu'aucune écriture TOML sur une ligne ne porte — un flottant, un caractère de
    contrôle — et ce refus arrivait ici par une exception : `reseed` sortait alors par
    un traceback, ou pire, écrivait un fichier que `tomllib` rejette en rendant 0. Un
    échec nommé, avant toute écriture, est la seule forme que ce paquet accepte.
    """
    tables: dict[str, list[tuple[str, object]]] = {"": []}
    for cle, valeur in plat.items():
        tete, feuille = _couper(cle)
        tables.setdefault(tete, []).append((feuille, valeur))

    morceaux: list[str] = []
    try:
        for entete, paires in tables.items():
            if entete:
                refus = _refus(entete)
                if refus:
                    return fail(refus)
                morceaux.append(f"[{entete}]")
            for feuille, v in paires:
                if isinstance(v, dict):
                    # `dump_value` dirait « champ … : type dict hors contrat » : le mot
                    # est faux et la sortie tue. Une table de premier niveau que le
                    # contrat ne déclare pas traverse `parse_contract` et `validate`,
                    # mais rend tout re-semis impossible tant qu'elle est là — le dire.
                    ou = f"{entete}.{feuille}" if entete else feuille
                    return fail(
                        f"contrat inécrivable — table « {ou} » : le contrat ne déclare "
                        "que « fields », « sections » et « origin ». La retirer du "
                        "contrat de la liste, ou de la semence, débloque le re-semis."
                    )
                # LA CLÉ TERMINALE PASSE LE MÊME CONTRÔLE QUE L'EN-TÊTE. Elle vient
                # d'un contrat écrit à la main, où `parse_contract` tolère une clé
                # inconnue dans un `[fields.*]` : `ma cle = "x"` s'y écrivait brute, et
                # le contrat réémis n'était plus du TOML. `dump_value` ne juge que la
                # VALEUR — le nom ne lui sert qu'à se nommer dans son message.
                refus = _refus(feuille)
                if refus:
                    return fail(refus)
                morceaux.append(f"{feuille} = {dump_value(v, feuille)}")
            morceaux.append("")
    except SerialiseError as exc:
        return fail(f"contrat inécrivable — {exc}")
    return ok("\n".join(morceaux).rstrip("\n") + "\n")


@final
@dataclass(frozen=True)
class Fusion:
    """Ce qu'une fusion a produit, et ce qu'elle n'a pas su trancher.

    LES DEUX SORTENT ENSEMBLE, et l'appelant n'écrit que si `conflits` est vide.
    Rendre un texte fusionné sur un conflit inviterait à l'écrire quand même.
    """

    plat: dict[str, object]
    changements: list[str]
    conflits: list[str]


def fusionner(
    base: Mapping[str, object], local: Mapping[str, object], semence: Mapping[str, object]
) -> Fusion:
    """Fusion à trois points, clé par clé.

    QUI GAGNE SE DÉDUIT DE QUI A BOUGÉ, jamais d'une préséance :

      local = base          la semence a bougé seule      → la semence gagne
      semence = base        le local a bougé seul         → le local reste
      les deux ont bougé    personne ne peut trancher     → CONFLIT
      absente de la semence retirée depuis                → GARDÉE et signalée
      absente du local       supprimée sur place           → LAISSÉE supprimée

    SANS BASE, la même règle donne le mode adoption : toute clé absente localement
    est un apport, toute clé absente de la semence est gardée, et une clé écrite des
    deux côtés à deux valeurs différentes est un conflit — l'attribution est
    impossible, et la refuser vaut mieux que la deviner.

    LA GRANULARITÉ EST LA CLÉ TOML, pas le bloc `[fields.x]` : un conflit sur une
    description ne doit pas emporter le type et les valeurs du champ avec lui.
    """
    plat: dict[str, object] = {}
    changements: list[str] = []
    conflits: list[str] = []

    for cle in list(semence) + [c for c in local if c not in semence]:
        b = base.get(cle, MISSING)
        l = local.get(cle, MISSING)  # noqa: E741 — `l` face à `b` et `s`, la triade se lit mieux
        s = semence.get(cle, MISSING)

        if l == s:
            gagnant = l
        elif s is MISSING:
            # RIEN N'EST SIGNALÉ ICI NON PLUS, pour la raison qui vaut deux branches
            # plus bas : une clé que la semence ne porte plus et que le local garde
            # est un ÉTAT, qui persistera identique au prochain appel. `validate` le
            # dit une fois — le contrat diffère de sa semence — au lieu que `reseed`
            # le rejoue indéfiniment sous le nom de « changement ».
            gagnant = l
        elif l == b:
            gagnant = s
            changements.append(f"{cle} — {'posée' if l is MISSING else 'reprise'} de la semence")
        elif s == b:
            # RIEN N'EST SIGNALÉ ICI, SUPPRESSION COMPRISE. Ce que le local a décidé
            # seul n'est pas un changement du re-semis : le rapporter décrirait un
            # ÉTAT qui persiste après coup — la semence porte toujours la clé, le
            # local continue de ne pas la porter — et une liste ainsi faite ne dirait
            # jamais « déjà à jour ». C'est `validate` qui dit l'écart durable, pas
            # `reseed` qui le rejoue à chaque appel.
            gagnant = l
        else:
            conflits.append(f"{cle} — modifiée des deux côtés")
            continue

        # UNE ABSENCE NE S'ÉCRIT PAS. Une clé que le local a supprimée est gagnée par
        # le local — c'est la règle générale, sans exception pour la suppression — et
        # ce que gagne une absence est de rester absente. La poser ferait descendre le
        # sentinelle jusque dans l'émetteur, qui sortait alors par un traceback, après
        # la sauvegarde et une partie de l'écriture.
        if gagnant is not MISSING:
            plat[cle] = gagnant

    return Fusion(plat, changements, conflits)


def fusionner_gabarits(
    base: Mapping[str, str], local: Mapping[str, str], semence: Mapping[str, str]
) -> tuple[dict[str, str], list[str], list[str]]:
    """La même règle, à la granularité du FICHIER ENTIER.

    Un gabarit est une prose libre : il n'a pas de clés à confronter, et deux
    versions d'un même paragraphe ne se fusionnent pas ligne à ligne sans inventer
    un texte que personne n'a écrit.
    """
    fusion = fusionner(
        cast("Mapping[str, object]", base),
        cast("Mapping[str, object]", local),
        cast("Mapping[str, object]", semence),
    )
    # Le nom du fichier est préfixé plutôt que laissé nu : « revue.md — modifiée des
    # deux côtés » ne dirait pas de quel genre d'objet il parle, au milieu d'une
    # liste de clés pointées venues du contrat.
    return (
        {nom: cast("str", corps) for nom, corps in fusion.plat.items()},
        [f"gabarit {c}" for c in fusion.changements],
        [f"gabarit {c}" for c in fusion.conflits],
    )


# ------------------------------------------------------------------ le re-semis
@final
@dataclass(frozen=True)
class Resemis:
    """Ce qu'un re-semis a fait, ou ferait. Rendu identique en `dry_run`."""

    verbatim: bool
    """La semence a été recopiée telle quelle, commentaires compris. Faux = le
    contrat a été réémis, et les commentaires locaux ne sont plus que dans la
    sauvegarde."""
    changements: list[str]
    ecrit: bool


def reseed(
    list_dir: Path,
    definition: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    expected_name: str = "",
) -> Result[Resemis]:
    """Rattrape une liste sur sa semence, sans jamais trancher à sa place.

    L'ORDRE DES REFUS EST CELUI DU COÛT : un gel se dit avant d'avoir lu quoi que ce
    soit, un conflit avant d'avoir écrit quoi que ce soit. Rien n'est jamais écrit à
    moitié.

    `force` NE FAIT QUE DÉGELER. Un conflit sort non nul avec ou sans lui : le seul
    arbitrage possible entre deux versions d'une même clé appartient à celui qui a
    écrit l'une des deux, et « aucune résolution automatique » est la règle de ce
    dispositif. La sauvegarde et le rapport lui donnent les deux textes.

    LA RECOPIE VERBATIM N'EST PAS UNE OPTIMISATION : elle préserve les commentaires
    de la définition, qui portent souvent le pourquoi d'un champ. Réémettre un
    contrat que rien ne distinguait de sa semence les perdrait pour rien.
    """
    lu = load_contract(list_dir)
    if not lu:
        return Result(lu.status, None, lu.message)
    origin = lu.unwrap().origin

    if origin is not None and origin.frozen and not force:
        return fail(
            f"{list_dir} : liste gelée (« frozen = true ») — « --force » pour passer outre. "
            "Le gel dit que ce contrat a délibérément pris ses distances avec sa semence."
        )

    semence = read_seed(definition)
    if not semence:
        return Result(semence.status, None, semence.message)
    texte_semence, gabarits_semence, contrat_semence = semence.unwrap()

    # Même règle qu'à l'`init`, et pour la même raison : une absence n'est pas une
    # contradiction, seuls DEUX NOMS QUI SE CONTREDISENT sont refusés.
    declare = contrat_semence.origin.name if contrat_semence.origin is not None else None
    if expected_name and declare is not None and declare != expected_name:
        return fail(
            f"{definition / CONTRACT}: rattrapée sous « {expected_name} », mais "
            f"« origin.def » y déclare « {declare} » — l'estampille pointerait ailleurs "
            "que là où cette liste vient d'être rattrapée",
            2,
        )

    base = list_base(list_dir)
    local = _brut(base / CONTRACT)
    if not local:
        return Result(local.status, None, local.message)
    graine = _brut(definition / CONTRACT)
    if not graine:
        return Result(graine.status, None, graine.message)
    ancien = _brut(seed_base(list_dir) / CONTRACT) if _semée(list_dir) else ok({})
    if not ancien:
        return Result(ancien.status, None, ancien.message)

    fusion = fusionner(flatten(ancien.unwrap()), flatten(local.unwrap()), flatten(graine.unwrap()))
    gabarits, changements_g, conflits_g = fusionner_gabarits(
        _gabarits(seed_base(list_dir)) if _semée(list_dir) else {},
        _gabarits(base),
        gabarits_semence,
    )

    conflits = fusion.conflits + conflits_g
    if conflits:
        # Rien n'est écrit, pas même la sauvegarde : un conflit laisse la liste
        # exactement dans l'état où on l'a trouvée, et le rapport dit où regarder.
        detail = "\n".join(f"  {c}" for c in conflits)
        return fail(
            f"{list_dir} : {len(conflits)} conflit(s) — la semence et cette liste ont modifié "
            f"les mêmes clés, rien n'a été écrit :\n{detail}\n"
            "Trancher à la main dans le contrat, puis relancer."
        )

    changements = fusion.changements + changements_g
    verbatim = fusion.plat == flatten(graine.unwrap()) and gabarits == gabarits_semence
    if verbatim:
        contrat = texte_semence
    else:
        emission = emit(fusion.plat)
        if not emission:
            return Result(emission.status, None, f"{list_dir} : {emission.message}")
        contrat = emission.unwrap()

    # RIEN À FAIRE SE FAIT EN NE FAISANT RIEN, sauvegarde comprise. `_ecrire` commence
    # par remplacer `.list/backup/`, et un second `reseed` — le geste de qui doute que
    # le premier ait pris — y recopiait donc l'état COURANT en répondant « déjà à
    # jour » : la seule marche arrière disparaissait sans un mot.
    #
    # La garde porte sur les TROIS cibles, et pas sur la liste des changements : c'est
    # ce que les fichiers contiennent qui dit s'il y a quelque chose à écrire.
    if not _a_ecrire(list_dir, contrat, gabarits, texte_semence, gabarits_semence):
        return ok(Resemis(verbatim, changements, ecrit=False))

    if dry_run:
        return ok(Resemis(verbatim, changements, ecrit=False))

    ecriture = _ecrire(list_dir, contrat, gabarits, gabarits_semence, texte_semence)
    if not ecriture:
        return Result(ecriture.status, None, ecriture.message)
    return ok(Resemis(verbatim, changements, ecrit=True))


def _a_ecrire(
    list_dir: Path,
    contrat: str,
    gabarits: Mapping[str, str],
    texte_semence: str,
    gabarits_semence: Mapping[str, str],
) -> bool:
    """Y a-t-il quoi que ce soit à changer sur le disque ?

    LES TROIS CIBLES SONT REGARDÉES, parce que les trois sont écrites : le contrat, les
    gabarits, et la semence gardée. Une liste dont le contrat est déjà à jour peut très
    bien porter une semence périmée — c'est l'état qu'un `reseed` interrompu laisserait.
    """
    base = list_base(list_dir)
    semence = seed_base(list_dir)
    return (
        _texte_differe(base / CONTRACT, contrat)
        or _gabarits(base) != dict(gabarits)
        or _lire(semence / CONTRACT) != texte_semence
        or _gabarits(semence) != dict(gabarits_semence)
    )


def _texte_differe(actuel: Path, projete: str) -> bool:
    """Le contrat en place dit-il autre chose que ce qu'on s'apprête à écrire ?

    SUR LE CONTENU, JAMAIS SUR LES OCTETS, et ce n'est pas la même prudence qu'à la
    lecture : ici la comparaison décide d'une ÉCRITURE. Un commentaire ajouté sur
    place ne change rien à ce que le contrat déclare ; réécrire pour lui ferait perdre
    ce commentaire sous le message « déjà à jour » — la liste s'appauvrirait d'un geste
    qui annonce n'avoir rien fait.
    """
    present = _lire(actuel)
    if present is None:
        return True
    try:
        return flatten(tomllib.loads(present)) != flatten(tomllib.loads(projete))
    except tomllib.TOMLDecodeError:
        return True


def _semée(list_dir: Path) -> bool:
    return (seed_base(list_dir) / CONTRACT).is_file()


def _brut(path: Path) -> Result[dict[str, object]]:
    """Le TOML d'un contrat, tel qu'il est écrit — défauts non remplis.

    Il est PARSÉ AUSSI, et le parsage est ce qui juge : fusionner deux contrats dont
    l'un est incohérent produirait un troisième contrat incohérent, et l'erreur ne
    se dirait qu'à la commande suivante, en nommant la copie plutôt que l'original.
    """
    try:
        texte = path.read_text(encoding="utf-8")
    except OSError as exc:
        return fail(f"{path}: illisible — {exc.strerror}")
    juge = parse_contract(texte, path)
    if not juge:
        return Result(juge.status, None, juge.message)
    return ok(tomllib.loads(texte))


def _gabarits(base: Path) -> dict[str, str]:
    return {
        f.name: f.read_text(encoding="utf-8")
        for f in sorted((base / TEMPLATES).glob("*"))
        if f.is_file()
    }


def _ecrire(
    list_dir: Path,
    contrat: str,
    gabarits: Mapping[str, str],
    gabarits_semence: Mapping[str, str],
    texte_semence: str,
) -> Result[None]:
    """Sauvegarder, écrire, rafraîchir la semence — dans cet ordre, jamais un autre.

    LA SAUVEGARDE PASSE D'ABORD parce qu'elle est la seule marche arrière : écrire
    avant elle laisserait, sur une erreur d'écriture au milieu, une liste modifiée
    dont l'état d'origine n'est plus nulle part.

    LA SEMENCE EST RAFRAÎCHIE EN DERNIER, et c'est ce qui rend le re-semis
    idempotent : le prochain appel compare à ce qui vient d'être appliqué, pas à un
    état que plus rien ne reflète.
    """
    base = list_base(list_dir)
    try:
        backup = base / BACKUP
        if backup.exists():
            shutil.rmtree(backup)
        (backup / TEMPLATES).mkdir(parents=True)
        _ = (backup / CONTRACT).write_text(
            (base / CONTRACT).read_text(encoding="utf-8"), encoding="utf-8"
        )
        for nom, corps in _gabarits(base).items():
            _ = (backup / TEMPLATES / nom).write_text(corps, encoding="utf-8")

        _ = (base / CONTRACT).write_text(contrat, encoding="utf-8")
        _poser(base, gabarits)

        semence = seed_base(list_dir)
        if semence.exists():
            shutil.rmtree(semence)
        semence.mkdir(parents=True)
        _ = (semence / CONTRACT).write_text(texte_semence, encoding="utf-8")
        _poser(semence, gabarits_semence)
    except OSError as exc:
        return fail(f"{list_dir} : re-semis interrompu — {exc.strerror}")
    return ok(None)


def _poser(base: Path, gabarits: Mapping[str, str]) -> None:
    if not gabarits:
        return
    (base / TEMPLATES).mkdir(parents=True, exist_ok=True)
    for nom, corps in gabarits.items():
        _ = (base / TEMPLATES / nom).write_text(corps, encoding="utf-8")
