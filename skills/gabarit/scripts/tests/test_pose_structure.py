"""`gabarit new` sur une section structurée : posée au marqueur de son motif, ou en
squelette de ses labels.

CE QUE CE FICHIER PROUVE (C4) : une section à motif est posée au marqueur qui porte son
motif ; une section à labels, en squelette de ses labels non dépréciés — `bold` ou `title`,
emboîtés —, chacun à son `text` ou à son marqueur, celui d'un motif à la ligne sous un
label `bold` ; un `text` sur la section l'emporte sur
le squelette ; le fichier posé passe `check`, et `check --filled` dit à remplir chaque
section ou label requis resté au marqueur, hors d'une table facultative laissée au squelette.
Les semences de test vivent sous `tmp_path`.
"""

from __future__ import annotations

from pathlib import Path

from gabarit.commandes import check, lire_semence, new
from gabarit.items import read_item

CONTRAT = """name = "essai"
description = ""

[sections."Étapes"]
description = ""
required = true
type = "motif"
motif = "[{etat: enum}] {n: int}. {intitule}"

[sections."Étapes".captures.etat]
description = "x"
values = ["x", " "]

[sections."Étapes".captures.n]
description = "x"

[sections."Étapes".captures.intitule]
description = "x"

[sections."État"]
description = ""
required = true
type = "label"
forme = "bold"

[sections."État".labels."Prochaine action"]
description = "x"
required = true

[sections."État".labels."Critères"]
description = "x"
type = "motif"
motif = "{code}: {texte}"

[sections."État".labels."Critères".captures.code]
description = "x"

[sections."État".labels."Critères".captures.texte]
description = "x"

[sections."État".labels."Notes"]
description = "x"
text = "rien"

[sections."État".labels."Ancien"]
description = "x"
deprecated = "ne plus l'écrire"

[sections."Plan"]
description = ""
type = "label"
forme = "title"

[sections."Plan".labels."Contexte"]
description = "x"
required = true

[sections."Plan".labels."Détail"]
description = "x"
type = "label"
forme = "title"

[sections."Plan".labels."Détail".labels."Un"]
description = "x"

[sections."Préremplie"]
description = ""
type = "label"
forme = "bold"
text = "**A** : déjà écrit"

[sections."Préremplie".labels."A"]
description = "x"
"""

ETAT = """\
**Prochaine action** : <À REMPLIR>

**Critères** :
<OPTIONNEL motif: - {code}: {texte};;>

**Notes** : rien"""

PLAN = """\
### Contexte

<À REMPLIR>

### Détail

#### Un

<OPTIONNEL>"""


def poser(tmp_path: Path) -> tuple[Path, Path]:
    semence = tmp_path / "essai"
    semence.mkdir()
    _ = (semence / "contract.toml").write_text(CONTRAT, encoding="utf-8")
    fiche = tmp_path / "fiche.md"
    _ = new(fiche, lire_semence(semence).unwrap()).unwrap()
    return semence, fiche


def test_une_section_a_motif_est_posee_au_marqueur_de_son_motif(tmp_path: Path) -> None:
    _, fiche = poser(tmp_path)
    sections = read_item(fiche).unwrap().sections
    assert sections["Étapes"] == "<À REMPLIR motif: - [{etat: enum}] {n: int}. {intitule};;>"


def test_une_section_bold_est_posee_en_squelette(tmp_path: Path) -> None:
    _, fiche = poser(tmp_path)
    assert read_item(fiche).unwrap().sections["État"] == ETAT


def test_une_section_title_est_posee_en_squelette_emboite(tmp_path: Path) -> None:
    _, fiche = poser(tmp_path)
    assert read_item(fiche).unwrap().sections["Plan"] == PLAN


def test_le_text_de_la_section_l_emporte_sur_le_squelette(tmp_path: Path) -> None:
    _, fiche = poser(tmp_path)
    assert read_item(fiche).unwrap().sections["Préremplie"] == "**A** : déjà écrit"


def test_le_fichier_pose_passe_check(tmp_path: Path) -> None:
    semence, fiche = poser(tmp_path)
    r = check(fiche, semence=lire_semence(semence).unwrap())
    assert r, r.message


def test_check_filled_dit_a_remplir(tmp_path: Path) -> None:
    semence, fiche = poser(tmp_path)
    r = check(fiche, filled=True, semence=lire_semence(semence).unwrap())
    assert not r
    assert "section « Étapes » — à remplir" in r.message
    assert "section « État », label « Prochaine action » — à remplir" in r.message
    assert "« Plan »" not in r.message  # facultative, laissée au squelette
    assert "Critères" not in r.message
    assert "« Un »" not in r.message


def test_un_motif_prerempli_sous_un_label_bold_se_pose_a_la_ligne(tmp_path: Path) -> None:
    semence = tmp_path / "essai"
    semence.mkdir()
    contrat = CONTRAT.replace(
        'motif = "{code}: {texte}"', 'motif = "{code}: {texte}"\ntext = "- C1: un ;;"'
    )
    _ = (semence / "contract.toml").write_text(contrat, encoding="utf-8")
    fiche = tmp_path / "fiche.md"
    _ = new(fiche, lire_semence(semence).unwrap()).unwrap()
    assert "**Critères** :\n- C1: un ;;\n" in read_item(fiche).unwrap().sections["État"] + "\n"
    assert check(fiche, semence=lire_semence(semence).unwrap())
