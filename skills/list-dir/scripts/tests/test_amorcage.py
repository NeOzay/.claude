"""Amorçage : la liste-jouet s'ouvre et se lit.

Ce fichier ne prouve rien du paquet — il prouve que le harnais tient : `import
listdir` résout, les fixtures montent une liste que `open_list` accepte, et
l'élément-jouet est conforme à son propre contrat. Un défaut ici ferait échouer
tous les autres fichiers pour une raison qui n'a rien à voir avec ce qu'ils testent.
"""

from __future__ import annotations

from pathlib import Path

from listdir import open_list


def test_liste_vide_s_ouvre(liste_vide: Path) -> None:
    lst = open_list(liste_vide).unwrap()
    assert lst.contract.name == "jouet"
    assert lst.items().unwrap() == []


def test_contrat_jouet_declare_les_cinq_types(liste_vide: Path) -> None:
    """Sans les cinq types, des branches entières de check_value seraient sans support."""
    lst = open_list(liste_vide).unwrap()
    assert {f.type for f in lst.contract.fields.values()} == {
        "slug",
        "text",
        "date",
        "enum",
        "list",
    }
    assert lst.contract.required_sections == ["Constat"]
    assert lst.contract.optional_sections == ["Assumé"]


def test_element_jouet_conforme_et_rempli(liste: Path) -> None:
    """La fixture doit être conforme AU SENS LE PLUS STRICT : les tests d'échec
    partent d'elle et n'injectent qu'un seul défaut à la fois."""
    lst = open_list(liste).unwrap()
    items = lst.items().unwrap()
    assert [it.id for it in items] == ["premier"]
    assert lst.validate(filled=True).unwrap() == []


def test_aucun_test_ne_lit_le_vrai_depot(liste: Path, tmp_path: Path) -> None:
    assert tmp_path in liste.parents or liste == tmp_path
