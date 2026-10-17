"""Un squelette de labels laissé au marqueur : ni réclamé s'il est facultatif, ni lu.

CE QUE CE FICHIER PROUVE (R2 de l'audit 01) : une table de labels facultative, telle que
`new` la pose, passe `check --filled` même si elle déclare un label requis ; entamée, elle
réclame ses labels requis ; requise, elle les réclame au squelette même. Un label
prérempli ne l'entame pas ; une étiquette non déclarée, un label vidé ou une prose écrite
l'entament. `is_section_untouched` le dit pour une section, à motif comme à labels.
"""

from __future__ import annotations

from pathlib import Path

from gabarit.check import check_item
from gabarit.commandes import check, lire_semence, new
from gabarit.contract import parse_contract
from gabarit.items import read_item
from gabarit.structure import is_section_untouched
from gabarit.types import Contract, Item

CONTRAT = """name = "essai"
description = ""

[sections."Constat"]
description = ""
required = true

[sections."Annexe"]
description = ""
type = "label"
forme = "bold"
prefix = "ce que l'annexe rassemble"

[sections."Annexe".labels."Source"]
description = "x"
required = true

[sections."Annexe".labels."Outil"]
description = "x"
text = "pytest"

[sections."Annexe".labels."Note"]
description = "x"

[sections."Plan"]
description = ""
required = true
type = "label"
forme = "title"

[sections."Plan".labels."Approche"]
description = "x"
required = true

[sections."Plan".labels."Détail"]
description = "x"
type = "label"
forme = "bold"

[sections."Plan".labels."Détail".labels."Retenu"]
description = "x"
required = true

[sections."Étapes"]
description = ""
type = "motif"
motif = "{intitule}"
"""


def contrat(tmp_path: Path) -> Contract:
    return parse_contract(CONTRAT, tmp_path / "contract.toml").unwrap()


def poser(tmp_path: Path) -> tuple[Contract, dict[str, str]]:
    semence = tmp_path / "essai"
    semence.mkdir()
    _ = (semence / "contract.toml").write_text(CONTRAT, encoding="utf-8")
    fiche = tmp_path / "fiche.md"
    _ = new(fiche, lire_semence(semence).unwrap()).unwrap()
    return contrat(tmp_path), dict(read_item(fiche).unwrap().sections)


def remplie(sections: dict[str, str]) -> dict[str, str]:
    """Les sections requises remplies, les facultatives telles que posées."""
    plan = sections["Plan"].replace("### Approche\n\n<À REMPLIR>", "### Approche\n\npar étapes")
    return sections | {"Constat": "vu", "Plan": plan}


def fautes(c: Contract, sections: dict[str, str]) -> list[str]:
    item = Item(Path("fiche.md"), {}, sections)
    return [f"{v.subject} — {v.reason}" for v in check_item(c, item, filled=True)]


# ----------------------------------------------------------------- facultative
def test_une_table_facultative_posee_passe_filled(tmp_path: Path) -> None:
    c, sections = poser(tmp_path)
    assert fautes(c, remplie(sections)) == []


def test_le_fichier_pose_passe_filled_par_la_commande(tmp_path: Path) -> None:
    _, sections = poser(tmp_path)
    fiche = tmp_path / "fiche.md"
    texte = fiche.read_text(encoding="utf-8")
    for titre, corps in remplie(sections).items():
        texte = texte.replace(sections[titre], corps, 1)
    _ = fiche.write_text(texte, encoding="utf-8")
    assert check(fiche, filled=True, semence=lire_semence(tmp_path / "essai").unwrap())


def test_une_table_facultative_entamee_reclame_ses_requis(tmp_path: Path) -> None:
    c, sections = poser(tmp_path)
    annexe = sections["Annexe"].replace("**Note** : <OPTIONNEL>", "**Note** : vue")
    assert fautes(c, remplie(sections) | {"Annexe": annexe}) == [
        "section « Annexe », label « Source » — à remplir",
    ]


def test_un_label_prerempli_n_entame_pas(tmp_path: Path) -> None:
    c, sections = poser(tmp_path)
    assert "**Outil** : pytest" in sections["Annexe"]
    assert is_section_untouched(c.sections["Annexe"], sections["Annexe"])


def test_ce_qui_entame_une_table(tmp_path: Path) -> None:
    c, sections = poser(tmp_path)
    s, posee = c.sections["Annexe"], sections["Annexe"]
    for entamee in (
        posee + "\n\n**Ailleurs** : x",  # une étiquette non déclarée
        posee.replace("**Note** : <OPTIONNEL>", "**Note** :"),  # un label vidé
        posee.replace("<OPTIONNEL>\n\n**Source**", "Les sources.\n\n**Source**", 1),
        "",  # une section vidée
    ):
        assert not is_section_untouched(s, entamee), entamee


# -------------------------------------------------------------------- requise
def test_une_table_requise_reclame_ses_requis_au_squelette(tmp_path: Path) -> None:
    c, sections = poser(tmp_path)
    assert fautes(c, sections | {"Constat": "vu"}) == [
        "section « Plan », label « Approche » — à remplir",
    ]


def test_une_table_facultative_dans_une_requise(tmp_path: Path) -> None:
    c, sections = poser(tmp_path)
    plan = remplie(sections)["Plan"]
    assert "**Retenu** : <À REMPLIR>" in plan
    assert fautes(c, remplie(sections)) == []


# --------------------------------------------------------------------- motif
def test_is_section_untouched_sur_un_motif(tmp_path: Path) -> None:
    c, sections = poser(tmp_path)
    etapes = c.sections["Étapes"]
    assert is_section_untouched(etapes, sections["Étapes"])
    assert not is_section_untouched(etapes, "- Faire ;;")
