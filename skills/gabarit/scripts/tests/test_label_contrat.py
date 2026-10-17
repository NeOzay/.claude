"""Une section à labels, déclarée au contrat : lue récursivement, ou refusée en nommant
son chemin.

CE QUE CE FICHIER PROUVE : un contrat déclare `type = "label"`, sa `forme`, son `prefix`
et ses labels, chacun lu comme une section — un motif compris ; la récursion `title` →
`title` → `bold` se lit, le rang 6 est admis et le 7 refusé ; chaque incohérence — forme
absente ou inconnue, labels sous un `bold`, aucun label, `order` mal typé, décroissant ou
hors d'un label, clé de label hors d'une section à labels (deux formes à un niveau) —
refuse le contrat en nommant section et label.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from gabarit.contract import parse_contract
from gabarit.types import Contract, Section

TETE = 'name = "essai"\ndescription = ""\n'
RACINE = '[sections."État"]\ndescription = ""\ntype = "label"\nforme = "bold"\n'


def label(chemin: str, *lignes: str) -> str:
    """La table d'un label, sous `sections."État"` puis `chemin` (« A.labels.B »…)."""
    return f'[sections."État".labels.{chemin}]\ndescription = "x"\n' + "".join(
        f"{ligne}\n" for ligne in lignes
    )


def lire(texte: str, tmp_path: Path) -> Contract:
    return parse_contract(TETE + texte, tmp_path / "contract.toml").unwrap()


def refus(texte: str, tmp_path: Path) -> str:
    r = parse_contract(TETE + texte, tmp_path / "contract.toml")
    assert not r
    assert str(tmp_path / "contract.toml") in r.message
    assert "section « État »" in r.message
    return r.message


def titres(profondeur: int) -> str:
    """Une section `title` et `profondeur` labels `title` emboîtés, le dernier à un label."""
    texte = RACINE.replace('"bold"', '"title"')
    chemin = ""
    for i in range(profondeur):
        chemin = f"{chemin}.labels.L{i}" if chemin else f"L{i}"
        texte += label(chemin, 'type = "label"', 'forme = "title"')
    return texte + label(f"{chemin}.labels.feuille" if chemin else "feuille")


# ------------------------------------------------------------------- déclaration
def test_une_section_a_labels_se_lit(tmp_path: Path) -> None:
    texte = (
        RACINE
        + 'prefix = "un mot d\'introduction"\n'
        + label("Prochaine", "required = true", "order = 1")
        + label("Notes")
        + label('"Vérification"', "order = 2", 'text = "pytest"')
    )
    s = lire(texte, tmp_path).sections["État"]
    assert (s.type, s.forme, s.prefix) == ("label", "bold", "un mot d'introduction")
    assert list(s.labels) == ["Prochaine", "Notes", "Vérification"]
    assert s.labels["Prochaine"] == Section(
        name="Prochaine", required=True, description="x", order=1
    )
    assert s.labels["Notes"].order is None
    assert s.labels["Vérification"].text == "pytest"


def test_un_label_porte_un_motif(tmp_path: Path) -> None:
    texte = (
        RACINE
        + label('"Critères"', 'type = "motif"', 'motif = "{code}: {texte}"')
        + '[sections."État".labels."Critères".captures.code]\ndescription = "C1…"\n'
        + '[sections."État".labels."Critères".captures.texte]\ndescription = "le critère"\n'
    )
    s = lire(texte, tmp_path).sections["État"].labels["Critères"]
    assert s.type == "motif"
    assert list(s.captures) == ["code", "texte"]


def test_un_message_de_capture_nomme_le_chemin_du_label(tmp_path: Path) -> None:
    texte = RACINE + label('"Critères"', 'type = "motif"', 'motif = "{code: enum}"')
    message = refus(texte, tmp_path)
    assert "section « État », label « Critères », capture « code »" in message


def test_une_capture_d_un_label_prend_la_description_du_label(tmp_path: Path) -> None:
    texte = RACINE + label('"Critères"', 'type = "motif"', 'motif = "{code}: {texte}"')
    critere = lire(texte, tmp_path).sections["État"].labels["Critères"]
    assert critere.captures["code"].description == critere.captures["texte"].description == "x"


def test_title_title_bold_se_lit(tmp_path: Path) -> None:
    texte = (
        RACINE.replace('"bold"', '"title"')
        + label("A", 'type = "label"', 'forme = "title"')
        + label("A.labels.B", 'type = "label"', 'forme = "bold"')
        + label("A.labels.B.labels.C")
    )
    s = lire(texte, tmp_path).sections["État"]
    feuille = s.labels["A"].labels["B"].labels["C"]
    assert s.labels["A"].forme == "title"
    assert s.labels["A"].labels["B"].forme == "bold"
    assert feuille.type is None


def test_le_rang_6_est_admis(tmp_path: Path) -> None:
    # Section de rang 2 ; ses labels au rang 3, puis 4, 5 et 6.
    s = lire(titres(3), tmp_path).sections["État"]
    assert s.labels["L0"].labels["L1"].labels["L2"].labels["feuille"].type is None


def test_le_rang_7_est_refuse(tmp_path: Path) -> None:
    message = refus(titres(4), tmp_path)
    assert "label « L0 », label « L1 », label « L2 », label « L3 »" in message
    assert "rang 7, au-delà de 6" in message


def test_un_bold_sous_le_rang_6_reste_admis(tmp_path: Path) -> None:
    texte = titres(3).replace(
        label("L0.labels.L1.labels.L2", 'type = "label"', 'forme = "title"'),
        label("L0.labels.L1.labels.L2", 'type = "label"', 'forme = "bold"'),
    )
    assert lire(texte, tmp_path).sections["État"].labels["L0"].labels["L1"].labels["L2"].forme == (
        "bold"
    )


# ----------------------------------------------------------------------- refus
def test_forme_absente(tmp_path: Path) -> None:
    message = refus(RACINE.replace('forme = "bold"\n', "") + label("A"), tmp_path)
    assert "« forme » manquante" in message


def test_forme_inconnue(tmp_path: Path) -> None:
    message = refus(RACINE.replace('"bold"', '"italique"') + label("A"), tmp_path)
    assert "forme « italique » inconnue" in message


def test_aucun_label(tmp_path: Path) -> None:
    assert "aucun label déclaré" in refus(RACINE, tmp_path)


def test_un_title_dans_un_bold(tmp_path: Path) -> None:
    texte = RACINE + label("A", 'type = "label"', 'forme = "title"') + label("A.labels.B")
    message = refus(texte, tmp_path)
    assert "label « A »" in message
    assert "un label « bold » ne porte pas de labels" in message


def test_deux_formes_a_un_niveau(tmp_path: Path) -> None:
    # Un label qui déclare sa forme sans porter de labels en imposerait une seconde à ses
    # voisins, au même niveau.
    message = refus(RACINE + label("A", 'forme = "title"') + label("B"), tmp_path)
    assert "label « A »" in message
    assert '« forme » réservé à une section de `type = "label"`' in message


@pytest.mark.parametrize("cle", ["labels = {}", 'prefix = "x"', 'forme = "bold"'])
def test_cle_de_label_sur_une_section_sans_labels(tmp_path: Path, cle: str) -> None:
    texte = f'[sections."État"]\ndescription = ""\n{cle}\n'
    message = refus(texte, tmp_path)
    assert f'« {cle.split()[0]} » réservé à une section de `type = "label"`' in message


def test_cle_de_label_sur_une_section_a_motif(tmp_path: Path) -> None:
    texte = '[sections."État"]\ndescription = ""\ntype = "motif"\nmotif = "x"\nforme = "bold"\n'
    assert "« forme » réservé" in refus(texte, tmp_path)


def test_cle_de_motif_sur_une_section_a_labels(tmp_path: Path) -> None:
    message = refus(RACINE + 'motif = "x"\n' + label("A"), tmp_path)
    assert '« motif » réservé à une section de `type = "motif"`' in message


def test_prefix_vide(tmp_path: Path) -> None:
    assert "« prefix » vide" in refus(RACINE + 'prefix = " "\n' + label("A"), tmp_path)


def test_order_hors_d_un_label(tmp_path: Path) -> None:
    message = refus('[sections."État"]\ndescription = ""\norder = 1\n', tmp_path)
    assert "« order » réservé à un label" in message


@pytest.mark.parametrize("valeur", ['"1"', "true", "1.5"])
def test_order_qui_n_est_pas_un_entier(tmp_path: Path, valeur: str) -> None:
    message = refus(RACINE + label("A", f"order = {valeur}"), tmp_path)
    assert "label « A », « order » — un entier est attendu" in message


@pytest.mark.parametrize("second", [1, 2])
def test_order_qui_ne_croit_pas(tmp_path: Path, second: int) -> None:
    texte = RACINE + label("A", "order = 2") + label("B") + label("C", f"order = {second}")
    message = refus(texte, tmp_path)
    assert "label « C »" in message
    assert f"« order » {second} ne croît pas après celui de « A » (2)" in message
