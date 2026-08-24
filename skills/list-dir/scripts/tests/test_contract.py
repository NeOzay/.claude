"""contract.py — le contrat lui-même, et la confrontation d'une valeur au contrat.

CE QUE CE FICHIER CADRE : le contrat est écrit à la main, donc il peut être écrit de
travers. `tomllib` rend des objets quelconques ; chaque valeur lue doit ressortir en
échec NOMMÉ plutôt qu'en AttributeError trois appels plus loin. Un contrat incohérent
qui se chargerait à moitié est un contrat qui ne contraint plus rien.

Le point le plus subtil, et le seul qui ne se déduit d'aucune signature : LE CONTRÔLE
DE TYPE EST SUSPENDU SUR UN MARQUEUR. `date = "<À REMPLIR>"` doit être signalé comme
*à remplir*, jamais comme *type invalide* — un message qui parle de type devant un
marqueur dit au lecteur de corriger ce qui va bien.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest
from listdir.contract import check_value, is_marker, load_contract, parse_contract
from listdir.types import OPTIONAL, PLACEHOLDER, Field

FICHIER = Path("/jouet/.list/contract.toml")

MINIMAL = """name = "n"

[fields.id]
type = "slug"

[sections]
required = ["Constat"]
optional = []
"""


def echec(texte: str) -> str:
    r = parse_contract(texte, FICHIER)
    assert not r, "ce contrat aurait dû être refusé"
    return r.message


# ------------------------------------------------------------------ cas nominal
def test_contrat_minimal_se_charge() -> None:
    c = parse_contract(MINIMAL, FICHIER).unwrap()
    assert c.name == "n"
    assert list(c.fields) == ["id"]
    assert c.sections == ["Constat"]


def test_sections_requises_d_abord() -> None:
    """`sections` est l'ordre dans lequel `new` les pose : requises, puis facultatives."""
    texte = MINIMAL.replace('optional = []', 'optional = ["Assumé"]')
    c = parse_contract(texte, FICHIER).unwrap()
    assert c.sections == ["Constat", "Assumé"]


def test_champ_porte_sa_declaration() -> None:
    texte = MINIMAL + """
[fields.category]
type = "enum"
values = ["a", "b"]
required = true
description = "la catégorie"
from = "source"
"""
    f = parse_contract(texte, FICHIER).unwrap().fields["category"]
    assert (f.type, f.required, f.values, f.description, f.source) == (
        "enum",
        True,
        ["a", "b"],
        "la catégorie",
        "source",
    )


# ------------------------------------------------------- ce qui doit être refusé
def test_toml_invalide() -> None:
    assert "TOML invalide" in echec("name = \n")


def test_fields_n_est_pas_une_table() -> None:
    assert "une table est attendue" in echec('name = "n"\nfields = "x"\n')


def test_champ_declare_par_autre_chose_qu_une_table() -> None:
    assert "champ « id »" in echec('name = "n"\n\n[fields]\nid = "slug"\n')


def test_type_inconnu_est_nomme_avec_les_types_admis() -> None:
    message = echec('name = "n"\n\n[fields.id]\ntype = "couleur"\n')
    assert "couleur" in message
    assert "slug" in message and "enum" in message


def test_type_absent_est_refuse() -> None:
    """Un champ sans type n'est pas un champ par défaut : la liste est fermée."""
    assert "inconnu" in echec('name = "n"\n\n[fields.id]\nrequired = true\n')


def test_enum_sans_values() -> None:
    message = echec('name = "n"\n\n[fields.c]\ntype = "enum"\n')
    assert "n'admet rien" in message


def test_values_n_est_pas_une_liste_de_chaines() -> None:
    assert "liste de chaînes" in echec(
        'name = "n"\n\n[fields.c]\ntype = "enum"\nvalues = [1, 2]\n'
    )


def test_description_de_champ_non_textuelle() -> None:
    assert "une chaîne est attendue" in echec(
        'name = "n"\n\n[fields.id]\ntype = "slug"\ndescription = 3\n'
    )


def test_from_qui_ne_nomme_pas_un_champ() -> None:
    message = echec('name = "n"\n\n[fields.id]\ntype = "slug"\nfrom = 3\n')
    assert "« from »" in message
    assert "int" in message


def test_section_a_la_fois_requise_et_optionnelle() -> None:
    texte = 'name = "n"\n\n[sections]\nrequired = ["A", "B"]\noptional = ["B"]\n'
    message = echec(texte)
    assert "à la fois requise et optionnelle" in message
    assert "B" in message


def test_sections_required_n_est_pas_une_liste() -> None:
    assert "une liste est attendue" in echec(
        'name = "n"\n\n[sections]\nrequired = "A"\noptional = []\n'
    )


def test_name_manquant() -> None:
    assert "une liste se nomme" in echec('[sections]\nrequired = []\noptional = []\n')


def test_name_vide_vaut_manquant() -> None:
    assert "une liste se nomme" in echec('name = ""\n')


def test_name_non_textuel() -> None:
    assert "une chaîne est attendue" in echec("name = 3\n")


def test_sans_fields_ni_sections_reste_valide() -> None:
    """Une liste sans champ déclaré est pauvre, pas incohérente."""
    c = parse_contract('name = "n"\n', FICHIER).unwrap()
    assert c.fields == {}
    assert c.sections == []


# ---------------------------------------------------------------- load_contract
def test_contrat_absent_est_nomme(tmp_path: Path) -> None:
    r = load_contract(tmp_path)
    assert not r
    assert "contrat introuvable" in r.message
    assert ".list/contract.toml" in r.message


def test_contrat_lu_depuis_le_disque(tmp_path: Path) -> None:
    cible = tmp_path / ".list/contract.toml"
    cible.parent.mkdir(parents=True)
    _ = cible.write_text(MINIMAL, encoding="utf-8")
    assert load_contract(tmp_path).unwrap().name == "n"


# -------------------------------------------------------------------- is_marker
@pytest.mark.parametrize("valeur", [PLACEHOLDER, OPTIONAL])
def test_les_deux_marqueurs_sont_reconnus(valeur: str) -> None:
    assert is_marker(valeur)


@pytest.mark.parametrize("valeur", ["", "-", None, "à remplir", 0, []])
def test_rien_d_autre_n_est_un_marqueur(valeur: object) -> None:
    """Un champ ABSENT et un champ À REMPLIR sont deux états différents : les
    confondre ferait passer un oubli pour une intention."""
    assert not is_marker(valeur)


# ------------------------------------------------------------------ check_value
def champ(type_: str, **kw: object) -> Field:
    return Field(name="x", type=type_, **kw)  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    "type_",
    ["slug", "text", "date", "enum", "list"],
)
def test_le_controle_de_type_est_suspendu_sur_un_marqueur(type_: str) -> None:
    """LE POINT CENTRAL : devant un marqueur, aucun message ne parle de type."""
    f = champ(type_, values=["a"])
    assert check_value(f, PLACEHOLDER) == ""
    assert check_value(f, OPTIONAL) == ""


def test_slug_accepte_un_identifiant() -> None:
    assert check_value(champ("slug"), "mon-id") == ""


@pytest.mark.parametrize("valeur", ["", "   ", 3, None])
def test_slug_exige_une_chaine_non_vide(valeur: object) -> None:
    assert "identifiant non vide" in check_value(champ("slug"), valeur)


@pytest.mark.parametrize("valeur", ["deux mots", " borde", "borde "])
def test_slug_refuse_espace_et_bord_blanc(valeur: str) -> None:
    assert "n'est pas un slug" in check_value(champ("slug"), valeur)


def test_text_accepte_du_texte() -> None:
    assert check_value(champ("text"), "un titre") == ""


def test_text_refuse_un_non_texte() -> None:
    assert "du texte est attendu" in check_value(champ("text"), 3)


def test_text_refuse_le_vide() -> None:
    assert "se remplit ou porte son marqueur" in check_value(champ("text"), "  ")


def test_date_accepte_un_objet_date() -> None:
    """tomllib rend une vraie date pour `date = 2026-08-24`, sans guillemets."""
    assert check_value(champ("date"), datetime.date(2026, 8, 24)) == ""


def test_date_accepte_une_chaine_iso() -> None:
    assert check_value(champ("date"), "2026-08-24") == ""


def test_date_refuse_une_chaine_non_iso() -> None:
    assert "n'est pas une date ISO" in check_value(champ("date"), "24/08/2026")


def test_date_refuse_un_non_texte() -> None:
    assert "une date est attendue" in check_value(champ("date"), 3)


def test_enum_dans_les_valeurs() -> None:
    assert check_value(champ("enum", values=["a", "b"]), "b") == ""


def test_enum_hors_des_valeurs_les_enumere() -> None:
    message = check_value(champ("enum", values=["a", "b"]), "c")
    assert "hors des valeurs déclarées" in message
    assert "a, b" in message


def test_list_accepte_une_liste_de_chaines() -> None:
    assert check_value(champ("list"), ["a", "b"]) == ""
    assert check_value(champ("list"), []) == ""


def test_list_refuse_un_non_liste() -> None:
    assert "une liste est attendue" in check_value(champ("list"), "a")


def test_list_refuse_une_liste_d_entiers() -> None:
    assert "liste de chaînes" in check_value(champ("list"), ["a", 2])


# ------------------------------------------------------------- marqueur du champ
def test_un_champ_requis_porte_le_marqueur_a_remplir() -> None:
    assert champ("text", required=True).marker == PLACEHOLDER


def test_un_champ_facultatif_porte_le_marqueur_optionnel() -> None:
    """Sinon --filled réclamerait de remplir ce que le contrat dit optionnel."""
    assert champ("text").marker == OPTIONAL
