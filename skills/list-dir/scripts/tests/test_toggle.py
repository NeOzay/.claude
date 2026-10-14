"""store.py — `toggle` : inverser un booléen écrit.

CE QUE CE FICHIER PROUVE : que `toggle` inverse le seul booléen écrit des éléments
désignés, qu'il ne réécrit du fichier que la ligne du champ, et qu'il refuse sans rien
écrire ce qui n'a pas d'état à inverser — autre type, marqueur, champ absent ou déprécié.
"""

from __future__ import annotations

from pathlib import Path

from jouet import element, monter_liste
from listdir import open_list
from listdir.store import ListStore
from test_fill import CONTRAT_FILL


def ouvrir(chemin: Path) -> ListStore:
    return open_list(chemin).unwrap()


def front(liste: Path, item_id: str) -> str:
    return (liste / f"{item_id}.md").read_text(encoding="utf-8")


def liste_de_pins(tmp_path: Path) -> Path:
    """`a` épinglé, `b` non, `c` au marqueur, `d` sans `pin`."""
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = (liste / "a.md").write_text(
        '+++\n# légende\nid = "a"\ntitle = "A"\npin = true\ntags = [\n  "x",\n]\n+++\n\n'
        "## Constat\n\nx\n",
        encoding="utf-8",
    )
    _ = element(liste, "b", 'id = "b"\ntitle = "B"\npin = false\n')
    _ = element(liste, "c", 'id = "c"\ntitle = "C"\npin = "<À REMPLIR bool>"\n')
    _ = element(liste, "d", 'id = "d"\ntitle = "D"\n')
    return liste


def test_true_devient_false_et_l_inverse(tmp_path: Path) -> None:
    liste = liste_de_pins(tmp_path)

    _ = ouvrir(liste).toggle("pin", ["a", "b"]).unwrap()

    lst = ouvrir(liste)
    assert lst.get("a").unwrap().fields["pin"] is False
    assert lst.get("b").unwrap().fields["pin"] is True


def test_seule_la_ligne_du_champ_change(tmp_path: Path) -> None:
    liste = liste_de_pins(tmp_path)
    avant = front(liste, "a")

    changes = ouvrir(liste).toggle("pin", ["a"]).unwrap()

    assert front(liste, "a") == avant.replace("pin = true", "pin = false")
    assert str(changes[0]).endswith("champ « pin » — « true » remplacé par « false »")


def test_un_second_toggle_revient_a_l_etat_de_depart(tmp_path: Path) -> None:
    liste = liste_de_pins(tmp_path)
    avant = front(liste, "a")

    _ = ouvrir(liste).toggle("pin", ["a"]).unwrap()
    _ = ouvrir(liste).toggle("pin", ["a"]).unwrap()

    assert front(liste, "a") == avant


def test_un_id_repete_n_inverse_qu_une_fois(tmp_path: Path) -> None:
    liste = liste_de_pins(tmp_path)

    _ = ouvrir(liste).toggle("pin", ["b", "b"]).unwrap()

    assert ouvrir(liste).get("b").unwrap().fields["pin"] is True


def test_dry_run_n_ecrit_rien(tmp_path: Path) -> None:
    liste = liste_de_pins(tmp_path)
    avant = front(liste, "a")

    changes = ouvrir(liste).toggle("pin", ["a"], dry_run=True).unwrap()

    assert len(changes) == 1
    assert front(liste, "a") == avant


def test_sans_id_echoue_en_code_2(tmp_path: Path) -> None:
    r = ouvrir(liste_de_pins(tmp_path)).toggle("pin", [])

    assert not r
    assert r.status == 2
    assert "toggle ne vaut que pour des éléments désignés" in r.message


def test_refus_sans_rien_ecrire(tmp_path: Path) -> None:
    """Non-bool, marqueur, champ absent, déprécié, non déclaré, id inconnu."""
    liste = liste_de_pins(tmp_path)
    avant = {p.name: p.read_text(encoding="utf-8") for p in liste.glob("*.md")}
    lst = ouvrir(liste)

    refus = {
        "non-bool": lst.toggle("compte", ["a"]),
        "marqueur": lst.toggle("pin", ["c"]),
        "absent": lst.toggle("pin", ["d"]),
        "déprécié": lst.toggle("ancien", ["a"]),
        "non déclaré": lst.toggle("severite", ["a"]),
        "id inconnu": lst.toggle("pin", ["a", "z"]),
    }

    assert [k for k, r in refus.items() if r] == []
    assert "de type int — toggle ne bascule qu'un bool" in refus["non-bool"].message
    assert "c.md: champ « pin » au marqueur" in refus["marqueur"].message
    assert "d.md: champ « pin » absent" in refus["absent"].message
    assert "déprécié" in refus["déprécié"].message
    assert "non déclaré au contrat" in refus["non déclaré"].message
    assert "élément « z » introuvable" in refus["id inconnu"].message
    assert {p.name: p.read_text(encoding="utf-8") for p in liste.glob("*.md")} == avant
