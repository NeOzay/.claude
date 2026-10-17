"""`section_values` : ce que porte une section structurée, lu par gabarit pour ses
consommateurs.

CE QUE CE FICHIER PROUVE (C5) : une section à motif rend une entrée par puce, captures
typées — `int` converti, `" "` d'une enum gardé, None pour une facultative vide ; une
section à labels rend un dict — corps rogné, liste d'un label à motif, dict d'un label à
labels —, sans clé pour un label absent, au marqueur ou non déclaré ; une section au
marqueur rend une liste ou un dict vides ; une section mal formée, sans `type`, absente
ou non déclarée rend un échec nommé.
"""

from __future__ import annotations

from pathlib import Path

from gabarit.contract import parse_contract
from gabarit.structure import section_values
from gabarit.types import Contract, Item

CONTRAT = """name = "essai"
description = ""

[sections."Étapes"]
description = ""
type = "motif"
motif = "[{etat: enum}] {n: int}. {intitule} — vérif: {verif}"

[sections."Étapes".captures.etat]
description = "x"
values = ["x", " "]

[sections."Étapes".captures.n]
description = "x"
sequence = true

[sections."Étapes".captures.intitule]
description = "x"

[sections."Étapes".captures.verif]
description = "x"
required = false

[sections."État"]
description = ""
type = "label"
forme = "title"

[sections."État".labels."Prochaine"]
description = "x"

[sections."État".labels."Notes"]
description = "x"

[sections."État".labels."Critères"]
description = "x"
type = "motif"
motif = "{code}: {texte}"

[sections."État".labels."Critères".captures.code]
description = "x"

[sections."État".labels."Critères".captures.texte]
description = "x"

[sections."État".labels."Détail"]
description = "x"
type = "label"
forme = "bold"

[sections."État".labels."Détail".labels."Clé"]
description = "x"

[sections."Prose"]
description = ""
"""

ETAPES = """\
- [x] 1. Écrire
  sur deux lignes — vérif: pytest ;;
- [ ] 2. Tester — vérif: ;;
"""

ETAT = """\
### Prochaine

  Étape 7.

### Notes

<OPTIONNEL>

### Critères

- C1: un ;;
- C2: deux ;;

### Détail

**Clé** : valeur

### Inconnu

rien
"""


def lire(tmp_path: Path, titre: str, corps: str | None) -> tuple[Contract, Item]:
    contrat = parse_contract(CONTRAT, tmp_path / "contract.toml").unwrap()
    sections = {} if corps is None else {titre: corps}
    return contrat, Item(tmp_path / "essai.md", {}, sections)


def test_une_section_a_motif_rend_ses_puces(tmp_path: Path) -> None:
    r = section_values(*lire(tmp_path, "Étapes", ETAPES), "Étapes")
    assert r.unwrap() == [
        {"etat": "x", "n": 1, "intitule": "Écrire sur deux lignes", "verif": "pytest"},
        {"etat": " ", "n": 2, "intitule": "Tester", "verif": None},
    ]
    puces = r.unwrap()
    assert isinstance(puces, list)
    assert type(puces[0]["n"]) is int


def test_une_section_a_labels_rend_un_dict(tmp_path: Path) -> None:
    r = section_values(*lire(tmp_path, "État", ETAT), "État")
    assert r.unwrap() == {
        "Prochaine": "Étape 7.",
        "Critères": [{"code": "C1", "texte": "un"}, {"code": "C2", "texte": "deux"}],
        "Détail": {"Clé": "valeur"},
    }


def test_un_label_structure_au_marqueur_rend_vide(tmp_path: Path) -> None:
    corps = ETAT.replace("- C1: un ;;\n- C2: deux ;;", "<OPTIONNEL motif: - {code}: {texte} ;;>")
    corps = corps.replace("**Clé** : valeur", "<OPTIONNEL>")
    valeurs = section_values(*lire(tmp_path, "État", corps), "État").unwrap()
    assert isinstance(valeurs, dict)
    assert valeurs["Critères"] == []
    assert valeurs["Détail"] == {}


def test_une_section_au_marqueur_rend_vide(tmp_path: Path) -> None:
    contrat, _ = lire(tmp_path, "Étapes", None)
    marqueur = contrat.sections["Étapes"].marker
    assert section_values(*lire(tmp_path, "Étapes", marqueur), "Étapes").unwrap() == []
    assert section_values(*lire(tmp_path, "État", "<À REMPLIR>"), "État").unwrap() == {}


def test_une_section_mal_formee_rend_un_echec_qui_nomme_chaque_faute(tmp_path: Path) -> None:
    corps = ETAPES.replace("2. Tester", "3. Tester") + "\nde la prose\n"
    r = section_values(*lire(tmp_path, "Étapes", corps), "Étapes")
    assert not r
    assert "section « Étapes », puce 2, capture « n » — 3 rompt la séquence" in r.message
    assert "section « Étapes » — texte hors puce" in r.message


def test_une_section_sans_type_rend_un_echec(tmp_path: Path) -> None:
    r = section_values(*lire(tmp_path, "Prose", "du texte"), "Prose")
    assert not r
    assert "section « Prose » — sans `type`" in r.message


def test_une_section_absente_ou_non_declaree_rend_un_echec(tmp_path: Path) -> None:
    r = section_values(*lire(tmp_path, "Étapes", None), "Étapes")
    assert not r
    assert "absente du fichier" in r.message
    r = section_values(*lire(tmp_path, "Autre", "x"), "Autre")
    assert not r
    assert "non déclarée au contrat « essai »" in r.message
