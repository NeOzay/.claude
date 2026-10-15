"""store.py — `fill` : poser une valeur sur un champ resté au marqueur.

CE QUE CE FICHIER PROUVE : que `fill` écrit la valeur de l'appelant sur les seuls champs
au marqueur, qu'il ne touche jamais une valeur écrite, qu'il refuse avant toute écriture
une valeur que le type déclaré refuse, et qu'il ne réécrit du fichier que la ligne du
champ. C'est ce qui permet à un agent d'écrire par lui sans édition libre.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from jouet import CONTRAT, element, monter_liste
from listdir import open_list
from listdir.store import ListStore

CONTRAT_FILL = (
    CONTRAT
    + """
[fields.pin]
type = "bool"
description = ""

[fields.compte]
type = "int"
description = ""

[fields.ancien]
type = "text"
deprecated = "remplacé par title"
description = ""
"""
)


def ouvrir(chemin: Path) -> ListStore:
    return open_list(chemin).unwrap()


def liste_au_marqueur(tmp_path: Path) -> Path:
    """Trois éléments : deux `category` au marqueur, un déjà rempli."""
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = element(liste, "a", 'id = "a"\ntitle = "A"\ncategory = "<À REMPLIR>"\n')
    _ = element(liste, "b", 'id = "b"\ntitle = "B"\ncategory = "<OPTIONNEL>"\n')
    _ = element(liste, "c", 'id = "c"\ntitle = "C"\ncategory = "vert"\n')
    return liste


def front(liste: Path, item_id: str) -> str:
    return (liste / f"{item_id}.md").read_text(encoding="utf-8")


# --------------------------------------------------------------- le cas nominal
def test_remplit_les_seuls_champs_au_marqueur(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)

    changes = ouvrir(liste).fill("category", "rouge").unwrap()

    assert [c.path.stem for c in changes] == ["a", "b"]
    lst = ouvrir(liste)
    assert lst.get("a").unwrap().fields["category"] == "rouge"
    assert lst.get("b").unwrap().fields["category"] == "rouge"
    assert lst.get("c").unwrap().fields["category"] == "vert"


def test_le_changement_nomme_l_ancien_marqueur_et_la_valeur(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)

    changes = ouvrir(liste).fill("category", "rouge", ["a"]).unwrap()

    assert str(changes[0]).endswith("champ « category » — « <À REMPLIR> » remplacé par « rouge »")


def test_seule_la_ligne_du_champ_change(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    avant = (
        '+++\n# légende\nid = "a"\ntitle = "A"\ncategory = "<À REMPLIR>"\n'
        'tags = [\n  "x",\n  "y",\n]\n+++\n\n## Constat\n\nx\n'
    )
    _ = (liste / "a.md").write_text(avant, encoding="utf-8")

    _ = ouvrir(liste).fill("category", "vert").unwrap()

    assert front(liste, "a") == avant.replace('"<À REMPLIR>"', '"vert"')


def test_rejouer_ne_touche_aucun_fichier(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)
    _ = ouvrir(liste).fill("category", "rouge").unwrap()
    dates = {p.name: p.stat().st_mtime_ns for p in liste.glob("*.md")}

    assert ouvrir(liste).fill("category", "rouge").unwrap() == []
    assert {p.name: p.stat().st_mtime_ns for p in liste.glob("*.md")} == dates


def test_dry_run_n_ecrit_rien(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)
    avant = front(liste, "a")

    changes = ouvrir(liste).fill("category", "rouge", dry_run=True).unwrap()

    assert len(changes) == 2
    assert front(liste, "a") == avant


def test_un_champ_absent_est_saute(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = element(liste, "a", 'id = "a"\ntitle = "A"\n')

    assert ouvrir(liste).fill("category", "rouge").unwrap() == []
    assert "category" not in ouvrir(liste).get("a").unwrap().fields


# ------------------------------------------------------------- conversion au type
def test_un_bool_s_ecrit_en_booleen(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = element(liste, "a", 'id = "a"\ntitle = "A"\npin = "<À REMPLIR bool>"\n')

    _ = ouvrir(liste).fill("pin", "false").unwrap()

    assert ouvrir(liste).get("a").unwrap().fields["pin"] is False
    assert "pin = false\n" in front(liste, "a")


def test_un_int_et_une_date_s_ecrivent_types(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = element(
        liste,
        "a",
        'id = "a"\ntitle = "A"\ndate = "<OPTIONNEL date>"\ncompte = "<OPTIONNEL int>"\n',
    )

    _ = ouvrir(liste).fill("compte", "3").unwrap()
    _ = ouvrir(liste).fill("date", "2026-10-07").unwrap()

    fields = ouvrir(liste).get("a").unwrap().fields
    assert fields["compte"] == 3
    assert fields["date"] == datetime.date(2026, 10, 7)


# --------------------------------------------------------------------- refus
def test_valeur_hors_enum_refusee_sans_rien_ecrire(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)
    avant = front(liste, "a")

    r = ouvrir(liste).fill("category", "bleu")

    assert not r
    assert "hors des valeurs déclarées : rouge, vert" in r.message
    assert front(liste, "a") == avant


def test_bool_ambigu_refuse(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = element(liste, "a", 'id = "a"\ntitle = "A"\npin = "<À REMPLIR bool>"\n')

    r = ouvrir(liste).fill("pin", "True")

    assert not r
    assert "ni « true » ni « false »" in r.message


def test_date_non_iso_refusee(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = element(liste, "a", 'id = "a"\ntitle = "A"\ndate = "<OPTIONNEL date>"\n')

    r = ouvrir(liste).fill("date", "07/10/2026")

    assert not r
    assert "n'est pas une date ISO" in r.message


def test_un_marqueur_n_est_pas_une_valeur(tmp_path: Path) -> None:
    r = ouvrir(liste_au_marqueur(tmp_path)).fill("category", "<OPTIONNEL>")

    assert not r
    assert "est un marqueur, pas une valeur" in r.message


def test_champ_non_declare_refuse(tmp_path: Path) -> None:
    r = ouvrir(liste_au_marqueur(tmp_path)).fill("severite", "note")

    assert not r
    assert "champ « severite » non déclaré au contrat" in r.message


def test_champ_deprecie_refuse(tmp_path: Path) -> None:
    r = ouvrir(liste_au_marqueur(tmp_path)).fill("ancien", "x")

    assert not r
    assert "déprécié — remplacé par title" in r.message


# --------------------------------------------------------------------- --id
def test_id_ne_remplit_que_l_element_designe(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)

    changes = ouvrir(liste).fill("category", "vert", ["b"]).unwrap()

    assert [c.path.stem for c in changes] == ["b"]
    assert ouvrir(liste).get("a").unwrap().fields["category"] == "<À REMPLIR>"


def test_id_deja_rempli_echoue_sans_rien_ecrire(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)
    avant = front(liste, "a")

    r = ouvrir(liste).fill("category", "rouge", ["a", "c"])

    assert not r
    assert "c.md: champ « category » déjà rempli, « vert »" in r.message
    assert front(liste, "a") == avant


def test_id_au_champ_absent_echoue(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    _ = element(liste, "a", 'id = "a"\ntitle = "A"\n')

    r = ouvrir(liste).fill("category", "rouge", ["a"])

    assert not r
    assert "champ « category » absent" in r.message


def test_id_inconnu_echoue(tmp_path: Path) -> None:
    r = ouvrir(liste_au_marqueur(tmp_path)).fill("category", "rouge", ["z"])

    assert not r
    assert "élément « z » introuvable" in r.message


# ------------------------------------------------------------------- --override
def liste_ecrite(tmp_path: Path) -> Path:
    """Un élément `a` dont tous les champs sont écrits, `b` voisin pour le contrôle."""
    liste = monter_liste(tmp_path / "jouet", CONTRAT_FILL)
    ecrit = (
        '+++\n# légende\nid = "{i}"\ntitle = "T"\ndate = 2026-08-24\ncategory = "rouge"\n'
        'pin = false\ncompte = 3\ntags = ["x"]\nancien = "z"\n+++\n\n## Constat\n\nx\n'
    )
    for ident in ("a", "b"):
        _ = (liste / f"{ident}.md").write_text(ecrit.format(i=ident), encoding="utf-8")
    return liste


def test_override_reecrit_un_bool_et_seule_sa_ligne_change(tmp_path: Path) -> None:
    liste = liste_ecrite(tmp_path)
    avant = front(liste, "a")

    changes = ouvrir(liste).fill("pin", "true", ["a"], override=True).unwrap()

    assert str(changes[0]).endswith("champ « pin » — « false » remplacé par « true »")
    assert front(liste, "a") == avant.replace("pin = false", "pin = true")
    assert ouvrir(liste).get("a").unwrap().fields["pin"] is True


def test_override_d_une_valeur_multiligne_tient_sur_une_ligne(tmp_path: Path) -> None:
    """UN CHANGEMENT, UNE LIGNE, comme pour `migrate`."""
    liste = liste_ecrite(tmp_path)

    changes = ouvrir(liste).fill("title", "ligne1\nligne2", ["a"], override=True).unwrap()

    assert str(changes[0]).endswith("champ « title » — « T » remplacé par « ligne1 … »")
    assert ouvrir(liste).get("a").unwrap().fields["title"] == "ligne1\nligne2"


def test_override_reecrit_text_int_date_et_enum(tmp_path: Path) -> None:
    liste = liste_ecrite(tmp_path)

    _ = ouvrir(liste).fill("title", "Neuf", ["a"], override=True).unwrap()
    _ = ouvrir(liste).fill("compte", "7", ["a"], override=True).unwrap()
    _ = ouvrir(liste).fill("date", "2026-10-14", ["a"], override=True).unwrap()
    _ = ouvrir(liste).fill("category", "vert", ["a"], override=True).unwrap()

    fields = ouvrir(liste).get("a").unwrap().fields
    assert fields["title"] == "Neuf"
    assert fields["compte"] == 7
    assert fields["date"] == datetime.date(2026, 10, 14)
    assert fields["category"] == "vert"
    assert ouvrir(liste).get("b").unwrap().fields["compte"] == 3


def test_override_pose_encore_un_champ_au_marqueur(tmp_path: Path) -> None:
    liste = liste_au_marqueur(tmp_path)

    changes = ouvrir(liste).fill("category", "vert", ["a"], override=True).unwrap()

    assert [c.path.stem for c in changes] == ["a"]
    assert ouvrir(liste).get("a").unwrap().fields["category"] == "vert"


def test_override_valeur_identique_ne_touche_aucun_fichier(tmp_path: Path) -> None:
    liste = liste_ecrite(tmp_path)
    dates = {p.name: p.stat().st_mtime_ns for p in liste.glob("*.md")}

    assert ouvrir(liste).fill("pin", "false", ["a"], override=True).unwrap() == []
    assert ouvrir(liste).fill("compte", "3", ["a", "b"], override=True).unwrap() == []
    assert {p.name: p.stat().st_mtime_ns for p in liste.glob("*.md")} == dates


def test_override_dry_run_n_ecrit_rien(tmp_path: Path) -> None:
    liste = liste_ecrite(tmp_path)
    avant = front(liste, "a")

    changes = ouvrir(liste).fill("pin", "true", ["a"], override=True, dry_run=True).unwrap()

    assert len(changes) == 1
    assert front(liste, "a") == avant


def test_override_sans_id_echoue_en_code_2(tmp_path: Path) -> None:
    liste = liste_ecrite(tmp_path)
    avant = front(liste, "a")

    r = ouvrir(liste).fill("pin", "true", override=True)

    assert not r
    assert r.status == 2
    assert "override ne vaut que pour des éléments désignés" in r.message
    assert front(liste, "a") == avant


def test_override_refuse_sans_rien_ecrire(tmp_path: Path) -> None:
    """list, deprecated, id, champ absent, et les valeurs que le contrat refuse."""
    liste = liste_ecrite(tmp_path)
    _ = (liste / "c.md").write_text('+++\nid = "c"\ntitle = "T"\n+++\n\n## Constat\n\nx\n')
    avant = {p.name: p.read_text(encoding="utf-8") for p in liste.glob("*.md")}
    lst = ouvrir(liste)

    refus = {
        "list": lst.fill("tags", "y", ["a"], override=True),
        "deprecated": lst.fill("ancien", "y", ["a"], override=True),
        "id": lst.fill("id", "b", ["a"], override=True),
        "absent": lst.fill("category", "vert", ["c"], override=True),
        "enum": lst.fill("category", "bleu", ["a"], override=True),
        "date": lst.fill("date", "07/10/2026", ["a"], override=True),
        "bool": lst.fill("pin", "True", ["a"], override=True),
    }

    assert [k for k, r in refus.items() if r] == []
    assert "de type list" in refus["list"].message
    assert "déprécié" in refus["deprecated"].message
    assert "il vaut le nom du fichier" in refus["id"].message
    assert "champ « category » absent" in refus["absent"].message
    assert {p.name: p.read_text(encoding="utf-8") for p in liste.glob("*.md")} == avant


def test_override_verifie_tout_avant_d_ecrire(tmp_path: Path) -> None:
    liste = liste_ecrite(tmp_path)
    avant = front(liste, "a")

    r = ouvrir(liste).fill("pin", "true", ["a", "z"], override=True)

    assert not r
    assert front(liste, "a") == avant


def test_sans_override_une_valeur_ecrite_reste_refusee(tmp_path: Path) -> None:
    liste = liste_ecrite(tmp_path)
    avant = front(liste, "a")

    r = ouvrir(liste).fill("pin", "true", ["a"])

    assert not r
    assert "a.md: champ « pin » déjà rempli, « false »" in r.message
    assert front(liste, "a") == avant
