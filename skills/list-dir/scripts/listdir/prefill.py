"""Le calcul, faillible, de la valeur initiale d'un champ ou d'une section.

POURQUOI UN MODULE À PART : `Field.marker` / `Section.marker` (types.py) restent
des propriétés pures — `<À REMPLIR>` ou `<OPTIONNEL>`, sans jamais rien exécuter.
Une valeur issue de `command`, elle, peut échouer : un `Result` n'a pas sa place
dans une propriété. Ce module porte donc, et lui seul, ce qui peut faillir : lire
`text`/`command` d'un `Field`/`Section` déjà validés par `parse_contract`, lancer la
commande le cas échéant, confronter ce qui en sort au contrat.

LE SECOND ET DERNIER APPEL DE PROCESSUS DU PAQUET, sur le modèle de gitcmd.py — « le
seul endroit qui lance un shell ». Un troisième site d'exécution qui apparaîtrait
ailleurs ferait diverger le traitement d'un code retour ou d'un OSError d'ici.

ÉCHEC FERMÉ : code retour non nul, `bash` introuvable, ou sortie refusée par
`check_value` rendent tous un `Result` en échec nommant la liste, le sujet (champ ou
section) et, pour `command`, la commande incriminée — la même forme que partout
ailleurs dans le paquet. Rien n'est avalé.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .contract import check_value
from .gitcmd import git
from .types import Contract, Field, FieldValue, Result, Section, fail, ok


@dataclass(frozen=True)
class PrefillContext:
    """Ce qui ne change pas d'un champ à l'autre au sein d'une même opération.

    CONSTRUIT UNE SEULE FOIS PAR OPÉRATION, pas par champ : `root` coûte un appel à
    git, et le relancer à chaque champ transformerait la création d'un élément en
    autant d'appels à git qu'il porte de champs préremplis.
    """

    list_dir: Path  # LISTDIR_LIST — la liste que le champ instruit
    cwd: Path  # d'où les commandes sont lancées — voir _cwd()
    contract_name: str  # LISTDIR_CONTRACT
    root: Path | None  # LISTDIR_ROOT — racine git, None hors dépôt


def _cwd(list_dir: Path) -> Path:
    """Le répertoire d'où lancer les commandes : la liste, ou son premier ancêtre
    qui existe.

    LES DEUX NE COÏNCIDENT PAS TOUJOURS. `derive` calcule toutes ses fiches en
    mémoire AVANT d'écrire quoi que ce soit — sa destination n'existe donc pas
    encore quand les commandes tournent, et `subprocess.run(cwd=…)` y lèverait un
    FileNotFoundError sur chaque champ prérempli. `LISTDIR_LIST` continue de nommer
    la liste engendrée, qui est bien celle que le champ instruit ; seul le cwd
    recule jusqu'à un répertoire réel.
    """
    # PAS DE REPLI : la chaîne des parents se termine toujours par « / » (chemin
    # absolu) ou « . » (chemin relatif), l'un et l'autre `is_dir()`. Un repli écrit
    # « au cas où » ne serait jamais exercé, et un chemin jamais exercé est un
    # chemin dont on ne sait rien.
    return next(c for c in (list_dir, *list_dir.parents) if c.is_dir())


def context(list_dir: Path, contract: Contract) -> PrefillContext:
    """Le contexte d'une opération sur `list_dir`, sous le contrat `contract`.

    Un échec de `git rev-parse` (pas de dépôt, git absent) vaut « hors dépôt » : il
    ne fait rien échouer, `LISTDIR_ROOT` sera simplement absente de l'environnement
    des commandes.
    """
    cwd = _cwd(list_dir)
    resolved = git("rev-parse", "--show-toplevel", cwd=cwd)
    root = Path(resolved.unwrap().strip()) if resolved else None
    return PrefillContext(list_dir=list_dir, cwd=cwd, contract_name=contract.name, root=root)


def _environment(name: str, item_id: str, ctx: PrefillContext) -> dict[str, str]:
    """L'environnement d'une commande de préremplissage : le sien, enrichi de
    LISTDIR_*. `LISTDIR_ROOT` est OMISE hors dépôt — jamais posée vide."""
    env = dict(os.environ)
    env["LISTDIR_ID"] = item_id
    env["LISTDIR_NAME"] = name
    env["LISTDIR_LIST"] = str(ctx.list_dir)
    env["LISTDIR_CONTRACT"] = ctx.contract_name
    if ctx.root is not None:
        env["LISTDIR_ROOT"] = str(ctx.root)
    return env


def _run(command: str, subject: str, name: str, item_id: str, ctx: PrefillContext) -> Result[str]:
    """La sortie standard de `command`, strippée — ou un échec nommant `subject` et
    la commande incriminée. `subject` nomme le sujet dans les messages (« champ «
    titre » »), `name` porte LISTDIR_NAME — le nom du champ ou le titre de la
    section, sans habillage."""
    try:
        proc = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            check=False,
            cwd=ctx.cwd,
            env=_environment(name, item_id, ctx),
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

    POUR `migrate --dry-run` ET LES SEULES DÉCLARATIONS PORTANT `command`. Un mode
    qui promet de ne rien faire ne peut pas lancer le shell d'un contrat pour
    composer son propre libellé : la commande est donc NOMMÉE, pas jouée.

    `text` NE PASSE PAS PAR ICI, et c'est délibéré : littéral, il n'a aucun shell à
    lancer, donc rien n'excuserait de sauter le `check_value` que `initial_field`
    lui applique. Un dry-run qui annonce un changement que la migration refusera
    ensuite est pire qu'inutile — il ment sur ce qui va se passer.
    """
    if decl.command is None:
        raise ValueError(
            f"preview() n'a de sens que sur une déclaration portant `command` : {decl.name}"
        )
    return f"sortie de « {decl.command} »"


def initial_field(f: Field, item_id: str, ctx: PrefillContext) -> Result[FieldValue]:
    """La valeur initiale d'un champ : `text` littéral, sortie de `command`, ou son
    marqueur si ni l'un ni l'autre n'est déclaré.

    Une valeur issue de `text` ou de `command` est CONFRONTÉE AU TYPE DÉCLARÉ via
    `check_value` : un contrat qui préremplit un champ `date` avec un texte
    quelconque doit être signalé à la création, pas laissé écrire un front matter
    que `validate` refusera ensuite.
    """
    if f.text is not None:
        value: FieldValue = f.text
    elif f.command is not None:
        produced = _run(f.command, f"{ctx.list_dir}: champ « {f.name} »", f.name, item_id, ctx)
        if not produced:
            return Result(produced.status, None, produced.message)
        value = produced.unwrap()
    else:
        return ok(f.marker)

    reason = check_value(f, value)
    if reason:
        origine = f"commande « {f.command} »" if f.command is not None else "« text »"
        return fail(
            f"{ctx.list_dir}: champ « {f.name} » — valeur issue de {origine} refusée : {reason}"
        )
    return ok(value)


def initial_section(s: Section, item_id: str, ctx: PrefillContext) -> Result[str]:
    """La valeur initiale d'une section : `text` littéral, sortie de `command`, ou
    son marqueur. Une section n'a pas de type déclaré : rien à confronter."""
    if s.text is not None:
        return ok(s.text)
    if s.command is not None:
        return _run(s.command, f"{ctx.list_dir}: section « {s.name} »", s.name, item_id, ctx)
    return ok(s.marker)
