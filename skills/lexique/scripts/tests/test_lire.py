"""Lecture d'un lexique : le format accepté, et chaque faute nommée."""

from collections.abc import Callable
from pathlib import Path

from lexique import GLOBAL, lire

Ecrire = Callable[[str, str], Path]


def test_format_accepte(ecrire: Ecrire) -> None:
    chemin = ecrire(
        "LEXIQUE.md",
        "!Une phrase avant.\n\n| Terme | Définition | Lien |\n|:--|---|--:|\n"
        "| Signal de dérive | Ce qui arrête. | [brief](skills/intent-brief/SKILL.md) |\n"
        "| A \\| b | Un pipe échappé. | [x](y) |\n\nUne phrase après.\n",
    )
    r = lire(chemin, GLOBAL)
    assert r.value is not None
    assert [(t.terme, t.ligne) for t in r.value] == [("Signal de dérive", 5), ("A \\| b", 6)]
    assert r.value[0].niveau == GLOBAL


def test_fichier_absent_ne_porte_aucun_terme(tmp_path: Path) -> None:
    r = lire(tmp_path / "absent.md", GLOBAL)
    assert r and r.value == []


def test_tableau_vide_accepte(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", ""), GLOBAL)
    assert r and r.value == []


def test_entete_faux(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "!| Mot | Sens | Lien |\n|---|---|---|\n"), GLOBAL)
    assert not r
    assert "en-tête attendu" in r.message


def test_separation_absente(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "!| Terme | Définition | Lien |\n| a | b | [c](d) |\n"), GLOBAL)
    assert not r
    assert "séparation" in r.message


def test_ligne_a_deux_cellules(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "| A | b |\n"), GLOBAL)
    assert not r
    assert "2 cellules, 3 attendues" in r.message


def test_cellule_vide(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "| A |  | [c](d) |\n"), GLOBAL)
    assert not r
    assert "cellule vide" in r.message


def test_lien_absent(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "| A | b | skills/gabarit |\n"), GLOBAL)
    assert not r
    assert "sans lien Markdown" in r.message


def test_deux_tableaux(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "| A | b | [c](d) |\n\n| E | f | [g](h) |\n"), GLOBAL)
    assert not r
    assert "2 tableaux" in r.message


def test_aucun_tableau(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "!De la prose seule.\n"), GLOBAL)
    assert not r
    assert "aucun tableau" in r.message


def test_toutes_les_fautes_d_un_coup(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "| A | b |\n| C | d | e |\n"), GLOBAL)
    assert not r
    assert len(r.message.splitlines()) == 2


def test_terme_sans_majuscule(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "| suivi | Le fichier d'un chantier. | [x](y) |\n"), GLOBAL)
    assert not r
    assert "« suivi » doit commencer par une majuscule" in r.message


def test_majuscule_accentuee(ecrire: Ecrire) -> None:
    r = lire(ecrire("LEXIQUE.md", "| Étape | Une unité du plan. | [x](y) |\n"), GLOBAL)
    assert r.value is not None
    assert r.value[0].terme == "Étape"


def test_tableau_en_bloc_de_code_ignore(ecrire: Ecrire) -> None:
    corps = (
        "!Exemple :\n\n```markdown\n| Terme | Définition | Lien |\n|---|---|---|\n"
        "| <terme> | <phrase> | [x](y) |\n```\n\n"
        "| Terme | Définition | Lien |\n|---|---|---|\n| Essai | Un terme. | [x](y) |\n"
    )
    r = lire(ecrire("LEXIQUE.md", corps), GLOBAL)
    assert r.value is not None
    assert [t.terme for t in r.value] == ["Essai"]


def test_fichier_non_utf8(tmp_path: Path) -> None:
    chemin = tmp_path / "LEXIQUE.md"
    chemin.write_bytes("| Terme | Définition | Lien |\n".encode("latin-1"))
    r = lire(chemin, GLOBAL)
    assert not r
    assert "pas en UTF-8" in r.message
