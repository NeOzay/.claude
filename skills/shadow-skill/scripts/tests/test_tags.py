"""Le registre `tags.toml` de chaque niveau."""

from pathlib import Path

from shadow_skill import GLOBAL, LOCAL, Niveau, lire_tags, registre


def _registre(tmp_path: Path, rel: str, texte: str) -> Path:
    chemin = tmp_path / rel / "tags.toml"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")
    return chemin.parent


def test_un_registre_absent_est_vide(tmp_path: Path) -> None:
    assert lire_tags(Niveau(GLOBAL, tmp_path)).unwrap() == ()


def test_un_registre_plat_rend_ses_tags_dans_l_ordre(tmp_path: Path) -> None:
    racine = _registre(tmp_path, "g", 'neovim = "Neovim."\nlua = """Le\n  langage."""\n')
    tags = lire_tags(Niveau(GLOBAL, racine)).unwrap()
    assert [(t.nom, t.description) for t in tags] == [("neovim", "Neovim."), ("lua", "Le langage.")]


def test_une_table_ou_une_description_vide_est_fautive(tmp_path: Path) -> None:
    for texte in ('[neovim]\nx = "y"\n', 'lua = ""\n', "lua = 3\n"):
        r = lire_tags(Niveau(GLOBAL, _registre(tmp_path, "g", texte)))
        assert not r
        assert "description non vide" in r.message


def test_un_toml_invalide_est_nomme(tmp_path: Path) -> None:
    r = lire_tags(Niveau(GLOBAL, _registre(tmp_path, "g", "lua = \n")))
    assert not r
    assert "TOML invalide" in r.message


def test_le_registre_d_un_niveau_fautif_n_empeche_pas_l_autre(tmp_path: Path) -> None:
    g = _registre(tmp_path, "g", 'lua = "Lua."\n')
    loc = _registre(tmp_path, "l", "lua = \n")
    reg = registre([Niveau(GLOBAL, g), Niveau(LOCAL, loc)])
    assert [t.nom for t in reg.tags] == ["lua"]
    assert len(reg.fautes) == 1
