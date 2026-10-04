"""Le lecteur unique de front matter : TOML vivant, YAML en repli pour les archives."""

from __future__ import annotations

import pytest
from fiche import FrontMatterError, lire_front


def test_toml_rend_les_champs_en_texte() -> None:
    front = lire_front(
        '+++\ngabarit = "suivi"\nslug = "x"\nsession = 3\n"créé" = 2026-09-19\n+++\n\n## A\n'
    )
    assert front.format == "toml"
    assert front.champs == {"gabarit": "suivi", "slug": "x", "session": "3", "créé": "2026-09-19"}


def test_toml_valeur_avec_diese_lue_intacte() -> None:
    # Ce que l'ancien lecteur tronquait : ` #` y ouvrait un commentaire de fin de ligne.
    front = lire_front('+++\nplan = "a/b #c.md"\n+++\n')
    assert front.champs["plan"] == "a/b #c.md"


def test_toml_cle_en_double_refusee() -> None:
    with pytest.raises(FrontMatterError, match="TOML invalide"):
        lire_front('+++\nplan = "a.md"\nplan = "b.md"\n+++\n')


def test_toml_liste_de_chaines_rendue_a_part() -> None:
    front = lire_front('+++\nslug = "x"\nskills = ["a", "b"]\nvide = []\n+++\n')
    assert front.champs == {"slug": "x"}
    assert front.listes == {"skills": ("a", "b"), "vide": ()}


def test_toml_table_refusee() -> None:
    with pytest.raises(FrontMatterError, match="non scalaire"):
        lire_front("+++\n[plan]\na = 1\n+++\n")


def test_toml_liste_d_autre_chose_que_des_chaines_refusee() -> None:
    with pytest.raises(FrontMatterError, match="liste de chaînes"):
        lire_front("+++\nskills = [1, 2]\n+++\n")


def test_yaml_en_repli_retire_le_commentaire() -> None:
    front = lire_front("---\nplan: .claude/p.md   # le plan\nbrief:\n---\n")
    assert front.format == "yaml"
    assert front.champs == {"plan": ".claude/p.md"}


def test_yaml_cle_en_double_refusee() -> None:
    with pytest.raises(FrontMatterError, match="en double"):
        lire_front("---\nplan: a.md\nplan: b.md\n---\n")


@pytest.mark.parametrize(
    ("texte", "motif"),
    [
        ("", "pas de front matter"),
        ("# titre\n", "pas de front matter"),
        ('+++\nslug = "x"\n', "non fermé : aucune ligne « \\+\\+\\+ »"),
        ("---\nslug: x\n", "non fermé : aucune ligne « --- »"),
        ('+++\nslug = "x"\n---\n', "non fermé"),
    ],
)
def test_refus_nommes(texte: str, motif: str) -> None:
    with pytest.raises(FrontMatterError, match=motif):
        lire_front(texte)
