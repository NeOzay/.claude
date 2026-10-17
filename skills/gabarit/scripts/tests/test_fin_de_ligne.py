"""Une section à motif dont la puce finit à la ligne : `fin = "\\n"`.

CE QUE CE FICHIER PROUVE : le contrat accepte `fin = "\\n"`, et la refuse à `debut` ; le
marqueur tient sur une ligne, sans `fin` ; une puce sur une ligne, ou dont la suite va en
retrait, passe ; une ligne vide, une puce ou un texte à la marge la closent, et ce qui suit
hors puce est nommé ; une puce en retrait est imbriquée, comptée dans la `sequence` ; les
captures se jugent comme ailleurs ; `section_values` rend les puces.
"""

from __future__ import annotations

from pathlib import Path

from gabarit.check import check_item
from gabarit.contract import parse_contract
from gabarit.structure import section_values
from gabarit.types import Contract, Item

CONTRAT = """name = "essai"
description = ""

[sections."Dettes"]
description = "les dettes"
type = "motif"
debut = "*"
fin = "\\n"
motif = "{intitule} (gravité {g: int})"

[sections."Dettes".captures.g]
min = 1
max = 3
sequence = false
"""


def contrat(tmp_path: Path, texte: str = CONTRAT) -> Contract:
    return parse_contract(texte, tmp_path / "contract.toml").unwrap()


def item(corps: str) -> Item:
    return Item(Path("essai.md"), {}, {"Dettes": corps})


def fautes(tmp_path: Path, corps: str) -> list[str]:
    return [f"{v.subject} — {v.reason}" for v in check_item(contrat(tmp_path), item(corps))]


# ----------------------------------------------------------------- déclaration
def test_le_contrat_accepte_une_fin_de_ligne(tmp_path: Path) -> None:
    assert contrat(tmp_path).sections["Dettes"].fin == "\n"


def test_debut_ne_peut_valoir_le_saut_de_ligne(tmp_path: Path) -> None:
    texte = CONTRAT.replace('debut = "*"', 'debut = "\\n"')
    r = parse_contract(texte, tmp_path / "contract.toml")
    assert not r
    assert "« debut » — ni vide ni blanc" in r.message


def test_le_marqueur_tient_sur_une_ligne(tmp_path: Path) -> None:
    marqueur = contrat(tmp_path).sections["Dettes"].marker
    assert marqueur == "<OPTIONNEL motif: * {intitule} (gravité {g: int})>"


# -------------------------------------------------------------------- conforme
def test_une_puce_par_ligne_passe(tmp_path: Path) -> None:
    assert fautes(tmp_path, "* Une régression (gravité 2)\n* Un oubli (gravité 1)\n") == []


def test_la_suite_en_retrait_continue_la_puce(tmp_path: Path) -> None:
    corps = "* Une régression qui court\n  sur deux lignes (gravité 2)\n* Un oubli (gravité 1)\n"
    assert fautes(tmp_path, corps) == []


def test_une_ligne_vide_entre_puces_passe(tmp_path: Path) -> None:
    assert fautes(tmp_path, "* Une régression (gravité 2)\n\n* Un oubli (gravité 1)\n") == []


def test_un_jeton_final_reste_dans_la_puce(tmp_path: Path) -> None:
    assert fautes(tmp_path, "* Une régression (gravité 2) ;;\n") == [
        "section « Dettes », puce 1 — « Une régression (gravité 2) ;; » ne suit pas le motif "
        "« {intitule} (gravité {g: int}) »"
    ]


# ---------------------------------------------------------------------- fautes
def test_un_texte_a_la_marge_clot_la_puce(tmp_path: Path) -> None:
    corps = "* Une régression (gravité 2)\nqui déborde\n"
    assert fautes(tmp_path, corps) == [
        "section « Dettes » — texte hors puce : « qui déborde » — une section à motif ne "
        "porte que des puces"
    ]


def test_une_suite_apres_une_ligne_vide_est_hors_puce(tmp_path: Path) -> None:
    corps = "* Une régression (gravité 2)\n\n  qui déborde\n"
    assert fautes(tmp_path, corps) == [
        "section « Dettes » — texte hors puce : « qui déborde » — une section à motif ne "
        "porte que des puces"
    ]


def test_une_puce_en_retrait_est_imbriquee(tmp_path: Path) -> None:
    corps = "* Une régression (gravité 2)\n  * Un détail (gravité 1)\n* Un oubli (gravité 1)\n"
    assert fautes(tmp_path, corps) == [
        "section « Dettes », puce 2 — puce imbriquée — une puce s'ouvre à la marge, sa suite "
        "seule va en retrait"
    ]


def test_une_capture_se_juge_comme_ailleurs(tmp_path: Path) -> None:
    assert fautes(tmp_path, "* Une régression (gravité 4)\n") == [
        "section « Dettes », puce 1, capture « g » — 4 dépasse le maximum 3"
    ]


def test_la_sequence_compte_la_puce_imbriquee(tmp_path: Path) -> None:
    texte = CONTRAT.replace("sequence = false", "sequence = true")
    corps = "* A (gravité 1)\n  * B (gravité 2)\n* C (gravité 3)\n"
    sujets = [v.subject for v in check_item(contrat(tmp_path, texte), item(corps))]
    assert sujets == ["section « Dettes », puce 2"]


# -------------------------------------------------------------------- lecture
def test_section_values_rend_les_puces(tmp_path: Path) -> None:
    corps = "* Une régression qui court\n  sur deux lignes (gravité 2)\n* Un oubli (gravité 1)\n"
    valeurs = section_values(contrat(tmp_path), item(corps), "Dettes").unwrap()
    assert valeurs == [
        {"intitule": "Une régression qui court sur deux lignes", "g": 2},
        {"intitule": "Un oubli", "g": 1},
    ]
