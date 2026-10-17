"""`check` sur une section à motif : un fichier conforme passe, chaque faute est nommée.

CE QUE CE FICHIER PROUVE (C1) : une section à motif passe avec des puces multilignes,
des lignes vides entre puces, un « ; » ou un « ;; » intérieur, `[ ]` et une capture
facultative vide ; chaque faute — `fin` manquante, texte hors puce, puce imbriquée,
puce hors motif, valeur hors `values`, `int` mal écrit ou hors min-max, `sequence`
rompue ou mal partie, slug invalide — est nommée par section, puce et capture ; une
section restée au marqueur n'est pas jugée. Le dernier bloc lance le point d'entrée.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from gabarit.check import check_item
from gabarit.contract import parse_contract
from gabarit.types import Contract, Item

CLI = Path(__file__).resolve().parent.parent / "gabarit-cli.py"

CONTRAT = """name = "essai"
description = ""

[sections."Étapes"]
description = ""
required = true
type = "motif"
motif = "[{etat: enum}] {n: int}. {intitule} — {lot: slug} — vérif: {verif}"

[sections."Étapes".captures.etat]
description = "l'état"
values = ["x", ">", "!", " "]

[sections."Étapes".captures.n]
description = "le numéro"
min = 1
max = 5
sequence = true

[sections."Étapes".captures.intitule]
description = "ce qu'elle fait"

[sections."Étapes".captures.lot]
description = "le lot"

[sections."Étapes".captures.verif]
description = "la commande"
required = false
"""

CONFORME = """\
- [x] 1. Écrire le contrat — a — vérif: `pytest; echo $?` ;;

- [ ] 2. Une puce qui court
  sur deux lignes ; avec un « ; » — b — vérif: x ;;
- [>] 3. Un « ;; » en fin de ligne ;;
  ne ferme rien — c — vérif: ;;
- [!] 4. Bloquée — d-e — vérif: y ;;
"""


def contrat(tmp_path: Path) -> Contract:
    return parse_contract(CONTRAT, tmp_path / "contract.toml").unwrap()


def fautes(tmp_path: Path, corps: str) -> list[str]:
    item = Item(tmp_path / "essai.md", {}, {"Étapes": corps})
    return [f"{v.subject} — {v.reason}" for v in check_item(contrat(tmp_path), item)]


def puce(n: int, etat: str = "x", intitule: str = "Faire", lot: str = "a") -> str:
    return f"- [{etat}] {n}. {intitule} — {lot} — vérif: v ;;\n"


def une_faute(tmp_path: Path, corps: str) -> str:
    trouvees = fautes(tmp_path, corps)
    assert len(trouvees) == 1, trouvees
    return trouvees[0]


# -------------------------------------------------------------------- conforme
def test_un_fichier_conforme_passe(tmp_path: Path) -> None:
    assert fautes(tmp_path, CONFORME) == []


def test_une_section_au_marqueur_n_est_pas_jugee(tmp_path: Path) -> None:
    assert fautes(tmp_path, contrat(tmp_path).sections["Étapes"].marker) == []


def test_des_bornes_declarees_decoupent(tmp_path: Path) -> None:
    texte = CONTRAT.replace('type = "motif"', 'type = "motif"\ndebut = "*"\nfin = "."')
    c = parse_contract(texte, tmp_path / "contract.toml").unwrap()
    corps = "* [x] 1. Faire — a — vérif: v .\n* [x] 2. Faire — a — vérif: ;; .\n"
    assert check_item(c, Item(tmp_path / "essai.md", {}, {"Étapes": corps})) == []


# -------------------------------------------------------------------- découpe
def test_fin_manquante_sur_la_derniere_puce(tmp_path: Path) -> None:
    corps = puce(1) + "- [x] 2. Faire — a — vérif: v\n"
    assert une_faute(tmp_path, corps) == "section « Étapes », puce 2 — « ;; » final manquant"


def test_texte_avant_la_premiere_puce(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, "Un mot d'intro.\n" + puce(1))
    assert faute.startswith("section « Étapes » — texte hors puce : « Un mot d'intro. »")


def test_texte_apres_une_puce_close_et_une_ligne_vide(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, puce(1) + "\nde la prose\nencore\n\n" + puce(2))
    assert faute.startswith("section « Étapes » — texte hors puce : « de la prose »")


def test_puce_imbriquee(tmp_path: Path) -> None:
    corps = "- [x] 1. Faire — a — vérif: v\n  - [x] 2. Faire — a — vérif: v ;;\n"
    faute = une_faute(tmp_path, corps)
    assert faute.startswith("section « Étapes », puce 1 — « ;; » manquant avant la puce suivante")


def test_puce_hors_motif(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, puce(1) + "- n'importe quoi ;;\n")
    assert faute.startswith("section « Étapes », puce 2 — « n'importe quoi » ne suit pas")


# -------------------------------------------------------------------- captures
def test_valeur_hors_values(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, puce(1, etat="?"))
    assert faute.startswith("section « Étapes », puce 1, capture « etat » — « ? » hors des")


def test_une_valeur_blanche_se_lit_entre_guillemets(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, puce(1, etat="?"))
    assert faute.endswith('hors des valeurs déclarées : x, >, !, " "')


def test_int_mal_ecrit(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, "- [x] un. Faire — a — vérif: v ;;\n")
    assert faute == "section « Étapes », puce 1, capture « n » — un entier est attendu, trouvé str"


@pytest.mark.parametrize(
    ("n", "raison"), [(0, "0 est sous le minimum 1"), (6, "6 dépasse le maximum 5")]
)
def test_int_hors_min_max(tmp_path: Path, n: int, raison: str) -> None:
    corps = "".join(puce(i) for i in range(1, 6)) if n == 6 else ""
    rang = 6 if n == 6 else 1
    trouvees = fautes(tmp_path, corps + puce(n))
    assert f"section « Étapes », puce {rang}, capture « n » — {raison}" in trouvees


def test_sequence_rompue(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, puce(1) + puce(3))
    assert faute == (
        "section « Étapes », puce 2, capture « n » — 3 rompt la séquence — 2 attendu à cette puce"
    )


def test_sequence_mal_partie(tmp_path: Path) -> None:
    trouvees = fautes(tmp_path, puce(2) + puce(3))
    assert trouvees[0] == (
        "section « Étapes », puce 1, capture « n » — 2 rompt la séquence — 1 attendu à cette puce"
    )


def test_sequence_depuis_min(tmp_path: Path) -> None:
    texte = CONTRAT.replace("min = 1\nmax = 5", "min = 0")
    c = parse_contract(texte, tmp_path / "contract.toml").unwrap()
    corps = puce(0) + puce(1)
    assert check_item(c, Item(tmp_path / "essai.md", {}, {"Étapes": corps})) == []


def test_slug_invalide(tmp_path: Path) -> None:
    # Le blanc réduit d'une capture slug reste un blanc : le slug est refusé par check_value.
    faute = une_faute(tmp_path, puce(1, lot="deux mots"))
    assert faute.startswith("section « Étapes », puce 1, capture « lot » — « deux mots »")


def test_capture_requise_faite_de_blancs(tmp_path: Path) -> None:
    faute = une_faute(tmp_path, "- [x] 1. Faire —   — vérif: v ;;\n")
    assert faute.startswith("section « Étapes », puce 1 — « [x] 1. Faire — — vérif: v » ne suit")


# ------------------------------------------------------------------ point d'entrée
def test_cli_check_nomme_section_puce_et_capture(tmp_path: Path) -> None:
    semence = tmp_path / "essai"
    semence.mkdir()
    _ = (semence / "contract.toml").write_text(CONTRAT, encoding="utf-8")
    fiche = tmp_path / "fiche.md"
    _ = fiche.write_text(
        f'+++\ngabarit = "essai"\n+++\n\n## Étapes\n\n{CONFORME}', encoding="utf-8"
    )

    def lancer() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), "check", fiche.name, "--from", str(semence)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    r = lancer()
    assert r.returncode == 0, r.stderr
    _ = fiche.write_text(fiche.read_text(encoding="utf-8").replace("[!]", "[?]"), "utf-8")
    r = lancer()
    assert r.returncode == 1
    assert "section « Étapes », puce 4, capture « etat » — « ? » hors des" in r.stderr
