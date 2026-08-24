"""items.py — lecture d'un élément, sérialisation, et la frontière entre les deux règles.

CE QUE CE FICHIER CADRE, et qu'aucun linter ne dira :

  Règle 1 — un élément lu conserve le texte brut de son front matter, et render() le
  reconduit à l'octet près. Guillemets, ordre des clés, commentaires compris.
  Règle 2 — un élément dont un champ a changé est resérialisé par un sérialiseur
  BORNÉ aux seuls types du contrat. Un type non couvert est une erreur qui le nomme.

La frontière entre les deux est `raw_front is None`, et c'est le seul commutateur.
Les deux défauts historiques du paquet vivaient dans ce module : le découpage sur un
`## ` de bloc de code, et un sérialiseur qui n'échappait pas les sauts de ligne. Les
deux sont corrigés ; ce qui suit est ce qui empêche leur retour.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest
from listdir.items import (
    SerialiseError,
    dump_front,
    dump_value,
    fence_ouverte,
    outside_fences,
    parse_sections,
    read_item,
    render_item,
    split_front,
    write_item,
)
from listdir.types import Item

# ------------------------------------------------------------------ split_front
FICHIER = Path("/jouet/x.md")


def test_front_matter_absent_est_nomme() -> None:
    r = split_front("pas de délimiteur\n", FICHIER)
    assert not r
    assert "front matter absent" in r.message


def test_front_matter_non_ferme_est_nomme() -> None:
    r = split_front('+++\nid = "x"\n\n## Constat\n', FICHIER)
    assert not r
    assert "non fermé" in r.message


def test_front_matter_vide_est_legitime() -> None:
    """Deux délimiteurs collés : un front matter vide n'est pas un front matter absent."""
    front, corps = split_front("+++\n+++\n\n## Constat\n\nx\n", FICHIER).unwrap()
    assert front == ""
    assert corps.startswith("\n## Constat")


# -------------------------------------------------- outside_fences / parse_sections
def test_titre_dans_un_bloc_de_code_n_ouvre_pas_de_section() -> None:
    """Le défaut historique : une preuve exécutée collée créait des sections fantômes."""
    corps = "## Constat\n\n```\n## pas un titre\n```\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]
    assert "## pas un titre" in parse_sections(corps)["Constat"]


def test_bloc_a_tildes() -> None:
    corps = "## Constat\n\n~~~\n## pas un titre\n~~~\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]


def test_une_cloture_plus_courte_ne_ferme_pas() -> None:
    """CommonMark : une clôture doit répéter le caractère AU MOINS autant de fois."""
    corps = "## Constat\n\n````\n```\n## avalé\n````\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]
    assert "## avalé" in parse_sections(corps)["Constat"]


def test_une_cloture_portant_une_info_string_n_en_est_pas_une() -> None:
    """« ```python » DANS un bloc ouvert par « ``` » est du contenu, pas une fermeture."""
    corps = "## Constat\n\n```\n```python\n## avalé\n```\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]


def test_un_bloc_ne_s_ouvre_pas_sur_une_info_string_a_backtick() -> None:
    """L'info string d'un bloc à backticks ne peut pas contenir de backtick."""
    lignes = dict(outside_fences("``` `x`\n## un vrai titre\n"))
    assert lignes["## un vrai titre"] is True


def test_ce_qui_precede_le_premier_titre_est_ignore() -> None:
    assert parse_sections("préambule libre\n\n## Constat\n\nx\n") == {"Constat": "x"}


def test_sections_vides_et_ordre_conserve() -> None:
    sections = parse_sections("## A\n\n## B\n\ntexte\n")
    assert list(sections) == ["A", "B"]
    assert sections["A"] == ""


# ------------------------------------------------------------------ fence_ouverte
def test_fence_refermee_ne_signale_rien() -> None:
    assert fence_ouverte("```\ncode\n```\n") is None


def test_texte_finissant_sur_la_cloture_ne_signale_rien() -> None:
    """Le cas limite : la ligne de clôture est elle-même rendue « non libre »."""
    assert fence_ouverte("avant\n```\ncode\n```") is None


def test_fence_jamais_refermee_est_nommee() -> None:
    assert fence_ouverte("## Constat\n\n```\ncode sans fin\n") == "```"


def test_une_fence_ouverte_avale_les_sections_suivantes() -> None:
    """COMPORTEMENT JUSTE, et qui doit le rester : c'est CommonMark, et l'aller-retour
    reste exact. Ce qui était faux, ce sont les diagnostics — cf. test_store_lecture."""
    corps = "## Constat\n\n```\n## Assumé\n\navalé\n"
    assert list(parse_sections(corps)) == ["Constat"]


# ------------------------------------------------- règle 1 : l'aller-retour octet
BRUT = '''+++
# un commentaire que tomllib ignore
title = "des \\"guillemets\\" et une apostrophe"
id = "z"
tags = [ "b",  "a" ]
+++

## Constat

Le corps.

## Assumé

<OPTIONNEL>
'''


def test_aller_retour_octet_pour_octet(tmp_path: Path) -> None:
    """Guillemets, ORDRE DES CLÉS et commentaires compris — c'est la règle 1."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    assert item.render() == BRUT


def test_raw_front_conserve_le_texte_brut(tmp_path: Path) -> None:
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    assert item.raw_front is not None
    assert "# un commentaire" in item.raw_front
    assert item.fields["id"] == "z"


def test_toml_invalide_est_nomme(tmp_path: Path) -> None:
    path = tmp_path / "z.md"
    _ = path.write_text("+++\nid = \n+++\n\n## Constat\n\nx\n", encoding="utf-8")
    r = read_item(path)
    assert not r
    assert "TOML invalide" in r.message


def test_fichier_illisible_est_nomme(tmp_path: Path) -> None:
    r = read_item(tmp_path / "absent.md")
    assert not r
    assert "illisible" in r.message


# ---------------------------------------- règle 2 : la frontière et le sérialiseur
def test_un_champ_modifie_declenche_la_reserialisation(tmp_path: Path) -> None:
    """LA FRONTIÈRE : with_fields met raw_front à None, et c'est le seul commutateur."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    modifie = item.with_fields(id="autre")

    assert modifie.raw_front is None
    assert "# un commentaire" not in modifie.render()
    assert 'id = "autre"' in modifie.render()


def test_with_sections_ne_reserialise_pas(tmp_path: Path) -> None:
    """Toucher le corps ne touche pas le front matter : la règle 1 y prime encore."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    modifie = item.with_sections(Constat="autre chose")

    assert modifie.raw_front is not None
    assert "# un commentaire" in modifie.render()


def test_realigned_reserialise_et_remplace(tmp_path: Path) -> None:
    """realigned REMPLACE — il sait retirer et réordonner, là où with_fields fusionne."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    aligne = item.realigned({"id": "z"}, {"Constat": "x"})

    assert aligne.raw_front is None
    assert dict(aligne.fields) == {"id": "z"}
    assert "title" not in aligne.render()


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        ("texte", '"texte"'),
        (True, "true"),
        (False, "false"),
        (7, "7"),
        (datetime.date(2026, 8, 24), "2026-08-24"),
        (["a", "b"], '["a", "b"]'),
        ([], "[]"),
    ],
)
def test_dump_value_couvre_les_types_du_contrat(valeur: object, attendu: str) -> None:
    assert dump_value(valeur, "champ") == attendu


def test_bool_est_serialise_avant_int() -> None:
    """bool EST un int en Python : l'ordre des tests du sérialiseur est ce qui décide."""
    assert dump_value(True, "x") == "true"
    assert dump_value(True, "x") != "1"


@pytest.mark.parametrize(
    ("brut", "attendu"),
    [
        ("a\nb", '"a\\nb"'),
        ("a\rb", '"a\\rb"'),
        ("a\tb", '"a\\tb"'),
        ("a\bb", '"a\\bb"'),
        ("a\fb", '"a\\fb"'),
        ('un "mot"', '"un \\"mot\\""'),
        ("c:\\chemin", '"c:\\\\chemin"'),
    ],
)
def test_echappements_relisibles(brut: str, attendu: str) -> None:
    """TOUT CE QUI EST ÉCRIT DOIT SE RELIRE : un saut de ligne non échappé fermait la
    chaîne au milieu, et migrate écrivait un fichier que tomllib refuse en rendant 0."""
    assert dump_value(brut, "x") == attendu


def test_caractere_de_controle_refuse_et_nomme() -> None:
    with pytest.raises(SerialiseError) as exc:
        _ = dump_value("a\x00b", "champ")
    assert "champ" in str(exc.value)
    assert "U+0000" in str(exc.value)


def test_type_hors_contrat_refuse_et_nomme() -> None:
    with pytest.raises(SerialiseError) as exc:
        _ = dump_value({"a": 1}, "champ")
    assert "champ" in str(exc.value)
    assert "dict" in str(exc.value)


def test_dump_front_conserve_l_ordre() -> None:
    assert dump_front({"b": "1", "a": "2"}) == 'b = "1"\na = "2"'


# ------------------------------------------------------------ write_item / relecture
def test_ecrire_puis_relire(tmp_path: Path) -> None:
    item = Item(
        tmp_path / "sous/dossier/n.md",
        {"id": "n", "title": "Titre", "tags": ["x"]},
        {"Constat": "corps"},
    )
    chemin = write_item(item).unwrap()
    relu = read_item(chemin).unwrap()

    assert relu.fields["id"] == "n"
    assert relu.fields["tags"] == ["x"]
    assert relu.sections["Constat"] == "corps"


def test_ecriture_refusee_sur_type_hors_contrat(tmp_path: Path) -> None:
    """L'échec du sérialiseur devient un Result, jamais une exception qui remonte nue."""
    item = Item(tmp_path / "n.md", {"id": "n", "bizarre": {"a": 1}}, {"Constat": "x"})
    r = write_item(item)
    assert not r
    assert "hors contrat" in r.message


def test_render_item_est_la_forme_canonique() -> None:
    item = Item(Path("/x/n.md"), {"id": "n"}, {"A": "un", "B": "deux"})
    assert render_item(item) == '+++\nid = "n"\n+++\n\n## A\n\nun\n\n## B\n\ndeux\n'
