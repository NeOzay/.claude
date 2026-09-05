"""Découverte et résolution des définitions de listes.

CE QUI SE JOUE ICI EST UN ORDRE, pas une lecture de fichier : quelle racine gagne,
laquelle masque l'autre, et laquelle refuse de choisir. Les deux ancrages sont des
paramètres de `roots()` — c'est ce qui permet de monter les quatre rangs sur
`tmp_path` et de ne jamais lire le vrai dépôt, comme le reste de la suite.
"""

from __future__ import annotations

from pathlib import Path

from jouet import CONTRAT, ecrire
from listdir.definitions import (
    config_root,
    definitions,
    project_root,
    resolve,
    roots,
)


def definition(base: Path, nom: str, contrat: str = CONTRAT) -> Path:
    """Une définition : un répertoire portant un `contract.toml`."""
    _ = ecrire(base, f"{nom}/contract.toml", contrat)
    return base / nom


# ------------------------------------------------------------------ les ancrages
def test_project_root_remonte_jusqu_au_premier_claude(tmp_path: Path) -> None:
    (tmp_path / "projet" / ".claude").mkdir(parents=True)
    profond = tmp_path / "projet" / "src" / "a" / "b"
    profond.mkdir(parents=True)
    assert project_root(profond) == tmp_path / "projet" / ".claude"


def test_project_root_rend_none_hors_de_tout_projet(tmp_path: Path) -> None:
    """Un état légitime : les rangs 1 et 2 sont alors simplement absents."""
    nu = tmp_path / "nu"
    nu.mkdir()
    assert project_root(nu) is None


def test_config_root_veut_un_repertoire_nomme_claude(tmp_path: Path) -> None:
    """La distinction qui porte le cas imbriqué.

    `config/.claude` CONTIENT un `.claude` ET EST un `.claude` selon d'où on regarde :
    depuis le paquet, c'est lui qu'on veut, pas son enfant.
    """
    paquet = tmp_path / ".claude" / "skills" / "list-dir" / "scripts" / "listdir"
    paquet.mkdir(parents=True)
    (tmp_path / ".claude" / ".claude").mkdir()

    assert config_root(paquet) == tmp_path / ".claude"
    # La règle du projet, elle, descend d'un cran — d'où les deux fonctions.
    assert project_root(paquet) == tmp_path / ".claude" / ".claude"


def test_config_root_rend_none_hors_de_toute_configuration(tmp_path: Path) -> None:
    ailleurs = tmp_path / "opt" / "list-dir"
    ailleurs.mkdir(parents=True)
    assert config_root(ailleurs) is None


# --------------------------------------------------------------------- les rangs
def test_les_quatre_rangs_dans_l_ordre_de_specificite(tmp_path: Path) -> None:
    projet = tmp_path / "projet"
    config = tmp_path / "config" / ".claude"
    _ = definition(projet / ".claude" / "list-dir", "a")
    _ = definition(projet / ".claude" / "skills" / "s1" / "list-dir", "b")
    _ = definition(config / "list-dir", "c")
    _ = definition(config / "skills" / "s2" / "list-dir", "d")

    trouves = roots(cwd=projet, package=config / "skills" / "list-dir" / "scripts")
    assert [r.rank for r in trouves] == [1, 2, 3, 4]
    assert [r.origin for r in trouves] == ["projet", "projet:s1", "config", "config:s2"]


def test_aucune_racine_est_un_etat_legitime(tmp_path: Path) -> None:
    nu = tmp_path / "nu"
    nu.mkdir()
    assert roots(cwd=nu, package=nu) == []
    assert definitions(roots(cwd=nu, package=nu)) == {}


def test_racine_atteinte_deux_fois_n_est_comptee_qu_une(tmp_path: Path) -> None:
    """Le cas réel du dépôt de configuration : il EST `.claude` et en CONTIENT un.

    Sans déduplication sur chemin résolu, la même racine se dénoncerait comme
    ambiguë avec elle-même dès qu'une définition y serait posée.
    """
    config = tmp_path / ".claude"
    _ = definition(config / "list-dir", "a")

    trouves = roots(cwd=config, package=config / "skills" / "list-dir")
    chemins = [r.path.resolve() for r in trouves]
    assert len(chemins) == len(set(chemins))
    assert resolve("a", trouves).unwrap() == config / "list-dir" / "a"


# ---------------------------------------------------------------- la résolution
def test_definition_trouvee_dans_un_skill_de_la_configuration(tmp_path: Path) -> None:
    config = tmp_path / ".claude"
    attendu = definition(config / "skills" / "tracker" / "list-dir", "recettes")

    trouve = resolve("recettes", roots(cwd=tmp_path / "vide", package=config / "skills"))
    assert trouve.unwrap() == attendu


def test_le_rang_le_plus_specifique_masque_l_autre(tmp_path: Path) -> None:
    """Masquer est le comportement voulu, pas un conflit : c'est ainsi qu'un projet
    reprend la main sur une définition de la configuration."""
    projet = tmp_path / "projet"
    config = tmp_path / "config" / ".claude"
    attendu = definition(projet / ".claude" / "list-dir", "recettes")
    _ = definition(config / "skills" / "tracker" / "list-dir", "recettes")

    trouve = resolve("recettes", roots(cwd=projet, package=config / "skills"))
    assert trouve
    assert trouve.unwrap() == attendu


def test_deux_racines_de_meme_rang_refusent_de_choisir(tmp_path: Path) -> None:
    """Choisir en silence ferait dépendre le contrat d'une liste de l'ordre de
    parcours d'un répertoire."""
    config = tmp_path / ".claude"
    _ = definition(config / "skills" / "un" / "list-dir", "recettes")
    _ = definition(config / "skills" / "deux" / "list-dir", "recettes")

    trouve = resolve("recettes", roots(cwd=tmp_path / "vide", package=config / "skills"))
    assert not trouve
    assert "ambiguë" in trouve.message
    assert "un/list-dir/recettes" in trouve.message
    assert "deux/list-dir/recettes" in trouve.message


def test_nom_inconnu_liste_les_noms_connus(tmp_path: Path) -> None:
    config = tmp_path / ".claude"
    _ = definition(config / "list-dir", "alpha")
    _ = definition(config / "list-dir", "beta")

    trouve = resolve("gamma", roots(cwd=tmp_path / "vide", package=config / "skills"))
    assert not trouve
    assert "introuvable" in trouve.message
    assert "alpha, beta" in trouve.message


def test_nom_de_gabarit_refuse_en_disant_ce_qu_il_est(tmp_path: Path) -> None:
    """Un gabarit n'est pas une définition : il projette une liste qui existe déjà.

    Le chercher dans les rangs rendrait « introuvable » sur un nom parfaitement
    valide, et enverrait chercher là où il n'a jamais été.
    """
    _ = definition(tmp_path / ".claude" / "list-dir", "technical-debt")
    r = resolve("technical-debt/review", roots(cwd=tmp_path, package=tmp_path))

    assert not r
    assert "introuvable" not in r.message
    assert "review" in r.message and "technical-debt" in r.message
    assert "--template review" in r.message


def test_un_nom_composite_mal_forme_ne_conseille_pas_une_commande_inutilisable() -> None:
    """La FORME se juge avant le sens, sinon le refus conseille ce qui ne marchera pas.

    « technical-debt/ » nommerait un gabarit vide et conseillerait « --template  » ;
    « a/b/c » inventerait un gabarit « b/c ». Un message qui envoie taper une commande
    vouée à échouer est un échec ouvert de plus, pas une aide.
    """
    for nom in ("technical-debt/", "/x", "../x", "a/b/c"):
        r = resolve(nom, [])
        assert not r, nom
        assert "--template " not in r.message, nom
        assert "n'est pas un nom de semence" in r.message, nom


def test_le_refus_du_gabarit_ne_depend_d_aucune_racine() -> None:
    """Il se prononce sur la FORME du nom : aucune racine n'a besoin d'exister."""
    r = resolve("a/b", [])

    assert not r
    assert "gabarit" in r.message


def test_repertoire_sans_contrat_n_est_pas_une_definition(tmp_path: Path) -> None:
    """Le proposer à `--def` reviendrait à promettre un amorçage qui échouerait
    ensuite sur un fichier manquant."""
    config = tmp_path / ".claude"
    (config / "list-dir" / "vide").mkdir(parents=True)
    _ = definition(config / "list-dir", "pleine")

    noms = definitions(roots(cwd=tmp_path / "ailleurs", package=config / "skills"))
    assert sorted(noms) == ["pleine"]


def test_definitions_conserve_toutes_les_racines_d_un_nom(tmp_path: Path) -> None:
    """C'est cette liste qui permet à `defs` de dire « masquée » plutôt que de
    taire l'exemplaire perdant."""
    projet = tmp_path / "projet"
    config = tmp_path / "config" / ".claude"
    _ = definition(projet / ".claude" / "list-dir", "recettes")
    _ = definition(config / "list-dir", "recettes")

    noms = definitions(roots(cwd=projet, package=config / "skills"))
    assert [r.rank for r in noms["recettes"]] == [1, 3]


def test_aucun_test_ne_lit_le_vrai_depot(tmp_path: Path) -> None:
    trouves = roots(cwd=tmp_path, package=tmp_path)
    assert all(tmp_path in r.path.parents or r.path == tmp_path for r in trouves)
