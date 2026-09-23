"""Contrôle de deux lexiques : doublons dans un niveau, local qui redéfinit un terme global."""

from collections.abc import Callable
from pathlib import Path

from lexique import GLOBAL, LOCAL, Terme, controler, lister, normaliser

Ecrire = Callable[[str, str], Path]


def _t(niveau: str, terme: str, ligne: int = 3) -> Terme:
    return Terme(niveau, terme, "Une définition.", "[x](y)", ligne)


def test_normaliser_casse_et_espaces() -> None:
    assert normaliser("  Signal   de\tDérive ") == "signal de dérive"


def test_aucun_constat() -> None:
    assert controler([_t(GLOBAL, "gabarit")], [_t(LOCAL, "essai")]) == []


def test_doublon_global() -> None:
    constats = controler([_t(GLOBAL, "gabarit", 3), _t(GLOBAL, "Gabarit", 5)], [])
    assert constats == ["global : « Gabarit » défini deux fois (lignes 3 et 5)."]


def test_doublon_local() -> None:
    constats = controler([], [_t(LOCAL, "essai", 3), _t(LOCAL, "essai", 4)])
    assert constats == ["local : « essai » défini deux fois (lignes 3 et 4)."]


def test_local_reserve_au_global() -> None:
    constats = controler([_t(GLOBAL, "gabarit", 3)], [_t(LOCAL, "gabarit", 7)])
    assert constats == [
        "local : « gabarit » (ligne 7) est déjà réservé au global (« gabarit », ligne 3)."
    ]


def test_local_reserve_au_global_en_variante() -> None:
    constats = controler([_t(GLOBAL, "signal de dérive")], [_t(LOCAL, "Signal  de DÉRIVE")])
    assert len(constats) == 1
    assert "déjà réservé au global" in constats[0]


def test_lister_global_d_abord(ecrire: Ecrire) -> None:
    g = ecrire("g/LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    lo = ecrire("p/.claude/LEXIQUE.md", "| Essai | Un terme local. | [x](x) |\n")
    r = lister(g, lo)
    assert r.value is not None
    assert [(t.niveau, t.terme) for t in r.value.termes] == [(GLOBAL, "Gabarit"), (LOCAL, "Essai")]
    assert r.value.constats == []


def test_lister_echoue_sur_un_lexique_malforme(ecrire: Ecrire) -> None:
    g = ecrire("g/LEXIQUE.md", "| Gabarit | Un fichier posé. |\n")
    r = lister(g, g.parent / "absent.md")
    assert not r
    assert "cellules" in r.message


def test_lister_dit_un_lexique_absent(ecrire: Ecrire) -> None:
    g = ecrire("g/LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    r = lister(g, g.parent / "absent.md")
    assert r.value is not None
    assert r.value.avis == [f"local : aucun lexique ({g.parent / 'absent.md'} absent)."]


def test_lister_dit_un_lexique_vide(ecrire: Ecrire) -> None:
    g = ecrire("g/LEXIQUE.md", "")
    lo = ecrire("p/.claude/LEXIQUE.md", "| Essai | Un terme local. | [x](x) |\n")
    r = lister(g, lo)
    assert r.value is not None
    assert r.value.avis == [f"global : lexique vide, aucun terme défini ({g})."]
    assert r.value.constats == []


def test_lister_ignore_un_local_qui_est_le_global(ecrire: Ecrire) -> None:
    """Le HOME versionné par git : sa racine git porte le global à l'emplacement du local."""
    g = ecrire("g/LEXIQUE.md", "| Gabarit | Un fichier posé. | [g](g) |\n")
    r = lister(g, g)
    assert r.value is not None
    assert r.value.constats == []
    assert [t.niveau for t in r.value.termes] == [GLOBAL]
    assert any("est le lexique global" in a for a in r.value.avis)
