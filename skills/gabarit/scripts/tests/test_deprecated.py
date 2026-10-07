"""`deprecated` : lu, refusé quand il se contredit, jamais posé ni réclamé.

CE QUE CE FICHIER PROUVE : un champ ou une section peut porter `deprecated = "<consigne>"`,
chaîne non vide ; le contrat qui l'associe à `required`, `text` ou `command` est refusé en
nommant la contradiction ; un fichier neuf ne porte ni l'un ni l'autre ; `check` ne les
réclame jamais, ne les signale jamais « non déclarés », et contrôle encore le type d'un champ
déprécié qu'un fichier porte.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from gabarit.check import check_item
from gabarit.commandes import check, lire_semence, new
from gabarit.contract import parse_contract
from gabarit.items import read_item
from gabarit.types import Item

BASE = """name = "essai"
description = ""

[fields.titre]
type = "text"
required = true
description = ""

[fields.ancien]
type = "int"
description = ""
deprecated = "remplacé par « titre »"

[sections."Objectif"]
required = true
description = ""

[sections."Vieille"]
description = ""
deprecated = "ne plus écrire"
"""


def lire(texte: str, tmp_path: Path):
    return parse_contract(texte, tmp_path / "contract.toml")


# ---------------------------------------------------------------------- lecture
def test_un_champ_et_une_section_deprecated_se_lisent(tmp_path: Path) -> None:
    contrat = lire(BASE, tmp_path).unwrap()

    assert contrat.fields["ancien"].deprecated == "remplacé par « titre »"
    assert contrat.sections["Vieille"].deprecated == "ne plus écrire"
    assert contrat.fields["titre"].deprecated is None
    assert contrat.sections["Objectif"].deprecated is None


@pytest.mark.parametrize("valeur", ['""', '"   "', "3", "true", '["x"]'])
def test_une_consigne_vide_ou_qui_n_est_pas_une_chaine_est_refusee(
    tmp_path: Path, valeur: str
) -> None:
    r = lire(
        BASE.replace('deprecated = "remplacé par « titre »"', f"deprecated = {valeur}"), tmp_path
    )

    assert not r
    assert "champ « ancien », « deprecated »" in r.message


@pytest.mark.parametrize(
    ("ajout", "nom"),
    [("required = true", "required"), ('text = "1"', "text"), ('command = "echo 1"', "command")],
)
def test_un_champ_deprecated_refuse_ce_qui_le_contredit(
    tmp_path: Path, ajout: str, nom: str
) -> None:
    r = lire(BASE.replace('type = "int"\n', f'type = "int"\n{ajout}\n'), tmp_path)

    assert not r
    assert "champ « ancien »" in r.message
    assert f"« deprecated » contredit « {nom} »" in r.message


def test_une_section_deprecated_refuse_required_text_et_command(tmp_path: Path) -> None:
    for ajout, nom in (
        ("required = true", "required"),
        ('text = "x"', "text"),
        ('command = "echo x"', "command"),
    ):
        r = lire(
            BASE.replace('deprecated = "ne plus écrire"', f'deprecated = "x"\n{ajout}'), tmp_path
        )
        assert not r
        assert "section « Vieille »" in r.message
        assert f"« deprecated » contredit « {nom} »" in r.message


# -------------------------------------------------------------------------- pose
def poser(tmp_path: Path) -> tuple[Path, Path]:
    graine = tmp_path / "semences" / "essai"
    graine.mkdir(parents=True)
    _ = (graine / "contract.toml").write_text(BASE, encoding="utf-8")
    cible = tmp_path / "fiche.md"
    _ = new(cible, lire_semence(graine).unwrap()).unwrap()
    return graine, cible


def test_new_ne_pose_ni_champ_ni_section_deprecated(tmp_path: Path) -> None:
    _, cible = poser(tmp_path)

    item = read_item(cible).unwrap()

    assert "ancien" not in item.fields
    assert list(item.sections) == ["Objectif"]


# ------------------------------------------------------------------------ contrôle
def test_check_ne_reclame_pas_ce_qui_est_deprecated(tmp_path: Path) -> None:
    graine, cible = poser(tmp_path)

    assert check(cible, semence=lire_semence(graine).unwrap()), "fichier neuf"
    r = check(cible, filled=True, semence=lire_semence(graine).unwrap())
    assert "ancien" not in r.message
    assert "Vieille" not in r.message


def test_un_champ_deprecated_porte_n_est_pas_non_declare(tmp_path: Path) -> None:
    contrat = lire(BASE, tmp_path).unwrap()
    item = Item(
        tmp_path / "f.md",
        {"titre": "T", "ancien": 3},
        {"Objectif": "x", "Vieille": "reste"},
    )

    assert check_item(contrat, item) == []


def test_le_type_d_un_champ_deprecated_porte_reste_controle(tmp_path: Path) -> None:
    contrat = lire(BASE, tmp_path).unwrap()
    item = Item(tmp_path / "f.md", {"titre": "T", "ancien": "pas un entier"}, {"Objectif": "x"})

    violations = check_item(contrat, item)

    assert [v.subject for v in violations] == ["champ « ancien »"]
    assert "un entier est attendu" in violations[0].reason


# ----------------------------------------------------------------- avertissement
def fiche_a_remettre_a_jour(tmp_path: Path) -> tuple[Path, Path]:
    graine, cible = poser(tmp_path)
    texte = cible.read_text(encoding="utf-8")
    texte = texte.replace("+++\n\n", "ancien = 3\n+++\n\n", 1) + "\n## Vieille\n\nreste\n"
    _ = cible.write_text(texte, encoding="utf-8")
    return graine, cible


def test_check_avertit_de_ce_qui_est_deprecie_sans_changer_le_verdict(tmp_path: Path) -> None:
    graine, cible = fiche_a_remettre_a_jour(tmp_path)

    r = check(cible, semence=lire_semence(graine).unwrap())

    assert r, r.message
    assert "champ « ancien » — déprécié : remplacé par « titre »" in r.message
    assert "section « Vieille » — dépréciée : ne plus écrire" in r.message
    assert len(r.message.splitlines()) == 2  # une note par champ ou section porté


def test_check_se_tait_sur_un_fichier_qui_ne_porte_rien_de_deprecie(tmp_path: Path) -> None:
    graine, cible = poser(tmp_path)

    assert check(cible, semence=lire_semence(graine).unwrap()).message == ""


def test_notes_sont_la_voie_de_l_avertissement_sur_un_echec_aussi(tmp_path: Path) -> None:
    graine, cible = fiche_a_remettre_a_jour(tmp_path)

    r = check(cible, filled=True, semence=lire_semence(graine).unwrap())

    assert not r
    assert "à remplir" in r.message
    assert "déprécié" in r.message
