"""Le marqueur d'une section structurée : construit, reconnu, réclamé par `--filled`.

CE QUE CE FICHIER PROUVE : une section à motif reçoit un marqueur qui porte son motif et
ses bornes, `fin` collée au motif sauf espace finale du motif, requis ou facultatif ; une
section sans `type` ou à labels garde le marqueur générique ; `is_section_marker` reconnaît
le générique et celui d'un motif, même réenroulé sur deux lignes ; `check` accepte une
section requise restée à ce marqueur, et `--filled` la dit à remplir — jamais une facultative.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from gabarit.check import check_item
from gabarit.contract import parse_contract
from gabarit.structure import is_section_marker
from gabarit.types import OPTIONAL, PLACEHOLDER, Contract, Item, Section

MOTIF = "[{etat: enum}] {n: int}. {intitule}"


def contrat(tmp_path: Path, *, required: bool = True) -> Contract:
    texte = (
        'name = "essai"\ndescription = ""\n'
        f'[sections."Étapes"]\ndescription = ""\ntype = "motif"\nmotif = "{MOTIF}"\n'
        f"required = {'true' if required else 'false'}\n"
        '[sections."Étapes".captures.etat]\ndescription = "x"\nvalues = ["x", " "]\n'
        '[sections."Étapes".captures.n]\ndescription = "x"\n'
        '[sections."Étapes".captures.intitule]\ndescription = "x"\n'
    )
    return parse_contract(texte, tmp_path / "contract.toml").unwrap()


def item(tmp_path: Path, corps: str) -> Item:
    return Item(tmp_path / "essai.md", {}, {"Étapes": corps})


def raisons(contract: Contract, it: Item, *, filled: bool) -> list[str]:
    return [v.reason for v in check_item(contract, it, filled=filled)]


# ----------------------------------------------------------------- construction
def test_le_marqueur_d_une_section_a_motif_porte_son_motif(tmp_path: Path) -> None:
    assert contrat(tmp_path).sections["Étapes"].marker == f"<À REMPLIR motif: - {MOTIF};;>"
    assert (
        contrat(tmp_path, required=False).sections["Étapes"].marker
        == f"<OPTIONNEL motif: - {MOTIF};;>"
    )


def test_le_marqueur_porte_les_bornes_declarees() -> None:
    s = Section(name="X", required=True, type="motif", motif="{a}", debut="*", fin=".")
    assert s.marker == "<À REMPLIR motif: * {a}.>"


def test_une_espace_finale_du_motif_reste_avant_la_fin() -> None:
    s = Section(name="X", required=True, type="motif", motif="{a} ", debut="-", fin=";;")
    assert s.marker == "<À REMPLIR motif: - {a} ;;>"


def test_une_section_sans_type_ou_a_labels_garde_le_marqueur_generique() -> None:
    assert Section(name="X", required=True).marker == PLACEHOLDER
    assert Section(name="X", type="label", forme="bold").marker == OPTIONAL


# ----------------------------------------------------------------- reconnaissance
@pytest.mark.parametrize(
    "texte",
    [
        PLACEHOLDER,
        OPTIONAL,
        f"<À REMPLIR motif: - {MOTIF} ;;>",
        f"<OPTIONNEL motif: - {MOTIF} ;;>",
        "  <À REMPLIR motif: - [{etat: enum}]\n  {n: int}. {intitule} ;;>\n",
    ],
)
def test_is_section_marker_reconnait(texte: str) -> None:
    assert is_section_marker(texte)


@pytest.mark.parametrize(
    "texte",
    ["- [x] 1. Fait ;;", "<À REMPLIR motif: - {a} ;;", "<AUTRE motif: {a}>", "", "texte"],
)
def test_is_section_marker_refuse(texte: str) -> None:
    assert not is_section_marker(texte)


# --------------------------------------------------------------------- check
def test_une_section_requise_au_marqueur_passe_check(tmp_path: Path) -> None:
    c = contrat(tmp_path)
    assert raisons(c, item(tmp_path, c.sections["Étapes"].marker), filled=False) == []


def test_filled_dit_a_remplir_une_section_requise_au_marqueur(tmp_path: Path) -> None:
    c = contrat(tmp_path)
    for corps in (c.sections["Étapes"].marker, PLACEHOLDER, OPTIONAL):
        assert raisons(c, item(tmp_path, corps), filled=True) == ["à remplir"]


def test_filled_reconnait_un_marqueur_reenroule(tmp_path: Path) -> None:
    c = contrat(tmp_path)
    corps = "<À REMPLIR motif: - [{etat: enum}]\n{n: int}. {intitule} ;;>"
    assert raisons(c, item(tmp_path, corps), filled=True) == ["à remplir"]


def test_filled_ne_reclame_pas_une_section_facultative(tmp_path: Path) -> None:
    c = contrat(tmp_path, required=False)
    assert raisons(c, item(tmp_path, c.sections["Étapes"].marker), filled=True) == []


def test_une_section_sans_type_ne_reconnait_pas_le_marqueur_de_motif(tmp_path: Path) -> None:
    # C7 : sans `type`, `is_marker` à l'identique — un texte qui a la forme d'un marqueur
    # de motif n'y est qu'un texte.
    texte = (
        'name = "essai"\ndescription = ""\n[sections."Étapes"]\ndescription = ""\nrequired = true\n'
    )
    c = parse_contract(texte, tmp_path / "contract.toml").unwrap()
    corps = f"<À REMPLIR motif: - {MOTIF} ;;>"
    assert raisons(c, item(tmp_path, corps), filled=True) == []
