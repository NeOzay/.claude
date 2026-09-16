"""Le préremplissage d'un élément de liste : celui d'un gabarit, plus `LISTDIR_*`.

LE CALCUL VIT DANS `gabarit.prefill`. Ce module n'ajoute que ce qu'une liste est seule
à savoir : l'environnement `LISTDIR_*` que reçoit une commande de préremplissage, et le
répertoire d'où elle est lancée.

L'environnement porte :

  LISTDIR_ID        l'identifiant de l'élément
  LISTDIR_NAME      le nom du champ, ou le titre de la section
  LISTDIR_LIST      le chemin du répertoire-liste
  LISTDIR_CONTRACT  le `name` du contrat
  LISTDIR_ROOT      la racine git — OMISE hors dépôt, jamais posée vide
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from gabarit.prefill import Contexte, premier_existant, racine_git
from gabarit.prefill import initial_field as _initial_field
from gabarit.prefill import initial_section as _initial_section
from gabarit.prefill import preview as preview

from .types import Contract, Field, FieldValue, Result, Section


@dataclass(frozen=True)
class PrefillContext:
    """Ce qui ne change pas d'un champ à l'autre au sein d'une même opération.

    CONSTRUIT UNE SEULE FOIS PAR OPÉRATION, pas par champ : `root` coûte un appel à
    git, et le relancer à chaque champ transformerait la création d'un élément en
    autant d'appels à git qu'il porte de champs préremplis.
    """

    list_dir: Path  # LISTDIR_LIST — la liste que le champ instruit
    cwd: Path  # d'où les commandes sont lancées : la liste, ou son premier ancêtre existant
    contract_name: str  # LISTDIR_CONTRACT
    root: Path | None  # LISTDIR_ROOT — racine git, None hors dépôt


def context(list_dir: Path, contract: Contract) -> PrefillContext:
    """Le contexte d'une opération sur `list_dir`, sous le contrat `contract`.

    LE CWD RECULE JUSQU'À UN RÉPERTOIRE RÉEL : `derive` calcule toutes ses fiches en
    mémoire avant d'écrire quoi que ce soit, et sa destination n'existe donc pas encore
    quand les commandes tournent. `LISTDIR_LIST` continue de nommer la liste engendrée.
    """
    cwd = premier_existant(list_dir)
    return PrefillContext(
        list_dir=list_dir, cwd=cwd, contract_name=contract.name, root=racine_git(cwd)
    )


def for_item(item_id: str, ctx: PrefillContext) -> Contexte:
    """Le contexte de `gabarit` pour poser l'élément `item_id`."""

    def environnement(name: str) -> dict[str, str]:
        env = {
            "LISTDIR_ID": item_id,
            "LISTDIR_NAME": name,
            "LISTDIR_LIST": str(ctx.list_dir),
            "LISTDIR_CONTRACT": ctx.contract_name,
        }
        if ctx.root is not None:
            env["LISTDIR_ROOT"] = str(ctx.root)
        return env

    return Contexte(lieu=str(ctx.list_dir), cwd=ctx.cwd, environnement=environnement)


def initial_field(f: Field, item_id: str, ctx: PrefillContext) -> Result[FieldValue]:
    """La valeur initiale d'un champ de l'élément `item_id` : voir `gabarit.prefill`."""
    return _initial_field(f, for_item(item_id, ctx))


def initial_section(s: Section, item_id: str, ctx: PrefillContext) -> Result[str]:
    """La valeur initiale d'une section de l'élément `item_id` : voir `gabarit.prefill`."""
    return _initial_section(s, for_item(item_id, ctx))
