"""`verifier` : les constats sur des skills et leur registre de tags."""

from pathlib import Path

from conftest import Poser
from shadow_skill import GLOBAL, Niveau, lister, niveaux, registre, verifier


def _tags(racine: Path, texte: str) -> None:
    racine.mkdir(parents=True, exist_ok=True)
    (racine / "tags.toml").write_text(texte, encoding="utf-8")


def _constats(tmp_path: Path) -> list[str]:
    ou = niveaux(tmp_path / "p", globale=tmp_path / "cfg")
    return verifier(lister(ou), registre(ou))


G = "cfg/shadow-skills"
L = "p/.claude/shadow-skills"


def test_un_ensemble_conforme_ne_rend_aucun_constat(poser: Poser, tmp_path: Path) -> None:
    poser(G, "alpha", tags=["lua"])
    poser(L, "beta", tags=["lua", "maison"])
    _tags(tmp_path / G, 'lua = "Lua."\n')
    _tags(tmp_path / L, 'maison = "Propre au projet."\n')
    assert _constats(tmp_path) == []


def test_aucun_skill_examine_est_un_constat(tmp_path: Path) -> None:
    assert _constats(tmp_path) == ["aucun Shadow-skill examiné"]


def test_un_tag_hors_registre_est_signale(poser: Poser, tmp_path: Path) -> None:
    poser(G, "alpha", tags=["inconnu"])
    (c,) = _constats(tmp_path)
    assert "tag « inconnu » absent du registre" in c


def test_un_tag_local_n_est_pas_connu_du_global(poser: Poser, tmp_path: Path) -> None:
    poser(G, "alpha", tags=["maison"])
    _tags(tmp_path / L, 'maison = "Propre au projet."\n')
    (c,) = _constats(tmp_path)
    assert "« maison » absent du registre" in c


def test_un_tag_local_qui_redefinit_un_global_est_signale(poser: Poser, tmp_path: Path) -> None:
    poser(G, "alpha", tags=["lua"])
    _tags(tmp_path / G, 'lua = "Lua."\n')
    _tags(tmp_path / L, 'lua = "Autre."\n')
    assert _constats(tmp_path) == ["tag « lua » : déjà déclaré au registre global"]


def test_un_nom_qui_n_est_pas_celui_du_repertoire_est_signale(poser: Poser, tmp_path: Path) -> None:
    chemin = poser(G, "alpha")
    texte = chemin.read_text(encoding="utf-8").replace('name = "alpha"', 'name = "autre"')
    chemin.write_text(texte, encoding="utf-8")
    (c,) = _constats(tmp_path)
    assert "« name » vaut « autre », le répertoire « alpha »" in c


def test_un_skill_non_conforme_a_la_semence_est_signale(poser: Poser, tmp_path: Path) -> None:
    chemin = poser(G, "alpha")
    chemin.write_text(chemin.read_text(encoding="utf-8") + "\n## Hors contrat\n\nx\n")
    (c,) = _constats(tmp_path)
    assert "non déclarée au contrat" in c


def test_une_autre_estampille_est_signalee(poser: Poser, tmp_path: Path) -> None:
    chemin = poser(G, "alpha")
    texte = chemin.read_text(encoding="utf-8").replace('gabarit = "shadow-skill"\n', "")
    chemin.write_text(texte, encoding="utf-8")
    constats = _constats(tmp_path)
    assert any("estampillé autrement" in c for c in constats)


def test_un_nom_des_deux_niveaux_est_signale(poser: Poser, tmp_path: Path) -> None:
    poser(G, "alpha")
    poser(L, "alpha")
    (c,) = _constats(tmp_path)
    assert "défini à plusieurs niveaux" in c


def test_un_skill_mal_forme_et_un_registre_fautif_sont_des_constats(
    poser: Poser, tmp_path: Path
) -> None:
    poser(G, "alpha")
    poser(G, "beta", front='name = "beta"\n')
    _tags(tmp_path / G, "lua = \n")
    constats = verifier(
        lister([Niveau(GLOBAL, tmp_path / G)]), registre([Niveau(GLOBAL, tmp_path / G)])
    )
    assert len(constats) == 2
