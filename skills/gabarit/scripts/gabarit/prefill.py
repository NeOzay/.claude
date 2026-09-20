"""Le calcul, faillible, de la valeur initiale d'un champ ou d'une section.

POURQUOI UN MODULE À PART : `Field.marker` / `Section.marker` (types.py) restent
des propriétés pures — `<À REMPLIR>` ou `<OPTIONNEL>`, sans jamais rien exécuter.
Une valeur issue de `command`, elle, peut échouer : un `Result` n'a pas sa place
dans une propriété. Ce module porte donc, et lui seul, ce qui peut faillir : lire
`text`/`command` d'un `Field`/`Section` déjà validés, lancer la commande le cas
échéant, confronter ce qui en sort au contrat.

L'ENVIRONNEMENT EST FOURNI PAR L'APPELANT. Ce module ne connaît aucune variable : il
ajoute à celui du processus ce que `Contexte.environnement` rend pour le champ ou la
section en cours. `listdir` y met ses `LISTDIR_*`, la commande `gabarit` les siennes.

LE SECOND APPEL DE PROCESSUS DU PAQUET, sur le modèle de gitcmd.py. Un troisième site
d'exécution qui apparaîtrait ailleurs ferait diverger le traitement d'un code retour
ou d'un OSError d'ici.

ÉCHEC FERMÉ : code retour non nul, `bash` introuvable, ou sortie refusée par
`check_value` rendent tous un `Result` en échec nommant le lieu, le sujet (champ ou
section) et, pour `command`, la commande incriminée. Rien n'est avalé.
"""

from __future__ import annotations

import datetime
import os
import re
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from .contract import check_value, is_marker
from .gitcmd import git
from .types import Contract, Field, FieldValue, Item, Result, Section, fail, ok

ENTIER = re.compile(r"[+-]?[0-9]+")
"""Un entier en base 10, tel qu'une commande ou un `text` l'écrit. `[0-9]` et non `\\d`,
qui admettrait des chiffres d'autres écritures que `int()` convertirait sans broncher."""

type Environnement = Callable[[str], Mapping[str, str]]
"""Les variables à ajouter pour un champ ou une section, dont le nom est donné."""


@dataclass(frozen=True)
class Contexte:
    """Ce qui ne change pas d'un champ à l'autre au sein d'une même pose."""

    lieu: str  # ce que les messages nomment en tête — la liste, ou le fichier
    cwd: Path  # d'où les commandes sont lancées
    environnement: Environnement


def premier_existant(chemin: Path) -> Path:
    """`chemin`, ou son premier ancêtre qui existe — d'où lancer une commande.

    LES DEUX NE COÏNCIDENT PAS TOUJOURS : une destination peut être calculée en mémoire
    avant d'être créée, et `subprocess.run(cwd=…)` lèverait alors un FileNotFoundError.

    PAS DE REPLI : la chaîne des parents se termine toujours par « / » (chemin absolu)
    ou « . » (chemin relatif), l'un et l'autre `is_dir()`.
    """
    return next(c for c in (chemin, *chemin.parents) if c.is_dir())


def racine_git(cwd: Path) -> Path | None:
    """La racine du dépôt git qui contient `cwd`, ou None — hors dépôt, ou git absent.

    Un échec ne fait rien échouer : il dit seulement qu'il n'y a pas de racine à donner.
    """
    resolved = git("rev-parse", "--show-toplevel", cwd=cwd)
    return Path(resolved.unwrap().strip()) if resolved else None


def _run(command: str, subject: str, name: str, ctx: Contexte) -> Result[str]:
    """La sortie standard de `command`, strippée — ou un échec nommant `subject` et
    la commande incriminée. `name` est le nom du champ ou le titre de la section,
    sans habillage, que l'environnement reçoit."""
    try:
        proc = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            check=False,
            cwd=ctx.cwd,
            env={**os.environ, **ctx.environnement(name)},
        )
    except OSError as exc:
        # C'est `bash` qui manque, pas la commande : celle-ci, introuvable, ressort
        # en code 127 par la branche suivante. Confondre les deux enverrait corriger
        # un contrat parfaitement valide.
        return fail(f"{subject} — commande « {command} » : bash introuvable — {exc}")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return fail(
            f"{subject} — commande « {command} » a échoué (code {proc.returncode}) : {detail}"
        )
    return ok(proc.stdout.strip())


def preview(decl: Field | Section) -> str:
    """Ce qu'un champ ou une section RECEVRA, sans rien exécuter.

    POUR UN ESSAI À BLANC ET LES SEULES DÉCLARATIONS PORTANT `command`. Un mode qui
    promet de ne rien faire ne peut pas lancer le shell d'un contrat pour composer son
    propre libellé : la commande est donc NOMMÉE, pas jouée.

    `text` NE PASSE PAS PAR ICI, et c'est délibéré : littéral, il n'a aucun shell à
    lancer, donc rien n'excuserait de sauter le `check_value` que `initial_field`
    lui applique.
    """
    if decl.command is None:
        raise ValueError(
            f"preview() n'a de sens que sur une déclaration portant `command` : {decl.name}"
        )
    return f"sortie de « {decl.command} »"


def initial_field(f: Field, ctx: Contexte) -> Result[FieldValue]:
    """La valeur initiale d'un champ : `text` littéral, sortie de `command`, ou son
    marqueur si ni l'un ni l'autre n'est déclaré.

    Une valeur issue de `text` ou de `command` est CONFRONTÉE AU TYPE DÉCLARÉ via
    `check_value` : un contrat qui préremplit un champ `date` avec un texte
    quelconque doit être signalé à la pose, pas laissé écrire un front matter que la
    vérification refusera ensuite.
    """
    if f.text is not None:
        value: FieldValue = f.text
    elif f.command is not None:
        produced = _run(f.command, f"{ctx.lieu}: champ « {f.name} »", f.name, ctx)
        if not produced:
            return Result(produced.status, None, produced.message)
        value = produced.unwrap()
    else:
        return ok(f.marker)

    origine = f"commande « {f.command} »" if f.command is not None else "« text »"
    # UN `int` SE POSE EN ENTIER, pas en texte : `text` et `command` ne produisent que
    # des chaînes, et « 1 » écrit tel quel serait refusé à la vérification suivante.
    # La conversion est stricte — une sortie qui n'est pas un entier est refusée ici,
    # en la nommant, plutôt que tronquée ou arrondie.
    if f.type == "int":
        if ENTIER.fullmatch(value) is None:
            return fail(
                f"{ctx.lieu}: champ « {f.name} » — valeur issue de {origine} refusée : "
                f"« {value} » n'est pas un entier en base 10"
            )
        value = int(value)

    reason = check_value(f, value)
    if reason:
        return fail(
            f"{ctx.lieu}: champ « {f.name} » — valeur issue de {origine} refusée : {reason}"
        )

    # UNE DATE SE POSE NUE, comme celles qui sont saisies : `text` et `command` ne rendent
    # que des chaînes, et l'écrivain rendrait `jour = "2026-08-31"` là où il écrit
    # `2026-08-31` pour un `datetime.date`. Sans cette conversion, une même liste porte
    # deux graphies du même champ selon l'origine de la valeur, toutes deux valides — donc
    # rien n'échoue, et un `grep '^jour = 2026'` n'en attrape que la moitié.
    # APRÈS `check_value`, qui a déjà refusé ce qui n'est pas une date ISO. Un marqueur,
    # que `check_value` laisse passer par construction, reste une chaîne.
    if f.type == "date" and isinstance(value, str) and not is_marker(value):
        value = datetime.date.fromisoformat(value)
    return ok(value)


def initial_section(s: Section, ctx: Contexte) -> Result[str]:
    """La valeur initiale d'une section : `text` littéral, sortie de `command`, ou
    son marqueur. Une section n'a pas de type déclaré : rien à confronter."""
    if s.text is not None:
        return ok(s.text)
    if s.command is not None:
        return _run(s.command, f"{ctx.lieu}: section « {s.name} »", s.name, ctx)
    return ok(s.marker)


def compose(
    contract: Contract, path: Path, ctx: Contexte, fixed: Mapping[str, FieldValue]
) -> Result[Item]:
    """Un fichier posé de TOUT le contrat : champs et sections, requis et facultatifs,
    chacun à sa valeur initiale. Rien n'est écrit.

    Poser aussi le facultatif n'est pas de la générosité : ce qu'on ne voit pas n'est
    jamais rempli. `fixed` donne les valeurs que l'appelant impose, qui ne passent ni
    par un marqueur ni par le préremplissage.

    LA PREMIÈRE COMMANDE QUI ÉCHOUE ARRÊTE TOUT, dans l'ordre du contrat : un fichier à
    moitié posé ne se rend pas.
    """
    fields: dict[str, FieldValue] = {}
    for name, f in contract.fields.items():
        if name in fixed:
            fields[name] = fixed[name]
            continue
        initial = initial_field(f, ctx)
        if not initial:
            return Result(initial.status, None, initial.message)
        fields[name] = initial.unwrap()

    sections: dict[str, str] = {}
    for title, s in contract.sections.items():
        posee = initial_section(s, ctx)
        if not posee:
            return Result(posee.status, None, posee.message)
        sections[title] = posee.unwrap()

    return ok(Item(path, fields, sections))
