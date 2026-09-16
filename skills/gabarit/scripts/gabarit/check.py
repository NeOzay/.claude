"""Un fichier confronté à un contrat.

DEUX VERDICTS, et c'est délibéré. Sans `filled`, seule la STRUCTURE est jugée : les
marqueurs sont légitimes, puisqu'un fichier fraîchement créé n'est pas encore rempli.
Avec `filled`, plus aucun marqueur n'est toléré là où le contrat exige quelque chose —
mais les facultatifs restés à leur marqueur ne sont JAMAIS réclamés.

`fixed` PORTE LES RÈGLES QU'UN APPELANT SUBSTITUE AU CONTRÔLE DE TYPE d'un champ
déclaré. `listdir` y met la sienne — `id` vaut le nom du fichier —, qu'un gabarit seul
n'a aucune raison d'imposer : un suivi archivé sous `done/<date>-<slug>.md` ne porte
plus le nom de son slug.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from .contract import check_value, is_marker
from .items import fence_ouverte
from .types import Contract, Item, Violation

type Rule = Callable[[Item, object], str]
"""La raison du manquement d'une valeur, ou une chaîne vide si elle convient."""


def check_item(
    contract: Contract,
    item: Item,
    filled: bool = False,
    fixed: Mapping[str, Rule] | None = None,
) -> list[Violation]:
    """Les manquements d'un fichier à `contract`. Liste VIDE = conforme."""
    return [
        *check_fields(contract, item, filled, fixed or {}),
        *check_sections(contract, item, filled),
    ]


def check_fields(
    contract: Contract, item: Item, filled: bool, fixed: Mapping[str, Rule]
) -> list[Violation]:
    out: list[Violation] = []
    for name in item.fields:
        if name not in contract.fields:
            out.append(Violation(item.path, f"champ « {name} »", "non déclaré au contrat"))

    for name, f in contract.fields.items():
        subject = f"champ « {name} »"
        if name not in item.fields:
            if f.required:
                out.append(Violation(item.path, subject, "manquant"))
            continue
        value = item.fields[name]

        rule = fixed.get(name)
        if rule is not None:
            reason = rule(item, value)
            if reason:
                out.append(Violation(item.path, subject, reason))
            continue

        reason = check_value(f, value)
        if reason:
            out.append(Violation(item.path, subject, reason))
        elif filled and f.required and is_marker(value):
            out.append(Violation(item.path, subject, "à remplir"))
    return out


def check_sections(contract: Contract, item: Item, filled: bool) -> list[Violation]:
    out: list[Violation] = []
    declared = set(contract.sections)
    for title, corps in item.sections.items():
        if title not in declared:
            out.append(Violation(item.path, f"section « {title} »", "non déclarée au contrat"))
        # LA FENCE SE SIGNALE ICI, à sa source. Un bloc jamais refermé absorbe les `## `
        # suivants : sans ce contrôle, les sections avalées étaient rapportées
        # « manquantes » alors qu'elles sont écrites dans le fichier.
        ouverte = fence_ouverte(corps)
        if ouverte is not None:
            out.append(
                Violation(
                    item.path,
                    f"section « {title} »",
                    f"bloc de code ouvert par « {ouverte} » et jamais refermé — "
                    "les sections suivantes y sont absorbées",
                )
            )

    for title in contract.required_sections:
        subject = f"section « {title} »"
        if title not in item.sections:
            out.append(Violation(item.path, subject, "manquante"))
            continue
        body = item.sections[title].strip()
        if not body:
            out.append(Violation(item.path, subject, "vide"))
        elif filled and is_marker(body):
            out.append(Violation(item.path, subject, "à remplir"))
    return out
