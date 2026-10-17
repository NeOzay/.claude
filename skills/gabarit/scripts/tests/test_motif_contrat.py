"""Une section à motif, déclarée au contrat : lue, ou refusée en nommant son chemin.

CE QUE CE FICHIER PROUVE : un contrat déclare `type = "motif"`, son motif et ses
captures ; une capture sans table ou sans description prend la description de sa section ;
chaque incohérence — capture orpheline, type inconnu, enum sans valeurs même sans table,
contrainte hors de son type, motif mal formé, clé de structure hors d'une section à
motif — refuse le contrat en nommant section et capture ;
l'espace est admise dans les `values` d'une capture et toujours refusée sur un champ ; un
contrat sans `type` se lit comme avant.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from gabarit.contract import parse_contract
from gabarit.motif import Trou, compile_motif, decoupe
from gabarit.types import DEBUT, FIN, Capture, Contract, Section

MOTIF = "[{etat: enum}] {n: int}. {intitule} — vérif: {verif}"

CAPTURES = """
[sections."Étapes".captures.etat]
description = "l'état de l'étape"
values = ["x", ">", "!", " "]
[sections."Étapes".captures.n]
description = "son numéro"
min = 1
sequence = true
[sections."Étapes".captures.intitule]
description = "ce qu'elle fait"
[sections."Étapes".captures.verif]
description = "la commande qui la vérifie"
required = false
"""


def contrat(section: str, captures: str = "") -> str:
    return f'name = "essai"\ndescription = ""\n[sections."Étapes"]\n{section}\n{captures}'


def lire(texte: str, tmp_path: Path) -> Contract:
    return parse_contract(texte, tmp_path / "contract.toml").unwrap()


def refus(texte: str, tmp_path: Path) -> str:
    r = parse_contract(texte, tmp_path / "contract.toml")
    assert not r
    assert str(tmp_path / "contract.toml") in r.message
    assert "section « Étapes »" in r.message
    return r.message


def a_motif(motif: str = MOTIF, en_plus: str = "") -> str:
    return f'description = ""\ntype = "motif"\nmotif = "{motif}"\n{en_plus}'


# ------------------------------------------------------------------- déclaration
def test_une_section_a_motif_se_lit(tmp_path: Path) -> None:
    s = lire(contrat(a_motif(), CAPTURES), tmp_path).sections["Étapes"]
    assert s.type == "motif"
    assert s.motif == MOTIF
    assert (s.debut, s.fin) == (DEBUT, FIN) == ("-", ";;")
    assert list(s.captures) == ["etat", "n", "intitule", "verif"]
    assert s.captures["etat"].type == "enum"
    assert s.captures["n"] == Capture(
        name="n", type="int", description="son numéro", min=1, sequence=True
    )
    assert s.captures["intitule"].type == "text"
    assert s.captures["intitule"].required
    assert not s.captures["verif"].required


def test_debut_et_fin_se_declarent(tmp_path: Path) -> None:
    s = lire(contrat(a_motif(en_plus='debut = "*"\nfin = "."'), CAPTURES), tmp_path)
    assert (s.sections["Étapes"].debut, s.sections["Étapes"].fin) == ("*", ".")


def test_l_espace_est_admise_dans_les_values_d_une_capture(tmp_path: Path) -> None:
    s = lire(contrat(a_motif(), CAPTURES), tmp_path).sections["Étapes"]
    assert " " in s.captures["etat"].values


def test_l_espace_reste_refusee_dans_les_values_d_un_champ(tmp_path: Path) -> None:
    texte = (
        'name = "essai"\ndescription = ""\n'
        '[fields.etat]\ntype = "enum"\ndescription = ""\nvalues = ["x", " "]\n'
    )
    r = parse_contract(texte, tmp_path / "contract.toml")
    assert not r
    assert "ni contenir d'espace" in r.message


def test_un_contrat_sans_type_se_lit_comme_avant(tmp_path: Path) -> None:
    texte = 'name = "essai"\ndescription = ""\n[sections.Notes]\ndescription = "libre"\n'
    s = lire(texte, tmp_path).sections["Notes"]
    assert s == Section(name="Notes", description="libre")
    assert s.type is None
    assert s.motif is None
    assert not s.captures


def test_un_motif_sans_capture_se_lit(tmp_path: Path) -> None:
    s = lire(contrat(a_motif("fait")), tmp_path).sections["Étapes"]
    assert not s.captures


# ------------------------------------------------------------------- refus : captures
def test_une_capture_sans_table_prend_la_description_de_sa_section(tmp_path: Path) -> None:
    section = a_motif().replace('description = ""', 'description = "les étapes"')
    captures = CAPTURES.replace('[sections."Étapes".captures.verif]', "[autre]")
    s = lire(contrat(section, captures), tmp_path).sections["Étapes"]
    assert s.captures["verif"] == Capture(name="verif", type="text", description="les étapes")


def test_une_enum_sans_table_reste_refusee(tmp_path: Path) -> None:
    message = refus(contrat(a_motif("[{etat: enum}]")), tmp_path)
    assert "capture « etat » — un enum sans `values` n'admet rien" in message


def test_capture_declaree_absente_du_motif(tmp_path: Path) -> None:
    en_trop = '[sections."Étapes".captures.fantome]\ndescription = "x"\n'
    message = refus(contrat(a_motif(), CAPTURES + en_trop), tmp_path)
    assert "capture « fantome »" in message
    assert "absente du motif" in message


@pytest.mark.parametrize("remplacement", ["", 'description = "  "\n'])
def test_une_capture_sans_description_prend_celle_de_sa_section(
    tmp_path: Path, remplacement: str
) -> None:
    section = a_motif().replace('description = ""', 'description = "les étapes"')
    captures = CAPTURES.replace('description = "ce qu\'elle fait"\n', remplacement)
    s = lire(contrat(section, captures), tmp_path).sections["Étapes"]
    assert s.captures["intitule"].description == "les étapes"
    assert s.captures["etat"].description == "l'état de l'étape"


@pytest.mark.parametrize("type_", ["truc", "bool", "list"])
def test_type_de_capture_inconnu_ou_refuse(tmp_path: Path, type_: str) -> None:
    message = refus(
        contrat(a_motif("{a: " + type_ + "}"), '[sections."Étapes".captures.a]\ndescription="x"'),
        tmp_path,
    )
    assert f"type « {type_} » inconnu" in message
    assert "capture « a »" in message


def test_enum_sans_values(tmp_path: Path) -> None:
    captures = CAPTURES.replace('values = ["x", ">", "!", " "]\n', "")
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "capture « etat »" in message
    assert "enum sans `values`" in message


def test_values_hors_enum(tmp_path: Path) -> None:
    captures = CAPTURES.replace(
        'description = "ce qu\'elle fait"', 'description = "x"\nvalues=["a"]'
    )
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "capture « intitule »" in message
    assert "réservé à une capture enum" in message


def test_valeur_vide_d_une_capture(tmp_path: Path) -> None:
    captures = CAPTURES.replace('["x", ">", "!", " "]', '["x", ""]')
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "ne peut être vide" in message


@pytest.mark.parametrize("cle", ["min = 1", "max = 3", "sequence = true"])
def test_contrainte_d_entier_hors_int(tmp_path: Path, cle: str) -> None:
    captures = CAPTURES.replace('description = "ce qu\'elle fait"', f'description = "x"\n{cle}')
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "capture « intitule »" in message
    assert "réservé à une capture int" in message


@pytest.mark.parametrize("valeur", ['"1"', "true", "1.5"])
def test_min_qui_n_est_pas_un_entier(tmp_path: Path, valeur: str) -> None:
    captures = CAPTURES.replace("min = 1", f"min = {valeur}")
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "capture « n », « min »" in message
    assert "un entier est attendu" in message


def test_min_au_dela_de_max(tmp_path: Path) -> None:
    captures = CAPTURES.replace("min = 1", "min = 5\nmax = 2")
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "« min » (5) dépasse « max » (2)" in message


def test_sequence_qui_n_est_pas_un_booleen(tmp_path: Path) -> None:
    captures = CAPTURES.replace("sequence = true", 'sequence = "oui"')
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "« sequence » — un booléen est attendu" in message


@pytest.mark.parametrize("cle", ['type = "int"', 'text = "1"', 'command = "echo 1"', "autre = 1"])
def test_cle_refusee_dans_une_capture(tmp_path: Path, cle: str) -> None:
    captures = CAPTURES.replace("min = 1", f"min = 1\n{cle}")
    message = refus(contrat(a_motif(), captures), tmp_path)
    assert "capture « n »" in message
    assert f"clé « {cle.split()[0]} » refusée" in message


# ----------------------------------------------------------------- refus : le motif
@pytest.mark.parametrize(
    ("motif", "raison"),
    [
        ("{a", "jamais fermée"),
        ("a}", "sans « { »"),
        ("{a {b}}", "dans une capture"),
        ("{a}{b}", "sans littéral entre elles"),
        ("{a} et {a}", "déclarée deux fois"),
        ("{1a}", "invalide"),
        ("{}", "invalide"),
    ],
)
def test_motif_mal_forme(tmp_path: Path, motif: str, raison: str) -> None:
    message = refus(contrat(a_motif(motif)), tmp_path)
    assert "« motif »" in message
    assert raison in message


def test_motif_absent_ou_vide(tmp_path: Path) -> None:
    for section in ('description = ""\ntype = "motif"', a_motif(" ")):
        assert "« motif » manquant ou vide" in refus(contrat(section), tmp_path)


@pytest.mark.parametrize("borne", ['debut = ""', 'fin = ""', 'fin = "; ;"', "debut = 1"])
def test_borne_vide_blanche_ou_mal_typee(tmp_path: Path, borne: str) -> None:
    message = refus(contrat(a_motif(en_plus=borne), CAPTURES), tmp_path)
    assert f"« {borne.split()[0]} »" in message


def test_type_de_section_inconnu(tmp_path: Path) -> None:
    message = refus(contrat('description = ""\ntype = "tableau"'), tmp_path)
    assert "type « tableau » inconnu" in message


@pytest.mark.parametrize(
    "cle",
    [
        'motif = "{a}"',
        'debut = "*"',
        'fin = "."',
        '[sections."Étapes".captures.a]\ndescription = "x"',
    ],
)
def test_cle_de_motif_sur_une_section_sans_type(tmp_path: Path, cle: str) -> None:
    message = refus(contrat('description = ""', cle), tmp_path)
    assert 'réservé à une section de `type = "motif"`' in message


# ------------------------------------------------------------------- compilation
def test_decoupe_rend_litteraux_et_captures() -> None:
    assert decoupe("[{etat: enum}] {n:int}. {intitule}").unwrap() == [
        "[",
        Trou("etat", "enum"),
        "] ",
        Trou("n", "int"),
        ". ",
        Trou("intitule", "text"),
    ]


def test_le_motif_compile_couvre_une_puce_aux_blancs_reduits(tmp_path: Path) -> None:
    s = lire(contrat(a_motif(), CAPTURES), tmp_path).sections["Étapes"]
    assert s.motif is not None
    expression = compile_motif(decoupe(s.motif).unwrap(), s.captures)
    trouve = expression.fullmatch("[ ] 3. Écrire ; puis tester — vérif: pytest")
    assert trouve is not None
    assert trouve.groupdict() == {
        "etat": " ",
        "n": "3",
        "intitule": "Écrire ; puis tester",
        "verif": "pytest",
    }
    assert expression.fullmatch("[x] 3. Écrire") is None


def test_une_capture_facultative_peut_rester_vide(tmp_path: Path) -> None:
    s = lire(contrat(a_motif(), CAPTURES), tmp_path).sections["Étapes"]
    assert s.motif is not None
    expression = compile_motif(decoupe(s.motif).unwrap(), s.captures)
    assert expression.fullmatch("[x] 1. Faire — vérif: ") is not None
