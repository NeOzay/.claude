"""Le type `date` prérempli : une seule graphie, quelle que soit l'origine de la valeur.

CE QUE CE FICHIER PROUVE : `text` et `command` posent une vraie `datetime.date`, et non
la chaîne que le shell a rendue ; une date écrite se relit date et s'écrit NUE, comme
celle qu'un humain saisit ; une sortie qui n'est pas une date ISO est refusée en la
nommant ; un champ `date` sans préremplissage garde son marqueur, qui reste une chaîne.

POURQUOI LA GRAPHIE EST L'ENJEU : les deux formes, `jour = 2026-08-31` et
`jour = "2026-08-31"`, passent la vérification. Rien n'échoue donc si elles cohabitent,
et c'est exactement ce qui rend l'incohérence invisible.
"""

from __future__ import annotations

import datetime
from collections.abc import Mapping
from pathlib import Path

import pytest
from gabarit.contract import check_value
from gabarit.items import read_item, toml_text, write_item
from gabarit.prefill import Contexte, initial_field
from gabarit.types import OPTIONAL, PLACEHOLDER, Field, Item


def jour(*, required: bool = True, text: str | None = None, command: str | None = None) -> Field:
    return Field(name="jour", type="date", required=required, text=text, command=command)


def aucun(_name: str) -> Mapping[str, str]:
    return {}


def contexte(tmp_path: Path) -> Contexte:
    return Contexte(lieu="essai.md", cwd=tmp_path, environnement=aucun)


# ------------------------------------------------------------------ préremplissage
def test_text_pose_une_vraie_date(tmp_path: Path) -> None:
    valeur = initial_field(jour(text="2026-08-31"), contexte(tmp_path)).unwrap()
    assert valeur == datetime.date(2026, 8, 31)
    assert type(valeur) is datetime.date


def test_command_pose_une_vraie_date(tmp_path: Path) -> None:
    valeur = initial_field(jour(command="echo ' 2026-08-31 '"), contexte(tmp_path)).unwrap()
    assert valeur == datetime.date(2026, 8, 31)
    assert type(valeur) is datetime.date


@pytest.mark.parametrize("sortie", ["hier", "31/08/2026", "2026-13-01", ""])
def test_une_sortie_qui_n_est_pas_une_date_est_refusee_en_la_nommant(
    tmp_path: Path, sortie: str
) -> None:
    r = initial_field(jour(command=f"printf '%s' '{sortie}'"), contexte(tmp_path))
    assert not r
    assert "jour" in r.message


def test_une_date_sans_preremplissage_pose_son_marqueur(tmp_path: Path) -> None:
    assert initial_field(jour(required=True), contexte(tmp_path)).unwrap() == PLACEHOLDER
    assert initial_field(jour(required=False), contexte(tmp_path)).unwrap() == OPTIONAL


# ------------------------------------------------------------------ graphie écrite
def test_une_date_s_ecrit_nue() -> None:
    assert toml_text(datetime.date(2026, 8, 31), "jour") == "2026-08-31"


def test_la_graphie_ne_depend_pas_de_l_origine_de_la_valeur(tmp_path: Path) -> None:
    preremplie = initial_field(jour(command="echo 2026-08-31"), contexte(tmp_path)).unwrap()
    saisie = datetime.date(2026, 8, 31)
    assert toml_text(preremplie, "jour") == toml_text(saisie, "jour")


# ------------------------------------------------------------------ aller-retour
def test_une_date_preremplie_ecrite_se_relit_date(tmp_path: Path) -> None:
    chemin = tmp_path / "essai.md"
    valeur = initial_field(jour(text="2026-08-31"), contexte(tmp_path)).unwrap()
    _ = write_item(Item(chemin, {"jour": valeur}, {"Notes": "rien"})).unwrap()

    assert "jour = 2026-08-31" in chemin.read_text(encoding="utf-8")
    relu = read_item(chemin).unwrap()
    assert relu.fields["jour"] == datetime.date(2026, 8, 31)
    assert check_value(jour(), relu.fields["jour"]) == ""
