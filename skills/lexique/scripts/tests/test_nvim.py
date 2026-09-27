"""Ce dont Neovim se sert : localiser un lexique, servir ses termes tolérants, en trouver un."""

from collections.abc import Callable
from pathlib import Path

from lexique import GLOBAL, LOCAL, definir, lire_valides, localiser, servir

Ecrire = Callable[[str, str], Path]


def test_localiser_global_present(ecrire: Ecrire) -> None:
    g = ecrire("LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    r = localiser(g, g.parent / "absent.md", GLOBAL)
    assert r.value == g


def test_localiser_global_absent(tmp_path: Path) -> None:
    g = tmp_path / "LEXIQUE.md"
    r = localiser(g, tmp_path / "absent.md", GLOBAL)
    assert not r
    assert f"aucun lexique global ({g} absent)" in r.message


def test_localiser_local_present(ecrire: Ecrire) -> None:
    g = ecrire("g/LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    lo = ecrire("p/.claude/LEXIQUE.md", "| Essai | Un terme local. | [x](x) |\n")
    r = localiser(g, lo, LOCAL)
    assert r.value == lo


def test_localiser_local_absent(ecrire: Ecrire) -> None:
    g = ecrire("g/LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    lo = g.parent / "p" / ".claude" / "LEXIQUE.md"
    r = localiser(g, lo, LOCAL)
    assert not r
    assert f"{lo} n'existe pas" in r.message


def test_localiser_local_egal_au_global(ecrire: Ecrire) -> None:
    g = ecrire("LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    r = localiser(g, g, LOCAL)
    assert not r
    assert "pas de lexique local" in r.message
    assert "est le lexique global" in r.message


def test_lire_valides_sert_les_lignes_valides_et_rapporte_la_faute(ecrire: Ecrire) -> None:
    chemin = ecrire(
        "LEXIQUE.md",
        "| Zorglubage | Un terme inventé. | [x](x) |\n| Autre | sans lien | pas de lien |\n",
    )
    r = lire_valides(chemin, GLOBAL)
    assert r.value is not None
    termes, fautes = r.value
    assert [t.terme for t in termes] == ["Zorglubage"]
    assert len(fautes) == 1
    assert "sans lien Markdown" in fautes[0]


def test_lire_valides_sert_les_lignes_sous_un_en_tete_fautif(ecrire: Ecrire) -> None:
    chemin = ecrire("LEXIQUE.md", "!| Mot | Def | Lien |\n|---|---|---|\n| Zorg | ok | [x](x) |\n")
    r = lire_valides(chemin, GLOBAL)
    assert r.value is not None
    termes, fautes = r.value
    assert [t.terme for t in termes] == ["Zorg"]
    assert len(fautes) == 1
    assert "en-tête attendu" in fautes[0]


def test_lire_valides_ne_sert_rien_sans_ligne_de_separation(ecrire: Ecrire) -> None:
    chemin = ecrire("LEXIQUE.md", "!| Terme | Définition | Lien |\n| Zorg | ok | [x](x) |\n")
    r = lire_valides(chemin, GLOBAL)
    assert r.value is not None
    termes, fautes = r.value
    assert termes == []
    assert "ligne de séparation" in fautes[0]


def test_lire_valides_echoue_sur_un_fichier_non_utf8(tmp_path: Path) -> None:
    chemin = tmp_path / "LEXIQUE.md"
    chemin.write_bytes("| Terme | Définition | Lien |\n".encode("latin-1"))
    r = lire_valides(chemin, GLOBAL)
    assert not r
    assert "pas en UTF-8" in r.message


def test_servir_un_niveau_illisible_laisse_servir_l_autre(ecrire: Ecrire, tmp_path: Path) -> None:
    g = tmp_path / "g" / "LEXIQUE.md"
    g.parent.mkdir(parents=True)
    g.write_bytes("| Terme | Définition | Lien |\n".encode("latin-1"))
    lo = ecrire("p/.claude/LEXIQUE.md", "| Zorglubage | Un terme local. | [x](x) |\n")
    s = servir(g, lo)
    assert [t.terme for t in s.termes] == ["Zorglubage"]
    assert len(s.erreurs) == 1
    assert "pas en UTF-8" in s.erreurs[0]


def test_servir_rapporte_un_doublon(ecrire: Ecrire) -> None:
    g = ecrire("g/LEXIQUE.md", "| Zorglubage | Un. | [x](x) |\n| ZORGLUBAGE | Deux. | [x](x) |\n")
    lo = g.parent / "p" / ".claude" / "LEXIQUE.md"
    s = servir(g, lo)
    assert s.erreurs == []
    assert any("défini deux fois" in c for c in s.signalements)


def test_definir_a_la_casse_et_aux_espaces_pres(ecrire: Ecrire) -> None:
    g = ecrire("LEXIQUE.md", "| Signal de dérive | Ce qui arrête. | [x](x) |\n")
    s = servir(g, g.parent / "p" / ".claude" / "LEXIQUE.md")
    assert [t.terme for t in definir(s.termes, "signal  de DÉRIVE")] == ["Signal de dérive"]


def test_definir_aucune_correspondance(ecrire: Ecrire) -> None:
    g = ecrire("LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    s = servir(g, g.parent / "p" / ".claude" / "LEXIQUE.md")
    assert definir(s.termes, "Zorglubage") == []
