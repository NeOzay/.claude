"""Une List-dir dont le contrat déclare une section à motif : validée, agglomérée.

CE QUE CE FICHIER PROUVE (C6) : `validate` — bibliothèque et ligne de commande — signale
une puce fautive d'un élément en nommant section, puce et capture, et accepte un élément
conforme ; `merge` omet une section facultative restée au marqueur de son motif, même
réenroulé, ou au squelette de ses labels, et garde une section remplie ou entamée.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from jouet import element, monter_liste
from listdir import open_list
from listdir.store import ListStore

CLI = Path(__file__).resolve().parent.parent / "list-dir.py"

CONTRAT = """name = "jouet"
description = "liste-jouet à motif"

[origin]
def = false

[fields.id]
type = "slug"
description = ""

[fields.title]
type = "text"
required = true
description = ""

[sections."Constat"]
required = true
description = ""

[sections."Étapes"]
description = ""
type = "motif"
motif = "[{etat: enum}] {n: int}. {intitule}"

[sections."Étapes".captures.etat]
description = "x"
values = ["x", " "]

[sections."Étapes".captures.n]
description = "x"
sequence = true

[sections."Étapes".captures.intitule]
description = "x"
"""

MARQUEUR = "<OPTIONNEL motif: - [{etat: enum}] {n: int}. {intitule} ;;>"


def liste(tmp_path: Path, etapes: str) -> ListStore:
    racine = monter_liste(tmp_path / "jouet", CONTRAT)
    _ = element(racine, "un", corps=f"## Constat\n\nvu\n\n## Étapes\n\n{etapes}\n")
    return open_list(racine).unwrap()


def raisons(store: ListStore, filled: bool = False) -> list[str]:
    return [f"{v.subject} — {v.reason}" for v in store.validate(filled).unwrap()]


def test_validate_accepte_un_element_conforme(tmp_path: Path) -> None:
    store = liste(tmp_path, "- [x] 1. Faire ;;\n- [ ] 2. Refaire ;;")
    assert raisons(store) == []
    assert raisons(store, filled=True) == []


def test_validate_signale_une_puce_fautive(tmp_path: Path) -> None:
    store = liste(tmp_path, "- [x] 1. Faire ;;\n- [?] 2. Refaire ;;")
    assert raisons(store) == [
        'section « Étapes », puce 2, capture « etat » — « ? » hors des valeurs déclarées : x, " "'
    ]


def test_list_dir_validate_signale_la_faute(tmp_path: Path) -> None:
    store = liste(tmp_path, "- [x] 1. Faire ;;\n- [x] 3. Refaire ;;")
    r = subprocess.run(
        [sys.executable, str(CLI), "validate", str(store.path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert r.returncode == 1
    assert "section « Étapes », puce 2, capture « n » — 3 rompt la séquence" in r.stderr + r.stdout


def test_merge_omet_une_section_au_marqueur_de_motif(tmp_path: Path) -> None:
    reenroule = MARQUEUR.replace("{n: int}. ", "{n: int}.\n")
    for i, corps in enumerate((MARQUEUR, reenroule)):
        document = liste(tmp_path / str(i), corps).merge_text().unwrap()
        assert "### Constat" in document
        assert "### Étapes" not in document
        assert "OPTIONNEL" not in document


def test_merge_garde_une_section_remplie(tmp_path: Path) -> None:
    document = liste(tmp_path, "- [x] 1. Faire ;;").merge_text().unwrap()
    assert "### Étapes\n\n- [x] 1. Faire ;;" in document


ANNEXE = """
[sections."Annexe"]
description = ""
type = "label"
forme = "bold"

[sections."Annexe".labels."Source"]
description = "x"
required = true

[sections."Annexe".labels."Note"]
description = "x"
"""

SQUELETTE = "**Source** : <À REMPLIR>\n\n**Note** : <OPTIONNEL>"


def annexe(tmp_path: Path, corps: str) -> ListStore:
    racine = monter_liste(tmp_path / "jouet", CONTRAT + ANNEXE)
    _ = element(
        racine, "un", corps=f"## Constat\n\nvu\n\n## Étapes\n\n{MARQUEUR}\n\n## Annexe\n\n{corps}\n"
    )
    return open_list(racine).unwrap()


def test_merge_omet_un_squelette_de_labels_au_marqueur(tmp_path: Path) -> None:
    store = annexe(tmp_path, SQUELETTE)
    assert raisons(store, filled=True) == []
    document = store.merge_text().unwrap()
    assert "### Annexe" not in document
    assert "REMPLIR" not in document
    assert "OPTIONNEL" not in document


def test_merge_garde_un_squelette_entame(tmp_path: Path) -> None:
    corps = SQUELETTE.replace("<À REMPLIR>", "le rapport")
    document = annexe(tmp_path, corps).merge_text().unwrap()
    assert "### Annexe\n\n**Source** : le rapport" in document
