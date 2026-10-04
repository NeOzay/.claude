"""Lecture des niveaux, recherche et résolution d'un shadow-skill."""

from pathlib import Path

from conftest import Poser
from shadow_skill import (
    GLOBAL,
    LOCAL,
    Niveau,
    charger,
    chercher,
    lire_niveau,
    lister,
    niveaux,
    trouver,
)


def test_un_niveau_absent_ne_rend_rien_sans_faute(tmp_path: Path) -> None:
    lu = lire_niveau(Niveau(GLOBAL, tmp_path / "absent"))
    assert (lu.skills, lu.fautes, lu.illisible) == ((), (), False)


def test_un_niveau_rend_ses_skills_dans_l_ordre(poser: Poser, tmp_path: Path) -> None:
    poser("g", "beta")
    poser("g", "alpha", tags=["lua", "tests"])
    lu = lire_niveau(Niveau(GLOBAL, tmp_path / "g"))
    assert [s.nom for s in lu.skills] == ["alpha", "beta"]
    assert lu.skills[0].tags == ("lua", "tests")


def test_un_repertoire_sans_skill_md_est_ignore(poser: Poser, tmp_path: Path) -> None:
    poser("g", "alpha")
    (tmp_path / "g" / "vide").mkdir()
    assert [s.nom for s in lire_niveau(Niveau(GLOBAL, tmp_path / "g")).skills] == ["alpha"]


def test_une_description_multiligne_tient_sur_une_ligne(poser: Poser, tmp_path: Path) -> None:
    poser("g", "alpha", description="Deux\n  lignes.")
    assert lire_niveau(Niveau(GLOBAL, tmp_path / "g")).skills[0].description == "Deux lignes."


def test_un_skill_mal_forme_est_une_faute_et_le_reste_est_servi(
    poser: Poser, tmp_path: Path
) -> None:
    poser("g", "alpha")
    poser("g", "beta", front='name = "beta"\ntags = "lua"\n')
    lu = lire_niveau(Niveau(GLOBAL, tmp_path / "g"))
    assert [s.nom for s in lu.skills] == ["alpha"]
    assert len(lu.fautes) == 1
    assert "beta" in lu.fautes[0]
    assert not lu.illisible


def test_des_tags_qui_ne_sont_pas_des_chaines_sont_une_faute(poser: Poser, tmp_path: Path) -> None:
    poser("g", "alpha", front='name = "alpha"\ndescription = "d"\nwhen-to-load = "q"\ntags = [1]\n')
    assert "tags" in lire_niveau(Niveau(GLOBAL, tmp_path / "g")).fautes[0]


def test_global_puis_local(poser: Poser, tmp_path: Path) -> None:
    poser("cfg/shadow-skills", "alpha")
    poser("p/.claude/shadow-skills", "beta")
    lu = lister(niveaux(tmp_path / "p", globale=tmp_path / "cfg"))
    assert [(s.niveau, s.nom) for s in lu.skills] == [(GLOBAL, "alpha"), (LOCAL, "beta")]


def test_un_local_confondu_avec_le_global_n_est_lu_qu_une_fois(tmp_path: Path) -> None:
    # La configuration globale est elle-même un `.claude` : son projet est son parent.
    cfg = tmp_path / ".claude"
    assert [n.nom for n in niveaux(tmp_path, globale=cfg)] == [GLOBAL]


def test_chercher_exige_chaque_mot_sans_casse(poser: Poser, tmp_path: Path) -> None:
    poser("g", "alpha", description="Tests de plugins Neovim.", tags=["lua"])
    poser("g", "beta", description="Serveur de langage.", tags=["lua", "lsp"])
    skills = lire_niveau(Niveau(GLOBAL, tmp_path / "g")).skills
    assert [s.nom for s in chercher(skills, ["LUA"])] == ["alpha", "beta"]
    assert [s.nom for s in chercher(skills, ["lua", "neovim"])] == ["alpha"]
    assert [s.nom for s in chercher(skills, ["quand", "lsp"])] == ["beta"]
    assert chercher(skills, ["absent"]) == []


def test_chercher_ignore_les_accents(poser: Poser, tmp_path: Path) -> None:
    poser("g", "alpha", description="Écrire le déploiement.", tags=["lua"])
    poser("g", "beta", description="Serveur de langage.", tags=["lua"])
    skills = lire_niveau(Niveau(GLOBAL, tmp_path / "g")).skills
    assert [s.nom for s in chercher(skills, ["deploiement"])] == ["alpha"]
    assert [s.nom for s in chercher(skills, ["ECRIRE"])] == ["alpha"]
    assert [s.nom for s in chercher(skills, ["sérveur"])] == ["beta"]


def test_trouver_un_nom_inconnu_liste_les_connus(poser: Poser, tmp_path: Path) -> None:
    poser("g", "alpha")
    r = trouver(lire_niveau(Niveau(GLOBAL, tmp_path / "g")).skills, "zeta")
    assert not r
    assert "Connus : alpha" in r.message


def test_trouver_un_nom_des_deux_niveaux_est_ambigu(poser: Poser, tmp_path: Path) -> None:
    poser("cfg/shadow-skills", "alpha")
    poser("p/.claude/shadow-skills", "alpha")
    r = trouver(lister(niveaux(tmp_path / "p", globale=tmp_path / "cfg")).skills, "alpha")
    assert not r
    assert "plusieurs niveaux" in r.message
    assert r.message.count("SKILL.md") == 2


def test_charger_donne_le_repertoire_puis_le_fichier(poser: Poser, tmp_path: Path) -> None:
    chemin = poser("g", "alpha")
    skill = trouver(lire_niveau(Niveau(GLOBAL, tmp_path / "g")).skills, "alpha").unwrap()
    texte = charger(skill).unwrap()
    assert texte.startswith(f"Répertoire : {chemin.parent}\n\n+++\n")
    assert texte.endswith("Corps.\n")
