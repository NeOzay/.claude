"""Le type `bool` : déclaré, confronté, prérempli, écrit et relu.

CE QUE CE FICHIER PROUVE : un contrat peut déclarer `type = "bool"` ; `check_value`
n'accepte qu'un booléen, et refuse un entier, une chaîne ou un entier valant 0 ou 1 ;
`text` et `command` posent un vrai booléen et refusent en la nommant toute autre sortie ;
un booléen écrit dans un front matter se relit booléen.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest
from gabarit.contract import check_value, parse_contract
from gabarit.items import read_item, write_item
from gabarit.prefill import Contexte, initial_field
from gabarit.types import OPTIONAL, PLACEHOLDER, Field, Item, marker


def booleen(*, required: bool = True, text: str | None = None, command: str | None = None) -> Field:
    return Field(name="pin", type="bool", required=required, text=text, command=command)


def aucun(_name: str) -> Mapping[str, str]:
    return {}


def contexte(tmp_path: Path) -> Contexte:
    return Contexte(lieu="essai.md", cwd=tmp_path, environnement=aucun)


# ------------------------------------------------------------------- déclaration
def test_un_contrat_declare_un_bool(tmp_path: Path) -> None:
    texte = 'name = "essai"\ndescription = ""\n[fields.pin]\ntype = "bool"\ndescription = ""\n'
    r = parse_contract(texte, tmp_path / "contract.toml")
    assert r.unwrap().fields["pin"].type == "bool"


def test_un_bool_peut_etre_prerempli(tmp_path: Path) -> None:
    texte = (
        'name = "essai"\ndescription = ""\n'
        '[fields.pin]\ntype = "bool"\ndescription = ""\ntext = "false"\n'
    )
    r = parse_contract(texte, tmp_path / "contract.toml")
    assert r.unwrap().fields["pin"].text == "false"


# ------------------------------------------------------------------ check_value
@pytest.mark.parametrize("valeur", [True, False])
def test_check_value_accepte_un_booleen(valeur: bool) -> None:
    assert check_value(booleen(), valeur) == ""


@pytest.mark.parametrize("valeur", [0, 1, "true", "false", 1.0, None, [True]])
def test_check_value_refuse_ce_qui_n_est_pas_un_booleen(valeur: object) -> None:
    assert "un booléen est attendu" in check_value(booleen(), valeur)


def test_check_value_suspend_le_type_sur_un_marqueur() -> None:
    assert check_value(booleen(), PLACEHOLDER) == ""
    assert check_value(booleen(required=False), OPTIONAL) == ""


# ------------------------------------------------------------------ préremplissage
@pytest.mark.parametrize(("sortie", "attendu"), [("true", True), ("false", False)])
def test_text_pose_un_vrai_booleen(tmp_path: Path, sortie: str, attendu: bool) -> None:
    valeur = initial_field(booleen(text=sortie), contexte(tmp_path)).unwrap()
    assert valeur is attendu


@pytest.mark.parametrize(("sortie", "attendu"), [("true", True), ("false", False)])
def test_command_pose_un_vrai_booleen(tmp_path: Path, sortie: str, attendu: bool) -> None:
    valeur = initial_field(booleen(command=f"echo ' {sortie} '"), contexte(tmp_path)).unwrap()
    assert valeur is attendu


@pytest.mark.parametrize("sortie", ["True", "FALSE", "0", "1", "oui", ""])
def test_une_sortie_qui_n_est_pas_un_booleen_est_refusee_en_la_nommant(
    tmp_path: Path, sortie: str
) -> None:
    r = initial_field(booleen(command=f"printf '%s' '{sortie}'"), contexte(tmp_path))
    assert not r
    assert "n'est ni « true » ni « false »" in r.message
    assert "pin" in r.message


def test_un_bool_sans_preremplissage_pose_son_marqueur(tmp_path: Path) -> None:
    assert initial_field(booleen(required=True), contexte(tmp_path)).unwrap() == marker(
        True, "bool"
    )
    assert initial_field(booleen(required=False), contexte(tmp_path)).unwrap() == marker(
        False, "bool"
    )


# ------------------------------------------------------------------ aller-retour
@pytest.mark.parametrize("valeur", [True, False])
def test_un_booleen_ecrit_se_relit_booleen(tmp_path: Path, valeur: bool) -> None:
    chemin = tmp_path / "essai.md"
    _ = write_item(Item(chemin, {"pin": valeur}, {"Notes": "rien"})).unwrap()

    assert f"pin = {str(valeur).lower()}\n" in chemin.read_text(encoding="utf-8")
    relu = read_item(chemin).unwrap()
    assert relu.fields["pin"] is valeur
    assert check_value(booleen(), relu.fields["pin"]) == ""
