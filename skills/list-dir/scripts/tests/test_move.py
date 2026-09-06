"""store.py — déplacer un élément d'une liste vers une autre. `git mv`, et rien d'autre.

CE QUE CE FICHIER PROUVE, et qu'aucun autre ne peut prouver : que le déplacement est
un RENOMMAGE PUR. Git ne stocke pas les renommages, il les DÉDUIT de la similarité
des contenus ; réécrire le fichier dans le même commit fait tomber cette déduction
sous son seuil, et l'historique montre alors une suppression suivie d'une création —
`git log --follow` s'arrête là, et la traçabilité d'un élément soldé est perdue.

C'est aussi la seule surface du paquet qui exige un vrai dépôt. Il est monté sur
`tmp_path`, jeté avec lui, et sa configuration est LOCALE : un test qui dépendrait de
l'identité git de la machine passerait ici et nulle part ailleurs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from jouet import CONTRAT, element, monter_liste
from listdir import open_list
from listdir.store import ListStore


def git(depot: Path, *argv: str) -> str:
    """git dans le dépôt-jouet, en échec bruyant. Ce n'est pas le git du paquet."""
    proc = subprocess.run(
        ["git", *argv], cwd=depot, capture_output=True, text=True, check=True
    )
    return proc.stdout


def ouvrir(chemin: Path) -> ListStore:
    return open_list(chemin).unwrap()


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un dépôt jetable : deux listes, un élément dans la première, un commit."""
    _ = git(tmp_path, "init", "-q", "-b", "principale")
    _ = git(tmp_path, "config", "user.name", "Jouet")
    _ = git(tmp_path, "config", "user.email", "jouet@example.invalid")
    _ = git(tmp_path, "config", "commit.gpgsign", "false")

    source = monter_liste(tmp_path / "source", CONTRAT)
    _ = monter_liste(tmp_path / "cible", CONTRAT)
    _ = element(source, "entree", 'id = "entree"\ntitle = "Une entrée"\n')

    _ = git(tmp_path, "add", "-A")
    _ = git(tmp_path, "commit", "-q", "-m", "création de l'entrée")
    return tmp_path


# --------------------------------------------------------------- le cas nominal
def test_l_element_arrive_dans_la_cible(depot: Path) -> None:
    arrivee = ouvrir(depot / "source").move("entree", depot / "cible").unwrap()

    assert arrivee == depot / "cible/entree.md"
    assert arrivee.is_file()
    assert not (depot / "source/entree.md").exists()


def test_git_voit_un_renommage(depot: Path) -> None:
    """LE POINT CENTRAL : `R`, et non `D` suivi de `??`."""
    _ = ouvrir(depot / "source").move("entree", depot / "cible").unwrap()

    statut = git(depot, "status", "--porcelain")
    assert statut.startswith("R ")
    assert "source/entree.md -> cible/entree.md" in statut


def test_le_fichier_n_est_pas_reecrit(depot: Path) -> None:
    """Ce qui accompagne un déplacement — la trace d'un solde, par exemple — va dans
    un SECOND commit. Sinon la détection de renommage tombe sous son seuil."""
    avant = (depot / "source/entree.md").read_bytes()
    _ = ouvrir(depot / "source").move("entree", depot / "cible").unwrap()

    assert (depot / "cible/entree.md").read_bytes() == avant


def test_log_follow_remonte_au_commit_de_creation(depot: Path) -> None:
    """LE CRITÈRE DE RÉUSSITE DU CHANTIER D'ORIGINE : après un solde, l'historique
    d'une entrée remonte jusqu'à sa création dans la liste de départ."""
    _ = ouvrir(depot / "source").move("entree", depot / "cible").unwrap()
    _ = git(depot, "commit", "-q", "-m", "solde de l'entrée")

    historique = git(depot, "log", "--follow", "--format=%s", "--", "cible/entree.md")
    assert historique.split("\n")[:2] == ["solde de l'entrée", "création de l'entrée"]


def test_move_accepte_un_store_deja_ouvert(depot: Path) -> None:
    cible = ouvrir(depot / "cible")
    arrivee = ouvrir(depot / "source").move("entree", cible).unwrap()
    assert arrivee.parent == cible.path


def test_move_n_ecrit_dans_aucun_fichier(depot: Path) -> None:
    """L'ÉTAT EST PORTÉ PAR LE RÉPERTOIRE, jamais par un champ : changer l'état d'un
    élément, c'est le déplacer, pas lui écrire son nouvel état."""
    _ = ouvrir(depot / "source").move("entree", depot / "cible").unwrap()
    item = ouvrir(depot / "cible").get("entree").unwrap()

    assert item.raw_front is not None
    assert "solde" not in item.render()


# ----------------------------------------------------------------- les refus
def test_element_introuvable(depot: Path) -> None:
    r = ouvrir(depot / "source").move("absent", depot / "cible")
    assert not r
    assert "« absent » introuvable" in r.message


def test_cible_qui_n_est_pas_une_liste(depot: Path) -> None:
    (depot / "vrac").mkdir()
    r = ouvrir(depot / "source").move("entree", depot / "vrac")

    assert not r
    assert "contrat introuvable" in r.message
    assert (depot / "source/entree.md").is_file()


def test_meme_liste_en_source_et_en_cible(depot: Path) -> None:
    r = ouvrir(depot / "source").move("entree", depot / "source")
    assert not r
    assert "déjà dans cette liste" in r.message


def test_meme_liste_par_un_chemin_different(depot: Path) -> None:
    """La comparaison passe par resolve() : `source/../source` est la même liste."""
    r = ouvrir(depot / "source").move("entree", depot / "source/../source")
    assert not r
    assert "déjà dans cette liste" in r.message


def test_destination_deja_occupee_ne_deplace_rien(depot: Path) -> None:
    _ = element(depot / "cible", "entree", 'id = "entree"\ntitle = "Un homonyme"\n')
    r = ouvrir(depot / "source").move("entree", depot / "cible")

    assert not r
    assert "rien n'est déplacé" in r.message
    assert (depot / "source/entree.md").is_file()
    assert "Un homonyme" in (depot / "cible/entree.md").read_text(encoding="utf-8")


def test_hors_depot_git_echoue_sans_rien_perdre(tmp_path: Path) -> None:
    """git mv hors dépôt échoue : l'élément doit rester où il est."""
    source = monter_liste(tmp_path / "source", CONTRAT)
    _ = monter_liste(tmp_path / "cible", CONTRAT)
    _ = element(source, "entree", 'id = "entree"\ntitle = "T"\n')

    r = ouvrir(source).move("entree", tmp_path / "cible")

    assert not r
    assert (source / "entree.md").is_file()


# ------------------------------------------------- ce que la cible exige en plus
def test_check_item_rappelle_sans_refuser(depot: Path) -> None:
    """Le contrat d'arrivée peut exiger davantage : c'est un RAPPEL, jamais un refus.
    Le déplacement a réussi ; compléter demande un second commit."""
    exigeant = CONTRAT + '\n[fields.verdict]\ntype = "text"\nrequired = true\ndescription = ""\n'
    _ = monter_liste(depot / "cible", exigeant)

    arrivee = ouvrir(depot / "source").move("entree", depot / "cible").unwrap()
    assert arrivee.is_file()

    cible = ouvrir(depot / "cible")
    manquements = cible.check_item(cible.get("entree").unwrap())
    assert [f"{v.subject} — {v.reason}" for v in manquements] == [
        "champ « verdict » — manquant"
    ]
