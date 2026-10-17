"""Le `prefix` d'une table à labels : posé à son marqueur, réclamé selon le `required` de
sa table.

CE QUE CE FICHIER PROUVE : le squelette d'une table à `prefix` pose avant le premier label
le marqueur du statut de sa table — `<À REMPLIR>` requise, `<OPTIONNEL>` sinon —, sous
une section comme sous un label ; une table requise dont la prose manque est fautive, et
`--filled` réclame sa prose restée au marqueur ; une table facultative ne réclame rien ;
le fichier posé passe `check`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from gabarit.check import check_item
from gabarit.contract import parse_contract
from gabarit.prefill import Contexte, initial_section
from gabarit.types import Contract, Item

CONTRAT = """name = "essai"
description = ""

[sections."État"]
description = ""
required = {required}
type = "label"
forme = "bold"
prefix = "une phrase d'introduction"

[sections."État".labels."A"]
description = "x"
"""

IMBRIQUE = """name = "essai"
description = ""

[sections."Plan"]
description = ""
type = "label"
forme = "title"

[sections."Plan".labels."Détail"]
description = "x"
required = true
type = "label"
forme = "bold"
prefix = "ce que le détail couvre"

[sections."Plan".labels."Détail".labels."B"]
description = "x"
"""


def contrat(tmp_path: Path, texte: str) -> Contract:
    return parse_contract(texte, tmp_path / "contract.toml").unwrap()


def etat(tmp_path: Path, *, required: bool) -> Contract:
    return contrat(tmp_path, CONTRAT.format(required="true" if required else "false"))


def pose(c: Contract, titre: str, tmp_path: Path) -> str:
    ctx = Contexte(lieu="essai.md", cwd=tmp_path, environnement=lambda _nom: {})
    return initial_section(c.sections[titre], ctx).unwrap()


def fautes(c: Contract, titre: str, corps: str, tmp_path: Path, *, filled: bool) -> list[str]:
    item = Item(tmp_path / "essai.md", {}, {titre: corps})
    return [f"{v.subject} — {v.reason}" for v in check_item(c, item, filled)]


# ------------------------------------------------------------------------ pose
@pytest.mark.parametrize(("required", "marqueur"), [(True, "<À REMPLIR>"), (False, "<OPTIONNEL>")])
def test_le_prefix_est_pose_au_marqueur_du_statut_de_sa_table(
    tmp_path: Path, required: bool, marqueur: str
) -> None:
    assert pose(etat(tmp_path, required=required), "État", tmp_path) == (
        f"{marqueur}\n\n**A** : <OPTIONNEL>"
    )


def test_le_prefix_d_un_label_est_pose_sous_son_titre(tmp_path: Path) -> None:
    assert pose(contrat(tmp_path, IMBRIQUE), "Plan", tmp_path) == (
        "### Détail\n\n<À REMPLIR>\n\n**B** : <OPTIONNEL>"
    )


def test_une_table_sans_prefix_ne_pose_aucune_prose(tmp_path: Path) -> None:
    c = contrat(
        tmp_path,
        CONTRAT.format(required="true").replace('prefix = "une phrase d\'introduction"\n', ""),
    )
    assert pose(c, "État", tmp_path) == "**A** : <OPTIONNEL>"


# ----------------------------------------------------------------------- check
def test_le_squelette_pose_passe_check_et_filled_reclame_la_prose(tmp_path: Path) -> None:
    c = etat(tmp_path, required=True)
    corps = pose(c, "État", tmp_path)
    assert fautes(c, "État", corps, tmp_path, filled=False) == []
    assert fautes(c, "État", corps, tmp_path, filled=True) == [
        "section « État » — prose d'introduction à remplir"
    ]


def test_une_table_requise_sans_prose_est_fautive(tmp_path: Path) -> None:
    c = etat(tmp_path, required=True)
    assert fautes(c, "État", "**A** : x", tmp_path, filled=False) == [
        "section « État » — prose d'introduction manquante — une phrase d'introduction"
    ]


def test_une_table_facultative_ne_reclame_rien(tmp_path: Path) -> None:
    c = etat(tmp_path, required=False)
    corps = pose(c, "État", tmp_path)
    assert fautes(c, "État", corps, tmp_path, filled=True) == []
    assert fautes(c, "État", "**A** : x", tmp_path, filled=True) == []


def test_une_prose_ecrite_passe(tmp_path: Path) -> None:
    c = etat(tmp_path, required=True)
    assert fautes(c, "État", "Une introduction.\n\n**A** : x", tmp_path, filled=True) == []


def test_le_prefix_d_un_label_requis(tmp_path: Path) -> None:
    c = contrat(tmp_path, IMBRIQUE)
    corps = pose(c, "Plan", tmp_path)
    # « Plan », facultative, laissée au squelette : rien n'y est réclamé tant qu'elle n'est
    # pas entamée.
    assert fautes(c, "Plan", corps, tmp_path, filled=True) == []
    entamee = corps.replace("**B** : <OPTIONNEL>", "**B** : x")
    assert fautes(c, "Plan", entamee, tmp_path, filled=True) == [
        "section « Plan », label « Détail » — prose d'introduction à remplir"
    ]
    assert fautes(c, "Plan", "### Détail\n\n**B** : x", tmp_path, filled=False) == [
        "section « Plan », label « Détail » — prose d'introduction manquante — ce que le "
        "détail couvre"
    ]
