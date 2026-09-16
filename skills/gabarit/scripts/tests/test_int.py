"""Le type `int` : déclaré, confronté, prérempli, écrit et relu.

CE QUE CE FICHIER PROUVE : un contrat peut déclarer `type = "int"` ; `check_value`
accepte un entier et refuse un booléen, une chaîne ou un flottant ; `text` et `command`
posent un vrai entier, et refusent en la nommant une sortie qui n'en est pas un ; un
entier écrit dans un front matter se relit entier.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest
from gabarit.contract import check_value, parse_contract
from gabarit.items import read_item, write_item
from gabarit.prefill import Contexte, initial_field
from gabarit.types import OPTIONAL, PLACEHOLDER, Field, Item


def entier(*, required: bool = True, text: str | None = None, command: str | None = None) -> Field:
    return Field(name="session", type="int", required=required, text=text, command=command)


def aucun(_name: str) -> Mapping[str, str]:
    return {}


def contexte(tmp_path: Path) -> Contexte:
    return Contexte(lieu="essai.md", cwd=tmp_path, environnement=aucun)


# ------------------------------------------------------------------- déclaration
def test_un_contrat_declare_un_int(tmp_path: Path) -> None:
    texte = 'name = "essai"\ndescription = ""\n[fields.session]\ntype = "int"\ndescription = ""\n'
    r = parse_contract(texte, tmp_path / "contract.toml")
    assert r.unwrap().fields["session"].type == "int"


def test_un_int_peut_etre_prerempli(tmp_path: Path) -> None:
    texte = (
        'name = "essai"\ndescription = ""\n'
        '[fields.session]\ntype = "int"\ndescription = ""\ntext = "1"\n'
    )
    r = parse_contract(texte, tmp_path / "contract.toml")
    assert r.unwrap().fields["session"].text == "1"


# ------------------------------------------------------------------ check_value
def test_check_value_accepte_un_entier() -> None:
    assert check_value(entier(), 3) == ""
    assert check_value(entier(), -2) == ""


@pytest.mark.parametrize("valeur", [True, False, "3", 3.0, None, [1]])
def test_check_value_refuse_ce_qui_n_est_pas_un_entier(valeur: object) -> None:
    assert "un entier est attendu" in check_value(entier(), valeur)


def test_check_value_suspend_le_type_sur_un_marqueur() -> None:
    assert check_value(entier(), PLACEHOLDER) == ""


# ------------------------------------------------------------------ préremplissage
def test_text_pose_un_vrai_entier(tmp_path: Path) -> None:
    valeur = initial_field(entier(text="1"), contexte(tmp_path)).unwrap()
    assert valeur == 1
    assert type(valeur) is int


def test_command_pose_un_vrai_entier(tmp_path: Path) -> None:
    valeur = initial_field(entier(command="echo ' 42 '"), contexte(tmp_path)).unwrap()
    assert valeur == 42
    assert type(valeur) is int


@pytest.mark.parametrize("sortie", ["un", "1.5", "true", "", "٣"])
def test_une_sortie_qui_n_est_pas_un_entier_est_refusee_en_la_nommant(
    tmp_path: Path, sortie: str
) -> None:
    r = initial_field(entier(command=f"printf '%s' '{sortie}'"), contexte(tmp_path))
    assert not r
    assert "n'est pas un entier" in r.message
    assert "session" in r.message


def test_un_int_sans_preremplissage_pose_son_marqueur(tmp_path: Path) -> None:
    assert initial_field(entier(required=True), contexte(tmp_path)).unwrap() == PLACEHOLDER
    assert initial_field(entier(required=False), contexte(tmp_path)).unwrap() == OPTIONAL


# ------------------------------------------------------------------ aller-retour
def test_un_entier_ecrit_se_relit_entier(tmp_path: Path) -> None:
    chemin = tmp_path / "essai.md"
    _ = write_item(Item(chemin, {"session": 3}, {"Notes": "rien"})).unwrap()

    relu = read_item(chemin).unwrap()
    assert relu.fields["session"] == 3
    assert type(relu.fields["session"]) is int
    assert check_value(entier(), relu.fields["session"]) == ""
