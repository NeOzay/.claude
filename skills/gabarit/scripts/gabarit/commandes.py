"""Les opérations de la commande `gabarit`, en bibliothèque.

AUCUNE LOGIQUE DANS LE POINT D'ENTRÉE. `gabarit-cli.py` parse des arguments et traduit
un Result en code de sortie ; tout ce qui décide vit ici, et un script qui importe le
paquet a exactement les mêmes moyens que la ligne de commande.

L'ESTAMPILLE : tout fichier créé par `new` porte en tête de son front matter
`gabarit = "<nom>"`, le nom sous lequel sa semence se résout. C'est ce qui permet de le
vérifier plus tard sans rien dire d'autre que son chemin. Le nom est réservé : une
semence qui déclare elle-même un champ `gabarit` est refusée.

L'ENVIRONNEMENT D'UNE COMMANDE DE PRÉREMPLISSAGE porte :

  GABARIT_FICHIER  le chemin du fichier créé
  GABARIT_NAME     le nom du champ, ou le titre de la section
  GABARIT_SEMENCE  le nom de la semence — celui de l'estampille
  GABARIT_ROOT     la racine git — OMISE hors dépôt, jamais posée vide
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .check import check_item
from .contract import CONTRACT, check_value, field_values, parse_contract
from .definitions import DEFS, Root, config_root, definitions, project_root, resolve, roots
from .items import read_item, write_item
from .prefill import Contexte, Environnement, compose, premier_existant, racine_git
from .types import Contract, Field, Item, Result, fail, ok

ESTAMPILLE = "gabarit"
"""Le champ qui nomme la semence d'un fichier créé. Réservé : aucune semence ne le déclare."""

_NOM = Field(name=ESTAMPILLE, type="slug", required=True)


@dataclass(frozen=True)
class Semence:
    """Une semence lue : le nom qui l'estampille, son répertoire, son contrat."""

    nom: str
    chemin: Path
    contrat: Contract
    texte: str  # le contrat tel qu'il est écrit, commentaires compris


def lire_semence(chemin: Path, nom: str | None = None) -> Result[Semence]:
    """La semence du répertoire `chemin`. Sans `nom`, elle s'estampille du nom de ce
    répertoire — celui sous lequel elle se résoudrait une fois rangée dans une racine."""
    f = chemin / CONTRACT
    if not f.is_file():
        return fail(f"{f}: contrat introuvable")
    try:
        texte = f.read_text(encoding="utf-8")
    except OSError as exc:
        return fail(f"{f}: illisible — {exc.strerror}")
    lu = parse_contract(texte, f)
    if not lu:
        return Result(lu.status, None, lu.message)
    contrat = lu.unwrap()

    if ESTAMPILLE in contrat.fields:
        return fail(
            f"{f}: champ « {ESTAMPILLE} » déclaré — ce nom est réservé à l'estampille que "
            "`gabarit new` pose en tête de chaque fichier"
        )

    retenu = nom if nom is not None else chemin.resolve().name
    raison = check_value(_NOM, retenu)
    if raison:
        return fail(f"{f}: « {retenu} » ne peut pas estampiller un fichier — {raison}")
    return ok(Semence(retenu, chemin, contrat, texte))


def trouver_semence(
    nom: str | None, depuis: Path | None, where: list[Root] | None = None
) -> Result[Semence]:
    """La semence nommée, résolue dans les racines — ou prise au chemin `depuis`.

    L'UN OU L'AUTRE, JAMAIS LES DEUX : un nom qui contredirait le chemin estampillerait
    le fichier d'une semence qui n'est pas celle qui l'a posé. Code 2, comme toute
    erreur d'appel.
    """
    if depuis is not None:
        if nom is not None:
            return fail("une semence se désigne par son nom ou par --from, pas les deux", 2)
        return lire_semence(depuis)
    if nom is None:
        return fail("aucune semence : un nom, ou --from <chemin>", 2)
    trouve = resolve(nom, where if where is not None else roots(DEFS))
    if not trouve:
        return Result(trouve.status, None, trouve.message)
    return lire_semence(trouve.unwrap(), nom)


def _environnement(fichier: Path, semence: Semence, racine: Path | None) -> Environnement:
    def environnement(name: str) -> Mapping[str, str]:
        env = {
            "GABARIT_FICHIER": str(fichier),
            "GABARIT_NAME": name,
            "GABARIT_SEMENCE": semence.nom,
        }
        if racine is not None:
            env["GABARIT_ROOT"] = str(racine)
        return env

    return environnement


def new(fichier: Path, semence: Semence) -> Result[Path]:
    """Crée `fichier`, prérempli de tout le contrat de `semence` et estampillé de son nom.

    RIEN N'EST ÉCRASÉ : un fichier existant est refusé, avant qu'aucune commande de
    préremplissage ne tourne. Une commande qui échoue n'écrit rien non plus.
    """
    if fichier.exists():
        return fail(f"{fichier}: existe déjà — `gabarit new` n'écrase rien")

    cwd = premier_existant(fichier.parent)
    ctx = Contexte(
        lieu=str(fichier),
        cwd=cwd,
        environnement=_environnement(fichier, semence, racine_git(cwd)),
    )
    pose = compose(semence.contrat, fichier, ctx, {})
    if not pose:
        return Result(pose.status, None, pose.message)
    item = pose.unwrap()

    return write_item(Item(fichier, {ESTAMPILLE: semence.nom, **item.fields}, item.sections))


def check(
    fichier: Path,
    filled: bool = False,
    semence: Semence | None = None,
    where: list[Root] | None = None,
) -> Result[str]:
    """`fichier` confronté au contrat de sa semence.

    LA SEMENCE VIENT DE L'ESTAMPILLE, sauf si l'appelant en impose une. Un fichier sans
    estampille et sans semence imposée est un échec nommé : le vérifier contre une
    semence devinée pourrait le déclarer conforme à un contrat qui n'est pas le sien.

    L'ESTAMPILLE N'EST PAS UN CHAMP DU CONTRAT : elle est retirée avant confrontation,
    faute de quoi tout fichier créé par `new` serait « non déclaré au contrat ». Une
    semence imposée qui contredit l'estampille est acceptée — c'est une demande
    explicite — mais dite, sur le canal des avertissements.

    DEUX VERDICTS, comme `list-dir validate` : sans `filled`, la structure seule ; avec,
    plus aucun marqueur là où le contrat exige quelque chose.
    """
    lu = read_item(fichier)
    if not lu:
        return Result(lu.status, None, lu.message)
    item = lu.unwrap()

    estampille = item.fields.get(ESTAMPILLE)
    if estampille is not None:
        raison = check_value(_NOM, estampille)
        if raison:
            return fail(f"{fichier}: champ « {ESTAMPILLE} » — {raison}")

    note = ""
    if semence is None:
        if not isinstance(estampille, str):
            return fail(
                f"{fichier}: aucune estampille « {ESTAMPILLE} » — "
                "désigner la semence par --def <nom> ou --from <chemin>"
            )
        trouvee = trouver_semence(estampille, None, where)
        if not trouvee:
            # LE FICHIER EST NOMMÉ comme dans tout autre échec de `check` : vérifiés en
            # boucle, plusieurs fichiers rendraient sinon le même message sans dire lequel.
            return fail(
                f"{fichier}: estampille « {estampille} » — {trouvee.message}", trouvee.status
            )
        semence = trouvee.unwrap()
    elif estampille is not None and estampille != semence.nom:
        note = (
            f"{fichier}: estampillé « {estampille} », vérifié contre la semence "
            f"« {semence.nom} » demandée"
        )

    sans_estampille = Item(
        item.path,
        {k: v for k, v in item.fields.items() if k != ESTAMPILLE},
        item.sections,
        raw_front=item.raw_front,
    )
    violations = check_item(semence.contrat, sans_estampille, filled)
    if violations:
        detail = "\n".join(str(v) for v in violations)
        pluriel = "s" if len(violations) > 1 else ""
        bilan = f"{detail}\n\n{fichier} : {len(violations)} manquement{pluriel}"
        return fail(f"{bilan}\n\n{note}" if note else bilan)

    quoi = "rempli et conforme" if filled else "conforme"
    return ok(f"{fichier} : {quoi} à la semence « {semence.nom} »", note)


def contract(semence: Semence, champ: str = "") -> Result[str]:
    """Le contrat d'une semence, TEL QU'IL EST ÉCRIT — ou les `values` d'un de ses champs.

    LE TEXTE EST RENDU TEL QUEL, commentaires compris : ils portent souvent le pourquoi
    d'un champ, et c'est ce qu'on vient chercher avant de remplir un fichier posé. Il
    a été JUGÉ avant d'être rendu, par `lire_semence` : un contrat cassé ne sort pas
    sous un code de succès.

    `champ` REND SES VALEURS, une par ligne et dans l'ordre du fichier, de quoi boucler
    dessus sans découper du TOML. Un champ inconnu ou sans `values` est un échec nommé,
    jamais une sortie vide sous un code 0.
    """
    if not champ:
        return ok(semence.texte.rstrip("\n"))
    valeurs = field_values(semence.contrat, champ, semence.chemin / CONTRACT)
    if not valeurs:
        return Result(valeurs.status, None, valeurs.message)
    return ok("\n".join(valeurs.unwrap()))


def _ligne(nom: str, portee: list[Root]) -> str:
    """Ce que `gabarit new <nom>` ferait de ce nom.

    LE RANG SE COMPARE, IL NE SE SUPPOSE PAS : deux racines de même rang sont ambiguës,
    et annoncer la première comme gagnante promettrait ce que `resolve` refuse.
    """
    premier = portee[0].rank
    exaequo = [r for r in portee if r.rank == premier]
    if len(exaequo) > 1:
        origines = ", ".join(r.origin for r in exaequo)
        return f"  {nom:<28} rang {premier}  AMBIGUË — {origines} ; `gabarit new` refusera"
    masquees = "".join(f"  (masque {r.origin})" for r in portee[1:])
    return f"  {nom:<28} rang {premier}  {portee[0].origin}{masquees}"


def defs(cwd: Path | None = None, package: Path | None = None) -> Result[str]:
    """Les semences disponibles, leur rang et leur origine — et les deux ancrages.

    LA RACINE DE PROJET RETENUE EST IMPRIMÉE : la remontée s'arrête au premier
    répertoire contenant un `.claude`, qui n'est pas toujours celui qu'on avait en tête.
    LES MASQUÉES SONT MONTRÉES, PAS TUES. Une liste vide n'est pas un échec : hors de
    tout `.claude`, il n'y a simplement rien à proposer, et c'est dit.
    """
    ici = cwd if cwd is not None else Path.cwd()
    paquet = package if package is not None else Path(__file__).parent
    projet = project_root(ici)
    config = config_root(paquet)
    lignes = [
        f"projet : {projet if projet is not None else 'aucun — rangs 1 et 2 absents'}",
        f"config : {config if config is not None else 'aucune — rangs 3 et 4 absents'}",
        "",
    ]
    trouvees = definitions(roots(DEFS, ici, paquet))
    if not trouvees:
        lignes.append("  aucune semence")
    else:
        lignes += [_ligne(nom, trouvees[nom]) for nom in sorted(trouvees)]
    return ok("\n".join(lignes))
