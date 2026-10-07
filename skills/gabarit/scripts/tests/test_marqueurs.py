"""Les Marqueurs typés : posés par `new`, reconnus par `check`.

CE QUE CE FICHIER PROUVE : un champ `int`, `date`, `bool` ou `list` sans préremplissage
reçoit `<À REMPLIR int>` / `<OPTIONNEL int>` (et son type), un champ `text`, `enum` ou
`slug` le marqueur générique ; `check` tient les formes typées pour des marqueurs, et
`--filled` ne réclame que les requis ; le marqueur d'un AUTRE type est un manquement
nommé ; le marqueur générique, ancienne forme, reste accepté.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from gabarit.commandes import check, contract, lire_semence, new
from gabarit.contract import REGLE_GUILLEMETS, check_value, is_marker
from gabarit.items import read_item
from gabarit.types import ALL_MARKERS, OPTIONAL, PLACEHOLDER, Field, FieldType, marker

CLI = Path(__file__).resolve().parent.parent / "gabarit-cli.py"

TYPES_A_MARQUEUR_TYPE: list[FieldType] = ["int", "date", "bool", "list"]
TYPES_A_MARQUEUR_GENERIQUE: list[FieldType] = ["text", "enum", "slug"]


def champ(type_: FieldType, *, required: bool = True) -> Field:
    return Field(
        name="x",
        type=type_,
        required=required,
        values=["a", "b"] if type_ == "enum" else [],
    )


# ------------------------------------------------------------------ construction
@pytest.mark.parametrize("type_", TYPES_A_MARQUEUR_TYPE)
def test_un_type_non_chaine_a_un_marqueur_qui_dit_son_type(type_: FieldType) -> None:
    assert marker(True, type_) == f"<À REMPLIR {type_}>"
    assert marker(False, type_) == f"<OPTIONNEL {type_}>"


@pytest.mark.parametrize("type_", [*TYPES_A_MARQUEUR_GENERIQUE, None])
def test_un_type_chaine_et_une_section_gardent_le_marqueur_generique(
    type_: FieldType | None,
) -> None:
    assert marker(True, type_) == PLACEHOLDER
    assert marker(False, type_) == OPTIONAL


def test_le_marqueur_d_un_champ_suit_son_type_et_son_statut() -> None:
    assert champ("date").marker == "<À REMPLIR date>"
    assert champ("date", required=False).marker == "<OPTIONNEL date>"
    assert champ("text").marker == PLACEHOLDER
    assert champ("enum", required=False).marker == OPTIONAL


# ---------------------------------------------------------------- reconnaissance
def test_toutes_les_formes_sont_des_marqueurs() -> None:
    assert {PLACEHOLDER, OPTIONAL} < ALL_MARKERS
    assert all(is_marker(m) for m in ALL_MARKERS)
    assert len(ALL_MARKERS) == 2 * (1 + len(TYPES_A_MARQUEUR_TYPE))


@pytest.mark.parametrize(
    "valeur", ["", "-", "<À REMPLIR str>", "<OPTIONNEL>x", "à remplir", None, 3, ["<OPTIONNEL>"]]
)
def test_ce_qui_n_est_pas_un_marqueur_n_en_est_pas_un(valeur: object) -> None:
    assert not is_marker(valeur)


@pytest.mark.parametrize("type_", TYPES_A_MARQUEUR_TYPE)
def test_check_value_suspend_le_type_sur_le_marqueur_de_son_type(type_: FieldType) -> None:
    assert check_value(champ(type_), marker(True, type_)) == ""
    assert check_value(champ(type_, required=False), marker(False, type_)) == ""


@pytest.mark.parametrize("type_", [*TYPES_A_MARQUEUR_TYPE, *TYPES_A_MARQUEUR_GENERIQUE])
def test_check_value_tolere_l_ancien_marqueur_generique(type_: FieldType) -> None:
    assert check_value(champ(type_), PLACEHOLDER) == ""
    assert check_value(champ(type_, required=False), OPTIONAL) == ""


def test_check_value_refuse_le_marqueur_d_un_autre_type() -> None:
    reason = check_value(champ("date", required=False), "<OPTIONNEL int>")
    assert "marqueur d'un autre type" in reason
    assert "<OPTIONNEL int>" in reason
    assert "date" in reason


def test_check_value_refuse_un_marqueur_type_sur_un_champ_texte() -> None:
    assert check_value(champ("text"), "<À REMPLIR date>") != ""


# -------------------------------------------------------------- new puis check
CONTRAT = """name = "essai"
description = ""

[fields.titre]
type = "text"
required = true
description = ""

[fields.session]
type = "int"
required = true
description = ""

[fields.reviewed]
type = "date"
description = ""

[fields.pin]
type = "bool"
required = true
description = ""

[fields.tags]
type = "list"
description = ""

[fields.categorie]
type = "enum"
values = ["a", "b"]
description = ""

[sections."Objectif"]
required = true
description = ""
"""


def poser(tmp_path: Path) -> Path:
    graine = tmp_path / "semences" / "essai"
    graine.mkdir(parents=True)
    _ = (graine / "contract.toml").write_text(CONTRAT, encoding="utf-8")
    semence = lire_semence(graine).unwrap()
    cible = tmp_path / "fiche.md"
    _ = new(cible, semence).unwrap()
    return cible


def test_new_pose_le_marqueur_du_type_de_chaque_champ(tmp_path: Path) -> None:
    fiche = read_item(poser(tmp_path)).unwrap()

    assert fiche.fields["titre"] == PLACEHOLDER
    assert fiche.fields["session"] == "<À REMPLIR int>"
    assert fiche.fields["reviewed"] == "<OPTIONNEL date>"
    assert fiche.fields["pin"] == "<À REMPLIR bool>"
    assert fiche.fields["tags"] == "<OPTIONNEL list>"
    assert fiche.fields["categorie"] == OPTIONAL
    assert fiche.sections["Objectif"] == PLACEHOLDER


def test_check_tient_les_marqueurs_types_pour_des_marqueurs(tmp_path: Path) -> None:
    fiche = poser(tmp_path)
    graine = lire_semence(tmp_path / "semences" / "essai").unwrap()

    r = check(fiche, semence=graine)

    assert r, r.message


def test_filled_ne_reclame_que_les_requis_types_compris(tmp_path: Path) -> None:
    fiche = poser(tmp_path)
    graine = lire_semence(tmp_path / "semences" / "essai").unwrap()

    r = check(fiche, filled=True, semence=graine)

    assert not r
    assert "champ « session » — à remplir" in r.message
    assert "champ « pin » — à remplir" in r.message
    assert "champ « titre » — à remplir" in r.message
    assert "reviewed" not in r.message
    assert "tags" not in r.message
    assert "categorie" not in r.message


def test_check_refuse_le_marqueur_d_un_autre_type_dans_un_fichier(tmp_path: Path) -> None:
    fiche = poser(tmp_path)
    graine = lire_semence(tmp_path / "semences" / "essai").unwrap()
    texte = fiche.read_text(encoding="utf-8").replace("<OPTIONNEL date>", "<OPTIONNEL int>")
    _ = fiche.write_text(texte, encoding="utf-8")

    r = check(fiche, semence=graine)

    assert not r
    assert "champ « reviewed »" in r.message
    assert "marqueur d'un autre type" in r.message


# ---------------------------------------------------------------- ancien marqueur
def remplacer_par_l_ancien(fiche: Path) -> None:
    texte = fiche.read_text(encoding="utf-8")
    texte = texte.replace("<OPTIONNEL date>", OPTIONAL).replace("<À REMPLIR int>", PLACEHOLDER)
    _ = fiche.write_text(texte, encoding="utf-8")


def test_check_avertit_d_un_ancien_marqueur_sans_changer_le_verdict(tmp_path: Path) -> None:
    fiche = poser(tmp_path)
    graine = lire_semence(tmp_path / "semences" / "essai").unwrap()
    remplacer_par_l_ancien(fiche)

    r = check(fiche, semence=graine)

    assert r, r.message
    assert "champ « reviewed » — ancien marqueur « <OPTIONNEL> »" in r.message
    assert "la forme typée est « <OPTIONNEL date> »" in r.message
    assert "champ « session » — ancien marqueur « <À REMPLIR> »" in r.message
    assert "la forme typée est « <À REMPLIR int> »" in r.message
    assert "titre" not in r.message  # un `text` garde son marqueur générique


def test_check_ne_dit_rien_d_un_fichier_a_jour(tmp_path: Path) -> None:
    fiche = poser(tmp_path)
    graine = lire_semence(tmp_path / "semences" / "essai").unwrap()

    assert check(fiche, semence=graine).message == ""


def test_l_avertissement_accompagne_aussi_un_echec(tmp_path: Path) -> None:
    fiche = poser(tmp_path)
    graine = lire_semence(tmp_path / "semences" / "essai").unwrap()
    remplacer_par_l_ancien(fiche)

    r = check(fiche, filled=True, semence=graine)

    assert not r
    assert "manquement" in r.message
    assert "ancien marqueur" in r.message


def test_cli_check_avertit_sur_stderr_et_sort_zero(tmp_path: Path) -> None:
    fiche = poser(tmp_path)
    remplacer_par_l_ancien(fiche)
    semence = tmp_path / "semences" / "essai"

    r = subprocess.run(
        [sys.executable, str(CLI), "check", str(fiche), "--from", str(semence)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert r.returncode == 0, r.stderr
    assert "ancien marqueur" in r.stderr
    assert "ancien marqueur" not in r.stdout


# ------------------------------------------------------- la règle des guillemets
def test_la_regle_des_guillemets_nomme_les_types_dans_chaque_camp() -> None:
    avec, _, sans = REGLE_GUILLEMETS.partition("Un champ ")
    garde = {t.strip(" .") for t in avec.split("champs ")[1].split(" gardent")[0].split(",")}
    nu = {t.strip() for t in sans.split(" s'écrit")[0].split(",")}

    assert garde == {"text", "enum", "slug"}
    assert nu == {"int", "date", "bool", "list"}


def test_contract_rend_la_regle_avec_le_contrat_et_pas_avec_values(tmp_path: Path) -> None:
    graine = tmp_path / "semences" / "essai"
    graine.mkdir(parents=True)
    _ = (graine / "contract.toml").write_text(CONTRAT, encoding="utf-8")
    semence = lire_semence(graine).unwrap()

    complet = contract(semence)
    valeurs = contract(semence, "categorie")

    assert complet.unwrap() == CONTRAT.rstrip("\n")
    assert complet.message == REGLE_GUILLEMETS
    assert valeurs.unwrap() == "a\nb"
    assert valeurs.message == ""


def test_cli_contract_garde_stdout_verbatim_et_dit_la_regle_sur_stderr(tmp_path: Path) -> None:
    graine = tmp_path / "semences" / "essai"
    graine.mkdir(parents=True)
    _ = (graine / "contract.toml").write_text(CONTRAT, encoding="utf-8")

    def lancer(*argv: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), "contract", "--from", str(graine), *argv],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    complet, valeurs = lancer(), lancer("--values", "categorie")

    assert complet.returncode == 0
    assert complet.stdout.rstrip("\n") == CONTRAT.rstrip("\n")
    assert REGLE_GUILLEMETS in complet.stderr
    assert valeurs.stdout == "a\nb\n"
    assert valeurs.stderr == ""
